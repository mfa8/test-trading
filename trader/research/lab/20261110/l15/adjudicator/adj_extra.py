"""Adjudicator: extra checks for the weaknesses list (prints only)."""
import math, numpy as np
import adj_core as K
frames, rep = K.load_frames()
up, pm = K.trend_series(frames['QQQ'])
N = {s: K.nights(frames, s, up) for s in K.NAMES}
print('== per name, trend on, p=0.25, whole span ==')
print('name   P0 g     P1 g     P2post-P1  P2during-P1  P1 episodes  nights differing (post)  largest single-year share of |P2post-P1| total')
tot_eps = 0
for s in K.NAMES:
    nt = N[s]; b = np.where(nt['up'], K.UP, K.DOWN)
    yrs = np.array([int(x[:4]) for x in nt['dates']])
    p0 = K.simulate(nt['r'], b, 'P0'); p1 = K.simulate(nt['r'], b, 'P1', 0.25)
    pp = K.simulate(nt['r'], b, 'P2', 0.25, 5, 'post'); pd_ = K.simulate(nt['r'], b, 'P2', 0.25, 5, 'during')
    d = pp['lr'] - p1['lr']
    ys = {y: d[yrs == y].sum() for y in np.unique(yrs)}
    big = max(ys.items(), key=lambda t: abs(t[1]))
    rest = d.sum() - big[1]
    tot_eps += len(p1['eps'])
    print('%-5s %+.4f  %+.4f  %+.4f    %+.4f       %3d          %4d        total %+.4f; biggest year %d %+.4f; without it %+.4f%s'
          % (s, 100 * p0['lr'].mean(), 100 * p1['lr'].mean(), 100 * d.mean(), 100 * (pd_['lr'] - p1['lr']).mean(),
             len(p1['eps']), int((d != 0).sum()), d.sum(), big[0], big[1], rest, '  SIGN FLIPS' if rest * d.sum() < 0 else ''))
print('P1 episodes over 11 names:', tot_eps)

nt = N['NVDA']; b = np.where(nt['up'], K.UP, K.DOWN); dts = np.array(nt['dates'])
p1 = K.simulate(nt['r'], b, 'P1', 0.25); pp = K.simulate(nt['r'], b, 'P2', 0.25, 5, 'post'); p0 = K.simulate(nt['r'], b, 'P0')
print('\n== NVDA drawdowns inside calendar windows (trend on, p=0.25): P0 / P1 / P2post ==')
for lo, hi in (('2020-01-02', '2020-12-31'), ('2003-01-02', '2003-12-31'), ('2019-01-02', '2019-12-31'), ('2022-01-03', '2023-12-29'), ('2024-01-02', '2025-12-31')):
    m = (dts >= lo) & (dts <= hi)
    print('  %s..%s: %.2f / %.2f / %.2f' % (lo, hi, K.maxdd(p0['lr'][m]), K.maxdd(p1['lr'][m]), K.maxdd(pp['lr'][m])))
# where does each variant's worst H2 drawdown sit
def dd_dates(lr, d):
    path = np.concatenate(([0.0], np.cumsum(lr))); pk = np.maximum.accumulate(path)
    i = int(np.argmin(path - pk)); j = int(np.argmax(path[:i + 1]))
    return d[max(j - 1, 0)], d[i - 1]
m2 = dts >= '2015-01-02'; m1 = ~m2
for lab, res in (('P1', p1), ('P2post', pp)):
    print('  %s worst H1 drawdown runs %s -> %s ; worst H2 drawdown runs %s -> %s' % ((lab,) + dd_dates(res['lr'][m1], dts[m1]) + dd_dates(res['lr'][m2], dts[m2])))
# the three March-2020 nights
d = pp['lr'] - p1['lr']
idx = [list(dts).index(x) for x in ('2020-03-05', '2020-03-06', '2020-03-10')]
print('\nP2post - P1 on the nights of 2020-03-05, 03-06, 03-10: %s ; sum %+.4f ; H2 total %+.4f ; H2 total without these three nights %+.4f'
      % (['%+.4f' % d[i] for i in idx], d[idx].sum(), d[m2].sum(), d[m2].sum() - d[idx].sum()))
i03 = [i for i, x in enumerate(dts) if '2003-08-15' <= x <= '2003-09-04']
print('P2post - P1 on the %d nights 2003-08-15..2003-09-04: sum %+.4f ; H1 total %+.4f ; best single night %+.4f' % (len(i03), d[i03].sum(), d[m1].sum(), d[i03].max()))
print('trigger night of the 2003 episode: overnight r on 2003-08-07 = %+.2f%% ; of the 2020 episode: 2020-02-26 = %+.2f%%' % (
    100 * nt['r'][list(dts).index('2003-08-07')], 100 * nt['r'][list(dts).index('2020-02-26')]))
# NVDA P1/P2 difference: top-|x| nights
o = np.argsort(-np.abs(d))[:8]
print('largest single-night P2post-P1 differences:', [(dts[i], round(float(d[i]), 4)) for i in o])
print('sum of the 5 largest |night| differences: %+.4f of total %+.4f' % (d[o[:5]].sum(), d.sum()))
