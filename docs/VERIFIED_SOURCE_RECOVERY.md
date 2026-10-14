# Verified monthly sources and correction

Download-origin metadata stored by Windows identifies the original Inside
Airbnb URLs for November 2025 through August 2026. The downloads are the
18-column summary `visualisations/listings.csv` files. October's supplied file
matches every Christchurch ID, rounded coordinate, price, minimum-night and
availability value in the previous October clean data. Its scrape date uses
the previously configured October date; no download-origin record was available.

| Download name | Correct project name |
|---|---|
| Teammate's 2025_10.csv | 2025_10.csv |
| listings.csv | 2025_11.csv |
| listings (1).csv | 2025_12.csv |
| listings (2).csv | 2026_01.csv |
| listings (3).csv | 2026_02.csv |
| listings (4).csv | 2026_03.csv |
| listings (5).csv | 2026_04.csv |
| listings (6).csv | 2026_05.csv |
| listings (7).csv | 2026_06.csv |
| listings (8).csv | 2026_07.csv |
| listings (9).csv | 2026_08.csv |

The original download `listings (10).csv` is September 2026 and is excluded
from this October 2025–August 2026 deliverable.

## Correction and affected results

The previous project's July and August labels were reversed. Correct July
source URL is `https://data.insideairbnb.com/new-zealand/2026-07-12/visualisations/listings.csv`.
Correct August source URL is `https://data.insideairbnb.com/new-zealand/2026-08-13/visualisations/listings.csv`.

Corrected results:

- July: 51,096 New Zealand rows; 3,488 Christchurch listings; median NZ$227/night.
- August: 51,325 New Zealand rows; 3,513 Christchurch listings; median NZ$224/night.
- Combined Christchurch listing-month rows: 35,796 (unchanged).
- August Christchurch Central median asking price: NZ$256/night.

All month-labelled outputs, review ages and latest-month rankings must be
regenerated; swapping just the labels on old chart images is insufficient.
The cache remains usable because SA2 codes depend on coordinates, not months.

## Source safeguards

`local_data/source_manifest.json` stores month, scrape date, source evidence
and SHA256 for each file. The pipeline checks configured entries before
processing, rejecting swapped or altered sources. The original bond CSV hash
matches the earlier cleaning report; its 226,080 rows are filtered and cleaned
to the matching quarters. No July-quarter bond data is fabricated.

Raw files and backups belong under ignored `local_data/`. Do not commit them
or the API cache. Review current Git changes before submitting; this recovery
does not create a commit or push to GitHub.

AI assistance: OpenAI Codex performed source comparisons, drafted code and
documentation, and ran checks. Course teamwork and submission evidence must
still be reviewed separately by the group.
