# T3X WEEK 8 (Mon 10/26 – Fri 10/30): engine v1.7 unchanged; a bad AMZN/INTC night wiped out a good week

**E 95.69 (10/23 close, night 33 marked) → 94.82 (10/30 09:32, all cash): −0.87 (−0.9%) on the week.**
- Realised this week: **−1.19**, from five overnight exits (N33–N37): 3 wins, 2 losses. The day leg is off.
- Campaign since the T3X start: 98.75 → 94.82 (−3.93). Since your original $100: −5.18 (−5.2%).
- HWM 107.11; E is 11.5% below it. PAUSE 85.69 (E is 10.7% above it), KILL 50.

## Overnight leg
| night | basket | P&L | NVDA close→open | note |
|---|---|---|---|---|
| 33 (10/23→10/26) | NVDL ×3 | **+1.80** | +1.02% | weekend hold |
| 34 (10/26→10/27) | NVDL ×2 + NVDX | **+1.27** | +1.07% | |
| 35 (10/27→10/28) | NVDL ×2 + NVDX | **+1.22** | +0.91% | FOMC eve |
| 36 (10/28→10/29) | NVDL ×3 | **−0.75** | −0.47% | tagged: MSFT/GOOGL/META after the close on FOMC day; GOOGL −11% |
| 37 (10/29→10/30) | NVDL ×3 | **−4.73** | −2.23% | tagged: AMZN/INTC after the close; INTC −25%, AMD −9% pre-market |
| 38 (10/30→11/2) | _filled in at EOD_ | | | weekend hold |

- **Week: −1.19 on 5 closed nights.** The three untagged nights made +4.29; the two earnings-tagged nights lost 5.48.
- N37 was the second-worst live NVDA-2x night (after N26, TSM, −5.61%). NVDA was −3.3% at 07:47 and −2.75% at our 09:31 exit; NVDL was −5.4% from its close.
- **Campaign: 37 nights, −7.28.** 16 wins and 21 losses.
- **Execution was clean.** Every order filled at or better than its limit on the first try; there were no re-prices this week. The ledger reconciles to the broker to the cent.

## Why the live record is negative (week-8 audit, independently verified)
**Live NVDA-2x-only nights (N25–N37): 13 nights, −$10.53, mean −0.84% per night.**
- Against zero, t is −1.03. Against the +12bp planning edge, t is −1.17. Against the +0.30% plan, t is −1.39.
- 13 nights cannot separate "edge" from "no edge". It would take roughly 400 nights at +0.30%, or about 2,400 at +12bp, to reach t = 2. The 40-night review in December will not settle it either; only the §3(f) edge-decay check and the §6 PAUSE should act on it.

**Where the shortfall comes from:**
- About **80% is NVDA's own nights.** On these 13 nights 1× NVDA averaged −0.26% overnight, against a long-run +0.14%. A perfect 1.9× copy of NVDA would have lost $7.79.
- About **20% (−$2.75, −0.26% per night, t −1.34)** is live minus model. Nearly all of that is the first minute after the open: the move from the opening print to 09:31 cost −$3.34 (11 of 13 nights negative). Our fills against the 09:31 price were +$0.41, slightly better than the market.
- The 164-night timing study (10/21) found the open print and 09:31 equal on average (−0.6bp). The first-minute fade is a September–October effect so far.
- The only executable alternative is a 09:29 pre-market sale. Its shadow log (n = 7) averages +7bp with t ≈ 0.5, well short of the pre-registered +10bp and t ≥ 2. **No change.**

**Would holding past 09:31 on a gap-down day like today have helped?** No, on the evidence.
- Gaps of −2% to −3% (like today's −2.2%) have not reliably recovered after 09:31; since 2022 the 09:31→10:00 move is about 0.
- Only crash opens of −5% or worse rebound (2019+: +4.7% at 2× by 10:00, n = 16, t 3.3; without the top 3 events, +2.8%). That stays a pre-registered shadow rule, judged at the 2027-01-11 review.
- Today NVDA kept falling after 09:31 (−3.5% by 10:24), and NVDL traded below our 29.89 exit all morning.

**Being flat during the day helped again.** NVDA's day sessions moved +1.36%, −0.17%, −2.06% and −0.33% (Mon–Thu). Being in cash saved $2.05 net, and about $0.9 more by mid-morning Friday.

## Risk, plainly (bootstrap from E 94.82; verifier reproduced it)
| | with the long-run edge | with zero edge |
|---|---|---|
| P(PAUSE within 20 sessions) | ~17% | ~21% |
| P(reach $200 within 12 months) | ~24% | ~7% |
| P(KILL at $50 within 12 months) | ~6% | ~20% |
| median E after 12 months | ~$124 | ~$85 |

- A single night triggers PAUSE at 85.69 only if NVDA falls 5.3% or more overnight. That happens about 1.8 times a year.
- **PAUSE level schedule** (0.80 × the 20-session high, if there are no new highs): 85.69 through 11/6, 84.65 on 11/9, 82.94 on 11/10, 80.95 from 11/11 to 11/17, and 80.72 from 11/18.

## Ideas tested this week (no rule changes)
1. **Fuller exposure.** Choose the whole-share NVDL/NVDX mix closest to 98% of E, instead of NVDL first plus at most one NVDX. Average invested would rise from 0.90 to about 0.97. That adds about 3 points to the $200 odds and 1.5–3 points to the KILL odds, and it only helps if the edge is real. Not before the 40-night review.
2. **Crash-open exit delay.** Exit at 10:00 instead of 09:31 when NVDA opens 5% or more down. This is the strongest candidate, but it was found after the fact and three events carry about half of its gain. It stays a shadow rule.
3. **The options sleeve** is the real lever for bigger gains (about 35% vs 19% odds of $200, with KILL odds of 8% vs 3%). It is waiting only on your options approval.

## Audit (8 agents, read-only; each auditor checked by an independent verifier)
- **Ledger:** 14 broker orders, 14 logged intents, no orphans. The cash path ends at the broker's 94.82 with 0.00 unexplained.
- **Rules:** 0 violations. Every limit, size, time, blackout and PAUSE check passed.
- **Fixed:**
  - The N37 entry was written as 31.47; the broker average is 31.4667. The P&L records already used the right figure. The narrative records and the related marks (+0.34, not +0.33) are now corrected.
  - Two citation slips in the DAY reports.
- **Process gaps I'm closing from today:**
  - Write the 15:40 pre-entry checks and the post-order open-order check to the journal, not only to the terminal.
  - Quote NVDX in the exit shadow even on nights we don't hold it.
  - Never chain two sleeps (10/27).

## Shadow logs (no orders)
- **Pre-market exit (§5), 7 days:** the 09:29 bid averaged +7bp vs our fill (t ≈ 0.5); 09:25 ≈ 0bp. Today's +74bp was the best day so far. The switch test is not met.
- **Day-leg TZA, 11 legs:** mean −0.72% gross (t −1.15). It stays suspended.
- **Options sleeve, 6 days (16 snapshots):** the Jan-15 300/310 spread was the pick in 11 of them and has been stable for the last 6. Today's budget fell to 14.82 with E, and 300/310 still fits (limit 0.11).

## Next week
- **Sun 11/1:** daylight saving ends. The crons are already in ET.
- **Mon 11/2:** §3(f) edge-decay check (the preview is +0.32% per night, t 1.34, so the leg stays on); exit night 38. PLTR and ON report after the close.
- **Tue 11/3:** US midterm election day. AMD, SMCI, ANET and ALAB report after the close, a semis-peer night. Tagged; the engine holds as normal.
- **Wed 11/4:** QCOM and ARM report after the close (tagged).
- **Fri 11/6:** the Jan-15-2027 expiry reaches 70 days. From 11/9 the sleeve shadow moves to the Feb-19-2027 monthly, which needs new contract IDs.
- **Tue 11/17:** NVDA earnings. That night we hold cash.

## For you to know
- **Action needed:** apply for options on account 8334 (Level 3 preferred): https://applink.robinhood.com/upgrade_options?account_number=445788334. Nothing in the options plan trades until the approval shows on the account.
- **Open questions from 10/22, each with a default:**
  - Do you accept the odds? Default: yes, run the plan once approved.
  - At $200, keep the engine running (default) or go to cash?
  - Keep the $80 floor (default) or lower it to $70?
  - Note: at E 94.82 the $80 floor leaves a $14.82 sleeve budget.
- **Trade approvals are OFF:** orders execute without your sign-off.
