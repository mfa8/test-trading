import csv, json, math, statistics as st
ET='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/exec_timing/'
REV='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/rev/'
PM='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/'
A=[r for r in csv.DictReader(open(ET+'tierA.csv')) if r['sym']=='NVDL']
print('NVDL mornings',len(A),A[0]['date'],A[-1]['date'], 'earn-exit flagged',sum(int(r['earn']) for r in A))
# daily closes NVDL
cl={}
for x in json.load(open(REV+'d2.json'))['data']['results']:
    if x['symbol']=='NVDL':
        for b in x['bars']:
            if b.get('interpolated') or not float(b['volume']): continue
            cl[b['begins_at'][:10]]=(float(b['open_price']),float(b['close_price']))
ds=sorted(cl)
def S(v):
    m=st.mean(v); s=st.stdev(v); return m,s,m/(s/math.sqrt(len(v))),len(v)
rows=[]
for r in A:
    d=r['date']; o=float(r['o0930']); p35=float(r['p0935']); dc=float(r['day_close']) if r['day_close'] else None
    i=ds.index(d) if d in ds else None
    if i is None or i<21: continue
    tr20=cl[ds[i-1]][1]/cl[ds[i-21]][1]-1            # trailing 20-session close-to-close return to the prior close
    oc20=st.mean([cl[ds[j]][1]/cl[ds[j]][0]-1 for j in range(i-20,i)])  # trailing 20 open->close mean
    gap=o/float(r['prev_close'])-1
    rows.append(dict(d=d,x=1e4*(p35/o-1),tr20=tr20,oc20=oc20,gap=gap,rest=(dc/p35-1) if dc else None,oc=(dc/o-1) if dc else None))
x=[r['x'] for r in rows]
print('open->09:35 bp all: mean %.1f sd %.1f t %.2f n %d'%S(x))
for lab,f in [('trailing 20d return < 0',lambda r:r['tr20']<0),('trailing 20d return >= 0',lambda r:r['tr20']>=0),('trailing-20 open->close mean < 0',lambda r:r['oc20']<0),('trailing-20 open->close mean >= 0',lambda r:r['oc20']>=0),
              ('trailing 20d return < -10%',lambda r:r['tr20']<-0.10),('before 2026-09-08',lambda r:r['d']<'2026-09-08'),('from 2026-09-08',lambda r:r['d']>='2026-09-08')]:
    v=[r['x'] for r in rows if f(r)]
    if len(v)>2: print('  %-34s mean %6.1f sd %6.1f t %5.2f n %d'%((lab,)+S(v)))
print('corr(x, trailing 20d return) %.3f ; corr(x, trailing-20 o->c mean) %.3f ; corr(x, gap) %.3f'%(st.correlation(x,[r['tr20'] for r in rows]),st.correlation(x,[r['oc20'] for r in rows]),st.correlation(x,[r['gap'] for r in rows])))
v=[(r['x'],1e4*r['rest']) for r in rows if r['rest'] is not None]
print('corr(first 5 min, rest of day) %.3f'%st.correlation([a for a,b in v],[b for a,b in v]))
# by month
from collections import defaultdict
bm=defaultdict(list)
for r in rows: bm[r['d'][:7]].append(r['x'])
for m in sorted(bm): print('  ',m,'n %d mean %.1f bp; '%(len(bm[m]),st.mean(bm[m])), end='')
print()
# variance share of first 5 min vs open->close day
oc=[1e4*r['oc'] for r in rows if r['oc'] is not None]
print('sd first5 %.0f bp ; sd open->close %.0f bp ; var share %.3f ; mean o->c %.1f bp'%(st.stdev(x),st.stdev(oc),(st.stdev(x)/st.stdev(oc))**2,st.mean(oc)))
# m1: first minute for the 1-minute mornings
M=list(csv.DictReader(open(ET+'m1.csv')))
print(M[0])
