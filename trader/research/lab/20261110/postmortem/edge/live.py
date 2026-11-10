import csv, json, math, collections
import numpy as np
B='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/'
bars={}
for x in json.load(open(B+'pm/day_0908_1110.json'))['data']['results']:
    for b in x['bars']:
        if b.get('interpolated') or not b.get('volume'): continue
        bars.setdefault(x['symbol'],{})[b['begins_at'][:10]]=(float(b['open_price']),float(b['close_price']))
legs=[]
for row in csv.reader(open(B+'pm/trades.csv')):
    if not row or not row[0].startswith('T3X-N'): continue
    nid=row[0]; d=row[1]; sym=row[2]; pin=float(row[8]); q=float(row[9]); pout=float(row[13]) if row[13] else None
    legs.append(dict(n=int(nid[5:]),d=d,sym=sym,pin=pin,q=q,pout=pout))
print('legs',len(legs),'nights',len(set(l['n'] for l in legs)), 'open legs',[l for l in legs if l['pout'] is None])
tot=co=ent=ex=0; per=collections.defaultdict(lambda: dict(pnl=0,co=0,ent=0,ex=0,inv=0,d=None))
miss=[]
for l in legs:
    if l['pout'] is None: continue
    ds=sorted(bars[l['sym']]); 
    if l['d'] not in bars[l['sym']]: miss.append(l); continue
    i=ds.index(l['d']); d1=ds[i+1]
    C=bars[l['sym']][l['d']][1]; O=bars[l['sym']][d1][0]
    q=l['q']; p=per[l['n']]; p['d']=l['d']
    p['pnl']+=q*(l['pout']-l['pin']); p['co']+=q*(O-C); p['ent']+=q*(C-l['pin']); p['ex']+=q*(l['pout']-O); p['inv']+=q*l['pin']
print('missing bars',miss)
ns=sorted(per)
P=np.array([per[n]['pnl'] for n in ns]); CO=np.array([per[n]['co'] for n in ns]); EN=np.array([per[n]['ent'] for n in ns]); EX=np.array([per[n]['ex'] for n in ns]); INV=np.array([per[n]['inv'] for n in ns])
print('nights %d: total pnl %.2f = close->open %.2f + entry timing %.2f + exit timing %.2f'%(len(ns),P.sum(),CO.sum(),EN.sum(),EX.sum()))
def t(v): return v.mean()/(v.std(ddof=1)/math.sqrt(len(v)))
for lab,sel in (('all 44 nights',np.ones(len(ns),bool)),('nights 1-24 (mixed basket)',np.array([n<=24 for n in ns])),('nights 25-44 (NVDA 2x only)',np.array([n>=25 for n in ns]))):
    r=P[sel]/INV[sel]; rc=CO[sel]/INV[sel]; re=EN[sel]/INV[sel]; rx=EX[sel]/INV[sel]
    print('%-28s n %2d | per-night %% of invested: total %+.3f (t %.2f) | close->open %+.3f (t %.2f) | entry vs close %+.3f (t %.2f) | exit vs open %+.3f (t %.2f) | timing sum %+.3f (t %.2f) | $: %.2f = %.2f %+.2f %+.2f | avg invested %.1f'%(
        lab,sel.sum(),100*r.mean(),t(r),100*rc.mean(),t(rc),100*re.mean(),t(re),100*rx.mean(),t(rx),100*(re+rx).mean(),t(re+rx),P[sel].sum(),CO[sel].sum(),EN[sel].sum(),EX[sel].sum(),INV[sel].mean()))
print('worst nights:',sorted([(round(per[n]['pnl'],2),n,per[n]['d']) for n in ns])[:6])
print('best nights:',sorted([(round(per[n]['pnl'],2),n,per[n]['d']) for n in ns])[-5:])
