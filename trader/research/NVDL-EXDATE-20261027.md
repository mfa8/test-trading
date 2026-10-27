# NVDL "ex-date 2026-10-28": verification (2026-10-27, read-only workflow wf_676522b1-487)

**Verdict: no NVDL distribution is expected at the 10/28 open. Confidence: high.**

The 10/28 entry in Robinhood's `ex_dividend_date` field is a date stamped across the GraniteShares family. It is not a distribution declared for NVDL.

## Evidence
- **The date is family-wide.** All 16 GraniteShares leveraged single-stock ETFs checked carry ex 2026-10-28.
  - That includes funds that have never paid (TSLR: no amount and no record date).
  - HIPS, the family's monthly income fund, shows 10/28 as simply its next monthly date. COMB shows 2026-12-29.
- **NVDL has paid once in about 3.9 years.** That payment went ex 2023-12-27 (about 10% of NAV). Robinhood's 0.561749 is the same 2023 payout restated per share after the 6:1 (Mar 2024) and 3:1 (Jun 2026) splits.
  - Dec 2024: the official GraniteShares notice lists NVDL at **0.00**.
  - Dec 2025: nothing in the prices and nothing at data vendors.
  - The same data does pick up NVDX's Dec 2024 and Dec 2025 payouts, so the missing NVDL entries are real, not a data gap.
- **No announcement exists.** Nothing from the issuer, an exchange, OCC or the news.
  - The issuer page shows "Next distribution: -". stockanalysis and TipRanks show the next ex-date as unannounced.
  - The only NVDL corporate action in 2026 is the 3:1 split, ex 2026-06-26 (BOX memo 207760).
- **Past 10/27→10/28 nights show no event.** The NVDL − 2×NVDA residual was −0.11% in 2024 and +0.06% in 2025.
- **One argument was rejected.** "Stale record/pay dates next to a new ex-date" is normal in this data feed (QQQ, SPY and TQQQ look the same), so it is not evidence either way.

## Remaining risk and checks
- The issuer's live distribution feed was not readable, and GraniteShares has posted notices on the ex-date itself. A declaration on 10/27 therefore cannot be ruled out entirely; the judge put the tail at 5% or less.
- **After the 10/27 close:** re-pull get_equity_fundamentals for NVDL. A record_date of 2026-10-28, or a new amount, would mean a real declaration.
- **10/28 pre-open:** check NVDL's `adjusted_previous_close` against `previous_close`. A drop equal to X means a distribution of X.
- **10/28 open:** compute r = NVDL gap − 2×NVDA gap and d = NVDL gap − NVDX gap.
  - |r| and |d| at 0.4% or less means normal.
  - Both at −0.5% or below means suspect: look for a matching adjusted_previous_close drop.
- **If a distribution is real:** the holder of record at the 10/27 close (T+1) receives the cash. Per the data-hygiene note in §8, add back only the declared amount; it is not a loss, not a PAUSE input and not a decay signal.

Sources: graniteshares.com NVDL page; the GraniteShares December 2024 distributions notice; stockanalysis.com and tipranks.com NVDL dividend pages; BOX memo 207760; Robinhood get_equity_fundamentals, get_equity_quotes and get_equity_historicals; `research/edge_decay/overnight_thru_20261023.csv`.
