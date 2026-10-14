# usage: python3 daysell.py N YYYYMMDD QTY TZA_bid [--reprice]   (15:49 close; TP must be cancelled+verified first)
import sys,math,json,uuid,datetime
n=sys.argv[1]; day=sys.argv[2]; q=int(sys.argv[3]); b=float(sys.argv[4]); rp='--reprice' in sys.argv
lim=math.floor((b*(1-0.003) if rp else b-max(0.02,0.0015*b))*100)/100
d={"t":datetime.datetime.now(datetime.timezone.utc).isoformat(),"coid":f"T3X-{day}-D{n}-TZA-S{'2' if rp else ''}","ref_id":str(uuid.uuid4()),"sym":"TZA","side":"sell","qty":q,"type":"limit","limit":lim,"tif":"gfd","hours":"regular_hours","rule":"RULES_v3 §11 15:49 day-leg close "+("re-price bid-0.3%" if rp else "bid-max(0.02,0.15%)"),"note":f"day leg #{n} close"}
open('/home/user/test-trading/trader/orders.jsonl','a').write(json.dumps(d)+"\n"); print("TZA sell",q,"@",lim,"ref",d['ref_id'])
