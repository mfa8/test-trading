# Peer-earnings nights study: 2026-10-22 (read-only workflow wf_35e5c9ec-9ec; 2 independent analysts, each adversarially verified)

**Question:** Is the NVDA overnight hold (close → next open) worse or riskier on nights when semiconductor or AI-megacap peers report earnings?

The two live losses that prompted this:
- 10/14→15, TSM reported before the open: −4.90.
- 10/21→22, LRCX/META/TXN reported after the close: −3.56.

The policy was pre-registered: information only, judged at the 2027-01-11 quarterly review, with no behaviour change before then.

**Verdict: no blackout, no subgroup blackout, no half-size.** Both verifiers rated their study "holds".
- They rebuilt the event lists independently: 408 of 408 events matched for B, and all but 2 nights matched for A.
- They checked dates and timings against a second source (95 of 95 matched) and against each peer's own price gap. In 482 of 487 events, the gap landed on the mapped night.

## Data
- **Sample:** NVDA daily close → next open, 2017-08-01 to 2026-10-21, with NVDA's own earnings nights excluded.
  - Analyst A: 2,318 nights.
  - Analyst B: 2,281 nights.
- **Event dates:** from walking get_earnings_calendar in 31-day windows. Coverage before mid-2017 is mega-caps only.
- **SK hynix:** Robinhood has no usable dates, so it is untestable.
- **Tonight's night (10/21→22):** not in the sample, because the daily bar is not out yet.

## Results (NVDA 1x, bp per night)
| Group | n | Mean | sd | Share of nights ≤ −2.5% |
|---|---|---|---|---|
| A: 13 semis peers, event nights | 384 | +25.5 | 168 | 4.9% |
| A: other nights | 1,897 | +11.0 | 171 | 4.7% |
| B: megacap + semis event nights | 304 | +32.4 | 182 | 5.3% |
| B: other nights | 1,977 | +10.5 | 168 | 4.7% |

- **Headline difference:** +14.5bp (t 1.54) for A and +21.8bp (t 1.97) for B.
  - The verifiers showed this mostly reflects day of week: event nights almost never span a weekend.
  - With weekday, season and FOMC controls the difference is about +7bp (t 0.7). **There is no reliable mean difference in either direction.**
- **Tails:** no difference per held night.
- **Variance:** about 1.25–1.45× higher on megacap (MSFT/GOOGL/META/AMZN/ORCL) nights and on nights with 2 or more peers reporting (Levene p 0.001). The signal is fragile: a permutation test gives p 0.10, and it shrinks after trimming one night at each end.
- **Nominal per-name tail hits:** AMZN 5 of 36 (p 0.03), GOOGL and INTC 4 of 36. None survives correction across about 40 tests.

## Strategy simulation (2x overnight)
- Every blackout variant **lowered** growth by 0.6–5.2bp per night.
  - No variant improved max drawdown or the per-held-night rate of −5% nights.
  - Every 95% CI includes zero, except one: the extended semis set (adding LRCX/KLAC/AMAT/INTC), where the blackout is significantly **worse**.
- **Half size on event nights:** costs about 1.1–1.7bp per night, with no drawdown benefit.

## The cost caveat: corrected, not a strategy alarm
- Both studies reported that the 2x hold had **negative** long-run growth. They used a flat **0.3% round-trip cost per night**.
  - **That 0.3% was my assumption in the prompt, and it is far too high.** The §4/§5 limit buffers (±0.15%) are price caps on marketable limits, not costs paid.
- **Measured costs (EXEC-TIMING-20261021):**
  - Live 15:52 entries fill within about 1bp of the 1-minute OHLC4; 09:31 exits fill at about +0.3bp (NVDL).
  - Quoted spreads in regular hours are 1 cent (about 3bp NVDL, about 5bp NVDX).
  - Realistic cost is therefore about **3–6bp round trip**.
  - The real ETFs also lose about 4–5bp per night to tracking against 2× NVDA. NVDL's close→open slope is 1.85–1.92× NVDA's.
- **Break-even:** the long-sample break-even round-trip cost is about **0.21%** per night. At about 0.05% cost plus about 0.05% tracking, the long-sample 2x net log growth is roughly **+8 to +12bp per night**, consistent with the planning edge.
- **Open check:** verifier B compared live NVDL fills with the bar close→open over 24 nights. Fills underperformed by 0.24% (se 0.21%), which is within noise. That comparison mixes timing (15:52 vs the close; 09:31 vs the open print) with cost. **Pre-registered:** the existing `fill_cost` shadow log (n ≥ 60) decides it at the review.

## Upcoming nights (no action; tracked out of sample)
- **10/27:** SK hynix and FOMC eve. Untestable, not a peer night.
- **10/28:** MSFT and GOOGL (megacap multi-event, FOMC day), plus KLAC (semis nights averaged +39bp).
- **10/29:** AMZN (−26.5bp mean, t −1.15; tails 5 of 36) plus INTC.

## Adopted (information only)
1. Keep the NVDA own-earnings blackout only. No peer blackout.
2. **New pre-registered hypotheses, tracked out of sample from 10/22, judged at the 2027-01-11 review, no behaviour change before then:**
   - (H1) Megacap/hyperscaler nights and nights with 2+ peers have higher overnight variance.
   - (H2) AMZN, GOOGL and INTC nights have elevated tails.
   - (H3) Megacap nights on FOMC day have elevated tails.
3. The live `event_night_tags` in state.json now records hyperscaler nights too.
