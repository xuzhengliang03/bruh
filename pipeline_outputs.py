"""Save earlier analyses, row accounting, checks and a local results gallery.

Raw review fields are never reconstructed from cleaned tables. Missing raw
months are reported explicitly, and review results use only available sources.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def collect_raw_listings(input_dir: Path, dates: dict) -> tuple[pd.DataFrame, list[str]]:
    frames, sources = [], []
    for month, date in sorted(dates.items()):
        path = input_dir / (month.replace("-", "_") + ".csv")
        if not path.is_file():
            continue
        frame = pd.read_csv(path, low_memory=False)
        frame["month_year"], frame["scrape_date"] = month, date
        frames.append(frame)
        sources.append(path.name)
    # The original combined file can restore reviews, but not national results.
    combined_path = input_dir / "christchurch_2025_10_to_2026_06.csv"
    if combined_path.is_file():
        frame = pd.read_csv(combined_path, low_memory=False)
        if not {"id", "month_year", "scrape_date", "neighbourhood_group"}.issubset(frame):
            raise ValueError("Original combined file lacks required metadata")
        loaded = set().union(*(set(f["month_year"]) for f in frames)) if frames else set()
        frame = frame.loc[~frame["month_year"].isin(loaded)]
        frames.append(frame)
        sources.append(combined_path.name)
    return (pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()), sources


def save_stats(frame: pd.DataFrame, prefix: str, output: Path) -> None:
    pd.DataFrame({"column": frame.columns, "missing_rows": frame.isna().sum().values,
                  "nonmissing_rows": frame.notna().sum().values}).to_csv(
        output / f"{prefix}_missing_values.csv", index=False)
    numeric = frame.select_dtypes(include="number")
    numeric.agg(["min", "max", "mean", "std"]).T.to_csv(
        output / f"{prefix}_numeric_summary.csv", index_label="column")
    records = []
    for column in frame.select_dtypes(exclude="number"):
        for value, count in frame[column].value_counts(dropna=False).items():
            records.append({"column": column, "value": value, "count": int(count)})
    pd.DataFrame(records, columns=["column", "value", "count"]).to_csv(
        output / f"{prefix}_category_counts.csv", index=False)


def save_hist(values: pd.Series, title: str, xlabel: str, path: Path,
              bins=30) -> int:
    values = values.dropna()
    if values.empty:
        return 0
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(values, bins=bins, edgecolor="black")
    ax.set(title=title, xlabel=xlabel, ylabel="Listing-month records")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return len(values)


def area_summary(rows: pd.DataFrame) -> pd.DataFrame:
    return rows.groupby("location_id").agg(
        airbnb_listing_count=("id", "nunique"),
        available_airbnb_count=("is_available", "sum"),
        priced_airbnb_count=("price_nzd_per_night", "count"),
        valid_gap_count=("price_gap_nzd_per_night", "count"),
        median_gap_nzd_per_night=("price_gap_nzd_per_night", "median"),
        active_bonds=("active_bonds", "first"),
    ).reset_index()


def save_complete_outputs(clean: pd.DataFrame, raw: pd.DataFrame,
                          sources: list[str], output: Path, counts: dict) -> dict:
    save_stats(clean, "clean_listings", output)
    bonds = pd.read_csv(output / "rental_bond_clean.csv.gz", low_memory=False)
    save_stats(bonds, "clean_bonds", output)
    cleaning_report = output / "CLEANING_REPORT.md"
    if cleaning_report.is_file():
        docs_dir = Path("docs")
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / "CLEANING_REPORT.md").write_text(
            cleaning_report.read_text(encoding="utf-8"), encoding="utf-8"
        )
    joined = pd.read_csv(output / "airbnb_bond_joined.csv.gz", low_memory=False)
    expected_months = sorted(clean["month_year"].unique())
    missing = []
    price = pd.to_numeric(clean["price_nzd_per_night"], errors="coerce")
    histogram_count = save_hist(price[price.between(0, 1000)],
        "Christchurch asking prices: " + expected_months[0] + " to " + expected_months[-1],
        "Nightly asking price (NZD); display range 0–1,000",
        output / "christchurch_price_distribution.png", range(0, 1051, 50))
    valid_review_count = 0
    coverage = []
    review_summary = None
    if not raw.empty:
        if "neighbourhood_group" not in raw:
            raise ValueError("Raw sources lack neighbourhood_group")
        cc = raw.loc[raw["neighbourhood_group"].astype("string").str.strip()
                     .str.casefold().eq("christchurch city")].copy()
        if cc.duplicated(["id", "month_year"]).any():
            raise ValueError("Raw Christchurch sources have duplicate ID/month records")
        coverage = sorted(cc["month_year"].unique())
        missing_months = sorted(set(expected_months) - set(coverage))
        if missing_months:
            missing.append("Raw Christchurch fields unavailable for: " + ", ".join(missing_months))
        if "last_review" in cc:
            days = (pd.to_datetime(cc["scrape_date"], errors="coerce") -
                    pd.to_datetime(cc["last_review"], errors="coerce")).dt.days
            valid_review_count = int(days.ge(0).sum())
            cc["days_since_last_review"] = days.where(days.ge(0))
            pd.DataFrame({"id": cc["id"], "month_year": cc["month_year"],
                          "days_since_last_review": cc["days_since_last_review"]}).to_csv(
                output / "review_age_records.csv.gz", index=False, compression="gzip")
            save_hist(days[days.between(0, 5000)],
                "Days since last review — " + coverage[0] + " to " + coverage[-1],
                "Days since last review; display range 0–5,000",
                output / "days_since_last_review.png", range(0, 5251, 250))
        else:
            missing.append("Raw sources lack last_review")
        save_stats(cc, "raw_christchurch", output)
        cc.to_csv(output / "christchurch_available_raw.csv.gz", index=False,
                  compression={"method": "gzip", "mtime": 0})
        if "number_of_reviews" in cc:
            latest = cc.loc[cc["month_year"].eq(expected_months[-1])].copy()
            reviews = pd.to_numeric(latest["number_of_reviews"], errors="coerce")
            threshold = reviews.quantile(.9, interpolation="higher")
            if pd.notna(threshold):
                top = latest.loc[reviews.ge(threshold)]
                top.to_csv(output / "top_10_percent_reviews_latest.csv", index=False)
                review_summary = {"month": expected_months[-1], "population": "Christchurch City",
                    "threshold": float(threshold), "qualifying_rows": len(top),
                    "valid_review_count_rows": int(reviews.notna().sum()),
                    "note": "Ties at threshold can include more than 10%."}
                (output / "top_10_percent_reviews_summary.json").write_text(
                    json.dumps(review_summary, indent=2), encoding="utf-8")
            else:
                missing.append("Latest month lacks usable review counts")
        else:
            missing.append("Raw sources lack number_of_reviews")
        # Week 4 national analysis is a June baseline, not mixed-month data.
        june_path = next((n for n in sources if n == "2026_06.csv"), None)
        if june_path:
            june = raw.loc[raw["month_year"].eq("2026-06")].copy()
            june_price = pd.to_numeric(june["price"], errors="coerce")
            save_hist(june_price[june_price.between(0, 1000)],
                "New Zealand asking prices — June 2026 baseline", "Nightly asking price (NZD)",
                output / "new_zealand_price_distribution_june.png", range(0, 1051, 50))
            june_cc = june.loc[june["neighbourhood_group"].eq("Christchurch City")]
            june_cc_prices = pd.to_numeric(june_cc["price"], errors="coerce")
            save_hist(june_cc_prices[june_cc_prices.between(0, 1000)],
                "Christchurch asking prices — June 2026 baseline", "Nightly asking price (NZD)",
                output / "christchurch_price_distribution_june.png", range(0, 1051, 50))
            national_review_days = (pd.to_datetime(june["scrape_date"], errors="coerce") -
                pd.to_datetime(june["last_review"], errors="coerce")).dt.days
            save_hist(national_review_days[national_review_days.between(0, 5000)],
                "New Zealand days since last review — June 2026 baseline",
                "Days since last review; display range 0–5,000",
                output / "new_zealand_review_age_june.png", range(0, 5251, 250))
            reviews = pd.to_numeric(june["number_of_reviews"], errors="coerce")
            threshold = reviews.quantile(.9, interpolation="higher")
            national_top = june.loc[reviews.ge(threshold)]
            national_result = {"month": "2026-06", "population": "New Zealand",
                "threshold": None if pd.isna(threshold) else float(threshold),
                "qualifying_rows": len(national_top),
                "christchurch_rows": int(national_top["neighbourhood_group"].eq("Christchurch City").sum())}
            (output / "national_top_reviews_june.json").write_text(
                json.dumps(national_result, indent=2), encoding="utf-8")
        else:
            missing.append("Week 4 New Zealand June baseline requires original 2026_06.csv or saved Orange evidence")
    else:
        missing.append("Raw listing sources unavailable; review analyses cannot be reconstructed")

    matched = joined.loc[joined["bond_join_status"].eq("both")]
    comparable_month = None
    largest_gap = None
    if not matched.empty:
        comparable_month = matched["month_year"].max()
        comparable = joined.loc[joined["month_year"].eq(comparable_month)]
        areas = area_summary(comparable)
        areas.to_csv(output / "area_comparison_latest_matched_month.csv", index=False)
        eligible = areas.loc[areas["valid_gap_count"].ge(10)].sort_values(
            "median_gap_nzd_per_night", ascending=False)
        if not eligible.empty:
            largest_gap = {"month": comparable_month, "location_id": int(eligible.iloc[0]["location_id"]),
                           "median_gap_nzd_per_night": float(eligible.iloc[0]["median_gap_nzd_per_night"])}
            shown = eligible.head(20)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.bar(shown["location_id"].astype(int).astype(str), shown["median_gap_nzd_per_night"])
            ax.set(title=f"Largest median nightly asking-price gaps — {comparable_month} (>=10 valid gaps)",
                   xlabel="SA2-2019 code (top 20; full table saved)", ylabel="Airbnb minus bond weekly rent / 7 (NZD)")
            ax.tick_params(axis="x", rotation=90)
            fig.tight_layout(); fig.savefig(output / "sa2_median_price_gap.png", dpi=160); plt.close(fig)
        save_hist(comparable["price_gap_nzd_per_night"],
            f"Nightly asking-price gap distribution — {comparable_month}",
            "Airbnb asking price minus bond weekly median / 7 (NZD)",
            output / "airbnb_bond_price_gap_distribution.png")
        plot_counts = areas.loc[areas["active_bonds"].notna()].sort_values(
            "airbnb_listing_count", ascending=False).head(20).set_index("location_id")
        if not plot_counts.empty:
            ax = plot_counts[["airbnb_listing_count", "active_bonds"]].plot.bar(figsize=(12, 6))
            ax.set(title=f"Observed Airbnb listings and active bonds — {comparable_month}",
                   xlabel="SA2-2019 code (top 20; different property populations)", ylabel="Count (bond counts rounded)")
            ax.figure.tight_layout(); ax.figure.savefig(output / "sa2_property_count_comparison.png", dpi=160)
            plt.close(ax.figure)
    else:
        missing.append("No month has matching bond summaries")

    checks = {"total_rows": len(clean), "duplicate_id_month_rows": int(clean.duplicated(["id", "month_year"]).sum()),
        "missing_sa2_rows": int(clean["location_id"].isna().sum()),
        "valid_price_rows": int(price.gt(0).sum()), "price_histogram_rows": histogram_count,
        "valid_review_age_rows_available_raw_only": valid_review_count,
        "bond_matched_rows": len(matched), "bond_unmatched_rows": len(joined) - len(matched),
        "valid_price_gap_rows": int(joined["price_gap_nzd_per_night"].notna().sum()),
        "latest_month": expected_months[-1], "latest_comparable_bond_month": comparable_month}
    if checks["duplicate_id_month_rows"] or checks["missing_sa2_rows"] or len(joined) != len(clean):
        raise AssertionError("Final data checks failed")
    if counts["retained_previous_rows"] + counts["replacement_clean_rows"] != len(clean):
        raise AssertionError("Row accounting does not balance")
    result = {"status": "INCOMPLETE_SOURCE_COVERAGE" if missing else "AVAILABLE_DATA_CHECKS_PASSED",
              "missing": missing, "raw_sources": sources, "raw_month_coverage": coverage,
              "checks": checks, "latest_review_ranking": review_summary,
              "largest_gap": largest_gap}
    (output / "validation_report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# Pipeline results and row accounting", "", f"Status: {result['status']}", "",
        "## Row accounting", "", *[f"- {k}: {v}" for k, v in counts.items() if k not in {"cleaning", "bond_cleaning"}],
        "", "## Cleaning decisions for refreshed raw months", "",
        *[f"- {k}: {v}" for k, v in counts["cleaning"].items()
          if k.startswith("rows_removed") or k.endswith("_set_missing") or k == "duplicate_listing_month_rows_removed"],
        "", "## Bond cleaning", "",
        *[f"- {k}: {v}" for k, v in (counts.get("bond_cleaning") or {}).items()
          if k.startswith("rows_") or k == "duplicate_key_rows_removed"],
        "", "## Analysis usability and checks", "", *[f"- {k}: {v}" for k, v in checks.items()],
        "", "## Latest review ranking (Christchurch only)", "", str(review_summary),
        "", "## Largest gap in the latest comparable bond month", "", str(largest_gap),
        "", "## Missing inputs", "", *(missing or ["None for implemented data analyses."]),
        "", "## Interpretation", "", "Missing prices or bond matches are not zero. Review statistics cover only the listed raw months. Price histogram limits apply to display only; high prices remain in the clean data. Bond rent divided by seven is a unit conversion across different rental markets.",
        "", "## Manual course evidence", "", "Git collaboration, Orange workflow demonstration, Māori data-governance slides, Trello and Week 12 questionnaires require separate evidence. Data checks do not certify these tasks."]
    (output / "pipeline_validation_report.md").write_text("\n".join(lines), encoding="utf-8")
    chart_names = ["monthly_airbnb_listing_count.png", "monthly_airbnb_median_price.png",
        "christchurch_price_distribution.png", "days_since_last_review.png",
        "new_zealand_price_distribution_june.png", "christchurch_price_distribution_june.png",
        "new_zealand_review_age_june.png", "sa2_median_price_gap.png",
        "airbnb_bond_price_gap_distribution.png", "sa2_property_count_comparison.png"]
    gallery = ['<!doctype html><meta charset="utf-8"><title>Airbnb results</title>',
        '<style>body{font:18px Arial;max-width:1100px;margin:30px auto;padding:20px}img{width:100%;border:1px solid #ccc}section{margin:40px 0}</style>',
        '<h1>Airbnb pipeline results</h1>', f'<p>Status: {html.escape(result["status"])}</p>',
        '<ul>' + ''.join('<li>' + html.escape(m) + '</li>' for m in missing) + '</ul>',
        '<p><a href="pipeline_validation_report.md">Row counts and checks</a> · <a href="airbnb_bond_analysis_report.md">Bond analysis</a></p>']
    for name in chart_names:
        if (output / name).is_file():
            gallery.append(f'<section><h2>{html.escape(name)}</h2><img src="{name}" alt="{html.escape(name)}"></section>')
    (output / "results_gallery.html").write_text('\n'.join(gallery), encoding="utf-8")
    print("Final checks:", json.dumps(checks))
    for item in missing:
        print("MISSING SOURCE:", item)
    return result
