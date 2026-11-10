import json, math, re, statistics as st
src=open('/home/user/test-trading/trader/research/edge_decay/s01_prep.py').read()
m=re.search(r'EARN = """(.*?)"""',src,re.S)
EARN=set(m.group(1).split())
print('earn dates',len(EARN), sorted(EARN)[:3], sorted(EARN)[-3:])
REV='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/rev/'
PM='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/'
B={}
for f in ['d0a.json','d0b.json','d1.json','d2.json']:
    for x in json.load(open(REV+f))['data']['results']:
        s=x['symbol']
        for b in x['bars']:
            d=b['begins_at'][:10]
            if b.get('interpolated') or not float(b.get('volume') or 0): continue
            if d>'2026-11-06': continue
            if s=='NVDA' and d<='2000-10-27': continue
            B.setdefault(s,{})[d]=(float(b['open_price']),float(b['close_price']))
for r in json.load(open(PM+'day_0908_1110.json'))['data']['results']:
    for b in r['bars']:
        d=b['begins_at'][:10]
        if b.get('interpolated') or not float(b.get('volume') or 0): continue
        if d>'2026-11-06': B.setdefault(r['symbol'],{})[d]=(float(b['open_price']),float(b['close_price']))
n=B['NVDA']; q=B['QQQ']
qd=sorted(q); qc=[q[d][1] for d in qd]; state={}
for i,d in enumerate(qd):
    if i>=199: state[d]=1 if qc[i]>=sum(qc[i-199:i])/199 else 0
ds=sorted(n)
rows=[]
for i in range(len(ds)-1):
    a,b=ds[i],ds[i+1]
    rows.append(dict(d=a,u=2*(n[b][0]/n[a][1]-1)-0.0009,day=2*(n[b][1]/n[b][0]-1),earn=a in EARN,st=state.get(a)))
print('nights',len(rows),rows[0]['d'],rows[-1]['d'])
def S(v):
    if len(v)<2: return (float('nan'),)*3+(len(v),)
    m=st.mean(v); s=st.stdev(v); return 100*m,100*s,m/(s/math.sqrt(len(v))),len(v)
print('BY YEAR synthetic 2x after 9bp: mean/sd/t/n | ex-earn mean')
for y in range(2015,2027):
    v=[r['u'] for r in rows if r['d'][:4]==str(y)]; ve=[r['u'] for r in rows if r['d'][:4]==str(y) and not r['earn']]
    print(y,'%+.2f / %.2f / %.1f / %d | ex-earn %+.2f'%(S(v)+(S(ve)[0],)))
v=[r['u'] for r in rows if r['d']>='2015']; print('2015-26','%+.3f / %.2f / %.1f / %d'%S(v))
ve=[r['u'] for r in rows if r['d']>='2015' and not r['earn']]; print('2015-26 ex-earn','%+.3f / %.2f / %.1f / %d'%S(ve))
v=[r['u'] for r in rows if r['d']<'2015']; print('2000-14','%+.3f / %.2f / %.1f / %d'%S(v))
e=[r['u']+0.0009 for r in rows if r['d']>='2015' and r['earn']]; tot=sum(r['u']+0.0009 for r in rows if r['d']>='2015')
print('earn nights n',len(e),'mean gross %.2f'%(100*st.mean(e)),'share of gross sum %.2f'%(sum(e)/tot), 'share of net sum %.2f'%(sum(x-0.0009 for x in e)/sum(r['u'] for r in rows if r['d']>='2015')))
for lab,f in [('2015-26',lambda r:r['d']>='2015'),('2000-14',lambda r:r['d']<'2015')]:
    for stt in (0,1):
        v=[r['u'] for r in rows if f(r) and r['st']==stt]; print(lab,'state',stt,'%+.3f / %.2f / %.1f / %d'%S(v))
        v=[r['u'] for r in rows if f(r) and r['st']==stt and not r['earn']]; print('   ex-earn','%+.3f / %.2f / %.1f / %d'%S(v))
# latest windows
for k in (44,60,120,250):
    v=[r['u'] for r in rows[-k:]]; ve=[r['u'] for r in rows[-k:] if not r['earn']]
    print('last',k,'%+.3f / %.2f / %.1f / %d'%S(v),'ex-earn %+.3f'%S(ve)[0], 'day(2x, no cost) %+.3f t %.1f'%(S([r['day'] for r in rows[-k:]])[0],S([r['day'] for r in rows[-k:]])[2]))
# What does a 44-night stretch look like historically at these exposures: P(sum<=x)
import random
v=[r['u'] for r in rows if r['d']>='2015' and not r['earn']]
# rolling 44-night compounded returns at 0.9 exposure
cnt=0;tot=0;c20=0
for i in range(len(v)-44):
    eq=1
    for x in v[i:i+44]: eq*=1+0.9*x
    tot+=1; cnt+= eq-1<=-0.097; c20+= eq-1<=-0.20
print('rolling 44-night windows 2015-26 ex-earn at 0.9 exposure: P(<=-9.7%%) %.3f P(<=-20%%) %.3f'%(cnt/tot,c20/tot))
json.dump(rows,open('c3_rows.json','w'))
