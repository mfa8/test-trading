import csv, math, numpy as np
rows=list(csv.DictReader(open('/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv')))
print('rows',len(rows),'first',rows[0]['date'],'last',rows[-1]['date'])
ne=[r for r in rows if r['earn']!='1' and r['nvda_on']!='']
print('non-earn nights',len(ne),'earn nights',sum(r['earn']=='1' for r in rows))
on=np.array([float(r['nvda_on']) for r in ne]); gd=np.array([int(r['gapdays']) for r in ne])
def stats(on,gd,lab):
    print(lab,'n',len(on),'<=-5%',(on<=-0.05).sum(),'%.2f%%'%(100*(on<=-0.05).mean()),'<=-9.8%',(on<=-0.098).sum(),'%.2f%%'%(100*(on<=-0.098).mean()))
stats(on,gd,'all')
for n in (493,496,500,501):
    stats(on[-n:],gd[-n:],'last%d'%n)
for r in ne:
    if float(r['nvda_on'])<=-0.05: print(r['date'],r['next'],r['gapdays'],r['nvda_on'])
# weekend ratio
wk=gd>=3
for lab,sl in (('all',slice(None)),('2y',slice(-485,None)),('2y496',slice(-496,None))):
    o=on[sl];g=gd[sl]
    print(lab,'weekend(gap3) n',(g==3).sum(),'weeknight n',(g==1).sum(),'ratio var %.2f'%(o[g==3].var()/o[g==1].var()),'ratio msq %.2f'%(np.mean(o[g==3]**2)/np.mean(o[g==1]**2)), 'gap>=3 ratio %.2f'%(o[g>=3].var()/o[g==1].var()), 'n>=3',(g>=3).sum())
# NVDL beta
b=[(float(r['nvda_on']),float(r['nvdl_on'])) for r in ne if r['nvdl_on']!='']
x=np.array([a for a,_ in b]);y=np.array([c for _,c in b])
print('NVDL nights',len(b),'beta %.3f'%(np.cov(x,y)[0,1]/x.var(ddof=1)))
bc=[(float(r['nvda_on']),float(r['nvdl_clean'])) for r in ne if r['nvdl_clean']!='']
x=np.array([a for a,_ in bc]);y=np.array([c for _,c in bc])
print('NVDL clean nights',len(bc),'beta %.3f'%(np.cov(x,y)[0,1]/x.var(ddof=1)))
# empirical z: trailing 20 sd lagged
allon=[(r['date'],float(r['nvda_on']),r['earn']=='1') for r in rows if r['nvda_on']!='']
z=[]
hist=[]
for dte,o,e in allon:
    if e: continue
    if len(hist)>=20:
        sd=np.std(hist[-20:],ddof=1)
        if sd>0: z.append(o/sd)
    hist.append(o)
z=np.array(z)
from scipy import stats as st
print('z n',len(z))
for k in (3,4,5):
    t3=st.t.cdf(-k*math.sqrt(3),3); 
    print('P(z<=-%d) emp %.2f%% t3 %.2f%% normal %.3f%%'%(k,100*(z<=-k).mean(),100*t3,100*st.norm.cdf(-k)))
print('excess kurt %.1f'%st.kurtosis(z))
