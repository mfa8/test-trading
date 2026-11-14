#!/usr/bin/env python3
"""Token use of this session's main thread since a given UTC time (default: the last weekly reset, Fri 10:00Z).
usage: python3 trader/tools/usage.py [YYYY-MM-DDTHH:MM:SS]
Reads the session transcript; writes nothing. Prints one JSON line. Sub-agent tokens are not in the transcript."""
import datetime, glob, json, sys

def last_reset(now):
    d = now.replace(hour=10, minute=0, second=0, microsecond=0)
    while d.weekday() != 4 or d > now:
        d -= datetime.timedelta(days=1)
    return d.strftime('%Y-%m-%dT%H:%M:%S')

def main():
    now = datetime.datetime.utcnow()
    since = sys.argv[1] if len(sys.argv) > 1 else last_reset(now)
    files = sorted(glob.glob('/root/.claude/projects/-home-user-test-trading/*.jsonl'))
    seen = set(); req = cr = cw = out = 0; peak = last = 0
    for fp in files:
        for line in open(fp, errors='replace'):
            if '"usage"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if (d.get('timestamp') or '')[:19] < since:
                continue
            m = d.get('message') or {}; u = m.get('usage')
            key = d.get('requestId') or m.get('id')
            if not u or key in seen:
                continue
            seen.add(key); req += 1
            a = u.get('cache_read_input_tokens') or 0; b = u.get('cache_creation_input_tokens') or 0
            cr += a; cw += b; out += u.get('output_tokens') or 0
            last = a + b + (u.get('input_tokens') or 0); peak = max(peak, last)
    print(json.dumps({'since_utc': since, 'asof_utc': now.strftime('%Y-%m-%dT%H:%M'), 'requests': req, 'cache_read_M': round(cr / 1e6, 2),
                      'cache_write_M': round(cw / 1e6, 2), 'output_M': round(out / 1e6, 3), 'context_now_k': round(last / 1e3), 'peak_context_k': round(peak / 1e3)}))

if __name__ == '__main__':
    main()
