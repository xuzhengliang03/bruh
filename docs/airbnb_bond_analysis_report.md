# Airbnb and rental-bond analysis

- Latest Airbnb month: 2026-08; matched to bond quarter starting 2026-07-01.
- Joined listing-month rows: 35,796; unchanged from Airbnb input.
- Listing-month rows with a matching ALL/ALL bond record: 24,551.
- Listing-month rows without a matching bond record: 11,245.
- Christchurch Central (SA2 326600) August 2026 median Airbnb price: NZ$256.00 per night, based on 121 priced listings.

## Largest median short- versus long-term nightly gap

Unavailable: no area has enough priced Airbnb listings and a matching bond rent.

## Counts and interpretation

- August 2026 Airbnb listings: 3,513 across 167 SA2 areas.
- August 2026 listings with a matching bond summary: 0; without: 3,513.
- `area_comparison_latest_month.csv` lists Airbnb counts beside active bonds for each area. Active bonds are a stock measure, while Airbnb counts are observed listings; the two are not identical property populations.
- Bond counts are confidentiality-rounded to base 3, and some bond results are suppressed. Missing bond matches are not zero rental properties.
- Airbnb nightly listing prices are asking prices, not observed bookings. Weekly bond median divided by 7 is only a unit conversion, not an estimate of equivalent whole-property rent.
- The SA2-2019 generalised layer was used for geocoding. Boundary-near points may warrant checking against exact polygons.

## Method

Airbnb month was assigned to its calendar-quarter start. Bond rows were restricted to `dwelling_type=ALL` and `number_of_beds=ALL` to avoid duplicating a listing through bond subcategories. A many-to-one left join retained every Airbnb listing-month. For the area ranking, each listing's nightly gap equals its Airbnb asking price minus the area's weekly bond median divided by 7; the area median of these gaps was ranked, requiring at least 10 priced Airbnb listings.

Sources: [Tenancy Services rental bond data](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/); [Stats NZ SA2-2019 layer](https://datafinder.stats.govt.nz/layer/98970-statistical-area-2-2019-generalised/); [Stats NZ area-code table](https://statsnz.contentdm.oclc.org/digital/api/collection/p20045coll24/id/980/download); [EHINZ SA2 code/name table](https://www.ehinz.ac.nz/assets/Social-Vulnerability-Indicators/2025-SVI-update/Heatmap_SVI2023_SA2.pdf).
