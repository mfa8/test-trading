#!/usr/bin/env python3
"""Record one options-sleeve shadow reading (no orders).
usage: shadow_rec.py "15:25 ET" E S "K:bid:ask K:bid:ask ..." EXPIRY
Runs sleeve_r4.py on the quotes and appends its result (plus the time and the raw leg quotes)
to state.today.sleeve_shadow. Kept in the repo since 2026-11-13 (the scratchpad copy was lost
when the container was replaced)."""
import json, os, subprocess, sys

def main():
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    t, E, S, legs, exp = sys.argv[1:6]
    here = os.path.dirname(os.path.abspath(__file__))
    out = subprocess.run([sys.executable, os.path.join(here, 'sleeve_r4.py'), E, S, exp] + legs.split(),
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit('sleeve_r4 failed: ' + out.stderr.strip())
    rec = json.loads(out.stdout.strip().splitlines()[-1])
    rec['t'] = t
    rec['leg_quotes'] = legs
    p = os.path.join(here, '..', 'state.json')
    s = json.load(open(p))
    s.setdefault('today', {}).setdefault('sleeve_shadow', []).append(rec)
    with open(p, 'w') as f:
        json.dump(s, f, indent=2)
        f.write('\n')
    print(json.dumps({k: rec[k] for k in ('t', 'E', 'S', 'B', 'spread', 'call')}))

if __name__ == '__main__':
    main()
