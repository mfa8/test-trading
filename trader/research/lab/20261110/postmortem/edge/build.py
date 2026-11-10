"""Build the nightly table used by every later script.
Night t = close of session t -> open of session t+1, labelled by entry date t.
"""
import sys, json, math, csv
sys.path.insert(0,'/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge')
from edgelib import load, stats, BASE
bars,pm=load()
EARN = set("""2015-02-11 2015-05-07 2015-08-06 2015-11-05
2016-02-17 2016-05-12 2016-08-11 2016-11-10
2017-02-09 2017-05-09 2017-08-10 2017-11-09
2018-02-08 2018-05-10 2018-08-16 2018-11-15
2019-02-14 2019-05-16 2019-08-15 2019-11-14
2020-02-13 2020-05-21 2020-08-19 2020-11-18
2021-02-24 2021-05-26 2021-08-18 2021-11-17
2022-02-16 2022-05-25 2022-08-24 2022-11-16
2023-02-22 2023-05-24 2023-08-23 2023-11-21
2024-02-21 2024-05-22 2024-08-28 2024-11-20
2025-02-26 2025-05-28 2025-08-27 2025-11-19
2026-02-25 2026-05-20 2026-08-26""".split())   # copied from trader/research/edge_decay/s01_prep.py (read-only source)
COST=0.0009
nv=bars['NVDA']; qq=bars['QQQ']; nl=bars['NVDL']; tq=bars['TQQQ']
dates=sorted(nv)
qd=sorted(qq)
qidx={d:i for i,d in enumerate(qd)}
# trend state at the close of t: QQQ close_t vs mean of previous 199 closes
def state(d):
    if d not in qidx: return None
    i=qidx[d]
    if i<199: return None
    L=sum(qq[x][3] for x in qd[i-199:i])/199.0
    return ('UP' if qq[d][3]>=L else 'DOWN', L, qq[d][3]/L-1)
rows=[]
for i,t in enumerate(dates):
    o,h,l,c,v=nv[t]
    row=dict(date=t, nvda_day=c/o-1)
    if i+1<len(dates):
        t1=dates[i+1]
        row['next']=t1
        row['nvda_on']=nv[t1][0]/c-1
        row['syn2x_on']=2*row['nvda_on']-COST
        if t in nl and t1 in nl:
            row['nvdl_on']=nl[t1][0]/nl[t][3]-1
        if t in tq and t1 in tq:
            row['tqqq_on']=tq[t1][0]/tq[t][3]-1
        if t in qq and t1 in qq:
            row['qqq_on']=qq[t1][0]/qq[t][3]-1
    if t in nl: row['nvdl_day']=nl[t][3]/nl[t][0]-1
    if t in tq: row['tqqq_day']=tq[t][3]/tq[t][0]-1
    s=state(t)
    if s: row['state'],row['line'],row['dist']=s[0],s[1],s[2]
    row['earn']=int(t in EARN)
    rows.append(row)
# NVDL distribution flag: residual vs 2x NVDA
flag=[]
for r in rows:
    if 'nvdl_on' in r:
        r['nvdl_resid']=r['nvdl_on']-2*r['nvda_on']
        if abs(r['nvdl_resid'])>0.008: flag.append((r['date'],round(100*r['nvdl_on'],2),round(200*r['nvda_on'],2),round(100*r['nvdl_resid'],2)))
print('NVDL nights with |residual vs 2xNVDA| > 0.8%:',flag)
# add back the one known NVDL distribution (ex 2023-12-27, 0.561749 per current share): research/NVDL-EXDATE-20261027.md
for r in rows:
    if 'nvdl_on' in r:
        r['nvdl_on_adj']=r['nvdl_on']
        if r['date']=='2023-12-26':
            c=nl['2023-12-26'][3]; o1=nl['2023-12-27'][0]
            r['nvdl_on_adj']=(o1+0.561749)/c-1
            print('NVDL 2023-12-26 night raw %.3f%% adj %.3f%% 2xNVDA %.3f%% close %.4f'%(100*r['nvdl_on'],100*r['nvdl_on_adj'],200*r['nvda_on'],c))
cols=['date','next','nvda_on','syn2x_on','nvda_day','nvdl_on','nvdl_on_adj','nvdl_resid','nvdl_day','tqqq_on','tqqq_day','qqq_on','state','line','dist','earn']
with open('nights.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore'); w.writeheader()
    for r in rows: w.writerow(r)
print('rows',len(rows),rows[0]['date'],rows[-1]['date'])
print('nights with syn2x',sum(1 for r in rows if 'syn2x_on' in r),'with state',sum(1 for r in rows if 'state' in r and 'syn2x_on' in r))
print('earnings nights found in data',sum(1 for r in rows if r['earn']),'of',len(EARN),'missing',sorted(EARN-set(dates)))
for r in rows[-6:]: print({k:(round(v,5) if isinstance(v,float) else v) for k,v in r.items()})
# residual stats NVDL - 2x NVDA by year, ex the flagged distribution night
import collections
by=collections.defaultdict(list)
for r in rows:
    if 'nvdl_resid' in r and r['date']!='2023-12-26': by[r['date'][:4]].append(r['nvdl_resid'])
for y in sorted(by):
    v=by[y]; m=sum(v)/len(v); print('NVDL-2xNVDA overnight residual',y,'n',len(v),'mean bp %.2f'%(1e4*m))
