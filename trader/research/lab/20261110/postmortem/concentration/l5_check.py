# Second pass, separate pure-python code path (no numpy, own loader) for the headline numbers + a few extras.
import json, math, csv
R='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/rev/'
px={}
for f in ('d0b.json','d1.json','d2.json'):
    for res in json.load(open(R+f))['data']['results']:
        if res['symbol'] not in ('NVDA','QQQ','TQQQ'): continue
        for b in res['bars']:
            day=b['begins_at'][:10]
            if b.get('interpolated') or not b.get('volume') or day>'2026-11-06': continue
            px.setdefault(res['symbol'],{})[day]=(float(b['open_price']),float(b['close_price']))
days=sorted(px['QQQ'])
qclose=[px['QQQ'][d][1] for d in days]
out=[]
for i in range(len(days)-1):
    t=days[i]; u=days[i+1]
    if t<'2015-01-02': continue
    line=sum(qclose[i-199:i])/199.0
    size=0.98 if qclose[i]>=line else 0.25
    a=2*(px['NVDA'][u][0]/px['NVDA'][t][1]-1); b=px['TQQQ'][u][0]/px['TQQQ'][t][1]-1
    out.append((t,size,a,b))
def summarize(rs):
    eq=1.0; peak=1.0; dd=0.0; hist=[1.0]; trig=0; lg=0.0
    for r in rs:
        eq*=1+r; lg+=math.log(1+r); peak=max(peak,eq); dd=min(dd,eq/peak-1); hist.append(eq)
        if eq<=0.8*max(hist[-20:]): trig+=1
    m=sum(rs)/len(rs); sd=math.sqrt(sum((r-m)**2 for r in rs)/(len(rs)-1))
    return 100*lg/len(rs),100*min(rs),100*dd,100*sd,trig
for name,lo,hi in (('2015-2020','2015','2020'),('2021-2026','2021','2026'),('2015-2026','2015','2026')):
    sel=[x for x in out if lo<=x[0][:4]<=hi]
    for mode in ('trend','full'):
        line=[]
        for w in (1.0,0.5,0.0):
            rs=[(s if mode=='trend' else 0.98)*(w*a+(1-w)*b-0.0009) for t,s,a,b in sel]
            line.append(summarize(rs))
        print(name,mode,len(sel),' | '.join('g %+.4f worst %+.2f dd %+.1f sd %.3f pauseN %d'%x for x in line))
# idiosyncratic NVDA nights: 2xNVDA leg at least 8 points worse than the TQQQ leg, by earnings flag
earn=set(r['date'] for r in csv.DictReader(open('/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv')) if r['earn']=='1')
idio=[(t,s,a,b) for t,s,a,b in out if a-b<=-0.08]
print('nights with 2xNVDA leg >=8 points worse than TQQQ leg: %d (earnings %d, non-earnings %d)'%(len(idio),sum(t in earn for t,_,_,_ in idio),sum(t not in earn for t,_,_,_ in idio)))
for t,s,a,b in idio: print('   %s size %.2f %s 2xNVDA %+.1f%% TQQQ %+.1f%% | account NVDL-only %+.2f%% split %+.2f%%'%(t,s,'E' if t in earn else ' ',100*a,100*b,100*s*(a-0.0009),100*s*(0.5*a+0.5*b-0.0009)))
ne=[x for x in idio if x[0] not in earn]
print('non-earnings idiosyncratic nights: sum NVDL-only %+.1f%% split %+.1f%% (trend rule); log saved by the split over 12 years: %.3f'%(100*sum(s*(a-0.0009) for t,s,a,b in ne),100*sum(s*(0.5*a+0.5*b-0.0009) for t,s,a,b in ne),sum(math.log(1+s*(0.5*a+0.5*b-0.0009))-math.log(1+s*(a-0.0009)) for t,s,a,b in ne)))
tot1=sum(math.log(1+s*(a-0.0009)) for t,s,a,b in out); tot5=sum(math.log(1+s*(0.5*a+0.5*b-0.0009)) for t,s,a,b in out)
print('total log growth 2015-26 (trend rule): NVDL-only %.3f split %.3f difference %.3f over %.2f years -> %.3f log per year'%(tot1,tot5,tot5-tot1,len(out)/251.0,(tot5-tot1)/(len(out)/251.0)))
# mirror: nights where 2xNVDA beat TQQQ by >=8 points
good=[(t,s,a,b) for t,s,a,b in out if a-b>=0.08]
print('nights with 2xNVDA leg >=8 points BETTER than TQQQ: %d (earnings %d, non-earnings %d)'%(len(good),sum(t in earn for t,_,_,_ in good),sum(t not in earn for t,_,_,_ in good)))
# gross overnight edge per leg (unsized, no cost), t-stats, by half and ex-earnings
def ts(v):
    m=sum(v)/len(v); sd=math.sqrt(sum((x-m)**2 for x in v)/(len(v)-1)); return len(v),100*m,100*sd,m/(sd/math.sqrt(len(v)))
for name,lo,hi in (('2015-2020','2015','2020'),('2021-2026','2021','2026'),('2015-2026','2015','2026'),('2026','2026','2026')):
    sel=[x for x in out if lo<=x[0][:4]<=hi]
    print(name,'gross overnight, unsized: 2xNVDA all n=%d mean %+.3f%% sd %.2f t %.2f | 2xNVDA ex-earnings n=%d mean %+.3f%% sd %.2f t %.2f | TQQQ n=%d mean %+.3f%% sd %.2f t %.2f'%(ts([a for t,s,a,b in sel])+ts([a for t,s,a,b in sel if t not in earn])+ts([b for t,s,a,b in sel])))
    print('    net growth at 0.98 always after 9bp: 2xNVDA ex-earnings g %+.4f | TQQQ g %+.4f'%(100*sum(math.log(1+0.98*(a-0.0009)) for t,s,a,b in sel if t not in earn)/len(sel),100*sum(math.log(1+0.98*(b-0.0009)) for t,s,a,b in sel)/len(sel)))
