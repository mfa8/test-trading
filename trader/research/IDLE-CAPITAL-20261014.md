# Idle-capital / unused-PDT-slot research (Wed 10/14)

**Method.** A multi-agent workflow (46 agents, read-only) in three phases:
- **Sweep:** 5 idea families, each tested on long data (1-minute SPY/QQQ/IWM back to 2005, NVDA, 25 years of daily bars), with out-of-sample halves and realistic costs.
- **Refute:** 2 independent skeptics per non-dead candidate, one on data-snooping/out-of-sample and one on costs/feasibility.
- **Judge.**
- Full output: `idle_capital_20261014.json`.

## Decision: adopt = **False**

NO NEW RULE. RULES_v3 v1.7 stays as it is: the 15:52 NVDL/NVDX entry, the 09:31 exit, the TZA day leg suspended, and all 3 PDT slots kept for §7 emergency exits. The 09:31-15:52 cash stays idle. The only result that survived both skeptics confirms the status quo and needs no rule change: keep holding the NVDA-2x leg on FOMC-eve nights and never add an FOMC blackout (§3 'No other event blackouts' already says this). Two factual notes the owner may want to fix by hand (the judge did not edit anything): (1) The RULES §1 claim that 'after a down intraday session the next night averages ~2x better' is false over 25 years. The sign is reversed in 2001-2013, 2013-2026 and the 1-minute data, and holds only in the last ~12 months. (2) The NVDL ex-date of 10/28 is unverified, because NVDL's price history shows no October distribution. If GraniteShares declares one, exclude only the declared $/share from PAUSE and decay inputs, never the whole opening gap.

### Rationale
The bar was: survives both skeptics, has long-sample and out-of-sample after-cost evidence, has a mechanism, and does not materially raise P(PAUSE). One of 21 candidates survived both skeptics: 'FOMC-eve overnight (status quo)'. It adds $0 because the current leg already holds those nights, and it is not significant over the last 2 years (permutation p 0.37-0.67). So it is not an addition to adopt. Every other candidate was refuted by at least one skeptic. The four 'one-skeptic-not-refuted' cases (UPONLY, SKIP_BOTHDOWN, C1-A, C1-D) failed on the out-of-sample or data-snooping lens, and the skeptics who passed them used the cost/feasibility lens.

My own re-check, independent code on the gap-and-open 1-minute checkpoint table (2005-01..2026-03 plus RH 5-minute tail), earnings days excluded:

(a) C1 exit-delay family, 2x NVDA from 09:31 to 10:00 per event.
- C1-A (NVDA open <= -3%): H1 +3.20% (t 2.96), H2 2019+ +1.43% (t 2.25), last 2 years +1.45% (t 1.02; -0.57% without the top 3). Measured from 09:32 instead of 09:31, H2 is +0.95% with median +0.03.
- The (-5%,-3%] band, which is the bulk of C1-A's events, gives H2 -0.03% (median -0.72) and last 2 years -0.64%.
- C1-D (market <= -1.5%) has the same pattern. Its (-3%,-1.5%] band gives H2 +0.20% (t 0.58) and last 2 years -0.49%.
- All of the edge sits in crash opens. NVDA <= -5%: H2 n=17, +5.03% (t 3.25). QQQ <= -3%: H2 n=14, +6.02% (t 3.58).
- So the rules as specified are mostly mean-zero triggers wrapped around about 2 crash days a year. Their per-event and $/yr claims do not survive. The crash-only version was found after the fact by the skeptics, rests on n≈14-17 dominated by 2020-03, 2024-08-05 and 2025-04-07, and was never put through two skeptics. It cannot be adopted now.

(b) Skip-down-session rules, 2x NVDA from 15:52 to 09:31, kept nights minus skipped nights.
- UPONLY: 2005-2015 diff +0.138% (t 1.10, not significant); 2016-21 +0.42% (t 2.49); 2022-26 +0.54% (t 2.35); last year +0.37% (t 0.62); 2026 YTD +0.06% (t 0.09).
- SKIP_BOTHDOWN: 2005-2015 diff +0.05% (t 0.41); last year -0.03%; 2026 -0.27%.
- The first decade does not support either rule. The skeptics showed that most of the PAUSE reduction comes from lower average exposure (a constant 0.64 exposure gives similar P(PAUSE)). Shrunk to a realistic forward edge, the growth gain is about zero. The tradable 15:50 signal lost to the current rule on real NVDL over 2026-04..10, and the candidate's 'break-even' tail result used the non-executable 16:00 close.
- These are risk-reduction or de-levering choices for the owner, not validated growth edges, and they were chosen post hoc from a large grid.

Everything else is dead or decaying: B9/B9p breakout (flat last 2 years, timing-fragile, full size raises PAUSE 6-7 pts), the calendar cells (best-of-many, family-wise p 0.2-0.6, last 2 years negative), and the day trades (negative at realistic cost, use the emergency PDT slots, crash-only tails). The honest conclusion is to adopt nothing and shadow-log the few ideas worth watching.

### Expected effect / risk
None. The strategy and its expected growth are unchanged. That avoids adding noise-level rules whose recent-window expectancy is zero to negative (for example C1-A's ordinary band since 2019 is -0.03%/event; UPONLY lost about $30-40/yr against the current rule in the last 12 months).

None. P(PAUSE) and P(KILL) stay at the current rule's level. No PDT slots are spent, so §7 emergency capacity stays at 3. The skeptics' long-sample bootstraps show the current overnight leg's 60-session P(PAUSE) is about 30-45%, far above the earlier 1-year estimate of 4.5%. That is a pre-existing risk this decision neither raises nor fixes. If the owner wants lower PAUSE risk, a deliberate exposure decision (for example the UPONLY or BOTHDOWN filter, or a smaller basket) should be made openly as de-risking, not as an edge.

## All candidates (verdict, net mean per trade, t)

**INTRADAY MOMENTUM**
- [dead] A1 Gao canonical, SPY to 3x S&P (both directions): net -0.126% (t -10.31); PDT slot: True
- [dead] A2 Gao canonical, QQQ to TQQQ/SQQQ: net -0.119% (t -9.8); PDT slot: True
- [dead] A3 Gao canonical, IWM to TNA/TZA: net -0.106% (t -7.84); PDT slot: True
- [dead] A4 Day-return momentum, long-only TQQQ: net -0.121% (t -9.04); PDT slot: True
- [dead] A5 Gao 12th half-hour (15:00-15:30) sign, SPY: net -0.116% (t -9.82); PDT slot: True
- [dead] A6 Strong first-half-hour filter, long-only SPXL: net -0.047% (t -1.26); PDT slot: True
- [dead] A7 LETF-rebalancing big-move day, SPY (both directions): net 0.078% (t 0.98); PDT slot: True
- [dead] A8 LETF-rebalancing big up-day, QQQ long-only TQQQ: net 0.048% (t 0.76); PDT slot: True
- [dead] B0a Unconditional earlier overnight entry at 15:00: net -0.039% (t -2.06); PDT slot: False
- [dead] B0b Unconditional earlier overnight entry at 15:31: net -0.026% (t -2.15); PDT slot: False
- [dead] B1 Enter at 15:00 if NVDA is up on the day (task variant b): net -0.028% (t -1.19); PDT slot: False
- [dead] B2 Enter at 15:31 if NVDA is up at 15:30 (task variant b): net -0.023% (t -1.51); PDT slot: False
- [dead] B6 Gao first half-hour signal for the NVDL entry: net -0.033% (t -2.15); PDT slot: False
- [dead] B7b Enter at 15:00 on big NVDA up days (LETF rebalancing): net 0.051% (t 1.08); PDT slot: False
- [dead] B8 Delay entry to 15:58 on NVDA down days: net 0.019% (t 1.7); PDT slot: False
- [marginal] B9 Full-size early overnight entry on an NVDA noise-band breakout: net 0.236% (t 3.27); PDT slot: False
- [marginal] B9p Partial early entry: 1 NVDL share on breakout, rest at 15:52: net 0.236% (t 3.27); PDT slot: False
- [marginal] C1 Noise-band breakout day trade, QQQ to TQQQ long-only: net 0.072% (t 1.82); PDT slot: True
- [dead] C2 Noise-band breakout, SPY both directions (paper's canonical form): net -0.051% (t -2.04); PDT slot: True
- [dead] C4 Noise-band breakout day trade, NVDA to NVDL long-only (with stop): net 0.086% (t 1.42); PDT slot: True

**CALENDAR & EVENT EFFECTS: pre-FOMC drift, turn of the month, pre-holiday sessions, options expiration, FOMC-cycle even weeks. Each is tested in three forms: an intraday day trade**
- [promising] FOMC-eve overnight (status-quo check, no change): net 0.629% (t 2.8); PDT slot: False
- [promising] FOMC-eve TQQQ while the overnight leg is in cash mode (conditional): net 0.456% (t 2.98); PDT slot: False
- [dead] Pre-FOMC intraday day trade, TQQQ 09:31->13:55: net 0.051% (t 0.18); PDT slot: True
- [dead] Pre-FOMC intraday day trade, 3x SPY 09:31->13:55: net -0.108% (t -0.44); PDT slot: True
- [dead] Extend the NVDL overnight hold to 13:55 on FOMC day: net 0.923% (t 2.46); PDT slot: False
- [dead] FOMC eve: TQQQ instead of NVDL, held to 13:55: net 0.17% (t 0.51); PDT slot: False
- [dead] FOMC-1 TQQQ day trade: net -0.11% (t -0.47); PDT slot: True
- [dead] Post-FOMC reversal: inverse day trade on FOMC+1: net 0.194% (t 0.71); PDT slot: True
- [marginal] E-TOM+3: move the NVDL entry to 09:31 on the 3rd trading day of the month: net 1.337% (t 3.05); PDT slot: False
- [marginal] H-TOM+3: hold NVDL through TOM+3 instead of exiting at 09:31: net 0.887% (t 2.62); PDT slot: False
- [marginal] Turn-of-month TQQQ day trades on TOM+2 and TOM+3: net 0.01% (t 0.07); PDT slot: True
- [dead] Classic turn-of-month day trades (TOM-1 and TOM+1..+3), TQQQ: net -0.061% (t -0.48); PDT slot: True
- [dead] Hold NVDL through TOM+1..+3: net 0.501% (t 2.63); PDT slot: False
- [dead] TQQQ instead of NVDL on turn-of-month nights: net 0.009% (t 0.11); PDT slot: False
- [dead] Pre-holiday day trade: net 0% (t 0); PDT slot: True
- [dead] Hold NVDL through the pre-holiday session: net 0.452% (t 1.35); PDT slot: False
- [dead] TQQQ instead of NVDL over holiday nights: net 0.109% (t 0.95); PDT slot: False
- [marginal] Quad-witching inverse day trade, SPXU: net 0.76% (t 2.39); PDT slot: True
- [dead] Monthly opex-Friday inverse day trade: net 0.269% (t 1.33); PDT slot: True
- [dead] Opex-Friday shifted entry (check of the status quo): net -0.801% (t -2.05); PDT slot: False
- [marginal] Hold NVDL through Tuesday of opex week: net 1.075% (t 3.55); PDT slot: False
- [dead] FOMC-cycle even weeks (Cieslak, Morse & Vissing-Jorgensen): net 0.4% (t 4.1); PDT slot: False

**OVERNIGHT-LEG TIMING & CONDITIONING**
- [promising] SKIP_DOWN_SESSION (UPONLY): hold overnight only when NVDA is up on the session at 15:50: net 0.382% (t 4.29); PDT slot: False
- [promising] SKIP_BOTHDOWN: skip only when NVDA at 15:50 is below BOTH today's open and yesterday's close: net 0.372% (t 4.67); PDT slot: False
- [marginal] DOWN_1SHARE: on down-session nights hold 1 NVDL share (~34% of E) instead of the full basket: net 0.149% (t 2.26); PDT slot: False
- [dead] RULES §1 claim / DOWNONLY: skip nights after UP intraday sessions (hold only after down sessions): net -0.097% (t -1); PDT slot: False
- [dead] ENTRY_1500: buy at 15:00 instead of 15:52 (exit 09:31): net 0.06% (t -3.4); PDT slot: False
- [dead] ENTRY_1530: buy at 15:30 instead of 15:52: net 0.119% (t -1.6); PDT slot: False
- [dead] ENTRY_CLOSE: buy at the 16:00 official close instead of 15:52: net 0.084% (t -4.8); PDT slot: False
- [dead] EXIT_0945_ALL: sell at 09:45 instead of 09:31: net 0.178% (t 0.7); PDT slot: False
- [dead] EXIT_1000_ALL / EXIT_1030_ALL: sell at 10:00 (or 10:30) instead of 09:31: net 0.215% (t 1.5); PDT slot: False
- [dead] COND_EXIT_1000_IF_GAPDOWN: exit at 10:00 only when NVDA gaps down at the open, else 09:31: net 0.239% (t 3.44); PDT slot: False
- [dead] COND_EXIT_1000_IF_GAPUP: exit at 10:00 only after a gap up: net 0.127% (t -0.6); PDT slot: False
- [dead] COND_ENTER_1500_IF_DOWN: enter at 15:00 when NVDA is below its open at 15:00, else 15:52: net 0.081% (t -3.6); PDT slot: False
- [dead] COND_ENTER_1500_IF_UP: enter at 15:00 when NVDA is above its open at 15:00, else 15:52: net 0.129% (t -1.1); PDT slot: False

**OPENING-GAP AND OPENING-AUCTION EFFECTS**
- [promising] C1-A: Conditional exit delay (NVDA gap-down >= 3% -> sell overnight leg at 10:00) [RECOMMENDED form]: net 1.94% (t 3.3); PDT slot: False
- [promising] C1-D: Conditional exit delay on market gap (QQQ open <= -1.5% -> sell overnight leg at 10:00) [equally valid alternative; isolates the mechanism]: net 1.23% (t 3.3); PDT slot: False
- [marginal] C1-C: Broader market trigger (QQQ open <= -1.0% -> 10:00 exit): net 0.78% (t 3.4); PDT slot: False
- [marginal] C1-B: Lower NVDA threshold (NVDA open <= -2% -> 10:00 exit): net 0.93% (t 3.3); PDT slot: False
- [marginal] C1 exit-time sensitivity: 09:40 instead of 10:00 (QQQ <= -1% trigger): net 0.58% (t 4); PDT slot: False
- [dead] Idiosyncratic NVDA gap-down exit delay (NVDA <= -3% but QQQ/SPY gap > -1%): net 0.14% (t 0.1); PDT slot: False
- [marginal] Gap-down hold-through (NVDA <= -3%: skip the 09:31 exit and the 15:52 re-entry, hold to next morning): net 2.14% (t 2); PDT slot: False
- [dead] Gap-down early entry of the overnight leg (buy NVDL at 10:00 or 10:30 instead of 15:52): net -0.15% (t -0.2); PDT slot: False
- [dead] Unconditional exit delay (sell the overnight leg at 09:35/09:45/10:00 every day instead of 09:31): net 0.078% (t 2); PDT slot: False
- [dead] Gap-up exit delay (NVDA open >= +3% -> sell at 10:00): net -0.42% (t -1.4); PDT slot: False
- [dead] Pre-market exit on gap-up (sell NVDL ~09:29 in extended hours when NVDA indicates >= +2%): net 0.27% (t 3.7); PDT slot: False
- [dead] Opening-auction exit (sell at the official open instead of 09:31): net 0% (t 0.4); PDT slot: False
- [marginal] TQQQ dip-buy day trade (QQQ open <= -2%: buy TQQQ 09:35, sell 10:00): net 1.07% (t 2.2); PDT slot: True
- [dead] SPXL / TNA dip-buy day trades (SPY or IWM open <= -2%: buy 3x 09:35, sell 10:30): net 0.05% (t 0.1); PDT slot: True
- [dead] NVDL dip-buy day trade (NVDA open <= -3%: buy NVDL 09:35, sell 10:30), for mornings with the leg flat: net 0.43% (t 0.8); PDT slot: True
- [dead] 3x gap-up continuation (gap >= +1%: buy 3x long 09:35, sell 10:30): net -0.18% (t -2); PDT slot: True
- [dead] 3x inverse gap-up fade (gap >= +1% or +2%: buy -3x at 09:35, sell 10:30): net -0.52% (t -4.4); PDT slot: True
- [dead] 3x inverse gap-down continuation (gap <= -1%: buy -3x 09:35, sell 10:30): net -0.44% (t -3); PDT slot: True

**EVERYTHING ELSE FOR IDLE CAPITAL**
- [dead] A1 Park cash in a T-bill ETF intraday (SGOV; BIL/USFR/TFLO/SHV also checked): net -0.109% (t -29.1); PDT slot: True
- [dead] A2 Earn T-bill yield without a day trade (residual cash, or a T-bill ETF instead of NVDA-2x overnight): net 0.0077% (t 0); PDT slot: False
- [dead] B1 Unconditional intraday long of the best-drift ETF in a 32-ETF scan (EWJ; EFA runner-up): net -0.084% (t -7.81); PDT slot: True
- [dead] B2 Long a -2x inverse intraday on assets whose early-sample intraday drift was negative (GDX, UNG, UUP, GLD): net -0.309% (t -4.16); PDT slot: True
- [dead] B3 Intraday short volatility (long a -1x VIX-futures product such as SVIX, or SVXY) 09:32-15:50: net -0.196% (t -3.5); PDT slot: True
- [dead] B4 Bitcoin intraday (long BITI -1x intraday; or long IBIT intraday): net -0.284% (t -4.47); PDT slot: True
- [dead] C1 Sector-SPDR overnight-gap laggard, intraday reversal (cross-sectional relative value): net 0.082% (t 0.7); PDT slot: True
- [dead] C2 Sector cross-sectional reversal with no threshold (largest gap-down sector daily) and 'yesterday's loser': net -0.09% (t 0.5); PDT slot: True
- [dead] C3 Pair overnight-divergence -> intraday convergence (15 liquid pairs): net -0.03% (t 0.7); PDT slot: True
- [dead] D1 Single-stock gap-down laggard intraday rebound (24 large caps): net -0.13% (t -0.2); PDT slot: True
- [dead] D2 Fade attention-driven gap-ups (Berkman et al. 2012) via single-stock inverse ETFs: net -0.412% (t -1.87); PDT slot: True

## Refutation outcomes
- B9 Full-size early overnight entry on an NVDA noise-band breakout: refuted (votes refuted=[True, True])
- B9p Partial early entry: 1 NVDL share on breakout, rest at 15:52: refuted (votes refuted=[True, True])
- C1 Noise-band breakout day trade, QQQ to TQQQ long-only: refuted (votes refuted=[True, True])
- FOMC-eve overnight (status-quo check, no change): SURVIVED (votes refuted=[False, False])
- FOMC-eve TQQQ while the overnight leg is in cash mode (conditional): refuted (votes refuted=[True, True])
- E-TOM+3: move the NVDL entry to 09:31 on the 3rd trading day of the month: refuted (votes refuted=[True, True])
- H-TOM+3: hold NVDL through TOM+3 instead of exiting at 09:31: refuted (votes refuted=[True, True])
- Turn-of-month TQQQ day trades on TOM+2 and TOM+3: refuted (votes refuted=[True, True])
- Quad-witching inverse day trade, SPXU: refuted (votes refuted=[True, True])
- Hold NVDL through Tuesday of opex week: refuted (votes refuted=[True, True])
- SKIP_DOWN_SESSION (UPONLY): hold overnight only when NVDA is up on the session at 15:50: refuted (votes refuted=[True, False])
- SKIP_BOTHDOWN: skip only when NVDA at 15:50 is below BOTH today's open and yesterday's close: refuted (votes refuted=[True, False])
- DOWN_1SHARE: on down-session nights hold 1 NVDL share (~34% of E) instead of the full basket: refuted (votes refuted=[True, True])
- C1-A: Conditional exit delay (NVDA gap-down >= 3% -> sell overnight leg at 10:00) [RECOMMENDED form]: refuted (votes refuted=[True, False])
- C1-D: Conditional exit delay on market gap (QQQ open <= -1.5% -> sell overnight leg at 10:00) [equally valid alternative; isolates the mechanism]: refuted (votes refuted=[True, False])
- C1-C: Broader market trigger (QQQ open <= -1.0% -> 10:00 exit): refuted (votes refuted=[True, True])
- C1-B: Lower NVDA threshold (NVDA open <= -2% -> 10:00 exit): refuted (votes refuted=[True, True])
- C1 exit-time sensitivity: 09:40 instead of 10:00 (QQQ <= -1% trigger): refuted (votes refuted=[True, True])
- Gap-down hold-through (NVDA <= -3%: skip the 09:31 exit and the 15:52 re-entry, hold to next morning): refuted (votes refuted=[True, True])
- TQQQ dip-buy day trade (QQQ open <= -2%: buy TQQQ 09:35, sell 10:00): refuted (votes refuted=[True, True])

## Rejections (judge)
- FOMC-eve overnight (status quo): survived both skeptics but adds $0, because the current leg already holds these nights. The FOMC-specific premium is real over 20 years for SPY/QQQ (both halves t>2.8) but absent in the last 2 years (permutation p 0.37-0.67). NVDA first half t is 2.05, not >=2.7 as claimed. Keep it as is with no blackout; it is not a new rule.
- FOMC-eve TQQQ in §3(f) cash mode: refuted by both skeptics. It only fires about 1.9 times a year (not 7.9) because §3(f) rarely triggers, worth about $0.7-1/yr. The cash-mode subset has t 1.49 and 1.59 by half and is mostly 2008-09. Excluding nights that coincided with mega-cap earnings gaps leaves a first half of about 0.
- SKIP_DOWN_SESSION (UPONLY): one skeptic refuted it. My re-check gives a 2005-15 executable UP-minus-DOWN diff of +0.14% (t 1.10, not significant), 2009-15 was negative, and the last 1y/2026 diff is about 0 or reversed. With the effect shrunk to a forward ~0.14%, expected growth is at or below the current rule. The PAUSE drop (~36% to ~12%) comes mostly from lower exposure. It was chosen post hoc as the mirror of the false §1 claim. It is a de-risking choice, not an edge.
- SKIP_BOTHDOWN: one skeptic refuted it. It was chosen post hoc from a 2x2 table, and my re-check gives a 2005-15 diff of +0.05% (t 0.41). It does not replicate on QQQ/SPY/peers. With the executable 15:50 signal it lost to the current rule over 2026-04..10 on real NVDL (+6% vs +18.5% at 0.07%/side). The candidate's 'break-even' result relied on the 16:00 close sign, which carries look-ahead.
- DOWN_1SHARE: both skeptics refuted it. Against matched constant exposure, 2005-15 shows no value once 2008 is excluded. The gain changes sign between 0.03 and 0.07%/side cost (breakeven about 0.03-0.05%/side, and live cost is measured at about 0-0.03%). Last 12 months about -$32/yr. The PAUSE benefit equals a flat 0.64 exposure.
- C1-A gap-down exit delay (NVDA <= -3% -> 10:00): one skeptic refuted it. My re-check shows the (-5,-3] band, about 72% of events, at H2 -0.03% (median -0.72) and last 2y -0.64%. Since 2019 all of the edge comes from 17 crash opens of -5% or worse. Last 2y without the top 3 is -0.57%, and with a 09:32 baseline H2 is +0.95% with median +0.03. In H2 it fails a 98-cell family-wise test (p 0.15).
- C1-D market-gap exit delay (QQQ <= -1.5%): one skeptic refuted it. My re-check gives the (-3,-1.5] band at H2 +0.20% (t 0.58) and last 2y -0.49%. The crash bucket (QQQ <= -3%, n=14 in H2) carries everything. Last 2y is +0.97% (t 0.88), -0.59% without the top 3. The 09:31->09:32 minute carries about 40% of the effect, so it is sensitive to execution timing.
- C1-C (QQQ <= -1.0%): both skeptics refuted it. The added -1.0..-1.5% band is negative out of sample at every exit time from 09:35 to 11:00 (H2 -0.17%). The rule is dominated by C1-D, and 2026-04..10 real NVDL averaged -0.36%/event.
- C1-B (NVDA <= -2%): both skeptics refuted it. The added (-3,-2] bucket is H2 +0.07% (t 0.3), and the increment over C1-A is about $0.85/yr. It loses in below-200dMA regimes (2022), and in H2 it worsens maxDD (-71% vs -63%) and raises historical P(PAUSE).
- C1 09:40 exit variant: both skeptics refuted it. Last 2y is -0.02% and post-sample 2026 is -0.59%. 09:40 is a local spike among nearby exit minutes, and the result disappears with a 1-minute execution delay (H2 -0.05%).
- Gap-down hold-through (NVDA <= -3%): both skeptics refuted it. The median is about 0. The 10:00->15:52 leg it adds over C1-A is negative (-0.32%, 2019+ -0.82%). The t-stat depends on 2012-18 and half the value needs a PAUSE override.
- TQQQ dip-buy day trade (QQQ <= -2%): both skeptics refuted it. 2015-08-24 (an untradable LULD print) supplies 38% of P&L, and without it H1 is -0.14%. The -2..-3% band is negative, the edge disappears with a 1-2 minute entry delay, it is worth about $1-2/yr, and it uses a PDT slot.
- B9 full-size NVDA noise-band early entry: both skeptics refuted it. It raises P(PAUSE within 60) by about 6-7 points in every window. The last-2y edge is about 0 (real NVDL -0.04%) and turns negative with a 5-minute fill. H1 t is 1.79 (1.21 with the official open). The stated LETF-rebalancing mechanism contradicts the timing of the effect.
- B9p (1 NVDL share early on breakout): both skeptics refuted it. Last 2y per-signal is -0.045% and real NVDL since 2024-10 is -0.05%. The edge decays by about 2 bp per minute of fill delay on real NVDL. P(PAUSE) still rises about 0.3-1.3 points, for about $2-4/yr. A 40-60 signal shadow log has no statistical power.
- C1 QQQ noise-band TQQQ day trade: both skeptics refuted it. Before 2011 (QLD-implied) it nets -0.34%/trade (t -3.6). Breakeven cost is about 0.09%/side, and at 0.15% it is -0.12%. The last 2y are about 0. It uses PDT slots and adds 1-4 points of PAUSE.
- E-TOM+3 (enter at 09:31 on the 3rd trading day): both skeptics refuted it. Two shock days (2008-07-03, 2024-08-05) carry the mean. Walk-forward cell selection gives t 0.47-1.51, the last 2y are negative on every measure, the NVDA-specific component has decayed, and last-2y PAUSE rises 24.5% to 34.7% at realistic cost.
- H-TOM+3 hold-through: both skeptics refuted it. Most of the t-stat is the generic 0.30% saved cost. The TOM+3-specific excess is best-of-23 noise (family-wise p 0.64, shrinks to about 0). The real saving at the measured fill cost is about 0.03-0.13%.
- Turn-of-month TQQQ day trades TOM+2/+3: both skeptics refuted it. At 0.15%/side it is +0.015%/trade, and at 0.06% the t is 1.30. Walk-forward pair selection gives about 0 or negative. It is positive only because of the last 2 years and raises P(PAUSE) 1.4-2.9 points.
- Quad-witching SPXU day trade: both skeptics refuted it. 2022+ is -0.31%/trade (0DTE era, with decay significant at t 2.1). 2020-03-20 is 28% of P&L. Low-volatility regimes like the current one (rv 9.3%) show about 0, and at E=$103 only 2 shares are affordable.
- Hold NVDL through opex-week Tuesday: both skeptics refuted it. The 57-cell family-wise p is about 0.24, and the effect comes from different sources in each half (FOMC overlap, then NVDA pre-earnings). The last 2y are -0.26%, and the next instance (2026-11-17) is an NVDA earnings day, which conflicts with §3(d).
- All other screened ideas were killed at the sweep stage: Gao first/last-half-hour momentum (A1-A8, 15:31-15:50 gross about 0, so -0.12%/trade net), earlier or later unconditional 15:52 entries (15:52 is a local optimum), later or conditional exits (decayed since 2021), T-bill parking (accrual is in the open print), the 32-ETF intraday drift scan, short-vol, BTC, sector/pair/single-stock reversals, and inverse fades. None has after-cost out-of-sample support, and several add large tail risk.

## Follow-ups (adopted as shadow logs / checks; no capital)
- Measure real round-trip fill cost for NVDL/NVDX from the live trades log, against 1-minute bars and quotes at fill time, with n >= 60. Several verdicts flip between 0.03 and 0.15%/side, including whether the overnight leg itself has positive net expectancy (at 0.15%/side it is about 0 over 2005-2026). This is the highest-value unknown.
- Re-estimate baseline risk for the current overnight leg. The long-sample bootstraps give 60-session P(PAUSE) of about 30-45% and P(KILL within 250) of 3-7%, against the 1-year 4.5% figure in prior reviews. Decide explicitly whether to reduce exposure (constant smaller basket vs the UPONLY/BOTHDOWN filters) as a risk choice, compared on equal average exposure.
- Pre-registered zero-capital shadow log of the crash-open exit delay: on mornings with NVDA official open <= -5% or QQQ <= -3% vs prior close (earnings mornings excluded), record the NVDL/NVDX bid at the actual 09:31 exit fill time and at 10:00. Also log the -3%/-1.5% band events to confirm they stay mean-zero. Review at the 2027-01-11 quarterly review and again after >= 10 crash events, before considering live adoption.
- Shadow-log the 15:50 NVDA-vs-open and vs-prior-close signs every non-earnings night, with real 15:52->09:31 NVDL outcomes for kept and would-be-skipped nights (UPONLY/BOTHDOWN), using no parameter changes. Judge after >= 120 nights at t >= 1.5. Until then, do not use the false RULES §1 down-day claim as a rationale for anything.
- Optional shadow logs, no capital, low expectation: E-TOM+3 (record the TOM+3 09:31 vs prior-15:52 counterfactual monthly, next 2026-11-04 and 2026-12-03) and B9p restricted to the 11:00 checkpoint (record the real NVDL ask at the agent's actual detection time). Both need years of data to have any power.
- Verify the NVDL distribution and ex-date with GraniteShares before the 2026-10-27 entry. If one is declared, exclude only the declared $/share amount from PAUSE and edge-decay inputs.
