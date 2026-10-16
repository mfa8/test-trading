# usage: python3 hb.py "<note>" HH:MM[et]   (UTC target by default; suffix "et" = America/New_York, DST-safe)
# sleeps min(480s, until target); never rolls to next day
import sys,datetime,time
from zoneinfo import ZoneInfo
note=sys.argv[1]; arg=sys.argv[2].lower()
tz=ZoneInfo('America/New_York') if arg.endswith('et') else datetime.timezone.utc
hh,mm=map(int,arg.rstrip('et').split(':'))
now=datetime.datetime.now(tz)
t=now.replace(hour=hh,minute=mm,second=0,microsecond=0)
d=max(0,min(480,(t-now).total_seconds()))
try: open('/tmp/t3x_scan.log','a').write(f"{now.isoformat()} {note}\n")
except Exception: pass
time.sleep(d); u=datetime.datetime.now(datetime.timezone.utc)
print(u.isoformat(), '|', u.astimezone(ZoneInfo('America/New_York')).strftime('%H:%M:%S ET'))
