# T7: when NVDA is below its SMA200, is rotating into a trend-healthy substitute (SOXL if SMH>SMA200, TQQQ if QQQ>SMA200) better than a quarter-size NVDA-2x?
import json, math, statistics as st, glob, csv
B={}
for f in ['d0a.json','d0b.json','d1.json','d2.json']:
    for x in json.load(open(f))['data']['results']:
        for b in x['bars']:
            if b.get('interpolated') or not b.get('volume'): continue
            B.setdefault(x['symbol'],{})[b['begins_at'][:10]]=(float(b['open_price']),float(b['close_price']))
earn=set(r['date'] for r in csv.DictReader(open('/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv')) if r['earn']=='1')
def st200(sym):
    b=B[sym]; ds=sorted(b); o={}
    for i in range(199,len(ds)):
        o[ds[i]]=b[ds[i]][1]>sum(b[ds[j]][1] for j in range(i-199,i+1))/200
    return o
def on(sym):
    b=B[sym]; ds=sorted(b); return {ds[i]:b[ds[i+1]][0]/b[ds[i]][1]-1 for i in range(len(ds)-1)}
AN,AS,AQ=st200('NVDA'),st200('SMH'),st200('QQQ')
ON={s:on(s) for s in ('NVDA','SMH','QQQ','SOXL','TQQQ')}
days=[d for d in sorted(AN) if d>='2001-09-01' and d in AS and d in AQ and d in ON['NVDA'] and d in ON['SMH'] and d in ON['QQQ']]
def leg(name,d):
    if name=='N': return 0.0 if d in earn else 2*ON['NVDA'][d]-0.0009
    if name=='S': return (ON['SOXL'][d]-0.0005) if d in ON['SOXL'] else 3*ON['SMH'][d]-0.0011
    if name=='Q': return (ON['TQQQ'][d]-0.0005) if d in ON['TQQQ'] else 3*ON['QQQ'][d]-0.0011
def run(rule,ds):
    v=[rule(d) for d in ds]; eq=pk=1; dd=0
    for y in v: eq*=1+y; pk=max(pk,eq); dd=min(dd,eq/pk-1)
    return 100*st.mean([math.log(1+max(-0.95,y)) for y in v]),100*dd
R={
 'S0 always NVDA2x          ':lambda d: leg('N',d),
 'S1 NVDA2x | quarter below ':lambda d: leg('N',d) if AN[d] else 0.25*leg('N',d),
 'S1f NVDA2x | flat below   ':lambda d: leg('N',d) if AN[d] else 0.0,
 'S2 N | SOXL | TQQQ | qtr  ':lambda d: leg('N',d) if AN[d] else (leg('S',d) if AS[d] else (leg('Q',d) if AQ[d] else 0.25*leg('N',d))),
 'S3 N | SOXL | qtr         ':lambda d: leg('N',d) if AN[d] else (leg('S',d) if AS[d] else 0.25*leg('N',d)),
 'S4 N | TQQQ | qtr         ':lambda d: leg('N',d) if AN[d] else (leg('Q',d) if AQ[d] else 0.25*leg('N',d)),
}
def S(v):
    if len(v)<5: return "n=%d"%len(v)
    m=st.mean(v); s=st.stdev(v); return "n=%4d mean %+.3f sd %4.2f t %+5.2f g %+.3f"%(len(v),100*m,100*s,m/(s/math.sqrt(len(v))),100*st.mean([math.log(1+max(-0.95,y)) for y in v]))
P=[('2001','2004'),('2005','2009'),('2010','2014'),('2001','2014'),('2015','2018'),('2019','2022'),('2023','2026'),('2015','2026'),('2001','2026')]
for a,b in P:
    ds=[d for d in days if a<=d[:4]<=b]
    print("== %s-%s n %d | NVDA below SMA200 on %d nights; of those SMH above %d, QQQ above %d"%(a,b,len(ds),sum(not AN[d] for d in ds),sum((not AN[d]) and AS[d] for d in ds),sum((not AN[d]) and AQ[d] for d in ds)))
    x=[d for d in ds if not AN[d] and AS[d]]; y=[d for d in ds if not AN[d] and AQ[d]]
    print("   in state (NVDA below, SMH above): SOXL leg %s | NVDA2x leg %s"%(S([leg('S',d) for d in x]),S([leg('N',d) for d in x])))
    print("   in state (NVDA below, QQQ above): TQQQ leg %s | NVDA2x leg %s"%(S([leg('Q',d) for d in y]),S([leg('N',d) for d in y])))
    print("   "+" | ".join("%s g %+.3f dd %3.0f%%"%((k.split()[0],)+run(f,ds)) for k,f in R.items()))
print({k.strip():k for k in R})
print("today-ish states (last date):",days[-1],"NVDA above:",AN[days[-1]],"SMH above:",AS[days[-1]],"QQQ above:",AQ[days[-1]])
