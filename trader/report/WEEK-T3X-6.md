# T3X WEEK 6 (Mon 10/12 – Fri 10/16): Overnight Engine, rules v1.5 → v1.7

**E 103.78 (10/9 close, marked) → 96.91 (10/16 close, night 28 marked): −6.87 (−6.6%) on the week.**
- Realised this week: **−6.51** (nights −6.99, day leg +0.48).
- Campaign since the T3X start: 98.75 → 96.91 (−1.84). Since your original $100: −3.09 (−3.1%). Last week's headline said the campaign was +5.03; this week erased that gain.
- HWM 107.11 (10/12); E is 9.5% below it. PAUSE 85.69, KILL 50.

This was a bad week. Four of the five overnight holds lost money, and the worst came on the night before TSM's earnings. Across our five overnight holds NVDA fell about 5%, while its daytime sessions lost only about 1% (including Friday's −1%): the reverse of the strategy's premise, in one bad week.

A 7-agent read-only audit (files: `research/week6_audit_20261016.json`) found the following:
- Every trade and every cent of cash matches the broker's fills.
- No rule was broken.
- The 9% drawdown is a typical outcome for this strategy. It also fits a strategy with no edge: 27 nights cannot tell the two apart.

## Overnight leg
| night | basket | P&L | note |
|---|---|---|---|
| 23 (10/9→10/12) | METU ×2 + NVDL | **+2.66** | weekend hold; METU +3.14, NVDL −0.48 |
| 24 (10/12→10/13) | METU ×2 + NVDL | **−1.73** | last night of the old basket |
| 25 (10/13→10/14) | NVDX ×5 (v1.5) | **−2.25** | risk-off after the 08:30 data; NVDA −1.9% at the open |
| 26 (10/14→10/15) | NVDL ×2 + NVDX (v1.6) | **−4.90** | TSM reported before the open; NVDA about −2.8% at the open |
| 27 (10/15→10/16) | NVDL ×2 + NVDX | **−0.78** | quiet; NVDA −0.5% at the open |
| 28 (10/16→10/19) | NVDL ×2 + NVDX ×1 | −0.54 marked (open) | weekend hold |

- **Week: −6.99** on 5 closed nights (1 win, 4 losses).
- **Campaign: 27 nights, −4.67.** 11 wins and 16 losses, mean −0.17 per night.
- Live vs plan: −0.24% per night per unit invested, against the +0.30% planning edge. That is about one standard error below plan (z ≈ −1.1), so the gap is not statistically significant.
  - 24 of the 27 nights were the *old* mixed baskets. Only 3 nights so far were NVDA-only (the current rule).
  - On those 3 nights, live results tracked the NVDL model within about 0.45 points per night. The record therefore says almost nothing yet about the current rule.
- Execution was clean. Every overnight order this week filled immediately, with no re-prices and no rejects.

## Day leg (TZA): suspended since 10/15
- **Mon 10/12:** TZA 2 @ 47.38 → 47.62 = **+0.48**. Blocked by PDT on 10/13–10/14. Suspended from 10/15 (rules v1.7).
- **Final live record:** 12 legs, **+3.23**, 7 wins and 5 losses.
- **Shadow log since the suspension** (hypothetical, no orders):

  | day | result |
  |---|---|
  | 10/15 | **−3.99%** (about −$4.08 at the old 2-share size) |
  | 10/16 | **+1.01%** (TP at 10:53; about +$0.99 at 2 shares) |

- The re-entry test is pre-registered and judged only at the 2027-01-11 quarterly review.

## What changed this week, and why
The rules were rewritten 4 times in about 28 hours (10/13–10/14). All rewrites were by the agent, each after a multi-agent adversarial review.
1. **v1.5 → v1.6 (10/13–10/14): the basket is now NVIDIA-only.** The core is NVDL; NVDX fills whatever cash NVDL shares leave over.
   - Why: the old 30-night ranking that chose METU, AMZU and others had no predictive power when tested.
   - NVDA's overnight edge is the best-documented: NVDL ex-earnings +0.29% per night since Dec 2022, t 2.7.
   - The choice of NVDA is partly hindsight, which I disclose.
   - Model estimate for this week (unverified by a second agent): the switch did about $2.6 worse than the old basket would have.
2. **v1.7 (10/14): the daytime TZA trade was turned off.** Long-history tests showed no daytime edge, and the trade roughly quadrupled the odds of hitting PAUSE. On 10/15 the switch-off avoided about −$4.08.
3. **§3(g), the pre-commitment:** no rule changes on short drawdowns. The next review is at 40 live NVDA-only nights (3 done, about mid-December).
4. **10/16 clarifications (no change in behaviour):**
   - **PAUSE basis:** the trigger is 0.80 × the rolling 20-session high of recorded E. The level stays 85.69 until about 11/9.
   - **Journal:** journal.md is the official log.
   - **Time to $200:** an honest estimate is now written down (see the target section below).

## Risk, plainly
- **The single biggest risk is one bad NVIDIA night.** From about 97, an overnight NVDA drop of about 7% would take the account to the PAUSE level (85.69), after which bets shrink to 1 share. Since 2015 that has happened about once a year outside earnings.
- **Odds of hitting PAUSE within the next ~60 sessions:**
  - About 11–40% if the edge is real (the range comes from different historical samples).
  - About 40–54% if there is no edge.
- **Odds of falling to $50 (KILL) within ~250 sessions:**
  - About 0.1–3% with an edge.
  - About 14–16% with no edge.
- **Monday's edge-decay check (§3(f))** already reads **+0.33%/night**, which is positive, so the strategy stays invested.
  - The switch moves the strategy to cash if NVDA's overnight edge fades. Checked on data available each Monday, it last fired in spring–summer 2025 and again in September 2025.
  - It is the protection against a slow 2022-style decline (in 2022 a 2x-NVDA overnight hold lost about 75%).

## The $200 target
- From 96.91 the account needs **+106%**.
- At the planning edge (+0.30% per night on about 86% invested), that takes about **280–310 held nights on average, roughly 1.1–1.25 years.** The bootstrap odds of reaching $200:
  - About 5–9% within 6 months.
  - About 27–45% within 12 months.
  - About 62–87% within 2 years.
- These odds assume the edge is real. With no edge the odds within a year are about 5%.
- **The "6–12 months" target is optimistic.** A lower-risk version (for example about 70% invested) would cut the PAUSE odds but slow growth by about 20–27%. **That trade-off is yours to choose. Tell me if you want it.**

## Next two weeks (calendar verified where marked in the audit)
- **No NVDA blackout until 11/17.** NVDA earnings are after the close that day, so we hold cash that night. The date is per Robinhood; I will recheck it when NVIDIA posts its call notice, expected about late October.
- **Crowded event nights:**
  - 10/21: META, LRCX, TXN after the close.
  - 10/27: FOMC eve plus the SK hynix call at 20:00.
  - 10/28: MSFT, GOOGL, KLAC after the close, then GDP/PCE at 08:30 and the ECB at 09:15.
  - 10/29: AMZN and INTC, then the BoJ overnight.
  - The rules hold through all of these. Only NVDA's own earnings are a blackout.
- **The NVDL 10/28 "ex-date"** in Robinhood's data is probably stale (it is paired with 2023 dates). I will check it before the 10/27 entry.

## Ops
- **Daylight saving ends 11/1.** The scheduled wake-ups were in UTC and would have fired an hour early from 11/2. All 5 now run on New York time with unchanged clock times, and the sleep tools accept ET.
- One-off wake-ups are set for the half-day sessions 11/27 and 12/24 (12:52 ET entries).
- **Incidents this week:**
  - Container reset on the night of 10/13 (recovered from git; tools now live in the repo).
  - A chained-sleep slip on 10/14 at 15:40, caught 1m48s before the entry.
  - Neither cost a trade.
- **Records:** broker order IDs do not match our intent IDs since 10/12. Every order still matches uniquely on symbol, side, quantity, limit and time.
- **Unexplained cash:** a +$0.17 credit with no orders behind it appeared between 9/29 and 9/30. It is noted but not yet explained, and it is in your favour.

## For you to know
- **Trade approvals are OFF.** Orders execute without your sign-off, and all rule changes are agent-written under your "iterate on your tactics" instruction.
- **Taxes:** selling NVDL at a loss at 09:31 and rebuying it at 15:52 creates wash sales. The loss is deferred into the new cost basis, and your 1099 will show adjustments. The dollar amounts are small.
