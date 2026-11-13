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
| L4 | Open-print exit: sell at the opening price instead of at 09:31:05. | The test fixed in advance in RULES_v3 §3(g) (2026-10-21) stands: switch only if the 09:29 bid beats the 09:31 fill by at least 10bp with t ≥ 2, counted by night. Now n 14, +35bp, t 1.35: not met. | **Pilot withdrawn 11/10, before any order.** On 11/10 I wrote a weaker bar ("not worse on average over 20 mornings") and planned a one-share pilot. The adversarial review was right to reject both: §3(g) already fixes the test, §14 says the lab places no orders, and a zero effect would pass the new bar half the time. What the data says, counted by night: our sells were 0.21% below the official open (t −1.6, 90% interval −0.42% to 0.00%; 26 of 44 nights negative). It is price movement in the 65 seconds after the open, not bad fills, and in 167 earlier mornings that movement averaged +3bp with no link to the prior trend. A repeatable part of 0–10bp is plausible; that is −$1.7 to +$1.7 a month at full size, sign unknown. Robinhood's documents conflict on whether an order queued before 09:30 fills in the opening cross. The shadow log continues. |
| L5 | Single-name risk: split the core between NVDL and an index fund (TQQQ). Brought forward 11/10 after the 11/6→11/9 night cost 15.84. | Pre-registered 11/10 17:20 ET (four criteria; the split's growth no more than 0.010% a night below NVDL-only in both halves; smaller worst night and drawdown in both halves; fewer PAUSE and KILL outcomes; independent re-derivation). | **Rejected 11/10.** Growth per night, NVDL-only / split: +0.205 / +0.135 in 2015–20 and +0.264 / +0.144 in 2021–26, so criterion 1 misses by 7 to 12 times the allowance. Worst night and drawdown were marginally worse for the split in 2015–20 (March 2020 hit TQQQ as hard). KILL probability is a tie; PAUSE triggers fall by about a third and volatility by a quarter. A second implementation reproduced the table to four decimals. Two honest notes: (1) my text said T1 found blends "a wash"; that was true of SOXL only, and T1 had already shown the TQQQ blend 0.025% a night behind, so this test was close to decided before it ran; (2) the fail measures NVIDIA's past premium, a hindsight pick, and does not show that single-name risk is safe. No other weight will be tested: that would be a search after a failed test. The only lever on a night like 11/6 is position size, which is the owner's risk decision. |
| L6 | down_session_skip | ≥ 120 nights, t ≥ 1.5 | Shadow since 11/5. |
| L7 | 09:29 pre-market exit | mean ≥ +10bp and t ≥ 2 | Shadow: n 13, +20bp, t 0.9. Not met. |
| L8 | Crash-open delay (NVDA open ≤ −5% or QQQ ≤ −3%, non-earnings) | ≥ 8 events, mean > 0, t ≥ 2 | Shadow: n 1. |
| L9 | Event tags H1–H3 | Judged 2027-01-11 | Shadow. |
| L10 | Sleeve R4 strike-width test | After options approval: ≥ 20 shadow sessions per width | Waiting on approval. From 2026-11-11 the sleeve shadow is recorded once a day (15:25) instead of three times while the budget above the $80 floor is under $8: with no approval and a budget of about $3, every reading says "nothing fits", and the §12 odds are stale anyway. Three readings a day resume when the budget reaches $8. |
| L11 | A hysteresis band around the trend line (for example, switch only when QQQ is more than 1% through it) | Fewer switches AND g not lower than the plain rule in both halves of 2000–26, for NVDA-2x and ≥ 8 of 11 names | Backlog. The 11/9 check argues against it: the first five nights of all spells below the line still favoured the plain rule (+0.55 log points), and the whipsaw cost sits in spells of 20 nights or fewer, which cannot be picked out in advance. |
| L13 | Exit fills: is the 09:31 sell filled at the limit instead of the bid? (Raised 11/10 after three exits in a row filled at the limit.) | Broker order history, all overnight sells: mean fill at or above the quoted bid | **Closed 11/10, no change.** 82 sells since 9/10: fills average 23bp above the limit, about 6bp above the quoted bid. 26% filled at the limit, and those are orders that rested 1–42 seconds because the quote had fallen before the order arrived. Cutting the quote-to-order gap by one tool turn would be worth about 2bp a night, too little to justify relaxing the intent-before-order rule. **Re-checked 11/10 with 15-second bars** after the review noted that 8 of the last 10 sells filled exactly at the limit: on 11/10 the price was already below the limit when the order arrived (order 09:31:22.7; the 09:31:15–30 bar closed 20.05 against the 20.07 limit; NVDX 11.255 against 11.27), and on 11/6 likewise (24.94 against 25.02). These are genuine rests, and resting filled above the market at arrival. The 11/10 journal remark that the bid stayed above the limit was wrong: the quotes were taken at 09:31:05 and 09:31:36 only. |
| L14 | PAUSE against a smaller DOWN size: when one share costs more than 25% of equity, PAUSE (exactly 1 share) is larger than the DOWN size it outranks. | Decide which the rules intend; if PAUSE should be min(1 share, DOWN size), amend §3(e) | Backlog (clarification). At E 82 and NVDL near 20.3 one share is 24.7% of equity, so it does not bind now. |
| L15 | PAUSE exit condition. As written (§6), PAUSE lasts 5 sessions and then continues until equity is back above the trigger (80% of the 20-session high), which can stretch it to about 4 weeks. Does that extension help or hurt, compared with a fixed 5 sessions? **Pre-registered 2026-11-10 13:10 ET, before any run.** Simulation: overnight-only 2× position, size from the §13 trend rule (0.98 / 0.25), 9bp cost scaled by size, 2000 → 2026-11-06, NVDA plus the 10 names of T6. Variants: P0 no pause; P1 the rule as written (pause size 0.25, minimum 5 sessions, then until equity > trigger); P2 fixed 5 sessions then normal, re-armed only after equity has been above the trigger; P3 threshold only, no minimum. Pause sizes 0.10 / 0.25 / 0.50. | **Change to P2 only if all hold:** (1) P2's compound growth is not lower than P1's in both halves (2000–14 and 2015–26) for NVDA; (2) P2's worst drawdown is no more than 5 points deeper than P1's in either half; (3) the sign of P2 − P1 growth is the same for at least 8 of 11 names; (4) two independent implementations agree. **Drop PAUSE (P0) is not on the table** from this test: it is a risk rule and stays. Anything else: keep the rule as written. | **Closed 11/10: keep the rule as written.** Two independent implementations and the adjudicator's third match night for night. NVDA, P2 − P1 in growth: +0.0064% a night in 2000–14, −0.0014% in 2015–26 (criterion 1 fails); worst drawdown identical (criterion 2 holds); P2 ahead for 5 of 11 names, or 7 on the other reading of the re-arm rule (criterion 3 fails). It is a tie decided by the criteria, not proof that the written rule is better: the two variants differ on 70 of 6,542 nights, and one night (2020-03-06) decides the second half. At $82 the difference is about 5 cents a month. |
| L16 | Does PAUSE still earn its place now that §13 is in force? By-product of L15: with the trend rule on, PAUSE lowered NVDA-2x growth by 0.012% a night over 2000–26 (90% interval −0.023 to −0.004) and trimmed the worst drawdown only from 58.0% to 55.7%; a fixed 10-session pause did better than the written rule in both halves (a sensitivity, not a pre-registered arm). | To be written before any run. PAUSE is a drawdown brake: it is not loosened on a marginal backtest or during a drawdown, and any proposal to weaken it goes to the human first. | Backlog for the 2027-01-11 quarterly review. |
| L17 | Entry at the close instead of 15:52. | RULES_v3 §3(g): entry timing may be reopened only on 120 new nights with t ≥ 2.5. | **Closed 11/10.** The 0.075% entry gap came from funds no longer traded (METU, AAPU, AMZU: −2.67 of the −2.85). NVDL and NVDX entries cost 0.19 over 39 nights (t −0.2). Opened in error against §3(g). |
| L18 | Is there a net edge after realistic costs? The 11/10 post-mortem puts the gross edge at about +0.2% a night without earnings nights (NVDA 2015–26; ten other large technology stocks average +0.04%) and the live fills 0.28% a night behind the official prints (mostly noise, with a repeatable part of perhaps 0–10bp plus about 3bp of fund drag). 44 nights cannot tell an edge of +0.15% from zero (standard error 0.61%). | To be written before any run. No new strategy search in reaction to this loss: each variant tried on this sample raises the chance of adopting noise. | For the 2027-01-11 review, or earlier if the human asks for a redesign. |
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
| 2026-11-10 | Post-mortem of the losses (4 independent analysts + 1 adversarial reviewer, all read-only) | 1 attribution, 1 pre-registered test (L5), mechanics research, edge check | −19.76 on nights = two nights (−21.27) and 42 others (+1.50); by exact dollars: market −9.61, sells below the open −7.29, buys above the close −2.85; timing is not solid by night (t −1.6 and −1.3); gross edge about +0.2% a night, net of live costs about zero to +0.15% | no rule change; records corrected; L5 rejected; L4 pilot withdrawn; L17 closed; L13 re-checked and kept closed |
| 2026-11-10 | L5 split with TQQQ | 3 weights × 2 size rules (+ secondary variants) | growth −0.069 and −0.121 a night against an allowance of −0.010 | **rejected** |
| 2026-11-10 | L15 PAUSE exit condition: as written vs fixed 5 sessions (2 independent runs + adjudicator) | 7 variants × 3 pause sizes × 2 trend settings × 11 names; 1 pre-registered comparison | growth +0.0064 / −0.0014 (halves), drawdown equal, 5 of 11 names | **kept as written** (criteria 1 and 3 not met) |
| 2026-11-10 | L13 exit fills against the quote | 1 | fills average about 6bp above the quoted bid; at-limit fills are rests after a falling quote | no change |
| 2026-11-09 | T8 independent re-derivation (separate agent, own code) | 72 sensitivity cells, 3 bootstraps, 1 placebo, 7 extra checks | every number reproduced; no look-ahead; gain +0.060 a night (year-block 90% interval +0.009 to +0.121); ten nights supply 98% of it; lost in 51 of 82 spells | §13 kept; reclassified as insurance, not edge |

Details and numbers for 11/9: `research/REVIEW-20261109.md`. Scripts and the check's full output: `research/lab/20261109/`. Tool reviews, L15 and the post-mortem of 11/10: `research/lab/20261110/` and `research/POSTMORTEM-20261110.md`.

## Live measurements

| week | nights | live return per night | model | slippage vs quote | trend state (nights UP / DOWN) | note |
|---|---|---|---|---|---|---|
| (first entry due Sat 11/14) | | | | | | |

- 2026-11-13 (ops note, L10): the daily options shadow is skipped while the budget above the $80 floor is under $2.00 (today it was $0.12). Nothing can fit below that, and each reading adds about 8k tokens to the session's memory. No rule changed.
- 2026-11-13 (ops note): crash-open shadow now n=2 (11/9 live, 11/12 marked). Both show a large gain from waiting. Two cases prove nothing, and hold-through was tested and rejected on 11/9. No change.
- 2026-11-13: no pre-registered hypothesis is open for the 11/14 cycle other than L12 (earnings-night blackout). The cycle runs single-threaded because of the usage limit.
