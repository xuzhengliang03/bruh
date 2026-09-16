"""Join geocoded Airbnb listings to quarterly SA2-2019 bond summaries.

Run from the project directory: python deliverable5_analysis.py
Requires pandas. Outputs are written to processed_data by default.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


AREA_NAMES = {
    322600: "Holmwood",
    322500: "Wigram North",
    332700: "Sumner",
    326600: "Christchurch Central",
}
# Highlighted SA2 names checked against Stats NZ and EHINZ area-code tables.
MIN_PRICED_LISTINGS_FOR_RANKING = 10


def require_columns(frame: pd.DataFrame, names: set[str], label: str) -> None:
    missing = sorted(names - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def read_sources(listings_path: Path, bonds_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    listings = pd.read_csv(listings_path, low_memory=False)
    bonds = pd.read_csv(bonds_path, low_memory=False)
    require_columns(
        listings,
        {"id", "month_year", "location_id", "price_nzd_per_night"},
        "Airbnb file",
    )
    require_columns(
        bonds,
        {
            "timeframe", "location_id", "dwelling_type", "number_of_beds",
            "total_bonds", "active_bonds", "median_rent_nzd_per_week",
        },
        "Bond file",
    )
    if listings.duplicated(["id", "month_year"]).any():
        raise ValueError("Airbnb file has duplicate listing ID/month combinations")
    if listings["location_id"].isna().any():
        raise ValueError("Airbnb file has missing SA2 codes; review geocoding first")
    listings["location_id"] = pd.to_numeric(listings["location_id"], errors="raise").astype("Int64")
    bonds["location_id"] = pd.to_numeric(bonds["location_id"], errors="coerce").astype("Int64")
    listings["price_nzd_per_night"] = pd.to_numeric(listings["price_nzd_per_night"], errors="coerce")
    for name in ("total_bonds", "active_bonds", "median_rent_nzd_per_week"):
        bonds[name] = pd.to_numeric(bonds[name], errors="coerce")
    month_dates = pd.to_datetime(listings["month_year"] + "-01", errors="coerce")
    if month_dates.isna().any():
        raise ValueError("Airbnb month_year contains invalid dates")
    listings["quarter_start"] = month_dates.dt.to_period("Q").dt.start_time.dt.strftime("%Y-%m-%d")
    bond_dates = pd.to_datetime(bonds["timeframe"], errors="coerce")
    if bond_dates.isna().any():
        raise ValueError("Bond timeframe contains invalid dates")
    bonds["quarter_start"] = bond_dates.dt.strftime("%Y-%m-%d")
    return listings, bonds


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listings", type=Path, default=Path("processed_data/christchurch_listings_with_sa2.csv.gz"))
    parser.add_argument("--bonds", type=Path, default=Path("processed_data/rental_bond_clean.csv.gz"))
    parser.add_argument("--output-dir", type=Path, default=Path("processed_data"))
    args = parser.parse_args()
    listings, bonds = read_sources(args.listings, args.bonds)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Each bond file has detail plus subtotals. ALL/ALL is the one overall row.
    bond_summary = bonds.loc[
        bonds["dwelling_type"].astype("string").str.upper().eq("ALL")
        & bonds["number_of_beds"].astype("string").str.upper().eq("ALL")
        & bonds["location_id"].gt(0).fillna(False),
        ["location_id", "quarter_start", "total_bonds", "active_bonds", "median_rent_nzd_per_week"],
    ].copy()
    if bond_summary.duplicated(["location_id", "quarter_start"]).any():
        raise ValueError("Bond ALL/ALL rows are not unique by SA2 and quarter")
    if bond_summary.empty:
        raise ValueError("No overall bond rows (ALL dwelling types and ALL bed counts) were found")

    joined = listings.merge(
        bond_summary,
        on=["location_id", "quarter_start"],
        how="left",
        validate="many_to_one",
        indicator="bond_join_status",
    )
    if len(joined) != len(listings):
        raise AssertionError("The join changed the number of Airbnb listing-month rows")
    joined["bond_rent_nzd_per_night"] = joined["median_rent_nzd_per_week"] / 7
    joined["price_gap_nzd_per_night"] = (
        joined["price_nzd_per_night"] - joined["bond_rent_nzd_per_night"]
    )

    latest_month = listings["month_year"].max()
    latest = joined.loc[joined["month_year"].eq(latest_month)].copy()
    latest_quarter = latest["quarter_start"].iloc[0]
    central = latest.loc[latest["location_id"].eq(326600)]
    central_median = central["price_nzd_per_night"].median()

    areas = (
        latest.groupby("location_id", dropna=False)
        .agg(
            airbnb_listing_count=("id", "nunique"),
            priced_airbnb_count=("price_nzd_per_night", "count"),
            median_airbnb_nzd_per_night=("price_nzd_per_night", "median"),
            median_gap_nzd_per_night=("price_gap_nzd_per_night", "median"),
            active_bonds=("active_bonds", "first"),
            median_bond_rent_nzd_per_week=("median_rent_nzd_per_week", "first"),
        )
        .reset_index()
    )
    areas["area_name"] = areas["location_id"].map(AREA_NAMES)
    areas = areas[[
        "location_id", "area_name", "airbnb_listing_count", "priced_airbnb_count",
        "median_airbnb_nzd_per_night", "active_bonds",
        "median_bond_rent_nzd_per_week", "median_gap_nzd_per_night",
    ]].sort_values("location_id")
    eligible = areas.loc[
        areas["priced_airbnb_count"].ge(MIN_PRICED_LISTINGS_FOR_RANKING)
        & areas["median_gap_nzd_per_night"].notna()
    ].sort_values("median_gap_nzd_per_night", ascending=False)

    joined_path = args.output_dir / "airbnb_bond_joined.csv.gz"
    area_path = args.output_dir / "area_comparison_latest_month.csv"
    report_path = args.output_dir / "deliverable5_results.md"
    joined.to_csv(joined_path, index=False, compression={"method": "gzip", "compresslevel": 6, "mtime": 0})
    areas.to_csv(area_path, index=False, encoding="utf-8-sig")
    top = eligible.iloc[0] if not eligible.empty else None
    report = [
        "# Deliverable 5: Airbnb and rental bonds",
        "",
        f"- Latest Airbnb month: {latest_month}; matched to bond quarter starting {latest_quarter}.",
        f"- Joined listing-month rows: {len(joined):,}; unchanged from Airbnb input.",
        f"- Listing-month rows with a matching ALL/ALL bond record: {int(joined['bond_join_status'].eq('both').sum()):,}.",
        f"- Listing-month rows without a matching bond record: {int(joined['bond_join_status'].eq('left_only').sum()):,}.",
        f"- Christchurch Central (SA2 326600) June 2026 median Airbnb price: NZ${central_median:,.2f} per night, based on {central['price_nzd_per_night'].count():,} priced listings.",
        "",
        "## Largest median short- versus long-term nightly gap",
        "",
    ]
    if top is not None:
        label = top["area_name"] if pd.notna(top["area_name"]) else f"SA2 {int(top['location_id'])}"
        report += [
            f"{label} (SA2 {int(top['location_id'])}) has the largest median gap among areas with at least {MIN_PRICED_LISTINGS_FOR_RANKING} priced June Airbnb listings: NZ${top['median_gap_nzd_per_night']:,.2f} per night.",
            f"Its median Airbnb price is NZ${top['median_airbnb_nzd_per_night']:,.2f}/night and bond median is NZ${top['median_bond_rent_nzd_per_week']:,.2f}/week (NZ${top['median_bond_rent_nzd_per_week']/7:,.2f}/night); {int(top['priced_airbnb_count'])} priced Airbnb listings.",
        ]
    else:
        report.append("Unavailable: no area has enough priced Airbnb listings and a matching bond rent.")
    report += [
        "",
        "## Counts and interpretation",
        "",
        f"- June Airbnb listings: {len(latest):,} across {len(areas):,} SA2 areas.",
        f"- June listings with a matching bond summary: {int(latest['bond_join_status'].eq('both').sum()):,}; without: {int(latest['bond_join_status'].eq('left_only').sum()):,}.",
        "- `area_comparison_latest_month.csv` lists Airbnb counts beside active bonds for each area. Active bonds are a stock measure, while Airbnb counts are observed listings; the two are not identical property populations.",
        "- Bond counts are confidentiality-rounded to base 3, and some bond results are suppressed. Missing bond matches are not zero rental properties.",
        "- Airbnb nightly listing prices are asking prices, not observed bookings. Weekly bond median divided by 7 is only a unit conversion, not an estimate of equivalent whole-property rent.",
        "- The SA2-2019 generalised layer was used for geocoding. Boundary-near points may warrant checking against exact polygons.",
        "",
        "## Method",
        "",
        "Airbnb month was assigned to its calendar-quarter start. Bond rows were restricted to `dwelling_type=ALL` and `number_of_beds=ALL` to avoid duplicating a listing through bond subcategories. A many-to-one left join retained every Airbnb listing-month. For the area ranking, each listing's nightly gap equals its Airbnb asking price minus the area's weekly bond median divided by 7; the area median of these gaps was ranked, requiring at least 10 priced Airbnb listings.",
        "",
        "Sources: [Tenancy Services rental bond data](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/); [Stats NZ SA2-2019 layer](https://datafinder.stats.govt.nz/layer/98970-statistical-area-2-2019-generalised/); [Stats NZ area-code table](https://statsnz.contentdm.oclc.org/digital/api/collection/p20045coll24/id/980/download); [EHINZ SA2 code/name table](https://www.ehinz.ac.nz/assets/Social-Vulnerability-Indicators/2025-SVI-update/Heatmap_SVI2023_SA2.pdf).",
        "",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")
    print(f"Latest month: {latest_month}; bond quarter: {latest_quarter}")
    print(f"Joined rows: {len(joined):,}; all-month bond matches: {int(joined['bond_join_status'].eq('both').sum()):,}")
    print(f"Christchurch Central median Airbnb price: NZ${central_median:,.2f}/night")
    if top is not None:
        print(f"Largest area median gap (>=10 priced listings): SA2 {int(top['location_id'])}, NZ${top['median_gap_nzd_per_night']:,.2f}/night")
    print(f"Saved: {joined_path}")
    print(f"Saved: {area_path}")
    print(f"Saved: {report_path}")


if __name__ == "__main__":
    main()
