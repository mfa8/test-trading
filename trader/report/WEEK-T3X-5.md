# T3X WEEK 5 (Mon 10/5 – Fri 10/9) — Overnight Engine + Day Leg (v1.3, §11 sizing v1.4)

**E 102.73 (10/2 close, marked) → 103.78 (10/9 close, marked): +1.05 (+1.0%) on the week. Campaign 98.75 → 103.78 = +5.03 (+5.1%). HWM 105.29 (10/6), PAUSE 84.23, KILL 50.**

A flat-to-positive week that leaned on the day leg again. The 10/5 re-rank basket (METU + NVDL) made +0.26 net on its five closed nights. The day leg made +1.06 on three active days.

## Overnight leg
| night | basket | P&L | note |
|---|---|---|---|
| 18 (10/2→10/5) | METU+AAPU | +0.39 | weekend hold; last AAPU night (METU +0.75, AAPU −0.35) |
| 19 (10/5→10/6) | METU+NVDL | +1.31 | first night of the new basket; NVDA +1.7% pre-open |
| 20 (10/6→10/7) | METU+NVDL | −0.82 | futures −0.7/−0.9%; selling at 09:31 still beat the close by about 1.5 |
| 21 (10/7→10/8) | METU ×2 + NVDL | −1.35 | first add-on night (96% of E); NVDA weak from the open, NVDL −5.7% on the day |
| 22 (10/8→10/9) | METU ×2 + NVDL | +0.73 | down-day entry; pre-market +1.9 faded to +0.73 by the open |
| 23 (10/9→10/12) | METU ×2 + NVDL | −0.19 open | weekend hold |

- Week's closed nights: **+0.26**, 3 wins / 2 losses.
- Campaign: **22 closed nights, net +2.33**; excluding night 3 (−4.33), +6.66.
- **Live vs backtest:** mean +0.10% per night (sd 1.75), 10 wins in 22, against a backtest of +0.61% and 59%.
  - The shortfall is about 1.3 standard errors: not conclusive, but it has persisted for five weeks.
  - With twice the deployment, the bad nights have also become twice as costly. Exposure rose from ~69% to ~94% of E on 10/7 because the §3 add-on now fits at METU ≈ 30.
- Pattern this week: pre-market marks repeatedly overstated what the 09:31 exit captured (10/9: +1.9 marked → +0.73 realised; 10/7: +0.18 at 16:01 → −1.35 at the open). The §1 attribution put about 63% of the edge in the 16:00–20:00 post-market window, which a 09:31 exit only partly keeps.

## Day leg
| day | instrument | P&L | path |
|---|---|---|---|
| Mon 10/5 | TZA 2 @ 45.75 → 46.21 | +0.92 | TP 09:43, held 12 min |
| Tue 10/6 | – | – | PDT blocked (TZA +2.3% that day) |
| Wed 10/7 | – | – | PDT blocked (TZA +3.9% that day) |
| Thu 10/8 | TZA 2 @ 48.2685 → 48.765 | +0.99 | TP 10:48; hold-to-close would have been −1.00 |
| Fri 10/9 | TZA 2 @ 47.4199 → 46.9924 | −0.85 | TP missed by 5c (high ~47.85); 15:49 sell; hold-to-close −0.60 |

- Week: **+1.06** on 3 active days.
- **10-active-day review (10/8): KEEP.** It stood at +3.60, mean +0.36. After Friday: **+2.75 over 11 days, mean +0.25**, 7 wins in 11.
- Take-profit record: 4 hits / 2 misses. The two misses missed by 3c and 5c.
- The PDT cap cost the two biggest inverse days of the week (TZA +2.3% Tue, +3.9% Wed). Neither could be traded.

## Rule changes this week (agent-authored manual)
- **§11 sizing v1.4** (Thu 10/8, written before the open): if `floor(0.95 × cash / limit)` leaves the leg below 85% of E, add one share when it fits under 0.98 × cash. Not triggered yet; TZA sized to 2 shares on its own on all three days.
- **Ops:** `hb.py` now caps each sleep at 480s, and exact-time bridges assert `d<500`. Zero overruns since Thursday morning; one caught and split Friday.

## Gaps found
- **§1 de-risk mode is a PDT trap.** Selling at 19:59 in extended hours after a 15:52 buy is a same-day round trip, so every use would count as a day trade. It cannot be the designated PAUSE fallback as written; it needs a rework before PAUSE can ever trigger.
- **Pre-market vs 09:31 gap.** No rule acts on large pre-market marks. An extended-hours sell before 09:30 of a position bought the previous day is *not* a day trade, so a pre-market take-profit is PDT-safe. **Research item for Monday:** test from historicals whether a pre-market exit (e.g. 08:00–09:25 limit at +X%) beats the 09:31 exit on the last 30 nights.

## Execution / ops
- 36 orders this week (10 exits, 3 day-leg buys, 3 TPs, 1 TP cancel, 1 day-leg 15:49 sell, 10 entries, 8 Friday/Thursday as counted in the DAY reports). **0 rejects, 0 re-prices.**
- One NVDL exit rested 20s at its limit before filling. Every entry filled inside 0.2s at or better than its limit.
- ALWAYS-ON loop ran 07:46 → 16:02 every session, with 8-minute scans and hourly heartbeat commits.
- One GitHub 500 (Wed 13:00) was recovered on the 13:07 retry. One container restart (Thu, overnight) caused no data loss. 45 backstop wakes were absorbed as no-ops.

## Risk state
- E 103.78, with night 23 (METU 2, NVDL 1) open over the weekend at 93% of E. Max realised single-night loss is still −4.33 (night 3).
- PAUSE 84.23 · KILL 50. Drawdown from HWM: −1.4%.

## Next week
- **Mon 10/12 07:45 re-rank** of both legs over 30 nights, plus:
  1. Overnight-leg review: live vs backtest, per-segment attribution of live nights, and the pre-market-exit test above.
  2. Rework the §1 de-risk mode to something PDT-safe.
  3. Day-leg instrument re-rank (TZA vs SPXS/SQQQ/NVDQ/SOXS), and whether a TP of 0.8–0.9% would have caught the two 3–5c misses without hurting the hits.
- Mon: exit night 23 at 09:31, day leg #12 (allowed), entry at 15:52. Tue/Wed: no day leg (PDT). Thu 10/15: day leg allowed.
- Earnings: META and NVDA clear this week. Semis ASML 10/14 am and TSM 10/15 am could move NVDA overnight (not a blackout under §3; watch). METU 10/28 (tent.), NVDL 11/17.
- **Target check:** $200 needs +93% from here. The realised run rate is about +1.0 per week (overnight +0.10/night; day leg +0.25/active day at ~3/week).
  - At this pace the target is out of reach; the levers have to change, not just persist.
  - Monday's research is aimed at the two biggest leaks:
    1. Overnight gains that fade before the open.
    2. Inverse days lost to the PDT cap.
  - Compounding alone won't close the gap.
