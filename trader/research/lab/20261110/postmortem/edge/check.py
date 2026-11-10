import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge')
from edgelib import *
from edgelib import _read
bars,pm=load()
for s in sorted(bars):
    ds=sorted(bars[s]); print(s,len(ds),ds[0],ds[-1])
# NVDA 10x check
r=_read('rev/d0a.json')['NVDA']
for d in sorted(r):
    if '2000-10-20'<=d<='2000-11-03': print(d,r[d])
# compare overlap rev d2 vs pm for Sept-Nov
d2=_read('rev/d2.json')
for s in ('NVDA','NVDL','QQQ','TQQQ'):
    mx=0;cnt=0
    for d in sorted(pm[s]):
        if d in d2[s]:
            a=d2[s][d]; b=pm[s][d]
            diff=max(abs(a[0]/b[0]-1),abs(a[3]/b[3]-1))
            if diff>1e-4: print('DIFF',s,d,a,b)
            cnt+=1
    print(s,'overlap',cnt)
# which pm dates missing
import json
for x in json.load(open(BASE+'pm/day_0908_1110.json'))['data']['results']:
    for b in x['bars']:
        if b.get('interpolated') or not b.get('volume'): print('pm bad',x['symbol'],b['begins_at'][:10],b)
for x in json.load(open(BASE+'rev/d2.json'))['data']['results']:
    if x['symbol'] in('NVDA','QQQ','TQQQ'):
        for b in x['bars']:
            if b.get('interpolated') or not b.get('volume'): print('d2 bad',x['symbol'],b['begins_at'][:10],b)
# date alignment between NVDA and QQQ
a=set(bars['NVDA']); q=set(bars['QQQ'])
print('NVDA not QQQ',sorted(a-q)[:20],len(a-q)); print('QQQ not NVDA (after 2000-10-30)',[d for d in sorted(q-a) if d>'2000-10-27'][:20])
nl=sorted(bars['NVDL']); print('NVDL first',nl[:5], 'count from 2022-12-13', sum(1 for d in nl if d>='2022-12-13'))
print('NVDA dates not in NVDL since 2022-12-13',[d for d in sorted(a) if d>='2022-12-13' and d not in bars['NVDL']])
print('last bars NVDA',[ (d,bars['NVDA'][d]) for d in sorted(a)[-4:]])
print('last bars QQQ',[ (d,bars['QQQ'][d]) for d in sorted(q)[-4:]])
