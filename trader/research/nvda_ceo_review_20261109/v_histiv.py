import json, math, datetime as dt
from statistics import NormalDist
N=NormalDist().cdf
h=json.load(open('../data_opt_hist_daily.json'))
bars=json.load(open('nvda_daily_verify.json'))['data']['results'][0]['bars']
cl={b['begins_at'][:10]:float(b['close_price']) for b in bars}
r=0.033
def bs(S,K,T,s,cp):
    F=S*math.exp(r*T); DF=math.exp(-r*T)
    d1=(math.log(F/K)+0.5*s*s*T)/(s*math.sqrt(T)); d2=d1-s*math.sqrt(T)
    return DF*(F*N(d1)-K*N(d2)) if cp=='C' else DF*(K*N(-d2)-F*N(-d1))
def iv(p,S,K,T,cp):
    lo,hi=1e-4,5
    for _ in range(100):
        m=(lo+hi)/2
        if bs(S,K,T,m,cp)>p: hi=m
        else: lo=m
    return m
mism=[(d,c,cl.get(d)) for d,c in zip(h['dates'],h['nvda_close']) if abs(c-cl.get(d,0))>0.01]
print('close mismatches',mism)
eB=0.0877**2
for exp,tdl in (('2026-11-20',None),('2026-12-18',None)):
    e=dt.datetime.fromisoformat(exp).replace(hour=16)
    out=[]
    for i,dd in enumerate(h['dates']):
        S=h['nvda_close'][i]; T=(e-dt.datetime.fromisoformat(dd).replace(hour=16)).total_seconds()/86400/365
        pts=[]
        for k,v in h[exp].items():
            K=float(k[:-1]); cp=k[-1]
            otm=(cp=='C' and K>=S) or (cp=='P' and K<=S)
            if otm: pts.append((K,iv(v[i],S,K,T,cp)))
        pts.sort()
        lo=[p for p in pts if p[0]<=S]; hi=[p for p in pts if p[0]>=S]
        if lo and hi:
            a,b=lo[-1],hi[0]; w=(S-a[0])/(b[0]-a[0]) if b[0]!=a[0] else 0; a_iv=a[1]*(1-w)+b[1]*w; tag=''
        else:
            near=min(pts,key=lambda p:abs(p[0]-S)); a_iv=near[1]; tag='(flat %s)'%near[0]
        # ex-earn base for 11/20: TD remaining
        out.append('%s S=%.2f ATM=%.1f%%%s'%(dd[5:],S,100*a_iv,tag))
        if exp=='2026-11-20':
            # trading days from dd close to 11/20 close
            d0=dt.date.fromisoformat(dd); n=0; x=d0
            while x<dt.date(2026,11,20):
                x+=dt.timedelta(1)
                if x.weekday()<5: n+=1
            tv=a_iv**2*T; b=(tv-eB)/(n-1)
            out[-1]+=' base=%s'%('%.1f%%'%(100*math.sqrt(b*252)) if b>0 else 'neg')
    print(exp); print('\n'.join(out))
