# T3X WEEK 7 (Mon 10/19 – Fri 10/23): engine v1.7 unchanged; options plan adopted, waiting on approval

**E 96.91 (10/16 close, marked) → 95.69 (10/23 close, night 33 marked): −1.22 (−1.3%) on the week.**
- Realised this week: **−1.42**, from five overnight exits (N28–N32). The day leg is off.
- Campaign since the T3X start: 98.75 → 95.69 (−3.06). Since your original $100: −4.31 (−4.3%).
- HWM 107.11; E is 10.7% below it. PAUSE 85.69 (until about 11/9), KILL 50.

## You asked for more risk and options (Thu 10/22)
- **What I did:**
  - A 9-agent read-only redesign: 5 options strategies priced on live chains, 3 independent judges and a synthesis.
  - All three judges ranked the same plan first: **"Floor-Funded Barbell with Lock"** (`research/OPTIONS-PLAN-20261022.md`, `RULES_v3 §12`).
- **The plan:**
  - Keep the overnight NVDA engine.
  - Add one 3-month NVDA call-spread "ticket" at a time, paid only from money above an $80 floor. Today that is about $16.
  - Take profit at 3×; roll about every 2 months; **stop opening new tickets at $200.**
  - Model odds over 12 months: reach $200 **~35% vs ~19%** for the engine alone; hit the $50 KILL **~8% vs ~3%**; typical ending **~$95 vs ~$135**.
- **Bolder designs were rejected**, because a single loss would end an account that cannot be refilled automatically:
  - Selling weekend SPY puts: ~50% chance of $200, but ~15% chance of ending below $20.
  - Nightly all-in calls: no better than the engine over 12 months, with a 40% KILL risk.
  - Dip-buying spreads: one loss means KILL.
- **Blocked on you:** account 8334 still has **no options level**. It is a limited-margin account, so it qualifies for Level 3 (spreads). Apply here: https://applink.robinhood.com/upgrade_options?account_number=445788334
- **Already running, with no orders:** a shadow log of the exact contracts the plan would buy, 3 snapshots on 10/23. Once you are approved, the first ticket can go in the next session.

## Overnight leg
| night | basket | P&L | note |
|---|---|---|---|
| 28 (10/16→10/19) | NVDL ×2 + NVDX | **+1.04** | weekend; the open faded, the 60s re-price cost about $1.9 vs the 1.9× model |
| 29 (10/19→10/20) | NVDL ×2 + NVDX | **−1.39** | NVDA −0.5% overnight |
| 30 (10/20→10/21) | NVDL ×2 + NVDX | **+3.75** | best T3X night; NVDA +2.1% overnight |
| 31 (10/21→10/22) | NVDL ×2 + NVDX | **−3.56** | LRCX/META/TXN reported; NVDA −2.2% overnight |
| 32 (10/22→10/23) | NVDL ×3 | **−1.26** | NVDL cheap enough for 3 shares |
| 33 (10/23→10/26) | NVDL ×3 | −0.32 marked (open) | weekend hold |

- **Week: −1.42** on 5 closed nights (2 wins, 3 losses). NVDA's overnight moves summed to +0.68%.
  - Our live result was 2.19 below the 1.9× model. Most of that (−1.86) was the 10/19 faded open and its forced re-price.
- **The day/night split favoured the thesis this week.** NVDA's day sessions (Mon–Thu) summed −2.04%, and being in cash during the day saved about $2.07 net, all of it Thursday (NVDA −4.4%).
- **Campaign: 32 nights, −6.09.** 13 wins and 19 losses.
- **Live NVDA-2x-only nights (N25–N32):** 8 nights, −$9.35, mean −1.26% per night.
  - t is −1.15 against zero and −1.42 against the +0.30% plan. Statistically we still cannot tell "edge" from "no edge".
  - About 70% of the shortfall is NVDA's own bad nights (1× NVDA averaged −0.46% per night against a long-run +0.14%). The rest is execution and tracking.
- **Execution was clean.** Every order filled at or better than the bid or ask, often 10–12c better on exits. One re-price (10/19).

## Research this week (all read-only, all independently verified)
1. **Execution timing (10/21):** keep the 09:31 exit and the 15:52 entry.
   - A pre-market exit at 08:00–09:29 does not beat 09:31 over 164 mornings once wider pre-market spreads are paid.
   - The recent "open fade" is an October effect.
   - I corrected an overstated "+0.77%/night post-market" claim in RULES_v3; the 142-night figure is about +10bp.
2. **Peer-earnings nights (10/22):** 2017–2026, about 2,300 nights.
   - Nights when chip or megacap peers report are not worse for the overnight hold.
   - Every blackout and half-size variant lowered growth and did not reduce drawdown. **No blackout.**
   - Higher variance on hyperscaler nights is a weak signal; it is pre-registered for the January review.
3. **Options redesign (10/22):** see above.
4. **Weekly audit (10/23, 3 agents):**
   - The ledger reconciles to the cent with the broker.
   - **0 rule violations.**
   - One report arithmetic error, now corrected: the NVDA-2x-only running total in the DAY reports from 10/20–10/22 was off by $1.00. The ledger was not affected.
   - Two cancel lines were missing from orders.jsonl; they are now backfilled.

## Shadow logs (no orders)
- **Pre-market exit (§5), 2 days:** the 09:29 bid matched our 09:31 fill both days (0bp). The 09:25 bid was −64bp on 10/22 and +107bp on 10/23. The pre-registered switch test (≥ +10bp, t ≥ 2) is nowhere near met.
- **Day-leg TZA, 7 legs:** mean **−0.73%** gross. It stays suspended.

## Risk, plainly (week-7 audit, simple bootstrap from E 96.01)
- **P(PAUSE at 85.69 within 20 sessions):** about 26% if the edge is real, about 30% if not.
  - About one NVDA night a year is bad enough (≤ −6%) to trigger it on its own.
- **P(reach $200 within 12 months), engine alone:** about **18%** with the edge, about **7%** without.
- **P(KILL at $50):** about 9% with the edge, about 20% without.
- These are worse than the 10/16 figures because E is lower and this audit used a raw-volatility bootstrap.

## Next week
- **Mon 10/26:**
  - §3(f) edge-decay check. The trailing-120 reading on 10/19 was +0.33%/night; the overnight leg goes to cash if it is ≤ 0.
  - Exit night 33.
- **Tue 10/27:** verify the NVDL ex-date (possibly 10/28) before the entry. FOMC eve; SK hynix call.
- **Wed 10/28:** FOMC at 14:00. MSFT/GOOGL/KLAC report after the close. This is a tagged hyperscaler night; the engine holds as normal.
- **Thu 10/29:** AMZN and INTC report after the close (tagged).
- **Sun 11/1:** daylight saving ends. The crons are already in ET.
- **11/17:** NVDA earnings. That night we hold cash.

## For you to know
- **Action needed:** apply for options on account 8334 (Level 3 preferred), then tell me. Nothing in the options plan trades until the approval shows on the account.
- **Open questions from 10/22, each with a default:**
  - Do you accept the odds? Default: yes, run the plan once approved.
  - At $200, keep the engine running (default) or go fully to cash?
  - Keep the $80 floor (default) or lower it to $70? $70 adds about 2 points of $200 odds for about 4 points of KILL odds.
- **Trade approvals are OFF:** orders execute without your sign-off.
