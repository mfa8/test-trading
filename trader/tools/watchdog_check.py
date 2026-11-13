#!/usr/bin/env python3
# t3x watchdog check (notify-only). Reviewed copy (challenge): alert headline leads with the recorded position.
# t3x watchdog check (notify-only). Reads ONLY git objects of the trading branch; writes nothing, places no orders.
# usage (inside the repo, after `git fetch origin claude/autonomous-swing-trading-hd9m81`):
#   python3 watchdog_check.py            first pass  (a would-be alert prints RETRY, exit 3)
#   python3 watchdog_check.py --final    second pass (prints ALERT, exit 1)
# exit codes: 0 QUIET, 1 ALERT, 2 BLIND (the check itself could not run), 3 RETRY (fetch again in ~5 min, then --final)
# test hooks (never set them in a real run): WD_NOW=YYYY-MM-DDTHH:MM (ET), WD_REF=<git ref>
import datetime, json, os, subprocess, sys
from zoneinfo import ZoneInfo

ET = ZoneInfo('America/New_York'); UTC = datetime.timezone.utc
HOLIDAYS = {'2026-11-26', '2026-12-25',
            '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26', '2027-05-31', '2027-06-18', '2027-07-05',
            '2027-09-06', '2027-11-25', '2027-12-24',
            '2028-01-17', '2028-02-21', '2028-04-14', '2028-05-29', '2028-06-19', '2028-07-04', '2028-09-04',
            '2028-11-23', '2028-12-25'}                      # same table as trader/tools/trend.py
HALF_DAYS = {'2026-11-27', '2026-12-24', '2027-11-26', '2028-07-03', '2028-11-24'}   # 13:00 ET close
TABLE_THROUGH = '2028-12-31'
PREOPEN_FROM = datetime.time(8, 30)     # before this: nothing is due yet
ANALYST_DEADLINE = datetime.time(7, 40) # a commit at or after this time today proves the 07:45 routine ran
EXIT_CHECK_FROM = datetime.time(9, 40)  # the 09:31:05 exit and its commit are due by now
MAX_AGE_MIN = 125                       # market hours: newest commit may be at most this old (hourly heartbeats)
EOD_GRACE_MIN = 45                      # the end-of-day commit is due this long after the close
EVENING_END = datetime.time(20, 0)


def decide(now, commit_ts, state, closed=()):
    """now: aware datetime (ET). commit_ts: aware datetime of the newest commit on the branch.
    Returns (verdict, headline, details[]) with verdict QUIET | ALERT | BLIND."""
    d = now.date().isoformat(); det = []
    if d > TABLE_THROUGH:
        return 'BLIND', 'holiday table in the watchdog ended %s; extend it' % TABLE_THROUGH, det
    if now.weekday() >= 5 or d in HOLIDAYS or d in closed:
        return 'QUIET', 'market closed today (%s)' % d, det
    if commit_ts > now + datetime.timedelta(minutes=10):
        return 'BLIND', 'newest commit is dated in the future (%s); clock or history problem' % commit_ts.astimezone(ET).strftime('%a %m/%d %H:%M ET'), det
    half = d in HALF_DAYS
    close = datetime.datetime.combine(now.date(), datetime.time(13, 0) if half else datetime.time(16, 0), ET)
    t = now.time()
    age = (now - commit_ts).total_seconds() / 60.0
    last = commit_ts.astimezone(ET).strftime('%a %m/%d %H:%M ET')
    today = state.get('today') or {}
    is_today = today.get('date') == d
    pos = [p for p in (state.get('positions') or []) if isinstance(p, dict) and p.get('leg', 'overnight') == 'overnight']
    def carried(p):
        e = str(p.get('entry_t') or '')[:10]
        if len(e) == 10 and e[4] == '-' and e[7] == '-':
            return e < d
        return not (is_today and today.get('entry_done') is True)
    held = [p for p in pos if carried(p)]
    held_txt = ', '.join('%s %s' % (p.get('sym'), p.get('qty')) for p in held)
    pos_txt = ', '.join('%s %s' % (p.get('sym'), p.get('qty')) for p in pos) or 'none'
    det.append('newest commit on the branch: %s (%d min before this check)' % (last, round(age)))
    det.append('state.json: today.date=%s exit_done=%s entry_done=%s eod_done=%s; positions recorded: %s' % (
        today.get('date'), today.get('exit_done'), today.get('entry_done'), today.get('eod_done'), pos_txt))
    if t < PREOPEN_FROM:
        return 'QUIET', 'too early (before 08:30 ET); nothing is due yet', det
    if t >= EVENING_END:
        return 'QUIET', 'after 20:00 ET; outside the checked hours', det
    problems = []
    if t < EXIT_CHECK_FROM:                                   # pre-open check
        deadline = datetime.datetime.combine(now.date(), ANALYST_DEADLINE, ET)
        if commit_ts < deadline:
            if pos:
                problems.append('%s recorded as held and its 09:31 ET sale is at risk: no commit since %s (07:45 ET routine missing)' % (pos_txt, last))
            else:
                problems.append('no commit since %s; the 07:45 ET morning routine has not shown up (account recorded flat)' % last)
    else:
        exit_ok = is_today and today.get('exit_done') is True
        if held and not exit_ok:
            problems.append('the 09:31 ET sale of %s is not recorded (exit_done is not true for %s); last commit %s' % (held_txt, d, last))
            if age <= 30:
                det.append('note: the newest commit is only %d min old, so the session appears to be running but has not recorded the sale' % round(age))
        if now < close + datetime.timedelta(minutes=EOD_GRACE_MIN):
            if age > MAX_AGE_MIN:
                problems.append('no commit for %d minutes during market hours (limit %d); last %s' % (round(age), MAX_AGE_MIN, last))
        else:                                                 # after the close
            if not (is_today and today.get('eod_done') is True):
                problems.append('the end-of-day record for %s is missing; last commit %s; recorded position: %s' % (d, last, pos_txt))
    if problems:
        return 'ALERT', problems[0], det + ['also: ' + p for p in problems[1:]]
    return 'QUIET', 'trading session looks alive (last commit %s)' % last, det


def git(*a):
    r = subprocess.run(['git'] + list(a), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('git %s failed: %s' % (' '.join(a), r.stderr.strip()[:200]))
    return r.stdout


def main():
    final = '--final' in sys.argv[1:]
    ref = os.environ.get('WD_REF', 'FETCH_HEAD')
    if os.environ.get('WD_NOW'):
        now = datetime.datetime.strptime(os.environ['WD_NOW'], '%Y-%m-%dT%H:%M').replace(tzinfo=ET)
    else:
        now = datetime.datetime.now(ET)
    try:
        commit_ts = datetime.datetime.fromtimestamp(int(git('log', '-1', '--format=%ct', ref).strip()), UTC)
        state = json.loads(git('show', ref + ':trader/state.json'))
        closed = ()
        try:
            x = json.loads(git('show', ref + ':trader/research/trend/closed.json'))
            closed = tuple(x) if isinstance(x, list) else tuple(x.get('closed', ())) if isinstance(x, dict) else ()
        except Exception:
            closed = ()
        verdict, head, det = decide(now, commit_ts, state, closed)
    except Exception as e:
        verdict, head, det = 'BLIND', 'the watchdog could not read the trading branch (%s: %s)' % (type(e).__name__, str(e)[:160]), []
    if verdict in ('ALERT', 'BLIND') and not final:
        print('VERDICT: RETRY'); print('WOULD SAY: %s: %s' % (verdict, head))
        print('Wait about 5 minutes, run the git fetch again, then run this script with --final.')
        sys.exit(3)
    print('VERDICT: ' + verdict)
    stamp = now.strftime('%a %m/%d %H:%M ET')
    if verdict == 'ALERT':
        print(('PUSH: ALERT t3x trading session: ' + head)[:206])
    elif verdict == 'BLIND':
        print(('PUSH: WATCHDOG BLIND t3x: ' + head)[:206])
    else:
        print('NOTE: ' + head)
    print('checked at %s' % stamp)
    for x in det: print('- ' + x)
    sys.exit({'QUIET': 0, 'ALERT': 1, 'BLIND': 2}[verdict])


if __name__ == '__main__':
    main()
