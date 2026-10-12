# T3X STATUS — Overnight Engine (started 2026-09-09)
**Mode:** DAY_LEG_OPEN (night 23 closed 09:31 Mon 10/12: +2.66; TZA day leg #12: 2 @47.3799, TP 47.86 resting; 15:49 close if TP open; 15:52 entry night 24)
**Equity:** 106.63 at 09:32 ET 10/12 (NEW HWM; TZA 94.76 + cash 11.87) · start 98.75 · HWM 106.63 · PAUSE 85.30 · KILL 50
thesis: leveraged-long semis/tech earn overnight, lose intraday -> hold NVDL/METU close->open; NEW v1.2: inverse day leg (TZA) open->close on <=3 days per rolling 5 (PDT cap); never inverse overnight; crypto ruled out (1.9% spread)
daily loop: 09:26 wake -> sell 09:31 -> day-leg buy 09:32 (if PDT count <3) -> ALWAYS-ON scans -> day-leg sell 15:49 -> buy 15:52 -> 16:02 EOD | Mon 07:45 re-rank both legs
blackouts: NVDL 2026-11-17 (NVDA); AMZU 2026-10-29 tentative (AMZN); MUU 2026-09-30 (MU)
schedule (5 crons, all live): t2x-analyst 07:45; t3x-exit-0926; t3x-entry-1548; t2x-wake-a/b hourly backstops — NEVER retired (human rule)
T2X archive: RULES.md untouched; state in trader/archive; FINAL_REPORT.md
to stop me: create trader/HUMAN_STOP or say so in chat
