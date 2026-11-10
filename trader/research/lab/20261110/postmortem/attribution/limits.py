import json, statistics as st, collections, math
legs=json.load(open('legs_orders.json'))
rows=[]
print(f"{'N':>3} {'sym':5} | {'Xlim':>7} {'Xfill':>8} {'f-lim c':>7} {'impBid':>7} {'open':>7} {'bid/O%':>7} {'fill/bid%':>9} {'exit%':>6} | {'Elim':>7} {'Efill':>8} {'lim-f c':>7} {'impAsk':>7} {'C/ask%':>7} {'ask/fill%':>9}")
for l in legs:
    x=[o for o in l['x_ord'] if isinstance(o[0],(int,float))]
    e=[o for o in l['e_ord'] if isinstance(o[0],(int,float))]
    first=x[0][0]; repriced=len(l['x_ord'])>1
    # implied bid from FIRST order limit: limit = bid - max(0.02,0.0015*bid)
    b=first/(1-0.0015)
    if 0.0015*b<0.02: b=first+0.02
    elim=e[0][0]
    a=elim/(1+0.0015)
    if 0.0015*a<0.02: a=elim-0.02
    r=dict(n=l['n'],sym=l['sym'],inv=l['inv'],xlim=first,xf=l['xf'],repriced=repriced,bid=b,O=l['O'],C=l['C'],
           drift=b/l['O']-1, slip=l['xf']/b-1, exit=l['exit'], elim=elim, ef=l['ef'], ask=a, e_drift=l['C']/a-1, e_slip=a/l['ef']-1, entry=l['entry'],
           model=l['model'])
    rows.append(r)
    print(f"{l['n']:3d} {l['sym']:5} | {first:7.2f} {l['xf']:8.4f} {100*(l['xf']-first):7.2f} {b:7.3f} {l['O']:7.3f} {100*r['drift']:7.2f} {100*r['slip']:9.2f} {100*l['exit']:6.2f}{'*R' if repriced else '  '} | {elim:7.2f} {l['ef']:8.4f} {100*(elim-l['ef']):7.2f} {a:7.3f} {100*r['e_drift']:7.2f} {100*r['e_slip']:9.2f}")
json.dump(rows,open('limits.json','w'),indent=1)
def agg(rs,label):
    inv=sum(r['inv'] for r in rs)
    d=sum(r['inv']*r['drift'] for r in rs); s=sum(r['inv']*r['slip'] for r in rs); x=sum(r['inv']*r['exit'] for r in rs)
    ed=sum(r['inv']*r['e_drift'] for r in rs); es=sum(r['inv']*r['e_slip'] for r in rs); en=sum(r['inv']*r['entry'] for r in rs)
    atlim=sum(1 for r in rs if not r['repriced'] and r['xf']-r['xlim']<=0.0101)
    print(f"{label:22} legs {len(rs):2d} | EXIT ${x:+.2f} = open->09:31 implied bid ${d:+.2f} ({100*d/inv:+.3f}%) + fill vs implied bid ${s:+.2f} ({100*s/inv:+.3f}%) [+cross {x-d-s:+.2f}] | first-order fills at limit(+<=1c): {atlim}/{sum(1 for r in rs if not r['repriced'])}, repriced {sum(1 for r in rs if r['repriced'])} | ENTRY ${en:+.2f} = ask->close ${ed:+.2f} + fill vs implied ask ${es:+.2f}")
agg(rows,'ALL')
agg([r for r in rows if r['n']<=24],'era1')
agg([r for r in rows if r['n']>=25],'era2')
agg([r for r in rows if r['n']>=43],'N43-44')
agg([r for r in rows if 25<=r['n']<=42],'era2 excl 43-44')
agg([r for r in rows if r['sym'] in('NVDL','NVDX')],'NVDA2x all')
agg([r for r in rows if r['sym'] not in('NVDL','NVDX')],'others')
# distribution of fill - limit in bp of price, non-repriced exits
nr=[r for r in rows if not r['repriced']]
v=[1e4*(r['xf']/r['xlim']-1) for r in nr]
print('exit fill above first limit, bp: mean %.1f median %.1f; share within 1c of limit %.2f; share >= ~15bp above limit (i.e. at or above the quoted bid) %.2f'%(st.mean(v),st.median(v),sum(1 for r in nr if r['xf']-r['xlim']<=0.0101)/len(nr), sum(1 for x in v if x>=14)/len(v)))
for lab,sel in (('era1',lambda r:r['n']<=24),('era2',lambda r:r['n']>=25),('N36-44',lambda r:r['n']>=36)):
    q=[r for r in nr if sel(r)]
    v=[1e4*(r['xf']/r['xlim']-1) for r in q]
    print(f"  {lab}: n {len(q)} mean {st.mean(v):.1f}bp median {st.median(v):.1f}bp at-limit {sum(1 for r in q if r['xf']-r['xlim']<=0.0101)}/{len(q)}  fill>=implied bid {sum(1 for r in q if r['xf']>=r['bid']-0.006)}/{len(q)}")
ev=[1e4*(r['elim']/r['ef']-1) for r in rows]
print('entry: limit above fill, bp: mean %.1f median %.1f; fills at limit (within 1c): %d/%d; fill<=implied ask: %d/%d'%(st.mean(ev),st.median(ev),sum(1 for r in rows if r['elim']-r['ef']<=0.0101),len(rows),sum(1 for r in rows if r['ef']<=r['ask']+0.006),len(rows)))
