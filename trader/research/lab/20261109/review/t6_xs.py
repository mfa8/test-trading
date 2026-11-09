# T6: cross-sectional robustness of the trend state (pre-registered sample: NVDA + 10 large tech/semis listed before 2000)
# Synthetic leveraged overnight (close->next open), cost 9bp/night when invested. State: close < SMA(N) of closes (known at the close).
import json, math, statistics as st, glob, sys
B={}
for f in ['d0a.json','d0b.json','d1.json','d2.json']+sorted(glob.glob('x*.json')):
    for x in json.load(open(f))['data']['results']:
        for b in x['bars']:
            if b.get('interpolated') or not b.get('volume'): continue
            B.setdefault(x['symbol'],{})[b['begins_at'][:10]]=(float(b['open_price']),float(b['close_price']))
C=0.0009
def series(sym,lev,N=200):
    b=B[sym]; ds=sorted(b); out=[]; lastbreak=-10**9; nbreak=0
    for i in range(len(ds)-1):
        c=b[ds[i]][1]; o1=b[ds[i+1]][0]; r=o1/c-1
        cc=b[ds[i+1]][1]/c-1
        if abs(r)>0.45 or abs(b[ds[i]][1]/b[ds[i]][0]-1)>0.6:   # data break (bad split adjustment), not a real gap
            lastbreak=i; nbreak+=1; continue
        if i<N-1 or i-lastbreak<N: continue
        sma=sum(b[ds[j]][1] for j in range(i-N+1,i+1))/N
        out.append((ds[i],max(-0.95,lev*r),c<sma))
    return out,nbreak
def g(v): return 100*st.mean([math.log(1+y) for y in v]) if v else float('nan')
def strat(X,sz): return [(sz*(r-C) if bl else r-C) for d,r,bl in X]
def dd(v):
    eq=pk=1; m=0
    for y in v: eq*=1+y; pk=max(pk,eq); m=min(m,eq/pk-1)
    return 100*m
SY=['NVDA','AMD','INTC','MU','AAPL','MSFT','AMZN','QCOM','TXN','AMAT','ORCL','QQQ','SMH','SPY']
LEV=float(sys.argv[1]) if len(sys.argv)>1 else 2.0
print("leverage",LEV,"| g = mean log growth, % per night | BELOW/ABOVE = stats of invested nights in each state")
for a,b_ in (('2000','2014'),('2015','2026'),('2000','2026')):
    print("== %s-%s"%(a,b_)); win0=winq=tot=0; pool_in=[]; pool_out=[]
    for s in SY:
        X,nb=series(s,LEV); Y=[x for x in X if a<=x[0][:4]<=b_]
        if len(Y)<300: continue
        IN=[r-C for d,r,bl in Y if bl]; OUT=[r-C for d,r,bl in Y if not bl]
        gf=g(strat(Y,1.0)); g0=g(strat(Y,0.0)); gq=g(strat(Y,0.25)); gh=g(strat(Y,0.5))
        if s not in('QQQ','SMH','SPY'):
            tot+=1; win0+=g0>gf; winq+=gq>gf; pool_in+=IN; pool_out+=OUT
        print(" %-4s n %4d below %4.0f%% | BELOW mean %+.3f sd %4.2f g %+.3f | ABOVE mean %+.3f sd %4.2f g %+.3f | g: full %+.3f  half %+.3f  quarter %+.3f  flat %+.3f | dd full %4.0f%% quarter %4.0f%% flat %4.0f%%%s"%(s,len(Y),100*len(IN)/len(Y),100*st.mean(IN),100*st.stdev(IN),g(IN),100*st.mean(OUT),100*st.stdev(OUT),g(OUT),gf,gh,gq,g0,dd(strat(Y,1.0)),dd(strat(Y,0.25)),dd(strat(Y,0.0)),"  [breaks dropped %d]"%nb if nb else ""))
    mi,mo=st.mean(pool_in),st.mean(pool_out); se=math.sqrt(st.variance(pool_in)/len(pool_in)+st.variance(pool_out)/len(pool_out))
    print("  single stocks: flat beats full in %d/%d names; quarter beats full in %d/%d | pooled BELOW mean %+.3f (n %d, g %+.3f) vs ABOVE %+.3f (n %d, g %+.3f); diff t %.2f (naive, nights are cross-correlated)"%(win0,tot,winq,tot,100*mi,len(pool_in),g(pool_in),100*mo,len(pool_out),g(pool_out),(mi-mo)/se))
