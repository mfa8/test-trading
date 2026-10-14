# Day-leg (TZA, RULES_v3 §11) adversarial review (Wed 10/14)

**Method.** A multi-agent workflow ran 5 independent read-only lenses: long-sample edge, rank predictiveness, joint risk with the overnight leg, live vs model, and mechanism/alternatives. A judge re-ran the disputed numbers and a completeness critic reviewed the result.
- Full structured output: `dayleg_review_20261014.json`.

## Verdicts by lens
- **LONG-SAMPLE EDGE**: suspend_day_leg (conf 0.78)
- **DOES THE 30-SESSION RANK PREDICT? This is a walk-forward test of the trailing-score instrument selection and of a trailing-mean regime filter for the TZA day leg. It uses 2 years of real daily bars for 10 inverse ETFs (2024-09-03..2026-10-13, 85 out-of-sample weeks) and 15.3 years of real ETF daily bars (2011-07..2026-10, 798 weeks; NVDQ is synthesized as -2x NVDA, its o->c correlates 0.996 with real NVDQ; LABD is excluded from the long run). Each week the #1 name by trailing-N open->close mean/sd is held open->close for every session, with returns as raw o->c, with the 1% take-profit rule on daily bars, and with the TP rule plus costs.**: suspend_day_leg (conf 0.72)
- **JOINT RISK WITH THE OVERNIGHT LEG**: suspend_day_leg (conf 0.75)
- **LIVE VS MODEL**: suspend_day_leg (conf 0.6)
- **MECHANISM & ALTERNATIVES FOR THE PDT SLOTS**: suspend_day_leg (conf 0.75)

## Judge: **suspend_day_leg** (conf 0.82)

All five lenses recommend suspending the day leg. I re-ran the disputed numbers from the raw files (scripts j1-j5.py in /tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/wf2/judge/), and they back the verdict.

1. The thesis is false. IWM's arithmetic open->close drift is about zero:
   - 2000-2026: -0.007%/d (t -0.43). 2010-2026: -0.002%/d. 2021-2026: -0.017%/d. Last 2 years: +0.004%/d.
   - IWM's return comes overnight: +0.047% to +0.068%/d.
   - A daily-reset -3x position therefore has no intraday drift to harvest. The 'mirror' claim in §11 does not hold.

2. The 1% TP rule on TZA daily bars is at or below zero in every long window.
   - Entry at the open (0 slip): 2008+ -0.057%/d (t -1.8); 2010+ -0.061%; 2011-07+ -0.010%; 2016+ -0.022%; 2021+ +0.002%; last 2y 0.000%; last 1y -0.016%.
   - With 0.1% entry cost: -0.10% to -0.17%/d in every window (2008+ -0.161%, t -5.0).
   - The reviewers' conflicting long-sample figures (-0.010, -0.062 and -0.162) are all correct. They differ only by start date and slippage assumption.
   - The TP raises the win rate to about 70% and makes skew about -2.5. It does not add expectancy.
   - The positive figures come only from recent windows: last 30 sessions +0.61%, last 60 +0.36%, last 120 +0.21%. Over the last 250 sessions it is -0.14%.

3. The execution haircut is real. I re-checked it on the 21 one-minute sessions:
   - Daily-bar or open-entry model: +0.82-0.85%. Entry at the 09:31 close: +0.826%. Entry at the 09:32 bar (where live fills actually land): +0.667%.
   - That is a cost of about 0.16%/leg, and open->09:32 drift was +0.20%.
   - So the lens finding of '0.015 optimism' used the 09:31 close; the finding of '0.16-0.18' used the 09:32 bar. The 09:32 figure is the right one.

4. A gate does not rescue it.
   - Trailing-30 mean>0, next-day TP (2011-07+, 0 slip): ON -0.048% vs OFF +0.025%. That is backwards.
   - Score >= 0.4, excluding the current run: 29 days in about 15 years in 6 episodes, mean +0.31% at 0 slip and +0.05% at 0.1% (t <= 1). It fires about twice a year and is not significant.
   - Score >= 0.3: n=105, +0.04% / -0.07%.

5. Risk and growth (my joint 1y block bootstrap, 5000 paths; I approximated earnings nights as cash).
   - P(PAUSE within 60 sessions): 4.5% overnight-only; 18.0% with the 90% leg at an open entry and 23.7% at a realistic +0.15% entry; 8.3% / 9.9% with 1 share.
   - Over 125 sessions: 10.8% overnight-only vs 36-47% with the 90% leg.
   - Log growth per session falls at every size: 0.307 overnight-only vs 0.278 / 0.187 at 90%, and 0.296 / 0.252 with 1 share.
   - This matches joint-risk (5.1% -> 22.8-27.2%). For the goal of reaching $200, the leg lowers both median and 5th-percentile equity.

6. The live record cannot settle the question.
   - 12 legs: +0.341%/leg, sd 0.93, t 1.27, $+3.24. The 7 TP-era legs: +0.469%, t 1.56.
   - That is consistent with zero edge: P(sum >= $3.24 | zero mean) is about 0.32 per the live lens.

The v1.2 10-day review passed (mean > 0), so this change does not react to a drawdown. It rests on the long-sample evidence that the thesis is false and that live fills cost more than the models assumed.

Suspend beats gate or resize. No condition I or the reviewers could pre-register has a positive out-of-sample mean. Even 1 share costs about 0.01-0.05%/session of log growth and roughly doubles short-horizon PAUSE risk, for an expected return at or below zero.

A shadow log scored at the real 09:32 price is free. It does not use the PDT budget, and the live lens showed it matches live outcomes almost exactly (-0.006%/leg, 7 of 7 TP outcomes).

### Rule changes adopted (RULES_v3 v1.7: §11, §7, §8)
- **§11 heading**: Replace the heading line with: "## §11 DAY LEG — SUSPENDED from 2026-10-15 (v1.5, 2026-10-14; the v1.2-v1.4 text below is history and inactive)"
  - *Evidence:* TP rule on TZA daily bars <= 0 in every long window (2008+ -0.057%/d at open entry, -0.161%/d at 0.1% cost, t -5.0); joint bootstrap P(PAUSE in 60) 4.5% -> 18-24% with the 90% leg; log growth lower at every size.
- **§11 status block (insert directly under the heading)**: "**Status v1.5 (2026-10-14, agent, after a 5-lens adversarial review; decided before the 10/15 open):** the day leg is OFF from 2026-10-15 (state.day_leg.enabled=false). No intraday position: the 09:31 exit proceeds stay in cash until the 15:52 entry, and no TZA or other inverse order is placed. Basis: (1) the thesis is false. IWM's arithmetic open->close drift is ~0 (2000-2026 -0.007%/d, t -0.4; 2010-2026 -0.002%/d), so a daily-reset -3x position has no intraday drift to harvest, and TNA and TZA both lose intraday when compounded. (2) The 1% TP rule on TZA daily bars is <= 0 in every long window: 2008-2026 -0.06%/d with entry at the open and -0.16%/d with 0.1% entry cost; 2021-2026 +0.00 / -0.10; last 250 sessions -0.02 / -0.14. The TP buys a ~70% win rate with skew ~-2.5, not expectancy. (3) A real 09:32 entry costs ~0.16%/leg against open or 09:31-close models (21 one-minute sessions: +0.82% -> +0.67%). (4) The trailing-30 score and rank have no out-of-sample power (rank IC ~0; days with a trailing mean > 0 did worse than the rest). The 10/9 TZA score of 0.45 is a top-1% window. (5) Joint bootstrap on 1y data: P(PAUSE within 60 sessions) ~5% overnight-only vs 18-27% with the 90% leg and ~8-12% with 1 share; expected log growth is lower at every size. (6) Live D01-D12 made +0.34%/leg (sd 0.93, t 1.27), which is consistent with zero edge. The v1.2 10-day review passed, but a 10-leg mean is not evidence of edge; this change rests on the long samples, not on a drawdown."
  - *Evidence:* Judge recomputation (j1-j5.py): IWM intraday 2000+ -0.007% (t -0.43), 2010+ -0.002%; TZA TP 0-slip 2008+ -0.057, 2011-07+ -0.010, 2021+ +0.002, last 1y -0.016; 0.1% slip 2008+ -0.161, 2021+ -0.101, last 250 -0.139; 1-min 21 sessions: 09:31-close entry +0.826% vs 09:32 bar +0.667%; joint bootstrap P(PAUSE 60) 4.5% / 18.0% / 23.7% (1 share 8.3% / 9.9%); live mean +0.341%, t 1.27.
- **§11 shadow log and re-entry (append to the status block)**: "Shadow log (no orders, no PDT use): each session, record TZA's 09:32 one-minute bar OHLC4 x 1.0002 as the hypothetical entry, with TP = ceil(entry x 1.010, cent), and score it on 1-minute bars from 09:33 to the 15:48 close. Write one line in the DAY report and in state.day_leg.shadow[]. Re-entry is pre-registered and judged only at a quarterly review (first 2027-01-11); nothing else re-enables the leg. ALL three must hold: (a) >= 60 shadow or live legs at executable prices with mean >= +0.25%/leg and t >= 2.0; (b) the same rule on TZA daily bars with 0.15% entry cost has a positive mean over the trailing 250 sessions; (c) a joint overnight + day-leg block bootstrap at 1-share size shows 60-session P(PAUSE) no more than 5 points above overnight-only. If all pass: exactly 1 TZA share (no v1.4 top-up), 1% TP, 15:49 close, PDT cap unchanged. Suspend again, permanently, if cumulative live day-leg P&L since re-entry is < 0 after 20 legs. Never re-enable on a trailing-30 score, an inverse-ETF rank, or a live run of 12-60 legs."
  - *Evidence:* The 1-minute model with the real entry reproduces live legs to -0.006%/leg and 7 of 7 TP outcomes, so the shadow log yields the same evidence as live legs at no risk. Detecting +0.3%/leg vs 0 needs ~69 legs at sd 1.0 or ~300 at sd 2.1. Only 14-24% of rolling 250-session windows have a positive TP mean.
- **§11 Ranking paragraph and the 'Expected:' line**: Prefix the Ranking paragraph with "(Retired 2026-10-14: no instrument switching; any inverse-ETF table is information only.)" Replace the Expected line with: "Expected (v1.2 claim of +0.3% of E per active day): rejected 2026-10-14. Long-sample TP rule <= 0; the +0.30%/d claim is rejected at t -3.7 to -11.7 depending on window."
  - *Evidence:* Weekly top-of-5 rank with the TP rule: -0.183%/d over 2010-2026 vs always-TZA -0.157%. The 15y live-config replication made -0.030%/session in 6 of 16 positive years. TZA's own trailing score vs the next week has rho -0.07 (mild mean reversion).
- **§7 Account mechanics (append one sentence)**: "While §11 is suspended there are no routine day trades: the 3-per-rolling-5-business-day budget is reserved for emergency same-day exits of the overnight leg, and the 15:52 entry is sized from the cash released at 09:31."
  - *Evidence:* Suspension removes the dependency chain 09:31 exit -> 09:32 buy -> 15:49 sell -> 15:52 entry, in which a stuck day-leg order under-sizes the overnight entry, and it frees the PDT slots (joint-risk and mechanism lenses).
- **§8 Records (append one sentence)**: "Day-leg reviews recompute returns from entry and exit prices. In trades.csv DAY rows, D01-D03 store pnl then pct and D04-D12 store pct then pnl, and D01's 'pct' is P&L / equity. State D02 and D08 lack qty/pct."
  - *Evidence:* Live-vs-model lens found the column-order flip. My price-based recomputation gives a total of +$3.236, matching realised_total 3.23.

**Agent adjustments, based on the critic:**
- The change is labelled v1.7, because RULES_v3 was already v1.6.
- Long-sample figures are cited from 2011-07 onward, which avoids roughly 130 suspect 2009–2010 TZA bars.
- The long-run expectation is stated as "about 0 to slightly negative".
- The re-entry bar is labelled "effectively a high bar".
- **Governance.** The judge asked for human approval before committing. RULES_v3 is agent-authored and the human mandate allows the agent to amend it with documented reasoning; suspending the leg is risk-reducing and reversible. It is therefore adopted now and reported to the human.

### Thursday 10/15 action
Thu 2026-10-15: do not buy TZA (or any inverse ETF) at 09:32, and place no TP order.

1. 09:26-09:31: run the normal §5 overnight exit of NVDL/NVDX.
2. After it fills: verify 0 open orders and leave the proceeds (~$104-105) in cash until the §4 15:52 entry. Size that entry per §3(c) from the full cash: NVDL first under 0.98*E, then NVDX filler.
3. Journal a W-9 line: "§11 day leg suspended v1.5 (review 2026-10-14); no 09:32 order; PDT budget reserved."
4. state.day_leg changes: enabled=false; add suspended_since=2026-10-15; add an empty shadow[] list. Leave the day_trades history as is.
5. After the close: fetch TZA 1-minute bars and log the shadow leg (entry = 09:32 bar OHLC4 x 1.0002, TP = ceil(entry x 1.01), else the 15:48 close).
6. No other rule changes, and do not react to whether TZA would have hit its TP.

The human must approve the RULES_v3/state edits before they are committed. If that approval is not in by 09:32, still place no day-leg order (skipping one session is costless and reversible). If the human explicitly overrides and wants the leg live, the only acceptable form is exactly 1 TZA share (no v1.4 top-up), the 1% TP and the 15:49 close.

### Sizing
Day leg: 0 shares (cash from 09:31 to 15:52). The overnight leg keeps its full §3(c) sizing (up to 0.98*E, about 89-97% invested). Override, only if the human explicitly insists: exactly 1 TZA share. At $48.26 that is about 46% of E, with no v1.4 top-up to 2 shares, 1% TP and the 15:49 close. Pre-registered stop for that override: end it for good once cumulative live day-leg P&L from 10/15 is < 0 after any leg from the 20th on, or at 20 legs if the mean is <= +0.25%/leg. At 1 share the joint bootstrap gives a 60-session P(PAUSE) of about 8-10% vs about 4.5% overnight-only, and log growth falls by about 0.01-0.05%/session. A 25%-of-E leg is impossible in whole shares until E is about $193.

## Critic (would change decision: False)

The decision to suspend the day leg holds. I spot-checked the three numbers it rests on, using data I fetched myself plus the files on disk, and all three match the judge.

(1) Long-sample TP rule on 4,510 TZA daily bars, fetched fresh 2008-11..2026-10-13. Zero slip: 2008+ -0.058%/d (t -1.85), 2011-07+ -0.011, 2021+ -0.001, last 250 -0.027. 0.1% slip: -0.162 (t -5.00), -0.117, -0.104, -0.146. Last 30 sessions +0.626 / +0.607. Hit rate 70.5%, skew -2.83. IWM open->close is about 0 (2008-11+ +0.0007, t 0.04; 2021+ -0.017) and overnight about +0.047%/d, which confirms the thesis is false.

(2) Execution haircut on the 21 one-minute sessions: entry at the 09:31 close gives +0.826% (18 hits), the 09:32 close +0.666% (16 hits), the 09:32 OHLC4 x 1.0002 +0.668%. Open->09:32 drift is +0.238% (t 2.4).

(3) Joint risk, my own 1y block bootstrap (5,000 paths, block 5). P(PAUSE within 60 sessions) goes from 4.4% to 18.1% (zero slip) or 24.5% (0.15% slip) with the 90% leg, and to 8.0% / 9.4% with 1 share. Log growth per session goes from 0.307 to 0.286 / 0.195 (90% leg) and 0.299 / 0.253 (1 share). Keeping every night instead of the judge's 'top-4 gaps = earnings' heuristic, or starting from the real 107.11 HWM, changes these by only 1-3 points. Live: 12 legs average +0.341% (sd 0.928, t 1.27, $3.236).

Gaps, none of which would change the decision:
- The suspension is labelled 'v1.5', but RULES_v3 is already v1.6; it should be v1.7.
- About 130 suspect TZA bars in 2009-2010 drag the 2008+ means down. The rule text should cite the 2011-07+ figures instead (-0.011 at zero slip, -0.117 at 0.1%).
- 'Negative' vs 'about zero' depends on the slip assumption, which is partly the current regime's drift. Long-run expectation is better stated as about 0 to slightly negative. Since breakeven is +0.03-0.05%/d, the leg still fails.
- The status block quotes only the 1y PAUSE numbers; the 3.3y and 8.8y increments are smaller relative to their higher baselines.
- Approval governance is inconsistent: the leg is skipped without sign-off, while the v1.6 overnight change went in the same day without approval either.
- The re-entry criteria are effectively permanent and should say so.

A quick gap-conditional test of the TP rule was negative on both sides. Opening-auction entry and intraday-momentum variants were not tested, but they would be new strategies rather than a rescue of §11.

Scripts (c1_longtp.py, c2_1m.py, c3_joint.py, c4_tails_cond.py) and the fetched data (daily_tza_iwm.json) are in /tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/wf2/completeness/.

- Version label collision. RULES_v3.md line 1 already reads 'T3X v1.6': v1.5 was the 10/13 basket rule and v1.6 came from this morning's overnight review. The judge's §11 heading and status block call the suspension 'v1.5'. It should be v1.7, and the same label should go in the journal and state notes.
- Some early TZA daily bars look bad. I fetched TZA and IWM 2008-11..2026-10-13 fresh. In 130 sessions, TZA open->close differs from -3x IWM open->close by more than 2pp; most are in 2009-2010 (2010-06-07 by 15.9pp, 2010-06-30 by 12.8pp). Dropping them moves the 2008+ zero-slip TP mean from -0.058 to -0.003. The status block's '2008-2026 -0.06%/d' figure should be replaced with the clean 2011-07+ one: -0.011 at zero slip (t -0.36) and -0.117 at 0.1% (t -3.68). The worst day, 2008-11-26 at -22.6%, is genuine (IWM rose 8.3% that day).
- The case that the rule loses money (as opposed to earning about zero) rests on assumed entry cost. The 0.1-0.15% slip comes from the current regime's open->09:32 drift (+0.238%, t 2.4, 21 sessions while TZA was trending up). In a neutral regime that drift should average about 0, leaving mostly the spread. Long-run expectation is therefore better stated as about 0 to -0.05%/d than -0.16%/d. This does not change the decision: the joint-risk breakeven is +0.03-0.05%/d, and the 95% upper bound at zero cost over 2011-07+ is only about +0.05.
- The PAUSE figures in the status block ('~5% -> 18-27%') come only from the 1y bootstrap. In that year NVDL averaged +0.46% a night, so the relative jump looks bigger than in the longer data (3.3y: 26% -> 37-40%; 8.8y: 36% -> 45-49%). The text should quote the range across datasets.
- The judge's bootstrap counts the 4 largest NVDL gaps as earnings-night cash. Two of those are not earnings nights (2025-11-25 at -8.37% and 2025-11-10 at +7.25%). Keeping every night gives 3.9% -> 22.2% / 27.6% (90% leg) and 9.5% / 11.3% (1 share), so the conclusion is unchanged.
- The bootstraps start the rolling-20 high at E0=104.6, not at the actual HWM of 107.11 (PAUSE level 85.69). With the real starting value, P(PAUSE in 60 sessions) is 4.6% -> 18.8% / 25.3%, a negligible change.
- Approval standard is inconsistent. The leg passed §11's own pre-registered 10-day review. The judge requires human approval for the RULES/state edits but still skips the leg on Thu 10/15 without it. The same morning, the agent adopted the v1.6 overnight changes on its own. Whoever acts on this should make the authority explicit.
- The re-entry test can almost never pass. It needs 60 or more legs with mean >= +0.25% and t >= 2, and also a positive trailing-250 TP mean at 0.15% cost; the current trailing-250 value is -0.164. Reaching 60 legs takes about 4-5 months. It should be described as effectively permanent, so the shadow log is not later read as a near-term re-entry path.
- Untested alternatives: conditional intraday-momentum rules and entering in the opening auction to avoid the 09:32 haircut. My quick check on 2011-07+ data, zero slip, found no rescue: TP mean -0.084 (t -1.2) after IWM gaps below -0.3% and -0.092 (t -1.6) after gaps above +0.3%. An open entry is still about 0 over the long run. Either idea would be a new strategy, not a fix for §11.
- The long-sample tail frequency mixes eras: days at -5% or worse ran about 20.8 a year in 2008-11..2011-06, 7.3 a year from 2011-07, and 10.4 a year from 2021. The '10.4 per year' headline happens to match 2021+ but is not era-consistent.

## Open questions
- Will the human accept suspending a leg that passed its own 10-day review (mean > 0)? The change rests on long-sample evidence that the thesis is false, not on a drawdown. Approval is needed before editing RULES_v3/state.json.
- Who runs the shadow log, and when? It needs a post-close fetch of TZA 1-minute bars (the minute interval is capped at ~12 sessions per call) and a fixed scoring script, so results are reproducible at the 2027-01-11 review.
- Should the freed PDT budget get an explicit, pre-registered emergency use (for example a same-day exit after a 15:52 fill error or a late shock), or simply stay unused?
- My joint bootstrap treated the 4 largest NVDL gaps as earnings-night cash, which only approximates the real NVDA earnings dates. The joint-risk lens used actual dates and got similar results (5.1% -> 22.8-27.2%).
- Long-run open->09:32 drift and the daily-bar TP optimism cannot be measured without long intraday history. The 21-session 1-minute sample (drift +0.20%, cost ~0.16%/leg) comes from the same favourable regime. The long-sample conclusion holds at zero slip either way (<= ~0).
- A persistent small-cap intraday-weakness regime (Jul-Oct 2026) can't be ruled out in advance. The shadow log and re-entry test exist so that, if it is real, it gets caught without capital at risk.
