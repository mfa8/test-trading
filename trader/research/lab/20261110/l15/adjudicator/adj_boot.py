"""Adjudicator: year-block bootstrap intervals for the NVDA differences (trend on, p=0.25). Seed 20261110, 2,000 draws."""
import numpy as np
import adj_core as K
frames, rep = K.load_frames()
up, pm = K.trend_series(frames['QQQ'])
nv = K.nights(frames, 'NVDA', up)
b = np.where(nv['up'], K.UP, K.DOWN)
yrs = np.array([int(x[:4]) for x in nv['dates']]); mk = K.masks(nv['dates'])
S = {'P0': K.simulate(nv['r'], b, 'P0'), 'P1': K.simulate(nv['r'], b, 'P1', 0.25),
     'P2post': K.simulate(nv['r'], b, 'P2', 0.25, 5, 'post'), 'P2during': K.simulate(nv['r'], b, 'P2', 0.25, 5, 'during'),
     'P3': K.simulate(nv['r'], b, 'P3', 0.25), 'P2x10': K.simulate(nv['r'], b, 'P2', 0.25, 10, 'post')}
def boot(dv, yv, seed=20261110, ndraw=2000):
    uy = np.unique(yv); sums = np.array([dv[yv == y].sum() for y in uy]); cnt = np.array([(yv == y).sum() for y in uy], float)
    rng = np.random.default_rng(seed); out = np.empty(ndraw)
    for i in range(ndraw):
        pick = rng.integers(0, len(uy), len(uy)); out[i] = 100 * sums[pick].sum() / cnt[pick].sum()
    return np.percentile(out, 5), np.percentile(out, 95)
for a, c in (('P1', 'P0'), ('P2post', 'P0'), ('P2during', 'P0'), ('P3', 'P0'), ('P2post', 'P1'), ('P2during', 'P1'), ('P2x10', 'P1')):
    d = S[a]['lr'] - S[c]['lr']
    print('%-9s - %-3s' % (a, c), ' | '.join('%s %+.4f [%+.4f, %+.4f]' % ((h, 100 * d[mk[h]].mean()) + boot(d[mk[h]], yrs[mk[h]])) for h in ('H1', 'H2', 'ALL')))
