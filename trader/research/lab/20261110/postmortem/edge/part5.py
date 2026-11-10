import sys, math
import numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge')
import sim as S
U,UPs,EARN,YEAR=S.U,S.UPs,S.EARN,S.YEAR
E=82.41
def dollars(lab,ret):
    ret=np.asarray(ret); m=ret.mean(); s=ret.std(ddof=1); n=len(ret)
    # rolling 21-night compounded
    lr=np.log1p(ret); cs=np.concatenate([[0],np.cumsum(lr)]); r21=np.expm1(cs[21:]-cs[:-21])
    q=np.percentile(r21,[5,25,50,75,95])
    print('%-52s n %4d | per night: mean %+.3f%% = $%+.3f, sd %.2f%% = $%.2f, 5th..95th $%+.2f..$%+.2f | per 21 nights: mean $%+.2f, sd(sqrt rule) $%.2f, rolling-21 5/25/50/75/95: $%+.1f %+.1f %+.1f %+.1f %+.1f | P(night>0) %.0f%%  P(21-night>0) %.0f%%'%(
        lab,n,100*m,E*m,100*s,E*s,E*np.percentile(ret,5),E*np.percentile(ret,95),E*(np.expm1(21*np.mean(lr))),E*s*math.sqrt(21),E*q[0],E*q[1],E*q[2],E*q[3],E*q[4],100*np.mean(ret>0),100*np.mean(r21>0)))
for lab,lo,hi,bo in (('2015-2026',2015,2026,True),('2000-2014',2000,2014,False),('2000-2026',2000,2026,False)):
    m=(YEAR>=lo)&(YEAR<=hi)
    size=np.where(UPs,0.98,0.25)
    if bo: size=np.where(EARN,0.0,size)
    print('\n== %s history, account of $%.2f =='%(lab,E))
    dollars('present rules, no pause (trend size%s)'%(', earnings cash' if bo else ''),(size*U)[m])
    mu=m&UPs&(~EARN if bo else True); md=m&(~UPs)&(~EARN if bo else True)
    dollars('UP nights at 0.98',0.98*U[mu])
    dollars('DOWN nights at 0.25 (also the PAUSE size)',0.25*U[md])
    dollars('PAUSE in an UP market: UP nights at 0.25',0.25*U[mu])
    dollars('always 0.98 (old sizing)',(np.where(EARN&bo,0,0.98)*U)[m])
# edge scenarios at full size, 2015-26 UP ex-earnings sd
print('\nFull size (0.98 of $%.2f = $%.2f invested), per-night and per-21-night expectation under different unit edges (sd per night taken as 3.2%% of invested):'%(E,0.98*E))
for lab,e in (('rules planning edge +0.30% gross (-9bp cost)',0.0030-0.0009),('2015-26 all nights +0.246% (includes earnings nights the account skips)',0.00246),('2015-26 ex-earnings +0.148%',0.00148),('2000-2014 +0.094%',0.00094),('last 250 nights ex-earnings +0.134%',0.00134),('zero edge after costs',0.0),('2015-26 ex-earnings less the live 28bp fill gap',0.00148-0.0028),('2015-26 ex-earnings less a 10bp fill gap',0.00148-0.0010)):
    inv=0.98*E; print('  %-70s per night $%+.3f | per month (21) $%+.2f | sd night $%.2f, sd month $%.2f | nights to see it at t=2: %s'%(lab,inv*e,inv*e*21,inv*0.032,inv*0.032*math.sqrt(21),('%.0f'%((2*0.032/abs(e))**2) if e!=0 else 'never')))
# how unusual is the live result
print('\nHow unusual is a 44-night loss like the live one?')
for lab,lo,hi in (('2015-2026',2015,2026),('2000-2026',2000,2026)):
    m=(YEAR>=lo)&(YEAR<=hi)
    for f,desc in ((0.88,'official close->open, 0.88 invested, earnings nights in cash'),):
        r=(np.where(EARN,0,f)*U)[m]; lr=np.log1p(r); cs=np.concatenate([[0],np.cumsum(lr)]); r44=np.expm1(cs[44:]-cs[:-44])
        print('  %s %s: 44-night return 5/25/50/75/95 pct = %s ; share of windows <= -9.7%% (the live close->open part): %.1f%% ; <= -20%% (live total incl. fill gap): %.1f%%'%(lab,desc,' '.join('%+.1f%%'%(100*x) for x in np.percentile(r44,[5,25,50,75,95])),100*np.mean(r44<=-0.097),100*np.mean(r44<=-0.20)))
# worst single nights at full size
m=(YEAR>=2015)&(~EARN)
print('\nNon-earnings nights 2015-26 with 2x overnight <= -10%%: %d of %d (%.2f%%), <= -14%%: %d ; 2000-14 all nights <= -10%%: %d of %d, <= -14%%: %d'%(np.sum(U[m]<=-0.10),m.sum(),100*np.mean(U[m]<=-0.10),np.sum(U[m]<=-0.14),np.sum(U[YEAR<=2014]<=-0.10),np.sum(YEAR<=2014),np.sum(U[YEAR<=2014]<=-0.14)))
