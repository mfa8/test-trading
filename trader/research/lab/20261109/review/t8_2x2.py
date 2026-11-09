# T8: which trend state matters - the stock's own SMA200, the market's (QQQ) SMA200, or both?
# Synthetic 2x overnight, 9bp cost when invested, loss capped -95%. Rules: size 0.25 in the defensive state, else 1.
import json, math, statistics as st, glob, sys
B={}
for f in ['d0a.json','d0b.json','d1.json','d2.json']+sorted(glob.glob('x*.json')):
    for x in json.load(open(f))['data']['results']:
        for b in x['bars']:
            if b.get('interpolated') or not b.get('volume'): continue
            B.setdefault(x['symbol'],{})[b['begins_at'][:10]]=(float(b['open_price']),float(b['close_price']))
C=0.0009; N=200
def state(sym):
    b=B[sym]; ds=sorted(b); o={}; lastbreak=-10**9
    for i in range(len(ds)-1):
        c=b[ds[i]][1]; r=b[ds[i+1]][0]/c-1
        if abs(r)>0.45 or abs(b[ds[i]][1]/b[ds[i]][0]-1)>0.6: lastbreak=i; continue
        if i<N-1 or i-lastbreak<N: continue
        sma=sum(b[ds[j]][1] for j in range(i-N+1,i+1))/N
        o[ds[i]]=(max(-0.95,2*r), c<sma, b[ds[i+1]][1]/b[ds[i+1]][0]-1)   # overnight 2x, below?, NEXT day's intraday (unlevered)
    return o
Q=state('QQQ')
def g(v): return 100*st.mean([math.log(1+max(-0.95,y)) for y in v]) if v else float('nan')
def dd(v):
    eq=pk=1; m=0
    for y in v: eq*=1+y; pk=max(pk,eq); m=min(m,eq/pk-1)
    return 100*m
def cell(v): 
    if len(v)<5: return "n=%4d"%len(v)
    return "n=%4d mean %+.3f sd %4.2f g %+.3f"%(len(v),100*st.mean(v),100*st.stdev(v),g(v))
RULES={'full':lambda ob,qb:1,'own':lambda ob,qb:0.25 if ob else 1,'mkt':lambda ob,qb:0.25 if qb else 1,'both':lambda ob,qb:0.25 if (ob and qb) else 1,'either':lambda ob,qb:0.25 if (ob or qb) else 1}
NAMES=['NVDA','AMD','INTC','MU','AAPL','MSFT','AMZN','QCOM','TXN','AMAT','ORCL']
for a,b_ in [('2000','2014'),('2015','2026'),('2000','2026')]:
    print("=== %s-%s"%(a,b_))
    wins={k:0 for k in RULES}; pooled={}
    for s in NAMES:
        X=state(s); ds=[d for d in sorted(X) if a<=d[:4]<=b_ and d in Q]
        cells={}
        for d in ds:
            r,ob,_=X[d]; qb=Q[d][1]; cells.setdefault((ob,qb),[]).append(r); pooled.setdefault((ob,qb),[]).append(r)
        res={k:[f(X[d][1],Q[d][1])*(X[d][0]-C) for d in ds] for k,f in RULES.items()}
        for k in RULES:
            if g(res[k])>g(res['full'])+1e-9: wins[k]+=1
        line="  %-5s "%s+" ".join("%s g %+.3f dd %3.0f%%"%(k,g(res[k]),dd(res[k])) for k in RULES)
        print(line)
        if s=='NVDA':
            for key,lab in [((False,False),'own UP , mkt UP '),((False,True),'own UP , mkt DN '),((True,False),'own DN , mkt UP '),((True,True),'own DN , mkt DN ')]:
                print("        NVDA2x overnight | %s: %s"%(lab,cell(cells.get(key,[]))))
    print("  rules beating full (of 11):",{k:v for k,v in wins.items() if k!='full'})
    for key,lab in [((False,False),'own UP , mkt UP '),((False,True),'own UP , mkt DN '),((True,False),'own DN , mkt UP '),((True,True),'own DN , mkt DN ')]:
        print("  pooled 11 names 2x overnight | %s: %s"%(lab,cell(pooled.get(key,[]))))
# T9: next-day INTRADAY (open->close) at 2x by trend state (NVDA and pooled), cost 0 (holding through saves trades)
print("=== T9 intraday 2x by state at the prior close")
for a,b_ in [('2000','2014'),('2015','2022'),('2023','2025'),('2026','2026'),('2000','2026')]:
    for grp,names in [('NVDA',['NVDA']),('pool11',NAMES)]:
        cells={}
        for s in names:
            X=state(s)
            for d in X:
                if a<=d[:4]<=b_ and d in Q: cells.setdefault((X[d][1],Q[d][1]),[]).append(max(-0.95,2*X[d][2]))
        print("  %s-%s %-6s"%(a,b_,grp)+" | ".join("%s %s"%(lab,cell(cells.get(key,[]))) for key,lab in [((False,False),'UP/UP'),((True,True),'DN/DN')]))
# current states
for s in ['NVDA','QQQ','SMH']:
    b=B[s]; ds=sorted(b); c=b[ds[-1]][1]; sma=sum(b[d][1] for d in ds[-200:])/200
    print(s,ds[-1],"close %.2f SMA200 %.2f  %+.1f%%"%(c,sma,100*(c/sma-1)))
