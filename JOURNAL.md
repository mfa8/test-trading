# Trading Journal

Newest entries first.

---

## 2026-08-13 (Thu) 23:15 UTC — Harness initialized

- Verified accounts: ••••8334 "Agentic" (limited margin, agentic_allowed=true,
  no options — as expected). ••••3273 confirmed agentic-blocked; will never be
  touched.
- Portfolio on 8334: $0 cash, $0 pending deposits, no positions. Status set to
  WAITING_FOR_FUNDING — owner funds manually.
- Scheduled autonomous loop:
  - Pre-market prep: 9:00 ET weekdays.
  - Market-hours scans: hourly, 9:30–15:30 ET weekdays.
- No trades possible until funding lands. First action on funding: run the
  playbook scan and deploy per STRATEGY.md.
