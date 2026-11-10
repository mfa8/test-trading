# Break-even diagnostic (not a rule variant): how much lower would the 2x NVDA overnight mean have to be for the split to match NVDL-only on growth?
import sys
import numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/concentration')
from l5lib import *
B = load_long('2026-11-06'); rows = build_nights(B); earn = earnings_dates()
legN = np.array([r['legN'] for r in rows]); legT = np.array([r['legT'] for r in rows]); up = np.array([r['up'] for r in rows])
isE = np.array([r['d'] in earn for r in rows]); yr = np.array([r['d'][:4] for r in rows]); d = np.array([r['d'] for r in rows])
g = lambda R: 100 * float(np.mean(np.log1p(R)))
def solve(f, lo=0.0, hi=0.01):
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2
for lab, s in (('trend rule', np.where(up, 0.98, 0.25)), ('0.98 always', np.full(len(rows), 0.98))):
    for nm, m in (('2015-2020', yr <= '2020'), ('2021-2026', yr >= '2021'), ('2015-2026', yr >= '2015')):
        for bl, keep in (('no blackout', np.ones(len(rows), bool)), ('NVDA part cash on earnings nights', ~isE)):
            def R(w, dl):
                partN = np.where(keep[m], w * (legN[m] - dl - COST), 0.0); partT = (1 - w) * (legT[m] - COST)
                return s[m] * (partN + partT)
            de = solve(lambda dl: g(R(1.0, dl)) - g(R(0.5, dl)))
            dz = solve(lambda dl: g(R(1.0, dl)))
            mN = 100 * legN[m][keep[m]].mean()
            print('%-11s %s %-34s 2xNVDA gross mean %+.3f%%/night | split matches NVDL-only if that mean were lower by %.3f (i.e. %+.3f) | NVDL-only growth hits zero if lower by %.3f (i.e. %+.3f) | TQQQ gross mean %+.3f' % (
                lab, nm, bl, mN, 100 * de, mN - 100 * de, 100 * dz, mN - 100 * dz, 100 * legT[m].mean()))
# real NVDL 2x era from 2024-01-23
X = [(r['d'], B['NVDL'][r['n']][0] / B['NVDL'][r['d']][1] - 1, r['legN'], r['legT'], r['up']) for r in rows if r['d'] >= '2024-01-23' and r['d'] in B['NVDL'] and r['n'] in B['NVDL']]
real = np.array([x[1] for x in X]); syn = np.array([x[2] for x in X]); lt = np.array([x[3] for x in X]); u = np.array([x[4] for x in X]); dd = np.array([x[0] for x in X]); e = np.array([x in earn for x in dd])
df = real - syn; ok = np.abs(df) <= 0.01
print('real NVDL 2x era from 2024-01-23: n=%d | mean diff real-syn %+.4f%% (se %.4f), excl |diff|>1%% (n=%d) %+.4f%% (se %.4f) -> about %.1f%% a year | corr %.4f' % (
    len(X), 100 * df.mean(), 100 * df.std(ddof=1) / len(X) ** .5, ok.sum(), 100 * df[ok].mean(), 100 * df[ok].std(ddof=1) / ok.sum() ** .5, 251 * 100 * df[ok].mean(), np.corrcoef(real, syn)[0, 1]))
s = np.where(u, 0.98, 0.25)
for nm, leg in (('real NVDL', real), ('synthetic', syn)):
    st = [stats(s * (w * leg + (1 - w) * lt - COST)) for w in (1.0, 0.5, 0.0)]
    print('   L5 on %s, trend rule, 2024-01-23..2026-11-05 n=%d: g %+.4f / %+.4f / %+.4f (split minus only %+.4f) | worst %+.2f / %+.2f / %+.2f | maxDD %+.1f / %+.1f / %+.1f' % (
        nm, len(X), st[0]['g'], st[1]['g'], st[2]['g'], st[1]['g'] - st[0]['g'], st[0]['worst'], st[1]['worst'], st[2]['worst'], st[0]['maxdd'], st[1]['maxdd'], st[2]['maxdd']))
