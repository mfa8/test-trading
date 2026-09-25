# T3X WEEK 3 (Mon 9/21 - Fri 9/25) — Overnight Engine + Day Leg (v1.2)

**E 101.44 (9/18 close, marked) -> 100.11 (9/25 close, marked): -1.33 (-1.3%) on the week. Campaign 98.75 -> 100.11 = +1.36 (+1.4%). HWM 103.56 (9/21).**

A flat-to-down week after week 2's +3.2%. The overnight engine had one strong weekend night and four small losers; the day leg gave back its early gains twice on midday small-cap reversals.

## Overnight leg
| night | basket | P&L | note |
|---|---|---|---|
| 8 (9/18->9/21) | NVDL x2 + METU | +3.57 | weekend hold; NVDL +1.46, METU +2.11 |
| 9 (9/21->9/22) | NVDL+METU+NVDX | -0.29 | METU -0.80 faded its spike; NVDL/NVDX +0.51 |
| 10 (9/22->9/23) | NVDL+METU+NVDX | -0.29 | NVDA legs -0.74, METU +0.45 |
| 11 (9/23->9/24) | NVDL+METU+NVDX | -0.46 | NVDA legs -1.04, METU +0.58 (re-priced once) |
| 12 (9/24->9/25) | NVDL+METU+NVDX | -0.99 | METU -1.43 after an +8.9% day; NVDA legs +0.44 |
| 13 (9/25->9/28) | NVDL+METU+NVDX | +0.09 open | weekend hold |

Week's closed nights (8-12): +1.54 net, 1 win / 4 losses. Campaign closed nights: 12, net +0.64; excluding night 3 (-4.33) the engine is +4.97 over 11 nights. Four straight small losers is the first losing streak since the re-rank; the NVDA legs are net -0.83 over nights 9-12 and METU is net -1.20, with METU's daily range now 4-9% making single-share exposure to it lumpy.

Correction: the 9/22 and 9/23 day reports quoted the closed-night tally as -1.77; the recorded night returns sum to +1.63 through night 11 and reconcile to equity. Arithmetic slip, corrected in the 9/24 journal.

## Day leg
| day | instrument | P&L | path |
|---|---|---|---|
| Mon 9/21 | TZA 2 @ 44.29 -> 43.9601 | -0.66 | |
| Thu 9/24 | TZA 2 @ 45.67 -> 45.5201 | -0.30 | +2.10 at 11:50, IWM bounced 0.7% 12:14-12:22 |
| Fri 9/25 | TZA 2 @ 45.3787 -> 45.1101 | -0.54 | +1.50 at 10:06, IWM bounced 0.7% 11:58-12:06 |

Realised after 5 active days: [1.8, 0.34, -0.66, -0.3, -0.54] = +0.64. Review at 10 active days (drop if mean < 0). Two data points of a pattern worth testing: TZA's gain peaks late morning and is gone by 15:49. Monday's analyst wake will backtest an earlier exit (open -> 12:00 vs open -> 15:49) on 30 days of intraday bars before touching the rule.

PDT: round trips 9/21, 9/24, 9/25 -> Mon 9/28 window (9/22-9/28) holds 2, so Monday is allowed; Tue 9/29 window (9/23-9/29) holds 3 -> blocked. Friday's day leg fired after a fills-based recount showed 9/18 had rolled out of the window; Thursday's note that Friday was blocked had miscounted.

## Research / rule changes this week
- Sizing clause v1.2 (9/21): when a further whole share of #1 no longer fits under 0.98E, a lower-priced same-underlying product of #1 (NVDX for NVDL) may be added as a partial unit. Used every night since; deployment 86-90% of E instead of ~70%.
- Weekly re-rank 9/21 kept NVDL/METU (overnight) and TZA (day leg).

## Execution / ops
- 36 orders this week, all filled, 0 rejects, 1 re-price (METU exit 9/24). Every entry and exit filled within 0.2s of placement except that one.
- ALWAYS-ON loop ran every session 09:26 -> 16:02 at 8-minute cadence (9-minute sleeps were hitting the 560s command cap and getting backgrounded), hourly heartbeat commits, backstop crons absorbed as NOOPs.
- One scripting bug (format string in the 9/24 15:49 state update) delayed two journal lines by one commit; no order impact.

## Risk state
E 100.11 · KILL 50 · PAUSE 82.85 (0.80 x HWM 103.56). Deployed 88.7% overnight, 3 whole shares. Max realised single-night loss remains -4.33 (night 3).

## Next week
- Mon 07:45: re-rank both legs (overnight universe; inverse candidates TZA/NVDQ/SOXS/SPXS); backtest day-leg early exit; check MUU 9/30 blackout (not held), AMZU 10/29, METU 10/28.
- Mon: exit 09:31, day leg #6 09:32, entry 15:52. Tue: no day leg (PDT). Wed 9/30: MU earnings pm (MUU not in basket, no action).
- Target check: $200 needs roughly +100% from here. The engine's realised run rate over 12 nights (+0.05/night net, +0.45/night ex night 3) does not get there; the levers remain the day leg surviving its review, an earlier day-leg exit if the backtest supports it, and compounding whole shares as E grows.
