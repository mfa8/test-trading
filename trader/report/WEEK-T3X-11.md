# T3X WEEK 11 (Mon 11/16 – Fri 11/20): a four-day lockout, in cash through a 23% fall in NVDA

**E 80.10 (11/13 close) → 78.95 (Friday close, night 49 marked): −1.15 (−1.4%) on the week.**
- Realised in the account: **−0.81** on one round trip (night 48). Unrealised on night 49 at the close: −0.36.
- Campaign since the T3X start: 98.75 → 78.95 (−19.80). Since your original $100: −21.05.
- HWM 107.11; E is 26.3% below it. PAUSE level 82.89 (E is below). KILL 50.

## The nights
| night | size | result | what happened |
|---|---|---|---|
| 48 (11/13→11/16) | NVDL ×1 (PAUSE) | **−0.81** (−4.5%) | weekend hold; chip stocks sold off before Monday's open |
| Mon→Tue | none | missed | locked out from Mon 13:36 ET |
| Tue→Wed | none | cash by rule | NVDA earnings night |
| Wed→Thu, Thu→Fri | none | missed | locked out |
| 49 (11/20→11/23) | NVDL ×1 (PAUSE) | open | bought at 10.635; exit Mon 09:31:05 |

- **Campaign: 48 nights, −24.81 on the strategy basis** (21 wins, 27 losses).
- **The three missed nights would have netted about zero** (+0.06 at one share each). Not booked.
- **The market:** NVDA 162.85 → 125.79 (−22.8%), NVDL 17.83 → 10.28 (−42.3%), QQQ 679.89 → 610.04 (−10.3%). Being limited to one share, and in cash for four days, kept the account's loss to 1.15.
- **Where the fall happened:** nearly all of NVDA's drop came during the day sessions; its five close-to-open moves add up to about zero. That fits the strategy's premise, but it is one week and proves nothing.

## What changed this week
- **11/16:** second lockout, 13:36 ET. Cause: the weekly usage allowance for the session's model ran out at about 50M cached tokens re-read, far below the 134M of the week before.
- **11/20:** context cut from 803k to 103k tokens; usage guard added (RULES_v3 §15); `tools/usage.py` measures use against the lockout level; routine cut to the fewest steps.
- No strategy rule changed.

## Audit (lean: no multi-agent audit, because of the usage limit)
- Cash path: 62.29 (11/13) + 17.02 (night 48 sale) = 79.31; − 10.635 (night 49 buy) = 68.675. The broker shows 68.67. Matches within the broker's rounding.
- Two order intents logged this week (the Monday sale, the Friday buy); two broker fills; no order between Mon 09:31:13 and Fri 15:52:09; no open orders.
- Not run this week: the options-sleeve shadow, the TZA shadow, the 09:29 exit shadow after Monday (nothing was held).

## Waiting on the owner
1. Usage: extra usage with a cap, a cheaper model for this session, or as is (a third lockout stays possible).
2. Ultracode: still on for this session; multi-agent runs are not being used because the allowance cannot carry them.
3. Wake cadence: hourly instead of half-hourly would save roughly a tenth of the weekly allowance.
4. The notify-only watchdog task (written, in the repo; creating it was refused by the permission check).

## Next week
- Mon 11/23: sell 1 NVDL at 09:31:05. The §3(f) edge check, computed 11/21, is +0.022% (t 0.06): positive by the thinnest margin, so the overnight leg stays on. (Friday's version of this line expected it at or below zero.)
- Thu 11/26 closed. Fri 11/27 half day (trend read 12:50, entry 12:52).
