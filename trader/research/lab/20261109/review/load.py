import json, math, statistics as st
def load():
    out={}
    for f in ('d1.json','d2.json'):
        for x in json.load(open(f))['data']['results']:
            s=x['symbol']
            for b in x['bars']:
                if b.get('interpolated'): continue
                if not b.get('volume'): continue
                out.setdefault(s,{})[b['begins_at'][:10]]=(float(b['open_price']),float(b['high_price']),float(b['low_price']),float(b['close_price']))
    return out
def legs(bars):
    ds=sorted(bars); r=[]
    for i in range(len(ds)-1):
        t,t1=ds[i],ds[i+1]
        o,h,l,c=bars[t]; o1,h1,l1,c1=bars[t1]
        r.append(dict(d=t,n=t1,on=o1/c-1,id=c1/o1-1,cc=c1/c-1))
    return r
def S(v):
    n=len(v); m=st.mean(v); s=st.stdev(v)
    return dict(n=n,mean=100*m,sd=100*s,t=m/(s/math.sqrt(n)),g=100*st.mean([math.log(1+x) for x in v]),win=100*sum(x>0 for x in v)/n)
