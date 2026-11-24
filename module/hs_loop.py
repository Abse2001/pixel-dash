# Spreading inductance of each processor DDR bypass capacitor into the VDDS_DDR / GND plane pair (inner2 over the
# inner1 ground): L = mu0 * d * (squares between the capacitor's VDDS_DDR via and the processor's VDDS_DDR ball vias),
# solved on the plane raster (planes-raster.json). Run twice: on the real copper (with the 0.14-0.15 mm webs) and on
# an ideal plane that only has the antipads of the other nets' vias. The difference is what the webs cost.
# Usage: python3 module/hs_loop.py [d_mm]   (d = inner1-inner2 dielectric, default 0.1 mm)
import json, base64, os, sys, numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl
d = os.path.dirname(os.path.abspath(__file__)); R = json.load(open(d + '/planes-raster.json')); plan = json.load(open(d + '/plan.json'))
NX, NY, P, x0, y0 = R['NX'], R['NY'], R['P'], R['x0'], R['y0']; H = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
k = R['nets'].index('VDDS_DDR') + 1; lay = 1  # inner2
own = np.frombuffer(base64.b64decode(R['layers'][lay]), dtype=np.int8).reshape(NY, NX) == k
cell = lambda v: (int((v['y'] - y0) / P), int((v['x'] - x0) / P))
# ideal copper: the whole processor/bypass area, minus the antipads (0.3 mm pad + 0.125 mm) of every foreign via
ideal = np.ones((NY, NX), bool)
ys, xs = (np.arange(NY) + 0.5) * P + y0, (np.arange(NX) + 0.5) * P + x0
for v in plan['vias']:
    if v['net'] == 'VDDS_DDR': continue
    j0, i0 = cell(v); r = int(0.3 / P) + 2
    for j in range(max(0, j0 - r), min(NY, j0 + r + 1)):
        for i in range(max(0, i0 - r), min(NX, i0 + r + 1)):
            if np.hypot(max(abs(xs[i] - v['x']) - P / 2, 0), max(abs(ys[j] - v['y']) - P / 2, 0)) < 0.15 + 0.125: ideal[j, i] = False
balls = [cell(v) for v in plan['vias'] if v['net'] == 'VDDS_DDR' and (v.get('ball') or '').startswith('U1.')]
caps = [p for p in plan['parts'] if p['name'].startswith('C_HS_CPU')]
def capvia(p):
    vs = [v for v in plan['vias'] if v['net'] == 'VDDS_DDR' and np.hypot(v['x'] - p['x'], v['y'] - p['y']) < 0.8]
    return min(vs, key=lambda v: np.hypot(v['x'] - p['x'], v['y'] - p['y'])) if vs else None
def squares(m):
    n = int(m.sum()); ix = -np.ones(m.shape, np.int64); ix[m] = np.arange(n); r, c = [], []
    for a, b in ((ix[:, :-1], ix[:, 1:]), (ix[:-1, :], ix[1:, :])):
        q = (a >= 0) & (b >= 0); r += [a[q], b[q]]; c += [b[q], a[q]]
    r = np.concatenate(r); c = np.concatenate(c); A = sp.csr_matrix((np.ones(len(r)), (r, c)), shape=(n, n))
    A = sp.diags(np.asarray(A.sum(1)).ravel()) - A
    fixed = np.zeros(n, bool)
    for b in balls:
        if m[b]: fixed[ix[b]] = True
    from scipy.sparse.csgraph import connected_components
    _, lab = connected_components(A, directed=False); live = np.isin(lab, np.unique(lab[fixed]))
    fr = np.where(~fixed & live)[0]; lu = spl.splu(A[fr][:, fr].tocsc()); pos = -np.ones(n, np.int64); pos[fr] = np.arange(len(fr)); out = {}
    for p in caps:
        v = capvia(p)
        if v is None: continue
        c0 = cell(v)
        if not m[c0]: out[p['name']] = None; continue
        if fixed[ix[c0]]: out[p['name']] = 0.0; continue
        if not live[ix[c0]]: out[p['name']] = None; continue
        b = np.zeros(len(fr)); b[pos[ix[c0]]] = 1.0; out[p['name']] = float(lu.solve(b)[pos[ix[c0]]])
    return out
real, ide = squares(own), squares(ideal)
mu0 = 4e-7 * np.pi; f = mu0 * H * 1e-3 * 1e12  # pH per square
print(f"processor DDR bypass capacitors: plane spreading inductance VDDS_DDR (inner2) over GND (inner1), d = {H} mm ({f:.0f} pH per square)")
print("capacitor            real copper | ideal plane | added by the webs")
tot_r = tot_i = 0; rows = []
for name in sorted(real, key=lambda n: -(real[n] or 0)):
    r, i = real[name], ide.get(name)
    if r is None or i is None: print(f"{name:20s} not on inner2"); continue
    rows.append((name, r * f, i * f)); print(f"{name:20s} {r*f:7.0f} pH | {i*f:7.0f} pH | {(r - i)*f:+6.0f} pH")
# the twenty in parallel, as the processor's DDR I/O sees them (each loop also has its two vias, about 400-500 pH)
via = 450.0
par = lambda xs: 1 / sum(1 / (x + via) for x in xs)
print(f"all {len(rows)} in parallel incl. {via:.0f} pH of via per capacitor: real {par([r for _, r, _ in rows]):.0f} pH, ideal {par([i for _, _, i in rows]):.0f} pH")
