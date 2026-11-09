import json, math
from statistics import NormalDist
N=NormalDist().cdf
d=json.load(open('my_quotes.json'))['q']
r=0.033
S=186.64
import datetime as dt
t0=dt.datetime(2026,11,6,16)
def T(exp):
    e=dt.datetime.fromisoformat(exp).replace(hour=16)
    return (e-t0).total_seconds()/86400/365
def b76(F,K,T,s,DF,cp):
    d1=(math.log(F/K)+0.5*s*s*T)/(s*math.sqrt(T)); d2=d1-s*math.sqrt(T)
    if cp=='C': return DF*(F*N(d1)-K*N(d2))
    return DF*(K*N(-d2)-F*N(-d1))
def iv(price,F,K,T,DF,cp):
    lo,hi=1e-4,5
    for _ in range(200):
        m=(lo+hi)/2
        if b76(F,K,T,m,DF,cp)>price: hi=m
        else: lo=m
    return m
from collections import defaultdict
by=defaultdict(dict)
for e,K,cp,b,a in d: by[e].setdefault(K,{})[cp]=(b+a)/2
res={}
for e in sorted(by):
    t=T(e); DF=math.exp(-r*t)
    Fs=[K+(v['C']-v['P'])/DF for K,v in by[e].items()]
    F=sum(Fs)/len(Fs)
    ivs={}
    for K,v in sorted(by[e].items()):
        ivs[K]=(iv(v['C'],F,K,t,DF,'C')+iv(v['P'],F,K,t,DF,'P'))/2
    Ks=sorted(ivs)
    # interp at F
    for i in range(len(Ks)-1):
        if Ks[i]<=F<=Ks[i+1]:
            w=(F-Ks[i])/(Ks[i+1]-Ks[i]); atm=ivs[Ks[i]]*(1-w)+ivs[Ks[i+1]]*w
    strad=b76(F,F,t,atm,DF,'C')+b76(F,F,t,atm,DF,'P')
    res[e]=dict(T=t,F=F,Fs=Fs,ivs=ivs,atm=atm,strad=strad,pct=strad/S)
    print(e,'Tcal_days=%.1f'%(t*365),'F=%.2f'%F,'Fs',[round(x,2) for x in Fs],'ivs',{k:round(v*100,1) for k,v in ivs.items()},'ATM %.1f%%'%(atm*100),'strad $%.2f %.2f%%'%(strad,strad/S*100))
json.dump({k:{kk:vv for kk,vv in v.items() if kk!='ivs'} for k,v in res.items()},open('v_iv_out.json','w'),indent=1)
# trading days from Fri close: 11/13: Mon-Fri =5; 11/16: 6; 11/18: 8; 11/20: 10; 12/18: 30 (11/26 Thanksgiving holiday, 11/27 half day counted)
TD={'2026-11-13':5,'2026-11-16':6,'2026-11-18':8,'2026-11-20':10,'2026-12-18':29}
var={e:res[e]['atm']**2*res[e]['T'] for e in res}
for e in res: print(e,'per-TD sigma %.2f%%'%(100*math.sqrt(var[e]/TD[e])))
base=var['2026-11-13']/5
eA=var['2026-11-20']-9*base
print('Method A earnings-day sigma %.2f%% share of 11/20 var %.1f%%'%(100*math.sqrt(eA),100*eA/var['2026-11-20']))
print('  7 pre-earn days share %.1f%%, 2 post %.1f%%'%(100*7*base/var['2026-11-20'],100*2*base/var['2026-11-20']))
b16=var['2026-11-16']/6
eB=var['2026-11-18']-7*b16
print('Method B earnings-day sigma %.2f%% share 11/18 %.1f%% share 11/20 %.1f%%'%(100*math.sqrt(eB),100*eB/var['2026-11-18'],100*eB/var['2026-11-20']))
# straddle dollars removed: price 11/20 straddle with var - eA
for lab,ev in (('A',eA),('B',eB)):
    e='2026-11-20'; t=res[e]['T']; DF=math.exp(-r*t); F=res[e]['F']
    s2=math.sqrt((var[e]-ev)/t)
    st2=b76(F,F,t,s2,DF,'C')+b76(F,F,t,s2,DF,'P')
    print(lab,'earn premium $%.2f = %.1f%% of straddle'%(res[e]['strad']-st2,100*(res[e]['strad']-st2)/res[e]['strad']))
# ex-earnings 12/18 base
e='2026-12-18'
b=(var[e]-eB)/(TD[e]-1); print('12/18 ex-earn per TD %.2f%% ann(252) %.1f%%'%(100*math.sqrt(b),100*math.sqrt(b*252)))
b=(var['2026-11-20']-eB)/9; print('11/20 ex-earn per TD %.2f%%'%(100*math.sqrt(b)))
