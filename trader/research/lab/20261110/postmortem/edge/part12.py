import csv, math, sys
import numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge')
R=list(csv.DictReader(open('/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge/nights.csv')))
def f(x): return float(x) if x not in ('',None) else None
for r in R:
    for k in ('nvda_on','syn2x_on','nvda_day','nvdl_on','nvdl_on_adj','nvdl_day','tqqq_on','tqqq_day','qqq_on','dist'):
        r[k]=f(r[k])
    r['earn']=int(r['earn'])
def S(v):
    v=np.asarray(v,float); n=len(v)
    if n<2: return (n,float('nan'),float('nan'),float('nan'),float('nan'),float('nan'))
    m=v.mean(); s=v.std(ddof=1)
    return (n,100*m,100*s,m/(s/math.sqrt(n)),100*np.mean(np.log1p(v)),100*np.mean(v>0))
def line(lab,v):
    n,m,s,t,g,w=S(v); print('%-26s n %5d  mean %+7.3f%%  sd %6.3f%%  t %+5.2f  log-growth %+7.3f%%  win %4.1f%%'%(lab,n,m,s,t,g,w))
def series(key,exearn=False,start=None,end=None):
    out=[]
    for r in R:
        if r[key] is None: continue
        if start and r['date']<start: continue
        if end and r['date']>end: continue
        if exearn and r['earn']: continue
        out.append((r['date'],r[key]))
    return out
def block(title,key,mult=1.0,cost=0.0,start_year=2015,exearn=False,daykey=False):
    print('\n=== %s ==='%title)
    ser=[(d,mult*x-cost) for d,x in series(key,exearn)]
    vals=np.array([x for d,x in ser]); ds=[d for d,x in ser]
    print('sample',ds[0],'->',ds[-1],'n',len(ds))
    line('ALL',vals)
    for a,b,lab in (('2000','2014','2000-2014'),('2015','2026','2015-2026'),('2015','2020','2015-2020'),('2021','2026','2021-2026')):
        v=[x for d,x in ser if a<=d[:4]<=b]
        if len(v)>1: line(lab,v)
    for y in range(max(start_year,int(ds[0][:4])),2027):
        v=[x for d,x in ser if d[:4]==str(y)]
        if len(v)>1: line(str(y),v)
    for w in (20,44,60,120,250):
        line('last %d (to %s)'%(w,ds[-1]),vals[-w:])
    # percentile of latest window vs all windows
    for w in (60,120,250):
        cs=np.concatenate([[0],np.cumsum(vals)])
        wm=(cs[w:]-cs[:-w])/w   # window ending at index i (i=w-1..)
        ends=ds[w-1:]
        latest=wm[-1]
        pct_all=100*np.mean(wm<=latest)
        m15=np.array([e>='2015-01-01' for e in ends])
        pct15=100*np.mean(wm[m15]<=latest) if m15.any() else float('nan')
        # non-overlapping windows counted back from the latest
        no=wm[::-1][::w][::-1]
        pct_no=100*np.mean(no<=latest)
        print('  window %3d: latest mean %+.3f%%; percentile among all %d overlapping windows %.1f; among windows ending 2015+ %.1f; among %d non-overlapping windows (anchored at latest) %.1f [rank %d of %d from bottom]; min %+.3f max %+.3f median %+.3f'%(
            w,100*latest,len(wm),pct_all,pct15,len(no),pct_no,int(np.sum(no<=latest)),len(no),100*wm.min(),100*wm.max(),100*np.median(wm)))
        # share of windows with mean<=0
        print('      share of %d-night windows with mean <= 0: all %.1f%%, 2015+ %.1f%%'%(w,100*np.mean(wm<=0),100*np.mean(wm[m15]<=0)))
    return ser
print('#### PART 1: synthetic 2x NVDA, 2*(open_t+1/close_t - 1) - 0.0009 ####')
s_all=block('2x NVDA overnight, all nights','nvda_on',2.0,0.0009)
s_ex=block('2x NVDA overnight, EX earnings nights (flags exist 2015+ only)','nvda_on',2.0,0.0009,exearn=True)
print('\nEarnings nights only, 2x NVDA overnight net 9bp:')
ev=[(r['date'],2*r['nvda_on']-0.0009) for r in R if r['earn'] and r['nvda_on'] is not None]
line('earnings nights 2015-26',[x for d,x in ev])
for y in (2023,2024,2025,2026):
    print('   ',y,[ (d,round(100*x,1)) for d,x in ev if d[:4]==str(y)])
s_day=block('2x NVDA DAY (2*(close/open-1), no cost) - the part the account avoids','nvda_day',2.0,0.0)
# drift 2023-2026
print('\n=== Drift of the overnight mean 2023..2026 (2x NVDA net 9bp) ===')
for lab,ser in (('all nights',s_all),('ex earnings',s_ex)):
    sub=[(d,x) for d,x in ser if '2023'<=d[:4]<='2026']
    y=np.array([x for d,x in sub]); t=np.arange(len(y))/252.0
    A=np.vstack([np.ones_like(t),t]).T
    beta,res,rk,sv=np.linalg.lstsq(A,y,rcond=None)
    resid=y-A@beta; s2=resid@resid/(len(y)-2); cov=s2*np.linalg.inv(A.T@A)
    print('%s: n %d slope %+.4f%% per night per year, t %.2f; intercept %+.3f%%'%(lab,len(y),100*beta[1],beta[1]/math.sqrt(cov[1,1]),100*beta[0]))
    ym={yy:np.array([x for d,x in sub if d[:4]==str(yy)]) for yy in (2023,2024,2025,2026)}
    for a,b in ((2023,2026),(2024,2026),(2025,2026),(2023,2025)):
        va,vb=ym[a],ym[b]; d=vb.mean()-va.mean(); se=math.sqrt(va.var(ddof=1)/len(va)+vb.var(ddof=1)/len(vb))
        print('   mean %d - mean %d = %+.3f%% (se %.3f, t %.2f)'%(b,a,100*d,100*se,d/se))
    # halves of each year
    for yy in (2023,2024,2025,2026):
        h1=[x for d,x in sub if d[:4]==str(yy) and d[5:7]<='06']; h2=[x for d,x in sub if d[:4]==str(yy) and d[5:7]>'06']
        print('   %d H1 mean %+.3f%% (n %d)  H2 mean %+.3f%% (n %d)'%(yy,100*np.mean(h1),len(h1),100*np.mean(h2),len(h2)))
# 2026 by month
print('\n2026 by month, 2x NVDA overnight net 9bp (all nights) and 2x day:')
for m in range(1,12):
    k='2026-%02d'%m
    v=[x for d,x in s_all if d[:7]==k]; dv=[x for d,x in s_day if d[:7]==k]
    if v: print('  %s n %2d overnight mean %+.3f%% sum %+.1f%% | day mean %+.3f%% sum %+.1f%%'%(k,len(v),100*np.mean(v),100*np.sum(v),100*np.mean(dv),100*np.sum(dv)))
print('\n#### PART 2: real NVDL and TQQQ bars ####')
block('NVDL overnight (real bars, open_t+1/close_t - 1, gross; 2023-12-26 distribution added back)','nvdl_on_adj',1.0,0.0,start_year=2022)
block('NVDL overnight EX NVDA earnings nights','nvdl_on_adj',1.0,0.0,start_year=2022,exearn=True)
block('NVDL DAY (close/open - 1)','nvdl_day',1.0,0.0,start_year=2022)
block('TQQQ overnight (real bars, gross)','tqqq_on',1.0,0.0)
block('TQQQ DAY (close/open - 1)','tqqq_day',1.0,0.0)
# NVDL leverage by year
print('\nNVDL overnight beta to NVDA overnight by year (OLS through origin):')
for y in (2022,2023,2024,2025,2026):
    a=np.array([r['nvda_on'] for r in R if r['nvdl_on'] is not None and r['date'][:4]==str(y) and r['date']!='2023-12-26'])
    b=np.array([r['nvdl_on'] for r in R if r['nvdl_on'] is not None and r['date'][:4]==str(y) and r['date']!='2023-12-26'])
    print('  ',y,len(a),'beta %.3f'%((a@b)/(a@a)))
for k in ('2023-10','2023-11','2023-12','2024-01','2024-02','2024-03'):
    a=np.array([r['nvda_day'] for r in R if r['nvdl_day'] is not None and r['date'][:7]==k]); b=np.array([r['nvdl_day'] for r in R if r['nvdl_day'] is not None and r['date'][:7]==k])
    print('   day-beta',k,len(a),'%.3f'%((a@b)/(a@a)))
# section 3(f): trailing-120 NVDL overnight mean ex earnings, distributions added back
v=[r['nvdl_on_adj'] for r in R if r['nvdl_on_adj'] is not None and not r['earn']]
dd=[r['date'] for r in R if r['nvdl_on_adj'] is not None and not r['earn']]
print('\nRULE 3(f) reading: trailing-120 NVDL overnight mean, ex NVDA earnings nights, day-bar close->open:')
for back in (0,1,2,3):
    w=np.array(v[len(v)-120-back:len(v)-back]); print('   window ending night of %s: mean %+.3f%% sd %.3f t %.2f'%(dd[len(v)-1-back],100*w.mean(),100*w.std(ddof=1),w.mean()/(w.std(ddof=1)/math.sqrt(120))))
