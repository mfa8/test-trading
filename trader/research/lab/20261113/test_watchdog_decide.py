import datetime, importlib.util, sys
from zoneinfo import ZoneInfo
spec = importlib.util.spec_from_file_location('wd', sys.argv[1]); wd = importlib.util.module_from_spec(spec); spec.loader.exec_module(wd)
ET = ZoneInfo('America/New_York')
def T(s): return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M').replace(tzinfo=ET)
def st(date, ex, en, eod, pos): return {'today': {'date': date, 'exit_done': ex, 'entry_done': en, 'eod_done': eod}, 'positions': pos}
P = lambda d: [{'sym': 'NVDL', 'qty': 1, 'entry_t': d + 'T15:52:16.7 ET', 'leg': 'overnight'}]
cases = [
 # name, now, commit, state, closed, expected
 ('half-day 12:47 alive',            '2026-11-27 12:47', '2026-11-27 12:00', st('2026-11-27', True, False, False, []), (), 'QUIET'),
 ('half-day 14:47 EOD done',         '2026-11-27 14:47', '2026-11-27 13:06', st('2026-11-27', True, True, True, P('2026-11-27')), (), 'QUIET'),
 ('half-day 14:47 EOD missing',      '2026-11-27 14:47', '2026-11-27 12:53', st('2026-11-27', True, True, False, P('2026-11-27')), (), 'ALERT'),
 ('half-day 16:47 EOD done, old',    '2026-11-27 16:47', '2026-11-27 13:06', st('2026-11-27', True, True, True, P('2026-11-27')), (), 'QUIET'),
 ('half-day 13:30 grace, alive',     '2026-11-27 13:30', '2026-11-27 12:53', st('2026-11-27', True, True, False, P('2026-11-27')), (), 'QUIET'),
 ('day after holiday: carried pos, exit done', '2026-11-27 09:47', '2026-11-27 09:32', st('2026-11-27', True, False, False, []), (), 'QUIET'),
 ('day after holiday: carried pos, no exit',   '2026-11-27 09:47', '2026-11-27 09:00', st('2026-11-27', False, False, False, P('2026-11-25')), (), 'ALERT'),
 ('11/18 no morning position 09:47', '2026-11-18 09:47', '2026-11-18 09:00', st('2026-11-18', False, False, False, []), (), 'QUIET'),
 ('11/18 16:47 pos entered today, exit_done false', '2026-11-18 16:47', '2026-11-18 16:03', st('2026-11-18', False, True, True, P('2026-11-18')), (), 'QUIET'),
 ('11/17 earnings night: flat, EOD done',  '2026-11-17 16:47', '2026-11-17 16:03', st('2026-11-17', True, False, True, []), (), 'QUIET'),
 ('future-dated commit',             '2026-11-16 09:47', '2026-11-17 09:00', st('2026-11-16', True, False, False, []), (), 'BLIND'),
 ('late exit, session alive 09:47',  '2026-11-16 09:47', '2026-11-16 09:44', st('2026-11-16', False, False, False, P('2026-11-13')), (), 'ALERT'),
 ('stale exit_done from yesterday',  '2026-11-16 09:47', '2026-11-13 16:10', st('2026-11-13', True, True, True, P('2026-11-13')), (), 'ALERT'),
 ('Monday pre-open, weekend commit only', '2026-11-16 08:47', '2026-11-14 15:10', st('2026-11-13', True, True, True, P('2026-11-13')), (), 'ALERT'),
 ('Monday pre-open, analyst ran',    '2026-11-16 08:47', '2026-11-16 07:48', st('2026-11-16', False, False, False, P('2026-11-13')), (), 'QUIET'),
 ('analyst slow: commit 07:41',      '2026-11-16 08:47', '2026-11-16 07:41', st('2026-11-13', True, True, True, P('2026-11-13')), (), 'QUIET'),
 ('pre-open, commit 07:30 only',     '2026-11-16 08:47', '2026-11-16 07:30', st('2026-11-13', True, True, True, P('2026-11-13')), (), 'ALERT'),
 ('unparsable entry_t, entry not done -> carried', '2026-11-16 12:47', '2026-11-16 12:00', st('2026-11-16', False, False, False, [{'sym': 'NVDL', 'qty': 1, 'entry_t': 'n/a'}]), (), 'ALERT'),
 ('unparsable entry_t, entry done today', '2026-11-16 16:47', '2026-11-16 16:03', st('2026-11-16', False, True, True, [{'sym': 'NVDL', 'qty': 1}]), (), 'QUIET'),
 ('one missed heartbeat (107 min)',  '2026-11-16 13:47', '2026-11-16 12:00', st('2026-11-16', True, False, False, []), (), 'QUIET'),
 ('two missed heartbeats (167 min)', '2026-11-16 14:47', '2026-11-16 12:00', st('2026-11-16', True, False, False, []), (), 'ALERT'),
 ('declared closure',                '2026-11-16 09:47', '2026-11-13 16:10', st('2026-11-13', True, True, True, P('2026-11-13')), ('2026-11-16',), 'QUIET'),
 ('before 08:30',                    '2026-11-16 08:10', '2026-11-13 16:10', st('2026-11-13', True, True, True, P('2026-11-13')), (), 'QUIET'),
 ('delayed 09:47 run arrives 10:40, exit done', '2026-11-16 10:40', '2026-11-16 10:00', st('2026-11-16', True, False, False, []), (), 'QUIET'),
 ('16:20 grace: entry done, EOD committed late', '2026-11-16 16:20', '2026-11-16 15:52', st('2026-11-16', True, True, False, P('2026-11-16')), (), 'QUIET'),
 ('option leg ignored',              '2026-11-16 12:47', '2026-11-16 12:00', st('2026-11-16', True, False, False, [{'sym': 'NVDA C', 'qty': 1, 'entry_t': '2026-11-02T10:30 ET', 'leg': 'sleeve'}]), (), 'QUIET'),
 ('missing today block',             '2026-11-16 09:47', '2026-11-16 09:40', {'positions': P('2026-11-13')}, (), 'ALERT'),
 ('table expired',                   '2029-01-02 09:47', '2029-01-02 09:40', st('2029-01-02', True, False, False, []), (), 'BLIND'),
 ('DST start week (Mar 2027) pre-open', '2027-03-15 08:47', '2027-03-15 07:47', st('2027-03-15', False, False, False, P('2027-03-12')), (), 'QUIET'),
]
bad = 0
for name, now, c, s, closed, exp in cases:
    v, head, det = wd.decide(T(now), T(c), s, closed)
    ok = (v == exp); bad += (not ok)
    print(('ok  ' if ok else 'FAIL'), '%-48s' % name, now, '->', v, '|', head[:95])
print('FAILURES:', bad, 'of', len(cases))
