# Pipeline results and row accounting

Status: AVAILABLE_DATA_CHECKS_PASSED

## Row accounting

- previous_clean_rows: 35796
- rows_replaced: 35796
- retained_previous_rows: 0
- replacement_clean_rows: 35796
- net_row_change: 0
- raw_month_rows: 542471

## Cleaning decisions for refreshed raw months

- rows_removed_outside_christchurch: 506675
- rows_removed_invalid_period: 0
- rows_removed_missing_or_invalid_coordinates: 0
- nonpositive_prices_set_missing: 0
- invalid_minimum_nights_set_missing: 0
- invalid_availability_set_missing: 0
- duplicate_listing_month_rows_removed: 0

## Bond cleaning

- rows_before: 226080
- rows_removed_invalid_timeframe: 0
- rows_removed_outside_matching_quarters: 198868
- rows_with_negative_counts_set_missing: 0
- rows_with_nonpositive_rent_set_missing: 0
- duplicate_key_rows_removed: 0
- rows_after: 27212

## Analysis usability and checks

- total_rows: 35796
- duplicate_id_month_rows: 0
- missing_sa2_rows: 0
- valid_price_rows: 24478
- price_histogram_rows: 24261
- valid_review_age_rows_available_raw_only: 30738
- bond_matched_rows: 24551
- bond_unmatched_rows: 11245
- valid_price_gap_rows: 15471
- latest_month: 2026-08
- latest_comparable_bond_month: 2026-06

## Latest review ranking (Christchurch only)

{'month': '2026-08', 'population': 'Christchurch City', 'threshold': 184.0, 'qualifying_rows': 354, 'valid_review_count_rows': 3513, 'note': 'Ties at threshold can include more than 10%.'}

## Largest gap in the latest comparable bond month

{'month': '2026-06', 'location_id': 322600, 'median_gap_nzd_per_night': 242.71428571428572}

## Missing inputs

None for implemented data analyses.

## Interpretation

Missing prices or bond matches are not zero. Review statistics cover only the listed raw months. Price histogram limits apply to display only; high prices remain in the clean data. Bond rent divided by seven is a unit conversion across different rental markets.

## Manual course evidence

Git collaboration, Orange workflow demonstration, Māori data-governance slides, Trello and Week 12 questionnaires require separate evidence. Data checks do not certify these tasks.