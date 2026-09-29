"""按 SA2-2019 区号和季度连接 Airbnb 房源与长期租赁押金汇总。

在项目根目录运行：python deliverable5_analysis.py
需要 pandas；结果默认保存到 processed_data 文件夹。
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


# 仅给报告中重点提及的 SA2 编号补上地名；其余区域仍可用编号分析。
#Add place names only for the SA2 codes highlighted in the report; the remaining areas can still be analyzed using the codes.
AREA_NAMES = {
    322600: "Holmwood",
    322500: "Wigram North",
    332700: "Sumner",
    326600: "Christchurch Central",
}
# 排名时要求至少 10 条有价格的 Airbnb 房源，避免极小样本左右结论。
# A minimum of 10 Airbnb listings with pricing data is required for ranking to prevent conclusions from being skewed by extremely small sample sizes.
MIN_PRICED_LISTINGS_FOR_RANKING = 10


def require_columns(frame: pd.DataFrame, names: set[str], label: str) -> None:
    # 输入文件缺少关键列时立即报错，避免后面出现难以定位的错误。
    # Raise an immediate error if the input file is missing a key column, to prevent hard-to-trace errors later on.
    missing = sorted(names - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def read_sources(listings_path: Path, bonds_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    # 第一块：读取两份已清洗的数据，确认必需字段存在。
    # Part 1: Load the two cleaned datasets and verify the presence of required fields.
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
    # 同一房源同一月份应只有一行；每条房源也必须已匹配到 SA2 编号。
    # There should be only one row per property per month; each property record must also be matched to an SA2 code.
    if listings.duplicated(["id", "month_year"]).any():
        raise ValueError("Airbnb file has duplicate listing ID/month combinations")
    if listings["location_id"].isna().any():
        raise ValueError("Airbnb file has missing SA2 codes; review geocoding first")
    # 第二块：统一连接键和价格/押金列的数据类型；Int64 可以保留缺失值。
    # Part 2: Standardize the data types of the join key and the price/deposit columns; Int64 allows for missing values.
    listings["location_id"] = pd.to_numeric(listings["location_id"], errors="raise").astype("Int64")
    bonds["location_id"] = pd.to_numeric(bonds["location_id"], errors="coerce").astype("Int64")
    listings["price_nzd_per_night"] = pd.to_numeric(listings["price_nzd_per_night"], errors="coerce")
    for name in ("total_bonds", "active_bonds", "median_rent_nzd_per_week"):
        bonds[name] = pd.to_numeric(bonds[name], errors="coerce")
    # Airbnb 是月度数据，押金数据是季度数据：都转换成季度首日作为时间连接键。
    #Airbnb data is monthly, while security deposit data is quarterly; both are converted to the first day of the quarter to serve as the time-linking key.
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
    # 第三块：设置输入、输出路径。默认路径适用于项目根目录直接运行。
    # Part 3: Set input and output paths. The default paths are suitable for running directly from the project root directory.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listings", type=Path, default=Path("processed_data/christchurch_listings_with_sa2.csv.gz"))
    parser.add_argument("--bonds", type=Path, default=Path("processed_data/rental_bond_clean.csv.gz"))
    parser.add_argument("--output-dir", type=Path, default=Path("processed_data"))
    args = parser.parse_args()
    listings, bonds = read_sources(args.listings, args.bonds)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # 第四块：押金表同时有分类明细和总计。只取 ALL/ALL 总计行，
    # 避免同一房源匹配多条明细而被重复计算。
    # Fourth part: The security deposit table contains both itemized details and totals. Select only the "ALL/ALL" total row
    # to avoid double-counting caused by matching multiple detail records for the same listing.
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

    # 第五块：按 SA2 区号和季度做多对一左连接。
    # 左连接保留没有押金匹配的 Airbnb 行；validate 防止意外的多对多连接。
    # Part 5: Perform a many-to-one left join based on SA2 code and quarter. 
    # The left join retains Airbnb rows that lack a matching deposit record; validation prevents unintended many-to-many joins.
    joined = listings.merge(
        bond_summary,
        on=["location_id", "quarter_start"],
        how="left",
        validate="many_to_one",
        indicator="bond_join_status",
    )
    if len(joined) != len(listings):
        raise AssertionError("The join changed the number of Airbnb listing-month rows")
    # 将每周押金租金中位数除以 7，统一为“每晚/每天”单位，再计算每条房源的价格差。
    # 这只是单位换算；短租挂牌价与长期租金并非完全等价。
    # Divide the median weekly rental price by 7 to standardize the unit to "per night/day," then calculate the price difference for each listing. 
    # This is merely a unit conversion; short-term listing prices are not directly equivalent to long-term rental rates.
    joined["bond_rent_nzd_per_night"] = joined["median_rent_nzd_per_week"] / 7
    joined["price_gap_nzd_per_night"] = (
        joined["price_nzd_per_night"] - joined["bond_rent_nzd_per_night"]
    )

    # 第六块：使用最新 Airbnb 月份回答题目，避免同一房源跨月重复出现在中位数中。
    # Part 6: Use the most recent Airbnb monthly data to answer the question, avoiding the issue of the same listing appearing across multiple months in the median calculation.
    latest_month = listings["month_year"].max()
    latest = joined.loc[joined["month_year"].eq(latest_month)].copy()
    latest_quarter = latest["quarter_start"].iloc[0]
    central = latest.loc[latest["location_id"].eq(326600)]
    central_median = central["price_nzd_per_night"].median()

    # 第七块：按 SA2 区域汇总 Airbnb 数量、价格、押金数量和价格差中位数。
    # Part 7: Aggregate Airbnb counts, prices, deposit amounts, and the median price difference by SA2 area.
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
    # 只在满足最小样本量且能算出价格差的区域中，寻找最大中位价差。
    #Identify the maximum median price difference only within areas that meet the minimum sample size requirement and allow for the calculation of a price difference.
    eligible = areas.loc[
        areas["priced_airbnb_count"].ge(MIN_PRICED_LISTINGS_FOR_RANKING)
        & areas["median_gap_nzd_per_night"].notna()
    ].sort_values("median_gap_nzd_per_night", ascending=False)

    # 第八块：保存完整连接表、最新月份的区域比较表及文字报告。
    # 完整表使用 gzip 压缩，便于小组共享且无需重新调用地理查询 API。
    # Part 8: Save the complete connection table, the regional comparison table for the latest month, and the text report. 
    # The complete table is compressed using gzip to facilitate team sharing and avoid re-calling the geographic query API.
    joined_path = args.output_dir / "airbnb_bond_joined.csv.gz"
    area_path = args.output_dir / "area_comparison_latest_month.csv"
    report_path = args.output_dir / "deliverable5_results.md"
    joined.to_csv(joined_path, index=False, compression={"method": "gzip", "compresslevel": 6, "mtime": 0})
    areas.to_csv(area_path, index=False, encoding="utf-8-sig")
    top = eligible.iloc[0] if not eligible.empty else None
    # 报告先写数据范围、连接匹配情况和 Christchurch Central 的中位价。
    # The report should first state the data range, the connection matching status, and the median price for Christchurch Central.
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
    # 如果有足够样本，再写价差最大的区域；否则明确说明无法排名。
    # If there is a sufficient sample size, report the regions with the largest price spreads; otherwise, explicitly state that ranking is not possible.
    if top is not None:
        label = top["area_name"] if pd.notna(top["area_name"]) else f"SA2 {int(top['location_id'])}"
        report += [
            f"{label} (SA2 {int(top['location_id'])}) has the largest median gap among areas with at least {MIN_PRICED_LISTINGS_FOR_RANKING} priced June Airbnb listings: NZ${top['median_gap_nzd_per_night']:,.2f} per night.",
            f"Its median Airbnb price is NZ${top['median_airbnb_nzd_per_night']:,.2f}/night and bond median is NZ${top['median_bond_rent_nzd_per_week']:,.2f}/week (NZ${top['median_bond_rent_nzd_per_week']/7:,.2f}/night); {int(top['priced_airbnb_count'])} priced Airbnb listings.",
        ]
    else:
        report.append("Unavailable: no area has enough priced Airbnb listings and a matching bond rent.")
    # 最后写明数量比较的定义和局限，避免把缺失押金误当作零。
    # Finally, specify the definition and limitations of the quantitative comparison to avoid mistaking missing deposit data for zero.
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
    # 终端只打印关键结果和输出路径，方便现场检查程序是否成功完成。
    # The terminal prints only key results and output paths, making it easy to verify on-site whether the program completed successfully.
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
