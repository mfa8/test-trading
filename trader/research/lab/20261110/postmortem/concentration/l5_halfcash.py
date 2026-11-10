# Benchmark diagnostic (NOT pre-registered, NOT a proposal): what does the TQQQ half add over leaving that half in cash?
import sys
import numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/concentration')
from l5lib import *
B = load_long('2026-11-06'); rows = build_nights(B)
legN = np.array([r['legN'] for r in rows]); legT = np.array([r['legT'] for r in rows]); up = np.array([r['up'] for r in rows]); yr = np.array([r['d'][:4] for r in rows])
dates = [r['d'] for r in rows]
for lab, s in (('trend rule', np.where(up, 0.98, 0.25)), ('0.98 always', np.full(len(rows), 0.98))):
    for nm, m in (('2015-2020', yr <= '2020'), ('2021-2026', yr >= '2021'), ('2015-2026', yr >= '2015')):
        V = [('NVDL-only', s[m] * (legN[m] - COST)), ('split', s[m] * (0.5 * legN[m] + 0.5 * legT[m] - COST)), ('half NVDL + half cash', s[m] * 0.5 * (legN[m] - COST)), ('TQQQ-only', s[m] * (legT[m] - COST))]
        d_ = [d for d, k in zip(dates, m) if k]
        bo = bootstrap(np.column_stack([v for _, v in V]), d_, offset=True)
        print(lab, nm)
        for j, (n_, R) in enumerate(V):
            x = stats(R)
            print('    %-22s g %+.4f sd %.3f worst %+.2f maxDD %+.1f PAUSE nights %d eps %d | boot P(KILL250) %.4f P(PAUSE250) %.4f' % (n_, x['g'], x['sd'], x['worst'], x['maxdd'], x['pause_nights'], x['pause_eps'], (bo['minE_h'][:, j] <= 0.5).mean(), bo['pause_h'][:, j].mean()))
