# T3X STATUS — Overnight Engine (started 2026-09-09)
**Mode:** IN_POSITION_OVERNIGHT (T3X night 25, first v1.5 basket: NVDX 5 @20.4699 = 102.35 (97% E), entered 15:52 Tue 10/13; exit 09:31 Wed 10/14; Wed day leg blocked (PDT), Thu allowed)
**Equity:** 105.38 at 15:52 ET 10/13 (cash 3.03, NVDX 102.35) · start 98.75 · HWM 107.11 · PAUSE 85.69 · KILL 50
thesis: leveraged-long NVDA-2x earns overnight, loses intraday (250 nights: NVDL +0.46%/night overnight, -0.24%/day intraday) -> hold NVDL/NVDX close->open (v1.5, 10/13: METU dropped, 30-night rank failed walk-forward); inverse day leg (TZA) open->close on <=3 days per rolling 5 (PDT cap); never inverse overnight
daily loop: 09:26 wake -> sell 09:31 -> day-leg buy 09:32 (if PDT count <3) -> ALWAYS-ON scans -> day-leg sell 15:49 -> buy 15:52 -> 16:02 EOD | Mon 07:45 re-rank both legs
blackouts: NVDL 2026-11-17 (NVDA); AMZU 2026-10-29 tentative (AMZN); MUU 2026-09-30 (MU)
schedule (5 crons, all live): t2x-analyst 07:45; t3x-exit-0926; t3x-entry-1548; t2x-wake-a/b hourly backstops — NEVER retired (human rule)
T2X archive: RULES.md untouched; state in trader/archive; FINAL_REPORT.md
to stop me: create trader/HUMAN_STOP or say so in chat
