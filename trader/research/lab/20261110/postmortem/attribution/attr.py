import json, csv, sys, collections, random, math
P='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/'
d=json.load(open(P+'day_0908_1110.json'))
bars={}
for r in d['data']['results']:
    bb=collections.OrderedDict()
    for x in r['bars']:
        if x.get('interpolated') or x['volume']==0: continue
        bb[x['begins_at'][:10]]={'o':float(x['open_price']),'c':float(x['close_price']),'h':float(x['high_price']),'l':float(x['low_price']),'v':x['volume']}
    bars[r['symbol']]=bb
def nxt(sym,date):
    ks=list(bars[sym].keys())
    i=ks.index(date)
    return ks[i+1]
legs=[]
for row in csv.reader(open(P+'trades.csv')):
    if not row or not row[0].startswith('T3X-N'): continue
    n=int(row[0][5:])
    date=row[1]; sym=row[2]
    ef=float(row[8]); q=int(row[9]); xf=float(row[13])
    c15=float(row[15]); c16=float(row[16])
    nd=nxt(sym,date)
    C=bars[sym][date]['c']; O=bars[sym][nd]['o']
    inv=ef*q
    L=dict(n=n,date=date,nd=nd,sym=sym,ef=ef,q=q,xf=xf,C=C,O=O,inv=inv,
           ours=xf/ef-1, model=O/C-1, entry=C/ef-1, exit=xf/O-1,
           et=row[7],xt=row[12],c15=c15,c16=c16,lim=row[10])
    L['ours_d']=(xf-ef)*q; L['model_d']=inv*L['model']; L['entry_d']=inv*L['entry']; L['exit_d']=inv*L['exit']
    L['cross_d']=L['ours_d']-L['model_d']-L['entry_d']-L['exit_d']
    legs.append(L)
json.dump(legs,open(P+'attribution/legs.json','w'),indent=1)
if __name__=='__main__':
    print('legs',len(legs),'nights',len(set(l['n'] for l in legs)))
    print(f"{'N':>3} {'date':10} {'sym':5} {'q':>1} {'entry':>8} {'close':>7} {'open':>7} {'exit':>8} {'ours%':>7} {'mod%':>7} {'ent%':>6} {'ext%':>6} {'ours$':>7} {'mod$':>7} {'ent$':>6} {'ext$':>6} {'x$':>6} xt")
    for l in legs:
        print(f"{l['n']:3d} {l['date']} {l['sym']:5} {l['q']} {l['ef']:8.4f} {l['C']:7.3f} {l['O']:7.3f} {l['xf']:8.4f} {100*l['ours']:7.2f} {100*l['model']:7.2f} {100*l['entry']:6.2f} {100*l['exit']:6.2f} {l['ours_d']:7.2f} {l['model_d']:7.2f} {l['entry_d']:6.2f} {l['exit_d']:6.2f} {l['cross_d']:6.3f} {l['xt']}")
    def tot(ls,label):
        s=lambda k: sum(l[k] for l in ls)
        inv=s('inv')
        print(f"{label:28} legs={len(ls):3d} nights={len(set(l['n'] for l in ls)):2d} inv=${inv:9.2f} ours={s('ours_d'):8.3f} model={s('model_d'):8.3f} entry={s('entry_d'):7.3f} exit={s('exit_d'):7.3f} cross={s('cross_d'):7.3f} | pct of inv: ours {100*s('ours_d')/inv:6.3f} model {100*s('model_d')/inv:6.3f} entry {100*s('entry_d')/inv:6.3f} exit {100*s('exit_d')/inv:6.3f}")
    tot(legs,'ALL')
    tot([l for l in legs if l['n']<=24],'era1 N1-24')
    tot([l for l in legs if l['n']>=25],'era2 N25-44')
    for m in ['2026-09','2026-10','2026-11']:
        tot([l for l in legs if l['date'].startswith(m)],'entry-month '+m)
    for m in ['2026-09','2026-10','2026-11']:
        tot([l for l in legs if l['nd'].startswith(m)],'exit-month '+m)
    for s in sorted(set(l['sym'] for l in legs)):
        tot([l for l in legs if l['sym']==s],'sym '+s)
