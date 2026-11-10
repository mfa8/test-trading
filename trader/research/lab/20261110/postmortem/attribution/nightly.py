import json, random, math, statistics as st, collections
legs=json.load(open('legs.json'))
N=collections.OrderedDict()
for l in legs:
    d=N.setdefault(l['n'],dict(n=l['n'],date=l['date'],nd=l['nd'],inv=0,ours=0,model=0,entry=0,exit=0,cross=0,syms=[]))
    d['inv']+=l['inv']; d['ours']+=l['ours_d']; d['model']+=l['model_d']; d['entry']+=l['entry_d']; d['exit']+=l['exit_d']; d['cross']+=l['cross_d']; d['syms'].append(f"{l['sym']}x{l['q']}")
nights=list(N.values())
for d in nights:
    for k in ('ours','model','entry','exit','cross'):
        d[k+'_p']=100*d[k]/d['inv']
json.dump(nights,open('nights.json','w'),indent=1)
print(f"{'N':>3} {'entry':10} {'exit':10} {'inv$':>7} {'ours$':>7} {'mod$':>7} {'ent$':>6} {'ext$':>6} {'ours%':>7} {'mod%':>7} {'ent%':>6} {'ext%':>6}  basket")
for d in nights:
    print(f"{d['n']:3d} {d['date']} {d['nd']} {d['inv']:7.2f} {d['ours']:7.2f} {d['model']:7.2f} {d['entry']:6.2f} {d['exit']:6.2f} {d['ours_p']:7.2f} {d['model_p']:7.2f} {d['entry_p']:6.2f} {d['exit_p']:6.2f}  {' '.join(d['syms'])}")
random.seed(20261110)
def boot(x,B=20000,w=None):
    n=len(x); ms=[]
    for _ in range(B):
        idx=[random.randrange(n) for _ in range(n)]
        if w is None: ms.append(sum(x[i] for i in idx)/n)
        else:
            sw=sum(w[i] for i in idx); ms.append(sum(x[i]*w[i] for i in idx)/sw)
    ms.sort()
    return ms[int(0.05*B)], ms[int(0.5*B)], ms[int(0.95*B)-1], sum(1 for m in ms if m<0)/B
def summ(ns,label):
    print(f"\n== {label}: {len(ns)} nights, invested ${sum(d['inv'] for d in ns):.2f}")
    for k in ('exit','entry','model','ours'):
        x=[d[k+'_p'] for d in ns]; w=[d['inv'] for d in ns]
        m=st.mean(x); sd=st.stdev(x) if len(x)>1 else float('nan'); t=m/(sd/math.sqrt(len(x))) if len(x)>1 else float('nan')
        lo,med,hi,pneg=boot(x)
        wl,wm,wh,wp=boot(x,w=w)
        dw=100*sum(d[k] for d in ns)/sum(d['inv'] for d in ns)
        neg=sum(1 for v in x if v<0); pos=sum(1 for v in x if v>0)
        print(f" {k:6}: mean {m:+.3f}%  sd {sd:.3f}  t {t:+.2f}  median {st.median(x):+.3f}%  boot90 [{lo:+.3f},{hi:+.3f}]  P(mean<0) {pneg:.3f} | $-wtd {dw:+.3f}% boot90 [{wl:+.3f},{wh:+.3f}] P<0 {wp:.3f} | neg {neg}/{len(x)} pos {pos}  sum$ {sum(d[k] for d in ns):+.2f}")
summ(nights,'ALL 44')
summ([d for d in nights if d['n']<=24],'era1 N1-24 mixed basket')
summ([d for d in nights if d['n']>=25],'era2 N25-44 NVDA-2x only')
summ([d for d in nights if d['n']<=42],'N1-42 (excluding the last two mornings 11/09, 11/10)')
summ([d for d in nights if 25<=d['n']<=42],'era2 without N43,N44')
# sign test
from math import comb
def binom_two(k,n):
    p=sum(comb(n,i) for i in range(0,min(k,n-k)+1))/2**n*2
    return min(1,p)
for lab,ns in (('all',nights),('era1',[d for d in nights if d['n']<=24]),('era2',[d for d in nights if d['n']>=25])):
    for k in ('exit','entry'):
        neg=sum(1 for d in ns if d[k+'_p']<0)
        print(lab,k,'neg',neg,'of',len(ns),'sign-test two-sided p',round(binom_two(neg,len(ns)),4))
# worst nights
print('\nworst nights by ours$:')
for d in sorted(nights,key=lambda d:d['ours'])[:8]:
    print(f"  N{d['n']:02d} {d['date']}->{d['nd']} ours {d['ours']:+.2f} model {d['model']:+.2f} entry {d['entry']:+.2f} exit {d['exit']:+.2f} ({d['ours_p']:+.2f}% / model {d['model_p']:+.2f}%) {' '.join(d['syms'])}")
print('worst nights by exit leg $:')
for d in sorted(nights,key=lambda d:d['exit'])[:8]:
    print(f"  N{d['n']:02d} {d['date']}->{d['nd']} exit {d['exit']:+.2f} ({d['exit_p']:+.2f}%) model {d['model_p']:+.2f}%")
print('best nights by exit leg $:')
for d in sorted(nights,key=lambda d:-d['exit'])[:5]:
    print(f"  N{d['n']:02d} {d['date']}->{d['nd']} exit {d['exit']:+.2f} ({d['exit_p']:+.2f}%) model {d['model_p']:+.2f}%")
tot=sum(d['ours'] for d in nights)
w3=sorted(nights,key=lambda d:d['ours'])[:3]
print('total',round(tot,2),'worst3',round(sum(d['ours'] for d in w3),2),'rest',round(tot-sum(d['ours'] for d in w3),2))
print('cum ours by night:')
c=0
for d in nights:
    c+=d['ours']; print(f"N{d['n']}:{c:+.2f}",end='  ')
print()
