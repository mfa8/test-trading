# usage: python3 bridge.py HH:MM:SS[et]   (UTC today by default; suffix "et" = America/New_York, DST-safe)
# exact-time sleep; refuses legs >= 500s
import sys,datetime,time
from zoneinfo import ZoneInfo
arg=sys.argv[1].lower()
tz=ZoneInfo('America/New_York') if arg.endswith('et') else datetime.timezone.utc
hh,mm,ss=map(int,arg.rstrip('et').split(':'))
now=datetime.datetime.now(tz)
t=now.replace(hour=hh,minute=mm,second=ss,microsecond=0)
d=(t-now).total_seconds()
assert d<500, f"leg too long: {d:.0f}s"
time.sleep(max(0,d)); u=datetime.datetime.now(datetime.timezone.utc)
print(u.isoformat(), '|', u.astimezone(ZoneInfo('America/New_York')).strftime('%H:%M:%S ET'))
