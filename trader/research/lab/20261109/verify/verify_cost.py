import sys, io, contextlib
sys.path.insert(0, '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/verify_t8')
with contextlib.redirect_stdout(io.StringIO()):
    import verify_t8 as V
import numpy as np
g, st, ps = V.g100, V.strat, V.psel
print('cost sensitivity NVDA: full / mkt / diff')
for c in (0.0, 0.0009, 0.0018, 0.0030):
    print(f"  cost {1e4*c:>4.0f}bp " + ' | '.join(
        f"{a}-{b} {g(st(ps(V.dN,a,b),'full',cost=c)):.3f} {g(st(ps(V.dN,a,b),'mkt',cost=c)):.3f} {g(st(ps(V.dN,a,b),'mkt',cost=c))-g(st(ps(V.dN,a,b),'full',cost=c)):+.3f}"
        for a, b in V.PERIODS))
p = V.dN; b = p.mk.values.astype(int)
dd = np.log1p(st(p,'mkt')) - np.log1p(st(p,'full'))
L = np.zeros(len(b), int); i = 0
while i < len(b):
    if b[i]:
        j = i
        while j+1 < len(b) and b[j+1]: j += 1
        L[i:j+1] = j-i+1; i = j+1
    else: i += 1
for lo, hi in ((1,5),(6,20),(21,59),(60,999)):
    m = (L>=lo)&(L<=hi)
    print(f"  episodes len {lo}-{hi}: nights {m.sum()}, gain {dd[m].sum():+.2f} log pts, mean R {100*p.R.values[m].mean():+.3f}% sd {100*p.R.values[m].std():.2f}%")
# first-k nights of each episode vs later
k = np.zeros(len(b), int); run = 0
for i in range(len(b)):
    run = run+1 if b[i] else 0; k[i] = run
for lo, hi in ((1,5),(6,20),(21,999)):
    m = (k>=lo)&(k<=hi)
    print(f"  nights {lo}-{hi} into a BELOW episode (known ex-ante): n {m.sum()}, gain {dd[m].sum():+.2f}, mean R {100*p.R.values[m].mean():+.3f}% sd {100*p.R.values[m].std():.2f}%")
