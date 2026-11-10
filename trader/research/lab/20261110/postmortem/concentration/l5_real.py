# L5: real NVDL / NVDX against the synthetic 2x NVDA leg; live-window comparison; trade-log check.
import sys, csv
import numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/concentration')
from l5lib import *

B = load_long('2026-11-06')
rows = build_nights(B)
earn = earnings_dates()
T = trend_states(B['QQQ'])
ed = {r['date']: r for r in csv.DictReader(open(EARN_CSV))}
g = lambda R: 100 * float(np.mean(np.log1p(R)))

def real_series(sym):
    out = []
    for r in rows:
        t, n = r['d'], r['n']
        if t in B[sym] and n in B[sym]:
            on = B[sym][n][0] / B[sym][t][1] - 1
            cc = B[sym][n][1] / B[sym][t][1] - 1
            ncc = B['NVDA'][n][1] / B['NVDA'][t][1] - 1
            out.append(dict(d=t, n=n, real=on, syn=r['legN'], nv=r['nvda_on'], legT=r['legT'], up=r['up'], cc=cc, ncc=ncc, earn=t in earn))
    return out

for sym in ('NVDL', 'NVDX'):
    X = real_series(sym)
    d = np.array([x['d'] for x in X]); real = np.array([x['real'] for x in X]); syn = np.array([x['syn'] for x in X]); nv = np.array([x['nv'] for x in X])
    cc = np.array([x['cc'] for x in X]); ncc = np.array([x['ncc'] for x in X]); legT = np.array([x['legT'] for x in X]); up = np.array([x['up'] for x in X]); isE = np.array([x['earn'] for x in X])
    print('#' * 100)
    print('%s real bars: %d nights with valid bars on both sides, %s .. %s (first valid bar %s)' % (sym, len(X), d[0], d[-1], min(B[sym])))
    # leverage by half-year (close-to-close beta and overnight beta)
    print('   leverage check (OLS slope on NVDA): by half-year, close-to-close | overnight')
    hy = np.array([x[:4] + ('H1' if x[5:7] <= '06' else 'H2') for x in d])
    for h in sorted(set(hy)):
        m = hy == h
        if m.sum() > 20:
            print('     %s n=%3d  cc beta %.2f (corr %.3f) | overnight beta %.2f (corr %.3f)' % (h, m.sum(), np.polyfit(ncc[m], cc[m], 1)[0], corr(ncc[m], cc[m]), np.polyfit(nv[m], real[m], 1)[0], corr(nv[m], real[m])))
    if sym == 'NVDL':
        mo = np.array([x[:7] for x in d])
        print('   NVDL monthly close-to-close beta around the leverage change: ' + ' '.join('%s %.2f' % (h, np.polyfit(ncc[mo == h], cc[mo == h], 1)[0]) for h in sorted(set(mo)) if '2023-10' <= h <= '2024-04'))
        rat = cc / ncc
        jj = [i for i in range(len(d)) if '2024-01-02' <= d[i] <= '2024-02-29' and abs(ncc[i]) > 0.01]
        print('   daily ratio NVDL cc / NVDA cc on days NVDA moved >1%: ' + ' '.join('%s %.2f' % (d[i][5:], rat[i]) for i in jj))
    diff = real - syn
    big = np.abs(diff) > 0.01
    print('   nights with |real - synthetic| > 1%%: %d' % big.sum())
    for i in np.flatnonzero(big)[:60]:
        e = ed.get(d[i], {})
        print('     %s real %+7.2f%% syn %+7.2f%% diff %+6.2f%% %s %s' % (d[i], 100 * real[i], 100 * syn[i], 100 * diff[i], 'E' if isE[i] else '', ('repo nvdl_on=%s clean=%s' % (e.get('nvdl_on'), e.get('nvdl_clean'))) if sym == 'NVDL' else ''))
    return_sets = {}
    # choose the 2x era: from the first half-year where cc beta > 1.8 onward (reported above); also report all
    for lab, m in (('all nights', np.ones(len(X), bool)), ('from 2024-07-01', d >= '2024-07-01'), ('2x era excl. |diff|>1%', (d >= '2024-07-01') & ~big), ('2x era non-earnings excl. |diff|>1%', (d >= '2024-07-01') & ~big & ~isE)):
        if m.sum() < 30:
            continue
        df = diff[m]
        print('   %-36s n=%4d | mean real %+.4f%% syn %+.4f%% | mean diff %+.4f%% (se %.4f) median %+.4f%% sd %.3f%% | corr %.4f | slope real on NVDA %.3f | g real %+.4f syn %+.4f (cost 9bp, 0.98)' % (
            lab, m.sum(), 100 * real[m].mean(), 100 * syn[m].mean(), 100 * df.mean(), 100 * df.std(ddof=1) / m.sum() ** .5, 100 * np.median(df), 100 * df.std(ddof=1), corr(real[m], syn[m]),
            np.polyfit(nv[m], real[m], 1)[0], g(0.98 * (real[m] - COST)), g(0.98 * (syn[m] - COST))))
    # L5 comparison on the real vehicle, trend rule, common nights
    for lab, m in (('all real nights', np.ones(len(X), bool)), ('from 2024-07-01', d >= '2024-07-01')):
        s = np.where(up[m], 0.98, 0.25)
        res = []
        for nm, leg in (('real', real[m]), ('synthetic', syn[m])):
            st = [stats(s * (w * leg + (1 - w) * legT[m] - COST)) for w in (1.0, 0.5, 0.0)]
            res.append(st)
            print('   L5 on %-9s %s leg, trend rule, %-16s n=%4d: g %+.4f / %+.4f / %+.4f (split-minus-only %+.4f) | worst %+.2f / %+.2f / %+.2f | maxDD %+.1f / %+.1f / %+.1f | PAUSE eps %d / %d / %d' % (
                nm, sym, lab, m.sum(), st[0]['g'], st[1]['g'], st[2]['g'], st[1]['g'] - st[0]['g'], st[0]['worst'], st[1]['worst'], st[2]['worst'], st[0]['maxdd'], st[1]['maxdd'], st[2]['maxdd'], st[0]['pause_eps'], st[1]['pause_eps'], st[2]['pause_eps']))
    # worst nights real vs synthetic
    o = np.argsort(real)[:8]
    print('   8 worst real %s nights: ' % sym + '; '.join('%s real %+.1f%% syn %+.1f%% TQQQ %+.1f%%' % (d[i], 100 * real[i], 100 * syn[i], 100 * legT[i]) for i in o))

# NVDL vs NVDX on common nights
XL = {x['d']: x for x in real_series('NVDL')}; XX = {x['d']: x for x in real_series('NVDX')}
cm = sorted(set(XL) & set(XX))
a = np.array([XL[d]['real'] for d in cm]); b = np.array([XX[d]['real'] for d in cm])
print('#' * 100)
print('NVDL vs NVDX, %d common nights from %s: mean %+.4f%% vs %+.4f%%, corr %.4f, nights differing by >1%%: %s' % (len(cm), cm[0], 100 * a.mean(), 100 * b.mean(), corr(a, b), [(d, round(100 * (XL[d]['real'] - XX[d]['real']), 2)) for d in cm if abs(XL[d]['real'] - XX[d]['real']) > 0.01]))
m2 = np.array([d >= '2024-07-01' for d in cm])
print('   from 2024-07-01: n=%d mean NVDL %+.4f%% NVDX %+.4f%% corr %.4f' % (m2.sum(), 100 * a[m2].mean(), 100 * b[m2].mean(), corr(a[m2], b[m2])))

# ------- live window -------
print('#' * 100)
print('LIVE WINDOW (official close->open from pm/day_0908_1110.json; not our fills)')
P = load_pm()
tr = [r for r in csv.reader(open(PM + 'trades.csv')) if r and r[0].startswith('T3X-N')]
PNL = lambda r: (float(r[13]) - float(r[8])) * float(r[9])  # recomputed from fills: early rows store pnl/pct in swapped columns (RULES s8)
print('   overnight legs in trades.csv: %d rows, %d nights, P&L recomputed from fills $%.2f; by symbol: %s' % (
    len(tr), len(set(r[0] for r in tr)), sum(PNL(r) for r in tr),
    {s: round(sum(PNL(r) for r in tr if r[2] == s), 2) for s in sorted(set(r[2] for r in tr))}))
nights = sorted(set((r[0], r[1]) for r in tr), key=lambda x: x[1])
pd = sorted(P['NVDL'])
tot = {}
lines = []
for nid, d in nights:
    i = pd.index(d); n = pd[i + 1] if i + 1 < len(pd) else None
    rec = dict(id=nid, d=d, n=n)
    for s in ('NVDL', 'TQQQ', 'NVDA'):
        rec[s] = (P[s][n][0] / P[s][d][1] - 1) if (n and d in P[s] and n in P[s]) else None
    pnl = sum(PNL(r) for r in tr if r[0] == nid); cost = sum(float(r[8]) * float(r[9]) for r in tr if r[0] == nid)
    rec['pnl'] = pnl; rec['cost'] = cost; rec['syms'] = '+'.join(sorted(set(r[2] for r in tr if r[0] == nid)))
    lines.append(rec)
ok = [x for x in lines if x['NVDL'] is not None and x['TQQQ'] is not None]
nvdl = np.array([x['NVDL'] for x in ok]); tq = np.array([x['TQQQ'] for x in ok])
print('   nights with both NVDL and TQQQ official bars: %d of %d (missing: %s)' % (len(ok), len(lines), [x['id'] for x in lines if x not in ok]))
print('   close->open over those %d nights, full size, no cost: NVDL sum %+.1f%% compounded %+.1f%% | TQQQ sum %+.1f%% compounded %+.1f%% | 50/50 sum %+.1f%% compounded %+.1f%% | corr %.2f' % (
    len(ok), 100 * nvdl.sum(), 100 * (np.prod(1 + nvdl) - 1), 100 * tq.sum(), 100 * (np.prod(1 + tq) - 1), 100 * (0.5 * nvdl + 0.5 * tq).sum(), 100 * (np.prod(1 + 0.5 * nvdl + 0.5 * tq) - 1), corr(nvdl, tq)))
# dollar counterfactual: same dollars at risk each night as actually deployed, but in NVDL / TQQQ / split at official close->open
dn = sum(x['cost'] * x['NVDL'] for x in ok); dt = sum(x['cost'] * x['TQQQ'] for x in ok)
act = sum(x['pnl'] for x in ok)
print('   same dollars as actually deployed each night (from trades.csv), at official close->open: all-NVDL $%+.2f | all-TQQQ $%+.2f | 50/50 $%+.2f | actual fills on those nights $%+.2f' % (dn, dt, 0.5 * dn + 0.5 * dt, act))
nvera = [x for x in ok if x['d'] >= '2026-10-14']
dn2 = sum(x['cost'] * x['NVDL'] for x in nvera); dt2 = sum(x['cost'] * x['TQQQ'] for x in nvera)
print('   NVDA-only era (entries from 2026-10-14, %d nights): all-NVDL $%+.2f | all-TQQQ $%+.2f | 50/50 $%+.2f | actual $%+.2f' % (len(nvera), dn2, dt2, 0.5 * dn2 + 0.5 * dt2, sum(x['pnl'] for x in nvera)))
print('   worst 6 actual nights: ' + '; '.join('%s %s %s $%+.2f (NVDL c->o %+.1f%%, TQQQ c->o %s)' % (x['id'], x['d'], x['syms'], x['pnl'], 100 * x['NVDL'] if x['NVDL'] is not None else float('nan'), ('%+.1f%%' % (100 * x['TQQQ'])) if x['TQQQ'] is not None else 'n/a') for x in sorted(lines, key=lambda x: x['pnl'])[:6]))
x43 = [x for x in lines if x['id'] == 'T3X-N43'][0]
print('   N43 (11/6->11/9): actual $%+.2f on $%.2f deployed; 50/50 at official prices would have been $%+.2f; all-TQQQ $%+.2f' % (x43['pnl'], x43['cost'], x43['cost'] * (0.5 * x43['NVDL'] + 0.5 * x43['TQQQ']), x43['cost'] * x43['TQQQ']))
