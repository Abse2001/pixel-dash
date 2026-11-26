# DC drop of each supply over all four inner layers at once (the copper `planes.ts` builds: fills and skeletons on
# every layer, joined at the net's vias; 0.1 mm plated barrel through a 1.0 mm board, 25 um plating). Adapted from
# module/irdrop3d.py: here the supplies start at the module's own regulators (inductor output vias held at 0 V) and the
# load is drawn at the chips' balls and, for 3.3 V / 1.8 V, at the CM4 pins that feed the carrier.
# Usage: DUMP=1 bun planes.ts; python3 irdrop.py [CARRIER_A] (current the carrier draws on 3.3 V and on 1.8 V, default 0.6
# A each, the CM4's own limit). KMAP=prefix writes a current-density picture per net and layer.
import json, base64, os, re, sys, numpy as np
import scipy.sparse as sp, scipy.sparse.linalg as spl
from scipy.sparse import csgraph
d = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(d + '/planes-raster.json')); plan = json.load(open(d + '/plan.json'))
NX, NY, P, x0, y0 = R['NX'], R['NY'], R['P'], R['x0'], R['y0']; RS = 1.72e-8 / 17.5e-6  # ohm per square, 0.5 oz inner copper
ZL = [0.1, 0.4, 0.6, 0.9]  # rough depth of inner1..inner4 in the 1.0 mm board (mm)
RVIA_MM = 1.72e-8 / (np.pi * 0.125e-3 * 25e-6) * 1e-3  # plated barrel, 0.1 mm hole + 25 um wall: ohm per mm of length
CAR = float(sys.argv[1]) if len(sys.argv) > 1 else 0.6
# net: (source vias, {load via pattern: amps}); a pattern 'U1.' / 'U_DDR.' means that chip's balls of the net
LOADS = {
    'VDD_CORE': (r'^V_L_DCDC3_pin2', {'U1.': 0.4}),
    'VDD_MPU': (r'^V_L_DCDC2_pin2', {'U1.': 1.0}),
    'VDDS_DDR': (r'^V_L_DCDC1_pin2', {'U1.': 0.25, 'U_DDR.': 0.35}),
    'VDD_3V3': (r'^V_L_3V3_pin2', {'U1.': 0.25, r'^V_J1_pin(84|86)$': CAR}),
    'VDD_1V8': (r'^V_L_1V8_pin2', {'U1.': 0.2, r'^V_J1_pin(88|90)$': CAR}),
    # 5 V input: from the CM4 pins to the PMIC's AC input and the two bucks (their input current at about 85 %)
    'VIN5': (r'^V_J1_pin(77|79|81|83|85|87)$', {r'^V_U_PMIC_pin10$': 0.6, r'^V_U_3V3_pin4$': (0.25 + CAR) * 3.3 / 5 / 0.85, r'^V_U_1V8_pin4$': (0.2 + CAR) * 1.8 / 5 / 0.85}),
}
Ls = np.stack([np.frombuffer(base64.b64decode(b), dtype=np.int8).reshape(NY, NX) for b in R['layers']])
cell = lambda v: (int((v['y'] - y0) / P), int((v['x'] - x0) / P))
res = {}
print(f"carrier load on 3.3 V and 1.8 V: {CAR:.2f} A each")
for net, (src, loads) in LOADS.items():
    k = R['nets'].index(net) + 1; own = Ls == k; n = int(own.sum()); ix = -np.ones(own.shape, np.int64); ix[own] = np.arange(n)
    mine = [v for v in plan['vias'] if v['net'] == net]
    rows, cols, vals = [], [], []
    def link(a, b, g): rows.extend([a, b, a, b]); cols.extend([a, b, b, a]); vals.extend([g, g, -g, -g])
    G = 1 / RS
    for l in range(4):
        for ax in (0, 1):
            a = ix[l]; b = np.roll(ix[l], -1, axis=ax); m = (a >= 0) & (b >= 0)
            if ax == 0: m[-1, :] = False
            else: m[:, -1] = False
            for p, q in zip(a[m], b[m]): link(p, q, G)
    for v in mine:
        j, i = cell(v); on = [l for l in range(4) if own[l, j, i]]
        for a, b in zip(on, on[1:]): link(ix[a, j, i], ix[b, j, i], 1 / (RVIA_MM * (ZL[b] - ZL[a])))
    A = sp.csr_matrix((vals, (rows, cols)), shape=(n, n))
    cur = np.zeros(n); miss = 0; tot = 0
    for pat, amps in loads.items():
        bv = [cell(v) for v in mine if ((v.get('ball') or '').startswith(pat) if pat.endswith('.') else re.search(pat, v['name']))]
        assert bv, (net, pat)
        tot += amps
        for c in bv:
            on = [l for l in range(4) if own[l][c]]
            if not on: miss += 1; continue
            cur[ix[on[0]][c]] -= amps / len(bv)
    fixed = np.zeros(n, bool); srcs = [v for v in mine if re.search(src, v['name'])]; assert srcs, net
    for v in srcs:
        j, i = cell(v)
        for l in range(4):
            if own[l, j, i]: fixed[ix[l, j, i]] = True
    ncomp, lab = csgraph.connected_components(A, directed=False)
    live = np.isin(lab, np.unique(lab[fixed]))
    fr = np.where(live & ~fixed)[0]; Aff = A[fr][:, fr].tocsc()
    x = np.zeros(n); x[fr] = spl.spsolve(Aff, cur[fr])  # potential (V) relative to the source, negative = below
    V = np.full(own.shape, np.nan); V[own] = x
    ends = [cell(v) for v in mine if v.get('ball') or any(not p.endswith('.') and re.search(p, v['name']) for p in loads)]
    drops = [-np.nanmin(V[:, c[0], c[1]]) * 1e3 for c in ends if own[:, c[0], c[1]].any()]
    gx = np.nan_to_num((V - np.roll(V, -1, axis=2)) / RS); gy = np.nan_to_num((V - np.roll(V, -1, axis=1)) / RS)
    gx[:, :, -1] = 0; gy[:, -1, :] = 0; K = np.hypot(gx, gy) / P; l, j, i = np.unravel_index(K.argmax(), K.shape)
    loss = ((gx ** 2 + gy ** 2) * RS).sum() * 1e3
    lost = int((cur[~live] != 0).sum())
    res[net] = dict(amps=tot, drop_mV=round(max(drops), 2), peak_A_per_mm=round(float(K.max()), 2), at=(round(float(x0 + i * P), 2), round(float(y0 + j * P), 2), f'inner{l + 1}'), above_1A_per_mm_mm2=round(float((K > 1).sum() * P * P), 3), loss_mW=round(loss, 2))
    print(f"{net:9s} {tot:.2f} A: worst load {max(drops):.1f} mV below the source; plane loss {loss:.1f} mW; peak current density {K.max():.2f} A/mm at {res[net]['at']}; copper above 1 A/mm {res[net]['above_1A_per_mm_mm2']:.2f} mm2"
          + (f"; {miss} loads without copper" if miss else '') + (f"; {lost} loads not joined to the source" if lost else ''), flush=True)
    if os.environ.get('KMAP'):
        from PIL import Image
        for l in range(4):
            if not own[l].any(): continue
            img = np.zeros((NY, NX, 3), np.uint8); img[Ls[l] > 0] = (35, 35, 35); t = np.clip(K[l] / 2.0, 0, 1); u = np.clip(K[l] / 0.5, 0, 1)
            img[own[l]] = np.stack([40 + 215 * t, 40 + 215 * u, 90 + 0 * t], -1)[own[l]].astype(np.uint8)
            Image.fromarray(img[::-1]).resize((NX * 2, NY * 2), Image.NEAREST).save(f"{os.environ['KMAP']}-{net}-inner{l + 1}.png")
if os.environ.get('JSON'): json.dump(res, open(os.environ['JSON'], 'w'), indent=1)
