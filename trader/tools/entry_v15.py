# usage: python3 entry_v15.py NIGHT YYYYMMDD NVDL_ask NVDL_last NVDX_ask NVDX_last E [--dry]
# RULES_v3 §3 v1.5: core NVDA-2x; choose a (NVDL), b (NVDX) maximizing a*lim*m + b*lim*m s.t. cost <= 0.98E
import sys,math,json,uuid,datetime
n=sys.argv[1]; day=sys.argv[2]
na,nl,xa,xl,E=map(float,sys.argv[3:8]); dry='--dry' in sys.argv
M={'NVDL':0.0046,'NVDX':0.0042}
def lim(ask,last):
    l=math.ceil((ask+max(0.02,0.0015*ask))*100)/100
    assert l<=last*1.004, f"limit {l} > last*1.004 {last*1.004:.4f}"
    return l
ln=lim(na,nl); lx=lim(xa,xl); cap=0.98*E
best=None
for a in range(0,int(cap//ln)+1):
    for b in range(0,int((cap-a*ln)//lx)+1):
        cost=a*ln+b*lx
        if cost>cap or a+b==0: continue
        ev=a*ln*M['NVDL']+b*lx*M['NVDX']
        key=(round(ev,4),a)
        if best is None or key>best[0]: best=(key,a,b,cost)
_,a,b,cost=best
print(f"NVDL lim {ln:.2f} x{a}  NVDX lim {lx:.2f} x{b}  cost {cost:.2f} = {cost/E*100:.1f}% of E {E:.2f}  EV ${best[0][0]:.3f}/night")
assert cost<=cap
if dry: sys.exit()
t=datetime.datetime.now(datetime.timezone.utc).isoformat()
for sym,l,q in (("NVDL",ln,a),("NVDX",lx,b)):
    if q==0: continue
    d={"t":t,"coid":f"T3X-{day}-{n}-{sym}-E","ref_id":str(uuid.uuid4()),"sym":sym,"side":"buy","qty":q,"type":"limit","limit":l,"tif":"gfd","hours":"regular_hours","rule":"RULES_v3 §3 v1.5 NVDA-2x core sizing + §4 entry 15:52 marketable limit","note":f"night {n} entry"}
    open('/home/user/test-trading/trader/orders.jsonl','a').write(json.dumps(d)+"\n")
    print(sym,q,l,d['ref_id'])
