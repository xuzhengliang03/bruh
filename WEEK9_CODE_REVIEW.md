# Week 9 Code Review Notes

## Review scope
1.检查了代码可读性、验证、安全性、可复现性和程序输出
We reviewed the existing data-cleaning, geocoding and analysis
pipeline using the coding practices discussed in Week 9.

The review focused on code readability, validation, security,
reproducibility and clear program output.


## Changes made
### 1. Replaced magic numbers with named constants
We added named constants for:

- the Christchurch Central SA2 location ID;
- the minimum number of priced listings required for ranking;
- the number of area rows displayed in the terminal.

Reason: important analysis settings should have descriptive names and
should be defined in one place. This makes the code easier to
understand and reduces the risk of inconsistent changes.

Coding practice: use descriptive names and avoid magic numbers.
对应
CHRISTCHURCH_CENTRAL_ID = 326600
MIN_PRICED_LISTINGS_FOR_RANKING = 10
DISPLAY_AREA_ROWS = 10

### 2. Added an SA2 uniqueness sanity check
The analysis now checks that each SA2 location ID appears only once in
the final area-comparison table. If duplicate location IDs are found,
the pipeline stops and reports them.
Reason: duplicate area rows could create misleading Airbnb and active
bond counts. It is safer to stop the pipeline than to save an
apparently valid but incorrect result.
Coding practice: fail fast and validate assumptions explicitly.
对应
if areas["location_id"].duplicated().any():
    raise AssertionError(...)

### 3. Added concise regional comparison output
The analysis now displays the ten SA2 areas with the largest Airbnb
listing counts. It also displays:
- the total number of SA2 areas;
- the number of areas with matching bond data;
- the number of areas with more than five priced Airbnb listings.
Reason: users can quickly inspect the main output without printing all
167 rows or manually opening the complete CSV file.
Coding practice: provide concise and useful program output.

这些功能原来已经存在，不是这次新增的
## Existing practices reviewed and retained

### Input validation

The scripts check that required columns exist before processing. They
also validate dates, listing-month uniqueness and the presence of SA2
codes.

### API-key security

The Koordinates API key is read from the
`KOORDINATES_API_KEY` environment variable. It is not stored in the
source code or committed to GitHub.

### API testing and caching

The geocoding script tests one known coordinate before batch
processing. Successful coordinate queries are cached, and temporary
API failures are retried.

### Join validation

The analysis uses a many-to-one left join and checks that the number
of Airbnb listing-month rows does not change after the join.

### Missing-data treatment

Missing Airbnb prices are preserved rather than invented. Missing bond
matches are not interpreted as zero rental properties.

## Verification
记录验证方法
We first checked the Python syntax using:

`python -m py_compile .\deliverable5_analysis.py`

We then ran the complete analysis using:

`python .\deliverable5_analysis.py`

The script completed successfully and reported:

- 28,795 joined listing-month rows;
- 167 SA2 areas in the June 2026 comparison;
- 133 areas with matching bond data;
- 116 areas with more than five priced Airbnb listings.

The number of joined rows remained equal to the number of Airbnb input
rows, and the SA2 uniqueness check did not find duplicate area IDs.

## Interpretation limitations
添加局限说明
Airbnb listing counts and active bond counts are displayed together,
but they are not identical measures.
Airbnb counts are observed online listings. Active bonds are
confidentiality-rounded stock values from the rental bond dataset.
A missing bond value does not mean that an area has zero rental
properties.
Airbnb prices are asking prices rather than confirmed booking prices.
These limitations remain documented in the analysis report。

## Sanity-check example

Before running the batch Koordinates queries, we tested one known
coordinate:

- Longitude: `172.59658`
- Latitude: `-43.51148`
- Expected SA2-2019 code: `320800`
- Actual SA2-2019 code: `320800`

The check was run using:

`python .\deliverable5_geocode.py --test-only`

The single-point test passed, and no batch requests were made.

This sanity check verifies the API key, layer ID, coordinate order and
response field before thousands of API queries are submitted. The
pipeline stops before batch processing if the returned code does not
match the expected value.