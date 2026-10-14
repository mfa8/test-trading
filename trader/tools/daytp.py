# usage: python3 daytp.py N YYYYMMDD ENTRY QTY   -> TP limit ceil(entry*1.01), GFD
import sys,math,json,uuid,datetime
n=sys.argv[1]; day=sys.argv[2]; e=float(sys.argv[3]); q=int(sys.argv[4])
tp=math.ceil(e*1.01*100)/100
d={"t":datetime.datetime.now(datetime.timezone.utc).isoformat(),"coid":f"T3X-{day}-D{n}-TZA-TP","ref_id":str(uuid.uuid4()),"sym":"TZA","side":"sell","qty":q,"type":"limit","limit":tp,"tif":"gfd","hours":"regular_hours","rule":"RULES_v3 §11 v1.3 TP +1.0%","note":f"day leg #{n} TP"}
open('/home/user/test-trading/trader/orders.jsonl','a').write(json.dumps(d)+"\n"); print("TP",q,tp,d['ref_id'])
