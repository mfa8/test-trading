import json, csv, math, random, sys
from collections import defaultdict
PM='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/'
d=json.load(open(PM+'day_0908_1110.json'))
bars={}
for r in d['data']['results']:
    s=r['symbol']; bars[s]={}
    for b in r['bars']:
        dt=b['begins_at'][:10]
        bars[s][dt]={'o':float(b['open_price']),'c':float(b['close_price']),'h':float(b['high_price']),'l':float(b['low_price']),'v':float(b['volume']),'interp':b.get('interpolated',False),'session':b.get('session')}
dates=sorted(bars['NVDL'].keys())
print('sessions',len(dates),dates[0],dates[-1])
for s in bars:
    bad=[(k,v['v'],v['interp']) for k,v in bars[s].items() if v['v']==0 or v['interp']]
    print(s,len(bars[s]),'bad',bad)
legs=[]
for row in csv.reader(open(PM+'trades.csv')):
    if not row or not row[0].startswith('T3X-N'): continue
    nid=int(row[0][5:]); ed=row[1]; sym=row[2]; ef=float(row[8]); q=float(row[9]); xf=float(row[13]); pnlcol=row[16]; pctcol=row[15]
    i=dates.index(ed); xd=dates[i+1]
    c=bars[sym][ed]['c']; o=bars[sym][xd]['o']
    assert not bars[sym][ed]['interp'] and not bars[sym][xd]['interp'], (sym,ed,xd)
    inv=ef*q
    ours=xf/ef-1; model=o/c-1; ent=c/ef-1; ext=xf/o-1
    cross=ours-model-ent-ext
    legs.append(dict(n=nid,ed=ed,xd=xd,sym=sym,ef=ef,q=q,xf=xf,c=c,o=o,inv=inv,ours=ours*inv,model=model*inv,ent=ent*inv,ext=ext*inv,cross=cross*inv,
                     ours_p=ours,model_p=model,ent_p=ent,ext_p=ext,pnlcol=float(pnlcol),
                     # alt decomposition: exact dollars
                     model_d=(o-c)*q, ent_d=(c-ef)*q, ext_d=(xf-o)*q, tot_d=(xf-ef)*q))
json.dump(legs,open('c1_legs.json','w'),indent=0)
def S(k,L=legs): return sum(x[k] for x in L)
print('legs',len(legs),'nights',len(set(x['n'] for x in legs)),'invested',round(S('inv'),2))
print('TOTAL ours %.3f model %.3f entry %.3f exit %.3f cross %.3f'%(S('ours'),S('model'),S('ent'),S('ext'),S('cross')))
print('ALT exact-dollar (no cross): tot %.3f model %.3f entry %.3f exit %.3f'%(S('tot_d'),S('model_d'),S('ent_d'),S('ext_d')))
print('pct of invested: ours %.3f model %.3f ent %.3f ext %.3f'%tuple(100*S(k)/S('inv') for k in ['ours','model','ent','ext']))
print('pnl column sum %.2f'%S('pnlcol'))
for lab,f in [('N1-24',lambda x:x['n']<=24),('N25-44',lambda x:x['n']>=25),('ex N43',lambda x:x['n']!=43),('ex N43,N44',lambda x:x['n']<43),('N43',lambda x:x['n']==43),('N44',lambda x:x['n']==44)]:
    L=[x for x in legs if f(x)]
    print(lab,len(L),'ours %.2f model %.2f ent %.2f ext %.2f cross %.2f'%(S('ours',L),S('model',L),S('ent',L),S('ext',L),S('cross',L)), 'ALT model %.2f ent %.2f ext %.2f'%(S('model_d',L),S('ent_d',L),S('ext_d',L)))
print('BY SYMBOL')
for s in ['NVDL','NVDX','METU','AAPU','AMZU']:
    L=[x for x in legs if x['sym']==s]
    print(s,len(L),'ours %.2f model %.2f ent %.2f ext %.2f | ALT ent %.2f ext %.2f model %.2f'%(S('ours',L),S('model',L),S('ent',L),S('ext',L),S('ent_d',L),S('ext_d',L),S('model_d',L)))
L=[x for x in legs if x['sym'] in('NVDL','NVDX')]
print('NVDA2x legs',len(L),'ent %.2f ext %.2f'%(S('ent',L),S('ext',L)))
L=[x for x in legs if x['sym'] not in('NVDL','NVDX')]
print('other legs',len(L),'ent %.2f ext %.2f'%(S('ent',L),S('ext',L)))
# by night
nights=defaultdict(list)
for x in legs: nights[x['n']].append(x)
N=[]
for n in sorted(nights):
    L=nights[n]; inv=S('inv',L)
    N.append(dict(n=n,ed=L[0]['ed'],xd=L[0]['xd'],inv=inv,ours=S('ours',L)/inv,model=S('model',L)/inv,ent=S('ent',L)/inv,ext=S('ext',L)/inv,ours_d=S('ours',L),ext_d=S('ext',L),ent_d=S('ent',L),model_d=S('model',L),
        nv=any(x['sym'] in('NVDL','NVDX') for x in L)))
json.dump(N,open('c1_nights.json','w'))
def stats(v):
    n=len(v); m=sum(v)/n; sd=math.sqrt(sum((a-m)**2 for a in v)/(n-1)); return m,sd,m/(sd/math.sqrt(n)),n
def boot(v,B=20000,seed=1):
    r=random.Random(seed); n=len(v); ms=[]
    for _ in range(B):
        ms.append(sum(v[r.randrange(n)] for _ in range(n))/n)
    ms.sort(); return ms[int(0.05*B)],ms[int(0.95*B)]
for lab,sel in [('all',N),('N25-44',[x for x in N if x['n']>=25]),('N1-24',[x for x in N if x['n']<=24]),('N25-42',[x for x in N if 25<=x['n']<=42]),('N1-42',[x for x in N if x['n']<=42])]:
    for k in ['ext','ent','ours','model']:
        v=[100*x[k] for x in sel]; m,sd,t,n=stats(v); lo,hi=boot(v)
        neg=sum(1 for a in v if a<0)
        srt=sorted(v); med=(srt[n//2] if n%2 else (srt[n//2-1]+srt[n//2])/2)
        print('%-8s %-5s n=%d mean %.3f sd %.3f t %.2f boot90 [%.3f,%.3f] median %.3f neg %d'%(lab,k,n,m,sd,t,lo,hi,med,neg))
# worst nights
for x in sorted(N,key=lambda x:x['ours_d'])[:6]: print('N%02d %s ours %.2f model %.2f ext %.2f ent %.2f'%(x['n'],x['ed'],x['ours_d'],x['model_d'],x['ext_d'],x['ent_d']))
# leg-level t for NVDA era exit
L=[100*x['ext_p'] for x in legs if x['n']>=25]; print('leg-level exit NVDA era',stats(L))
L=[100*x['ent_p'] for x in legs]; print('leg-level entry all',stats(L))
L=[1e4*x['ext_p'] for x in legs if x['sym']=='NVDL']; print('NVDL exit legs bp',stats(L),min(L),max(L))
L=[1e4*x['ext_p'] for x in legs]; print('all exit legs bp',stats(L))
L=[-1e4*x['ent_p'] for x in legs if x['sym']=='NVDL']; print('NVDL entry legs bp (fill above close)',stats(L))
