# Pipeline Design Principles

## AI Used

ChatGPT was used to help create this design principles document.  
The document was checked against the actual Python code to make sure it matches the pipeline.

## 1. Inputs to the Pipeline

The pipeline uses two main prepared datasets:

- Christchurch Airbnb listing data with SA2 location IDs
- New Zealand rental bond data

The Airbnb data includes information such as listing ID, month, SA2 location ID and nightly price.

The rental bond data includes quarter, SA2 location ID, active bond counts and median weekly rent.

## 2. Outputs from the Pipeline

The main outputs are:

- `airbnb_bond_joined.csv.gz`
- `area_comparison_latest_month.csv`
- `deliverable5_results.md`

These outputs provide the joined Airbnb and rental bond data, an SA2-level comparison table, and a short written summary of the analysis.

## 3. Main Steps in the Pipeline

The main steps are:

1. Read the cleaned Airbnb and rental bond datasets.
2. Check that required columns and valid data are present.
3. Convert the Airbnb month and bond date into matching quarters.
4. Keep the overall rental bond summary rows.
5. Join the Airbnb and rental bond data using SA2 location ID and quarter.
6. Calculate Airbnb and rental price comparisons.
7. Group the latest Airbnb month by SA2 area.
8. Run sanity checks on the final area table.
9. Save the results and print a short summary in the terminal.

## 4. Coding and Software Strategies

Several coding practices are used in the project.

### Descriptive Names and Named Constants

Important values use clear names instead of unexplained numbers.

For example:

```python
CHRISTCHURCH_CENTRAL_ID = 326600
```

This makes the code easier to understand and maintain.

### Validation and Fail-Fast Behaviour

The code checks required columns, duplicate records and join assumptions.

If an important assumption is not satisfied, the program stops instead of continuing with incorrect results.

### Sanity Checks

The final area table is checked to make sure each SA2 location ID appears only once.

This helps detect possible problems in the data processing or aggregation.

### Clear Output

The program prints a short summary of the main results in the terminal.

This allows the user to quickly inspect the results without opening the full CSV files.