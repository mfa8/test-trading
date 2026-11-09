# Lab archive, 2026-11-09: strategy review and its independent check

Scripts and outputs behind `research/REVIEW-20261109.md`. They are kept so that a later lab cycle can re-run them. The raw bar files are not in the repo (19 MB); the scripts read them from a scratch directory, so set the path at the top of `review/load.py` and `verify/vload.py` after re-fetching.

## Contents

- `review/`: the review's own scripts. `load.py` (loader), `t1_blend.py`, `t2_gap.py`, `t4_vol.py`, `t5_trend.py`, `t6_xs.py`, `t7_rot.py`, `t8_2x2.py`.
- `verify/`: the independent re-derivation, written by a separate read-only agent that did not read `review/`. `vload.py` (loader), `verify_t8.py` (main), `verify_extra.py`, `verify_cost.py`, and their outputs `results.txt`, `results_extra.txt`, `results_cost.txt`.

## Rebuilding the data

Day bars from the broker (`get_equity_historicals`, interval `day`, split-adjusted, at most 10 symbols a call). Save each raw tool result as JSON (`data.results[].bars`) under these names:

| file | symbols | range |
|---|---|---|
| `d0a.json` | NVDA QQQ SPY SMH | 2000-01-03 → 2007-12-31 |
| `d0b.json` | NVDA QQQ SPY SMH | 2008-01-02 → 2015-01-02 |
| `d1.json` | NVDA QQQ SPY SMH TQQQ SOXL TECL UPRO | 2015-01-02 → 2020-12-31 |
| `d2.json` | the eight above plus NVDL NVDX | 2021-01-04 → present |
| `x1.json`, `x2.json`, `x3.json` | AMD INTC MU AAPL MSFT | 2000 → 2008, 2009 → 2017, 2018 → present |
| `x4.json`, `x5.json`, `x6.json` | AMZN QCOM TXN AMAT ORCL | same three ranges |

## Known data problems (found by the check)

- NVDA bars up to 2000-10-27 are priced 10x too high (a missing split adjustment). Both loaders drop that stretch through a break filter. Dividing those bars by 10 instead makes the trend rule look slightly better.
- Prices are not dividend-adjusted, so ex-dividend gaps count as overnight losses for dividend payers. Negligible for NVDA.
- The bar for the current day is partial or interpolated until the session completes. Cut the sample at the last completed session.
- SPY has 7 zero-volume bars in 2004. AMD 2002-10-16 shows +39.5% overnight, possibly a bad open print (unverified).
