# OPTIONS PLAN: T3X v2.0 "Floor-Funded Barbell with Lock" (FFB-L), adopted 2026-10-22

This plan follows the human's 2026-10-22 instruction: "take more risks and introduce options, rethink your strategy... big gains. Do options."

It was produced by the read-only workflow `options-strategy-redesign` (wf_dcd4d644-26d):
- 5 independent designs, priced on live option chains.
- 3 judges: quant, operations and skeptic.
- 1 synthesis step.

The full output is in `options_redesign_20261022.json`.

**Status: INACTIVE until account 8334 has an options level.** Today `option_level` is empty. The human must apply through the Robinhood app. Until then the v1.7 engine runs unchanged, and the shadow quote log starts 10/23.

## Summary for the human

The plan: keep the overnight NVDA-2x engine, which is still our only measured edge, and add one small options "lottery ticket" at a time. The ticket is a 3-month NVDA call spread. Today that means buying the Jan-15-2027 $300 call and selling the $310 call, for about $16 in total.

It pays only if NVDA rallies hard. If NVDA rises about 15-18% within 1-2 months, the ticket roughly triples and we sell it. Its maximum value is $1,000, which needs NVDA at or above $310 on Jan 15.

We only bet money above an $80 floor: the budget is the smaller of 20% of the account or the account minus $80. We roll the ticket about every 2 months. Options stop the moment the account is worth $200.

Realistic odds (my 20,000-path simulation, planning case):
- Chance of reaching $200 within 12 months: about 35%, vs about 19% now. Chance of being at or above $200 after 12 months: about 29% vs 14%.
- Within 3 months: about 11% vs about 0%.
- The cost: the chance of hitting the $50 kill switch rises from about 3% to about 8%. The typical (median) result after a year falls from about $135 to about $95. About half of outcomes end below today's $97.
- 60-70% of tickets expire worthless. That is expected.

What could go wrong:
- NVDA stalls or falls, and the engine and the ticket lose together.
- If the engine edge isn't real, kill-switch risk is about 29%.
- Options turn out to be overpriced.

Bigger bets we tested raised the chance of $200 to about 35-50%, but also gave a 35-50% chance of ending at $50 or below, so we rejected them.

Your action: apply for options Level 3 on account ...8334 in the Robinhood app (Level 2 works as a fallback). Until then nothing changes.

## Allocation

Two sleeves in one account. At E=$97.30 that is about $81 engine and $17.30 options. The engine sleeve is cash outside market hours: it holds ETFs only overnight.

(1) ENGINE (T3X v1.7, unchanged except the sizing base):
- Hold NVDA-2x 15:52 -> 09:31:05: NVDL first, then NVDX filler.
- Sizing base is 0.98 x cash available at 15:50. The cash excludes money tied up in the option position.
- Cash on the NVDA earnings night (11/17).
- Cash during the day.
- Effect at E~97 with a $16 ticket open: 2 NVDL (about 65% of E) instead of 3 (about 96%).

(2) OPTIONS SLEEVE:
- At most ONE position.
- Budget per cycle: B = min(0.20 x E, E - $80). The $80 floor is fixed and never ratchets.
- No open if B < $8, so the sleeve sleeps whenever E < $88.
- At E=$97.30: B = $17.30 (17.8% of E); 1 contract.
- n = floor(B / (100 x limit + $0.10)), capped at 3 while E < $400. In practice n = 1 until E is about $190.

REBALANCING:
- The sleeve is funded only at an open: the first open after approval, then each roll date, about every 2 months.
- All option proceeds (take-profit, roll close, lock) go to cash and are used automatically by the next 15:52 engine entry.
- Money is never moved from the engine into options between roll dates.

LOCK:
- The first time E is at or above $200 (option valued at its closing natural credit), the sleeve is closed and retired, and the human is alerted.
- The engine continues unless the human says otherwise.
- No other sleeves are added: no D2 earnings spread, no D5 dip spread, no D4 put selling, no D1 nightly calls.

## Exact rules (pre-registered)

FFB-L v1. Pre-registered; it amends RULES_v3 T3X v1.7 only where stated.

R0 SCOPE AND GATES
- Account 445788334 only. Never touch ****3273. No transfers. No margin borrowing.
- Long premium only: an NVDA call debit spread (Level 3) or a single long NVDA call (Level-2 mode). No short naked options, no puts, no credit spreads.
- One open option position, and at most one live option order (INV-9).

Gates before the FIRST live option order:
(a) get_accounts shows option_level >= L3 on 8334 (spread mode), or L2 only (call mode).
(b) At least 2 sessions of shadow quotes are logged (R9).
(c) The human's reply approving this plan is taken as the one-time OK of the pre-registered net-price limit rule in R5. The multi-leg tool guidance asks for a user price.
(d) Run review_option_order immediately before EVERY option order and log collateral, fees and order_checks. If it raises an alert that needs user acknowledgement: do not send, alert the human, retry the next session.

BEFORE APPROVAL
- Run T3X v1.7 exactly as now (3 NVDL nights, weekend hold, cash on 11/17).
- Each 07:45 ANALYST wake: check option_level with get_accounts.
- Log shadow quotes (R9). Place no option orders.

R1 ENGINE
- Unchanged §3-§8: 15:52 marketable-limit entry, NVDL first then NVDX filler, 09:31:05 exit, §4/§5 re-pricing, §3(d) earnings-night cash, §3(f) edge-decay switch, §6 KILL/PAUSE.
- Only change: in §3(c), a and b are sized against 0.98 x (cash available at 15:50). The option position is excluded.

R2 VALUATION AND BUDGET
- E = cash + ETFs at bid + option position at its closing natural credit.
  - Spread: bid(K1) - ask(K2) - fees.
  - Call: bid - fee.
- F = $80, fixed.
- B = min(0.20E, E - 80).
- Open only if B >= $8 AND none of the following hold:
  - §6 PAUSE is active;
  - §3(f) has the engine in cash;
  - trader/HUMAN_STOP exists;
  - LOCK or KILL has fired.

R3 SCHEDULE
- First open: the first session after the gates pass, 10:00-15:30 ET (half-days 10:00-12:30).
- After that, opens happen only on ROLL DATES: the first trading day on which the held (or last-planned) expiry is <= 25 calendar days away.
- If the sleeve went flat early (take-profit), it waits for that roll date.
- If an open fails for 3 sessions, skip to the next roll date.

R4 CONTRACT SELECTION (fresh quotes at order time)
- S = NVDA last.
- Candidate expiries: standard 3rd-Friday monthlies with 70 <= DTE <= 150, nearest first.
- Width W = $10 while 150 <= S <= 300; otherwise the listed strike step closest to 4.7% of S.
- For each expiry, scan listed K1 >= S in ascending order, with K2 = K1 + W also listed:
  - mid = mid(K1) - mid(K2)
  - nat = ask(K1) - bid(K2)
  - L0 = mid + 0.25 x (nat - mid), rounded UP to $0.01
- ACCEPT the first K1 where all of these hold:
  - 100 x L0 + 0.10 <= B;
  - W / L0 >= 4;
  - bid(K1) > 0;
  - liquidity guard: nat - mid <= max(0.06, 0.5 x mid).
- If none qualifies, try the next expiry. If nothing qualifies at all: no open today.
- Call mode (Level 2 only): the lowest listed K whose L0 = mid + 0.25 x (ask - mid), rounded up, gives 100 x L0 + 0.05 <= B, with bid > 0 and ask - bid <= max(0.03, 0.5 x mid). Same expiry rule.

R5 ENTRY
- One order (both legs together in spread mode), net DEBIT limit, GFD, with an INV-12 intent line listing the legs, ids and limit.
- Start at L0. On each loop scan (at most every 9 minutes), if unfilled: cancel/replace +$0.01, never above Lmax = min(nat, floor_cent((B - 0.10)/100)).
- 15:30 (12:30 on half-days): cancel and VERIFY 0 open option orders.
- Never leg in. Never place a sleeve order in 09:26-10:00 or after 15:30: the engine has priority. On FOMC days (10/28, 12/9), no sleeve orders 13:55-14:30.

R6 EXITS. These run from the session AFTER the open; the sleeve is never closed on its open day (PDT 0).
(a) TAKE-PROFIT.
- Each scan, compute C = bid(K1) - ask(K2) (call mode: bid).
- If 100 x n x C - fees >= 3 x total debit paid incl. fees: sell to close as one order, limit = mid - 0.25 x (mid - C).
- Step -$0.01 per scan, never below C.
(b) LOCK.
- Trigger: E (R2) >= $200 at any scan or at EOD.
- Close the sleeve with the same limit logic. No further opens. Alert the human ("$200 reached").
- The engine continues unless the human orders cash.
(c) ROLL.
- On the roll date, close between 10:00 and 15:30 with the (a) logic. If unfilled, retry the next session. Never open the next cycle before the old one is closed.
- Exception: if bid(K1) <= 0.02 and S < 0.95 x K1, leave the spread to expire. On the Monday of expiry week, close it at any credit if S >= 0.95 x K1. Never hold into Robinhood's 15:30 ET expiry-day sellout.
(d) KILL (E <= 50).
- Close the option at natural (marketable limit).
- Then run the §6 flatten, HALT and alert. This may use one emergency PDT slot.
(e) No stop-loss, no adding, no rolling up or out mid-cycle, no legging out. Early assignment is negligible: NVDA's dividend is $0.01. If it ever happens, close the stock the same day and log an incident.

R7 PAUSE INTERACTION
- For §6 PAUSE, both the high-water mark and today's E value an OPEN option at cost, not at its mark.
- Realized option losses at roll or expiry count normally; there is no exemption.

R8 EVENT CALENDAR THROUGH 2026-12-31 (ET)

Fri 10/23
- 09:31:05: sell 3 NVDL (§5).
- Shadow day 1.
- 15:52: buy NVDL (3 shares if no options yet), weekend hold.

Mon 10/26: earliest possible first sleeve open (if approved over the weekend and 2 shadow days are logged).

Tue 10/27: verify the NVDL 10/28 ex-date before entry (§8).

Wed 10/28: FOMC 14:00, no sleeve orders 13:55-14:30. MSFT/GOOGL report after the close; engine unchanged.

Thu 10/29: AMZN/INTC report after the close; unchanged.

Sun 11/1: DST ends (crons already in ET).

Tue 11/3: AMD reports after the close; unchanged.

Fri 11/6: last day Jan-15-2027 qualifies (DTE 70). From 11/9 a first open goes to Feb-19-2027 or Mar-19-2027, subject to the R4 liquidity guard. At today's close the Feb-19 far strikes failed it: 310C 0.40/0.96.

About 11/9: the 10/12 high (107.11) leaves the PAUSE window. Trigger 85.69 until then.

Tue 11/17: NVDA Q3 FY27 report after the close (get_earnings_results: verified pm).
- Engine: 09:31 exit, NO 15:52 entry.
- Sleeve: holds through it (event premium already paid); no sleeve orders after 15:00.

Wed 11/18:
- Take-profit and LOCK scans from 10:00 (the most likely take-profit day).
- Engine re-enters 15:52.

Thu 11/26: market closed.

Fri 11/27: half-day.
- Sleeve window 10:00-12:30.
- Engine entry 12:52 (§4).

About mid-December: the engine's 40-night review (§3(g)).

Wed 12/9: FOMC (date to verify), no sleeve orders 13:55-14:30.

Mon 12/21: ROLL DATE for a Jan-15-2027 spread (DTE 25).
- Close it, then open the next cycle the same day: Mar-19-2027 (DTE 88) at a fresh B and K1 per R4.
- If the first open was Feb-19, the roll is Mon 1/25/2027.

Thu 12/24: half-day; sleeve window 10:00-12:30. Fri 12/25: market closed.

Late December: NVDX distribution handling (§8).

2027-01-11: process review.

2027-01-15: Jan expiry (already rolled).

2027-02-24: next NVDA report (unverified; verify at T-15 business days).

R9 SHADOW AND RECORDS
- Every session from 10/23, at about 10:30, 13:00 and 15:25, log the R4 candidate:
  - expiry, K1 and K2;
  - each leg's bid, ask, mark and high/low_fill_rate prices;
  - mid, nat and L0.
- Once the sleeve is live, log the same on every scan.
- trades.csv exit_kind values: slv-open, slv-tp, slv-roll, slv-exp, slv-lock, slv-kill.
- state.sleeve = {mode, expiry, K1, K2, ids, n, debit_incl_fees, opened, tp_credit_trigger, roll_date}.
- orders.jsonl INV-12; one journal line per action.

R10 IF LEVEL 3 IS NOT GRANTED
- L2 only: call mode (R4 call branch), with identical R2/R3/R5-R9.
- No options level: baseline v1.7 unchanged.
- Level revoked: close at the next window and revert.

## First trades

I re-verified all prices live: Robinhood get_option_quotes (marks updated 15:59:59 ET 10/22) and get_equity_quotes (post-market about 17:39 ET). NVDA closed 212.29 (post-market 212.82), NVDL 31.31 (bid/ask 31.38/31.52), NVDX 17.60 (17.56/17.77).

1) Fri 10/23 09:31:05, ENGINE EXIT (unchanged §5)
- SELL 3 NVDL (bought 10/22 15:52 at 31.29) at a marketable limit of bid - max(0.02, 0.15%), re-pricing per §5.

2) Fri 10/23 15:52, ENGINE ENTRY (options not yet approved)
- BUY 3 NVDL at ask + max(0.02, 0.15%), about 31.41: 3 x 31.41 = 94.2 <= 0.98 x 97.3 = 95.35.
- NVDX filler does not fit.
- Weekend hold per v1.7. This is also shadow day 1 for the sleeve; no option order.

3) FIRST OPTIONS TRADE
When: the first session after Level 3 shows on 8334 and 2 shadow days are logged, 10:00-15:30 ET (earliest Mon 10/26), after review_option_order.

Legs, as ONE 2-leg net-DEBIT limit order, GFD:
- BUY TO OPEN 1 NVDA 2027-01-15 300C (id 8acaf208-49b6-4861-bf3c-9a68cf60ac75): 0.47/0.49, mark 0.48, IV 36.5%, delta 0.035, OI 68,196.
- SELL TO OPEN 1 NVDA 2027-01-15 310C (id f0d4c64a-0b4c-4f7c-b4fa-60bb6c05606b): 0.30/0.38, mark 0.34, IV 37.3%, OI 15,065.

Limit:
- Spread mid 0.14, natural 0.19.
- Start at 0.16 (mid plus 25% of the 0.05 gap, rounded up). Step +0.01 per scan up to a cap of 0.17, which is (B - 0.10)/100 with B = min(19.46, 97.30 - 80) = $17.30.
- Robinhood's own fill-rate estimates are 0.17 (high: 0.486 - 0.314) and 0.13 (low: 0.478 - 0.352).

Economics:
- Cost $16-17 plus about $0.16 fees, about 17% of E. That is also the maximum loss.
- Maximum value $1,000 if NVDA >= 310 on 1/15/2027 (+46%). Break-even at expiry about 300.17.
- Take-profit when the closing natural credit is about 0.50 or more (3x).
- By Black-Scholes at IV about 0.37, the spread mid is about 0.61 at NVDA 245 with 60 days left and about 0.46 at NVDA 250 with 40 days left. So a take-profit needs NVDA roughly +15-18% within 3-6 weeks; the 11/17 earnings report falls inside that window.
- Roll date 12/21/2026.

Rejected neighbours (all at today's prices):
- 290/300: mid 0.21, natural 0.27, limit 0.225, cost $22.6 > B.
- 280/290: 0.385/0.46.
- Feb-19-2027 far strikes are too wide at the close: 310C 0.40/0.96, 320C 0.19/0.82.

Engine that night: about $81 of cash buys 2 NVDL. NVDX does not fit under 0.98 x cash.

If NVDA has moved before approval, re-run R4; K1 will shift.

3-L2) LEVEL-2-ONLY version of trade 3
- BUY 1 NVDA 2027-01-15 350C (id c86b3db1-2c7b-4d75-84f4-1c4669d0e5cf): 0.10/0.12, IV 40.8%, OI 13,952.
- Limit 0.11, then 0.12 (at most $12.05 including fees).
- It needs NVDA +65% to finish in the money. Take-profit when the bid is >= 3x cost (about 0.36 or more).
- The 330C (0.19/0.21, rule limit 0.21, $21.05) and 340C (0.13/0.26, $22) exceed the budget.

## Odds

SOURCE
- My own 20,000-path rerun of D3's simulator, with three changes:
  - a LOCK at $200 on liquidation value (spread at bid, net of fees);
  - the first open delayed 5 sessions for approval;
  - the expiry window set to DTE >= 70.
- Files:
  - /tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/options_redesign/synth/code/sim_lock.py
  - /tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/options_redesign/synth/code/drive.py
  - outputs in /tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/options_redesign/synth/out/ (r1-r4.log, summary.json)

MODEL
- Block bootstrap of NVDA (overnight, intraday) return pairs, 2017-08 to 2026-10, earnings nights excluded, rescaled to 40% volatility.
- Engine: NVDL night = 1.9x NVDA - 9bp, at 0.88 exposure; cash on NVDA earnings nights.
- Options: Black-Scholes. IV = blend of RV20 and 40%, x1.08, plus earnings variance; smile fitted to the 10/22 chain.
- Costs: half the modelled spread per leg each way, plus $0.04 per leg.
- KILL at $50 freezes the path.
- Check against the live 10/22 Jan-15 chain: the model prices 300/310 at 0.169 vs the market mid of 0.14, so it is about 20% dearer and therefore conservative for a buyer. The 330C-350C are within 0.04 of market mids.

PLANNING CASE A: engine edge +12bp/night, NVDA drift +20%/yr, options priced like today.

Format in the tables below: P(>=$200 at horizon end) [P(reached $200 at any time)] / P(<=$50, i.e. KILL) / P(<=$20) / median ending equity.

| Horizon | PLAN | BASELINE ENGINE |
|---|---|---|
| 3 months | 9.4% [11.4%] / 1.0% / 0% / $90 | 0.0% [0.0%] / 0.3% / 0% / $107 |
| 6 months | 17.0% [21.2%] / 3.3% / 0% / $90 | 1.0% [1.4%] / 1.0% / 0% / $115 |
| 12 months | 29.0% [35.1%] / 8.1% / 0% / $95 (10th-90th percentile $59-$317) | 13.8% [19.4%] / 2.9% / 0% / $135 ($80-$214) |

- Expected log growth: +0.47%/week (plan) vs +0.61%/week (baseline).
- Per sleeve cycle, from D3's runs at this size: E[log] about +0.002 in A, and about -0.06 when options are fairly or richly priced.
- About 60-70% of cycles end near zero; 20-30% hit the 3x take-profit.
- Sleeve P&L over 12 months: mean +$13, median -$15.5.
- Going fully to cash at $200, instead of keeping the engine running: 12-month P(end >= 200) 35.1% vs 29.0%.

STRESS CASES, 12 months. Format: P(>=$200 at end) [reached] / KILL / median / log growth per week.

| Scenario | Plan | Baseline |
|---|---|---|
| Options rich vs realized (NVDA realized vol 32% vs about 40% implied) | 19.7% [22.9%] / 3.9% / $87 / +0.23% | 7.9% [11.0%] / 0.7% / $134 / +0.61% |
| IV 15% rich and NVDA drift only 4% | 17.7% [21.8%] / 8.8% / $88 / +0.16% | 13.8% [19.4%] / 2.9% / $135 / +0.61% |
| Half engine edge | 17.5% [25.1%] / 16.0% / $84 / 0.00% | 3.3% [5.5%] / 7.0% / $105 / +0.12% |
| No edge | 9.1% [17.5%] / 28.9% / $69 / -0.43% | 0.5% [1.0%] / 16.8% / $82 / -0.35% |
| Raw 2017-26 history | 44.5% [55.6%] / 9.6% / $174 | 19.5% [27.5%] / 5.7% / $138 |
| Bear, -30%/yr | 6.0% [11.9%] / 35.5% / $66 | 1.1% [2.4%] / 20.8% / $82 |

P(<=$20) is about 0% everywhere, because KILL halts near $50.

CROSS-CHECKS
- J-quant, independent code with a lock: A 35.3% / 7.7% / $98; fair options 28.9% / 8.2%; rich 20.1% / 10.1%. Its engine alone: 14.8% / 3.1% / $130.
- Other harnesses put the baseline at 14-20% (end) and 19-29% (reached) for 12 months.

LEVEL-2 CALL MODE, case A
- 27.4% [32.9%] / 6.6% / $109.
- With rich options: 16.9% [19.2%] / 3.4%.
- No edge: 8.9% [15.2%] / 26.4%.
- These are rough: the simulated strike grid stops at +70% out of the money.

RISK DIAL
- An $80 floor vs a $70 floor in A: 29.0 / 8.1% / $95 vs 31.2 / 12.5% / $93. A $70 floor is not recommended.

## Review triggers

Automatic actions, all pre-registered:
- Options level appears on 8334: start the shadow-to-live sequence (R0). Level 2 only: call mode. Level revoked: close and revert.
- LOCK at E >= $200: close the sleeve, retire it, alert the human. The human decides between cash and continuing; the engine continues by default.
- KILL at E <= $50: flatten, HALT, alert.
- §6 PAUSE, §3(f) edge-decay switch or HUMAN_STOP: no new sleeve, and an open spread is held to its normal exits.
- Sleeve sleeps while E < $88.

Execution review:
- After every sleeve fill, compare the fill with L0, mid and natural.
- If entries average worse than mid + 50% of (natural - mid) over the first 3 fills, or the shadow log shows natural - mid > 50% of mid on 3 of the first 5 days, revisit the strike window or width at the next roll date, not mid-cycle.

Scheduled reviews:
- Engine 40-night review (~mid-December, §3(g)), unchanged.
- 2027-01-11 quarterly review: process only (fills, take-profit monitoring, shadow vs model, quotes).
- Sleeve P&L is judged only after 6 cycles (about Oct 2027). Pre-registered stop: if 0 of the first 6 cycles hit the take-profit, the sleeve pauses pending human review.
- 3-4 straight losing cycles are about 25-35% likely and are NOT grounds for a change.

Never change on a losing streak:
- Never raise f above 0.20, lower the floor below $80, or add a second ticket without an explicit human instruction that names the resulting KILL probability.

Add-ons:
- D2 (NVDA earnings-night call spread) or D5-B (SPY dip spread) may be proposed only at a quarterly review, only if E >= $130, and only inside a shared cap: total option debit at risk <= min(0.25E, E - 80). If D2 is ever used, its expiry must be pinned to the Friday weekly after the report.

Calendar checks:
- Re-verify NVDA's 2027-02-24 report (currently unverified) at T-15 business days.
- Verify the 12/9 FOMC date.

## Open questions for the human

- Please apply for options Level 3 (spreads) on account ...8334 only, in the Robinhood app: https://applink.robinhood.com/upgrade_options?account_number=445788334. Level 2 alone also works, as a fallback. Nothing on ...3273.
- Do you accept these odds? Planning case: about 35% chance of reaching $200 within 12 months (vs about 19% now), about 8% chance of hitting the $50 kill switch (vs about 3%), median after a year about $95 (vs about $135), and about half of outcomes ending below $97. Most option tickets will expire worthless.
- Is your approval of this plan also your one-time OK for the agent to set multi-leg net-debit and credit limits by the pre-registered rule (mid + 25% toward the natural price, stepping $0.01, capped at the budget), rather than asking you for a price on each order?
- At $200, the default is: sell the options position, stop opening new ones, keep running the overnight engine, and alert you. Would you rather go fully to cash at $200? That raises the chance of still holding at least $200 after 12 months from about 29% to about 35%.
- If only Level 2 is granted: OK to run the single far out-of-the-money call version (today the Jan-15 $350 call for about $12, same $80 floor)? It runs by default unless you say no.
- Risk dial: keep the $80 floor and 20% budget (recommended), or lower the floor to $70? That adds about 2 points of chance of reaching $200 but about 4.4 points of kill-switch risk.

## Dissent and answers

1) "No lock, so the headline P(200) is only first passage" (all three judges).
- FIXED with rule R6(b). The lock fires on liquidation value with the spread at natural, and the sim values the spread at bid.
- Odds are reported both at period end and as "reached".

2) "It buys variance, not edge: lower median, lower log growth, half of paths end below start; positive EV only if NVDA drift beats the ~4% rate options price in" (J-quant, J-skeptic).
- Accepted and stated plainly to the human:
  - median $95 vs $135;
  - +0.47 vs +0.61%/week;
  - about 50% of paths end below $97.
- The cost is bounded: about $17 is at risk now, and the sleeve sleeps below $88.
- My rerun shows the P($200) lift survives the stresses:
  - options rich vs realized: 19.7% vs 7.9% at end;
  - drift = r with IV 15% rich: 17.7% vs 13.8%;
  - no edge: 9.1% vs 0.5%.
- Its price is +3 to +12 points of KILL risk.

3) "Everything rides on NVDA; a 2022-like path kills both" (J-skeptic: about 86% KILL either way).
- Accepted. The §3(f) edge-decay switch is the only defence. No uncorrelated edge was found to diversify into.

4) Whole-share lumpiness (J-ops).
- At E about 97 a $16 ticket cuts the engine from 3 to 2 NVDL (about 96% to 65% exposure).
- That gives up roughly $2-4 of expected engine gain per cycle at today's size, which the sim (0.88 exposure for both) does not capture.
- Accepted as a known cost.

5) Wide far legs (J-ops).
- The Jan-15 310C is 0.30/0.38 against a spread mid of 0.14; Feb-19 far strikes were 0.40/0.96 at the close.
- Mitigations:
  - mid + 25% limits, +$0.01 steps, a budget cap;
  - the R4 liquidity guard;
  - DTE >= 70, which keeps the very liquid Jan-15 expiry through 11/6;
  - shadow quotes before going live.

6) Tooling: multi-leg orders are limit-only, need a user-approved net price, and pre-trade alerts need acknowledgement (J-ops).
- review_option_order runs before every order.
- The human's approval of this plan is the one-time OK for the rule-based limit.
- Alerts defer the order to the next session; the 10:00-15:30 window absorbs this.

7) "Too timid for big gains" (the human's likely objection).
- Bolder designs were scored and rejected because the account cannot be refilled:
  - D4 (weekend SPY put spreads): about 50% P(200), but about 15% P(<=$20) and negative log growth. Its weekend-premium evidence was overstated: 1.13x, not 1.31x.
  - D5 (dip spreads): 35-52% KILL.
  - D1 (all-in nightly calls): no better 12-month P(200) than the baseline, with 36-40% P(<=50).
  - D2 (earnings spread): about +12 points of P(200) for about +13 points of P(<=50). Its edge is hindsight-heavy: 0.56x payoff over the last 8 reports.
- The $70-floor dial adds about 2 points of P(200) for about 4.4 points of KILL.

8) D2 as a later add-on.
- J-ops is in favour; J-quant and J-skeptic are against: shared-budget tests raised P(<=50) from about 8% to 17-18%.
- Resolved as "not now; quarterly review only, E >= $130, shared cap".

9) Model risk.
- The smile is calibrated on one post-selloff day, and the bootstrap draws from NVDA's bull decade.
- The model prices our spread about 20% above market, i.e. conservatively.
- The shadow log and the process-only first review are the checks.

10) The Level-2 fallback is model-fragile (J-skeptic).
- Its downside is identical (the same floor-funded budget of about $12-17), so it runs by default in L2-only mode. The human can veto it.

## Scorecard (each judge out of 50; higher is better)

| Design | Description | J-quant | J-ops | J-skeptic | Verdict |
|---|---|---|---|---|---|
| D3 | T3X-B "Floor-Funded Barbell": the NVDA-2x overnight engine plus one 3-month NVDA call-spre | 31 | 31 | 27 | adopted (with a lock at $200) |
| D2 | CCX-1: NVDA earnings call-spread overlay on the overnight NVDA-2x engine (catalyst convexi | 28 | 28 | 22 | later add-on only (E>=$130, shared cap) |
| D1 | D1 'Overnight Call Sprint' (OCS): all-in NVDA weekly calls bought at 15:51 and sold at 09: | 21 | 22 | 21 | rejected |
| D4 | D4 "WPS-H": Weekend SPY 1-day put credit spread (1 lot, only when priced rich) + NVDL on T | 20.5 | 17 | 18 | rejected (coin flip vs near-zero) |
| D5 | D5 "DTS": dip-triggered SPY call-spread overlay on the NVDA-2x overnight core | 22.5 | 20 | 15 | rejected (one loss = KILL) |
