import json, re, collections, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/attribution')
legs=json.load(open('legs.json'))
rows=[json.loads(l) for l in open('/home/user/test-trading/trader/orders.jsonl') if l.strip()]
ords=collections.defaultdict(list)
others=[]
for i,o in enumerate(rows):
    c=o.get('coid','')
    m=re.match(r'T3X-(\d{8})-(\d+)-([A-Z]+)-([A-Z0-9]+)',c)
    t=o.get('t') or o.get('ts') or o.get('utc') or ''
    if m:
        d=m.group(1); d=f"{d[:4]}-{d[4:6]}-{d[6:]}"
        ords[(d,m.group(3),m.group(4)[0])].append((i,o,t,m.group(2),m.group(4)))
    elif t>='2026-09-09' or 'T3X' in c:
        others.append((i,o))
print('non-standard T3X-era lines:',len(others))
for i,o in others: print(' ',i,json.dumps(o)[:260])
suffixes=collections.Counter(k[2] for k in ords for _ in ords[k])
print('suffix kinds',suffixes)
used=set()
out=[]
for l in legs:
    e=ords.get((l['date'],l['sym'],'E'),[])
    x=ords.get((l['nd'],l['sym'],'X'),[])
    l['e_ord']=[(o.get('limit'),o.get('qty'),t,nn,sfx,o.get('type')) for i,o,t,nn,sfx in e]
    l['x_ord']=[(o.get('limit'),o.get('qty'),t,nn,sfx,o.get('type')) for i,o,t,nn,sfx in x]
    for i,o,t,nn,sfx in e+x: used.add(i)
    out.append(l)
print()
print(f"{'N':>3} {'sym':5} q | entry: fill   limit(s) qty  t                 | exit: fill   limit(s) qty t")
ne=nx=0; viol=[]
for l in out:
    es=' ; '.join(f"{a} x{b} {c[11:19]} n{d} {s}" for a,b,c,d,s,ty in l['e_ord']) or 'NO INTENT'
    xs=' ; '.join(f"{a} x{b} {c[11:19]} n{d} {s}" for a,b,c,d,s,ty in l['x_ord']) or 'NO INTENT'
    print(f"{l['n']:3d} {l['sym']:5} {l['q']} | E {l['ef']:8.4f} [{es}] | X {l['xf']:8.4f} [{xs}]")
json.dump(out,open('legs_orders.json','w'),indent=1)
# unmatched T3X orders
print('\nUNMATCHED T3X intent lines (not tied to an overnight leg in trades.csv):')
for k,v in sorted(ords.items()):
    for i,o,t,nn,sfx in v:
        if i not in used:
            print(' ',k,nn,sfx,json.dumps({kk:vv for kk,vv in o.items() if kk not in('ref_id','rule','hours','tif','coid')})[:230])
