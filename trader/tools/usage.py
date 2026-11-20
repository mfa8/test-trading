#!/usr/bin/env python3
"""Token use of this session's main thread since a given UTC time (default: the last weekly reset, Fri 10:00Z).
usage: python3 trader/tools/usage.py [SINCE YYYY-MM-DDTHH:MM:SS [UNTIL YYYY-MM-DDTHH:MM:SS]]
Reads the session transcript; writes nothing. Prints one JSON line. Sub-agent tokens are not in the transcript.
weighted_M is a price-weighted total in cache-read units (cache read 1, uncached input 10, cache write 12.5, output 50):
the weekly allowance is not published, so RULES_v3 section 15 uses whichever of the two fractions is larger.
LOCK_READ_M / LOCK_WEIGHTED_M are the totals measured at the 2026-11-16 lockout (week from 2026-11-13T10:00Z)."""
import datetime, glob, json, sys

LOCK_READ_M = 50.0
LOCK_WEIGHTED_M = 75.4

def last_reset(now):
    d = now.replace(hour=10, minute=0, second=0, microsecond=0)
    while d.weekday() != 4 or d > now:
        d -= datetime.timedelta(days=1)
    return d.strftime('%Y-%m-%dT%H:%M:%S')

def main():
    now = datetime.datetime.utcnow()
    since = sys.argv[1] if len(sys.argv) > 1 else last_reset(now)
    until = sys.argv[2] if len(sys.argv) > 2 else '9999'
    files = sorted(glob.glob('/root/.claude/projects/-home-user-test-trading/*.jsonl'))
    seen = set(); req = cr = cw = out = unc = 0; peak = last = 0
    for fp in files:
        for line in open(fp, errors='replace'):
            if '"usage"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            ts = (d.get('timestamp') or '')[:19]
            if ts < since or ts >= until:
                continue
            m = d.get('message') or {}; u = m.get('usage')
            key = d.get('requestId') or m.get('id')
            if not u or key in seen:
                continue
            seen.add(key); req += 1
            a = u.get('cache_read_input_tokens') or 0; b = u.get('cache_creation_input_tokens') or 0
            cr += a; cw += b; out += u.get('output_tokens') or 0; unc += u.get('input_tokens') or 0
            last = a + b + (u.get('input_tokens') or 0); peak = max(peak, last)
    w = (cr + 10 * unc + 12.5 * cw + 50 * out) / 1e6
    res = {'frac_read': round(cr / 1e6 / LOCK_READ_M, 3)}
    if LOCK_WEIGHTED_M:
        res['frac_weighted'] = round(w / LOCK_WEIGHTED_M, 3)
    res['frac'] = max(res.values())
    print(json.dumps({'since_utc': since, 'asof_utc': now.strftime('%Y-%m-%dT%H:%M'), 'requests': req, 'cache_read_M': round(cr / 1e6, 2),
                      'cache_write_M': round(cw / 1e6, 2), 'output_M': round(out / 1e6, 3), 'uncached_in_M': round(unc / 1e6, 3), 'weighted_M': round(w, 1), **res,
                      'context_now_k': round(last / 1e3), 'peak_context_k': round(peak / 1e3)}))

if __name__ == '__main__':
    main()
