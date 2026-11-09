# T4: does the STATE known at the close (today's NVDA move, recent realised vol, trend) change the next overnight's growth?
import csv, math, statistics as st
from load import load
B=load()
earn=set(r['date'] for r in csv.DictReader(open('/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv')) if r['earn']=='1')
C=0.0009  # 4bp product drag + 5bp round-trip cost
def series(sym,lev):
    b=B[sym]; ds=sorted(b); out=[]
    for i in range(200,len(ds)-1):
        d=ds[i]; c=b[d][3]; o1=b[ds[i+1]][0]
        if d in earn: continue
        cc=[b[ds[j]][3]/b[ds[j-1]][3]-1 for j in range(i-19,i+1)]
        rv5=math.sqrt(sum(x*x for x in cc[-5:])/5); rv20=math.sqrt(sum(x*x for x in cc)/20)
        hist=[]  # trailing 252d distribution of rv5 computed lazily below
        sma50=sum(b[ds[j]][3] for j in range(i-49,i+1))/50; sma200=sum(b[ds[j]][3] for j in range(i-199,i+1))/200
        out.append(dict(d=d,on=lev*(o1/c-1)-C,r=cc[-1],rv5=rv5,rv20=rv20,a50=c>sma50,a200=c>sma200,idr=c/b[d][0]-1))
    # trailing percentile of rv5 (252 obs, no look-ahead)
    for k,x in enumerate(out):
        w=[y['rv5'] for y in out[max(0,k-252):k]]
        x['p5']=sum(v<x['rv5'] for v in w)/len(w) if len(w)>=60 else None
        w=[y['rv20'] for y in out[max(0,k-252):k]]
        x['p20']=sum(v<x['rv20'] for v in w)/len(w) if len(w)>=60 else None
    return out
def stat(v):
    if len(v)<8: return "n=%3d"%len(v)
    m=st.mean(v); s=st.stdev(v); g=st.mean([math.log(1+x) for x in v])
    return "n=%4d mean %+.3f sd %5.2f t %+5.2f g %+.3f"%(len(v),100*m,100*s,m/(s/math.sqrt(len(v))),100*g)
P=[('2015','2018'),('2019','2022'),('2023','2024'),('2025','2026'),('2015','2026')]
def inp(x,a,b): return a<=x['d'][:4]<=b
for sym,lev in (('NVDA',2),('SMH',3)):
    X=series(sym,lev)
    print("=====",sym,"x",lev,"overnight, net 9bp, ex NVDA earnings nights; n",len(X))
    print("-- by today's close-to-close move")
    for lo,hi in [(-1,-.05),(-.05,-.03),(-.03,-.015),(-.015,0),(0,.015),(.015,.03),(.03,.05),(.05,1)]:
        print("  r in [%+.1f,%+.1f): "%(100*lo,100*hi)+" | ".join(stat([x['on'] for x in X if lo<=x['r']<hi and inp(x,a,b)]) for a,b in (P[-1],)))
    for nm,f in [("r<=-3%",lambda x:x['r']<=-.03),("r<=-4%",lambda x:x['r']<=-.04),("|r|>=4%",lambda x:abs(x['r'])>=.04),("rv5 top20% (trail252)",lambda x:x['p5'] is not None and x['p5']>=.8),("rv5 top10%",lambda x:x['p5'] is not None and x['p5']>=.9),("rv20 top20%",lambda x:x['p20'] is not None and x['p20']>=.8),("below SMA50",lambda x:not x['a50']),("below SMA200",lambda x:not x['a200'])]:
        print("-- state:",nm)
        for a,b in P:
            print("   %s-%s  IN: %-52s OUT: %s"%(a,b,stat([x['on'] for x in X if f(x) and inp(x,a,b)]),stat([x['on'] for x in X if not f(x) and inp(x,a,b)])))
    # strategy sims: size s in state, 1 otherwise
    print("-- strategy log growth per night (all nights incl. skipped=0), by period")
    for nm,f in [("always full",lambda x:False),("r<=-3%",lambda x:x['r']<=-.03),("r<=-4%",lambda x:x['r']<=-.04),("|r|>=4%",lambda x:abs(x['r'])>=.04),("rv5 top20%",lambda x:x['p5'] is not None and x['p5']>=.8),("rv20 top20%",lambda x:x['p20'] is not None and x['p20']>=.8),("below SMA50",lambda x:not x['a50']),("below SMA200",lambda x:not x['a200'])]:
        for sz in ((1.0,) if nm=="always full" else (0.5,0.0)):
            row=[]
            for a,b in P:
                v=[(sz if f(x) else 1.0)*x['on'] for x in X if inp(x,a,b)]
                eq=1; pk=1; dd=0
                for y in v:
                    eq*=1+y; pk=max(pk,eq); dd=min(dd,eq/pk-1)
                row.append("%+.3f/dd%4.0f%%"%(100*st.mean([math.log(1+y) for y in v]),100*dd))
            print("   %-14s size %.1f : "%(nm,sz)+"  ".join(row))
