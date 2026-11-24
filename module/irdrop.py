# DC drop estimate of the supply planes: connector pin vias held at 0 V, load current drawn at the chip balls.
# Single layer per net (the layer that carries its plane), 17.5 um copper (0.98 mOhm per square), conjugate gradient
# on the plane raster written by `DUMP=1 bun module/planes.ts`.
import json, base64, os, numpy as np
d = os.path.dirname(os.path.abspath(__file__)); R = json.load(open(d + '/planes-raster.json')); plan = json.load(open(d + '/plan.json'))
NX, NY, P, x0, y0 = R['NX'], R['NY'], R['P'], R['x0'], R['y0']; RS = 1.72e-8 / 17.5e-6
LOADS = {'VDD_CORE': (2, {'U1': 0.4}), 'VDD_MPU': (2, {'U1': 1.0}), 'VDDS_DDR': (1, {'U1': 0.25, 'U_DDR': 0.35}), 'VDD_3V3': (1, {'U1': 0.25}), 'VDD_1V8': (1, {'U1': 0.2})}
import sys
for net, (layer, loads) in LOADS.items():
    if len(sys.argv) > 1 and net not in sys.argv[1:]: continue
    k = R['nets'].index(net) + 1; own = np.frombuffer(base64.b64decode(R['layers'][layer]), dtype=np.int8).reshape(NY, NX) == k
    cell = lambda v: (int((v['y'] - y0) / P), int((v['x'] - x0) / P))
    pins = [cell(v) for v in plan['vias'] if v['net'] == net and v['name'].startswith('V_J')]
    # keep only the copper that is joined to the pins on this layer
    comp = np.zeros((NY, NX), bool); st = [c for c in pins if own[c]]
    for c in st: comp[c] = True
    while st:
        j, i = st.pop()
        for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b2 = j + dj, i + di
            if 0 <= a < NY and 0 <= b2 < NX and own[a, b2] and not comp[a, b2]: comp[a, b2] = True; st.append((a, b2))
    own = comp
    cur = np.zeros((NY, NX)); miss = 0
    for chip, amps in loads.items():
        bv = [cell(v) for v in plan['vias'] if v['net'] == net and (v.get('ball') or '').startswith(chip + '.')]
        for c in bv:
            if own[c]: cur[c] -= amps / len(bv)
            else: miss += 1
    fixed = np.zeros((NY, NX), bool)
    for c in pins:
        for dj in (-1, 0, 1):
            for di in (-1, 0, 1): fixed[c[0] + dj, c[1] + di] = own[c[0] + dj, c[1] + di]
    free = own & ~fixed
    def A(v):  # Laplacian on the copper cells (neighbours outside copper carry no current; fixed cells are 0 V)
        v = np.where(free, v, 0.0); out = np.zeros_like(v)
        for ax, sh in ((0, 1), (0, -1), (1, 1), (1, -1)):
            nb = np.roll(v, sh, axis=ax); m = np.roll(own, sh, axis=ax)
            out += np.where(m, v - nb, 0.0)
        return np.where(free, out / RS, 0.0)
    b = np.where(free, cur, 0.0); x = np.zeros_like(b); r = b - A(x); p = r.copy(); rs = (r * r).sum()
    for it in range(6000):
        Ap = A(p); a = rs / (p * Ap).sum(); x += a * p; r -= a * Ap; rn = (r * r).sum()
        if rn < 1e-22: break
        p = r + (rn / rs) * p; rs = rn
    worst = -x[own].min() * 1e3
    gx = np.where(own & np.roll(own, -1, axis=1), (x - np.roll(x, -1, axis=1)) / RS, 0.0); gy = np.where(own & np.roll(own, -1, axis=0), (x - np.roll(x, -1, axis=0)) / RS, 0.0)
    K = np.hypot(gx, gy) / P; jmax, imax = np.unravel_index(K.argmax(), K.shape)  # sheet current density, A per mm of copper width
    if os.environ.get('KMAP'):
        from PIL import Image
        img = np.zeros((NY, NX, 3), np.uint8); img[own] = (40, 40, 90); t = np.clip(K / 2.0, 0, 1); img[own, 0] = (40 + 215 * t[own]).astype(np.uint8); img[own, 1] = (40 + 215 * np.clip(K[own] / 0.5, 0, 1)).astype(np.uint8)
        Image.fromarray(img[::-1]).resize((NX * 4, NY * 4), Image.NEAREST).save(os.environ['KMAP'] + '-' + net + '.png')
    loss = ((gx ** 2 + gy ** 2) * RS).sum() * 1e3
    print(f"          peak current density {K.max():.2f} A/mm at ({x0 + imax * P:.2f}, {y0 + jmax * P:.2f}) (0.15 mm inner trace at 10 K rise: about 2 A/mm); copper above 1 A/mm: {(K > 1).sum() * P * P:.2f} mm2; total loss {loss:.1f} mW")
    print(f"{net:9s} on {['inner1','inner2','inner3','inner4'][layer]}: {sum(loads.values()):.2f} A, {len(pins)} pin vias, worst drop {worst:.1f} mV ({it} iterations{', %d balls not on this layer' % miss if miss else ''})")
