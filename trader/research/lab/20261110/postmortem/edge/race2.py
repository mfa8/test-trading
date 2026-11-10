import sys
import numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge')
import sim as S
S.T=1500; S.HORIZ=(250,750,1500)
rng=np.random.default_rng(5)
m=(S.YEAR>=2015)&(~S.EARN); dm=np.where(S.UPs,S.U[m&S.UPs].mean(),S.U[m&(~S.UPs)].mean())
r=S.run(S.make_paths(2015,2026,40000,rng),demean=dm)
print('RACE C0 (2015-26, blackout, no edge in either state):',' | '.join('by %d: above 98.75 first %.1f%%, 50 first %.1f%%'%(h,100*r['reach'][h],100*r['killfirst'][h]) for h in S.HORIZ))
r=S.run(S.make_paths(2015,2026,40000,rng),demean=0.5*S.U[m].mean())
print('RACE C4 (2015-26, blackout, half edge):',' | '.join('by %d: above 98.75 first %.1f%%, 50 first %.1f%%'%(h,100*r['reach'][h],100*r['killfirst'][h]) for h in S.HORIZ))
