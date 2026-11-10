import json, collections
legs=json.load(open('legs.json'))
s15=s16=sf=0
print(f"{'N':>3} {'sym':5} q {'fill$':>7} {'fill%':>7} {'col15':>7} {'col16':>7}  col16-is")
groups=collections.defaultdict(lambda:[0,0,0,0])
for l in legs:
    d=l['ours_d']; p=100*l['ours']
    def close(a,b,tol=0.011): return abs(a-b)<=tol
    k16='dollars' if close(l['c16'],d) else ('percent' if close(l['c16'],p,0.02) else 'OTHER')
    k15='dollars' if close(l['c15'],d) else ('percent' if close(l['c15'],p,0.02) else 'OTHER')
    # percent-of-equity style? 
    flag=''
    if k16!='dollars': flag='<-- col16 not dollars (%s); col15=%s'%(k16,k15)
    print(f"{l['n']:3d} {l['sym']:5} {l['q']} {d:7.2f} {p:7.2f} {l['c15']:7.2f} {l['c16']:7.2f}  {flag}")
    s15+=l['c15']; s16+=l['c16']; sf+=d
    g=groups[(k15,k16)]; g[0]+=1; g[1]+=d; g[2]+=l['c15']; g[3]+=l['c16']
print('sum fills $',round(sf,3),'sum col15',round(s15,2),'sum col16',round(s16,2))
for k,g in groups.items(): print(k,'legs',g[0],'fill$',round(g[1],2),'col15 sum',round(g[2],2),'col16 sum',round(g[3],2))
# by night range
for a,b in ((1,7),(8,11),(12,44)):
    ls=[l for l in legs if a<=l['n']<=b]
    print(f"N{a}-{b}: legs {len(ls)} fill$ {sum(l['ours_d'] for l in ls):+.2f} col15 {sum(l['c15'] for l in ls):+.2f} col16 {sum(l['c16'] for l in ls):+.2f}")
# what is col16 in N1-7? test hypotheses
print('\nN1-7 col16 hypotheses:')
for l in legs:
    if l['n']<=7:
        lim=float(l['lim']) if l['lim'] else float('nan')
        print(l['n'],l['sym'],'col15',l['c15'],'col16',l['c16'],'fill$',round(l['ours_d'],3),'model$ (O-C)*q',round((l['O']-l['C'])*l['q'],3),'pct',round(100*l['ours'],2),'pct_of_equity98.75?',round(100*l['ours_d']/98.75,2), 'vs limit',round((l['xf']-lim)*l['q'],3))
