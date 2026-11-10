"""Core simulation for L15 (analyst A). Pure Python, no shared code with other scripts.

Indexing convention
-------------------
Night t runs from the close of session t to the open of session t+1.
E[t] is the equity recorded after the exit of night t-1 (E[0] = 1), i.e. the
equity known when the size for night t is chosen.
u[t] = 2*r[t] - 0.0009 is the return of one unit of size on night t.
R[t] = s[t] * u[t];  E[t+1] = E[t] * (1 + R[t]).
H[t] = max(E[t-19..t]) (fewer values at the very start);  C[t] = E[t] <= 0.80*H[t].
"""
import math

COST = 0.0009
LEV = 2.0


def unit_return(r):
    return LEV * r - COST


def simulate(u, b, variant, p=0.25, n_len=5, window=20, thr=0.80,
             rearm_during_pause=True, min_obs=1):
    """Run one variant.

    u : list of unit returns per night
    b : list of base sizes per night (trend rule output, or 0.98 always)
    variant : 'P0', 'P1', 'P2', 'P3'   (P2x10 = 'P2' with n_len=10)
    p : pause size; a paused night uses min(b, p)
    rearm_during_pause : P2 only. True  = reading A: the rule re-arms on the first
                         night after the pause START on which C is false, even if
                         that night is still inside the 5-night pause.
                         False = reading B: C is only looked at for re-arming on
                         nights after the 5-night pause has run out.
    min_obs : number of E values that must exist before C can be true (1 = use
              whatever is available at the start; 20 = wait for a full window).
    Returns dict with E (len n+1), s, lr, paused, cond, episodes [(start, length)].
    """
    n = len(u)
    E = [1.0]
    s = [0.0] * n
    lr = [0.0] * n
    paused = [False] * n
    cond = [False] * n
    starts = []
    in_pause = False
    left = 0          # mandatory paused nights still to come after the current one
    armed = True
    for t in range(n):
        Et = E[t]
        lo = t - window + 1
        if lo < 0:
            lo = 0
        H = max(E[lo:t + 1])
        C = (t + 1 >= min_obs) and (Et <= thr * H)
        cond[t] = C
        if variant == 'P0':
            pz = False
        elif variant == 'P3':
            pz = C
        elif variant == 'P1':
            if in_pause and left == 0 and not C:
                in_pause = False            # minimum served and equity above trigger
            if in_pause:
                pz = True
                if left > 0:
                    left -= 1
            elif C:
                in_pause = True
                left = n_len - 1
                pz = True
                starts.append(t)
            else:
                pz = False
        elif variant == 'P2':
            if in_pause and left == 0:
                in_pause = False            # fixed length served
            if (not armed) and (not C) and (rearm_during_pause or not in_pause):
                armed = True
            if in_pause:
                pz = True
                left -= 1
            elif C and armed:
                in_pause = True
                left = n_len - 1
                armed = False
                pz = True
                starts.append(t)
            else:
                pz = False
        else:
            raise ValueError(variant)
        paused[t] = pz
        st = min(b[t], p) if pz else b[t]
        s[t] = st
        R = st * u[t]
        if 1.0 + R <= 0:
            raise ValueError('equity wiped out on night %d (R=%f)' % (t, R))
        lr[t] = math.log1p(R)
        E.append(Et * (1.0 + R))
    episodes = _episodes(variant, paused, starts, n_len)
    return dict(E=E, s=s, lr=lr, paused=paused, cond=cond, episodes=episodes)


def _episodes(variant, paused, starts, n_len):
    """List of (start_index, length_in_nights)."""
    n = len(paused)
    eps = []
    if variant == 'P0':
        return eps
    if variant == 'P3':
        t = 0
        while t < n:
            if paused[t]:
                j = t
                while j < n and paused[j]:
                    j += 1
                eps.append((t, j - t))
                t = j
            else:
                t += 1
        return eps
    if variant == 'P2':
        for st in starts:
            eps.append((st, min(n_len, n - st)))
        return eps
    # P1: contiguous run from each start (a P1 episode always ends on a normal night)
    for st in starts:
        j = st
        while j < n and paused[j]:
            j += 1
        eps.append((st, j - st))
    return eps


def max_drawdown(E_segment):
    """Worst peak-to-trough drawdown (fraction) of an equity list."""
    peak = E_segment[0]
    worst = 0.0
    for v in E_segment:
        if v > peak:
            peak = v
        dd = 1.0 - v / peak
        if dd > worst:
            worst = dd
    return worst
