# T3X WEEK 4 (Mon 9/28 - Fri 10/2) — Overnight Engine + Day Leg (v1.3)

**E 100.11 (9/25 close, marked) -> 102.73 (10/2 close, marked): +2.62 (+2.6%) on the week. Campaign 98.75 -> 102.73 = +3.98 (+4.0%). HWM 103.56 (9/21).**

A week that the day leg carried. The re-ranked overnight basket (METU + AAPU) lost money on three of its four closed nights while the new +1% take-profit rule fired twice in two live attempts and turned the day leg from a drag into the week's best contributor.

## Overnight leg
| night | basket | P&L | note |
|---|---|---|---|
| 13 (9/25->9/28) | NVDL+METU+NVDX | +2.00 | weekend hold; NVDL +2.08, NVDX +1.19, METU -1.27 |
| 14 (9/28->9/29) | METU+AAPU | -0.62 | first night of the new basket; AAPL gapped -1.5%, AAPU -1.42, METU +0.80 |
| 15 (9/29->9/30) | METU+AAPU | -0.10 | METU -0.66, AAPU +0.56; both exits price-improved |
| 16 (9/30->10/1) | METU+AAPU | -1.11 | AAPL -1.5% at the open again; AAPU -1.24, METU +0.13; AAPU exit filled at the limit as the re-price cancel was rejected |
| 17 (10/1->10/2) | METU+AAPU | +1.26 | 08:30 data pop, QQQ +1.2% at the open; METU +0.89, AAPU +0.37 |
| 18 (10/2->10/5) | METU+AAPU | +0.06 open | weekend hold |

Week's closed nights (13-17): +1.43 net, 2 wins / 3 losses. Campaign closed nights: 17, net +2.07; excluding night 3 (-4.33) the engine is +6.40 over 16 nights.

AAPU is the question. Across its four nights it is -1.42, +0.56, -1.24, +0.37 = **-1.73**, while METU over the same nights is +0.80, -0.66, +0.13, +0.89 = +1.16. The 9/28 ranking put AAPU second on a 30-night mean that was built before two -1.5% AAPL opening gaps in three sessions. The METU+AAPU basket also deploys only ~74% of E (two whole shares, no cheaper same-underlying product for either), versus 86-90% under the NVDL/NVDX stack. Monday's re-rank re-scores with these four nights included; no mid-week override was made.

## Day leg
| day | instrument | P&L | path |
|---|---|---|---|
| Mon 9/28 | TZA 2 @ 46.5299 -> 46.3501 | -0.36 | first v1.3 TP at 47.00; day high 46.97, missed by 3 cents; 15:49 sell |
| Tue 9/29 | - | - | PDT blocked |
| Wed 9/30 | - | - | PDT blocked |
| Thu 10/1 | TZA 1 @ 47.42 -> 47.90 | +0.48 | TP filled 09:40, held 7 min; hold-to-close would have been -0.48 |
| Fri 10/2 | TZA 2 @ 45.4368 -> 45.90 | +0.93 | TP filled 11:17, held 106 min; TZA was -1.0% on the position at 10:46 before the midday small-cap fade |

Week +1.05 over 3 active days. Realised after 8 active days: [1.80, 0.34, -0.66, -0.30, -0.54, -0.36, 0.48, 0.93] = **+1.69**, mean +0.21. Review at 10 active days (drop if mean < 0): two more active days needed, and the leg is now comfortably positive. TP record: 2 hits / 1 miss. Both hits would have been losers or near-flat as hold-to-close legs.

PDT: round trips 9/28, 10/1, 10/2. Mon 10/5 window (9/29-10/5) holds 2 -> day leg #9 allowed. Tue 10/6 window (9/30-10/6) would hold 3 after Monday -> blocked; Wed 10/7 (10/1-10/7) holds 3 -> blocked; Thu 10/8 (10/2-10/8) holds 2 -> allowed. The three-in-five cap means roughly 3 day legs per week.

## Research / rule changes this week
- Rule v1.3 (9/28): resting +1.0% take-profit limit sell placed immediately after the day-leg buy fills; cancel and sell at 15:49 if unfilled. Backtest on 30 days of TZA 10-minute bars: hold-to-close score 0.31 (win 50%) vs TP score 0.50 (win 73%). Live: 2 for 3, +1.41 on the two fires vs -0.48 and roughly +0.5 for the hold-to-close counterfactuals.
- Weekly re-rank 9/28: METU 0.30, AAPU 0.28, NVDL 0.20, NVDX 0.15, MUU 0.04 -> METU + AAPU. NVDL dropped after the NVDA legs lost 0.83 over nights 9-12 (they then made +3.27 on night 13, their last night).

## Execution / ops
- 29 orders this week (10 exits, 3 day-leg buys, 3 TPs, 1 TP cancel, 1 exit cancel attempt rejected-as-filled, 10 entries, 1 recount), 0 rejects on placement, 0 re-prices needed. Every entry filled inside 0.2s of placement at or inside the limit.
- One lesson from 10/1: a cancel rejected with "cannot be cancelled at this time" means the order is filling; re-query before any further action.
- ALWAYS-ON loop ran every session 07:46 -> 16:02 at 8-minute cadence with a TP status check while a day leg was open; hourly heartbeat commits; backstop crons absorbed as NOOPs. One container restart (Tue 10:14-11:04) left the loop dark for 50 minutes while flat; recovered clean. Three long combined sleeps were backgrounded by the 540s command cap, none affecting order timing; sleeps now split into legs of 8 minutes or less.

## Risk state
E 102.73 (night 18 marked +0.06 open) · KILL 50 · PAUSE 82.85 (0.80 x HWM 103.56). Deployed 73.1% overnight into the weekend, 2 whole shares. Max realised single-night loss remains -4.33 (night 3).

## Next week
- Mon 10/5 07:45: re-rank both legs with nights 14-17 included. AAPU under review; candidates to replace it include NVDL/NVDX (back to the 3-share stack if they re-rank above AAPU), MUU after its earnings, AMZU (blackout 10/29). Day leg: TZA vs NVDQ/SOXS/SPXS, and whether a 2-share TZA leg at ~95% of cash remains the right size.
- Mon: exit night 18 09:31, day leg #9 09:32 with TP, entry 15:52. Tue/Wed: no day leg (PDT). Thu 10/8: day leg #10 -> 10-active-day review.
- Blackouts: METU 10/28 (tent.), AAPU 10/29 (tent.), AMZU 10/29 (tent.), NVDL 11/17.
- Target check: $200 needs roughly +95% from here. Realised run rate: overnight +0.12/night net over 17 nights (+0.40 ex night 3); day leg +0.21/active day over 8. At 5 nights + 3 day legs a week that is roughly +1.2/week, far short. The levers remain the same: a basket that deploys closer to 90% of E, the TP day leg surviving its review, and compounding whole shares as E grows.
