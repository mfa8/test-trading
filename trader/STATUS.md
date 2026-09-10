# T3X STATUS — Overnight Engine (started 2026-09-09)
mode: IN_POSITION_OVERNIGHT | night 2: NVDL 1 @ 33.9399 + AMZU 1 @ 35.1339 (cost 69.07) | exit 09:31 Fri 9/11
E: 97.15 marked (start 98.75; night 1 -1.66) | KILL 50 | PAUSE if E <= 80% of 20-session high (79.04)
thesis: leveraged-long semis/tech earn overnight, lose intraday (NVDL ovn-only +41% / 62 nights, maxDD -17%); hold close->open, flat intraday; never inverse/vol overnight
daily loop: 09:26 wake -> sell 09:31 | intraday wakes NOOP | 15:48 wake -> buy 15:52 | 16:05 EOD | Mon 07:45 re-rank (30-night score)
blackouts: NVDL 2026-11-17 (NVDA); AMZU 2026-10-29 tentative (AMZN); MUU 2026-09-30 (MU)
schedule (5 crons, all live): t2x-analyst 07:45; t3x-exit-0926; t3x-entry-1548; t2x-wake-a/b hourly backstops — NEVER retired (human rule)
T2X archive: RULES.md untouched; state in trader/archive; FINAL_REPORT.md
to stop me: create trader/HUMAN_STOP or say so in chat
