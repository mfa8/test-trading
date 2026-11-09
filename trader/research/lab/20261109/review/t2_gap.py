import csv, math, statistics as st, sys
from load import load, legs, S
B=load()
# earnings nights for NVDA: from edge_decay csv (earn flag is on 'date' = close date before the report gap)
earn=set()
for r in csv.DictReader(open('/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv')):
    if r['earn']=='1': earn.add(r['date'])
def stat(v):
    if len(v)<3: return "n=%d"%len(v)
    m=st.mean(v); s=st.stdev(v); 
    return "n=%4d mean %+6.2f sd %5.2f t %+5.2f win %3.0f%% med %+5.2f"%(len(v),100*m,100*s,m/(s/math.sqrt(len(v))),100*sum(x>0 for x in v)/len(v),100*st.median(v))
buckets=[(-1,-.07),(-.07,-.05),(-.05,-.03),(-.03,-.02),(-.02,-.01),(-.01,0),(0,.01),(.01,.02),(.02,.03),(.03,.05),(.05,1)]
for sym in ('NVDA','SMH','QQQ','SOXL','TQQQ','NVDL'):
    L=legs(B[sym])
    if sym in('NVDA','NVDL'): L=[x for x in L if x['d'] not in earn]
    print("==",sym,"ID given same-morning ON gap (earnings nights excluded for NVDA/NVDL)", len(L))
    for lo,hi in buckets:
        v=[x['id'] for x in L if lo<=x['on']<hi]
        print("  ON [%+.0f%%,%+.0f%%): %s"%(100*lo,100*hi,stat(v)))
    on=[x['on'] for x in L]; idr=[x['id'] for x in L]
    mo,mi=st.mean(on),st.mean(idr)
    c=sum((a-mo)*(b-mi) for a,b in zip(on,idr))/(len(on)-1)/st.stdev(on)/st.stdev(idr)
    print("  corr(ON,ID same day) = %+.3f"%c)
