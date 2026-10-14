# Week 9 code review notes

## Review scope

We reviewed the data preparation, cleaning, geocoding and rental-comparison
pipeline for readability, validation, security, reproducibility and clear
program output.

## Changes made

### Descriptive script names

The numbered script names were replaced with names that describe their work:

- `prepare_airbnb_monthly_data.py`
- `clean_airbnb_and_bond_data.py`
- `geocode_airbnb_sa2.py`
- `analyse_airbnb_bonds.py`

Reason: a team member can understand the purpose of each file without knowing
which weekly deliverable originally introduced it.

### Explanatory comments moved to documentation

Long bilingual block-by-block comments were removed from the geocoding and
analysis scripts. The code retains short docstrings and comments only where
they explain a non-obvious implementation choice. Pipeline reasoning now lives
in `docs/DESIGN_PRINCIPLES.md` and the README.

Reason: source code should remain readable, while high-level design decisions
should be maintained in one documentation location.

### API-key use documented

The README now identifies the exact script and environment variable that use
the Koordinates key. The key is read only by `geocode_airbnb_sa2.py` from
`KOORDINATES_API_KEY`; it is never stored in source code, output data, logs or
the cache.

Reason: credentials should not be committed to source control or exposed in
screenshots.

### Deliverable 4 paths documented

The README now lists the cleaning script, both input paths, the output directory
and the complete command that can be run from the project root.

Reason: every team member should be able to reproduce the cleaning outputs
without editing Python source code.

### Named constants retained

The analysis uses named constants for the Christchurch Central SA2 code, the
minimum priced-listing sample and the number of area rows printed.

Reason: descriptive names make important analysis choices easy to find and
avoid unexplained magic numbers.

### Area-summary sanity check retained

The analysis stops if an SA2 location appears more than once in the final area
table.

Reason: duplicate area rows could produce misleading Airbnb and active-bond
counts.

## Existing practices reviewed and retained

- Required columns, dates, listing-month keys and SA2 codes are validated.
- The Koordinates key is read from an environment variable.
- A known coordinate is tested before any batch API requests.
- Successful coordinate queries are cached and temporary failures are retried.
- The rental comparison uses a validated many-to-one left join.
- The joined row count must equal the Airbnb input row count.
- Missing Airbnb prices and missing bond matches are not converted to zero.

## Sanity-check example

Before batch geocoding, we run:

```powershell
python .\geocode_airbnb_sa2.py --test-only
```

The known coordinate (`172.59658`, `-43.51148`) must return SA2-2019 code
`320800`. The test checks the API key, layer ID, coordinate order and response
field. Batch processing stops if the actual code differs from the expected
code.

The observed result was:

```text
Example point returned SA2 code: 320800
Single-point test passed; no batch requests were made.
```

## Interpretation limitations

Airbnb listing counts and active-bond counts are displayed together but are not
identical measures. Airbnb counts are observed online listings, while active
bonds are confidentiality-rounded stock values. A missing bond match does not
mean that an area has zero rental properties. Airbnb prices are asking prices,
not confirmed booking prices.
