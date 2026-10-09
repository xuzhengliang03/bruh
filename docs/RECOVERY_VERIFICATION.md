# Verified recovery results

Data scope: October 2025–August 2026. September is excluded.

| Check | Result |
|---|---:|
| National monthly input records (listing-month rows, not unique homes) | 542,471 |
| Rows filtered outside Christchurch | 506,675 |
| Christchurch listing-month records retained | 35,796 |
| Invalid-period rows removed | 0 |
| Invalid-coordinate rows removed | 0 |
| Duplicate ID/month rows removed | 0 |
| Final duplicate ID/month records | 0 |
| Final missing SA2 records | 0 |
| Unique coordinate pairs | 4,100 |
| API requests on repeat | 0 |
| Usable price records | 24,478 |
| Price histogram records (0–1,000) | 24,261 |
| Usable nonnegative review-age records | 30,738 |
| Records with matching bond summary | 24,551 |
| Records without matching bond summary | 11,245 |
| Usable price-gap records | 15,471 |
| Raw bond records | 226,080 |
| Bond records outside matching quarters | 198,868 |
| Prepared bond records | 27,212 |

Missing fields do not make an entire record useless: usable sample sizes
depend on the analysis. Filtering outside Christchurch is scope selection,
not a finding that those national records are invalid.

Repeat corrected-source runs produced identical core dataset and monthly
summary hashes. All nine historical clean months were independently compared
with the previous clean file and remained unchanged (28,795 rows).

National June top-review threshold is 185; 5,130 listings qualify, of which
343 are in Christchurch. The latest Christchurch (August) threshold is 184;
354 listings qualify. These are different populations and should not be mixed.

## Code changes relative to the currently installed project

Line comparison uses Python difflib; it excludes documentation and installer.

| File | Added | Removed |
|---|---:|---:|
| update_airbnb_pipeline.py | 24 | 1 |
| pipeline_outputs.py | 21 | 6 |
| Total | 45 | 7 |

The earlier completion package added other functionality. These counts cover
this source-recovery correction only. Git's final diff may group lines
differently; use submitted-commit statistics for the final code-change total.
