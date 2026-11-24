# DC drop of each supply over all four inner layers at once (copper fill and skeletons on every layer, joined at the
# net's vias; 0.1 mm plated barrel through 1.0 mm board, 25 um plating = about 2.5 mOhm per via, layer to layer pro rata).
# Connector pin vias held at 0 V, load current drawn evenly at the chip's balls of that net. Sparse direct solve.
# Usage: python3 module/irdrop3d.py [module dir] [NET ...]   (KMAP=prefix writes a current-density picture per net)
import json, base64, os, sys, numpy as np
import scipy.sparse as sp, scipy.sparse.linalg as spl
d = sys.argv[1] if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else os.path.dirname(os.path.abspath(__file__))
only = [a for a in sys.argv[1:] if not os.path.isdir(a)]
R = json.load(open(d + '/planes-raster.json')); plan = json.load(open(d + '/plan.json'))
NX, NY, P, x0, y0 = R['NX'], R['NY'], R['P'], R['x0'], R['y0']; RS = 1.72e-8 / 17.5e-6  # ohm per square, 0.5 oz inner copper
ZL = [0.1, 0.4, 0.6, 0.9]  # rough depth of inner1..inner4 in a 1.0 mm board (mm)
RVIA_MM = 1.72e-8 / (np.pi * 0.125e-3 * 25e-6) * 1e-3  # plated barrel 0.1 mm hole + 25 um wall: ohm per mm of length
LOADS = {'VDD_CORE': {'U1': 0.4}, 'VDD_MPU': {'U1': 1.0}, 'VDDS_DDR': {'U1': 0.25, 'U_DDR': 0.35}, 'VDD_3V3': {'U1': 0.25}, 'VDD_1V8': {'U1': 0.2}}
Ls = np.stack([np.frombuffer(base64.b64decode(b), dtype=np.int8).reshape(NY, NX) for b in R['layers']])
res = {}
for net, loads in LOADS.items():
    if only and net not in only: continue
    k = R['nets'].index(net) + 1; own = Ls == k; n = int(own.sum()); ix = -np.ones(own.shape, np.int64); ix[own] = np.arange(n)
    cell = lambda v: (int((v['y'] - y0) / P), int((v['x'] - x0) / P))
    mine = [v for v in plan['vias'] if v['net'] == net]
    rows, cols, vals = [], [], []
    def link(a, b, g):
        rows.extend([a, b, a, b]); cols.extend([a, b, b, a]); vals.extend([g, g, -g, -g])
    G = 1 / RS
    for l in range(4):
        for ax in (1, 2):
            sl0 = [l, slice(None), slice(None)]; a = ix[l]; b = np.roll(ix[l], -1, axis=ax - 1)
            m = (a >= 0) & (b >= 0)
            if ax == 1: m[-1, :] = False
            else: m[:, -1] = False
            for p, q in zip(a[m], b[m]): link(p, q, G)
    for v in mine:
        j, i = cell(v); on = [l for l in range(4) if own[l, j, i]]
        for a, b in zip(on, on[1:]): link(ix[a, j, i], ix[b, j, i], 1 / (RVIA_MM * (ZL[b] - ZL[a])))
    A = sp.csr_matrix((vals, (rows, cols)), shape=(n, n))
    cur = np.zeros(n); miss = 0
    for chip, amps in loads.items():
        bv = [cell(v) for v in mine if (v.get('ball') or '').startswith(chip + '.')]
        for c in bv:
            on = [l for l in range(4) if own[l][c]]
            if not on: miss += 1; continue
            cur[ix[on[0]][c]] -= amps / len(bv)
    fixed = np.zeros(n, bool)
    for v in mine:
        if v['name'].startswith('V_J'):
            j, i = cell(v)
            for l in range(4):
                if own[l, j, i]: fixed[ix[l, j, i]] = True
    # only copper joined to a pin counts; the rest is left floating (reported)
    ncomp, lab = sp.csgraph.connected_components(A, directed=False)
    live = np.isin(lab, np.unique(lab[fixed]))
    fr = np.where(live & ~fixed)[0]; Aff = A[fr][:, fr].tocsc()
    x = np.zeros(n); x[fr] = spl.spsolve(Aff, cur[fr])  # potential (V) relative to the pins, negative = below
    V = np.full(own.shape, np.nan); V[own] = x
    balls = [-np.nanmin(V[:, c[0], c[1]]) * 1e3 for c in [cell(v) for v in mine if v.get('ball')] if own[:, c[0], c[1]].any()]
    gx = np.nan_to_num((V - np.roll(V, -1, axis=2)) / RS); gy = np.nan_to_num((V - np.roll(V, -1, axis=1)) / RS)
    gx[:, :, -1] = 0; gy[:, -1, :] = 0; K = np.hypot(gx, gy) / P; l, j, i = np.unravel_index(K.argmax(), K.shape)
    loss = ((gx ** 2 + gy ** 2) * RS).sum() * 1e3
    lost = int((cur[~live] != 0).sum())
    res[net] = dict(drop=max(balls), peak=float(K.max()), at=(round(x0 + i * P, 2), round(y0 + j * P, 2), f'inner{l + 1}'), hot=float((K > 1).sum() * P * P), loss=loss)
    print(f"{net:9s} {sum(loads.values()):.2f} A: worst ball {max(balls):.1f} mV below the connector pins; plane loss {loss:.1f} mW; peak current density {K.max():.2f} A/mm at {res[net]['at']}; copper above 1 A/mm {res[net]['hot']:.2f} mm2"
          + (f"; {miss} balls without copper" if miss else '') + (f"; {lost} balls not joined to the pins" if lost else ''), flush=True)
    if os.environ.get('KMAP'):
        from PIL import Image
        for l in range(4):
            if not own[l].any(): continue
            img = np.zeros((NY, NX, 3), np.uint8); img[Ls[l] > 0] = (35, 35, 35); t = np.clip(K[l] / 2.0, 0, 1); u = np.clip(K[l] / 0.5, 0, 1)
            img[own[l]] = np.stack([40 + 215 * t, 40 + 215 * u, 90 + 0 * t], -1)[own[l]].astype(np.uint8)
            Image.fromarray(img[::-1]).resize((NX * 2, NY * 2), Image.NEAREST).save(f"{os.environ['KMAP']}-{net}-inner{l + 1}.png")
if os.environ.get('JSON'): json.dump(res, open(os.environ['JSON'], 'w'), indent=1)
