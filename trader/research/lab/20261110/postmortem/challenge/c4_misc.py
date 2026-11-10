import json, math, statistics as st, random
legs=json.load(open('c1_legs.json')); N=json.load(open('c1_nights.json')); rows=json.load(open('c3_rows.json'))
PM='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/'
def S(v):
    m=st.mean(v); s=st.stdev(v); return m,s,m/(s/math.sqrt(len(v))),len(v)
# (c) combined timing by night
tim=[100*(x['ext']+x['ent']) for x in N]
print('combined timing by night %% : mean %.3f sd %.3f t %.2f n %d'%S(tim))
tim42=[100*(x['ext']+x['ent']) for x in N if x['n']<=42]; print(' N1-42: mean %.3f sd %.3f t %.2f n %d'%S(tim42))
# NVDA-2x-only nights (all legs NVDA 2x): N25-44 ; plus NVDA-2x legs across all nights
from collections import defaultdict
byn=defaultdict(list)
for x in legs:
    if x['sym'] in('NVDL','NVDX'): byn[x['n']].append(x)
v_ext=[];v_ent=[];v_tim=[]
for n,L in sorted(byn.items()):
    inv=sum(x['inv'] for x in L)
    v_ext.append(100*sum(x['ext'] for x in L)/inv); v_ent.append(100*sum(x['ent'] for x in L)/inv); v_tim.append(v_ext[-1]+v_ent[-1])
print('NVDA-2x legs by night: n',len(v_ext),'exit mean %.3f sd %.3f t %.2f'%S(v_ext)[:3],'| entry mean %.3f sd %.3f t %.2f'%S(v_ent)[:3],'| combined %.3f sd %.3f t %.2f'%S(v_tim)[:3], 'neg exit',sum(1 for a in v_ext if a<0))
# without last two
print('  w/o N43,N44: exit mean %.3f sd %.3f t %.2f'%S(v_ext[:-2])[:3],'combined %.3f sd %.3f t %.2f'%S(v_tim[:-2])[:3])
# SE of sums in dollars
inv=[x['inv'] for x in N]; avg_inv=st.mean(inv)
print('avg invested per night %.2f'%avg_inv)
md=[x['model_d'] for x in N]; print('model $ per night: sum %.2f, sd %.2f, SE of sum %.2f'%(sum(md),st.stdev(md),st.stdev(md)*math.sqrt(len(md))))
td=[x['ext_d']+x['ent_d'] for x in N]; print('timing $ per night: sum %.2f sd %.2f SE of sum %.2f'%(sum(td),st.stdev(td),st.stdev(td)*math.sqrt(len(td))))
# (b) NVDL daily open->close sd in window and c2c
d=json.load(open(PM+'day_0908_1110.json'))
bars={r['symbol']:{b['begins_at'][:10]:b for b in r['bars'] if not b.get('interpolated')} for r in d['data']['results']}
nv=bars['NVDL']; ds=sorted(nv)
oc=[float(nv[x]['close_price'])/float(nv[x]['open_price'])-1 for x in ds if '2026-09-10'<=x<='2026-11-10']
print('NVDL open->close in window: mean %.3f%% sd %.3f%% n %d'%(100*st.mean(oc),100*st.stdev(oc),len(oc)))
ex=[x['ext_p'] for x in legs if x['sym']=='NVDL']
print('NVDL exit-leg sd %.3f%% => variance share of first ~85s vs open->close day: %.3f'%(100*st.stdev(ex),(st.stdev(ex)/st.stdev(oc))**2))
print(' implied proportional drift for first 85s: %.1f bp'%(1e4*st.mean(oc)*(st.stdev(ex)/st.stdev(oc))**2))
# entry leg: 15:52->close
en=[-(x['ent_p']) for x in legs if x['sym']=='NVDL']
print('NVDL entry-leg sd %.3f%% var share %.3f implied drift %.1f bp'%(100*st.stdev(en),(st.stdev(en)/st.stdev(oc))**2,1e4*st.mean(oc)*(st.stdev(en)/st.stdev(oc))**2))
# does exit leg correlate with the rest-of-day move (open->close)? If first-minute move is part of intraday trend
pairs=[(x['ext_p'], float(nv[x['xd']]['close_price'])/float(nv[x['xd']]['open_price'])-1) for x in legs if x['sym']=='NVDL']
print('corr(exit leg, same-day open->close) NVDL legs: %.2f'%st.correlation([p[0] for p in pairs],[p[1] for p in pairs]))
# exit leg on days when day closed down vs up
dn=[p[0] for p in pairs if p[1]<0]; up=[p[0] for p in pairs if p[1]>=0]
print(' exit leg mean on down-days %.1f bp (n %d), up-days %.1f bp (n %d)'%(1e4*st.mean(dn),len(dn),1e4*st.mean(up),len(up)))
# (a) frequency of big overnight losses, 2x NVDA synthetic gross, ex-earnings
r15=[r for r in rows if r['d']>='2015' and not r['earn']]
yrs=len(r15)/252
for thr in (-0.10,-0.12,-0.145,-0.15):
    c=sum(1 for r in r15 if r['u']+0.0009<=thr); print('2x NVDA ex-earn nights <= %.1f%%: %d in %.1f yrs = %.2f/yr'%(100*thr,c,yrs,c/yrs))
r00=[r for r in rows if r['d']<'2015']
for thr in (-0.10,-0.145):
    c=sum(1 for r in r00 if r['u']+0.0009<=thr); print('2000-14 (incl earn) nights <= %.1f%%: %d in %.1f yrs = %.2f/yr'%(100*thr,c,len(r00)/252,c/(len(r00)/252)))
big=[(r['d'],round(100*(r['u']+0.0009),1),r['st']) for r in r15 if r['u']+0.0009<=-0.12]; print(big)
# N43's rank
u43=[r for r in rows if r['d']=='2026-11-06'][0]; print('N43 2x NVDA gross %.2f%% state %s'%(100*(u43['u']+0.0009),u43['st']))
# shadow window: open - fill bp for NVDL exits 10/22..11/10
sh=[x for x in legs if x['sym']=='NVDL' and '2026-10-22'<=x['xd']<='2026-11-10']
v=[1e4*(x['o']/x['xf']-1) for x in sh]; print('shadow mornings n %d open-fill mean %.1f sd %.1f t %.2f sum %.0f; last two %.0f'%(len(v),S(v)[0],S(v)[1],S(v)[2],sum(v),sum(v[-2:])), [round(a) for a in v])
# NVDL entries ef/c-1
v=[1e4*(x['ef']/x['c']-1) for x in legs if x['sym']=='NVDL']; print('NVDL entry fill/close-1 bp mean %.1f t %.2f'%(S(v)[0],S(v)[2]))
v=[1e4*(x['ef']/x['c']-1) for x in legs if x['sym']=='NVDL' and x['ed']>='2026-11-01']; print('Nov NVDL entry bp',[round(a) for a in v], 'mean %.0f'%st.mean(v))
# equity context
