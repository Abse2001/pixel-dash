// Inner-layer copper for the module: L2 GND, L3 VDDS_DDR (west) + 3V3 / 1V8 (east), L4 core / MPU / VREF and the
// few local nets that cannot run on the outer layers, L5 GND.
// Every net first gets a 0.15 mm skeleton that reaches each of its vias (so connectivity never depends on the
// fill), then the free copper is filled, kept clear of other nets and stripped of slivers and islands.
// Output: module/pours.json (polygons with holes per layer/net) and a connectivity + clearance report.
import type { Pt } from "./geom"
const dir = import.meta.dir
const plan = await Bun.file(dir + "/plan.json").json(), items = (await Bun.file(dir + "/plan-items.json").json()).items as any[]
const routes = (await Bun.file(dir + "/routes.json").exists()) ? await Bun.file(dir + "/routes.json").json() : { nets: {} }
const P = 0.05, E = plan.edge, NX = Math.round((E.x1 - E.x0) / P), NY = Math.round((E.y1 - E.y0) / P), NN = NX * NY
const cx = (i: number) => E.x0 + (i + 0.5) * P, cy = (j: number) => E.y0 + (j + 0.5) * P
const LAYERS = ["inner1", "inner2", "inner3", "inner4"] as const
const XB = +(process.env.XB ?? -46.4) // layer 3: VDDS_DDR west of this, 3V3 / 1V8 east of it
// trunk order, with the layers a net may use (first = preferred) and where it is filled
// skeleton order: the nets with the fewest ways through first, the big planes last
// the 3V3 balls N5, P5, P6, P7 sit west of the layer-3 split: this corner of layer 3 is 3V3 too
const SW = (x: number, y: number) => x > -49.1 && x < XB && y > 10.9 && y < 12.0 // row P only: N6 above it is a 1V8 ball
const NETS: { name: string; layers: number[]; fill: Record<number, (x: number, y: number) => boolean> }[] = [
  { name: "GND", layers: [0], fill: { 0: () => true, 3: () => true } },
  ...["VDDS_RTC", ...plan.innerNets].map((name: string) => ({ name, layers: [2, 1], fill: {} })),
  { name: "DDR_VREF", layers: [1, 2], fill: { 2: (x: number, y: number) => x < -53 && x > -76 && y > 9 && y < 21 } }, // the channel between the two chips; the rest of layer 4 is left to core and MPU,
  { name: "VDD_3V3", layers: [1, 2], fill: { 1: (x: number, y: number) => x >= XB || SW(x, y) } },
  { name: "VDD_1V8", layers: [1, 2], fill: { 2: (x: number, y: number) => x >= XB && y < 13 } }, // layer 3 east is the 3V3 plane; 1V8 fills the lower part of layer 4 and runs fattened feeds elsewhere
  { name: "VDDS_DDR", layers: [1, 2], fill: { 1: (x: number, y: number) => x < XB && !SW(x, y) } },
  { name: "VDD_MPU", layers: [2, 1], fill: { 2: () => true } },
  { name: "VDD_CORE", layers: [2, 1], fill: { 2: () => true } },
]
const CENTRE4 = new Set(["VDD_CORE", "VDD_MPU"]), CENTRE3 = new Set(["VDD_1V8", "VDD_3V3", "VDDS_DDR"]) // who may cross the middle of the processor on layers 4 / 3 cheaply
const idx = new Map(NETS.map((n, i) => [n.name, i + 1]))
// ---------- vias ----------
type V = { x: number; y: number; d: number; net: string }
const vias: V[] = plan.vias.map((v: any) => ({ x: v.x, y: v.y, d: v.d, net: v.net }))
for (const it of items) if (it.kind === "ddrvia" && !vias.some((v) => Math.hypot(v.x - it.pts[0].x, v.y - it.pts[0].y) < 0.01)) vias.push({ x: it.pts[0].x, y: it.pts[0].y, d: it.r * 2, net: it.net })
for (const [name, n] of Object.entries(routes.nets) as any) for (const v of n.vias) vias.push({ x: v.x, y: v.y, d: v.d, net: name })
// a plane net may also have to be reached at through vias of local parts joined by outer-layer traces only: none here
const ci = (x: number) => Math.floor((x - E.x0) / P), cj = (y: number) => Math.floor((y - E.y0) / P)
// ---------- static: who may have copper in a cell (0 anybody, k only net k, 127 nobody) ----------
const ANTI = +(process.env.ANTI ?? 0.125) // copper to via pad: 0.2 mm to the wall of a 0.1 mm hole (JLCPCB inner layers: 0.2 mm), 0.3 mm webs between ball vias
const stat = new Int8Array(NN)
for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) { const x = cx(i), y = cy(j); if (x < E.x0 + 0.3 || x > E.x1 - 0.3 || y < E.y0 + 0.3 || y > E.y1 - 0.3) stat[j * NX + i] = 127 }
for (const h of plan.holes) { const R = h.d / 2 + 0.4; for (let j = cj(h.y - R); j <= cj(h.y + R); j++) for (let i = ci(h.x - R); i <= ci(h.x + R); i++) if (i >= 0 && j >= 0 && i < NX && j < NY && Math.hypot(cx(i) - h.x, cy(j) - h.y) < R) stat[j * NX + i] = 127 }
for (const v of vias) { const R = Math.max(v.d, 0.3) / 2 + ANTI, k = idx.get(v.net) ?? 127 // exact: a cell is closed when any part of its square is nearer than R
  for (let j = Math.max(0, cj(v.y - R) - 1); j <= Math.min(NY - 1, cj(v.y + R) + 1); j++) for (let i = Math.max(0, ci(v.x - R) - 1); i <= Math.min(NX - 1, ci(v.x + R) + 1); i++) if (Math.hypot(Math.max(Math.abs(cx(i) - v.x) - P / 2, 0), Math.max(Math.abs(cy(j) - v.y) - P / 2, 0)) < R - 1e-9) { const c = j * NX + i; stat[c] = stat[c] === 0 || stat[c] === k ? k : 127 } }
// signal traces on an inner layer: no plane copper within 0.15 mm of them
const blockL = LAYERS.map(() => new Uint8Array(NN))
for (const n of Object.values(routes.nets) as any[]) for (const g of n.segs) { const l = LAYERS.indexOf(g.layer); if (l < 0) continue
  for (let i = 0; i + 1 < g.pts.length; i++) { const a = g.pts[i], b = g.pts[i + 1], R = 0.05 + 0.15 + P / 2, dx = b.x - a.x, dy = b.y - a.y, len2 = dx * dx + dy * dy
    for (let j = Math.max(0, cj(Math.min(a.y, b.y) - R)); j <= Math.min(NY - 1, cj(Math.max(a.y, b.y) + R)); j++) for (let i2 = Math.max(0, ci(Math.min(a.x, b.x) - R)); i2 <= Math.min(NX - 1, ci(Math.max(a.x, b.x) + R)); i2++) { const t = len2 ? Math.max(0, Math.min(1, ((cx(i2) - a.x) * dx + (cy(j) - a.y) * dy) / len2)) : 0
      if (Math.hypot(cx(i2) - a.x - t * dx, cy(j) - a.y - t * dy) < R) blockL[l][j * NX + i2] = 1 } } }
for (const g of plan.ddrInner ?? []) { const l = 2, a = g.a, b = g.b, R = 0.051 + 0.15 + P / 2, dx = b.x - a.x, dy = b.y - a.y, len2 = dx * dx + dy * dy // DDR sections on layer 4
  for (let j = Math.max(0, cj(Math.min(a.y, b.y) - R)); j <= Math.min(NY - 1, cj(Math.max(a.y, b.y) + R)); j++) for (let i2 = Math.max(0, ci(Math.min(a.x, b.x) - R)); i2 <= Math.min(NX - 1, ci(Math.max(a.x, b.x) + R)); i2++) { const t = len2 ? Math.max(0, Math.min(1, ((cx(i2) - a.x) * dx + (cy(j) - a.y) * dy) / len2)) : 0; if (Math.hypot(cx(i2) - a.x - t * dx, cy(j) - a.y - t * dy) < R) blockL[l][j * NX + i2] = 1 } }
// ---------- per-layer ownership ----------
const owner = LAYERS.map(() => new Int8Array(NN)), trunk = LAYERS.map(() => new Uint8Array(NN))
const report: string[] = []
/** cells where a (2k+1) square of the given predicate is all true */
function boxAll(pred: (c: number) => boolean, k: number): Uint8Array { const S = new Int32Array((NX + 1) * (NY + 1))
  for (let j = 0; j < NY; j++) { let row = 0; for (let i = 0; i < NX; i++) { row += pred(j * NX + i) ? 0 : 1; S[(j + 1) * (NX + 1) + i + 1] = S[j * (NX + 1) + i + 1] + row } }
  const out = new Uint8Array(NN)
  for (let j = k; j < NY - k; j++) for (let i = k; i < NX - k; i++) { const a = S[(j - k) * (NX + 1) + i - k], b = S[(j - k) * (NX + 1) + i + k + 1], c = S[(j + k + 1) * (NX + 1) + i - k], d = S[(j + k + 1) * (NX + 1) + i + k + 1]; if (d - b - c + a === 0) out[j * NX + i] = 1 }
  return out }
const TK = 1, GAPK = 4 // skeleton half-width (cells) and its distance to other nets' copper (cells)
const D8 = [1, 0, -1, 0, 0, 1, 0, -1, 1, 1, 1, -1, -1, 1, -1, -1]
for (const [ni, net] of NETS.entries()) { const k = ni + 1, mine = vias.filter((v) => v.net === net.name); if (!mine.length) continue
  const cellOf = (v: V) => cj(v.y) * NX + ci(v.x)
  const valid = net.layers.map((l) => { const a = boxAll((c) => (stat[c] === 0 || stat[c] === k) && !blockL[l][c], TK), b = boxAll((c) => owner[l][c] === 0 || owner[l][c] === k, GAPK); for (let c = 0; c < NN; c++) a[c] &= b[c]; return a })
  const connected = new Uint8Array(mine.length), byCell = new Map<number, number[]>(); mine.forEach((v, m) => { const c = cellOf(v); byCell.set(c, [...(byCell.get(c) ?? []), m]) })
  const claim = (l: number, c: number) => { const i = c % NX, j = (c / NX) | 0; for (let dj = -TK; dj <= TK; dj++) for (let di = -TK; di <= TK; di++) { const c2 = (j + dj) * NX + i + di; owner[l][c2] = k; trunk[l][c2] = 1 } }
  // start at a connector pin of the net when it has one
  const start = Math.max(0, mine.findIndex((v) => plan.vias.some((p: any) => /^V_J/.test(p.name) && p.x === v.x && p.y === v.y)))
  // cheapest-first search over every allowed layer at once; a reached via feeds all layers and the search goes on
  { const L = net.layers, dist = L.map(() => new Float32Array(NN).fill(1e9)), pred = L.map(() => new Int32Array(NN).fill(-1)), heap: number[] = [], key: number[] = []
    const hpush = (kk: number, n: number) => { let i = heap.length; heap.push(n); key.push(kk); while (i > 0) { const p = (i - 1) >> 1; if (key[p] <= key[i]) break; [heap[p], heap[i]] = [heap[i], heap[p]]; [key[p], key[i]] = [key[i], key[p]]; i = p } }
    const hpop = () => { const top = heap[0], tk = key[0], n = heap.pop()!, kk = key.pop()!; if (heap.length) { heap[0] = n; key[0] = kk; let i = 0; for (;;) { const a = 2 * i + 1, b = a + 1; let m = i; if (a < heap.length && key[a] < key[m]) m = a; if (b < heap.length && key[b] < key[m]) m = b; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; [key[m], key[i]] = [key[i], key[m]]; i = m } } return [top, tk] }
    const factor = (s: number, c: number) => { const l = L[s], x = cx(c % NX), y = cy((c / NX) | 0), centre = x > -48.0 && x < -41.6 && y > 11.9 && y < 18.4
      return (s === 0 ? 1 : 4) * (centre && l === 2 && !CENTRE4.has(net.name) ? 30 : 1) * (centre && l === 1 && !CENTRE3.has(net.name) ? 8 : 1) }
    const feed = (m: number) => { connected[m] = 1; const c = cellOf(mine[m]); L.forEach((_, s) => { if (valid[s][c]) { dist[s][c] = 0; pred[s][c] = -1; hpush(0, s * NN + c) } }) }
    feed(start)
    while (heap.length) { const [u, du] = hpop(), s = (u / NN) | 0, c = u % NN, l = L[s]; if (du > dist[s][c]) continue
      const i = c % NX, j = (c / NX) | 0
      for (const m of byCell.get(c) ?? []) if (!connected[m]) { const way: number[] = []; for (let b = c; b !== -1; b = pred[s][b]) { way.push(b); if (trunk[l][b] && owner[l][b] === k) break }
        for (const b of way) claim(l, b); feed(m) }
      for (let d = 0; d < 16; d += 2) { const ii = i + D8[d], jj = j + D8[d + 1]; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY) continue; const c2 = jj * NX + ii; if (!valid[s][c2]) continue
        const nd = Math.fround(dist[s][c] + (d < 8 ? 1 : 1.4142) * factor(s, c2)); if (nd < dist[s][c2]) { dist[s][c2] = nd; pred[s][c2] = c; hpush(nd, s * NN + c2) } } } }
  const miss = mine.filter((_, m) => !connected[m])
  report.push(`${net.name}: ${mine.length - miss.length}/${mine.length} vias on the skeleton${miss.length ? " !! missing " + miss.slice(0, 6).map((v) => `(${v.x.toFixed(2)}, ${v.y.toFixed(2)})`).join(" ") : ""}`) }
// ---------- fill ----------
const FG = 3 // fill copper stays this many cells (0.15 mm + cell) from another net's copper
for (const [l] of LAYERS.entries()) { const own = owner[l], fillers = NETS.map((n, ni) => ({ k: ni + 1, f: n.fill[l] })).filter((n) => n.f)
  // skeletons of nets that are only passing through this layer are fattened to about 0.45 mm where there is room
  for (let pass = 0; pass < 3; pass++) { const grow: number[] = []
    for (let c = 0; c < NN; c++) { const k = own[c]; if (!k || fillers.some((f) => f.k === k)) continue; const i = c % NX, j = (c / NX) | 0
      for (let d = 0; d < 8; d += 2) { const ii = i + D8[d], jj = j + D8[d + 1]; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY) continue; const c2 = jj * NX + ii; if (own[c2] === 0 && (stat[c2] === 0 || stat[c2] === k) && !blockL[l][c2]) grow.push(c2, k) } }
    for (let g = 0; g < grow.length; g += 2) if (own[grow[g]] === 0) own[grow[g]] = grow[g + 1] }
  // seeds: skeleton cells and the cells around the net's own vias
  const q: number[] = []
  for (const v of vias) { const k = idx.get(v.net); if (!k || !fillers.some((f) => f.k === k)) continue; const c = cj(v.y) * NX + ci(v.x); if (own[c] === 0 && (stat[c] === 0 || stat[c] === k) && !blockL[l][c]) own[c] = k }
  for (let c = 0; c < NN; c++) if (own[c] && fillers.some((f) => f.k === own[c])) q.push(c)
  for (let h = 0; h < q.length; h++) { const c = q[h], k = own[c], i = c % NX, j = (c / NX) | 0, f = fillers.find((n) => n.k === k)!.f!
    for (let d = 0; d < 8; d += 2) { const ii = i + D8[d], jj = j + D8[d + 1]; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY) continue; const c2 = jj * NX + ii
      if (own[c2] === 0 && (stat[c2] === 0 || stat[c2] === k) && !blockL[l][c2] && f(cx(ii), cy(jj))) { own[c2] = k; q.push(c2) } } }
  // clearance between nets: fill cells near another net's copper go (skeletons stay: they were routed with clearance)
  const near = new Int8Array(NN)
  for (let c = 0; c < NN; c++) { if (!own[c] || trunk[l][c]) continue; const i = c % NX, j = (c / NX) | 0
    search: for (let dj = -FG - 1; dj <= FG + 1; dj++) for (let di = -FG - 1; di <= FG + 1; di++) { const ii = i + di, jj = j + dj; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY || Math.hypot(di, dj) > FG + 1) continue; const o = own[jj * NX + ii]; if (o && o !== own[c]) { near[c] = 1; break search } } }
  for (let c = 0; c < NN; c++) if (near[c]) own[c] = 0
  // slivers: keep fill only where a 0.15 mm square fits (opening), skeletons untouched
  for (const f of fillers) { const core = boxAll((c) => own[c] === f.k, 1), keep = new Uint8Array(NN)
    for (let c = 0; c < NN; c++) if (core[c]) { const i = c % NX, j = (c / NX) | 0; for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) keep[(j + dj) * NX + i + di] = 1 }
    for (let c = 0; c < NN; c++) if (own[c] === f.k && !keep[c] && !trunk[l][c]) own[c] = 0 }
  // islands: every piece of copper must hold a via of its net
  const lab = new Int32Array(NN); let nl = 0; const hasVia: boolean[] = [false]
  for (let c0 = 0; c0 < NN; c0++) { if (!own[c0] || lab[c0]) continue; lab[c0] = ++nl; hasVia.push(false); const st = [c0]
    while (st.length) { const c = st.pop()!, i = c % NX, j = (c / NX) | 0; for (let d = 0; d < 8; d += 2) { const ii = i + D8[d], jj = j + D8[d + 1]; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY) continue; const c2 = jj * NX + ii; if (own[c2] === own[c0] && !lab[c2]) { lab[c2] = nl; st.push(c2) } } } }
  for (const v of vias) { const k = idx.get(v.net), c = cj(v.y) * NX + ci(v.x); if (k && own[c] === k) hasVia[lab[c]] = true }
  let dropped = 0; for (let c = 0; c < NN; c++) if (own[c] && !hasVia[lab[c]]) { own[c] = 0; dropped++ }
  report.push(`${LAYERS[l]}: copper ${(100 * own.reduce((s, v) => s + (v ? 1 : 0), 0) / NN).toFixed(0)}% of the board; ${(dropped * P * P).toFixed(1)} mm2 of unconnected fill removed`) }
// ---------- independent check of the result: connectivity through copper + vias, clearances ----------
{ const par = new Map<string, string>(), find = (a: string): string => { let r = a; while (par.get(r) !== r) r = par.get(r)!; par.set(a, r); return r }, uni = (a: string, b: string) => { for (const x of [a, b]) if (!par.has(x)) par.set(x, x); par.set(find(a), find(b)) }
  const labs = LAYERS.map((_, l) => { const lab = new Int32Array(NN); let nl = 0; for (let c0 = 0; c0 < NN; c0++) { if (!owner[l][c0] || lab[c0]) continue; lab[c0] = ++nl; const st = [c0]; while (st.length) { const c = st.pop()!, i = c % NX, j = (c / NX) | 0; for (let d = 0; d < 8; d += 2) { const ii = i + D8[d], jj = j + D8[d + 1]; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY) continue; const c2 = jj * NX + ii; if (owner[l][c2] === owner[l][c0] && !lab[c2]) { lab[c2] = nl; st.push(c2) } } } } return lab })
  let clearBad = 0, minClear = 9
  vias.forEach((v, m) => { const k = idx.get(v.net) ?? 0, c = cj(v.y) * NX + ci(v.x); par.set("v" + m, "v" + m)
    LAYERS.forEach((_, l) => { if (k && owner[l][c] === k) uni("v" + m, `L${l}:${labs[l][c]}`)
      // copper of other nets near this via
      const R = v.d / 2 + 0.3; for (let j = Math.max(0, cj(v.y - R)); j <= Math.min(NY - 1, cj(v.y + R)); j++) for (let i = Math.max(0, ci(v.x - R)); i <= Math.min(NX - 1, ci(v.x + R)); i++) { const o = owner[l][j * NX + i]; if (!o || o === k) continue
        const g = Math.hypot(Math.max(Math.abs(cx(i) - v.x) - P / 2, 0), Math.max(Math.abs(cy(j) - v.y) - P / 2, 0)) - v.d / 2; if (g < minClear) minClear = g; if (g < 0.1) clearBad++ } }) })
  for (const net of NETS) { const ms = vias.map((v, m) => [v, m] as const).filter(([v]) => v.net === net.name); if (!ms.length) continue; const roots = new Set(ms.map(([, m]) => find("v" + m)))
    report.push(`check ${net.name}: ${ms.length} vias in ${roots.size} connected group${roots.size === 1 ? "" : "s !!"}`) }
  // different nets on one layer
  let minNet = 9; for (const [l] of LAYERS.entries()) for (let c = 0; c < NN; c++) { const o = owner[l][c]; if (!o) continue; const i = c % NX, j = (c / NX) | 0; for (let dj = 0; dj <= 4; dj++) for (let di = -4; di <= 4; di++) { const ii = i + di, jj = j + dj; if (ii < 0 || ii >= NX || jj >= NY) continue; const o2 = owner[l][jj * NX + ii]; if (o2 && o2 !== o) minNet = Math.min(minNet, Math.hypot(Math.max(Math.abs(di) - 1, 0), Math.max(dj - 1, 0)) * P) } }
  report.push(`check clearances: copper to foreign via pad min ${minClear.toFixed(3)} mm (${clearBad} cells below 0.10); copper of different nets on a layer min ${minNet > 8 ? ">0.2" : minNet.toFixed(3)} mm`) }
{ // feed width: vias of a supply reached from its connector pins through copper at least 0.2 mm wide (4 cells), on any layer
  for (const [ni, net] of NETS.entries()) { const k = ni + 1; if (!["VDD_3V3", "VDD_1V8", "VDD_CORE", "VDD_MPU", "VDDS_DDR"].includes(net.name)) continue
    const mine = vias.filter((v) => v.net === net.name), wide = LAYERS.map((_, l) => { const core = new Uint8Array(NN), w = new Uint8Array(NN) // opening with a 4x4 square
      for (let j = 0; j < NY - 3; j++) for (let i = 0; i < NX - 3; i++) { let ok = true; for (let dj = 0; dj < 4 && ok; dj++) for (let di = 0; di < 4; di++) if (owner[l][(j + dj) * NX + i + di] !== k) { ok = false; break } if (ok) core[j * NX + i] = 1 }
      for (let c = 0; c < NN; c++) if (core[c]) { const i = c % NX, j = (c / NX) | 0; for (let dj = 0; dj < 4; dj++) for (let di = 0; di < 4; di++) w[(j + dj) * NX + i + di] = 1 }
      return w })
    const seen = LAYERS.map(() => new Uint8Array(NN)), st: number[] = [], hit = new Set<number>()
    const near = (l: number, v: V) => { const c0 = cj(v.y) * NX + ci(v.x); for (let dj = -3; dj <= 3; dj++) for (let di = -3; di <= 3; di++) { const c = c0 + dj * NX + di; if (c >= 0 && c < NN && wide[l][c]) return c } return -1 }
    const enter = (m: number) => { if (hit.has(m)) return; hit.add(m); LAYERS.forEach((_, l) => { const c = near(l, mine[m]); if (c >= 0 && !seen[l][c]) { seen[l][c] = 1; st.push(l * NN + c) } }) }
    mine.forEach((v, m) => { if (plan.vias.some((p: any) => /^V_J/.test(p.name) && p.x === v.x && p.y === v.y)) enter(m) })
    const at = new Map<number, number[]>(); mine.forEach((v, m) => LAYERS.forEach((_, l) => { const c = near(l, v); if (c >= 0) at.set(l * NN + c, [...(at.get(l * NN + c) ?? []), m]) }))
    while (st.length) { const u = st.pop()!, l = (u / NN) | 0, c = u % NN, i = c % NX, j = (c / NX) | 0; for (const m of at.get(u) ?? []) enter(m)
      for (let d = 0; d < 8; d += 2) { const ii = i + D8[d], jj = j + D8[d + 1]; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY) continue; const c2 = jj * NX + ii; if (wide[l][c2] && !seen[l][c2]) { seen[l][c2] = 1; st.push(l * NN + c2) } } }
    report.push(`feed width ${net.name}: ${hit.size}/${mine.length} vias reached from the connector pins through copper >= 0.2 mm wide`) } }
// ---------- polygons ----------
function outlines(own: Int8Array, k: number) { // directed boundary edges with the region on the left, linked into loops
  const VX = NX + 1, next = new Map<number, number[]>(), add = (a: number, b: number) => { const l = next.get(a); if (l) l.push(b); else next.set(a, [b]) }
  const inR = (i: number, j: number) => i >= 0 && j >= 0 && i < NX && j < NY && own[j * NX + i] === k
  for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) { if (own[j * NX + i] !== k) continue
    if (!inR(i, j - 1)) add(j * VX + i, j * VX + i + 1); if (!inR(i + 1, j)) add(j * VX + i + 1, (j + 1) * VX + i + 1); if (!inR(i, j + 1)) add((j + 1) * VX + i + 1, (j + 1) * VX + i); if (!inR(i - 1, j)) add((j + 1) * VX + i, j * VX + i) }
  const loops: Pt[][] = []
  for (const [s0] of next) { while (next.get(s0)?.length) { const loop: number[] = [s0]; let prev = -1, cur = s0
      for (;;) { const outs = next.get(cur)!; let pick = 0
        if (outs.length > 1 && prev >= 0) { const dx = (cur % VX) - (prev % VX), dy = ((cur / VX) | 0) - ((prev / VX) | 0); pick = outs.findIndex((o) => { const ex = (o % VX) - (cur % VX), ey = ((o / VX) | 0) - ((cur / VX) | 0); return dx * ey - dy * ex > 0 }); if (pick < 0) pick = 0 } // left turn keeps diagonal neighbours apart
        const nx = outs.splice(pick, 1)[0]; prev = cur; cur = nx; if (cur === s0) break; loop.push(cur) }
      const pts = loop.map((v) => ({ x: +(E.x0 + (v % VX) * P).toFixed(3), y: +(E.y0 + ((v / VX) | 0) * P).toFixed(3) }))
      loops.push(pts.filter((p, i) => { const a = pts[(i + pts.length - 1) % pts.length], b = pts[(i + 1) % pts.length]; return Math.abs((p.x - a.x) * (b.y - p.y) - (p.y - a.y) * (b.x - p.x)) > 1e-9 })) } }
  const area = (p: Pt[]) => p.reduce((s, q, i) => s + q.x * p[(i + 1) % p.length].y - p[(i + 1) % p.length].x * q.y, 0) / 2
  const inside = (q: Pt, poly: Pt[]) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) if ((poly[i].y > q.y) !== (poly[j].y > q.y) && q.x < ((poly[j].x - poly[i].x) * (q.y - poly[i].y)) / (poly[j].y - poly[i].y) + poly[i].x) c = !c; return c }
  const outers = loops.filter((l) => area(l) > 0).map((l) => ({ outer: l, holes: [] as Pt[][], a: area(l) })).sort((a, b) => a.a - b.a)
  for (const h of loops.filter((l) => area(l) < 0)) { const q = { x: h[0].x + 1e-4, y: h[0].y + 1e-4 }, o = outers.find((o) => inside(q, o.outer) || inside({ x: h[0].x - 1e-4, y: h[0].y - 1e-4 }, o.outer)); if (o) o.holes.push(h) }
  return outers }
const pours: any[] = []
for (const [l, name] of LAYERS.entries()) for (const [ni, net] of NETS.entries()) for (const o of outlines(owner[l], ni + 1)) pours.push({ layer: name, net: net.name, outer: o.outer, holes: o.holes, area: +o.a.toFixed(2) })
await Bun.write(dir + "/pours.json", JSON.stringify(pours))
report.push(`${pours.length} copper shapes, ${pours.reduce((s, p) => s + p.outer.length + p.holes.reduce((t: number, h: Pt[]) => t + h.length, 0), 0)} vertices`)
for (const [l, name] of LAYERS.entries()) report.push(`${name}: ` + NETS.map((n, ni) => { const a = owner[l].reduce((s, v) => s + (v === ni + 1 ? 1 : 0), 0) * P * P; return a > 0.05 ? `${n.name} ${a.toFixed(0)} mm2` : "" }).filter(Boolean).join(", "))
console.log(report.join("\n"))
if (process.env.DUMP) await Bun.write(dir + "/planes-raster.json", JSON.stringify({ NX, NY, P, x0: E.x0, y0: E.y0, layers: owner.map((o) => Buffer.from(o.buffer).toString("base64")), nets: NETS.map((n) => n.name) }))
