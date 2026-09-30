# Pipeline Design Principles

## AI use

OpenAI Codex was used to help review the pipeline structure and draft
the initial version of this design-principles document.

The team checked the document against the actual Python code and the
intended analysis. The final responsibility for the code, methods and
documentation remains with the team.

## 1. Pipeline inputs

### Raw inputs

The original pipeline begins with:

- monthly Christchurch Airbnb listing CSV files covering October 2025
  to June 2026;
- the Detailed Quarterly Rental Bond dataset published by New Zealand
  Tenancy Services.

The raw Airbnb files contain listing identifiers, price, availability,
room type, minimum nights, neighbourhood, latitude and longitude.

The rental bond data contains quarterly information by location ID,
dwelling type and number of bedrooms, including active bond counts and
weekly rent statistics.

### Prepared inputs for geocoding and analysis

Deliverable 5 uses the cleaned outputs from Deliverable 4:

- `processed_data/christchurch_listings_clean.csv.gz`;
- `processed_data/rental_bond_clean.csv.gz`.

The geocoding step also uses:

- the Stats NZ Statistical Area 2 2019 generalised Koordinates layer,
  layer ID `98970`;
- the `SA22019_V1_00` response field;
- a Koordinates API key supplied through the
  `KOORDINATES_API_KEY` environment variable.

The API key is not stored in the code or committed to GitHub.

## 2. Pipeline outputs

### Cleaning outputs

The cleaning step produces:

- `processed_data/christchurch_listings_clean.csv.gz`;
- `processed_data/rental_bond_clean.csv.gz`;
- `processed_data/CLEANING_REPORT.md`;
- `processed_data/cleaning_summary.json`.

### Geocoding outputs

The geocoding step produces:

- `processed_data/christchurch_listings_with_sa2.csv.gz`;
- `processed_data/geocoding_report.json`.

The local Koordinates cache supports recovery and avoids repeated API
requests. It is an intermediate file rather than a final analysis
output.

### Analysis outputs

The analysis step produces:

- `processed_data/airbnb_bond_joined.csv.gz`;
- `processed_data/area_comparison_latest_month.csv`;
- `processed_data/deliverable5_results.md`.

The joined file contains listing-month records with corresponding bond
summary information when a match is available. The area-comparison
file reports Airbnb counts, prices, active bonds and price-gap measures
by SA2 area for the latest month.

## 3. Main pipeline steps

### Step 1: Clean the Airbnb data

The cleaning script validates required columns, standardises dates and
numeric fields, checks coordinates, removes duplicate listing-month
keys and retains fields required for later analysis.

Missing prices are preserved rather than invented. Latitude and
longitude are retained for geocoding.

### Step 2: Clean the rental bond data

The bond data is restricted to quarters covering the Airbnb study
period. Numeric fields and dates are standardised, invalid values are
handled, and `location_id` and `timeframe` are retained.

### Step 3: Run a single-coordinate API test

Before batch geocoding, the program queries one known coordinate. The
expected SA2-2019 code is `320800`.

Batch processing begins only if the actual result matches the expected
result.

### Step 4: Geocode unique Airbnb coordinates

The program extracts unique latitude and longitude pairs and queries
Koordinates layer `98970`.

Longitude is sent as `x`, latitude as `y`, and the returned
`SA22019_V1_00` value is stored as the Airbnb `location_id`.

### Step 5: Cache and save geocoding results

Successful coordinate results are written to a local cache. This
allows an interrupted run to continue and avoids querying the same
coordinate more than once.

The geocoded Airbnb dataset is saved so later analysis does not require
running the API queries again.

### Step 6: Align the time periods

Airbnb data is monthly, while rental bond data is quarterly. Each
Airbnb month is mapped to the first date of its calendar quarter.

The bond `timeframe` is converted to the same quarter-start format.

### Step 7: Prepare the bond summary

The bond table contains both detailed categories and overall totals.
The analysis keeps rows where dwelling type is `ALL` and number of
beds is `ALL`.

This prevents one Airbnb listing from joining to multiple bond
subcategory rows.

### Step 8: Join the datasets

The datasets are joined using:

- `location_id`;
- quarter start date.

The code uses a many-to-one left join. This retains all Airbnb
listing-month records, including records without a matching bond
summary.

### Step 9: Calculate the regional comparison

For the latest Airbnb month, the program calculates:

- Airbnb listing count;
- number of listings with a valid price;
- median Airbnb nightly asking price;
- active bond count;
- median weekly bond rent;
- median Airbnb-minus-bond nightly price gap.

Weekly bond rent is divided by seven only to place both values on a
daily unit basis.

### Step 10: Save and report the results

The pipeline saves the joined dataset, area-comparison table and
written analysis report. It also prints a concise result summary to
the terminal.

## 4. Coding and software strategies

### Separation of concerns

Cleaning, geocoding and analysis are implemented in separate scripts.
Each script has one main responsibility.

This makes the pipeline easier to understand, test and maintain.

### Descriptive names and named constants

Important analysis settings use named constants, including:

- `CHRISTCHURCH_CENTRAL_ID`;
- `MIN_PRICED_LISTINGS_FOR_RANKING`;
- `DISPLAY_AREA_ROWS`;
- `LAYER_ID`;
- `CODE_FIELD`.

This avoids repeating unexplained magic numbers and strings.

### Fail-fast validation

The pipeline checks required columns, dates, duplicate keys, missing
SA2 codes, join relationships and duplicate area summaries.

When an important assumption is violated, the program stops with a
clear error rather than saving a misleading result.

### Secret management

The Koordinates API key is read from an environment variable. It is
not written into Python source code, reports or GitHub files.

### Caching and recoverability

Coordinate responses are cached. If a geocoding run is interrupted,
the next run only queries coordinates that are not already cached.

### Retry handling

Temporary API and network failures are retried. Authentication and
permission failures stop immediately so that an invalid key is not
repeatedly used.

### Controlled concurrency

The geocoding step uses a `ThreadPoolExecutor` with a limited number
of workers. Concurrent threads are suitable because API queries spend
most of their time waiting for network responses.

The implementation uses concurrent threads, not multiprocessing.

### Reproducibility

Scripts accept input and output paths through command-line arguments
or documented defaults. Prepared datasets and reports are saved so
team members can reproduce later stages without repeating all API
queries.

### Defensive joining

The analysis uses `validate="many_to_one"` during the merge and checks
that the joined row count equals the Airbnb input row count.

This protects against unintended many-to-many joins and accidental row
loss or duplication.

### Explicit missing-data treatment

Missing prices and missing bond matches are kept as missing values.
They are not silently converted to zero.

This prevents unknown values from being interpreted as real prices or
property counts.

### Concise output and documentation

The program prints important summary values rather than the entire
dataset. Detailed results are saved in CSV, JSON and Markdown files.

High-level changes and their reasons are recorded in
`WEEK9_CODE_REVIEW.md`.

## 5. Sanity checks

The primary sanity check uses the following known coordinate:

- longitude: `172.59658`;
- latitude: `-43.51148`;
- expected SA2-2019 code: `320800`.

The test is run with:

`python .\deliverable5_geocode.py --test-only`

The test passed and returned `320800`. No batch requests were made.

The analysis also checks that:

- each listing ID and month combination is unique;
- each bond location and quarter summary is unique;
- the left join does not change the number of Airbnb rows;
- each SA2 location ID appears once in the final area summary.

## 6. Interpretation and design limitations

Airbnb listings and active bonds are not identical property measures.
Airbnb counts are observed online listings, while active bonds are
confidentiality-rounded stock values.

Missing bond matches are not interpreted as zero rental properties.

Airbnb prices are asking prices and are not confirmed booking prices.
The weekly bond median divided by seven is a unit conversion, not a
claim that short-term and long-term rental products are equivalent.

The geocoding step uses the SA2-2019 generalised layer because the bond
dataset uses SA2-2019 geographic definitions. Points close to area
boundaries may require further checking against exact polygons.
