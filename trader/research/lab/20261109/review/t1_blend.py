import csv, math, statistics as st
from load import load, legs, S
B=load()
earn=set(r['date'] for r in csv.DictReader(open('/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv')) if r['earn']=='1')
L={s:{x['d']:x for x in legs(B[s])} for s in B}
def g(v): return 100*st.mean([math.log(1+x) for x in v])
def row(name,v):
    m=st.mean(v); s=st.stdev(v)
    print("  %-22s n=%4d mean %+.3f sd %5.2f t %+5.2f g %+.3f worst %+6.1f  p1 %+5.1f"%(name,len(v),100*m,100*s,m/(s/math.sqrt(len(v))),g(v),100*min(v),100*sorted(v)[len(v)//100]))
def corr(a,b):
    ma,mb=st.mean(a),st.mean(b); return sum((x-ma)*(y-mb) for x,y in zip(a,b))/(len(a)-1)/st.stdev(a)/st.stdev(b)
periods=[('2015-01-01','2018-12-31'),('2019-01-01','2022-12-31'),('2023-01-01','2024-12-31'),('2025-01-01','2025-12-31'),('2026-01-01','2026-12-31'),('2015-01-01','2026-12-31')]
C=0.0005  # round-trip cost per night per unit held (5bp) applied to every leveraged product
print("NVDA2x proxy = 2*NVDA_on - 4bp; all series net of 5bp/night round-trip cost; NVDA earnings nights in cash (0) for NVDA products")
for a,b in periods:
    ds=[d for d in sorted(L['NVDA']) if a<=d<=b and d in L['SOXL'] and d in L['TQQQ']]
    nv=[0.0 if d in earn else 2*L['NVDA'][d]['on']-0.0004-C for d in ds]
    so=[L['SOXL'][d]['on']-C for d in ds]; tq=[L['TQQQ'][d]['on']-C for d in ds]; te=[L['TECL'][d]['on']-C for d in ds]
    print(a[:4],b[:4],"corr NVDA2x~SOXL %.2f  NVDA2x~TQQQ %.2f  SOXL~TQQQ %.2f"%(corr(nv,so),corr(nv,tq),corr(so,tq)))
    row('NVDA2x',nv); row('SOXL',so); row('TQQQ',tq); row('TECL',te)
    for w in (0.25,0.5):
        row('NVDA2x %.0f/SOXL %.0f'%(100-100*w,100*w),[(1-w)*x+w*y for x,y in zip(nv,so)])
    row('NVDA2x 50/TQQQ 50',[0.5*x+0.5*y for x,y in zip(nv,tq)])
    row('SOXL 50/TQQQ 50',[0.5*x+0.5*y for x,y in zip(so,tq)])
# real NVDL where it exists
print("REAL NVDL period (12/2022+), net 5bp, NVDA earnings nights cash")
ds=[d for d in sorted(L['NVDL']) if d in L['SOXL']]
for a,b in [('2022-12-01','2024-12-31'),('2025-01-01','2025-12-31'),('2026-01-01','2026-12-31'),('2022-12-01','2026-12-31')]:
    dd=[d for d in ds if a<=d<=b]
    nv=[0.0 if d in earn else L['NVDL'][d]['on']-C for d in dd]; so=[L['SOXL'][d]['on']-C for d in dd]
    print(a[:4],b[:4],"corr %.2f"%corr(nv,so)); row('NVDL',nv); row('SOXL',so); row('NVDL75/SOXL25',[0.75*x+0.25*y for x,y in zip(nv,so)]); row('NVDL50/SOXL50',[0.5*x+0.5*y for x,y in zip(nv,so)])
