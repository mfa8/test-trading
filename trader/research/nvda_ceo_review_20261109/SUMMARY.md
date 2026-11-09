# CEO governance/scandal/security shock case studies - summary (2026-11-09)
Data: Robinhood daily RTH bars (split-adjusted) in ../data/all_bars.csv; metrics in case_metrics.json/csv, overnight_only_paths.json, from_T0_open_paths.json. Scripts in ../scripts/.
T0 = first regular session reflecting the shock. "Big move" = |close-to-close| >= 5% or |overnight gap| >= 5%. Window for "second gap" = T0+1..T0+10 sessions (~2 weeks).
Base rate = same stock, up to 250 sessions ending T0-6: P(at least one big move in 10 sessions).

| case | T0 | T0 cc% (vs SPY) | next overnight gap% | T0close->+5/+10/+20 % | big moves T0+1..10 | sessions to resolution (move) |
|---|---|---|---|---|---|---|
| HPQ Hurd 2010 | 2010-08-09 | -8.0 (-8.5) | +0.6 | -4.8/-8.4/-6.3 | none | 0 (exit same news) |
| WYNN S.Wynn 2018 | 2018-01-26 | -10.1 (-11.3) | -5.0 | -7.6/-7.8/-6.3 | k1 gap -5.0 cc -9.3; k8 gap +7.5 (CEO resigned) | 8 (+8.6) |
| META CA 2018 | 2018-03-19 | -6.8 (-5.4) | -2.9 | -7.2/-9.5/-2.3 | none (3/27 -4.9) | 15 testimony (+4.5) |
| INTC Krzanich 2018 | 2018-06-21 | -2.4 (-1.8) | +1.0 | -5.6/-1.6/-0.5 | none | 0 |
| JD Liu 2018 | 2018-09-04 | -6.0 (-5.8) | -5.1 | -8.0/-12.5/-15.4 | k1 gap -5.1 cc -10.6; k9 cc -5.1 (trade war) | 76 no charges (+5.9) |
| TSLA SEC 2018 | 2018-09-28 | -13.9 (-13.9) | +15.6 | -1.1/-2.3/+25.0 | k1 gap +15.6 (settled); k5 cc -7.1 | 1 (+17.3) |
| SMCI BigHack 2018 (small cap, natsec) | 2018-10-04 | -41.1 | +3.1 | +3.6/+6.2/+9.4 | k2 +19.0, k3 -15.5, k7 +5.0 | n/a (denials backed 10/5-6) |
| BA Muilenburg 2019 | 2019-10-18 | -6.8 (-6.4) | -3.2 | -1.2/+0.4/+8.1 | none | 45 fired (+2.9) |
| MCD Easterbrook 2019 | 2019-11-04 | -2.7 (-3.1) | +0.5 | +2.1/+3.0/+2.4 | none | 0 |
| BABA Jack Ma 2020 | 2020-11-03 | -8.1 (-9.9) | +0.8 | -6.7/-10.1/-8.5 | k5 cc -8.3 (draft rules) | 52 Ma reappears (+5.5); 12/24 probe -13.3 |
| ERIC Iraq/ISIS 2022 (natsec) | 2022-02-16 | -11.6 (-11.7) | -6.6 | -10.0/-26.7/-18.4 | k1 gap -6.6; k7 gap -9.0; k9 gap -14.2 (DOJ breach) | unresolved in window |
| BP Looney 2023 | 2023-09-13 | +0.4 | +1.4 | +0.9/+3.2/+1.0 | none | 0 |
| MSFT/Altman 2023 | 2023-11-17 | -1.7 (-1.8) | +0.4 | +2.4/-0.2/+0.8 | none | 1 (+2.05) |
| SMCI Hindenburg/10-K 2024 | 2024-08-27 | -2.6 (gap -7.8) | -11.3 | -22.7/-18.7/-16.3 | k1 gap -11.3 cc -19.0 (10-K delay); k7 -6.8; k8 +6.1; k10 +7.9 | 67 committee clears (+28.7) |
| INTC Lip-Bu Tan 2025 (natsec/China) | 2025-08-07 | -3.1 (-3.1) | +1.2 | +20.7/+18.9/+23.9 | k3 +5.6; k5 +7.4; k8 gap +5.4; k9 -7.0 | 3 Trump meeting (+5.6) |

Frequencies (T0+1..10):
- Any big move: 8/15 (base-rate expectation 4.8). Open-ended (CEO not out at T0): 8/11 (exp 4.1). Resolved-at-T0 (HPQ, INTC18, MCD, BP): 0/4.
- Any >=5% overnight gap: 7/15 (exp 2.1); adverse >=5% overnight gap: 4/15 (WYNN, JD, ERIC, SMCI24) - in all 4 the first adverse one came on the FIRST overnight after T0.
- Adverse overnight gap <= -9.8%: 2/15 (SMCI24 -11.3% k1; ERIC -14.2% k9) - both <$100B names with filing/auditor/DOJ escalations.
- Market cap >= ~$100B at the time (HPQ, META, INTC18, BA, MCD, BABA, MSFT, BP; caps approximate/UNVERIFIED): 0/8 had a >=5% overnight gap in window; 1/8 had a >=5% close-to-close move (BABA -8.3%, gap only -3.6%). Open-ended mega-caps (META, BA, BABA, MSFT): worst overnight -1.4..-3.6%, but META and BABA still drifted ~-10% over 10 sessions.
- Overnight-only (holder from T0 close, 10 nights): median -1.0% (1x), median -2.0% (2x daily-reset proxy); range 2x: -56.9% (ERIC) .. +57.9% (SMCI18). META 2x overnight-only -14.8% with no single >=5% gap.
- Resolution moves (exit/clearance/settlement): 9/10 positive (incl. CBS -1.5% from web), median ~+5.6%. Adverse second gaps came from NEW escalations (regulators, police report, 10-K delay, DOJ, state action), not from resolutions.
- Resolution time: bimodal. External actor can end it fast (TSLA SEC settlement 2 days; Altman/MSFT 3-5 days; INTC/Trump meeting 4 days). Board/legal reviews: CEO exit 11 days (WYNN) to 44 days (CBS) to ~66 days (BA) to ~4 months (Uber); formal findings ~3 months (SMCI) to ~4.7 months (CBS); legal clearance ~16 weeks (JD). Median sessions to first decisive event among 9 open-ended listed cases: 15.
