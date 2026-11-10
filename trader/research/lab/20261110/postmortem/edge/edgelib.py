import json, math
BASE='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/'
def _read(f):
    out={}
    for x in json.load(open(BASE+f))['data']['results']:
        s=x['symbol']
        for b in x['bars']:
            if b.get('interpolated'): continue
            if not b.get('volume'): continue
            d=b['begins_at'][:10]
            out.setdefault(s,{})[d]=(float(b['open_price']),float(b['high_price']),float(b['low_price']),float(b['close_price']),float(b['volume']))
    return out
def load():
    """long history to 2026-11-06 from rev/, then 2026-11-09 and 11-10 from pm/ (and pm overrides nothing before 11-09)"""
    bars={}
    for f in ('rev/d0a.json','rev/d0b.json','rev/d1.json','rev/d2.json'):
        r=_read(f)
        for s,dd in r.items():
            for d,v in dd.items():
                if d>'2026-11-06': continue
                if s=='NVDA' and d<='2000-10-27': continue
                bars.setdefault(s,{})[d]=v
    pm=_read('pm/day_0908_1110.json')
    for s,dd in pm.items():
        for d,v in dd.items():
            if d>='2026-11-09':
                bars.setdefault(s,{})[d]=v
    return bars,pm
def stats(v):
    n=len(v)
    if n<2: return dict(n=n,mean=float('nan'),sd=float('nan'),t=float('nan'),g=float('nan'),win=float('nan'))
    m=sum(v)/n
    s=math.sqrt(sum((x-m)**2 for x in v)/(n-1))
    g=sum(math.log(1+x) for x in v)/n
    return dict(n=n,mean=100*m,sd=100*s,t=(m/(s/math.sqrt(n)) if s>0 else float('nan')),g=100*g,win=100*sum(x>0 for x in v)/n)
