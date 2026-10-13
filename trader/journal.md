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
2026-10-08T14:52:31Z W-9 CORRECTION: TP v1.3 record is 4 hit / 1 miss (9/28 miss; 10/1,10/2,10/5,10/8 hit), not 5/1 as logged at 10:52
2026-10-08T15:00:08Z W-9 11:00 HB flat E 104.10; METU 30.13 NVDL 39.28 TZA 48.92 QQQ -0.40% IWM -0.88%
2026-10-08T16:00:00Z W-9 12:00 HB flat E 104.10
2026-10-08T17:00:00Z W-9 13:00 HB flat E 104.10; tech fading (QQQ -1.2%, NVDL -3.8%, METU -1.4%) -> down-day entry tonight (§1: next night ~2x avg after down session)
2026-10-08T18:00:00Z W-9 14:00 HB flat E 104.10; NVDL -6.1% METU -1.5% QQQ -1.7% on day
2026-10-08T19:00:00Z W-9 15:00 HB flat E 104.10; entry22.py ready (2 METU + 1 NVDL ~96.8 = 93% E)
2026-10-08T19:40:09Z W-9 15:40 pre-entry check: 0 pos, 0 open orders, BP 104.10; METU ~30.03 NVDL ~37.18 (-6.0% day) QQQ -1.5%; bridging to 15:51:30 (2 legs)
2026-10-08T19:52:01Z W-9 15:52 ENTRY night22 METU x2 @30.0999 (lim 30.15) + NVDL x1 @37.2999 (lim 37.38) = 97.50 (94% E); cash 6.60; down-day entry (NVDL -5.7% day)
2026-10-08T20:01:59Z W-9 16:02 EOD E 104.18 (day -0.47: night21 -1.35, day leg +0.99, night22 mark +0.08); TP worth +1.99 vs hold-to-close; report DAY-20261008 written; Fri: exit 09:31 + day leg #11 + entry + WEEK-T3X-5
2026-10-08T20:02:18Z W-9 NOOP absorbed 15 queued backstop wakes 10/8 (13:26 exit-0926, wake-a/b 13:37-19:37, 19:48 entry-1548) - all duties done in-session (exit 09:31, day leg 09:31-10:48, entry 15:51, EOD 16:02)
2026-10-08T20:12:38Z W-9 NOOP 16:12 post-close wake (wake-b); EOD already done; holding night22 METU2+NVDL1
2026-10-09T11:47:11Z W-9 07:46 ANALYST 10/9: pos METU2+NVDL1 ok, 0 open orders; E 105.80 pre-mkt (night22 +1.64: NVDL b38.30 vs 37.30, METU b30.42 vs 30.10) - above HWM 105.29; QQQ +0.84% IWM +0.40% TZA 47.21; PDT broker-verified 10/5,10/8 -> prior-4 = 2 -> day leg #11 ALLOWED; earnings: basket clear thru 10/15 (ASML 10/14, TSM 10/15 semis noted). Plan: exit 09:31, TZA 09:32 + TP, entry 15:52, EOD, WEEK-T3X-5
2026-10-09T12:00:00Z W-9 08:00 HB premkt METU b30.51 NVDL b38.36 (night22 ~+1.88); QQQ +0.89%
2026-10-09T13:00:00Z W-9 09:00 HB premkt E 105.73 (night22 ~+1.56); premarket gains fading slightly (QQQ +0.64%)
2026-10-09T13:24:04Z W-9 09:24 EXIT prep night22 METU2+NVDL1 (~+1.9 pre-mkt); then TZA day leg #11 at 09:32; bridging to 09:31:05
2026-10-09T13:33:12Z W-9 09:31 EXIT night22 METU 2 @30.2301 (+0.26) NVDL @37.77 (+0.47; rested 20s at limit, filled 09:31:40, no re-price) = +0.73; pre-mkt mark was +1.9, open faded. 09:32:33 DAY LEG #11 TZA 2 @47.4199 (lim 47.54); TP 47.90 resting (6ac8ed02); day_trades +10/9 (window 10/5-10/9 = 3/3; Mon 10/12 prior-4 10/6-10/9 = 2 -> allowed; Tue 10/13 blocked if Mon taken)
2026-10-09T14:00:00Z W-9 10:00 HB day leg open TZA 2 @47.4199 bid ~47.40, TP 47.90 open (high so far ~47.85 at 09:49)
2026-10-09T15:00:00Z W-9 11:00 HB day leg open TZA 2 @47.4199 ~flat, TP 47.90 open; E ~104.8
2026-10-09T16:00:00Z W-9 12:00 HB day leg open TZA 2 @47.4199 bid ~47.22 (-0.4%), TP 47.90 open; small caps firm (IWM +0.4%)
2026-10-09T17:00:00Z W-9 13:00 HB day leg TZA 2 @47.4199 bid 47.06 (-0.76%), TP 47.90 open; E 104.13; small caps +0.5% (inverse leg working against)
2026-10-09T18:00:00Z W-9 14:00 HB day leg TZA 2 @47.4199 bid 46.89 (-1.1%), TP 47.90 open; no intraday stop per §11; E 103.80
2026-10-09T19:00:00Z W-9 15:00 HB day leg TZA 2 @47.4199 bid 46.81 (-1.3%), TP open -> 15:49 close likely; E 103.62
2026-10-09T19:40:07Z W-9 15:40 pre-close check: TZA 2 held (TP 6ac8ed02 open @47.90), bid 46.99 (-0.91%); METU 30.03 NVDL 36.92; plan 15:49:00 cancel TP -> verify -> sell; 15:52 entry night 23
2026-10-09T19:52:05Z W-9 15:49 DAY LEG #11 close: TP cancel 15:49:05 verified cancelled; sold TZA 2 @46.9924 (lim 46.90) = -0.86 (-0.90%); TP missed (high ~47.85 at 09:49, 5c short); day leg total +2.74 over 11 active days, mean +0.25. 15:51:43 ENTRY night23 METU x2 @30.0299 (lim 30.08) + NVDL x1 @36.8899 (lim 36.96) = 96.95 (93% E); cash 7.02; weekend hold
2026-10-09T20:02:33Z W-9 16:02 EOD E 103.78 (day -0.40: night22 +0.73, day leg -0.85, night23 mark -0.19); week +1.05 (+1.0%); DAY-20261009 + WEEK-T3X-5 written; trades.csv D11 pnl normalised to -0.85 (=2x-0.4275); Mon 10/12: re-rank + overnight review + pre-mkt exit test + §1 de-risk rework
2026-10-09T20:03:08Z W-9 NOOP absorbed 15 queued backstop wakes 10/9 (13:27 exit-0926, wake-a/b 13:37-19:38, 19:49 entry-1548) - all duties done in-session (exit 09:31, day leg 09:32-15:49, entry 15:51, EOD+WEEK 16:02)
2026-10-09T20:12:35Z W-9 NOOP 16:12 post-close wake Fri (wake-b); EOD + WEEK-T3X-5 done; holding night23 METU2+NVDL1 over weekend; next live action Mon 10/12 07:45 analyst/re-rank
2026-10-12T11:47:38Z W-9 07:46 ANALYST Mon 10/12: container restarted over weekend (scratchpad intact); trade-approval setting OFF (agent orders execute directly); pos METU2+NVDL1 ok, 0 open orders; E 105.45 pre-mkt (night23 +1.42: METU b30.87 vs 30.03, NVDL b36.63 vs 36.89); PDT broker-verified 10/8,10/9 -> day leg #12 ALLOWED (Tue/Wed blocked after); earnings: basket clear (ASML 10/14, TSM 10/15). WEEKLY RE-RANK (daily bars thru 10/9): overnight METU 0.34, NVDL 0.26, NVDX 0.22, GGLL 0.19 -> basket METU+NVDL unchanged; day leg TZA 0.46 (NVDQ 0.15) unchanged. Plan: exit 09:31, TZA 09:32+TP, entry 15:52, EOD
2026-10-12T12:00:00Z W-9 08:00 HB premkt METU b31.00 NVDL b36.63 (night23 ~+1.68); QQQ -0.12%
2026-10-12T13:00:00Z W-9 09:00 HB premkt E 105.40 (night23 ~+1.36); METU b30.87 NVDL b36.52
2026-10-12T13:24:04Z W-9 09:24 EXIT prep night23 METU2+NVDL1 (~+1.3 pre-mkt); then TZA day leg #12 at 09:32; bridging to 09:31:05
2026-10-12T13:32:23Z W-9 09:31 EXIT night23 (weekend) METU 2 @31.60 (+3.14; METU opened +5.8%) NVDL @36.41 (-0.48) = +2.66 (best night since #8); E 106.63 NEW HWM (PAUSE now 85.30). NOTE: broker now returns its own ref_id (01a1304f-...) instead of echoing ours; order ids unaffected. 09:31:41 DAY LEG #12 TZA 2 @47.3799 (lim 47.47); TP 47.86 resting (6acce150); day_trades +10/12 (Tue/Wed blocked, Thu allowed)
2026-10-12T14:00:00Z W-9 10:00 HB day leg TZA 2 @47.3799 bid 47.21, TP 47.86 open; E ~106.3; METU +7% on day (sold at open +5.6%)
2026-10-12T15:00:00Z W-9 11:00 HB day leg TZA 2 @47.3799 bid 47.33 (-0.11%), TP 47.86 open; E ~106.5; METU 32.20 NVDL 35.66; QQQ -0.69% IWM -0.16%
2026-10-12T16:00:05Z W-9 12:00 HB day leg TZA 2 @47.3799 bid 47.25 (-0.27%), TP 47.86 open; E ~106.37; METU 32.29 NVDL 35.94; QQQ -0.50% IWM -0.10%
2026-10-12T17:00:05Z W-9 13:00 HB day leg TZA 2 @47.3799 bid 47.49 (+0.23%), TP 47.86 open; E ~106.85; METU 31.63 NVDL 35.87; QQQ -0.73% IWM -0.28%
2026-10-12T18:00:05Z W-9 14:00 HB day leg TZA 2 @47.3799 bid 47.46 (+0.17%), TP 47.86 open; E ~106.79; METU 32.35 NVDL 35.92; QQQ -0.74% IWM -0.26%
2026-10-12T19:00:05Z W-9 15:00 HB day leg TZA 2 @47.3799 bid 47.55 (+0.36%), TP 47.86 open; E ~106.97; METU 32.11 NVDL 35.90; QQQ -0.83% IWM -0.32%; 15:49 close if TP unfilled, 15:52 night 24
2026-10-12T19:52:20Z W-9 15:49 DAY LEG #12 close: TP cancel 15:49:02 verified cancelled; sold TZA 2 @47.6201 (lim 47.56) = +0.48 (+0.51%); TP missed (scan high ~47.66). Day leg total +3.23 over 12 active days, mean +0.27. E 107.11 all-cash = NEW HWM (PAUSE 85.69). 15:52:05 ENTRY night24 METU x2 @31.9299 (lim 31.97) + NVDL x1 @36.0299 (lim 36.09) = 99.89 (93.3% E); cash 7.22
2026-10-13T11:47:30Z W-9 07:47 PREMKT Tue: METU b31.07 (-2.8% vs 31.95 close) NVDL b35.26 (-1.9%); night24 marked ~-2.49; E ~104.62; QQQ -0.66% (NVDA -0.8%, META -1.3%) IWM +0.34%; JPM missed. approvals off. PDT: day leg BLOCKED today+Wed (10/8,10/9,10/12), Thu allowed. Plan: 09:31:05 exit (rule, no discretion), 15:52 night 25.
2026-10-13T12:04:30Z W-9 08:04 RESEARCH: OCO/TP re-test on TZA 1-min bars (21 sessions) + 5-min (40): stops hurt at every level (TP1.0% no stop +0.82% vs stop1% +0.40%, stop2% +0.76%); TP 1.0% best/near-best mean under 3 entry assumptions. No rule change. research/OCO-TP-20261013.md
2026-10-13T13:00:05Z W-9 09:00 HB premkt METU b31.11 NVDL b35.15 (night24 ~-2.52); E ~104.59; QQQ -0.75% IWM +0.08%; exit 09:31:05
2026-10-13T13:24:10Z W-9 09:24 EXIT prep night24 METU2+NVDL1 (~-2.35 premkt); 0 open orders; bridging to 09:31:05
2026-10-13T13:31:40Z W-9 09:31 EXIT night24 METU 2 @31.5309 (lim 31.41; -0.80) + NVDL 1 @35.1001 (lim 35.09; -0.93) = -1.73 (-1.7%); gap-down open (QQQ -0.75%). E 105.38 all cash. No day leg (PDT: 10/8,10/9,10/12). Loop until 15:52 night 25.
