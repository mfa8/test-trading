import sys, json
import numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge')
import sim as S
rng=np.random.default_rng(4242); N=200000
m=(S.YEAR>=2015)&(~S.EARN)
mu_up=S.U[m&S.UPs].mean(); mu_dn=S.U[m&(~S.UPs)].mean()
dm=np.where(S.UPs,mu_up,mu_dn)
print('state means removed (2015-26 ex-earnings): UP %+.3f%%, DOWN %+.3f%%'%(100*mu_up,100*mu_dn))
idx=S.make_paths(2015,2026,N,rng)
r=S.run(idx,demean=dm); S.table('C0: 2015-2026 year blocks, blackout, NO EDGE IN EITHER STATE (each state mean removed; volatility kept)',r)
m0=(S.YEAR<=2014); mu_up0=S.U[m0&S.UPs].mean(); mu_dn0=S.U[m0&(~S.UPs)].mean()
dm0=np.where(S.UPs,mu_up0,mu_dn0)
idx0=S.make_paths(2000,2014,N,rng)
r0=S.run(idx0,blackout=False,demean=dm0); S.table('C0b: 2000-2014 year blocks, NO EDGE IN EITHER STATE',r0)
# main spec repeated with a second seed, to show Monte-Carlo noise
r2=S.run(S.make_paths(2015,2026,N,rng)); S.table('A1 repeat (different seed)',r2)
r3=S.run(S.make_paths(2000,2014,N,rng),blackout=False); S.table('B1 repeat (different seed)',r3)
# half-edge: 2015-26 ex-earnings mean halved in each state
r4=S.run(S.make_paths(2015,2026,N,rng),demean=0.5*S.U[m].mean()); S.table('C4: 2015-2026, blackout, every night lowered by half the ex-earnings mean (edge +0.074%)',r4)
