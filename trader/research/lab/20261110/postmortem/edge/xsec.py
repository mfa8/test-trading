"""Unselected prior: the same 2x close->open series (net 9bp) for ten other large tech names, 2015..2026-11-06 and 2000-2014.
Earnings nights are included for every name (no flags for the others). Prices are not dividend-adjusted (small downward bias for payers)."""
import json, math
import numpy as np
B='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/rev/'
bars={}
for f in ('x1','x2','x3','x4','x5','x6','d0a','d0b','d1','d2'):
    for x in json.load(open(B+f+'.json'))['data']['results']:
        for b in x['bars']:
            if b.get('interpolated') or not b.get('volume'): continue
            d=b['begins_at'][:10]
            if d>'2026-11-06': continue
            if x['symbol']=='NVDA' and d<='2000-10-27': continue
            bars.setdefault(x['symbol'],{})[d]=(float(b['open_price']),float(b['close_price']))
names=['NVDA','AMD','INTC','MU','AAPL','MSFT','AMZN','QCOM','TXN','AMAT','ORCL','QQQ','SPY']
def ser(s,lo,hi):
    ds=sorted(bars[s]); out=[]
    for a,b in zip(ds,ds[1:]):
        if lo<=a[:4]<=hi: out.append(2*(bars[s][b][0]/bars[s][a][1]-1)-0.0009)
    return np.array(out)
rows=[]
print('%-5s | 2015-2026: n mean%% sd%% t log-g%% | 2021-2026: mean%% t | last 250: mean%% t | 2000-2014: mean%% t'%'name')
for s in names:
    a=ser(s,'2015','2026'); b=ser(s,'2021','2026'); c=a[-250:]; e=ser(s,'2000','2014')
    f=lambda v:(100*v.mean(),v.mean()/(v.std(ddof=1)/math.sqrt(len(v))))
    print('%-5s | %4d %+.3f %.2f %+.2f %+.3f | %+.3f %+.2f | %+.3f %+.2f | %+.3f %+.2f'%(s,len(a),100*a.mean(),100*a.std(ddof=1),f(a)[1],100*np.mean(np.log1p(a)),f(b)[0],f(b)[1],f(c)[0],f(c)[1],f(e)[0],f(e)[1]))
    rows.append((s,a.mean(),b.mean(),c.mean(),e.mean()))
oth=[r for r in rows if r[0] not in ('NVDA','QQQ','SPY')]
print('ten other names, equal-weight mean of the 2x net-9bp overnight mean: 2015-26 %+.3f%% (median %+.3f, min %+.3f, max %+.3f); 2021-26 %+.3f%%; last 250 nights %+.3f%%; 2000-14 %+.3f%%'%(
    100*np.mean([r[1] for r in oth]),100*np.median([r[1] for r in oth]),100*min(r[1] for r in oth),100*max(r[1] for r in oth),100*np.mean([r[2] for r in oth]),100*np.mean([r[3] for r in oth]),100*np.mean([r[4] for r in oth])))
print('NVDA rank among the 11 names by 2015-26 mean:',1+sum(1 for r in oth if r[1]>rows[0][1]),' by 2000-14 mean:',1+sum(1 for r in oth if r[4]>rows[0][4]))
