# ngspice simulation of the routed AM3354 <-> DDR3L block (external/ddr-route/out/module9), generic I/O (no IBIS).
# Adapted from the RK3566 module's ddr_sim.py for DDR3L:
#   - channel: every routed piece in route order as a lossless line (TLINE); outer microstrip over the L2/L5 ground
#     from the field solver of module/si/zo_fd.py for the 1080 prepreg (0.102 mm: 56.1 ohm, effective er 3.01);
#     0.09 mm neck-downs scaled by Hammerstad-Jensen; each via a 45 ohm line over the 1.0 mm board at the FR-4
#     velocity (x1.2 for its pads) plus 0.3 pF
#   - DDR3L: VDDQ 1.35 V, VTT 0.675 V, DDR3-800 (UI 1250 ps), 20-80 % edges of 250 ps
#   - data (DQ, DM, DQS): write = processor driver (40 / 34 ohm) into the memory's 60 ohm ODT to VTT + 1.5 pF;
#     read = memory driver 34 ohm (RZQ/7) into a 60 ohm termination to VTT at the processor + 1.5 pF
#   - address/command/CK: one DDR3 device without VTT termination (TI SPRS717L figure 7-48): processor driver into
#     the memory input (1.5 pF die + 0.5 pF package), judged for overshoot and settling
# Usage: python3 si/ddr_sim.py   -> si/ddr_sim_results.txt
import json, math, os, subprocess, tempfile
D = os.path.dirname(os.path.abspath(__file__)); EXT = D + "/../../external/ddr-route"
R = json.load(open(EXT + "/out/module9/ddr-cpu-ram.routed.json")); NAMES = json.load(open(EXT + "/net-names.json"))
INV = {v: k for k, v in NAMES.items()}
VDD, VTT, RATE = 1.35, 0.675, 800.0
UI = 1e6 / RATE; TR = 250 / 0.6  # ps, 0-100 % ramp for a 250 ps 20-80 % edge
PS_OUT = 1000 * math.sqrt(3.01) / 299.792458  # ps/mm, 0.102 mm outer trace (field solver)
PS_IN = 1000 * math.sqrt(4.2) / 299.792458  # ps/mm in FR-4 (via barrel)
BARREL = 0.9  # mm, top to bottom copper of the 1.0 mm board
def hj(w, h=0.0764, er=3.91):  # Hammerstad-Jensen microstrip Z0 (only used for the ratio of the neck-down)
    u = w / h; ee = (er + 1) / 2 + (er - 1) / 2 / math.sqrt(1 + 12 / u); f = 6 + (2 * math.pi - 6) * math.exp(-((30.666 / u) ** 0.7528))
    return 60 / math.sqrt(ee) * math.log(f / u + math.sqrt(1 + (2 / u) ** 2))
Z_OUT = {0.102: 56.1}; Z_NECK = 56.1 * hj(0.09) / hj(0.102)
def pieces(net):
    out = []
    for t in R["traces"]:
        if t["connection_name"] != INV[net]: continue
        r = t["route"]
        for a, b in zip(r, r[1:]):
            if a["route_type"] == b["route_type"] == "wire" and a["layer"] == b["layer"]:
                s = math.hypot(b["x"] - a["x"], b["y"] - a["y"])
                if s < 1e-6: continue
                out.append((Z_NECK if (a.get("width") or 0.102) < 0.1 else 56.1, s * PS_OUT, "wire", s))
            if b["route_type"] == "via": out.append((45.0, BARREL * PS_IN * 1.2, "via", 0))
    return out
def merged(net):
    out = []
    for z0, td, kind, s in pieces(net):
        if out and kind == "wire" and out[-1][2] == "wire" and (abs(out[-1][0] - z0) < 0.5 or td < 1.0):
            pz, pt, _ = out[-1]; out[-1] = ((pz * pt + z0 * td) / (pt + td), pt + td, "wire")
        else: out.append((z0, td, kind))
    return out
def delay(net): return sum(td for _, td, _, _ in pieces(net))
def length(net): return sum(s for *_, s in pieces(net))
def prbs7(n, seed=0x7F):
    s = seed; bits = []
    for _ in range(n): b = ((s >> 6) ^ (s >> 5)) & 1; s = ((s << 1) | b) & 0x7F; bits.append(b)
    return bits
def pwl(bits, invert=False):
    pts = []; v0 = None; t = 0.0
    for b in bits:
        v = VDD if (b ^ invert) else 0.0
        if v0 is None: pts = [(0, v)]
        elif v != v0: pts += [(t, v0), (t + TR, v)]
        v0 = v; t += UI
    pts.append((t, v0)); return " ".join(f"{p[0]:.1f}p {p[1]:.4f}" for p in pts)
def channel(pfx, net, src, rx, reverse=False):
    segs = merged(net)[::-1] if reverse else merged(net); lines = []; node = src
    for k, (z0, td, kind) in enumerate(segs):
        nxt = f"{pfx}{k}"; lines.append(f"T{pfx}{k} {node} 0 {nxt} 0 Z0={z0:.2f} TD={td:.3f}p")
        if kind == "via": lines.append(f"C{pfx}v{k} {nxt} 0 0.3p")
        node = nxt
    lines.append(f"R{pfx}j {node} {rx} 0.001"); return lines
def run(nets, bits, rs, term, cload, invert=(), reverse=False):
    net = ["* DDR3L channel, generic I/O", f"Vtt vtt 0 {VTT}"]
    for i, n in enumerate(nets):
        net += [f"V{i} s{i} 0 PWL({pwl(bits, n in invert)})", f"Rs{i} s{i} d{i} {rs}"]
        net += channel(f"n{i}_", n, f"d{i}", f"r{i}", reverse)
        if term: net.append(f"Rt{i} r{i} vtt {term}")
        net.append(f"Ct{i} r{i} 0 {cload}p")
    tstop = len(bits) * UI + 2000; out = tempfile.mktemp(suffix=".txt"); cir = tempfile.mktemp(suffix=".cir")
    net += [".options reltol=1e-4", f".tran 2p {tstop:.0f}p", ".control", "run", "wrdata " + out + " " + " ".join(f"v(r{i})" for i in range(len(nets))), ".endc", ".end"]
    open(cir, "w").write("\n".join(net)); p = subprocess.run(["ngspice", "-b", cir], capture_output=True, text=True)
    if not os.path.exists(out): raise SystemExit(p.stdout[-2000:] + p.stderr[-2000:])
    rows = [list(map(float, l.split())) for l in open(out) if l.strip()]
    return [r[0] * 1e12 for r in rows], [[r[2 * i + 1] for r in rows] for i in range(len(nets))]
def eye(t, v, bits, d, ref):
    """eye at the receiver against a reference level: height at the best phase, width where it is open > 0.1 V"""
    folded = {}
    for ti, vi in zip(t, v):
        k = (ti - d - TR / 2) / UI
        if k < 8 or k >= len(bits) - 1: continue
        b = int(k); folded.setdefault(round((k - b) * 100), []).append((vi, bits[b]))
    hs = {ph: min(x for x, b in xs if b) - max(x for x, b in xs if not b) for ph, xs in folded.items() if any(b for _, b in xs) and any(not b for _, b in xs)}
    best = max(hs.values()) if hs else 0
    return best, sum(1 for h in hs.values() if h > 0.1) / 100 * UI
def crossings(t, x, th):
    return [t[k - 1] + (th - x[k - 1]) / (x[k] - x[k - 1]) * (t[k] - t[k - 1]) for k in range(1, len(x)) if (x[k - 1] - th) * (x[k] - th) < 0]
if __name__ == "__main__":
    out = []
    def say(s): print(s); out.append(s)
    say(f"DDR3L {RATE:.0f} MT/s (UI {UI:.0f} ps), VDDQ {VDD} V, VTT {VTT} V, 250 ps edges; generic I/O, no IBIS")
    say(f"outer trace {PS_OUT:.3f} ps/mm, 56.1 ohm (neck-down {Z_NECK:.1f} ohm); via {BARREL * PS_IN * 1.2:.1f} ps, 45 ohm + 0.3 pF")
    bits = prbs7(127)
    DQ = [f"DDR_D{i}" for i in range(16)] + ["DDR_DQM0", "DDR_DQM1"]
    worst = sorted(DQ, key=delay, reverse=True)[:2] + sorted(DQ, key=delay)[:1]
    say("-- data, PRBS7, 60 ohm ODT to VTT + 1.5 pF at the receiver")
    for n in worst:
        for name, rs, rev in (("write, CPU 40 ohm", 40, False), ("write, CPU 34 ohm", 34, False), ("read, RAM 34 ohm", 34, True)):
            t, v = run([n], bits, rs, 60, 1.5, reverse=rev); h, w = eye(t, v[0], bits, delay(n), VTT)
            say(f"  {n:9s} {length(n):5.2f} mm {delay(n):6.1f} ps {sum(1 for p in pieces(n) if p[2] == 'via')} vias  {name}: eye height {h * 1000:4.0f} mV, width {w:4.0f} ps of {UI:.0f}; swing {min(v[0]):.3f}..{max(v[0]):.3f} V")
    say("-- address/command, unterminated (one device), PRBS7 at 400 MT/s (1T commands), 1.5 + 0.5 pF at the memory")
    ADDR = [f"DDR_A{i}" for i in range(16)] + ["DDR_BA0", "DDR_BA1", "DDR_BA2", "DDR_RASn", "DDR_CASn", "DDR_WEn", "DDR_CSn0", "DDR_CKE", "DDR_ODT"]
    ADDR = [a for a in ADDR if a in INV]
    for n in sorted(ADDR, key=delay, reverse=True)[:2]:
        for rs in (40, 34):
            cb = [b for b in bits[:64] for _ in (0, 1)]  # 1T: each command bit lasts one clock = two data UIs
            t, v = run([n], cb, rs, None, 2.0); vv = v[0]; h, w = eye(t, vv, cb, delay(n), VDD / 2)
            say(f"  {n:9s} {length(n):5.2f} mm, CPU {rs} ohm: overshoot {max(vv) - VDD:+.3f} V, undershoot {-min(vv):+.3f} V (DDR3L limit 0.4 V); levels open {h * 1000:4.0f} mV")
    say("-- pairs: complementary drive, crossing skew at the receiver and differential eye")
    for p, q, rs, term, rev, label in (("DDR_CK", "DDR_CKn", 40, None, False, "clock, CPU 40 ohm, unterminated"),
                                       ("DDR_DQS0", "DDR_DQSn0", 40, 60, False, "write strobe, CPU 40 ohm, ODT 60"), ("DDR_DQS0", "DDR_DQSn0", 34, 60, True, "read strobe, RAM 34 ohm"),
                                       ("DDR_DQS1", "DDR_DQSn1", 40, 60, False, "write strobe, CPU 40 ohm, ODT 60"), ("DDR_DQS1", "DDR_DQSn1", 34, 60, True, "read strobe, RAM 34 ohm")):
        ck = [k % 2 for k in range(100)]
        t, v = run([p, q], ck, rs, term, 2.0 if term is None else 1.5, invert=(q,), reverse=rev)
        th = (max(v[0][len(v[0]) // 3:]) + min(v[0][len(v[0]) // 3:])) / 2
        cp, cn = crossings(t, v[0], th), crossings(t, v[1], th)
        sk = [min(abs(a - b) for b in cn) for a in cp[10:80]] if cn else [float("nan")]
        dif = [a - b for a, b in zip(v[0], v[1])]; settle = [abs(x) for ti, x in zip(t, dif) if ti > 20 * UI]
        say(f"  {p}/{q} {label}: delay {delay(p):.1f} / {delay(q):.1f} ps, P/N crossing skew {sum(sk) / len(sk):.2f} ps (worst {max(sk):.2f}); differential peak {max(dif):.3f} / {min(dif):.3f} V")
    open(D + "/ddr_sim_results.txt", "w").write("\n".join(out) + "\n")
