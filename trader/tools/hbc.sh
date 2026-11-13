#!/usr/bin/env bash
# Heartbeat + commit + push in one step.
# usage: bash trader/tools/hbc.sh "<journal note>" "<commit title>" [TAG]
#   appends "<utc> TAG <note>" to trader/journal.md, stamps state.wake, commits trader/ and pushes.
# Kept in the repo (not the scratchpad) since 2026-11-13: a container replacement wipes the scratchpad.
set -u
ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$ROOT" || exit 1
NOTE="${1:?note}"; TITLE="${2:?commit title}"; TAG="${3:-W-10}"
BR=claude/autonomous-swing-trading-hd9m81
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "$TS $TAG $NOTE" >> trader/journal.md
python3 - "$TS" "$NOTE" <<'PY'
import json, sys
p = 'trader/state.json'
s = json.load(open(p))
s.setdefault('wake', {})
s['wake']['last_heartbeat_utc'] = sys.argv[1]
s['wake']['loop_note'] = sys.argv[2][:160]
with open(p, 'w') as f:
    json.dump(s, f, indent=2)
    f.write('\n')
PY
git add -A trader
git commit -q -m "$TITLE" -m "Co-Authored-By: Claude <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_014SecwMmw22oHfWJSukz1AT" || { echo "nothing to commit"; exit 0; }
for i in 1 2 3 4; do
  git push -q -u origin "$BR" && break
  sleep $((2 ** i))
done
git log --oneline | head -1
git status -sb | head -1
