# Automated update and verified source recovery

Run from the project directory: `python .\update_airbnb_pipeline.py`.

The recovery restored eleven New Zealand summary files, October 2025 through
August 2026. July and August were corrected using original download URLs.
The command validates the source manifest, applies the existing cleaner,
replaces matching months, reuses SA2 cache entries, cleans the original bond
file when present, reruns the bond join and regenerates statistics, plots and
reports. Completely cached runs need no API key and make no network requests.

## Verified final data

- July: 3,488 Christchurch listings; NZ$227 median nightly asking price.
- August: 3,513 Christchurch listings; NZ$224 median nightly asking price.
- Total listing-month rows: 35,796; duplicate ID/month keys: 0.
- SA2 coordinates cached: 4,100; missing SA2 rows: 0.
- August Christchurch Central: NZ$256/night, 121 priced listings.
- Latest comparable bond month: June 2026. Missing August bonds are not zero.
- August Christchurch top-review threshold: 184 reviews; 354 qualifying
  listings. Ties at the threshold can include more than 10%.

## Display all outputs

`Start-Process .\processed_data\results_gallery.html`

The gallery contains ten charts: two monthly trends, full-period Christchurch
price and review-age histograms, June national and Christchurch price
histograms, June national review-age histogram, matched-month SA2 median-gap
ranking, price-gap distribution and property-count comparison.

`pipeline_validation_report.md` explains row filtering and usable sample
counts. `validation_report.json` stores checks and source coverage.
All eleven raw months are present; the data-source status is
`AVAILABLE_DATA_CHECKS_PASSED`. This status does not certify Git teamwork,
Orange demonstration, Māori governance slides, Trello or course questionnaires.

## Repeat-run verification

Two corrected-source runs on a project copy completed without an API key.
Core datasets and monthly summaries had identical SHA256 on the repeat run.
The old nine-month clean data remained unchanged. Restoring all months
replaces 35,796 existing rows with 35,796 freshly cleaned rows: net change 0.
Relative to the original nine-month deliverable, July and August contribute
7,001 additional listing-month rows.

## AI assistance

OpenAI Codex drafted changes and documents, checked download metadata and
ran the comparisons. Review the supplied changes and outputs before submission.
