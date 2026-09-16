"""Clean the Christchurch Airbnb and Tenancy Services bond datasets.

The script is deliberately path-driven so every team member can reproduce the
same outputs without editing the source code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


LISTING_REQUIRED = {
    "id",
    "neighbourhood_group",
    "neighbourhood",
    "latitude",
    "longitude",
    "room_type",
    "price",
    "minimum_nights",
    "availability_365",
    "month_year",
    "scrape_date",
}

BOND_RENAME = {
    "TimeFrame": "timeframe",
    "Location Id": "location_id",
    "Dwelling Type": "dwelling_type",
    "Number Of Beds": "number_of_beds",
    "Total Bonds": "total_bonds",
    "Active Bonds": "active_bonds",
    "Closed Bonds": "closed_bonds",
    "Median Rent": "median_rent_nzd_per_week",
    "Geometric Mean Rent": "geometric_mean_rent_nzd_per_week",
    "Upper Quartile Rent": "upper_quartile_rent_nzd_per_week",
    "Lower Quartile Rent": "lower_quartile_rent_nzd_per_week",
    "Log Std Dev Weekly Rent": "log_std_dev_weekly_rent",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")


def clean_listings(source: Path) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(source, low_memory=False)
    require_columns(raw, LISTING_REQUIRED, "Listing dataset")

    report: dict = {
        "source_file": source.name,
        "source_sha256": sha256(source),
        "rows_before": int(len(raw)),
        "columns_before": int(len(raw.columns)),
        "missing_before": {k: int(v) for k, v in raw.isna().sum().items()},
    }

    data = raw.copy()
    for column in ["neighbourhood_group", "neighbourhood", "room_type"]:
        data[column] = data[column].astype("string").str.strip()

    group_mask = data["neighbourhood_group"].str.casefold().eq("christchurch city")
    report["rows_removed_outside_christchurch"] = int((~group_mask).sum())
    data = data.loc[group_mask].copy()

    data["month_year"] = pd.to_datetime(data["month_year"], errors="coerce").dt.to_period("M")
    data["scrape_date"] = pd.to_datetime(data["scrape_date"], errors="coerce")
    invalid_period = data["month_year"].isna() | data["scrape_date"].isna()
    report["rows_removed_invalid_period"] = int(invalid_period.sum())
    data = data.loc[~invalid_period].copy()

    for column in ["latitude", "longitude", "price", "minimum_nights", "availability_365"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    valid_coordinates = data["latitude"].between(-90, 90) & data["longitude"].between(-180, 180)
    report["rows_removed_missing_or_invalid_coordinates"] = int((~valid_coordinates).sum())
    data = data.loc[valid_coordinates].copy()

    nonpositive_prices = data["price"].notna() & data["price"].le(0)
    report["nonpositive_prices_set_missing"] = int(nonpositive_prices.sum())
    data.loc[nonpositive_prices, "price"] = pd.NA

    invalid_minimum_nights = data["minimum_nights"].notna() & data["minimum_nights"].lt(1)
    report["invalid_minimum_nights_set_missing"] = int(invalid_minimum_nights.sum())
    data.loc[invalid_minimum_nights, "minimum_nights"] = pd.NA

    invalid_availability = data["availability_365"].notna() & ~data["availability_365"].between(0, 365)
    report["invalid_availability_set_missing"] = int(invalid_availability.sum())
    data.loc[invalid_availability, "availability_365"] = pd.NA

    data = data.sort_values(["scrape_date", "id"], kind="stable")
    duplicate_mask = data.duplicated(["id", "month_year"], keep="last")
    report["duplicate_listing_month_rows_removed"] = int(duplicate_mask.sum())
    data = data.loc[~duplicate_mask].copy()

    data["id"] = pd.to_numeric(data["id"], errors="raise").astype("int64")
    data["minimum_nights"] = data["minimum_nights"].round().astype("Int64")
    data["availability_365"] = data["availability_365"].round().astype("Int64")
    data["is_available"] = data["availability_365"].gt(0).astype("boolean")
    data["has_price"] = data["price"].notna().astype("boolean")
    data["month_year"] = data["month_year"].astype(str)
    data["scrape_date"] = data["scrape_date"].dt.strftime("%Y-%m-%d")

    data = data.rename(columns={"price": "price_nzd_per_night"})
    keep = [
        "id",
        "month_year",
        "scrape_date",
        "neighbourhood",
        "latitude",
        "longitude",
        "room_type",
        "price_nzd_per_night",
        "has_price",
        "minimum_nights",
        "availability_365",
        "is_available",
    ]
    data = data[keep].sort_values(["month_year", "id"], kind="stable").reset_index(drop=True)

    monthly = (
        data.groupby("month_year", sort=True)
        .agg(
            rows=("id", "size"),
            unique_listings=("id", "nunique"),
            valid_prices=("price_nzd_per_night", "count"),
            available_listings=("is_available", "sum"),
            median_price_nzd_per_night=("price_nzd_per_night", "median"),
            maximum_price_nzd_per_night=("price_nzd_per_night", "max"),
        )
        .reset_index()
    )

    monthly_records = monthly.to_dict(orient="records")
    for record in monthly_records:
        for field, value in record.items():
            if pd.isna(value):
                record[field] = None
            elif hasattr(value, "item"):
                record[field] = value.item()

    report.update(
        {
            "rows_after": int(len(data)),
            "columns_after": int(len(data.columns)),
            "date_min": data["month_year"].min(),
            "date_max": data["month_year"].max(),
            "missing_after": {k: int(v) for k, v in data.isna().sum().items()},
            "monthly_summary": monthly_records,
            "price_outliers_above_1000_retained": int(data["price_nzd_per_night"].gt(1000).sum()),
        }
    )
    return data, report


def clean_bonds(source: Path, listing_report: dict) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(source, low_memory=False)
    require_columns(raw, set(BOND_RENAME), "Bond dataset")

    report: dict = {
        "source_file": source.name,
        "source_sha256": sha256(source),
        "rows_before": int(len(raw)),
        "columns_before": int(len(raw.columns)),
        "missing_before": {k: int(v) for k, v in raw.isna().sum().items()},
    }

    data = raw.rename(columns=BOND_RENAME).copy()
    data["timeframe"] = pd.to_datetime(data["timeframe"], errors="coerce")
    invalid_timeframe = data["timeframe"].isna()
    report["rows_removed_invalid_timeframe"] = int(invalid_timeframe.sum())
    data = data.loc[~invalid_timeframe].copy()

    listing_start = pd.Timestamp(listing_report["date_min"] + "-01")
    listing_end = pd.Timestamp(listing_report["date_max"] + "-01")
    first_quarter = listing_start.to_period("Q").start_time
    last_quarter = listing_end.to_period("Q").start_time
    in_range = data["timeframe"].between(first_quarter, last_quarter)
    report["rows_removed_outside_matching_quarters"] = int((~in_range).sum())
    data = data.loc[in_range].copy()

    data["location_id"] = pd.to_numeric(data["location_id"], errors="coerce").astype("Int64")
    data["location_id_status"] = "valid"
    data.loc[data["location_id"].isna(), "location_id_status"] = "missing"
    data.loc[data["location_id"].lt(0).fillna(False), "location_id_status"] = "source_special_code"

    data["dwelling_type"] = data["dwelling_type"].astype("string").str.strip()
    data["number_of_beds"] = data["number_of_beds"].astype("string").str.strip().fillna("Unknown")

    count_columns = ["total_bonds", "active_bonds", "closed_bonds"]
    rent_columns = [
        "median_rent_nzd_per_week",
        "geometric_mean_rent_nzd_per_week",
        "upper_quartile_rent_nzd_per_week",
        "lower_quartile_rent_nzd_per_week",
    ]
    for column in count_columns + rent_columns + ["log_std_dev_weekly_rent"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    invalid_counts = pd.Series(False, index=data.index)
    for column in count_columns:
        invalid_counts |= data[column].lt(0).fillna(False)
        data.loc[data[column].lt(0).fillna(False), column] = pd.NA
        data[column] = data[column].round().astype("Int64")
    report["rows_with_negative_counts_set_missing"] = int(invalid_counts.sum())

    nonpositive_rents = pd.Series(False, index=data.index)
    for column in rent_columns:
        bad = data[column].notna() & data[column].le(0)
        nonpositive_rents |= bad
        data.loc[bad, column] = pd.NA
    report["rows_with_nonpositive_rent_set_missing"] = int(nonpositive_rents.sum())

    key = ["timeframe", "location_id", "dwelling_type", "number_of_beds"]
    duplicate_mask = data.duplicated(key, keep="first")
    report["duplicate_key_rows_removed"] = int(duplicate_mask.sum())
    data = data.loc[~duplicate_mask].copy()

    data["timeframe"] = data["timeframe"].dt.strftime("%Y-%m-%d")
    data = data[
        [
            "timeframe",
            "location_id",
            "location_id_status",
            "dwelling_type",
            "number_of_beds",
            "total_bonds",
            "active_bonds",
            "closed_bonds",
            "median_rent_nzd_per_week",
            "geometric_mean_rent_nzd_per_week",
            "upper_quartile_rent_nzd_per_week",
            "lower_quartile_rent_nzd_per_week",
            "log_std_dev_weekly_rent",
        ]
    ].sort_values(key, kind="stable", na_position="last").reset_index(drop=True)

    report.update(
        {
            "rows_after": int(len(data)),
            "columns_after": int(len(data.columns)),
            "date_min": data["timeframe"].min(),
            "date_max": data["timeframe"].max(),
            "quarters_retained": sorted(data["timeframe"].unique().tolist()),
            "missing_after": {k: int(v) for k, v in data.isna().sum().items()},
            "location_id_status_counts": {
                str(k): int(v) for k, v in data["location_id_status"].value_counts().items()
            },
        }
    )
    return data, report


def markdown_report(listing: dict, bond: dict) -> str:
    monthly_rows = []
    for row in listing["monthly_summary"]:
        median = "n.a." if row["median_price_nzd_per_night"] is None else f'{row["median_price_nzd_per_night"]:.0f}'
        monthly_rows.append(
            f'| {row["month_year"]} | {row["rows"]} | {row["valid_prices"]} | '
            f'{row["available_listings"]} | {median} |'
        )
    monthly_table = "\n".join(monthly_rows)

    return f"""# Deliverable 4 cleaning report

## Result

| Dataset | Rows before | Rows after | Columns before | Columns after |
|---|---:|---:|---:|---:|
| Christchurch listings | {listing['rows_before']} | {listing['rows_after']} | {listing['columns_before']} | {listing['columns_after']} |
| Rental bonds | {bond['rows_before']} | {bond['rows_after']} | {bond['columns_before']} | {bond['columns_after']} |

The listing data covers {listing['date_min']} to {listing['date_max']}. The bond data keeps the corresponding quarter starts: {', '.join(bond['quarters_retained'])}.

## Monthly listing coverage

| Month | Rows | Valid prices | Available listings | Median nightly price (NZD) |
|---|---:|---:|---:|---:|
{monthly_table}

Price is entirely missing in the supplied source for 2025-12, 2026-01 and 2026-02. Those rows remain available for property-count analysis but must not be used for price comparisons. No prices were imputed.

## Listing decisions

- Kept `latitude` and `longitude`, as required, and removed {listing['rows_removed_missing_or_invalid_coordinates']} rows with missing or invalid coordinates.
- Kept one record per listing and month; removed {listing['duplicate_listing_month_rows_removed']} duplicate keys.
- Kept positive price outliers instead of choosing an unsupported cutoff. {listing['price_outliers_above_1000_retained']} prices above NZD 1,000 per night remain.
- Added `has_price` and `is_available` so price coverage and available-property counts are explicit.
- Kept only fields needed to identify a listing, locate it, classify the room, compare price, and count availability. Names, host details, licence, review metrics and the constant Christchurch group field were dropped. This reduces file size and avoids carrying unrelated personal/free-text fields.
- Preserved missing prices and minimum-night values. Filling them would invent information and bias later comparisons.

## Bond decisions

- Kept `timeframe` and `location_id`, as required.
- Filtered to the three quarters overlapping the listing period. This removed {bond['rows_removed_outside_matching_quarters']} rows.
- Preserved missing and negative source location identifiers, with `location_id_status` marking `missing`, `source_special_code`, or `valid`; their meaning is not guessed.
- Changed non-positive weekly rents to missing in {bond['rows_with_nonpositive_rent_set_missing']} rows because a zero/negative weekly rent is not analytically usable. Other missing rent values remain missing and were not imputed.
- Standardised column names, dates, integer count types and the missing bedroom label. Removed {bond['duplicate_key_rows_removed']} duplicate keys.

## Consequences and limitations

- Airbnb `price_nzd_per_night` is an advertised nightly short-stay price. Bond rent is a weekly long-term tenancy measure. Convert units and explain the market difference before comparing them.
- `availability_365 > 0` indicates that at least one future day is open in the Airbnb calendar; it is not the number of occupied or vacant long-term homes.
- Tenancy Services applies fixed random rounding to base 3 and suppresses results for fewer than five bonds. Exact small-area counts cannot be recovered.
- Tenancy Services states that recent records are provisional during its bond-system migration and may be revised. Recent periods may not be directly comparable with earlier periods.
- `location_id` uses the source's SA2-2019 geography. Joining listing coordinates to bond areas requires an SA2-2019 spatial boundary or another defensible crosswalk; neighbourhood names should not be joined directly to numeric IDs.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listing-input", required=True, type=Path)
    parser.add_argument("--bond-input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    listings, listing_report = clean_listings(args.listing_input)
    bonds, bond_report = clean_bonds(args.bond_input, listing_report)

    gzip_options = {"method": "gzip", "compresslevel": 9, "mtime": 0}
    listing_output = args.output_dir / "christchurch_listings_clean.csv.gz"
    bond_output = args.output_dir / "rental_bond_clean.csv.gz"
    listings.to_csv(listing_output, index=False, compression=gzip_options, float_format="%.6f")
    bonds.to_csv(bond_output, index=False, compression=gzip_options, float_format="%.6f")

    summary = {"listings": listing_report, "rental_bonds": bond_report}
    (args.output_dir / "cleaning_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8"
    )
    (args.output_dir / "CLEANING_REPORT.md").write_text(
        markdown_report(listing_report, bond_report), encoding="utf-8"
    )

    print(f"Clean listings: {len(listings):,} rows -> {listing_output}")
    print(f"Clean bonds: {len(bonds):,} rows -> {bond_output}")


if __name__ == "__main__":
    main()
