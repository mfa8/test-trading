# The lab: backlog and ledger (RULES_v3 §14)

The lab is the engine's self-improvement loop. It runs every Saturday at 14:23 ET (scheduled task `t3x-lab-weekly`) and whenever the human asks. It places no orders.

## The cycle

1. **Measure.** Score the week's fills against the model: return per night, slippage against the quote, each shadow log.
2. **Hypothesis.** Pick at most one test from the backlog. Write its pass criteria here before running it.
3. **Test.** Long history first, costs included.
4. **Decide.** Adopt, reject or keep as a shadow.
5. **Record.** Add the result to the ledger, failures included. Add new ideas to the backlog.

## Adoption bar

A rule changes only if all of these hold:

- The effect has the same sign in at least two non-overlapping sub-periods of long history.
- It survives realistic costs.
- An independent re-derivation from the raw data agrees.
- A rollback criterion is written down first.
- The number of variants tried is stated next to the result.

## Limits

- A change takes effect at the next entry, never mid-hold.
- At most one rule change a week.
- No change on fewer than 120 live nights of P&L alone.
- Off limits: the hard rules (account 8334 only, never 3273, never a transfer), KILL, the $80 floor and 0.20 share (§12(j)), human directives, the scheduler.

## Backlog

| id | Hypothesis | Pass criteria (pre-registered) | Status |
|---|---|---|---|
| L1 | Trend-filter audit: on DOWN nights the quarter position beats the full-size counterfactual in compound terms | Quarterly: the 2000 → present re-run still shows the rule ahead of always-full for NVDA-2x and for ≥ 8 of 11 names. Live shadow is audited, not decisive. | Live shadow from night 45. First review 2027-01-11. |
| L2 | Own-trend variant: also cut size when NVDA or SMH is below its own average | Only if the "both" or "either" rule beats the QQQ rule in both halves of history at the review | Shadow (logged nightly). The 11/9 check found "either" best for 7 of 11 names but the QQQ rule best for NVDA. |
| L3 | Fractional execution: the dollar-based top-up and fractional sell fill within 5bp of the quote mid | First 10 fractional fills: mean cost vs mid ≤ 5bp; otherwise drop the top-up when it is under $10 | Opens with the first fractional order. |
| L4 | Open-print exit: sell in the opening auction instead of at 09:31:05 | ≥ 60 mornings of the 09:30 print vs the 09:31:05 fill; mean ≥ +5bp and t ≥ 2 | Not started; needs a print log. |
| L5 | Blends (NVDA-2x with SOXL or TQQQ) | At the 2027-01-11 review: a blend beats NVDA-2x on g in both halves of 2015–26 and on the real-ETF period, AND it meets the RULES_v3 §3(b) bar for a second name (executable 15:52→09:31 prices, ex-earnings, volume ≥ 1M, score lead ≥ 0.06 at two consecutive Monday re-ranks) | Backlog. T1 says a wash. |
| L6 | down_session_skip | ≥ 120 nights, t ≥ 1.5 | Shadow since 11/5. |
| L7 | 09:29 pre-market exit | mean ≥ +10bp and t ≥ 2 | Shadow: n 13, +20bp, t 0.9. Not met. |
| L8 | Crash-open delay (NVDA open ≤ −5% or QQQ ≤ −3%, non-earnings) | ≥ 8 events, mean > 0, t ≥ 2 | Shadow: n 1. |
| L9 | Event tags H1–H3 | Judged 2027-01-11 | Shadow. |
| L10 | Sleeve R4 strike-width test | After options approval: ≥ 20 shadow sessions per width | Waiting on approval. |
| L11 | A hysteresis band around the trend line (for example, switch only when QQQ is more than 1% through it) | Fewer switches AND g not lower than the plain rule in both halves of 2000–26, for NVDA-2x and ≥ 8 of 11 names | Backlog. The 11/9 check argues against it: the first five nights of all spells below the line still favoured the plain rule (+0.55 log points), and the whipsaw cost sits in spells of 20 nights or fewer, which cannot be picked out in advance. |
| L13 | Exit fills: is the 09:31 sell filled at the limit instead of the bid? (Raised 11/10 after three exits in a row filled at the limit.) | Broker order history, all overnight sells: mean fill at or above the quoted bid | **Closed 11/10, no change.** 82 sells since 9/10: fills average 23bp above the limit, about 6bp above the quoted bid. 26% filled at the limit, and those are orders that rested 1–42 seconds because the quote had fallen before the order arrived. Cutting the quote-to-order gap by one tool turn would be worth about 2bp a night, too little to justify relaxing the intent-before-order rule. |
| L14 | PAUSE against a smaller DOWN size: when one share costs more than 25% of equity, PAUSE (exactly 1 share) is larger than the DOWN size it outranks. | Decide which the rules intend; if PAUSE should be min(1 share, DOWN size), amend §3(e) | Backlog (clarification). At E 82 and NVDL near 20.3 one share is 24.7% of equity, so it does not bind now. |
| L15 | PAUSE exit condition. As written (§6), PAUSE lasts 5 sessions and then continues until equity is back above the trigger (80% of the 20-session high), which can stretch it to about 4 weeks. Does that extension help or hurt, compared with a fixed 5 sessions? **Pre-registered 2026-11-10 13:10 ET, before any run.** Simulation: overnight-only 2× position, size from the §13 trend rule (0.98 / 0.25), 9bp cost scaled by size, 2000 → 2026-11-06, NVDA plus the 10 names of T6. Variants: P0 no pause; P1 the rule as written (pause size 0.25, minimum 5 sessions, then until equity > trigger); P2 fixed 5 sessions then normal, re-armed only after equity has been above the trigger; P3 threshold only, no minimum. Pause sizes 0.10 / 0.25 / 0.50. | **Change to P2 only if all hold:** (1) P2's compound growth is not lower than P1's in both halves (2000–14 and 2015–26) for NVDA; (2) P2's worst drawdown is no more than 5 points deeper than P1's in either half; (3) the sign of P2 − P1 growth is the same for at least 8 of 11 names; (4) two independent implementations agree. **Drop PAUSE (P0) is not on the table** from this test: it is a risk rule and stays. Anything else: keep the rule as written. | **Run 11/10 (ad hoc cycle; PAUSE triggered this morning).** A change, if any, cannot take effect before the 11/18 entry (one rule change a week). |
| L12 | Earnings blackout (§3(d)): hold a reduced position through NVDA earnings nights instead of cash. Prompted by the 11/9 check: 47 earnings nights supplied about 44% of always-full's 2015–26 growth. | At least 60 earnings nights since 2005. Sizes tested: 0.25 and 0.5 only. Mean log growth per earnings night > 0 in both halves and with the best 3 nights removed; the worst night at that size costs less than 20% of E; an independent re-derivation agrees. | Backlog. Candidate for the first cycle, 11/14. The 11/17 earnings night stays in cash whatever the test says (one rule change a week); earliest effect February 2027. |

## Ledger

| date | test | variants tried | result | decision |
|---|---|---|---|---|
| 2026-10-13 | BASKET: NVDL alone vs an equal-weight 14-name basket | 2 | +0.46% vs +0.43% a night | NVDA-2x only (v1.6) |
| 2026-10-21 | EXEC-TIMING: alternative exit and entry times | about 12 | none beat 09:31:05; entry \|t\| ≤ 1.06 | no change |
| 2026-11-09 | T1 vehicle and blends | 6 | a wash | rejected; L5 |
| 2026-11-09 | T2 gap-down hold-through | 4 | \|t\| < 2, sign inconsistent | rejected |
| 2026-11-09 | T4 states known at the close | 8 states × 2 symbols | only the 200-day average survived | 7 rejected, 1 carried forward |
| 2026-11-09 | T5 200-day average out of sample (ETFs 2000–14) | 3 ETFs × 4 lengths | positive except 2010–14 | supports |
| 2026-11-09 | T6 cross-section, own average, 4 sizes | 11 names × 4 sizes | quarter beats full for 10 of 11 | supports |
| 2026-11-09 | T7 rotation when NVDA is below its average | 5 | worse than cutting size | rejected |
| 2026-11-09 | T8 own trend × market trend | 5 rules | the QQQ rule is best in every period | **adopted as §13 (v1.8)** |
| 2026-11-09 | T9 hold through the day in uptrends | 4 periods | negative in 3 of 4 | rejected |
| 2026-11-10 | Pre-flight review of the v1.8 tools before first use (3 lenses + verification) | 25 findings examined | no high defect; 1 medium (documents omitted the case with no whole-share order) fixed the same morning; 3 low in `trend.py` | tools hardened in scratch, deployed only after a second review |
| 2026-11-10 | L13 exit fills against the quote | 1 | fills average about 6bp above the quoted bid; at-limit fills are rests after a falling quote | no change |
| 2026-11-09 | T8 independent re-derivation (separate agent, own code) | 72 sensitivity cells, 3 bootstraps, 1 placebo, 7 extra checks | every number reproduced; no look-ahead; gain +0.060 a night (year-block 90% interval +0.009 to +0.121); ten nights supply 98% of it; lost in 51 of 82 spells | §13 kept; reclassified as insurance, not edge |

Details and numbers for 11/9: `research/REVIEW-20261109.md`. Scripts and the check's full output: `research/lab/20261109/`. Tool reviews of 11/10: `research/lab/20261110/`.

## Live measurements

| week | nights | live return per night | model | slippage vs quote | trend state (nights UP / DOWN) | note |
|---|---|---|---|---|---|---|
| (first entry due Sat 11/14) | | | | | | |
