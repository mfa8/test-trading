"""Adjudicator: night-by-night traces of the episodes that matter, plus a vectorised
re-derivation of the trigger flags from the finished size series (pandas rolling max)."""
import numpy as np, pandas as pd
import adj_core as K
frames, rep = K.load_frames()
up, pm = K.trend_series(frames['QQQ'])
nv = K.nights(frames, 'NVDA', up)
d = np.array(nv['dates']); b = np.where(nv['up'], K.UP, K.DOWN)
P1 = K.simulate(nv['r'], b, 'P1', 0.25)
PP = K.simulate(nv['r'], b, 'P2', 0.25, 5, 'post')
PD = K.simulate(nv['r'], b, 'P2', 0.25, 5, 'during')
def roll(E): return pd.Series(E).rolling(20, min_periods=1).max().values
# vectorised re-derivation of C from sizes
for lab, res in (('P1', P1), ('P2post', PP), ('P2during', PD)):
    R = res['size'] * (2 * nv['r'] - K.COST)
    Eout = np.cumprod(1 + R); Ein = np.concatenate(([1.0], Eout[:-1]))
    C = Ein <= 0.80 * roll(Ein)
    print(lab, 'C flags re-derived from sizes: mismatches', int((C != res['C']).sum()), '| paused nights', int(res['pz'].sum()),
          '| paused nights with size != min(b,0.25):', int((res['size'][res['pz']] != np.minimum(b[res['pz']], 0.25)).sum()),
          '| unpaused nights with size != b:', int((res['size'][~res['pz']] != b[~res['pz']]).sum()))
def trace(start, n_before=2, n=24):
    i0 = list(d).index(start) - n_before
    print('\n trace from %s (r = NVDA overnight %%, tr = trend, ratio = E/20-high, C; s = size)' % d[i0])
    print(' date        r%     tr | P1: ratio  C s    | P2post: ratio  C s    | P2during: ratio  C s')
    for t in range(i0, i0 + n):
        row = ' %s %+6.2f  %s |' % (d[t], 100 * nv['r'][t], 'UP ' if nv['up'][t] else 'DN ')
        for res in (P1, PP, PD):
            H = max(res['Ein'][max(0, t - 19):t + 1])
            row += '   %.4f %s %.2f%s |' % (res['Ein'][t] / H, 'C' if res['C'][t] else '.', res['size'][t], '*' if res['pz'][t] else ' ')
        print(row)
trace('2015-05-11', 2, 14)
trace('2023-10-18', 2, 18)
trace('2020-02-27', 2, 22)
trace('2003-08-08', 2, 22)
