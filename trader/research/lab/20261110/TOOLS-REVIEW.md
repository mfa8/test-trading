# Hardened tools: two reviews before deployment (2026-11-10)

The pre-flight review (`PREFLIGHT.md`) left a list of low-severity gaps in `trend.py`, `entry_v18.py`, `exit_ovn.py` and `exit_frac.py`. Hardened versions were written in a scratch folder and reviewed twice by read-only agents before replacing the live tools. No agent had broker access or wrote to the repo. The live tools were not changed during the trading day.

## Review 1 (version 2)

Raw output: `tools_v2_review_result.json`. One reviewer per tool family, then one agent per medium finding prompted to refute it.

| tool | safe to deploy | confirmed medium findings |
|---|---|---|
| trend | yes | 1: Unscheduled market closure: state exits 2 on the next session and on each of the following ~199 sessions unles |
| entry | no | 3: reprice applies the first-order cap (last*1.004) to the +0.3% limit and refuses most quotes with ask 2c or mor; After a core intent exists, an x0 result prints 'place the top-up at once ... topup N D E 0', and that command; A top-up intent line blocks core/reprice for the rest of the night with no override, and the x0 hint printed u |
| exit | no | 1: exit_frac.py: duplicate guard has no override and gives the wrong instruction after a broker reject or a corre |

All five were new refusals in rare paths (an unscheduled market closure, the re-price cap, a top-up after a failed first order, a rehearsal line blocking the real order, a rejected fractional sell with no override). Each got a tested fix.

## Review 2 (version 2.1)

Raw output: `tools_v21_review_result.json`.

| tool | safe to deploy | earlier findings closed | new findings |
|---|---|---|---|
| trend | yes | 8 of 9 (the rest partly closed or accepted) | 6, all low |
| entry | yes | 4 of 7 (the rest partly closed or accepted) | 3, all low |
| exit | yes | 8 of 9 (the rest partly closed or accepted) | 6, all low |

What the second review measured:

- **Trend:** all 538 sessions to the end of 2028 give exit 0 and the live tool's flip level; holiday table checked against nyse.com; stale, missing and non-session dates give exit 2 with a repair that works when followed literally.
- **Entry:** 20 million core cases and 18 million top-up cases match the live tool except 26 exact ties, where the live tool is one share short; the PAUSE path writes the same intent as the live tool in 110,050 sequences.
- **Exit:** the limit equals the live tool's for every cent bid from 4.03 to 60.00 in both modes; a simulated PAUSE week gives identical logs.

## Version 2.2 (deployed after the close)

Version 2.1 plus the simple low findings of review 2:

- `trend.py`: a bad value for one symbol in `add` no longer blocks the others; a duplicated or malformed shadow token in `state` gives an invalid shadow row only; the log keeps the read that sized the order (a re-run replaces it only on the same day within 20 minutes); `init` skips today's unfinished bar; 2025 holidays added.
- `entry_v18.py`: the intent line records the sizing state, and a top-up whose state differs from the night's core intent is stopped (a PAUSE night has no top-up); reworded cut-off times for half-days.
- `exit_ovn.py`: a zero-quantity leg is skipped instead of stopping the command; `--again` is accepted and ignored.
- `exit_frac.py`: clearer text for more than 6 decimals; notes when `--again` has nothing to override.

Checks on 2.2 (by the author, not a third review): 3,000 random trend cases and 800 random entry runs identical to 2.1; calendar sweep to 2028 valid on all 538 sessions; exit limits identical to the live formula for bids 15.00–30.00; the PAUSE-night intent matches the live tool.

## Not done

- A partial fill followed by a re-price still has no tool path; the remainder is sized by hand and journalled.
- The whole-share market order of §5 step 3 (after two unfilled limits) is still logged by hand.
- Limits are computed in floating point with a rounding guard; a 6-decimal bid can differ by a cent from exact arithmetic in about 1 case in 800,000. Quotes are in cents, so this does not occur.
