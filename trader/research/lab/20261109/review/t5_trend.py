# T5: OUT-OF-SAMPLE test of the trend state found in T4 (hypothesis formed on 2015-2026 only).
# H: overnight (close->open) growth of a leveraged long is lower when the underlying closes below its 200-day SMA.
import json, math, statistics as st, csv, sys
def loadf(files):
    out={}
    for f in files:
        for x in json.load(open(f))['data']['results']:
            for b in x['bars']:
                if b.get('interpolated') or not b.get('volume'): continue
                out.setdefault(x['symbol'],{})[b['begins_at'][:10]]=(float(b['open_price']),float(b['close_price']))
    return out
B=loadf(['d0a.json','d0b.json','d1.json','d2.json'])
earn=set(r['date'] for r in csv.DictReader(open('/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv')) if r['earn']=='1')
C=0.0009
def series(sym,lev,N):
    b=B[sym]; ds=sorted(b); out=[]
    for i in range(N-1,len(ds)-1):
        d=ds[i]; c=b[d][1]; o1=b[ds[i+1]][0]
        if sym=='NVDA' and d in earn: continue
        sma=sum(b[ds[j]][1] for j in range(i-N+1,i+1))/N
        out.append((d,lev*(o1/c-1),c<sma))
    return out
def stat(v):
    if len(v)<8: return "n=%4d"%len(v)+" "*40
    m=st.mean(v); s=st.stdev(v); g=st.mean([math.log(max(1e-9,1+x)) for x in v])
    return "n=%4d mean %+.3f sd %5.2f t %+5.2f g %+.3f"%(len(v),100*m,100*s,m/(s/math.sqrt(len(v))),100*g)
def strat(X,sz):
    v=[(sz*(r-C) if below else r-C) for d,r,below in X]
    eq=pk=1; dd=0
    for y in v:
        eq*=1+y; pk=max(pk,eq); dd=min(dd,eq/pk-1)
    return 100*st.mean([math.log(max(1e-9,1+y)) for y in v]),100*dd
P=[('2000','2004'),('2005','2009'),('2010','2014'),('2000','2014'),('2015','2026')]
print("first dates:",{s:min(B[s]) for s in B if s in('NVDA','QQQ','SPY','SMH')})
for sym,lev in (('NVDA',2),('QQQ',3),('SPY',3),('SMH',3)):
    print("=====",sym,"x",lev,"(synthetic leveraged overnight; 9bp/night cost when invested; NVDA earnings nights NOT removed before 2015)")
    X=series(sym,lev,200)
    big=[(d,round(100*r,1)) for d,r,_ in X if abs(r)>0.45]
    if big: print("  check extreme nights:",big[:8])
    for a,b in P:
        Y=[x for x in X if a<=x[0][:4]<=b]
        if len(Y)<50: continue
        gi,di=strat(Y,1.0); g0,d0=strat(Y,0.0); gh,dh=strat(Y,0.5)
        print(" %s-%s BELOW: %s | ABOVE: %s"%(a,b,stat([r-C for d,r,bl in Y if bl]),stat([r-C for d,r,bl in Y if not bl])))
        print("            strategy g/night: always %+.3f (dd %3.0f%%) | half below %+.3f (dd %3.0f%%) | flat below %+.3f (dd %3.0f%%)"%(gi,di,gh,dh,g0,d0))
    print("  SMA length sensitivity, flat-below g minus always-full g (pp/night): "+"  ".join("%d: "%N+"/".join("%+.3f"%(strat([x for x in series(sym,lev,N) if a<=x[0][:4]<=b],0.0)[0]-strat([x for x in series(sym,lev,N) if a<=x[0][:4]<=b],1.0)[0]) for a,b in (('2000','2014'),('2015','2026'))) for N in (100,150,200,250)))
