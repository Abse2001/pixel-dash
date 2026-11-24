# Signal-integrity simulation of the unterminated ADDR/CTRL and CK lines (TI SPRS717L Figure 7-48: one DDR3 device,
# no VTT termination; TI asks for an analysis of the actual board). Extends the first-order addr_si.py with:
#  - per-unit-length L and C matrices from the 2D field solver (zo_fd.py) for the prepregs JLCPCB uses on L1-L2
#    (1080, 3313, 2116; 7628 is excluded by the ordering note because it gives 89 ohm);
#  - coupled multiconductor lines, solved in the time domain (FDTD on 0.4 mm cells, 1 ps steps): the victim between
#    two aggressors at the routed spacing profile of the worst net (A1: 18.07 mm at the 0.1 mm minimum gap, split
#    over both fan-outs, 4w = 0.408 mm gap on the rest of its 42.31 mm);
#  - losses: conductor skin effect at the 400 MHz fundamental (signal + return) only; dielectric loss is left out,
#    which under-damps the lines (conservative for overshoot and ringing);
#  - the two through vias of every net (0.2 pF each), processor ball + package (1.0 pF), memory package
#    (0.5 pF ball side, 1.5 nH) in front of the die input (1.5 pF single die, 3.0 pF for two dice);
#  - three aggressor patterns: switching against the victim, with the victim, and independent PRBS.
# Judged at the memory ball (where JESD79-3-1A defines the levels), DDR3L 1.35 V address/command inputs:
#   VIH/VIL(AC135) reached early enough to leave setup time in the 2.5 ns bit, VIH/VIL(DC90) held for the rest of the
#   bit, overshoot / undershoot amplitude <= 0.4 V.
import numpy as np, itertools, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zo_fd import solve
VDD = 1.35; VREF = VDD / 2; c0 = 299792458.0; E0 = 8.854e-12
LEN = 42.31e-3; TIGHT = 18.07e-3; DZ = 0.4e-3; DT = 1.0e-12
STACKS = {"1080": (0.0764, 3.91), "3313": (0.0994, 4.10), "2116": (0.1194, 4.16)}
RAC = 2 * np.sqrt(np.pi * 400e6 * 4e-7 * np.pi * 1.72e-8) / 0.102e-3 * 1.4  # ohm/m at 400 MHz, signal + return
def prbs7(seed):
    r = seed & 0x7F or 1; out = []
    for _ in range(127): b = ((r >> 6) ^ (r >> 5)) & 1; r = ((r << 1) | b) & 0x7F; out.append(b)
    return out
def pair_mats(h, er, gap):
    """Maxwell C (per line to ground Cg, mutual Cm) with dielectric and in air, from even/odd solutions."""
    d = solve(H=h, er=er, gap=gap, even=True)
    cg, cga = d['Ceven'] / 2, d['Cair_even'] / 2
    cm, cma = (d['Codd'] / 2 - cg) / 2, (d['Cair_odd'] / 2 - cga) / 2
    return cg, cm, cga, cma
def line_mats(n, cg, cm, cga, cma):
    """n parallel lines, neighbours coupled (next-nearest ignored); returns L, C per metre."""
    def maxwell(g, m):
        C = np.zeros((n, n))
        for i in range(n):
            C[i, i] = g + m * ((i > 0) + (i < n - 1))
            if i: C[i, i - 1] = C[i - 1, i] = -m
        return C
    C = maxwell(cg, cm); L = np.linalg.inv(maxwell(cga, cma)) / c0 ** 2
    return L, C
def simulate(cases, n, drive, nbits, tbit, tr):
    """cases: dicts with stack, Rs, Cdie, gaps (list of (gap, length)); drive(m, line) -> bit list. Returns ball voltages [steps, M, n]."""
    M = len(cases); N = int(round(LEN / DZ)); z = (np.arange(N) + 0.5) * DZ
    Lc = np.zeros((M, N, n, n)); Cc = np.zeros((M, N + 1, n, n))
    for m, c in enumerate(cases):
        h, er = STACKS[c['stack']]
        mats = {g: line_mats(n, *pair_mats(h, er, g)) for g in set(g for g, _ in c['profile'])}
        tight = (z < TIGHT / 2) | (z > LEN - TIGHT / 2)
        for k in range(N):
            L, C = mats[c['profile'][0][0] if tight[k] else c['profile'][1][0]]
            Lc[m, k] = L * DZ; Cc[m, k] += C * DZ / 2; Cc[m, k + 1] += C * DZ / 2
        eye = np.eye(n)
        Cc[m, 0] += 1.0e-12 * eye; Cc[m, -1] += 0.5e-12 * eye
        for k in (int(N * 0.08), int(N * 0.92)): Cc[m, k] += 0.2e-12 * eye
    Linv = np.linalg.inv(Lc); Cinv = np.linalg.inv(Cc)
    Rs = np.array([c['Rs'] for c in cases])[:, None]; Cd = np.array([c['Cdie'] for c in cases])[:, None]
    Rl = RAC * DZ  # dielectric loss left out on purpose: less damping, more ringing (conservative)
    V = np.zeros((M, N + 1, n)); I = np.zeros((M, N, n)); Ip = np.zeros((M, n)); Vd = np.zeros((M, n)); Lpk = 1.5e-9
    steps = int(round(tbit / DT)); bits = np.array([[drive(m, l)[:nbits] for l in range(n)] for m in range(M)], float)  # M, n, nbits
    out = np.empty((nbits * steps, M, n), np.float32)
    prev = np.zeros((M, n))
    for bi in range(nbits):
        cur = bits[:, :, bi]
        for s in range(steps):
            vs = (prev + (cur - prev) * min(1.0, s * DT / tr)) * VDD
            dVz = V[:, :-1] - V[:, 1:] - Rl * I
            I = I + DT * np.einsum('mkij,mkj->mki', Linv, dVz)
            J = np.empty_like(V); J[:, 1:-1] = I[:, :-1] - I[:, 1:]
            J[:, 0] = (vs - V[:, 0]) / Rs - I[:, 0]; J[:, -1] = I[:, -1] - Ip
            Q = np.einsum('mkij,mkj->mki', Cinv, J)
            V = V + DT * Q
            Ip = Ip + DT * (V[:, -1] - Vd) / Lpk; Vd = Vd + DT * Ip / Cd
            out[bi * steps + s] = V[:, -1]
        prev = cur
    return out, bits, steps
def judge(wave, bits, steps, delay_steps, setup_ps=400):
    """levels of one line at the memory ball; window of each bit shifted by the line + package delay."""
    late = 0; hold = 9.0; hold_lo = -9.0; ov = 0.0; un = 0.0
    for bi in range(8, len(bits) - 1):
        seg = wave[bi * steps + delay_steps:(bi + 1) * steps + delay_steps]; b = bits[bi]
        ok = seg >= VREF + 0.135 if b else seg <= VREF - 0.135
        if not ok.any(): return None
        f = int(np.argmax(ok)); late = max(late, f)
        if b: hold = min(hold, seg[f:].min()); ov = max(ov, float(seg.max()) - VDD)
        else: hold_lo = max(hold_lo, seg[f:].max()); un = max(un, -float(seg.min()))
    return dict(late=late * DT * 1e12, hi=hold, lo=hold_lo, ov=ov, un=un)
if __name__ == '__main__':
    NB = int(os.environ.get('NB', 100))
    pats = {"against": lambda v: [1 - x for x in v], "with": lambda v: v, "random": None}
    cases = []
    for st, rs, cd, pat in itertools.product(STACKS, (34, 40, 48, 60), (1.5e-12, 3.0e-12), pats):
        cases.append(dict(stack=st, Rs=rs, Cdie=cd, pat=pat, profile=[(0.1, TIGHT), (0.408, LEN - TIGHT)]))
    vic = prbs7(0x55)
    def drive(m, l):
        if l == 1: return vic
        p = cases[m]['pat']
        return prbs7(0x13 + 7 * l) if p == "random" else pats[p](vic)
    out, bits, steps = simulate(cases, 3, drive, NB, 2.5e-9, 250e-12)
    geo = {st: solve(H=h, er=er) for st, (h, er) in STACKS.items()}
    print(f"ADDR/CTRL: worst net (A1), 42.31 mm, 18.07 mm of it at the 0.1 mm minimum gap between two aggressors, the rest at 4w;")
    print(f"DDR3-800 (2.5 ns per bit), PRBS7 victim, {NB} bits, rise 250 ps, lossy coupled lines, 2 vias per net, packages. Levels at the memory ball.")
    print("prepreg Z0    Rs  die   aggressors | AC135 reached after | holds high >= (DC90 0.765) | holds low <= (DC90 0.585) | over / under (<= 0.4 V) | verdict")
    verdict = {}
    for m, c in enumerate(cases):
        z0, se = geo[c['stack']]; d = int(round(LEN * se / c0 / DT))
        r = judge(out[:, m, 1], bits[m, 1], steps, d)
        good = r is not None and r['hi'] >= VREF + 0.09 and r['lo'] <= VREF - 0.09 and r['ov'] <= 0.4 and r['un'] <= 0.4 and r['late'] <= 2500 - 400
        key = (c['stack'], c['Rs']); verdict[key] = verdict.get(key, True) and good
        print(f"{c['stack']}  {z0:5.1f} {c['Rs']:3d}  {c['Cdie']*1e12:3.1f}  {c['pat']:8s}   | " + ("never valid" if r is None else
              f"{r['late']:5.0f} ps | {r['hi']:.3f} V | {r['lo']:.3f} V | {r['ov']:.3f} / {r['un']:.3f} V | {'OK' if good else 'FAIL'}"), flush=True)
    print("\nprocessor ADDR/CTRL output impedance settings that pass every case, per prepreg:")
    for st in STACKS: print(f"  {st} ({geo[st][0]:.1f} ohm): " + (", ".join(f"{rs} ohm" for rs in (34, 40, 48, 60) if verdict[(st, rs)]) or "none"))
    # CK/CKn: the pair itself, driven complementary, 400 MHz
    ckc = [dict(stack=st, Rs=rs, Cdie=1.5e-12, pat=None, profile=[(gap, TIGHT), (gap, LEN - TIGHT)])
           for st, rs, gap in itertools.product(STACKS, (34, 40, 48), (0.1, 0.2))]
    clk = [i % 2 for i in range(80)]
    o2, b2, s2 = simulate(ckc, 2, lambda m, l: clk if l == 0 else [1 - x for x in clk], 80, 1.25e-9, 200e-12)
    print("\nCK / CKn pair, 400 MHz, complementary drive; differential level at the memory ball (DDR3L VIHdiff(AC) >= 0.27 V)")
    for m, c in enumerate(ckc):
        z0, se = geo[c['stack']]; d = int(round(LEN * se / c0 / DT)); w = o2[:, m, 0] - o2[:, m, 1]
        seg = w[20 * s2 + d:78 * s2 + d]; ov = float(max(o2[20 * s2:, m, 0].max(), o2[20 * s2:, m, 1].max()) - VDD); un = float(-min(o2[20 * s2:, m, 0].min(), o2[20 * s2:, m, 1].min()))
        # per half period: reaches +-0.27 V and how early
        lat = 0; okall = True
        for bi in range(20, 78):
            sg = w[bi * s2 + d:(bi + 1) * s2 + d]; b = clk[bi]; ok = sg >= 0.27 if b else sg <= -0.27
            if not ok.any(): okall = False; break
            lat = max(lat, int(np.argmax(ok)))
        print(f"  {c['stack']} gap {c['profile'][0][0]:.1f} mm Rs {c['Rs']}: differential peak {seg.max():.3f} / {seg.min():.3f} V, +-0.27 V reached after {lat*DT*1e12:.0f} ps of each 1250 ps half period" + ("" if okall else " (NOT reached)") + f", single-ended over/under {ov:.3f}/{un:.3f} V {'OK' if okall and ov <= 0.4 and un <= 0.4 else 'FAIL'}", flush=True)
