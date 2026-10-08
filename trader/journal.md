2026-10-07T13:24:05Z W-9 09:24 EXIT prep night20 METU1+NVDL1; bridging to 09:31:05
2026-10-07T13:31:46Z W-9 09:31 EXIT night20 filled METU 31.552 (-0.43) NVDL 39.8409 (-0.39) = -0.82; E 104.47 cash; nights 20 net +2.95; no day leg (PDT); flat loop until 15:52
2026-10-07T14:03:08Z W-9 10:04 HB flat; METU 30.28 NVDL 39.96 TZA 47.38 QQQ -0.84% IWM -1.10%; E 104.47 cash
2026-10-07T14:59:07Z W-9 11:00 HB flat; METU 30.45 NVDL 39.50 TZA 47.70 QQQ -0.72% IWM -1.33%; E 104.47 cash
2026-10-07T16:00:00Z W-9 12:00 HB flat; E 104.47 cash; METU -3.9% NVDL -1.4% on day; QQQ -0.4% IWM -1.4%
2026-10-07T17:00:00Z W-9 13:00 HB flat; E 104.47 cash; range-bound midday
2026-10-07T18:00:00Z W-9 14:00 HB flat; E 104.47 cash
2026-10-07T19:00:00Z W-9 15:00 HB flat; E 104.47 cash; tonight add-on likely fits (2 METU + 1 NVDL ~100.8 vs cap 102.38)
2026-10-07T19:40:07Z W-9 15:40 pre-entry check: 0 pos, 0 open orders, BP 104.47; METU 30.18 NVDL 39.41 QQQ -0.33% IWM -1.34%; bridging to 15:51:30
2026-10-07T19:52:01Z W-9 15:52 ENTRY night21 METU x2 @30.24 (lim 30.29) + NVDL x1 @39.5083 (lim 39.57) = 99.99 (96% E); first add-on night; cash 4.48. Note: 15:40 bridge leg exceeded 540s cap -> backgrounded, re-bridged; entry on time
2026-10-07T20:01:36Z W-9 16:02 EOD E 104.65 (day -0.34); night21 marked +0.18; report DAY-20261007 written; Thu: exit 09:31 + day leg #10 (PDT 2/3) + review
2026-10-07T20:01:55Z W-9 NOOP absorbed 15 queued backstop wakes (13:27 exit-0926, wake-a/b 13:38-19:37, 19:48 entry-1548) - all duties done in-session (exit 09:31, entry 15:52, EOD 16:02)
2026-10-07T20:12:30Z W-9 NOOP 16:12 post-close wake (wake-b); EOD already done; holding night21 METU2+NVDL1
2026-10-08T11:48:05Z W-9 07:46 ANALYST 10/8: pos METU2+NVDL1 ok, 0 open orders, E 103.11 (night21 marked -1.40; QQQ -0.63% IWM -0.86% pre-mkt; TZA 48.91 +2.6%); PDT broker-verified 10/1,10/2,10/5 -> prior-4 count 2 -> day leg #10 ALLOWED; earnings PEP/DAL only, basket clear; RULES_v3 §11 sizing v1.4 added pre-open (top-up to q+1 when q*lim<0.85E and (q+1)*lim<=0.98cash). Plan: exit 09:31, TZA 09:32 + TP, entry 15:52, EOD + 10-day review
2026-10-08T12:00:07Z W-9 08:00 HB premkt METU b29.87 NVDL b38.75 TZA 48.84 QQQ -0.66% IWM -0.83%; night21 ~-1.53
2026-10-08T13:00:00Z W-9 09:00 HB premkt E 103.49 (night21 ~-1.16); METU 30.07 NVDL 38.80 TZA 48.72
2026-10-08T13:24:04Z W-9 09:24 EXIT prep night21 METU2+NVDL1; then TZA day leg #10 at 09:32; bridging to 09:31:05
2026-10-08T13:32:25Z W-9 09:31 EXIT night21 METU 2 @30.0767 (-0.33) NVDL @38.48 (-1.03) = -1.35; 09:31:38 DAY LEG #10 TZA 2 @48.2685 (lim 48.44; v1.4 not needed, floor gave 2); TP 48.76 resting (6ac79b4c); day_trades +10/8 (window 10/2-10/8 = 3/3); E 103.11
2026-10-08T14:00:00Z W-9 10:00 HB day leg open TZA 2 @48.2685 bid 48.23, TP 48.76 open; E ~103.03
2026-10-08T14:00:26Z W-9 10:01 RESEARCH NOTE: overnight live 21 nights mean +0.07%/night (sd 1.79, win 9/21) vs backtest +0.61% / 59%; ~1.4 SE short, not conclusive. Last 10 nights net -0.03. Day leg +0.29/active day. GAP FOUND: §1 PAUSE de-risk mode (sell 19:59 ext-hours after 15:52 buy) is a same-day round trip = DAY TRADE -> would hit PDT cap; needs rework. Agenda for WEEK-T3X-5 (Fri) + Mon re-rank: per-segment attribution of live nights; consider shifting capital weight toward day leg.
2026-10-08T14:52:21Z W-9 10:52 DAY LEG #10 TP FILLED 10:48:57 TZA 2 @48.765 (entry 48.2685) = +0.99 (+1.03%), held 77 min; E 104.10 cash. 10-ACTIVE-DAY REVIEW: total +3.60, mean +0.36/day, 6 wins/10; TP v1.3 record 5 hit / 1 miss -> KEEP day leg. Day 10/8 net so far: night -1.35 + day +0.99 = -0.36
