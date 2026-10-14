# usage: python3 dayleg.py N YYYYMMDD TZA_ask TZA_last cash E [--dry]
# RULES_v3 §11 (v1.4 sizing): lim=ceil(ask+max(0.02,0.15%)) <= last*1.004; q=floor(0.95*cash/lim); top-up if q*lim<0.85E and (q+1)*lim<=0.98*cash
import sys,math,json,uuid,datetime
n=sys.argv[1]; day=sys.argv[2]; a,l0,cash,E=map(float,sys.argv[3:7]); dry='--dry' in sys.argv
lim=math.ceil((a+max(0.02,0.0015*a))*100)/100
assert lim<=l0*1.004, f"limit {lim} > last*1.004"
q=math.floor(0.95*cash/lim)
if q*lim<0.85*E and (q+1)*lim<=0.98*cash: q+=1
assert q>=1 and q*lim<=cash
print(f"TZA buy {q} @ {lim} cost {q*lim:.2f} ({q*lim/E*100:.1f}% E)")
if dry: sys.exit()
d={"t":datetime.datetime.now(datetime.timezone.utc).isoformat(),"coid":f"T3X-{day}-D{n}-TZA-B","ref_id":str(uuid.uuid4()),"sym":"TZA","side":"buy","qty":q,"type":"limit","limit":lim,"tif":"gfd","hours":"regular_hours","rule":"RULES_v3 §11 day leg 09:32 marketable limit (v1.4 sizing)","note":f"day leg #{n}"}
open('/home/user/test-trading/trader/orders.jsonl','a').write(json.dumps(d)+"\n"); print(d['ref_id'])
