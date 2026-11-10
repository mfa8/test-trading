import csv, math
import numpy as np
P='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge/'
R=[r for r in csv.DictReader(open(P+'nights.csv')) if r['syn2x_on']!='']
for r in R:
    r['u']=float(r['syn2x_on']); r['earn']=int(r['earn']); r['y']=int(r['date'][:4])
rng=np.random.default_rng(20261110)
def ci_boot(v,B=20000):
    v=np.asarray(v); n=len(v)
    idx=rng.integers(0,n,size=(B,n)) if n*B<4e7 else None
    if idx is None:
        ms=np.array([v[rng.integers(0,n,n)].mean() for _ in range(B)])
    else: ms=v[idx].mean(axis=1)
    return np.percentile(ms,[2.5,5,95,97.5])
def ci_yearblock(rows,B=20000):
    ys=sorted(set(r['y'] for r in rows))
    s={y:sum(r['u'] for r in rows if r['y']==y) for y in ys}; c={y:sum(1 for r in rows if r['y']==y) for y in ys}
    S=np.array([s[y] for y in ys]); C=np.array([c[y] for y in ys])
    idx=rng.integers(0,len(ys),size=(B,len(ys)))
    ms=S[idx].sum(axis=1)/C[idx].sum(axis=1)
    return np.percentile(ms,[2.5,5,95,97.5]),len(ys)
def rep(lab,rows):
    v=np.array([r['u'] for r in rows]); n=len(v)
    if n<5: print(lab,'n',n); return
    m=v.mean(); s=v.std(ddof=1); se=s/math.sqrt(n)
    b=ci_boot(v); (yb,ny)=ci_yearblock(rows)
    g98=np.mean(np.log1p(0.98*v)); g25=np.mean(np.log1p(0.25*v))
    print('%-34s n %4d  mean %+6.3f%%  sd %5.2f%%  t %+5.2f | 95%% CI t-based [%+.3f, %+.3f]  iid-boot [%+.3f, %+.3f]  year-block(%d yrs) [%+.3f, %+.3f] (90%%: [%+.3f, %+.3f]) | win %.1f%% | log-growth/night at f=0.98 %+.3f%%, at f=0.25 %+.4f%% | worst %+.1f%% best %+.1f%%'%(
        lab,n,100*m,100*s,m/se,100*(m-1.96*se),100*(m+1.96*se),100*b[0],100*b[3],ny,100*yb[0],100*yb[3],100*yb[1],100*yb[2],100*np.mean(v>0),100*g98,100*g25,100*v.min(),100*v.max()))
for lab,a,b in (('2015-2026',2015,2026),('2000-2014',2000,2014),('2000-2026',2000,2026),('2021-2026',2021,2026),('2015-2020',2015,2020)):
    sub=[r for r in R if a<=r['y']<=b]
    print('\n== %s (2x NVDA overnight net 9bp; state = QQQ close vs mean of its previous 199 closes) =='%lab)
    rep('ALL nights',sub)
    rep('DOWN (QQQ below line)',[r for r in sub if r['state']=='DOWN'])
    rep('UP (QQQ at/above line)',[r for r in sub if r['state']=='UP'])
    if a>=2015:
        rep('DOWN ex-earnings',[r for r in sub if r['state']=='DOWN' and not r['earn']])
        rep('UP ex-earnings',[r for r in sub if r['state']=='UP' and not r['earn']])
        rep('ALL ex-earnings',[r for r in sub if not r['earn']])
        print('   earnings nights in DOWN:',[(r['date'],round(100*r['u'],1)) for r in sub if r['state']=='DOWN' and r['earn']])
    # DOWN nights by year
    print('   DOWN nights by year:',' '.join('%d:%d(%+.2f)'%(y,len(v),100*np.mean(v)) for y in range(a,b+1) for v in [[r['u'] for r in sub if r['y']==y and r['state']=='DOWN']] if len(v)))
# difference DOWN - UP
for lab,a,b in (('2015-2026',2015,2026),('2000-2014',2000,2014)):
    d=np.array([r['u'] for r in R if a<=r['y']<=b and r['state']=='DOWN']); u=np.array([r['u'] for r in R if a<=r['y']<=b and r['state']=='UP'])
    diff=d.mean()-u.mean(); se=math.sqrt(d.var(ddof=1)/len(d)+u.var(ddof=1)/len(u))
    print('%s DOWN mean - UP mean = %+.3f%% (se %.3f, t %.2f)'%(lab,100*diff,100*se,diff/se))
# spells
st=[r['state'] for r in R]; sp=0
for i in range(1,len(st)):
    if st[i]=='DOWN' and st[i-1]!='DOWN': sp+=1
print('DOWN spells 2000-2026:',sp,' share of nights DOWN: 2000-14 %.1f%%, 2015-26 %.1f%%'%(100*np.mean([r['state']=='DOWN' for r in R if r['y']<=2014]),100*np.mean([r['state']=='DOWN' for r in R if r['y']>=2015])))
# current spell
i=len(R)-1; k=0
while R[i]['state']=='DOWN': k+=1; i-=1
print('current DOWN spell length (nights to 2026-11-09):',k,' last 12 states:',[(r['date'][5:],r['state'],r['dist'][:7]) for r in R[-12:]])
# near-line nights: |dist|<1%
for lab,a,b in (('2015-2026',2015,2026),('2000-2014',2000,2014)):
    sub=[r for r in R if a<=r['y']<=b and r['state']=='DOWN']
    rep(lab+' DOWN within 2% of line',[r for r in sub if float(r['dist'])>-0.02])
    rep(lab+' DOWN more than 2% below',[r for r in sub if float(r['dist'])<=-0.02])
