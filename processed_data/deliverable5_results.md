# Deliverable 5: Airbnb and rental bonds

- Latest Airbnb month: 2026-06; matched to bond quarter starting 2026-04-01.
- Joined listing-month rows: 28,795; unchanged from Airbnb input.
- Listing-month rows with a matching ALL/ALL bond record: 24,551.
- Listing-month rows without a matching bond record: 4,244.
- Christchurch Central (SA2 326600) June 2026 median Airbnb price: NZ$250.00 per night, based on 117 priced listings.

## Largest median short- versus long-term nightly gap

Holmwood (SA2 322600) has the largest median gap among areas with at least 10 priced June Airbnb listings: NZ$242.71 per night.
Its median Airbnb price is NZ$347.00/night and bond median is NZ$730.00/week (NZ$104.29/night); 10 priced Airbnb listings.

## Counts and interpretation

- June Airbnb listings: 3,469 across 167 SA2 areas.
- June listings with a matching bond summary: 2,982; without: 487.
- `area_comparison_latest_month.csv` lists Airbnb counts beside active bonds for each area. Active bonds are a stock measure, while Airbnb counts are observed listings; the two are not identical property populations.
- Bond counts are confidentiality-rounded to base 3, and some bond results are suppressed. Missing bond matches are not zero rental properties.
- Airbnb nightly listing prices are asking prices, not observed bookings. Weekly bond median divided by 7 is only a unit conversion, not an estimate of equivalent whole-property rent.
- The SA2-2019 generalised layer was used for geocoding. Boundary-near points may warrant checking against exact polygons.

## Method

Airbnb month was assigned to its calendar-quarter start. Bond rows were restricted to `dwelling_type=ALL` and `number_of_beds=ALL` to avoid duplicating a listing through bond subcategories. A many-to-one left join retained every Airbnb listing-month. For the area ranking, each listing's nightly gap equals its Airbnb asking price minus the area's weekly bond median divided by 7; the area median of these gaps was ranked, requiring at least 10 priced Airbnb listings.

Sources: [Tenancy Services rental bond data](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/); [Stats NZ SA2-2019 layer](https://datafinder.stats.govt.nz/layer/98970-statistical-area-2-2019-generalised/); [Stats NZ area-code table](https://statsnz.contentdm.oclc.org/digital/api/collection/p20045coll24/id/980/download); [EHINZ SA2 code/name table](https://www.ehinz.ac.nz/assets/Social-Vulnerability-Indicators/2025-SVI-update/Heatmap_SVI2023_SA2.pdf).
