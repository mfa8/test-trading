# Pre-flight review of the v1.8 tools (2026-11-10, before the first live use)

Three read-only review agents each took one lens (sizing arithmetic, trend state, operations and documents). A fourth agent gathered the morning news. Every medium finding was then handed to a separate agent whose job was to refute it. No agent had broker access or wrote to the repo. Raw output: `preflight_result.json`.

**Result: no high-severity defect.** With today's inputs the tools size and price the orders as RULES_v3 requires. 25 findings: 4 verified (1 medium, 3 low after verification), 21 low and unverified.

## What the lenses checked

- **sizing:** No high or medium defect found in the sizing arithmetic of /home/user/test-trading/trader/tools/entry_v18.py. For today's inputs (E 82.9-88.4, NVDL ask 21.00-23.50, last within 4 cents of the ask) the tool produces the orders that RULES_v3 §3(c), §3(e), §4 and §13(b) require. All eight findings are low: edge cases, missing guards and misleading prints.
- **trend:** No defect found that affects today's 15:50 run: the cache is fresh, the window is right, and the flip level reproduces from public data. Seven findings remain (3 medium, 4 low), all on paths that need a skipped or mistaken `add` or an exact tie.
- **ops:** No high-severity defect found: with today's realistic inputs the four tools compute the right side and size in every case I ran. One medium and nine low findings follow; the medium one can cause a missed entry on a DOWN night at today's prices.

## Verified findings

| lens | finding | file | severity after verification | action |
|---|---|---|---|---|
| trend | A cache 1-3 sessions stale still exits 0 and prints a binding f; rc 2 only fires when the gap exceeds 4 calendar days | `trader/tools/trend.py`:92 | low | Operating check today (last QQQ date must be 2026-11-09; any WARNING on the QQQ line counts as exit code 2). Code fix after the close |
| trend | A session missing inside the 199-close window is never detected | `trader/tools/trend.py`:82 | low | Code fix after the close (holiday table and a hole check) |
| trend | add accepts any date and any value and overwrites existing closes; a mis-dated or mis-typed add corrupts L for up to 199 sessions with rc 0 | `trader/tools/trend.py`:64 | low | Code fix after the close (guards on date, value, symbol and overwrite) |
| ops | DOWN night with one NVDL share above 0.25×E: core exits silently at size 0, and the plan and docs say the top-up comes only after a core fill | `trader/tools/entry_v18.py`:35 | medium | **Fixed 11/10 08:40 ET**: next-step message added to `entry_v18.py`; README, STATUS, RULES_v3 §7, state plan and sizing text corrected |

## Low findings, not verified by a second agent

| lens | finding | file |
|---|---|---|
| sizing | Limit-cap violation aborts with a bare AssertionError; neither the tool nor §4 says what to do next | `trader/tools/entry_v18.py`:27 |
| sizing | Core quantity is one share short when 0.98*E equals q*lim exactly | `trader/tools/entry_v18.py`:31 |
| sizing | topup cannot see the core's outcome: SPENT=0 in state up, or a second run, writes a market-buy intent | `trader/tools/entry_v18.py`:45 |
| sizing | Numeric arguments are not sanity-checked; negative or zero values reach the intent line | `trader/tools/entry_v18.py`:24 |
| sizing | Unknown flags are silently dropped, so a mistyped --dry writes a live intent line | `trader/tools/entry_v18.py`:16 |
| sizing | Core print can mislead: target rounded to 2 decimals, planned top-up computed from the limit without the epsilon | `trader/tools/entry_v18.py`:33 |
| sizing | No tool path for the §4 re-price at 15:55 (ask + 0.3%) | `trader/tools/entry_v18.py`:26 |
| sizing | In a 4-cent ask window the top-up buys slightly more than 1 share, leaving a dust remainder for the exit | `trader/tools/entry_v18.py`:45 |
| trend | Exact tie P == L is usually classified DOWN because of float summation error; rounded output shows price equal to flip with DOWN | `trader/tools/trend.py`:89 |
| trend | --log writes rows for an invalid state with no flag, writes no QQQ row when the cache is short, and appends duplicates on a re-run | `trader/tools/trend.py`:95 |
| trend | state does not validate P and silently ignores `--date=YYYY-MM-DD` | `trader/tools/trend.py`:75 |
| trend | Crash paths exit 1, not the documented 2; the cache is rewritten in place (not atomic) | `trader/tools/trend.py`:37 |
| ops | No tool checks for an existing intent, and on DOWN nights the broker no longer blocks a repeated buy | `trader/tools/entry_v18.py`:36 |
| ops | exit_ovn.py crashes on any quantity that is not a bare integer | `trader/tools/exit_ovn.py`:8 |
| ops | exit_frac.py rejects a zero-padded quantity | `trader/tools/exit_frac.py`:11 |
| ops | trend.py does not detect one to three missing sessions or a hole in the cache | `trader/tools/trend.py`:92 |
| ops | RULES_v3 §3 and §6 still carry pre-v1.8 sizing text and a stale PAUSE trigger | `trader/RULES_v3.md`:17 |
| ops | state.json still describes the v1.6 basket and a September ranking | `trader/state.json`:344 |
| ops | PAUSE can force a larger position than the DOWN size it is supposed to sit below | `trader/RULES_v3.md`:77 |
| ops | §13(a) fixes the trend state at 15:50, after the close on half-days | `trader/RULES_v3.md`:76 |
| ops | LAB.md L5 and RULES_v3 §3(b) set different bars for adding a second name | `trader/LAB.md`:38 |

## Follow-up list (after the 11/10 close unless marked)

1. `trend.py`: NYSE holiday table; a stale cache or a hole in the window gives exit code 2; guards in `add` (date format, weekday, not today or later, positive finite value, known symbol, no silent overwrite, 25% jump check); exact-tie comparison; validity column in the log.
2. `entry_v18.py`: a re-price mode for the §4 15:55 step; refuse a second intent for the same night and kind; argument sanity checks; reject unknown flags.
3. `exit_ovn.py` / `exit_frac.py`: accept the broker's quantity format directly (zero-padded decimals) and split whole and fractional parts in one place.
4. RULES_v3 text: remove the superseded v1.1/v1.2 sizing sentences in §3; say that on half-days the trend state is read at 12:50; settle PAUSE against a smaller DOWN size (lab item, Saturday).
5. `state.json`: drop the September `ranking` block and the v1.6 basket text.
6. LAB.md L5 against RULES_v3 §3(b): align the bar for a second name.

