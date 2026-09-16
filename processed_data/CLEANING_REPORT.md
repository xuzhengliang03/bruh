# Deliverable 4 cleaning report

## Result

| Dataset | Rows before | Rows after | Columns before | Columns after |
|---|---:|---:|---:|---:|
| Christchurch listings | 28795 | 28795 | 21 | 12 |
| Rental bonds | 226080 | 27212 | 12 | 13 |

The listing data covers 2025-10 to 2026-06. The bond data keeps the corresponding quarter starts: 2025-10-01, 2026-01-01, 2026-04-01.

## Monthly listing coverage

| Month | Rows | Valid prices | Available listings | Median nightly price (NZD) |
|---|---:|---:|---:|---:|
| 2025-10 | 2991 | 2821 | 2863 | 155 |
| 2025-11 | 3047 | 2835 | 2905 | 166 |
| 2025-12 | 3180 | 0 | 3049 | n.a. |
| 2026-01 | 3057 | 0 | 3012 | n.a. |
| 2026-02 | 3190 | 0 | 3115 | n.a. |
| 2026-03 | 3227 | 3059 | 3130 | 237 |
| 2026-04 | 3273 | 3069 | 3144 | 229 |
| 2026-05 | 3361 | 3149 | 3207 | 215 |
| 2026-06 | 3469 | 3195 | 3262 | 214 |

Price is entirely missing in the supplied source for 2025-12, 2026-01 and 2026-02. Those rows remain available for property-count analysis but must not be used for price comparisons. No prices were imputed.

## Listing decisions

- Kept `latitude` and `longitude`, as required, and removed 0 rows with missing or invalid coordinates.
- Kept one record per listing and month; removed 0 duplicate keys.
- Kept positive price outliers instead of choosing an unsupported cutoff. 153 prices above NZD 1,000 per night remain.
- Added `has_price` and `is_available` so price coverage and available-property counts are explicit.
- Kept only fields needed to identify a listing, locate it, classify the room, compare price, and count availability. Names, host details, licence, review metrics and the constant Christchurch group field were dropped. This reduces file size and avoids carrying unrelated personal/free-text fields.
- Preserved missing prices and minimum-night values. Filling them would invent information and bias later comparisons.

## Bond decisions

- Kept `timeframe` and `location_id`, as required.
- Filtered to the three quarters overlapping the listing period. This removed 198868 rows.
- Preserved missing and negative source location identifiers, with `location_id_status` marking `missing`, `source_special_code`, or `valid`; their meaning is not guessed.
- Changed non-positive weekly rents to missing in 0 rows because a zero/negative weekly rent is not analytically usable. Other missing rent values remain missing and were not imputed.
- Standardised column names, dates, integer count types and the missing bedroom label. Removed 0 duplicate keys.

## Consequences and limitations

- Airbnb `price_nzd_per_night` is an advertised nightly short-stay price. Bond rent is a weekly long-term tenancy measure. Convert units and explain the market difference before comparing them.
- `availability_365 > 0` indicates that at least one future day is open in the Airbnb calendar; it is not the number of occupied or vacant long-term homes.
- Tenancy Services applies fixed random rounding to base 3 and suppresses results for fewer than five bonds. Exact small-area counts cannot be recovered.
- Tenancy Services states that recent records are provisional during its bond-system migration and may be revised. Recent periods may not be directly comparable with earlier periods.
- `location_id` uses the source's SA2-2019 geography. Joining listing coordinates to bond areas requires an SA2-2019 spatial boundary or another defensible crosswalk; neighbourhood names should not be joined directly to numeric IDs.
