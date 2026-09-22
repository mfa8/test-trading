# T3X STATUS — Overnight Engine (started 2026-09-09)
mode: IN_POSITION_OVERNIGHT | night 10: NVDL 1 @ 37.21 + METU 1 @ 32.14 + NVDX 1 @ 20.98 (Tue 15:52 -> exit Wed 09:31) | no day leg Wed (PDT 3/3), Thu re-opens
**Equity:** 101.95 at 16:02 ET 9/22 close (night 10 open -0.66) · start 98.75 · HWM 103.56 · PAUSE 82.85 · KILL 50
thesis: leveraged-long semis/tech earn overnight, lose intraday -> hold NVDL/METU close->open; NEW v1.2: inverse day leg (TZA) open->close on <=3 days per rolling 5 (PDT cap); never inverse overnight; crypto ruled out (1.9% spread)
daily loop: 09:26 wake -> sell 09:31 -> day-leg buy 09:32 (if PDT count <3) -> ALWAYS-ON scans -> day-leg sell 15:49 -> buy 15:52 -> 16:02 EOD | Mon 07:45 re-rank both legs
blackouts: NVDL 2026-11-17 (NVDA); AMZU 2026-10-29 tentative (AMZN); MUU 2026-09-30 (MU)
schedule (5 crons, all live): t2x-analyst 07:45; t3x-exit-0926; t3x-entry-1548; t2x-wake-a/b hourly backstops — NEVER retired (human rule)
T2X archive: RULES.md untouched; state in trader/archive; FINAL_REPORT.md
to stop me: create trader/HUMAN_STOP or say so in chat
