"""Adjudicator: how far is the synthetic 2x (2 * NVDA overnight) from the real 2x ETF (NVDL) overnight, where NVDL has real bars?"""
import numpy as np, pandas as pd
import adj_core as K
frames, rep = K.load_frames()
print('NVDL', rep['NVDL']); print('NVDX', rep['NVDX'])
for etf in ('NVDL', 'NVDX'):
    x = frames[etf]; n = frames['NVDA']
    common = sorted(x.index.intersection(n.index))
    # consecutive NVDA sessions only
    pos = {d: i for i, d in enumerate(n.index)}
    rows = []
    for a, b in zip(common[:-1], common[1:]):
        if pos[b] - pos[a] != 1: continue
        rows.append((a, x.loc[b, 'o'] / x.loc[a, 'c'] - 1, 2 * (n.loc[b, 'o'] / n.loc[a, 'c'] - 1)))
    df = pd.DataFrame(rows, columns=['d', 'etf', 'syn']).set_index('d')
    diff = df['etf'] - df['syn']
    print('%s: %d nights %s..%s | mean ETF overnight %+.4f%%, mean synthetic 2x %+.4f%%, mean difference %+.4f%% (s.e. %.4f%%), sd of difference %.3f%%, corr %.4f'
          % (etf, len(df), df.index[0], df.index[-1], 100 * df['etf'].mean(), 100 * df['syn'].mean(), 100 * diff.mean(),
             100 * diff.std(ddof=1) / np.sqrt(len(df)), 100 * diff.std(ddof=1), df['etf'].corr(df['syn'])))
    big = diff.abs().sort_values(ascending=False).head(5)
    print('   largest |ETF - synthetic| nights:', [(d, round(100 * float(diff[d]), 2)) for d in big.index])
    trimmed = diff[diff.abs() < 0.03]
    print('   excluding %d nights with |difference| >= 3%%: mean difference %+.4f%%, sd %.3f%%' % (len(diff) - len(trimmed), 100 * trimmed.mean(), 100 * trimmed.std(ddof=1)))
