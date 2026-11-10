# independent second pass: different code path (no shared helpers), numpy bootstrap
import json, csv
import numpy as np
P='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/'
raw=json.load(open(P+'day_0908_1110.json'))['data']['results']
px={}
for r in raw:
    for b in r['bars']:
        if b.get('interpolated') or not b['volume']: continue
        px[(r['symbol'],b['begins_at'][:10])]=(float(b['open_price']),float(b['close_price']))
dates=sorted({d for (s,d) in px if s=='NVDL'})
T=dict(ours=0,model=0,entry=0,exit=0)
byn={}
for row in csv.reader(open(P+'trades.csv')):
    if len(row)<17 or not row[0].startswith('T3X-N'): continue
    n=int(row[0].split('N')[1]); s=row[2]; d0=row[1]; d1=min(d for d in dates if d>d0)
    ef=float(row[8]); q=float(row[9]); xf=float(row[13]); C=px[(s,d0)][1]; O=px[(s,d1)][0]
    inv=ef*q
    v=dict(ours=(xf-ef)*q, model=inv*(O/C-1), entry=inv*(C/ef-1), exit=inv*(xf/O-1))
    for k in T: T[k]+=v[k]
    a=byn.setdefault(n,dict(inv=0,ours=0,model=0,entry=0,exit=0)); a['inv']+=inv
    for k in v: a[k]+=v[k]
print({k:round(v,3) for k,v in T.items()},'cross',round(T['ours']-T['model']-T['entry']-T['exit'],3),'nights',len(byn))
rng=np.random.default_rng(12345)
for k in ('exit','entry','model','ours'):
    x=np.array([100*byn[n][k]/byn[n]['inv'] for n in sorted(byn)])
    bs=rng.choice(x,size=(200000,len(x)),replace=True).mean(axis=1)
    x2=x[24:]; bs2=rng.choice(x2,size=(200000,len(x2)),replace=True).mean(axis=1)
    x1=x[:24]; bs1=rng.choice(x1,size=(200000,len(x1)),replace=True).mean(axis=1)
    print(f"{k:6} all: mean {x.mean():+.3f} 90% [{np.percentile(bs,5):+.3f},{np.percentile(bs,95):+.3f}] neg {int((x<0).sum())}/44 | era1 {x1.mean():+.3f} [{np.percentile(bs1,5):+.3f},{np.percentile(bs1,95):+.3f}] neg {int((x1<0).sum())}/24 | era2 {x2.mean():+.3f} [{np.percentile(bs2,5):+.3f},{np.percentile(bs2,95):+.3f}] neg {int((x2<0).sum())}/20")
