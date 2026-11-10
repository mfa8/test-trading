import sys, csv
import numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge')
from edgelib import load
bars,pm=load()
for s in ('NVDA','QQQ','NVDL','TQQQ'):
    bad=[(d,v) for d,v in sorted(bars[s].items()) if not (v[2]-1e-9<=v[0]<=v[1]+1e-9 and v[2]-1e-9<=v[3]<=v[1]+1e-9)]
    print(s,'bars with open or close outside [low,high]:',len(bad),bad[:6])
R=[r for r in csv.DictReader(open('nights.csv')) if r['syn2x_on']!='']
ext=sorted(R,key=lambda r: float(r['syn2x_on']))
print('10 worst 2x NVDA nights:',[(r['date'],round(100*float(r['syn2x_on']),1),r['state'],'E' if r['earn']=='1' else '') for r in ext[:10]])
print('10 best  2x NVDA nights:',[(r['date'],round(100*float(r['syn2x_on']),1),r['state'],'E' if r['earn']=='1' else '') for r in ext[-10:]])
# calendar gaps > 5 days between consecutive NVDA bars (missing data?)
from datetime import date
ds=sorted(bars['NVDA']); g=[(a,b) for a,b in zip(ds,ds[1:]) if (date.fromisoformat(b)-date.fromisoformat(a)).days>5]
print('NVDA gaps >5 calendar days:',g)
ds=sorted(bars['QQQ']); g=[(a,b) for a,b in zip(ds,ds[1:]) if (date.fromisoformat(b)-date.fromisoformat(a)).days>5]
print('QQQ gaps >5 calendar days:',g)
# 3(f) headroom
v=[float(r['nvdl_on_adj']) for r in R if r['nvdl_on_adj']!='' and r['earn']!='1']; d=[r['date'] for r in R if r['nvdl_on_adj']!='' and r['earn']!='1']
w=np.array(v[-120:]); print('3(f) window now: %s..%s mean %+.3f%% sum %+.1f%%'%(d[-120],d[-1],100*w.mean(),100*w.sum()))
for k in (4,5,9):
    keep=np.array(v[-(120-k):]); print('   after %d more nights the window keeps a sum of %+.1f%% -> the next %d NVDL nights would have to total <= %.1f%% (arithmetic sum) for the mean to reach 0'%(k,100*keep.sum(),k,-100*keep.sum()))
# history of the 3(f) signal on synthetic 2x ex-earnings 2015+: how often <=0
u=np.array([float(r['syn2x_on']) for r in R if r['earn']!='1' and r['date']>='2015']); cs=np.concatenate([[0],np.cumsum(u)]); wm=(cs[120:]-cs[:-120])/120
print('synthetic 2x ex-earnings 2015+: share of 120-night windows with mean <= 0: %.1f%%; current %+.3f%%'%(100*np.mean(wm<=0),100*wm[-1]))
