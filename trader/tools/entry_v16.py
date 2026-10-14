# RULES_v3 §3 v1.6 sizing — NVDL first, NVDX filler. Two steps:
#   python3 entry_v16.py nvdl NIGHT YYYYMMDD NVDL_ask NVDL_last E [--dry]          -> a = max whole NVDL with a*lim <= 0.98E
#   python3 entry_v16.py nvdx NIGHT YYYYMMDD NVDX_ask NVDX_last E SPENT [--dry]    -> b = max whole NVDX with SPENT + b*lim <= 0.98E
# SPENT = actual NVDL fill cost (qty*avg) after the NVDL order fills (or a*lim_NVDL if planning).
import sys,math,json,uuid,datetime
mode=sys.argv[1]; n=sys.argv[2]; day=sys.argv[3]; ask,last,E=map(float,sys.argv[4:7]); dry='--dry' in sys.argv
spent=float(sys.argv[7]) if mode=='nvdx' and len(sys.argv)>7 and not sys.argv[7].startswith('--') else 0.0
lim=math.ceil((ask+max(0.02,0.0015*ask))*100)/100
assert lim<=last*1.004, f"limit {lim} > last*1.004 {last*1.004:.4f}"
cap=0.98*E
q=int((cap-spent)//lim) if cap>spent else 0
sym='NVDL' if mode=='nvdl' else 'NVDX'
print(f"{sym} lim {lim:.2f} x{q}  cost {q*lim:.2f}  total {spent+q*lim:.2f} = {(spent+q*lim)/E*100:.1f}% of E {E:.2f} (cap {cap:.2f})")
if dry or q==0: sys.exit()
d={"t":datetime.datetime.now(datetime.timezone.utc).isoformat(),"coid":f"T3X-{day}-{n}-{sym}-E","ref_id":str(uuid.uuid4()),"sym":sym,"side":"buy","qty":q,"type":"limit","limit":lim,"tif":"gfd","hours":"regular_hours","rule":"RULES_v3 §3 v1.6 NVDL-first sizing + §4 entry 15:52 marketable limit","note":f"night {n} entry ({'core' if sym=='NVDL' else 'filler'})"}
open('/home/user/test-trading/trader/orders.jsonl','a').write(json.dumps(d)+"\n"); print(sym,q,lim,d['ref_id'])
