# T3X WEEK 9 (Mon 11/2 – Fri 11/6): engine v1.7 unchanged; a crash, then the best night of the campaign

**E 95.30 (10/30 close, night 38 marked) → 103.58 (all cash after Friday's 09:31 exit): +8.28 (+8.7%) on the week.** Friday's close, with night 43 marked, is in DAY-20261106.
- Realised this week: **+8.76**, from five overnight exits (N38–N42): 3 wins, 2 losses. The day leg is off.
- Campaign since the T3X start: 98.75 → 103.58 (+4.83). Since your original $100: +3.58.
- **The campaign total is back above zero: 42 nights, +1.48** (19 wins, 23 losses).
- HWM 107.11; E is 3.3% below it.
- KILL 50.
- PAUSE 85.69 through today (E is 20.9% above it), then:

| from | PAUSE level |
|---|---|
| 11/9 | 84.65 |
| 11/10 | 82.94 |
| 11/11 to 12/4 | 82.86 |

## Overnight leg
| night | basket | P&L | NVDA close→09:31 | note |
|---|---|---|---|---|
| 38 (10/30→11/2) | NVDL ×3 | **+2.76** (+3.19%) | +1.4% | weekend hold |
| 39 (11/2→11/3) | NVDL ×3 | **+3.68** (+4.33%) | +2.3% | election day |
| 40 (11/3→11/4) | NVDL ×3 | **−2.16** (−2.44%) | −1.1% | tagged: election + AMD/SMCI/ANET/ALAB reported |
| 41 (11/4→11/5) | NVDL ×3 | **−4.74** (−5.69%) | −2.4% | tagged: QCOM −12% and ARM −8% after reporting |
| 42 (11/5→11/6) | NVDL ×4 | **+9.22** (+10.15%) | +5.9% | rebound after Thursday's crash; best live night so far |

- **Week: +8.76 on 5 closed nights.** The two earnings-tagged nights lost 6.90; the three untagged nights made +15.66.
- **Thursday 11/5 was a broad tech crash.** NVDA −9.3% (181.60), QQQ −6.5%, SMH −11.2%, AMD −17.3%. Press accounts blamed fears of tighter AI rules after the midterms, plus a hot inflation print.
  - We were in cash from 09:31 to 15:52 and avoided **$10.42**.
  - NVDL's lower price then let v1.6 sizing buy a fourth share (96% of E). That share caught Friday's rebound.
- **Being flat during the day saved $18.03 Mon–Thu** (4.55, 0.03, 3.03, 10.42). Friday is in the DAY report.
- **Execution was clean.** Every order filled at or better than its limit on the first try. The longest rest was 31.7s (N41), well inside the 60s re-price.

## Why the live record still sits near zero (week-9 audit, verified)
**Live NVDA-2x-only nights (N25–N42): 18 nights, −$1.78, mean −0.08% per night** (t −0.08). Week 8 stood at −$10.53 after 13 nights. The extra nights are still far too few to tell edge from no edge: t = 2 would take about 740 nights at +0.30%.

**Where the shortfall now comes from,** against a long-run model of 1.9× NVDA:
- **NVDA's own nights: −0.49 (11%).** Over 18 nights NVDA's overnight moves were about average (+0.15% close→open). This reverses week 8, when about 80% of the shortfall was NVDA's bad nights.
- **Everything else: −3.98.**
  - The first minute after the open: −2.42. NVDA's open→09:31 was negative on 13 of 18 nights. This week it reversed: +0.91, negative on 2 of 5 mornings.
  - Our 15:52 entry vs the official close: −0.60. N42 alone is −0.86, because NVDA kept falling into the close after we bought. The crash-day research predicted this for down days (about −33bp).
  - ETF tracking: −0.38. Opening-print convention: −0.31. Fills vs the 09:31 price: −0.26.
  - **Order handling itself (entry plus fills) is only about −0.87,** roughly 19% of the gap.
- The 09:29 pre-market exit test (12 days): +5.7bp, t 0.3. Not met.

## Research and audit this week (all read-only, every number independently verified)
1. **Overnight after big NVDA down days** (2005–2026, earnings nights excluded): the next overnight averages about 0 (−0.04%, n 202). The risk is about 1.8× normal: an overnight of −5% or worse happens about 4% of the time against 0.5%. The usual rebound arrives in the next *day* session, which we don't hold. Friday's +5.9% overnight was the good side of that higher variance.
2. **Earnings nights of chip peers, live:** 7 nights, **0 wins, −$23.09**, mean −3.68%. The other 11 live nights made +$21.31. A 9-year long sample (n 384) shows no penalty on these nights. The judgement is pre-registered for 2027-01-11, so nothing changes now. See "For you to decide" below.
3. **The pre-registered "skip after a down session" shadow had not been logged nightly.**
   - It is now rebuilt for N25–N41 and logged nightly from 11/5.
   - Both definitions are noise (t 0.76 and −0.58).
   - N42 was a down-session night and made +10.15%.
4. **Week-9 audit (8 agents: 4 auditors, each checked by an independent verifier):**
   - **Ledger:** 10 broker orders, 10 logged intents, no orphans. The cash path ends at the broker's 103.58 with 0.00 unexplained.
   - **Rules:** 0 trading violations. Every limit, size, time, blackout and PAUSE check passed. The 4-NVDL entry on 11/5 is exactly what v1.6 prescribes.
   - **Fixed today:**
     - A floating-point slip in `sleeve_r4.py` rejected a spread costing exactly the budget. One shadow pick changed (11/4 15:25).
     - STATUS.md was stale since 10/23.
     - Corrected: one slippage figure, one closing price and the exit order IDs.
     - Journal timestamps had partly been typed by hand; they now come from the clock.
5. **§3(f) preview for Monday:** trailing-120 NVDL overnight mean **+0.364%** (t 1.40), so the leg stays on. It would take −44% over the next 5 nights to flip it.

## Risk, plainly (from E 103.58; bootstrap of the NVDL overnight series since 12/2022; v1.6 whole-share sizing; verified)
| | planning edge (+0.30%/night) | long-run 1.9× NVDA model | zero edge |
|---|---|---|---|
| P(PAUSE within 20 sessions) | ~8% | ~10% | ~11% |
| P(reach $200 within 12 months) | ~52% | ~32% | ~10% |
| P(KILL at $50 within 12 months) | ~1% | ~4% | ~14% |
| median E after 12 months | ~$178 | ~$136 | ~$93 |

- **The planning-edge column is optimistic.** The long-run 1.9× NVDA model is the fairer middle case. If the measured execution drag (about −0.27pt per night) persists, the odds fall to about 4% for $200 and 25% for KILL.
- **On a like-for-like basis the odds improved this week.** In the long-run-model column, P($200) went from about 24% at E 94.82 to about 32% at E 103.58.
- **Bigger nights at 4 NVDL:** about 40% of nights will get 4 shares (95–98% of E) rather than 3 + 1 (87–90%). That adds about 2 points to the 20-session PAUSE odds. It is the v1.6 rule working as written, so no change.
- **A single night triggers PAUSE only on an NVDA overnight gap of about −9% to −11%**, which happens about 0.5 times a year.

## Options sleeve (shadow only; approval still pending)
- The Jan-15-2027 expiry is at 70 days today, the last day in the window. **From Monday the sleeve shadow moves to Feb-19-2027.**
- **New finding:** at E ≈ $100 and current quotes, the R4 rule finds **no Feb-19 spread or single call**. Every spread that fits the ~$20 budget fails the bid/ask width test. The cheapest passing spread costs $33–53, which needs E of about $165–266.
- So even with approval, the sleeve would probably sit idle at this account size unless option markets tighten. I'll re-examine R4's width test at the next sleeve review, when approval arrives. No rule change now.

## Next week
- **Mon 11/9:**
  - §3(f) edge-decay check (the preview is +0.364%).
  - PAUSE level 84.65.
  - The sleeve shadow moves to Feb-19-2027.
  - TTWO, ONTO and QRVO report after the close (note only).
- **Thu 11/12:** AMAT reports after the close (a chip-peer night, tagged as N47), along with CSCO.
- **Tue 11/17: NVDA earnings.** We hold cash that night: exit 11/17 09:31 as usual, no 11/17 entry, re-enter 11/18 15:52.
- Half-days 11/27 and 12/24: the entry moves to 12:52.

## For you to decide
1. **Chip-peer earnings nights (live: 0 for 7, −$23).**
   - The 9-year sample says these nights are not worse on average, and skipping them costs a little growth if that is true.
   - My default is to keep the pre-registered plan: hold through them and judge at 2027-01-11.
   - If you'd rather I sit in cash on those nights from now on (next: AMAT, Thu 11/12), say so and I'll apply it.
2. **Options approval for account 8334 (Level 3 preferred):** https://applink.robinhood.com/upgrade_options?account_number=445788334 Note the sleeve finding above: at today's size it may not find a tradeable contract.
3. **Open questions from 10/22, with defaults still in force:**
   - Accept the odds: yes.
   - At $200: keep the engine running.
   - Keep the $80 options floor.
- **Trade approvals are OFF:** orders execute without your sign-off.
