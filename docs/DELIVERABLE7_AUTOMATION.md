# Deliverable 7 automation

## Goal

Update the previous Christchurch Airbnb pipeline with the July and August 2026
New Zealand summary downloads using one command.

## Inputs

- `local_data/2026_07.csv` — Inside Airbnb summary `listings.csv` dated
  12 July 2026.
- `local_data/2026_08.csv` — Inside Airbnb summary `listings.csv` dated
  13 August 2026.
- Existing prepared listings, SA2 matches and rental-bond data in
  `processed_data/`.
- `KOORDINATES_API_KEY` in the current terminal session.

## One-command update

```powershell
python .\update_airbnb_pipeline.py
```

## Automated stages

1. Discover files whose names follow `YYYY_MM.csv`.
2. Attach the verified month and scrape date.
3. Apply the existing Christchurch cleaning rules.
4. Replace those months in the previous clean listing dataset, preventing
   duplicates when the command is rerun.
5. Build a local coordinate cache from previously geocoded rows.
6. Run the known-point Koordinates test and query only unseen coordinates.
7. Re-run the Airbnb/rental-bond comparison using the latest month.
8. Save updated listing-count and median-price plots plus a monthly table and
   machine-readable update summary.

## Safeguards and sanity checks

- Required previous outputs must exist before the update starts.
- Only explicitly configured scrape dates are accepted.
- Listing ID and month must remain unique.
- A coordinate cannot map to two different SA2 codes.
- The known coordinate must return SA2 `320800` before batch requests begin.
- The existing geocoder and analysis retain their coordinate, row-count and
  many-to-one join validation.
- Re-running the command replaces July/August rows instead of appending copies.

## Expected interpretation

The latest Airbnb month is August 2026. The current cleaned rental-bond input
does not contain a July 2026 quarter, so August Airbnb rows may have missing
bond matches. Missing bond values are reported as unavailable, not zero.

## Presentation checklist

- Show the two input files in `local_data/`.
- Show the single update command.
- Point out that previous SA2 matches are reused and only new coordinates call
  the API.
- Show the successful terminal summary and the two updated PNG plots.
- Explain the idempotence and duplicate-key sanity check.
