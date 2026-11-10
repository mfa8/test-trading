# L5 supplementary: validation, worst nights, correlation, real NVDL/NVDX vs synthetic, downside of the split,
# sensitivity (+11/6->11/9 night), per-year table, bootstrap robustness, live window.
import sys, json, csv
import numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/concentration')
from l5lib import *

B = load_long('2026-11-06')
rows = build_nights(B)
earn = earnings_dates()
dates = [r['d'] for r in rows]; nxt = [r['n'] for r in rows]
N = len(rows)
legN = np.array([r['legN'] for r in rows]); legT = np.array([r['legT'] for r in rows]); qon = np.array([r['qon'] for r in rows])
up = np.array([r['up'] for r in rows]); isE = np.array([r['d'] in earn for r in rows])
yr = np.array([d[:4] for d in dates])
s_tr = np.where(up, 0.98, 0.25); s_fu = np.full(N, 0.98)
R1 = account_returns(legN, legT, s_tr, 1.0); R5 = account_returns(legN, legT, s_tr, 0.5); R0 = account_returns(legN, legT, s_tr, 0.0)
F1 = account_returns(legN, legT, s_fu, 1.0); F5 = account_returns(legN, legT, s_fu, 0.5); F0 = account_returns(legN, legT, s_fu, 0.0)
H1 = yr <= '2020'; H2 = yr >= '2021'; ALL = np.ones(N, bool)
PER = [('2015-2020', H1), ('2021-2026', H2), ('2015-2026', ALL)]

print('#' * 100); print('A. VALIDATION against RULES_v3 s13(c) (independently verified): size 1.0 / 0.25, NVDA-2x, 9bp, 2015-26')
g = lambda R: 100 * float(np.mean(np.log1p(R)))
print('   always-full (s=1): g %+.4f (s13c says +0.184) | rule (1 / 0.25): g %+.4f (s13c says +0.238)' % (
    g(account_returns(legN, legT, np.ones(N), 1.0)), g(account_returns(legN, legT, np.where(up, 1.0, 0.25), 1.0))))
# compare with the repo's own overnight csv (nvda_on) for the same nights
ed = {r['date']: r for r in csv.DictReader(open(EARN_CSV))}
mx = max(abs(float(ed[d]['nvda_on']) - rows[i]['nvda_on']) for i, d in enumerate(dates) if d in ed)
print('   max |my NVDA overnight - repo edge_decay csv nvda_on| over %d common nights: %.2e' % (sum(d in ed for d in dates), mx))

print('#' * 100); print('B. 20 WORST NVDA-ONLY NIGHTS (account return under the trend rule) and what the split / TQQQ-only lost the same night')
o = np.argsort(R1)[:20]
print('   %-10s %-10s %5s %4s %5s | %9s %9s | %8s %8s %8s' % ('entry', 'exit', 'state', 'size', 'earn', '2xNVDA%', 'TQQQ%', 'NVDL-only', 'split', 'TQQQ-only'))
for i in o:
    print('   %-10s %-10s %5s %4.2f %5s | %+9.2f %+9.2f | %+8.2f %+8.2f %+8.2f' % (dates[i], nxt[i], 'UP' if up[i] else 'DOWN', s_tr[i], 'E' if isE[i] else '', 100 * legN[i], 100 * legT[i], 100 * R1[i], 100 * R5[i], 100 * R0[i]))
print('   sum of the 20 nights:  NVDL-only %+.1f%%  split %+.1f%%  TQQQ-only %+.1f%%   | mean %+.2f / %+.2f / %+.2f | split loss as share of NVDL-only loss: %.0f%%' % (
    100 * R1[o].sum(), 100 * R5[o].sum(), 100 * R0[o].sum(), 100 * R1[o].mean(), 100 * R5[o].mean(), 100 * R0[o].mean(), 100 * R5[o].sum() / R1[o].sum()))
print('   of the 20: earnings nights %d; nights where TQQQ leg also < 0: %d; nights where TQQQ leg <= -5%%: %d; split lost less on %d, more on %d' % (
    isE[o].sum(), (legT[o] < 0).sum(), (legT[o] <= -0.05).sum(), (R5[o] > R1[o]).sum(), (R5[o] < R1[o]).sum()))
print('   --- same, size 0.98 always (raw legs) ---')
o2 = np.argsort(F1)[:20]
for i in o2:
    print('   %-10s %-10s %5s %5s | %+9.2f %+9.2f | %+8.2f %+8.2f %+8.2f' % (dates[i], nxt[i], 'UP' if up[i] else 'DOWN', 'E' if isE[i] else '', 100 * legN[i], 100 * legT[i], 100 * F1[i], 100 * F5[i], 100 * F0[i]))
print('   sum of the 20 nights:  NVDL-only %+.1f%%  split %+.1f%%  TQQQ-only %+.1f%% | split/NVDL-only %.0f%% | earnings nights %d | TQQQ leg <0 on %d' % (
    100 * F1[o2].sum(), 100 * F5[o2].sum(), 100 * F0[o2].sum(), 100 * F5[o2].sum() / F1[o2].sum(), isE[o2].sum(), (legT[o2] < 0).sum()))
ne = ~isE
o3 = np.argsort(np.where(ne, R1, 9))[:20]
print('   --- trend rule, NON-earnings nights only (the live rule is in cash on earnings nights): 20 worst ---')
print('   sum NVDL-only %+.1f%%  split %+.1f%%  TQQQ-only %+.1f%% | split/NVDL-only %.0f%% | TQQQ leg <0 on %d of 20 | TQQQ leg <= -5%% on %d' % (
    100 * R1[o3].sum(), 100 * R5[o3].sum(), 100 * R0[o3].sum(), 100 * R5[o3].sum() / R1[o3].sum(), (legT[o3] < 0).sum(), (legT[o3] <= -0.05).sum()))
print('   --- 20 worst SPLIT nights (trend rule) ---')
o4 = np.argsort(R5)[:20]
for i in o4:
    print('   %-10s %5s %4.2f %2s | 2xNVDA %+7.2f TQQQ %+7.2f | NVDL-only %+7.2f split %+7.2f TQQQ-only %+7.2f' % (dates[i], 'UP' if up[i] else 'DOWN', s_tr[i], 'E' if isE[i] else '', 100 * legN[i], 100 * legT[i], 100 * R1[i], 100 * R5[i], 100 * R0[i]))
print('   sum: NVDL-only %+.1f%% split %+.1f%% | overlap with NVDL-only worst-20: %d' % (100 * R1[o4].sum(), 100 * R5[o4].sum(), len(set(o4) & set(o))))
print('   --- tail counts (trend rule): nights with account return <= level, NVDL-only / split / TQQQ-only ---')
for nm, m in PER:
    print('   %s: ' % nm + ' | '.join('<=%d%%: %d / %d / %d' % (L, (R1[m] <= L / 100).sum(), (R5[m] <= L / 100).sum(), (R0[m] <= L / 100).sum()) for L in (-3, -5, -10, -15)))
print('   --- tail counts (0.98 always) ---')
for nm, m in PER:
    print('   %s: ' % nm + ' | '.join('<=%d%%: %d / %d / %d' % (L, (F1[m] <= L / 100).sum(), (F5[m] <= L / 100).sum(), (F0[m] <= L / 100).sum()) for L in (-3, -5, -10, -15)))

print('#' * 100); print('C. CORRELATION of the two legs overnight (2xNVDA vs TQQQ, close->open)')
def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b)); return corr(ra, rb)
for nm, m in PER + [('UP nights', up), ('DOWN nights', ~up), ('non-earnings', ne), ('2015-20 non-earn', H1 & ne), ('2021-26 non-earn', H2 & ne)]:
    a, b = legN[m], legT[m]
    bt = np.polyfit(b, a, 1)[0]
    print('   %-18s n=%4d Pearson %.3f Spearman %.3f | sd 2xNVDA %.2f%% TQQQ %.2f%% | slope of 2xNVDA on TQQQ %.2f' % (nm, m.sum(), corr(a, b), spearman(a, b), 100 * a.std(ddof=1), 100 * b.std(ddof=1), bt))
print('   by year: ' + ' '.join('%s %.2f' % (y, corr(legN[yr == y], legT[yr == y])) for y in sorted(set(yr))))
# tail dependence
for q in (5, 1):
    thr = np.percentile(legN, q); m = legN <= thr
    thrT = np.percentile(legT, q); mT = legT <= thrT
    print('   NVDA-leg worst %d%% nights (n=%d, leg <= %.1f%%): mean 2xNVDA %+.2f%%, mean TQQQ %+.2f%%, TQQQ<0 on %.0f%%, TQQQ also in its own worst %d%% on %.0f%%, corr inside tail %.2f' % (
        q, m.sum(), 100 * thr, 100 * legN[m].mean(), 100 * legT[m].mean(), 100 * (legT[m] < 0).mean(), q, 100 * (m & mT).sum() / m.sum(), corr(legN[m], legT[m])))
    print('   TQQQ-leg worst %d%% nights (n=%d, leg <= %.1f%%): mean TQQQ %+.2f%%, mean 2xNVDA %+.2f%%, 2xNVDA<0 on %.0f%%, 2xNVDA worse than TQQQ on %.0f%%' % (
        q, mT.sum(), 100 * thrT, 100 * legT[mT].mean(), 100 * legN[mT].mean(), 100 * (legN[mT] < 0).mean(), 100 * (legN[mT] < legT[mT]).mean()))
# idiosyncratic part: residual of 2xNVDA on TQQQ
bt, a0 = np.polyfit(legT, legN, 1); resid = legN - (a0 + bt * legT)
print('   variance of 2xNVDA explained by TQQQ overnight (R^2): %.2f ; residual (company-specific) sd %.2f%% vs total %.2f%%' % (corr(legN, legT) ** 2, 100 * resid.std(ddof=1), 100 * legN.std(ddof=1)))
for nm, m in PER:
    vN = legN[m].var(ddof=1); vT = legT[m].var(ddof=1); c = np.cov(legN[m], legT[m])[0, 1]
    v5 = 0.25 * vN + 0.25 * vT + 0.5 * c
    print('   %s raw-leg sd: 2xNVDA %.2f%% | 50/50 %.2f%% | TQQQ %.2f%%  (50/50 sd is %.0f%% of 2xNVDA sd; with zero correlation it would be %.0f%%)' % (
        nm, 100 * vN ** .5, 100 * v5 ** .5, 100 * vT ** .5, 100 * (v5 / vN) ** .5, 100 * ((0.25 * vN + 0.25 * vT) / vN) ** .5))

print('#' * 100); print('D. MARKET (index) EXPOSURE: beta of each raw leg to QQQ overnight; gross notional')
for nm, m in PER:
    bN = np.polyfit(qon[m], legN[m], 1)[0]; bT = np.polyfit(qon[m], legT[m], 1)[0]
    print('   %s beta to QQQ close->open: 2xNVDA %.2f | TQQQ %.2f | 50/50 %.2f   (corr 2xNVDA~QQQ %.2f, TQQQ~QQQ %.3f)' % (nm, bN, bT, 0.5 * bN + 0.5 * bT, corr(legN[m], qon[m]), corr(legT[m], qon[m])))
print('   gross notional per $1 held: NVDL-only 2.0x NVDA | split 1.0x NVDA + 1.5x Nasdaq-100 = 2.5x | TQQQ-only 3.0x Nasdaq-100')
print('   worst 20 TQQQ nights (raw leg): what 2xNVDA did')
oT = np.argsort(legT)[:20]
for i in oT:
    print('   %-10s %5s %2s | TQQQ %+7.2f  2xNVDA %+7.2f | trend-rule account: NVDL-only %+7.2f split %+7.2f TQQQ-only %+7.2f' % (dates[i], 'UP' if up[i] else 'DOWN', 'E' if isE[i] else '', 100 * legT[i], 100 * legN[i], 100 * R1[i], 100 * R5[i], 100 * R0[i]))
print('   sums (raw legs): TQQQ %+.1f%%, 2xNVDA %+.1f%%; trend-rule account sums: NVDL-only %+.1f%% split %+.1f%% TQQQ-only %+.1f%%; 2xNVDA worse than TQQQ on %d of 20; UP-state on %d of 20' % (
    100 * legT[oT].sum(), 100 * legN[oT].sum(), 100 * R1[oT].sum(), 100 * R5[oT].sum(), 100 * R0[oT].sum(), (legN[oT] < legT[oT]).sum(), up[oT].sum()))
# drawdown episodes: where is each strategy's worst drawdown
def dd_when(R):
    E = np.concatenate([[1.0], np.cumprod(1 + R)]); pk = np.maximum.accumulate(E); d = E / pk - 1; j = int(d.argmin()); p = int(np.argmax(E[:j + 1]))
    return 100 * d[j], (dates[p - 1] if p > 0 else 'start'), dates[j - 1]
for nm, m in PER:
    idx = np.flatnonzero(m)
    for lab, R in (('NVDL-only', R1), ('split', R5), ('TQQQ-only', R0)):
        E = np.concatenate([[1.0], np.cumprod(1 + R[idx])]); pk = np.maximum.accumulate(E); d = E / pk - 1; j = int(d.argmin()); p = int(np.argmax(E[:j + 1]))
        print('   %s %-9s worst drawdown %.1f%% from %s to %s (trend rule)' % (nm, lab, 100 * d[j], dates[idx[p - 1]] if p > 0 else 'start', dates[idx[j - 1]]))
# per-year min equity from the first night of the year (KILL knife-edge)
print('   per calendar year, minimum equity from the start of the year (trend rule): NVDL-only / split / TQQQ-only')
for y in sorted(set(yr)):
    m = yr == y
    f = lambda R: float(np.concatenate([[1.0], np.cumprod(1 + R[m])]).min())
    print('     %s n=%3d  min equity %.3f / %.3f / %.3f | year growth x%.2f / x%.2f / x%.2f | g %+.3f / %+.3f / %+.3f | DOWN nights %d' % (
        y, m.sum(), f(R1), f(R5), f(R0), np.prod(1 + R1[m]), np.prod(1 + R5[m]), np.prod(1 + R0[m]), g(R1[m]), g(R5[m]), g(R0[m]), (~up[m]).sum()))
print('   years (of 12) in which the split grew faster than NVDL-only: %d ; TQQQ-only faster than NVDL-only: %d' % (
    sum(g(R5[yr == y]) > g(R1[yr == y]) for y in set(yr)), sum(g(R0[yr == y]) > g(R1[yr == y]) for y in set(yr))))
print('   same per-year table, size 0.98 always:')
for y in sorted(set(yr)):
    m = yr == y
    f = lambda R: float(np.concatenate([[1.0], np.cumprod(1 + R[m])]).min())
    print('     %s  min equity %.3f / %.3f / %.3f | year growth x%.2f / x%.2f / x%.2f' % (y, f(F1), f(F5), f(F0), np.prod(1 + F1[m]), np.prod(1 + F5[m]), np.prod(1 + F0[m])))

print('#' * 100); print('E. UPSIDE GIVEN UP: best NVDA nights and rebounds')
ob = np.argsort(-R1)[:20]
print('   20 best NVDL-only nights (trend rule): sum NVDL-only %+.1f%% split %+.1f%% TQQQ-only %+.1f%% (split keeps %.0f%%); earnings nights among them: %d' % (
    100 * R1[ob].sum(), 100 * R5[ob].sum(), 100 * R0[ob].sum(), 100 * R5[ob].sum() / R1[ob].sum(), isE[ob].sum()))
obn = np.argsort(-np.where(ne, R1, -9))[:20]
print('   20 best NON-earnings NVDL-only nights: sum NVDL-only %+.1f%% split %+.1f%% (split keeps %.0f%%)' % (100 * R1[obn].sum(), 100 * R5[obn].sum(), 100 * R5[obn].sum() / R1[obn].sum()))
print('   earnings nights (n=%d): sum of account return NVDL-only %+.1f%% split %+.1f%% TQQQ-only %+.1f%%; log growth contributed: NVDL-only %.3f of %.3f total log (%.0f%%)' % (
    isE.sum(), 100 * R1[isE].sum(), 100 * R5[isE].sum(), 100 * R0[isE].sum(), np.log1p(R1[isE]).sum(), np.log1p(R1).sum(), 100 * np.log1p(R1[isE]).sum() / np.log1p(R1).sum()))
# after the 20 worst NVDA nights: next 20 and 60 nights
for hz in (20, 60):
    a = []; b = []; c = []
    for i in sorted(o):
        if i + 1 + hz <= N:
            a.append(np.prod(1 + R1[i + 1:i + 1 + hz]) - 1); b.append(np.prod(1 + R5[i + 1:i + 1 + hz]) - 1); c.append(np.prod(1 + R0[i + 1:i + 1 + hz]) - 1)
    print('   next %d nights after each of the 20 worst NVDL-only nights (n=%d with full window): mean NVDL-only %+.1f%% split %+.1f%% TQQQ-only %+.1f%% | median %+.1f / %+.1f / %+.1f | NVDL-only ahead of split in %d of %d' % (
        hz, len(a), 100 * np.mean(a), 100 * np.mean(b), 100 * np.mean(c), 100 * np.median(a), 100 * np.median(b), 100 * np.median(c), sum(x > y for x, y in zip(a, b)), len(a)))
# deep-drawdown state of NVDA (close >= 20% below its 250-session closing high) - the state today
nd = sorted(B['NVDA']); nc = np.array([B['NVDA'][d][1] for d in nd]); pos = {d: i for i, d in enumerate(nd)}
below = np.array([nc[pos[d]] / nc[max(0, pos[d] - 249):pos[d] + 1].max() - 1 for d in dates])
for thr in (-0.20, -0.30):
    m = below <= thr
    for nm, mm in PER:
        k = m & mm
        if k.sum() > 20:
            print('   NVDA close <= %d%% below its 250-session high, %s: n=%d (DOWN-trend %d) | g NVDL-only %+.3f split %+.3f TQQQ-only %+.3f | size-0.98-always g %+.3f / %+.3f / %+.3f' % (
                100 * thr, nm, k.sum(), (~up[k]).sum(), g(R1[k]), g(R5[k]), g(R0[k]), g(F1[k]), g(F5[k]), g(F0[k])))

print('#' * 100); print('F. SENSITIVITY: add the night 2026-11-06 -> 2026-11-09 (opens from pm/day_0908_1110.json); TQQQ 11/10 bar is interpolated so 11/9->11/10 cannot be added')
P = load_pm()
T = trend_states(B['QQQ'])
upx, qc, line = T['2026-11-06']
lN = 2 * (P['NVDA']['2026-11-09'][0] / B['NVDA']['2026-11-06'][1] - 1); lT = P['TQQQ']['2026-11-09'][0] / B['TQQQ']['2026-11-06'][1] - 1
sx = 0.98 if upx else 0.25
print('   11/06 QQQ close %.2f vs line %.2f -> %s (size %.2f) | 2xNVDA %+.2f%% TQQQ %+.2f%% | account: NVDL-only %+.2f%% split %+.2f%% TQQQ-only %+.2f%%' % (
    qc, line, 'UP' if upx else 'DOWN', sx, 100 * lN, 100 * lT, 100 * sx * (lN - COST), 100 * sx * (0.5 * lN + 0.5 * lT - COST), 100 * sx * (lT - COST)))
print('   real NVDL official close->open that night: %+.2f%% ; NVDX %+.2f%%' % (100 * (P['NVDL']['2026-11-09'][0] / B['NVDL']['2026-11-06'][1] - 1), 100 * (P['NVDX']['2026-11-09'][0] / B['NVDX']['2026-11-06'][1] - 1)))
for lab, s_, in (('trend', np.append(s_tr, sx)), ('0.98 always', np.append(s_fu, 0.98))):
    ln = np.append(legN, lN); lt = np.append(legT, lT); yy = np.append(yr, '2026')
    for nm, m in (('2021-2026', yy >= '2021'), ('2015-2026', np.ones(N + 1, bool))):
        st = [stats(account_returns(ln[m], lt[m], s_[m], w)) for w in (1.0, 0.5, 0.0)]
        print('   %-11s %s +1 night: g %+.4f / %+.4f / %+.4f (split-NVDL %+.4f) | worst %+.2f / %+.2f / %+.2f | maxDD %+.1f / %+.1f / %+.1f | PAUSE eps %d / %d / %d' % (
            lab, nm, st[0]['g'], st[1]['g'], st[2]['g'], st[1]['g'] - st[0]['g'], st[0]['worst'], st[1]['worst'], st[2]['worst'], st[0]['maxdd'], st[1]['maxdd'], st[2]['maxdd'], st[0]['pause_eps'], st[1]['pause_eps'], st[2]['pause_eps']))
# current trend state through 11/9 (pm) -- QQQ 11/10 bar interpolated
qq = dict(B['QQQ']); qq['2026-11-09'] = P['QQQ']['2026-11-09']
T2 = trend_states(qq)
for d in ('2026-11-04', '2026-11-05', '2026-11-06', '2026-11-09'):
    print('   QQQ %s close %.2f line %.2f (%+.2f%%) -> %s' % (d, T2[d][1], T2[d][2], 100 * (T2[d][1] / T2[d][2] - 1), 'UP' if T2[d][0] else 'DOWN'))
nv = dict(B['NVDA']); nv.update({d: v for d, v in P['NVDA'].items()})
nd2 = sorted(nv); c2 = np.array([nv[d][1] for d in nd2])
print('   NVDA close %s %.2f = %+.1f%% vs its 250-session closing high %.2f (%s)' % (nd2[-1], c2[-1], 100 * (c2[-1] / c2[-250:].max() - 1), c2[-250:].max(), nd2[len(nd2) - 250 + int(c2[-250:].argmax())]))
print('   prices 11/10 close (11/09 for TQQQ): NVDL %.2f, TQQQ %.2f, NVDX %.2f' % (P['NVDL']['2026-11-10'][1], P['TQQQ']['2026-11-09'][1], P['NVDX']['2026-11-10'][1]))

print('#' * 100); print('G. BOOTSTRAP ROBUSTNESS for criterion 3 (whole span, trend rule): seeds and block types')
Rm = np.column_stack([R1, R5, R0])
for seed in (20261110, 1, 2, 3, 4, 5):
    bo = bootstrap(Rm, dates, seed=seed, offset=True)
    k = bo['minE_h'] <= 0.5
    print('   year blocks, random phase, seed %-8d P(KILL250) %.4f / %.4f / %.4f (draws %d / %d / %d; NVDL-only only %d, split only %d, both %d) | P(PAUSE250) %.4f / %.4f / %.4f | P(-39.3%%, i.e. 82.41->50) %.4f / %.4f / %.4f' % (
        seed, k[:, 0].mean(), k[:, 1].mean(), k[:, 2].mean(), k[:, 0].sum(), k[:, 1].sum(), k[:, 2].sum(), (k[:, 0] & ~k[:, 1]).sum(), (k[:, 1] & ~k[:, 0]).sum(), (k[:, 0] & k[:, 1]).sum(),
        bo['pause_h'][:, 0].mean(), bo['pause_h'][:, 1].mean(), bo['pause_h'][:, 2].mean(), *(bo['minE_h'] <= 50 / 82.41).mean(axis=0)))
for bl in (250, 60, 20):
    bo = bootstrap(Rm, dates, seed=SEED, blocklen=bl)
    k = bo['minE_h'] <= 0.5
    print('   circular blocks of %3d nights: P(KILL250) %.4f / %.4f / %.4f | P(PAUSE250) %.4f / %.4f / %.4f | P(-39.3%%) %.4f / %.4f / %.4f | eps/1000n %.2f / %.2f / %.2f' % (
        bl, *k.mean(axis=0), *bo['pause_h'].mean(axis=0), *(bo['minE_h'] <= 50 / 82.41).mean(axis=0), *bo['eps'].mean(axis=0)))
# historical rolling windows (no resampling)
def rolling(R, hz=250):
    E = np.concatenate([[1.0], np.cumprod(1 + R)]); out = []; pz = []
    fl, _ = pause_flags(R)
    for i in range(0, len(R) - hz + 1):
        w = E[i:i + hz + 1] / E[i]; out.append(w.min())
        fl2, _ = pause_flags(R[i:i + hz]); pz.append(fl2.any())
    return np.array(out), np.array(pz)
for lab, R in (('NVDL-only', R1), ('split', R5), ('TQQQ-only', R0)):
    mn, pz = rolling(R)
    print('   historical rolling 250-night windows (%d starts) %-9s: share with min equity <=0.5: %.4f ; <=0.607: %.4f ; <=0.7: %.4f ; share with a PAUSE trigger: %.3f ; worst window min %.3f' % (len(mn), lab, (mn <= 0.5).mean(), (mn <= 50 / 82.41).mean(), (mn <= 0.7).mean(), pz.mean(), mn.min()))
for lab, R in (('NVDL-only', F1), ('split', F5), ('TQQQ-only', F0)):
    mn, pz = rolling(R)
    print('   [0.98 always] rolling 250-night windows %-9s: share min equity <=0.5: %.4f ; <=0.607: %.4f ; share with a PAUSE trigger: %.3f ; worst window min %.3f' % (lab, (mn <= 0.5).mean(), (mn <= 50 / 82.41).mean(), pz.mean(), mn.min()))
