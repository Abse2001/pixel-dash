# First-order signal-integrity check of the unterminated ADDR/CTRL and CK lines (TI SPRS717L Figure 7-48 topology:
# one DDR3 device, no VTT termination; TI asks for an analysis of the actual board before using it).
# Model: driver = ramped source behind an output resistance, lossless line (Z0, delay), receiver = capacitance
# (two dice in the package + ball/via). Time-domain wave simulation, 1 ps steps, pseudo-random bit pattern.
# Judged at the memory ball against the DDR3L (1.35 V) address/command input levels of JESD79-3-1A:
#   VIH(AC135) = VREF + 0.135, VIH(DC90) = VREF + 0.09, mirrored for low; overshoot/undershoot amplitude limit 0.4 V.
import random, json, sys
VDD = 1.35; VREF = VDD / 2; DT = 1e-12
def run(Z0, td, Rs, C, tr, tbit, nbits=400, seed=1):
    random.seed(seed); bits = [random.randint(0, 1) for _ in range(nbits)]
    n = max(1, round(td / DT)); fwd = [0.0] * n; bwd = [0.0] * n; vl = 0.0; steps = round(tbit / DT); out = []; k = 0; prev = 0
    for bi, b in enumerate(bits):
        for s in range(steps):
            t = s * DT; vs = (prev + (b - prev) * min(1.0, t / tr)) * VDD
            bin_ = bwd[k]                                   # wave arriving back at the driver
            v0 = (vs / Rs + 2 * bin_ / Z0) / (1 / Rs + 1 / Z0); a = v0 - bin_
            ain = fwd[k]                                    # wave arriving at the receiver
            vl += DT * (2 * ain - vl) / (Z0 * C); bref = vl - ain
            fwd[k] = a; bwd[k] = bref; k = (k + 1) % n
            out.append((bi, s, vl))
        prev = b
    # per bit: when does the level become valid (last crossing of the AC level), worst level afterwards, overshoot
    late = 0.0; hi_min = 9; lo_max = -9; over = 0.0; under = 0.0
    for bi in range(8, nbits):
        seg = [v for (i, s, v) in out[bi * steps + n:(bi + 1) * steps + n]] if (bi + 1) * steps + n <= len(out) else None
        if not seg: continue
        b = bits[bi]; ac = VREF + 0.135 if b else VREF - 0.135
        ok = [(v >= ac) if b else (v <= ac) for v in seg]
        if not any(ok): return None
        first = ok.index(True); late = max(late, first * DT)
        after = seg[first:]
        if b: hi_min = min(hi_min, min(after)); over = max(over, max(seg) - VDD)
        else: lo_max = max(lo_max, max(after)); under = max(under, -min(seg))
    return dict(valid_after_ps=late * 1e12, high_min=hi_min, low_max=lo_max, overshoot=over, undershoot=under)
rows = []
TD = 42.3e-3 * 6.0e-9      # 42.3 mm of outer-layer microstrip at about 6.0 ps/mm
for Z0 in (50, 60, 75):
    for Rs in (25, 34, 40, 48, 60):
        for C in (3.0e-12, 4.5e-12):
            r = run(Z0, TD, Rs, C, tr=250e-12, tbit=2.5e-9)   # DDR3-800: one address bit per 2.5 ns clock
            if r is None: rows.append((Z0, Rs, C, None)); continue
            good = r['high_min'] >= VREF + 0.09 and r['low_max'] <= VREF - 0.09 and r['overshoot'] <= 0.4 and r['undershoot'] <= 0.4
            rows.append((Z0, Rs, C, r, good))
print("ADDR/CTRL, 42.3 mm, DDR3-800 (2.5 ns per bit), rise 250 ps")
print(" Z0  Rs  Cload | valid after | high stays >= | low stays <= | overshoot | undershoot | verdict")
for z, rs, c, r, *g in rows:
    if r is None: print(f"{z:3d} {rs:3d} {c*1e12:4.1f}pF | never valid"); continue
    print(f"{z:3d} {rs:3d} {c*1e12:4.1f}pF | {r['valid_after_ps']:6.0f} ps | {r['high_min']:.3f} V (need {VREF+0.09:.3f}) | {r['low_max']:.3f} V (need {VREF-0.09:.3f}) | {r['overshoot']:.3f} V | {r['undershoot']:.3f} V | {'OK' if g[0] else 'MARGINAL'}")
ck = []
for Rs in (25, 34, 40, 48):
    r = run(60, TD, Rs, 2.5e-12, tr=200e-12, tbit=1.25e-9, nbits=200); ck.append((Rs, r))   # clock: alternating at 400 MHz is the worst pattern inside PRBS
print("CK (each leg against its 60 ohm odd-mode line), 400 MHz")
for rs, r in ck: print(f" Rs {rs}: " + ("never valid" if r is None else f"valid after {r['valid_after_ps']:.0f} ps, high >= {r['high_min']:.3f} V, low <= {r['low_max']:.3f} V, overshoot {r['overshoot']:.3f} V, undershoot {r['undershoot']:.3f} V"))
