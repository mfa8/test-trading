import json, random, math, statistics as st
nights=json.load(open('nights.json')); legs=json.load(open('legs.json'))
random.seed(7)
def boot(x,B=20000):
    n=len(x)
    if n<2: return (float('nan'),float('nan'))
    ms=sorted(sum(x[random.randrange(n)] for _ in range(n))/n for _ in range(B))
    return ms[int(0.05*B)], ms[int(0.95*B)-1]
def row(ns,label,key='exit'):
    if not ns: print(f"  {label:34} n=0"); return
    x=[d[key+'_p'] for d in ns]
    lo,hi=boot(x)
    sd=st.stdev(x) if len(x)>1 else float('nan')
    t=st.mean(x)/(sd/math.sqrt(len(x))) if len(x)>1 and sd>0 else float('nan')
    print(f"  {label:34} n={len(ns):2d} mean {key} {st.mean(x):+.3f}% median {st.median(x):+.3f}% sd {sd:.3f} t {t:+.2f} boot90 [{lo:+.3f},{hi:+.3f}] neg {sum(1 for v in x if v<0)}/{len(x)} sum$ {sum(d[key] for d in ns):+.2f} (inv ${sum(d['inv'] for d in ns):.0f}, $-wtd {100*sum(d[key] for d in ns)/sum(d['inv'] for d in ns):+.3f}%)")
def bucket(m):
    return 'down<-2%' if m<-2 else ('up>+2%' if m>2 else 'mid')
for era,sel in (('ALL',lambda d:True),('era1 N1-24',lambda d:d['n']<=24),('era2 N25-44',lambda d:d['n']>=25),('era2 excl N43-44',lambda d:25<=d['n']<=42),('ALL excl N43-44',lambda d:d['n']<=42)):
    print('NIGHT level',era)
    ns=[d for d in nights if sel(d)]
    for b in ('down<-2%','mid','up>+2%'):
        row([d for d in ns if bucket(d['model_p'])==b],b)
    row([d for d in ns if d['model_p']<0],'gap down (model<0)')
    row([d for d in ns if d['model_p']>=0],'gap up (model>=0)')
    row([d for d in ns if abs(d['model_p'])>2],'|gap|>2%')
    row([d for d in ns if abs(d['model_p'])<=2],'|gap|<=2%')
# correlations
def corr(x,y):
    mx,my=st.mean(x),st.mean(y)
    sxy=sum((a-mx)*(b-my) for a,b in zip(x,y)); sxx=sum((a-mx)**2 for a in x); syy=sum((b-my)**2 for b in y)
    return sxy/math.sqrt(sxx*syy), sxy/sxx, my-sxy/sxx*mx
def spearman(x,y):
    def rk(v):
        s=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v)
        for k,i in enumerate(s): r[i]=k
        return r
    return corr(rk(x),rk(y))[0]
for era,sel in (('ALL',lambda d:True),('era1',lambda d:d['n']<=24),('era2',lambda d:d['n']>=25),('ALL excl N43-44',lambda d:d['n']<=42),('era2 excl 43-44',lambda d:25<=d['n']<=42)):
    ns=[d for d in nights if sel(d)]
    x=[d['model_p'] for d in ns]; y=[d['exit_p'] for d in ns]
    r,b,a=corr(x,y); n=len(x); t=r*math.sqrt((n-2)/(1-r*r))
    r2,b2,a2=corr([abs(v) for v in x],y); t2=r2*math.sqrt((n-2)/(1-r2*r2))
    print(f"{era:18} n={n} corr(exit%,gap%)={r:+.3f} (t {t:+.2f}) slope {b:+.4f} intercept {a:+.3f}% spearman {spearman(x,y):+.3f} | corr(exit%,|gap|%)={r2:+.3f} (t {t2:+.2f}) slope {b2:+.4f} icpt {a2:+.3f} spearman {spearman([abs(v) for v in x],y):+.3f}")
# leg-level (description only, not for inference)
print('\nLEG level (descriptive only; legs on the same morning are correlated)')
for era,sel in (('ALL',lambda l:True),('era1',lambda l:l['n']<=24),('era2',lambda l:l['n']>=25)):
    ls=[l for l in legs if sel(l)]
    for b in ('down<-2%','mid','up>+2%'):
        s=[l for l in ls if bucket(100*l['model'])==b]
        if s: print(f"  {era:5} {b:9} legs={len(s):2d} mean exit {100*st.mean(l['exit'] for l in s):+.3f}% $-wtd {100*sum(l['exit_d'] for l in s)/sum(l['inv'] for l in s):+.3f}% sum$ {sum(l['exit_d'] for l in s):+.2f} neg {sum(1 for l in s if l['exit']<0)}")
# by symbol family: NVDA-2x legs across both eras vs others
print('\nNVDA-2x legs vs other names, nightly aggregation within family')
import collections
for fam,syms in (('NVDA2x',('NVDL','NVDX')),('other',('METU','AAPU','AMZU'))):
    agg=collections.OrderedDict()
    for l in legs:
        if l['sym'] in syms:
            a=agg.setdefault(l['n'],dict(n=l['n'],inv=0,exit=0,model=0,entry=0))
            a['inv']+=l['inv']; a['exit']+=l['exit_d']; a['model']+=l['model_d']; a['entry']+=l['entry_d']
    ns=list(agg.values())
    for d in ns:
        for k in ('exit','model','entry'): d[k+'_p']=100*d[k]/d['inv']
    row(ns,fam+' all nights held')
    row([d for d in ns if d['n']<=24],fam+' era1')
    row([d for d in ns if d['n']>=25],fam+' era2')
    row(ns,fam+' ENTRY leg','entry')
