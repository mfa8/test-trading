# T3X STATUS — Overnight Engine (started 2026-09-09)
**Mode:** FLAT_DAY_LEG_CLOSED (T3X: night 18 closed +0.39; day leg #9 TZA TP hit 46.21 at 09:43 +0.92; night 19 entry 15:52 = METU 2 + NVDL 1 if <=0.98E else METU 1 + NVDL 1)
**Equity:** 103.98 at 09:48 ET 10/5 (flat, all cash; new HWM) · start 98.75 · HWM 103.98 · PAUSE 83.18 · KILL 50
thesis: leveraged-long semis/tech earn overnight, lose intraday -> hold NVDL/METU close->open; NEW v1.2: inverse day leg (TZA) open->close on <=3 days per rolling 5 (PDT cap); never inverse overnight; crypto ruled out (1.9% spread)
daily loop: 09:26 wake -> sell 09:31 -> day-leg buy 09:32 (if PDT count <3) -> ALWAYS-ON scans -> day-leg sell 15:49 -> buy 15:52 -> 16:02 EOD | Mon 07:45 re-rank both legs
blackouts: NVDL 2026-11-17 (NVDA); AMZU 2026-10-29 tentative (AMZN); MUU 2026-09-30 (MU)
schedule (5 crons, all live): t2x-analyst 07:45; t3x-exit-0926; t3x-entry-1548; t2x-wake-a/b hourly backstops — NEVER retired (human rule)
T2X archive: RULES.md untouched; state in trader/archive; FINAL_REPORT.md
to stop me: create trader/HUMAN_STOP or say so in chat
