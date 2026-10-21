# Execution-timing study: 2026-10-21 (read-only workflow wf_f7a3b25d-17f; 2 studies, each with an adversarial verifier)

**Verdict: keep the 09:31:05 exit and the 15:52 entry.** Both verifiers rebuilt the headline numbers from their own Robinhood pulls and their own code, and the numbers matched to 0.1bp.
- Expected gain from any timing change today: about $0 per night.
- Full output: `exec_timing_20261021.json`.

## Data
| Item | Detail |
|---|---|
| 5-minute bars | From 2026-02-23 |
| 1-minute bars | From 2026-09-08 |
| Earlier history | Robinhood returns only interpolated bars before these dates; verified by both agents |
| Sample | 164 non-earnings nights (Feb 23 to Oct 20) |
| NVDA earnings nights excluded | 02-25, 05-20, 08-26 (reported after the close) |
| Exact 1-minute subset | 31 nights |

## Exit (NVDL; bp vs the 09:31:05 proxy, gross)
| Exit time | bp | t |
|---|---|---|
| 08:00 | −4.7 | |
| 09:15 | −7.5 | −1.3 |
| 09:25 | −4.4 | −0.8 |
| 09:29:59 | −0.9 | |
| 09:30 open print | −0.6 | |
| 09:35 | +1.6 | |
| 09:45 | −8.1 | |
| 10:00 | −7.4 | |

- **Pre-market spreads:** half-spread about 6–10bp for NVDL and 9–27bp for NVDX. The estimate comes from journal bids, so it is thin.
- **Net:** a pre-market exit loses about 10–13bp per night, roughly −$0.09 to −$0.11.
- **The recent open fade is real but local.** Over 31 exact nights, 09:29 beat the 09:31 fill by about +24bp (t 2.1).
  - By month: September +5bp, October +47bp.
  - It does not survive a correction for about 10 candidate times.
  - The 133 earlier mornings showed open→09:35 at +7bp.
- **Gap rule ("sell pre-market if the gap is above 1%"):** the sign flips between sub-periods. It is data-mined, so it is not adopted.
- **Live calibration:** our 09:31 exit fills sit at the 09:31 1-minute OHLC4 (NVDL +0.3bp, n=24).
  - There were 2 rest-and-re-price exits (9/14 and 10/19). Amortized they cost about −7bp per night.

## Entry (NVDL; bp vs the 15:52 price; negative = a cheaper entry)
| Entry time | bp | t |
|---|---|---|
| 15:30 | +3.9 | |
| 15:45 | −0.4 | |
| 15:55 | −1.2 | |
| 15:59 | −2.5 | −0.5 |
| Official close | −1.6 | |
| 16:05 (post-market) | −4.3 | |
| 16:15 | −4.2 | |

- **Largest |t|** in any independent rebuild was about 1.06.
- **The small "later is cheaper" tilt** comes from 4 index-rebalance or expiry closes (3/20, 5/29, 6/26, 9/18). Excluding them, 15:52→close is −0.3bp.
- **The 5-minute reference is biased** about 3bp in the direction that flatters later entries.
- **Power:** the minimum detectable effect is about 15bp, so effects of 5–10bp cannot be ruled out.
- **Practical cost of entering later:** a 15:59 entry would lose the 15:55 re-price and 15:58 cancel safety loop. Post-market NVDX trades in only about 40% of minutes.
- **Overnight decomposition** (NVDL, 142 nights; total ≈ +31bp on the 5-minute exit proxy):

  | Segment | bp |
  |---|---|
  | close→16:15 | −0.2 |
  | 16:15→17:00 | +4 |
  | 17:00→20:00 | +6.6 |
  | 20:00→04:00 | +11 |
  | 04:00→09:25 | +12 |
  | 09:25→exit | −2 |

  - The RULES_v3 §1 claim of "+0.77%/night post-market" (25 nights) is corrected.
  - 15:52→open is about +20bp (t 1.0): about 0 in Feb–Jul and about +55–62bp in Aug–Oct. The edge is weaker and more regime-dependent than the 0.30% planning edge implies. This is consistent with the §3(f) trailing-120 reading of +0.33 (t 1.4) and the week-6 audit.

## Adopted (RULES_v3 §5, §3(g), 2026-10-21)
1. **Shadow log only, no orders.** Record NVDL/NVDX bid and ask at 09:25, 09:29 and 09:31:05, plus the fill time and price.
2. **Pre-registered tests at the 40-night review:**
   - **Pre-market exit:** switch to a 09:29 exit only if mean(09:29 bid − 09:31 fill) ≥ +10bp with t ≥ 2.
   - **Entry timing:** reopen only on ≥120 new nights with a drift beyond ±10bp and t ≥ 2.5.
   - **Wider first exit cap / re-quote:** judged at the same review.
3. **Correction:** RULES_v3 §1's post-market decomposition is corrected.
