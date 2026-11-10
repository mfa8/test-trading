import csv, math
import numpy as np
R=[r for r in csv.DictReader(open('/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge/nights.csv')) if r['syn2x_on']!='']
d=[r['date'] for r in R]; u=np.array([float(r['syn2x_on']) for r in R])
nl=[(r['date'],float(r['nvdl_on_adj'])) for r in R if r['nvdl_on_adj']!='']
# the 62 sessions to 2026-09-08 -> nights with exit open on or before 2026-09-08
i=max(k for k,r in enumerate(R) if r['next']<='2026-09-08')
w=62
cs=np.concatenate([[0],np.cumsum(u)]); wm=(cs[w:]-cs[:-w])/w; ends=d[w-1:]
k=ends.index(d[i]); cur=wm[k]
print('2x NVDA synthetic: 62-night mean ending night %s->%s: %+.3f%%; percentile among all 62-night windows since 2000: %.1f; among windows ending 2015+: %.1f'%(d[i],R[i]['next'],100*cur,100*np.mean(wm<=cur),100*np.mean(wm[np.array([e>='2015' for e in ends])]<=cur)))
v=np.array([x for _,x in nl]); dd=[a for a,_ in nl]
j=max(k for k,a in enumerate(dd) if a<=d[i])
print('NVDL real bars: 62-night mean ending %s: %+.3f%% (rules quoted +0.61%%)'%(dd[j],100*v[j-61:j+1].mean()))
# what followed the best 62-night windows in history: next-44-night mean after windows at or above this level (non-overlapping picks)
hi=np.where(wm>=cur)[0]; nxt=[]
last=-999
for q in hi:
    e=q+w-1  # index of last night in window
    if e-last<62: continue
    if e+44<len(u): nxt.append(u[e+1:e+45].mean()); last=e
print('after earlier 62-night windows at or above that level (non-overlapping, n=%d): mean of the next 44 nights = %+.3f%% per night (sd across episodes %.3f); all-history mean %+.3f%%'%(len(nxt),100*np.mean(nxt),100*np.std(nxt,ddof=1),100*u.mean()))
# live 44 nights market: 2x NVDA and NVDL
a=d.index('2026-09-09'); print('2x NVDA synthetic over the 44 live nights (entry 9/09..11/09): mean %+.3f%% sum %+.1f%% t %.2f'%(100*u[a:].mean(),100*u[a:].sum(),u[a:].mean()/(u[a:].std(ddof=1)/math.sqrt(len(u[a:])))),'n',len(u[a:]))
