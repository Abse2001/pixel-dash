# 2D finite-difference field solver for the outer DDR traces: surface microstrip with solder mask over the
# reference plane on layer 2. Z0 = 1 / (c * sqrt(C * C_air)), C from the Laplace solution with and without dielectrics.
# Also the CK pair (odd / differential impedance). Sweeps the prepregs JLCPCB uses in its 6-layer stacks.
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl, sys
D = 0.0025  # grid, mm
def solve(W=0.102, T=0.035, H=0.0764, er=3.91, mask=0.015, er_mask=3.8, gap=None, even=False):
    X, Y = 1.6, 0.6; nx, ny = int(X / D), int(Y / D)
    eps = np.ones((ny, nx)); yh = int(H / D); yt = yh + int(T / D)
    eps[:yh, :] = er
    xs = [(-W / 2, W / 2)] if gap is None else [(-gap / 2 - W, -gap / 2), (gap / 2, gap / 2 + W)]
    cond = np.zeros((ny, nx), int)  # 0 free, 1.. conductor index
    xc = (np.arange(nx) + 0.5) * D - X / 2
    for k, (a, b) in enumerate(xs): cond[yh:yt, (xc >= a) & (xc <= b)] = k + 1
    # mask: conformal 'mask' thickness over the dielectric and around the traces
    m = np.zeros((ny, nx), bool); r = int(mask / D)
    tr = cond > 0
    from scipy.ndimage import binary_dilation
    m |= binary_dilation(tr, iterations=r); m[yh:yh + r, :] = True; m &= ~tr; m[:yh, :] = False
    eps_m = eps.copy(); eps_m[m] = er_mask
    def cap(epsg, volts):
        N = nx * ny; idx = np.arange(N).reshape(ny, nx)
        fixed = np.zeros((ny, nx), bool); val = np.zeros((ny, nx)); fixed[0, :] = True  # ground plane at the bottom
        for k, v in enumerate(volts): fixed[cond == k + 1] = True; val[cond == k + 1] = v
        rows, cols, data = [], [], []; b = np.zeros(N)
        for dj, di in ((0, 1), (1, 0)):
            a0 = idx[:ny - dj, :nx - di].ravel(); a1 = idx[dj:, di:].ravel()
            e = 0.5 * (epsg[:ny - dj, :nx - di] + epsg[dj:, di:]).ravel()
            rows += [a0, a1, a0, a1]; cols += [a0, a1, a1, a0]; data += [e, e, -e, -e]
        A = sp.csr_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(N, N))
        f = fixed.ravel(); u = val.ravel().copy(); fr = ~f
        u[fr] = spl.spsolve(A[fr][:, fr].tocsc(), -A[fr][:, f] @ u[f])
        return 8.854e-12 * u @ (A @ u)  # energy form: C V^2 (per metre, grid-size independent in 2D)
    c0 = 299792458.0
    if gap is None:
        C, Ca = cap(eps_m, [1.0]), cap(np.ones_like(eps), [1.0])
        return 1 / (c0 * np.sqrt(C * Ca)), np.sqrt(C / Ca)
    C, Ca = cap(eps_m, [1.0, -1.0]), cap(np.ones_like(eps), [1.0, -1.0])  # odd mode, energy of both lines at +-1 V
    Zodd = 1 / (c0 * np.sqrt((C / 2) * (Ca / 2)))  # per line
    if not even: return Zodd, 2 * Zodd
    Ce, Cea = cap(eps_m, [1.0, 1.0]), cap(np.ones_like(eps), [1.0, 1.0])
    Zeven = 1 / (c0 * np.sqrt((Ce / 2) * (Cea / 2)))
    return dict(Zodd=Zodd, Zeven=Zeven, eodd=C / Ca, eeven=Ce / Cea, Codd=C, Cair_odd=Ca, Ceven=Ce, Cair_even=Cea)
if __name__ == '__main__':
    print("outer DDR trace 0.102 mm, 35 um copper, 15 um mask (er 3.8), reference = layer 2 ground")
    print("prepreg L1-L2              | Z0 single | eff. er | CK pair (0.102 / 0.1 gap): Zodd, Zdiff")
    for name, h, er in [("1080  0.0764 mm er 3.91", 0.0764, 3.91), ("3313  0.0994 mm er 4.10", 0.0994, 4.10),
                        ("2116  0.1194 mm er 4.16", 0.1194, 4.16), ("7628  0.2104 mm er 4.40", 0.2104, 4.40)]:
        z, ee = solve(H=h, er=er); zo, zd = solve(H=h, er=er, gap=0.1)
        print(f"{name:26s} | {z:6.1f} ohm | {ee**2:5.2f}   | {zo:5.1f} / {zd:5.1f} ohm", flush=True)
