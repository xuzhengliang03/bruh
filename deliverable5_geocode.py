"""Add Stats NZ SA2-2019 codes to cleaned Christchurch Airbnb listings.

Run from the project directory after setting KOORDINATES_API_KEY in the
current terminal. The API key is never written to the output or cache.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


ENDPOINT = "https://datafinder.stats.govt.nz/services/query/v1/vector.json"
LAYER_ID = 98970  # Stats NZ Statistical Area 2 2019 (generalised)
CODE_FIELD = "SA22019_V1_00"
TEST_LATITUDE = -43.51148
TEST_LONGITUDE = 172.59658
EXPECTED_TEST_CODE = "320800"
CODE_RE = re.compile(r"\d{6}")


def coordinate_key(latitude: float, longitude: float) -> str:
    return f"{latitude:.15g},{longitude:.15g}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def extract_sa2_code(payload: object) -> str | None:
    """Find the named SA2 field in a Koordinates JSON response."""
    found: set[str] = set()

    def visit(value: object) -> None:
        if isinstance(value, dict):
            if CODE_FIELD in value and value[CODE_FIELD] is not None:
                candidate = str(value[CODE_FIELD]).strip()
                if CODE_RE.fullmatch(candidate):
                    found.add(candidate)
            # Some API versions return field names and values as parallel lists.
            names = value.get("field_names")
            fields = value.get("fields")
            if isinstance(names, list) and isinstance(fields, list) and CODE_FIELD in names:
                position = names.index(CODE_FIELD)
                if position < len(fields):
                    candidate = str(fields[position]).strip()
                    if CODE_RE.fullmatch(candidate):
                        found.add(candidate)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(payload)
    if len(found) > 1:
        raise ValueError("API returned more than one distinct SA2 code for one point")
    return next(iter(found), None)


def query_sa2(api_key: str, latitude: float, longitude: float) -> str | None:
    parameters = {
        "key": api_key,
        "layer": LAYER_ID,
        "x": longitude,
        "y": latitude,
        "max_results": 1,
        "radius": 0,
        "geometry": "false",
        "with_field_names": "true",
    }
    url = ENDPOINT + "?" + urlencode(parameters)
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "DATA201-D5-SA2-geocoder/1.0"})
    for attempt in range(5):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            return extract_sa2_code(payload)
        except HTTPError as error:
            if error.code in (401, 403):
                raise RuntimeError(f"API authentication/permission failed (HTTP {error.code})") from None
            if error.code not in (429, 500, 502, 503, 504) or attempt == 4:
                raise RuntimeError(f"API request failed (HTTP {error.code})") from None
        except (URLError, TimeoutError):
            if attempt == 4:
                raise RuntimeError("API request failed after 5 attempts; check connection") from None
        time.sleep(min(2**attempt, 16))
    raise RuntimeError("API request failed")


def load_cache(path: Path) -> dict[str, str | None]:
    cache: dict[str, str | None] = {}
    if not path.exists():
        return cache
    with path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                raise RuntimeError(
                    f"Cache line {line_number} is incomplete. Repair or rename {path} before retrying."
                ) from None
            if record.get("layer_id") != LAYER_ID:
                continue
            code = record.get("location_id")
            if code is None or CODE_RE.fullmatch(str(code)):
                cache[str(record["coordinate"])] = None if code is None else str(code)
    return cache


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("processed_data/christchurch_listings_clean.csv.gz"))
    parser.add_argument("--output-dir", type=Path, default=Path("processed_data"))
    parser.add_argument("--workers", type=int, default=4, help="Concurrent API requests; default 4")
    parser.add_argument("--test-only", action="store_true", help="Check the known example point, then stop")
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("--workers must be between 1 and 8")
    api_key = os.environ.get("KOORDINATES_API_KEY", "").strip()
    if not api_key:
        parser.error("Set KOORDINATES_API_KEY in this terminal first")

    test_code = query_sa2(api_key, TEST_LATITUDE, TEST_LONGITUDE)
    print(f"Example point returned SA2 code: {test_code or 'no match'}")
    if test_code != EXPECTED_TEST_CODE:
        raise RuntimeError(
            f"Expected {EXPECTED_TEST_CODE}, received {test_code!r}. "
            "Check the layer, API key, coordinate order and JSON result before the batch run."
        )
    if args.test_only:
        print("Single-point test passed; no batch requests were made.")
        return 0

    if not args.input.is_file():
        parser.error(f"Input file not found: {args.input}")
    listings = pd.read_csv(args.input, low_memory=False)
    required = {"id", "month_year", "latitude", "longitude"}
    missing = required.difference(listings.columns)
    if missing:
        parser.error(f"Input lacks columns: {sorted(missing)}")
    if "location_id" in listings.columns:
        parser.error("Input already has location_id; use the cleaned pre-geocode file")
    if listings.duplicated(["id", "month_year"]).any():
        parser.error("Input has duplicate id/month_year rows; fix source data first")
    for field in ("latitude", "longitude"):
        listings[field] = pd.to_numeric(listings[field], errors="coerce")
    if listings[["latitude", "longitude"]].isna().any().any():
        parser.error("Input contains missing or nonnumeric coordinates")
    valid = listings["latitude"].between(-90, 90) & listings["longitude"].between(-180, 180)
    if not valid.all():
        parser.error("Input contains out-of-range coordinates")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cache_path = args.output_dir / "koordinates_sa2_2019_cache.jsonl"
    output_path = args.output_dir / "christchurch_listings_with_sa2.csv.gz"
    report_path = args.output_dir / "geocoding_report.json"
    cache = load_cache(cache_path)
    coordinates = list(dict.fromkeys(
        coordinate_key(lat, lon)
        for lat, lon in zip(listings["latitude"], listings["longitude"])
    ))
    pending = [key for key in coordinates if key not in cache]
    print(f"Listing rows: {len(listings):,}; unique coordinates: {len(coordinates):,}")
    print(f"Cached coordinates: {len(coordinates) - len(pending):,}; API requests remaining: {len(pending):,}")

    failures: list[str] = []
    with cache_path.open("a", encoding="utf-8") as sink, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {}
        for key in pending:
            latitude, longitude = (float(piece) for piece in key.split(","))
            futures[pool.submit(query_sa2, api_key, latitude, longitude)] = key
        for done, future in enumerate(as_completed(futures), 1):
            key = futures[future]
            try:
                code = future.result()
            except Exception as error:
                failures.append(f"{key}: {error}")
                continue
            cache[key] = code
            sink.write(json.dumps({"coordinate": key, "location_id": code, "layer_id": LAYER_ID}) + "\n")
            sink.flush()
            if done % 250 == 0 or done == len(pending):
                print(f"Processed {done:,}/{len(pending):,} new coordinates")

    if failures:
        print(f"{len(failures):,} requests failed. Re-run this command to retry only failures.", file=sys.stderr)
        for detail in failures[:5]:
            print(detail, file=sys.stderr)
        return 1

    listings["location_id"] = pd.array(
        [cache[coordinate_key(lat, lon)] for lat, lon in zip(listings["latitude"], listings["longitude"])],
        dtype="Int64",
    )
    unmatched = int(listings["location_id"].isna().sum())
    if unmatched > len(listings) * 0.10:
        raise RuntimeError(
            f"{unmatched:,} of {len(listings):,} listings have no SA2 code (>10%). "
            "The cache is saved, but check the API result and layer before writing a final dataset."
        )
    temporary = output_path.with_name(output_path.name + ".tmp")
    listings.to_csv(temporary, index=False, compression={"method": "gzip", "compresslevel": 6, "mtime": 0})
    temporary.replace(output_path)
    report = {
        "source_file": str(args.input),
        "source_sha256": sha256(args.input),
        "layer_id": LAYER_ID,
        "sa2_field": CODE_FIELD,
        "test_coordinate": {"latitude": TEST_LATITUDE, "longitude": TEST_LONGITUDE},
        "test_code": test_code,
        "listing_rows": len(listings),
        "unique_coordinates": len(coordinates),
        "matched_listing_rows": int(listings["location_id"].notna().sum()),
        "unmatched_listing_rows": int(listings["location_id"].isna().sum()),
        "output_file": str(output_path),
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved: {output_path}")
    print(f"Unmatched listing rows: {report['unmatched_listing_rows']:,}")
    print(f"Saved summary: {report_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
