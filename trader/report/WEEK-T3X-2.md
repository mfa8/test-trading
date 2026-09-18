# T3X WEEK 2 (Mon 9/14 - Fri 9/18) — Overnight Engine + Day Leg (v1.2)

**E 98.25 (9/11 close, marked) -> 101.44 (9/18 close, marked): +3.19 (+3.2%) on the week. Campaign 98.75 -> 101.44 = +2.69 (+2.7%). HWM 101.44.**

Low of the campaign was Monday morning: night 3's weekend gap-down (-4.33) took E to 93.42 at the 9/14 close. From there five straight sessions of gains.

## Overnight leg
| night | basket | P&L | note |
|---|---|---|---|
| 3 (9/11->9/14) | NVDL+AMZU | -4.33 | weekend; semis gap-down on AI-slowdown headlines |
| 4 (9/14->9/15) | NVDL x2 + METU | +0.28 | first night after the re-rank swapped AMZU -> METU and added a 2nd NVDL |
| 5 (9/15->9/16) | NVDL x2 + METU | +1.51 | |
| 6 (9/16->9/17) | NVDL x2 + METU | +2.80 | best night of the campaign |
| 7 (9/17->9/18) | NVDL x2 + METU | -0.81 | NVDL -1.02, METU +0.21 |
| 8 (9/18->9/21) | NVDL x2 + METU | +1.45 open | weekend hold |

Closed nights so far: 7, win 4/7, net -0.90 (mean -0.13/night). The week's closed nights (4-7) net +3.78. The night-3 loss is the whole drawdown; excluding it the engine is +3.43 over 6 nights. Sample is still small; the 30-night backtest mean (+0.6%/night) remains the prior.

## Day leg (new this week, v1.2)
Launched Thursday after the intraday decomposition showed the long basket loses money 09:31 -> 15:52 and small-cap inverse TZA gains on average intraday (+0.35%/day, sd 1.9%).
| day | instrument | P&L |
|---|---|---|
| Thu 9/17 | TZA 2 @ 43.1699 -> 44.0717 | +1.80 |
| Fri 9/18 | TZA 2 @ 44.7899 -> 44.9617 | +0.34 |

2/2 wins, +2.14. PDT hard cap holds: 2 day trades used in the rolling window; Monday allowed (3rd), Tue/Wed blocked, Thursday re-opens. Review rule: drop the leg if realised mean < 0 after 10 active days.

## Research decisions this week
- Full overnight hold kept: post-market 16:00-20:00 carries +0.77% of NVDL's +1.21% average night, but 20:00-09:30 still adds +0.43%; post-only would be a PAUSE-mode de-risking, not the default.
- Crypto rejected on data: Robinhood BTC/ETH/SOL bid-ask ~1.9%, wider than any edge at this size.
- Sizing clause v1.1 lets idle cash buy extra shares of #1 (NVDL x2) when the 2-name basket is < 70% of E.

## Execution / ops
- 17 orders this week, 17 fills, 0 rejects. Two exits needed the §5 re-price (NVDL 9/14, METU 9/18); both filled on the second limit.
- ALWAYS-ON loop live since Wed: in-turn 9-min scans through the session, hourly heartbeat commits; the 5 crons stay as backstop and are absorbed as NOOPs.
- Container rebuilt on a stale checkout over last weekend; recovered with a fast-forward merge. Sync check now part of the Monday analyst wake.

## Risk state
E 101.44 · KILL 50 · PAUSE 81.15. Deployed 94.7% overnight, 2-3 whole shares. Max realised single-night loss -4.33 (-4.4%).

## Next week
- Mon 07:45: re-rank both legs (overnight universe; inverse candidates TZA/NVDQ/SOXS). Check MUU 9/30, AMZU 10/29, METU 10/28 blackouts.
- Mon: exit 09:31, day leg #3 09:32 (last allowed until Thu), entry 15:52. Tue/Wed: no day leg.
- Target check: $200 needs +97%; at the week-2 run rate that is far off, so the levers are (a) keeping the day leg if it survives its 10-day review and (b) compounding whole shares as E grows past the next share price.
