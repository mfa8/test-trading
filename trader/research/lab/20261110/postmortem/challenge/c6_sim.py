import sys, numpy as np
sys.dont_write_bytecode=True
sys.path.insert(0,'/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge')
import sim as S
rng=np.random.default_rng(99); N=60000
def show(lab,res):
    out=[]
    for h in (20,60,125,250):
        e=res['snap'][h]; q=np.percentile(e,[5,25,50,75,95])
        out.append('%d: %s | >98.75 %.0f%% | ever %.0f%% | kill %.1f%%'%(h,'/'.join('%.1f'%x for x in q),100*np.mean(e>S.START),100*res['reach'][h],100*res['kill'][h]))
    print(lab); [print('   ',o) for o in out]
m=(S.YEAR>=2015)&(~S.EARN)
print('pool means (after 9bp): 2015-26 ex-earn %.3f%%; 2000-14 %.3f%%'%(100*S.U[m].mean(),100*S.U[S.YEAR<=2014].mean()))
show('A1 repeat (my seed)',S.run(S.make_paths(2015,2026,N,rng)))
show('MY CENTRAL-KIND: 2015-26, +3bp fund drag +6bp extra execution (15bp execution total) = extra 9bp',S.run(S.make_paths(2015,2026,N,rng),extra_cost=0.0009))
show('2015-26, extra 9bp AND half the remaining edge',S.run(S.make_paths(2015,2026,N,rng),extra_cost=0.0009,demean=0.5*(S.U[m].mean()-0.0009)))
show('2000-14, extra 9bp',S.run(S.make_paths(2000,2014,N,rng),blackout=False,extra_cost=0.0009))
show('2000-26, extra 9bp, no blackout',S.run(S.make_paths(2000,2026,N,rng),blackout=False,extra_cost=0.0009))
show('2015-26 extra 20bp (the live NVDA-2x gap of ~30bp vs 9bp modelled)',S.run(S.make_paths(2015,2026,N,rng),extra_cost=0.0020))
# per-state means
for lab,mm in [('2015-26 ex-earn',m),('2000-14',S.YEAR<=2014)]:
    print(lab,'UP mean %.3f n %d | DOWN mean %.3f n %d'%(100*S.U[mm&S.UPs].mean(),(mm&S.UPs).sum(),100*S.U[mm&~S.UPs].mean(),(mm&~S.UPs).sum()))
