import json, math, csv
import numpy as np
bars=json.load(open('nvda_daily_verify.json'))['data']['results'][0]['bars']
d=[(b['begins_at'][:10],float(b['open_price']),float(b['close_price'])) for b in bars]
rows=list(csv.DictReader(open('/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv')))
earn={r['date'] for r in rows if r['earn']=='1'}
csvon={r['date']:float(r['nvda_on']) for r in rows if r['nvda_on']}
# per day i (i>=1): overnight = log(open_i/close_{i-1}); cc=log(close_i/close_{i-1}); intraday=log(close_i/open_i)
recs=[]
for i in range(1,len(d)):
    dp,op,cp=d[i-1]; di,oi,ci=d[i]
    on=math.log(oi/cp); cc=math.log(ci/cp); intr=math.log(ci/oi)
    recs.append((di,dp,on,cc,intr,dp in earn))
# check consistency with csv
mm=[abs(math.exp(r[2])-1-csvon[r[1]]) for r in recs if r[1] in csvon]
print('n match',len(mm),'max abs diff simple vs csv',max(mm))
ne=[r for r in recs if not r[5]]
print('last date',ne[-1][0],'n non-earn',len(ne))
for lab,n in (('1y',247),('2y',496),('2y_all',len(ne)),('60',60),('20',20),('10',10)):
    s=ne[-n:]
    on=np.array([r[2] for r in s]); cc=np.array([r[3] for r in s]); it=np.array([r[4] for r in s])
    print(lab,len(s),'share sumsq %.3f'%(np.sum(on**2)/np.sum(cc**2)),'share var %.3f'%(on.var()/cc.var()),'share on/(on+intra) %.3f'%(np.sum(on**2)/(np.sum(on**2)+np.sum(it**2))),'sd_on %.2f%%'%(on.std(ddof=1)*100),'cc ann %.1f%%'%(cc.std(ddof=1)*math.sqrt(252)*100))
