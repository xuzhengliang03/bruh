"""Incrementally add new Airbnb months and refresh all downstream outputs.

Place summary ``listings.csv`` downloads in ``local_data`` using names such as
``2026_07.csv``. Run this script once from the project root after setting the
Koordinates API key. Re-running it replaces the same months instead of creating
duplicate listing-month rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from clean_airbnb_and_bond_data import clean_listings, clean_bonds, markdown_report
from geocode_airbnb_sa2 import LAYER_ID, coordinate_key, load_cache
from pipeline_outputs import save_complete_outputs, collect_raw_listings


MONTH_FILE_RE = re.compile(r"^(\d{4})_(\d{2})\.csv$")
SCRAPE_DATES = {
    "2025-10": "2025-10-05",
    "2025-11": "2025-11-07",
    "2025-12": "2025-12-11",
    "2026-01": "2026-01-16",
    "2026-02": "2026-02-13",
    "2026-03": "2026-03-17",
    "2026-04": "2026-04-16",
    "2026-05": "2026-05-23",
    "2026-06": "2026-06-19",
    "2026-07": "2026-07-12",
    "2026-08": "2026-08-13",
}


def discover_month_files(input_dir: Path) -> list[tuple[Path, str, str]]:
    """Return validated month files with their month and scrape date."""
    discovered: list[tuple[Path, str, str]] = []
    manifest_path = input_dir / "source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    for path in sorted(input_dir.glob("*.csv")):
        match = MONTH_FILE_RE.fullmatch(path.name)
        if not match:
            continue
        month = f"{match.group(1)}-{match.group(2)}"
        if path.name in manifest:
            source = manifest[path.name]
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != source["sha256"] or month != source["month"]:
                raise ValueError(f"Source identity mismatch for {path.name}; check verified month mapping")
            if source["scrape_date"] != SCRAPE_DATES.get(month):
                raise ValueError(f"Scrape date mismatch for {path.name}")
        if month not in SCRAPE_DATES:
            raise ValueError(
                f"No verified scrape date is configured for {path.name}; "
                "add it to SCRAPE_DATES before processing."
            )
        discovered.append((path, month, SCRAPE_DATES[month]))
    if not discovered:
        raise FileNotFoundError(
            f"No YYYY_MM.csv files were found in {input_dir}."
        )
    return discovered


def prepare_new_months(
    month_files: list[tuple[Path, str, str]],
) -> tuple[pd.DataFrame, dict]:
    """Attach month metadata and apply the established listing cleaner."""
    raw_months: list[pd.DataFrame] = []
    for path, month, scrape_date in month_files:
        frame = pd.read_csv(path, low_memory=False)
        frame["month_year"] = month
        frame["scrape_date"] = scrape_date
        raw_months.append(frame)
        print(f"Loaded {path.name}: {len(frame):,} New Zealand rows")

    combined_raw = pd.concat(raw_months, ignore_index=True)
    with tempfile.TemporaryDirectory(prefix="airbnb_update_") as temp_dir:
        temporary_input = Path(temp_dir) / "new_months.csv"
        combined_raw.to_csv(temporary_input, index=False)
        return clean_listings(temporary_input)


def write_atomically(frame: pd.DataFrame, destination: Path) -> None:
    """Write a deterministic gzip CSV, then replace the previous file."""
    temporary = destination.with_name(destination.name + ".tmp")
    frame.to_csv(
        temporary,
        index=False,
        compression={"method": "gzip", "compresslevel": 6, "mtime": 0},
        float_format="%.6f",
    )
    temporary.replace(destination)


def seed_cache_from_existing_geocodes(
    existing: pd.DataFrame,
    cache_path: Path,
) -> int:
    """Reuse the project's previous SA2 matches before making API requests."""
    required = {"latitude", "longitude", "location_id"}
    missing = sorted(required - set(existing.columns))
    if missing:
        raise ValueError(f"Existing geocoded data is missing columns: {missing}")

    current = load_cache(cache_path)
    additions: dict[str, str] = {}
    usable = existing.dropna(subset=["latitude", "longitude", "location_id"])
    for row in usable[["latitude", "longitude", "location_id"]].itertuples(index=False):
        key = coordinate_key(float(row.latitude), float(row.longitude))
        code = str(int(row.location_id))
        known = additions.get(key, current.get(key))
        if known is not None and str(known) != code:
            raise ValueError(f"Coordinate {key} has conflicting SA2 codes")
        if current.get(key) != code:
            additions[key] = code

    if additions:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("a", encoding="utf-8") as sink:
            for key, code in sorted(additions.items()):
                sink.write(
                    json.dumps(
                        {
                            "coordinate": key,
                            "location_id": code,
                            "layer_id": LAYER_ID,
                        }
                    )
                    + "\n"
                )
    return len(additions)


def save_monthly_plots(listings: pd.DataFrame, output_dir: Path) -> None:
    """Save updated count and median-price plots for every available month."""
    monthly = (
        listings.groupby("month_year", sort=True)
        .agg(
            listing_count=("id", "nunique"),
            median_price_nzd=("price_nzd_per_night", "median"),
        )
        .reset_index()
    )

    figure, axis = plt.subplots(figsize=(9, 5))
    axis.plot(monthly["month_year"], monthly["listing_count"], marker="o")
    axis.set_title("Christchurch Airbnb listings by month")
    axis.set_xlabel("Month")
    axis.set_ylabel("Unique listings")
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(output_dir / "monthly_airbnb_listing_count.png", dpi=160)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(9, 5))
    axis.plot(monthly["month_year"], monthly["median_price_nzd"], marker="o")
    axis.set_title("Christchurch median Airbnb asking price by month")
    axis.set_xlabel("Month")
    axis.set_ylabel("Median nightly price (NZD)")
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(output_dir / "monthly_airbnb_median_price.png", dpi=160)
    plt.close(figure)

    monthly.to_csv(
        output_dir / "monthly_airbnb_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )


def run_checked(command: list[str]) -> None:
    """Run one pipeline stage and stop immediately if it fails."""
    print("Running:", " ".join(command))
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("local_data"))
    parser.add_argument("--processed-dir", type=Path, default=Path("processed_data"))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    if not 1 <= args.workers <= 8:
        parser.error("--workers must be between 1 and 8")

    args.processed_dir.mkdir(parents=True, exist_ok=True)
    clean_path = args.processed_dir / "christchurch_listings_clean.csv.gz"
    geocoded_path = args.processed_dir / "christchurch_listings_with_sa2.csv.gz"
    bonds_path = args.processed_dir / "rental_bond_clean.csv.gz"
    for path in (clean_path, geocoded_path, bonds_path):
        if not path.is_file():
            parser.error(f"Required previous pipeline output not found: {path}")

    month_files = discover_month_files(args.input_dir)
    new_months = {month for _, month, _ in month_files}
    print("Months to update:", ", ".join(sorted(new_months)))
    new_clean, new_report = prepare_new_months(month_files)

    previous_clean = pd.read_csv(clean_path, low_memory=False)
    previous_geocoded = pd.read_csv(geocoded_path, low_memory=False)
    old_clean = previous_clean.loc[~previous_clean["month_year"].isin(new_months)]
    combined_clean = pd.concat([old_clean, new_clean], ignore_index=True)
    # Use the same coordinate precision as the deterministic CSV writer before
    # cache checks; otherwise raw high-precision coordinates appear uncached.
    for coordinate_column in ("latitude", "longitude"):
        combined_clean[coordinate_column] = combined_clean[coordinate_column].map(
            lambda value: float("%.6f" % value)
        )
    combined_clean = combined_clean.sort_values(["month_year", "id"], kind="stable")
    if combined_clean.duplicated(["id", "month_year"]).any():
        raise ValueError("Combined clean data has duplicate listing ID/month rows")

    cache_path = args.processed_dir / "koordinates_sa2_2019_cache.jsonl"
    seeded = seed_cache_from_existing_geocodes(previous_geocoded, cache_path)
    print(f"Seeded {seeded:,} reusable coordinate matches from previous output")
    cache = load_cache(cache_path)
    pending = {coordinate_key(lat, lon) for lat, lon in
               zip(combined_clean["latitude"], combined_clean["longitude"])} - set(cache)
    if pending and not os.environ.get("KOORDINATES_API_KEY", "").strip():
        parser.error(f"{len(pending)} new coordinates require KOORDINATES_API_KEY; clean data has not been replaced")
    write_atomically(combined_clean, clean_path)
    raw_bonds_path = args.input_dir / "Detailed-Quarterly-Tenancy.csv"
    bond_report = None
    if raw_bonds_path.is_file():
        listing_period = dict(new_report, date_min=combined_clean["month_year"].min(),
                              date_max=combined_clean["month_year"].max())
        cleaned_bonds, bond_report = clean_bonds(raw_bonds_path, listing_period)
        write_atomically(cleaned_bonds, bonds_path)
        (args.processed_dir / "cleaning_summary.json").write_text(
            json.dumps({"listings": new_report, "rental_bonds": bond_report}, indent=2), encoding="utf-8")
        (args.processed_dir / "CLEANING_REPORT.md").write_text(
            markdown_report(new_report, bond_report), encoding="utf-8")
        print(f"Bond cleaning: {bond_report['rows_before']:,} -> {bond_report['rows_after']:,} rows")

    run_checked(
        [
            sys.executable,
            "geocode_airbnb_sa2.py",
            "--input",
            str(clean_path),
            "--output-dir",
            str(args.processed_dir),
            "--workers",
            str(args.workers),
        ]
    )
    run_checked(
        [
            sys.executable,
            "analyse_airbnb_bonds.py",
            "--listings",
            str(geocoded_path),
            "--bonds",
            str(bonds_path),
            "--output-dir",
            str(args.processed_dir),
        ]
    )
    generated_report = args.processed_dir / "airbnb_bond_analysis_report.md"
    report_copy = Path("docs") / "airbnb_bond_analysis_report.md"
    report_copy.parent.mkdir(parents=True, exist_ok=True)
    report_copy.write_text(
        generated_report.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    refreshed = pd.read_csv(geocoded_path, low_memory=False)
    save_monthly_plots(refreshed, args.processed_dir)
    raw, raw_sources = collect_raw_listings(args.input_dir, SCRAPE_DATES)
    row_counts = {
        "previous_clean_rows": len(previous_clean),
        "rows_replaced": int(previous_clean["month_year"].isin(new_months).sum()),
        "retained_previous_rows": len(old_clean),
        "replacement_clean_rows": len(new_clean),
        "net_row_change": len(refreshed) - len(previous_clean),
        "raw_month_rows": new_report["rows_before"],
        "cleaning": new_report,
        "bond_cleaning": bond_report,
    }
    completion = save_complete_outputs(refreshed, raw, raw_sources,
                                      args.processed_dir, row_counts)
    summary = {
        "updated_months": sorted(new_months),
        "new_clean_rows": int(len(new_clean)),
        "total_listing_month_rows": int(len(refreshed)),
        "latest_month": str(refreshed["month_year"].max()),
        "new_month_cleaning": new_report,
        "row_counts": row_counts,
        "completion": completion,
    }
    (args.processed_dir / "pipeline_update_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    print("Pipeline update completed successfully.")
    print(f"Latest month: {summary['latest_month']}")
    print(f"Total listing-month rows: {summary['total_listing_month_rows']:,}")
    print(f"Plots saved in: {args.processed_dir}")
    print(f"Data readiness: {completion['status']}")
    print(f"Open all plots: {args.processed_dir / 'results_gallery.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
