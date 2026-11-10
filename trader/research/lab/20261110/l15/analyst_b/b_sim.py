"""Analyst B simulation for L15: explicit night-by-night loop with a small state machine,
plus independent vectorised cross-checks.

Conventions
  night t      : close of session t -> open of session t+1, labelled by the date of session t
  r[t]         : open[t+1]/close[t] - 1 of the underlying
  unit[t]      : 2*r[t] - COST                     (return of one unit of size)
  R[t]         : s[t] * unit[t]
  E_in[t]      : equity going into night t (after the previous night's exit); E_in[0] = 1
  H[t]         : max(E_in[t-19 .. t])              (20 values including the current one)
  C[t]         : E_in[t] <= 0.80 * H[t]
"""
import numpy as np

COST = 0.0009
THR = 0.80
WIN = 20


def run_loop(r, b, variant, p=0.25, nfix=5, rearm='post'):
    """variant in {'P0','P1','P2','P3'}.
    rearm (P2 only): 'post' = re-arm test only on non-paused nights (primary reading);
                     'any'  = re-arm on any night with C false, pause nights included.
    Returns dict with s, paused, C, E_in, lnR, starts (indices where an episode starts)."""
    n = len(r)
    s = np.empty(n)
    paused = np.zeros(n, dtype=bool)
    Cv = np.zeros(n, dtype=bool)
    E_in = np.empty(n)
    lnR = np.empty(n)
    starts = []
    E = 1.0
    hist = [1.0]            # recorded E values, most recent last
    in_pause = False        # P1
    left = 0                # mandatory paused nights still to serve (P1, P2)
    armed = True            # P2
    for t in range(n):
        H = max(hist[-WIN:])
        C = E <= THR * H
        Cv[t] = C
        E_in[t] = E
        pz = False
        if variant == 'P0':
            pz = False
        elif variant == 'P3':
            pz = C
            if C and (t == 0 or not paused[t - 1]):
                starts.append(t)
        elif variant == 'P1':
            if not in_pause and C:
                in_pause = True
                left = nfix
                starts.append(t)
            if in_pause:
                if left > 0:
                    pz = True
                    left -= 1
                elif C:
                    pz = True
                else:
                    in_pause = False
                    pz = False
        elif variant == 'P2':
            if rearm == 'any' and not C:
                armed = True
            if left > 0:
                pz = True
                left -= 1
            else:
                if rearm == 'post' and (not armed) and (not C):
                    armed = True
                if armed and C:
                    starts.append(t)
                    armed = False
                    left = nfix - 1
                    pz = True
        else:
            raise ValueError(variant)
        paused[t] = pz
        st = min(b[t], p) if pz else b[t]
        s[t] = st
        R = st * (2.0 * r[t] - COST)
        lnR[t] = np.log1p(R)
        E = E * (1.0 + R)
        hist.append(E)
    return dict(s=s, paused=paused, C=Cv, E_in=E_in, lnR=lnR, starts=starts,
                E_out=np.append(E_in[1:], E))


# ---------------------------------------------------------------- vectorised checks

def _E_in_from_s(r, s):
    R = s * (2.0 * r - COST)
    E_out = np.cumprod(1.0 + R)
    return np.concatenate(([1.0], E_out[:-1])), np.log1p(R)


def _rolling_max(x, w=WIN):
    pad = np.concatenate((np.full(w - 1, -np.inf), x))
    return np.lib.stride_tricks.sliding_window_view(pad, w).max(axis=1)


def _C_from_E(E_in):
    return E_in <= THR * _rolling_max(E_in)


def vec_P0(r, b):
    E_in, lnR = _E_in_from_s(r, b)
    return dict(s=b.copy(), E_in=E_in, lnR=lnR)


def vec_P3(r, b, p=0.25, maxit=100000):
    """Fixed-point iteration, all array operations. s[t] depends only on E up to t, which
    depends only on s[0..t-1], so the fixed point is unique and each pass fixes at least
    one more night."""
    s = b.copy()
    for it in range(maxit):
        E_in, lnR = _E_in_from_s(r, s)
        C = _C_from_E(E_in)
        s_new = np.where(C, np.minimum(b, p), b)
        if np.array_equal(s_new, s):
            return dict(s=s, E_in=E_in, lnR=lnR, C=C, iters=it + 1)
        # keep only the first changed night's prefix exact: everything up to and including
        # the first disagreement is now final, later nights get re-derived next pass
        s = s_new
    raise RuntimeError('P3 fixed point did not converge')


def recheck_flags(variant, C, nfix=5, rearm='post'):
    """Independent derivation of the paused flags from a C vector (different code
    structure from run_loop: episode-jumping while loop). Used to verify P1/P2."""
    n = len(C)
    pz = np.zeros(n, dtype=bool)
    starts = []
    t = 0
    if variant == 'P1':
        while t < n:
            if not C[t]:
                t += 1
                continue
            starts.append(t)
            e = min(t + nfix, n)              # mandatory part [t, e)
            while e < n and C[e]:
                e += 1                        # extension while C holds
            pz[t:e] = True
            t = e + 1                         # night e (if any) is normal: C[e] is False
    elif variant == 'P2':
        armed = True
        while t < n:
            if armed and C[t]:
                starts.append(t)
                e = min(t + nfix, n)
                pz[t:e] = True
                if rearm == 'any':
                    armed = bool((~C[t:e]).any())
                else:
                    armed = False
                t = e
            else:
                if not C[t]:
                    armed = True
                t += 1
    elif variant == 'P3':
        pz = C.copy()
        starts = [i for i in range(n) if C[i] and (i == 0 or not C[i - 1])]
    return pz, starts


def verify(r, b, res, variant, p=0.25, nfix=5, rearm='post'):
    """Returns max abs discrepancy in lnR and count of flag mismatches for a loop result."""
    E_in, lnR = _E_in_from_s(r, res['s'])
    C = _C_from_E(E_in)
    if variant == 'P0':
        pz = np.zeros(len(r), dtype=bool)
        st = []
    else:
        pz, st = recheck_flags(variant, C, nfix, rearm)
    s_exp = np.where(pz, np.minimum(b, p), b)
    return dict(max_lnR_diff=float(np.max(np.abs(lnR - res['lnR']))),
                flag_mismatch=int((pz != res['paused']).sum()),
                C_mismatch=int((C != res['C']).sum()),
                size_mismatch=int((s_exp != res['s']).sum()),
                starts_equal=(list(st) == list(res['starts'])))


# ---------------------------------------------------------------- statistics

def episodes_from(res):
    """List of (start_index, length) of paused runs, one per recorded start.
    Length = paused nights from the start up to (not including) the next non-paused
    night or the next recorded start."""
    pz = res['paused']
    n = len(pz)
    st = list(res['starts'])
    out = []
    for k, t0 in enumerate(st):
        lim = st[k + 1] if k + 1 < len(st) else n
        e = t0
        while e < lim and pz[e]:
            e += 1
        out.append((t0, e - t0))
    return out


def max_drawdown(E_start, lnR):
    """Worst peak-to-trough fall (as a positive percent) of the equity path that starts
    at E_start (taken as 1) and follows lnR."""
    path = np.concatenate(([0.0], np.cumsum(lnR)))
    peak = np.maximum.accumulate(path)
    return float(100.0 * (1.0 - np.exp((path - peak).min())))


def boot_ci(d, years, seed, ndraw=2000, lo=5, hi=95):
    """Block bootstrap by calendar year of the mean of d (per night), in the same units
    as d. Resample the distinct years with replacement (as many as there are), pool the
    nights of the drawn years, statistic = pooled mean."""
    uy = np.unique(years)
    sums = np.array([d[years == y].sum() for y in uy])
    cnts = np.array([(years == y).sum() for y in uy], dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(uy), size=(ndraw, len(uy)))
    stat = sums[idx].sum(axis=1) / cnts[idx].sum(axis=1)
    return float(np.percentile(stat, lo)), float(np.percentile(stat, hi)), float((stat > 0).mean())
