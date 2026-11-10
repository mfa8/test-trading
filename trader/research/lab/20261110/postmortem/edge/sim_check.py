"""(a) scalar re-implementation of the rules, compared path by path with the vectorised sim;
(b) long-horizon race: back above 98.75 first, or 50 first."""
import sys, math
import numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge')
import sim as S
def scalar(idx_row,blackout=True):
    E=S.E0; hist=list(S.SEED_WINDOW); in_pause=True; nights_in=0  # nights already served in this pause
    out=[]; killed=False
    for j in idx_row:
        if killed: out.append(E); continue
        H=max(hist[-20:]); trig=0.8*H
        if in_pause and nights_in>=5 and E>trig: in_pause=False; nights_in=0
        if (not in_pause) and E<=trig: in_pause=True; nights_in=0
        size=0.98 if S.UPs[j] else 0.25
        if in_pause: size=min(size,0.25); nights_in+=1
        if blackout and S.EARN[j]: size=0.0
        E=E*(1+size*S.U[j])
        if E<=S.KILL: killed=True
        hist.append(E); out.append(E)
    return out
rng=np.random.default_rng(7)
idx=S.make_paths(2015,2026,3000,rng)
res=S.run(idx)
worst=0
for h in S.HORIZ:
    ref=np.array([scalar(idx[i])[h-1] for i in range(3000)])
    worst=max(worst,np.abs(ref-res['snap'][h]).max())
print('scalar vs vectorised, 3000 paths (2015-26, blackout): max abs equity difference at the 4 horizons = %.2e'%worst)
idx=S.make_paths(2000,2014,3000,rng)
res=S.run(idx,blackout=False)
worst=max(np.abs(np.array([scalar(idx[i],False)[h-1] for i in range(3000)])-res['snap'][h]).max() for h in S.HORIZ)
print('scalar vs vectorised, 3000 paths (2000-14, no blackout): max abs difference = %.2e'%worst)
# (b) race, horizon 1500 nights
S.T=1500; S.HORIZ=(250,500,750,1000,1500)
rng=np.random.default_rng(99)
for lab,lo,hi,kw in (('2015-2026 blackout',2015,2026,{}),('2000-2014 no blackout',2000,2014,dict(blackout=False)),
                     ('2015-2026 blackout, no edge (mean removed)',2015,2026,dict(demean=S.U[(S.YEAR>=2015)&(~S.EARN)].mean())),
                     ('2015-2026 blackout, +10bp drag',2015,2026,dict(extra_cost=0.0010)),
                     ('2015-2026 blackout, +28bp drag',2015,2026,dict(extra_cost=0.0028))):
    idx=S.make_paths(lo,hi,40000,rng)
    r=S.run(idx,**kw)
    print('RACE %-44s'%lab,' | '.join('by %d nights: above 98.75 first %.1f%%, 50 first %.1f%%, neither %.1f%%'%(h,100*r['reach'][h],100*r['killfirst'][h],100*(1-r['reach'][h]-r['killfirst'][h])) for h in (250,750,1500)))
