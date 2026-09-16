# T3X STATUS — Overnight Engine (started 2026-09-09)
mode: IN_POSITION_OVERNIGHT | night 6: NVDL 2 @ 32.3699 + METU 1 @ 27.331 (cost 92.07) | exit 09:31 Thu 9/17
E: 95.66 marked (start 98.75; nights -1.66 / +1.31 / -4.33 / +0.28 / +1.51 / open) | KILL 50 | PAUSE if E <= 80% of 20-session high (79.04)
thesis: leveraged-long semis/tech earn overnight, lose intraday -> hold NVDL/METU close->open; NEW v1.2: inverse day leg (TZA) open->close on <=3 days per rolling 5 (PDT cap); never inverse overnight; crypto ruled out (1.9% spread)
daily loop: 09:26 wake -> sell 09:31 -> day-leg buy 09:32 (if PDT count <3) -> ALWAYS-ON scans -> day-leg sell 15:49 -> buy 15:52 -> 16:02 EOD | Mon 07:45 re-rank both legs
blackouts: NVDL 2026-11-17 (NVDA); AMZU 2026-10-29 tentative (AMZN); MUU 2026-09-30 (MU)
schedule (5 crons, all live): t2x-analyst 07:45; t3x-exit-0926; t3x-entry-1548; t2x-wake-a/b hourly backstops — NEVER retired (human rule)
T2X archive: RULES.md untouched; state in trader/archive; FINAL_REPORT.md
to stop me: create trader/HUMAN_STOP or say so in chat
