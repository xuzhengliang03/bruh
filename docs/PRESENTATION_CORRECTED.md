# Simple presentation with corrected month labels

## 1. Show local_data and the verified source notes

Good morning. We have now connected our earlier analyses to one automatic
process. It covers October 2025 to August 2026.

These are the eleven original monthly files. We checked their source dates.
During this check, we found that July and August had been named the wrong way
round. We corrected the names and ran all the analyses again.

## 2. Show update_airbnb_pipeline.py and Terminal

We only need one command: `python update_airbnb_pipeline.py`.

It reads the files, adds the month and source date, selects Christchurch,
cleans the data, adds area codes, updates the rental-bond comparison, and
saves the charts and reports.

The program also checks the files against saved file hashes. This helps us
detect a file with the wrong name before processing it.

## 3. Show the final terminal summary

The eleven New Zealand files contain 542,471 rows. We kept 35,796 rows for
Christchurch. The other 506,675 rows were outside Christchurch.

Each row represents one listing in one month. The same listing can appear
in several months.

July has 3,488 Christchurch listings, and August has 3,513. These are the
corrected numbers. The total is still 35,796.

All 4,100 different coordinates are saved in the local cache. This run needed
no new API calls. We keep the API key outside the code.

## 4. Open processed_data/results_gallery.html

This page brings our ten charts together.

The first two charts show the number of listings and the middle nightly
price in each month. August has the highest listing count. The middle price
was 227 New Zealand dollars in July and 224 dollars in August.

The missing price points from December to February are left empty because
the original files contain no prices for those months.

The next charts show Christchurch prices and days since the last review
across the study period. We also kept the June New Zealand charts so we can
show our earlier analysis.

## 5. Show review summary and June national review summary

For August Christchurch data, the top-review threshold is 184 reviews.
354 listings meet this threshold. Ties can make the selected group slightly
larger than ten percent.

For the earlier June New Zealand analysis, the threshold is 185. There are
5,130 listings in that group, including 343 in Christchurch.

## 6. Show the bond comparison charts and analysis report

We match Airbnb listings and rental-bond data by area code and quarter.
The August middle price in Christchurch Central is 256 New Zealand dollars
per night, based on 121 listings with prices.

There is no matching July-quarter bond data, so we leave August bond values
empty. Empty values do not mean zero rental properties.

For the bond charts, we use June, the latest month with matching bond data.
Holmwood has the largest middle price gap among areas with at least ten
usable price comparisons: about 242 dollars and 71 cents per night.

We divide weekly bond rent by seven to put both prices in daily units.
However, short stays and long-term rentals are different markets, so this
comparison needs care.

## 7. Show pipeline_validation_report.md

We checked that there are no repeated listing-and-month records and no
missing area codes. There are 24,478 rows with usable prices and 24,551 rows
with matching bond data.

We ran the command again. The main output files stayed exactly the same,
and the total row count did not increase.

## 8. Show design document and Trello (only if updated)

We use clear names, separate functions, saved source information and checks
before joining data. Our documents explain the inputs, outputs and decisions.

[Describe the actual completed Trello tasks and each team member's work.
Do not claim the board is updated until the group has checked it.]

Thank you.
