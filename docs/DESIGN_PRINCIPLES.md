# Pipeline design principles

## AI use

OpenAI Codex was used to help review the pipeline structure and draft this
document. The team checked the document against the Python implementation and
remains responsible for the final code, methods and documentation.

## 1. Inputs

### Raw inputs

- Monthly New Zealand summary Airbnb CSV files stored under `local_data/`,
  filtered to Christchurch City during processing.
- `local_data/Detailed-Quarterly-Tenancy.csv`, downloaded from New Zealand
  Tenancy Services.

### Prepared inputs

- `processed_data/christchurch_listings_clean.csv.gz`
- `processed_data/rental_bond_clean.csv.gz`
- Stats NZ Statistical Area 2 2019 generalised layer `98970` on Koordinates.
- A Koordinates API key supplied at runtime through the
  `KOORDINATES_API_KEY` environment variable.

The API key is used only by `geocode_airbnb_sa2.py` to call the Koordinates
spatial-query endpoint. It is not stored in source code, output files, reports
or the coordinate cache.

## 2. Outputs

### Data preparation and cleaning

- Combined monthly Airbnb data under `local_data/`.
- `processed_data/christchurch_listings_clean.csv.gz`
- `processed_data/rental_bond_clean.csv.gz`
- `processed_data/CLEANING_REPORT.md`
- `processed_data/cleaning_summary.json`

### Geocoding

- `processed_data/christchurch_listings_with_sa2.csv.gz`
- `processed_data/geocoding_report.json`
- `processed_data/koordinates_sa2_2019_cache.jsonl` as a local intermediate
  cache, not a final analytical output.

### Rental comparison

- `processed_data/airbnb_bond_joined.csv.gz`
- `processed_data/area_comparison_latest_month.csv`
- `processed_data/airbnb_bond_analysis_report.md`
- `docs/airbnb_bond_analysis_report.md` as the version-controlled report copy.

## 3. Main steps

1. `prepare_airbnb_monthly_data.py` reads the monthly Airbnb files, selects
   Christchurch City, attaches month and scrape-date fields, and combines the
   observations.
2. `clean_airbnb_and_bond_data.py` validates required columns, standardises
   dates and numeric values, removes invalid or duplicate keys, aligns the
   study period and saves compressed prepared datasets.
3. `geocode_airbnb_sa2.py` tests one known coordinate before new API requests.
   Fully cached runs skip the API test and do not require an API key.
4. The geocoder extracts unique coordinate pairs, reuses cached results and
   queries only coordinates not already cached.
5. The returned `SA22019_V1_00` value is stored as the Airbnb `location_id`,
   and the geocoded dataset is saved so later runs need not repeat the API
   requests.
6. `analyse_airbnb_bonds.py` maps Airbnb months and bond dates to calendar
   quarter starts.
7. The analysis retains the bond `ALL` dwelling-type and `ALL` bedroom summary
   rows to avoid duplicate matches through subcategories.
8. The prepared datasets are joined on `location_id` and quarter using a
   validated many-to-one left join.
9. The latest month is summarised by SA2, including Airbnb counts, active-bond
   counts, median prices and the short-term-minus-long-term daily price gap.
10. The joined data, area comparison, written report and concise terminal
    summary are produced.
11. `update_airbnb_pipeline.py` orchestrates the incremental monthly update,
    reuses existing SA2 matches, refreshes the analysis and saves current plots.
12. `pipeline_outputs.py` saves raw-field statistics for available months,
    Christchurch histograms and review rankings, latest matched-month bond
    comparison charts, balanced row accounting and a local HTML gallery.
    Missing historical raw months are recorded explicitly. See
    `docs/PIPELINE_COMPLETION.md` for inputs, outputs and coverage limitations.
13. When `local_data/source_manifest.json` is present, monthly hashes and
    dates are checked against verified download identities before processing.
    If the original quarterly bond CSV is available, its existing cleaner is
    rerun for the combined listing period. Otherwise the prepared bond input
    is reused. See `docs/VERIFIED_SOURCE_RECOVERY.md` for the July/August fix.

## 4. Coding and software strategies

### Separation of concerns

Preparation, cleaning, geocoding and analysis use separate, descriptively named
scripts. Each script has one primary responsibility.

### Path-driven reproducibility

Cleaning, geocoding and analysis accept documented input and output paths.
Users can reproduce results from the project root without editing source code.

### Descriptive names and named constants

Important settings such as `LAYER_ID`, `CODE_FIELD`,
`CHRISTCHURCH_CENTRAL_ID` and `MIN_PRICED_LISTINGS_FOR_RANKING` have explicit
names instead of being repeated as unexplained literals.

### Fail-fast validation

The pipeline checks required columns, dates, coordinate ranges, duplicate keys,
missing SA2 codes and join assumptions. It stops with a clear error instead of
saving a misleading result.

### Secret management

The Koordinates API key is read from an environment variable and never written
to the repository or output. Errors avoid printing the request URL because it
contains the key.

### Caching, retries and controlled concurrency

Successful spatial queries are cached by coordinate. Temporary network errors
are retried, while authentication failures stop immediately. A bounded
`ThreadPoolExecutor` is used because HTTP queries are I/O-bound.

### Defensive joining

The analysis uses `validate="many_to_one"` and checks that the left join does
not change the number of Airbnb listing-month rows.

### Explicit missing-data treatment

Missing prices and missing bond matches remain missing rather than being
silently converted to zero. This prevents unknown values from being treated as
real prices or property counts.

### Documentation location

Source files retain concise docstrings and comments for non-obvious code. The
pipeline design, methods, commands and interpretation limitations are kept in
the README and `docs/` rather than repeated block by block inside the code.

### Idempotent automation

New monthly files follow the `YYYY_MM.csv` naming convention. The update
command replaces rows for those months before appending their refreshed data,
so running the same command twice does not duplicate listing-month records.

## Sanity checks

The primary sanity check queries longitude `172.59658` and latitude
`-43.51148`; layer `98970` must return SA2 code `320800` before batch requests
are allowed. The analysis also checks listing-month uniqueness, bond-summary
uniqueness, join row-count preservation and SA2 uniqueness in the final area
table.

## Interpretation limitations

Airbnb listings and active bonds are different measures. Active-bond counts are
confidentiality-rounded stock values, while Airbnb counts are observed online
listings. A missing bond match is not zero rental properties. Airbnb prices are
asking prices, and dividing weekly bond rent by seven is only a unit conversion.
