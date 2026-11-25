// Routes the CM4 module's signal nets (plan.json `nets`: processor balls, part pads, CM4 connector pins) around the
// fixed DDR block, the placed parts and the plane vias. Negotiated congestion on a 0.1 mm grid (as module 0.4.4's
// route-signals.ts): every net is ripped up and re-routed with rising penalties for shared space until no two nets
// conflict. A net with several terminals is routed as a tree (each terminal joins the copper already laid).
// MODE=inner: nets that start at a ball the DDR copper boxes in (via-in-pad, then layer 4 / bottom / top).
// MODE=outer: everything else on the two outer layers. Output: cm4-module/routes.json.
import { gap, disc, type Item, type Pt } from "./geom"
const dir = import.meta.dir
const plan = await Bun.file(dir + "/plan.json").json(), { items, bodies }: { items: Item[]; bodies: any[] } = await Bun.file(dir + "/plan-items.json").json()
const E = plan.edge, P = 0.1, X0 = E.x0, Y0 = E.y0, NX = Math.round((E.x1 - X0) / P) + 1, NY = Math.round((E.y1 - Y0) / P) + 1, NN = NX * NY
const W = 0.1, CLR = 0.1, CLR_DDR = +(process.env.CLR_DDR ?? 0.31), VIA_D = 0.3
const gx = (x: number) => Math.round((x - X0) / P), gy = (y: number) => Math.round((y - Y0) / P), wx = (i: number) => X0 + i * P, wy = (j: number) => Y0 + j * P
const MODE = process.env.MODE ?? "outer"
const LAYERS = MODE === "inner" ? ["top", "inner3", "bottom"] : ["top", "bottom"], NL = LAYERS.length
// inside the processor's ball field a via sits exactly on a ball centre (via-in-pad) or >= 0.45 mm from every ball centre
const offBallAt = (x: number, y: number) => { if (x < -51.6 - 0.45 || x > -38.0 + 0.45 || y < 8.35 - 0.45 || y > 21.95 + 0.45) return false
  const kx = Math.min(17, Math.max(0, Math.round((x + 51.6) / 0.8))), ky = Math.min(17, Math.max(0, Math.round((21.95 - y) / 0.8))), d = Math.hypot(x - (-51.6 + 0.8 * kx), y - (21.95 - 0.8 * ky)); return d > 0.02 && d < 0.45 }
const inCpu = (x: number, y: number) => x > -52.4 && x < -37.2 && y > 7.55 && y < 22.75
// ---------- previous pass (inner nets) as fixed copper ----------
const prev = MODE === "outer" && (await Bun.file(dir + "/routes.json").exists()) ? await Bun.file(dir + "/routes.json").json() : { nets: {} }
for (const [name, r] of Object.entries(prev.nets) as any) { if (!plan.nets.find((n: any) => n.name === name)?.inner) { delete prev.nets[name]; continue }
  for (const g of r.segs) for (let i = 0; i + 1 < g.pts.length; i++) items.push({ pts: [g.pts[i], g.pts[i + 1]], r: W / 2, layers: [g.layer], net: name, kind: "trace" } as any)
  for (const v of r.vias) items.push({ pts: [{ x: v.x, y: v.y }], r: v.d / 2, layers: ["top", "bottom"], net: name, kind: "via" } as any) }
// ---------- nets ----------
type Term = { ref: string; x: number; y: number; layer: string; shape: { pts: Pt[]; r: number }; kind: string }
type Net = { name: string; terms: Term[]; inner: boolean; path?: number[]; id: number }
const nets: Net[] = (plan.nets as any[]).filter((n) => n.inner === (MODE === "inner")).map((n, i) => ({ ...n, id: 0 }))
const netId = new Map<string, number>(); const idOf = (n: string) => { let i = netId.get(n); if (!i) netId.set(n, (i = netId.size + 1)); return i }
nets.forEach((n) => (n.id = idOf(n.name)))
// ---------- static masks: 0 free, id = only that net, -1 nobody ----------
const statT = LAYERS.map(() => new Int32Array(NN)), statV = new Int32Array(NN)
const mark = (a: Int32Array, c: number, id: number) => { a[c] = a[c] === 0 || a[c] === id ? id : -1 }
function stamp(it: { pts: Pt[]; r: number }, a: Int32Array, id: number, reach: number, only?: (x: number, y: number) => boolean) { const xs = it.pts.map((p) => p.x), ys = it.pts.map((p) => p.y), R = it.r + reach
  for (let j = Math.max(0, gy(Math.min(...ys) - R)); j <= Math.min(NY - 1, gy(Math.max(...ys) + R)); j++) for (let i = Math.max(0, gx(Math.min(...xs) - R)); i <= Math.min(NX - 1, gx(Math.max(...xs) + R)); i++) if ((!only || only(wx(i), wy(j))) && gap(disc(wx(i), wy(j), 0), it as any) < reach - 1e-6) mark(a, j * NX + i, id) }
const L = (name: string) => LAYERS.indexOf(name)
for (const it of items) { if (!it.layers.length) continue
  const ddr = it.kind === "ddr" || it.kind === "ddrvia", id = it.net.startsWith("NC:") || it.net === "HOLE" ? -1 : idOf(it.net), out = (x: number, y: number) => !inCpu(x, y)
  for (const ln of it.layers) { const l = L(ln); if (l < 0) continue; stamp(it, statT[l], id, CLR + W / 2 + 0.005); if (ddr) stamp(it, statT[l], id, CLR_DDR + W / 2 + 0.005, out) }
  // through vias have a pad on layer 4 too: 0.1 mm to it keeps 0.2 mm to the 0.1 mm hole
  if (MODE === "inner" && it.layers.length === 2) stamp(it, statT[L("inner3")], id, CLR + W / 2 + 0.005)
  stamp(it, statV, id, CLR + VIA_D / 2 + 0.005); if (ddr) stamp(it, statV, id, CLR_DDR + VIA_D / 2 + 0.005, out) }
// vias with a pad smaller than 0.3 mm (layer-4 dips of the DDR block): keep the same distance to the hole as for a 0.3 mm pad
for (const it of items) if (it.layers.length === 2 && it.pts.length === 1 && it.r < 0.149) { const big = { pts: it.pts, r: 0.15 }, id = idOf(it.net); for (let l = 0; l < NL; l++) stamp(big, statT[l], id, CLR + W / 2 + 0.005) }
// layer-4 copper: the DDR sections there, the inner pass's traces: closed to vias; in the inner pass also to its traces
for (const g of plan.ddrInner ?? []) { const it = { pts: [g.a, g.b], r: 0.051 }; stamp(it, statV, idOf(g.net), 0.13 + VIA_D / 2 + 0.005); if (MODE === "inner") stamp(it, statT[L("inner3")], idOf(g.net), (g.a.x > -56 ? 0.13 : CLR_DDR) + W / 2 + 0.005) }
for (const [name, n] of Object.entries(prev.nets) as any) for (const g of n.segs) if (g.layer === "inner3") for (let i = 0; i + 1 < g.pts.length; i++) stamp({ pts: [g.pts[i], g.pts[i + 1]], r: 0.05 }, statV, idOf(name), 0.13 + VIA_D / 2 + 0.005)
// no tracks between the pads of a part or under its body, no vias under a part (the BGAs and the connectors excepted: their pads are the obstacle)
const padsOfRef = new Map<string, Item[]>(); for (const it of items) if (it.kind === "pad" && it.ref) { const r = it.ref.split(".")[0]; if (!padsOfRef.has(r)) padsOfRef.set(r, []); padsOfRef.get(r)!.push(it) }
for (const b of bodies) { if (b.ref === "U1" || b.ref === "U_DDR" || b.ref === "HOLE" || /^J\d/.test(b.ref)) continue; const l = L(b.layer), ps = padsOfRef.get(b.ref) ?? []
  const xs = ps.flatMap((p) => p.pts.map((q) => q.x)), ys = ps.flatMap((p) => p.pts.map((q) => q.y)), core = { x0: Math.min(...xs), x1: Math.max(...xs), y0: Math.min(...ys), y1: Math.max(...ys) }
  const inCore = (x: number, y: number) => x > core.x0 && x < core.x1 && y > core.y0 && y < core.y1 && !ps.some((p) => gap(disc(x, y, 0), p as any) < W / 2 + 0.005)
  for (let j = Math.max(0, gy(core.y0) - 1); j <= Math.min(NY - 1, gy(core.y1) + 1); j++) for (let i = Math.max(0, gx(core.x0) - 1); i <= Math.min(NX - 1, gx(core.x1) + 1); i++) if (inCore(wx(i), wy(j))) { if (l >= 0) statT[l][j * NX + i] = -1 }
  stamp({ pts: b.s.pts, r: 0 }, statV, -1, VIA_D / 2 + 0.02, (x, y) => !ps.some((p) => gap(disc(x, y, 0), p as any) < -0.05)) }
// board edge, mounting holes
for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) if (wx(i) < E.x0 + 0.35 || wx(i) > E.x1 - 0.35 || wy(j) < E.y0 + 0.35 || wy(j) > E.y1 - 0.35) { for (let l = 0; l < NL; l++) statT[l][j * NX + i] = -1; statV[j * NX + i] = -1 }
// ---------- terminals: goal cells on a layer (a trace end fully on the pad), via cells (via-in-pad) ----------
type TermCells = { onLayer: Map<number, number[]>; via: number[] }
function cellsOf(t: Term, id: number): TermCells { const xs = t.shape.pts.map((p) => p.x), ys = t.shape.pts.map((p) => p.y), R = t.shape.r, l = L(t.layer), onLayer = new Map<number, number[]>(), via: number[] = []
  for (let j = gy(Math.min(...ys) - R) - 1; j <= gy(Math.max(...ys) + R) + 1; j++) for (let i = gx(Math.min(...xs) - R) - 1; i <= gx(Math.max(...xs) + R) + 1; i++) { if (i < 0 || j < 0 || i >= NX || j >= NY) continue
    const c = j * NX + i, g = gap(disc(wx(i), wy(j), 0), t.shape as any)
    if (l >= 0 && g <= -W / 2 + 1e-6 && (statT[l][c] === 0 || statT[l][c] === id)) { if (!onLayer.has(l)) onLayer.set(l, []); onLayer.get(l)!.push(c) }
    // via in the pad: centre on the pad, legal on every layer of this pass; a ball's via only at its centre
    if (process.env.DEBUGTERM === t.ref && g <= -0.05) console.log(`   cell (${wx(i).toFixed(2)}, ${wy(j).toFixed(2)}) g ${g.toFixed(3)} statV ${statV[c]} statT ${LAYERS.map((_, k) => statT[k][c]).join("/")} id ${id}`)
    if (g <= -0.05 && (statV[c] === 0 || statV[c] === id) && !offBallAt(wx(i), wy(j)) && (t.kind !== "ball" || Math.hypot(wx(i) - t.x, wy(j) - t.y) < 0.051) && LAYERS.every((_, k) => statT[k][c] === 0 || statT[k][c] === id)) via.push(c) }
  return { onLayer, via } }
const TC = new Map<Net, TermCells[]>()
for (const n of nets) { TC.set(n, n.terms.map((t) => cellsOf(t, n.id))); n.terms.forEach((t, k) => { const tc = TC.get(n)![k]; if (!tc.onLayer.size && !tc.via.length) console.log(`!! ${n.name}: terminal ${t.ref} has no reachable cell`) }) }
// in the inner pass a boxed-in ball starts as the via already in its pad (planner): the net starts on every layer there
const ballVia = (n: Net) => n.terms.findIndex((t) => t.kind === "ball")
// ---------- dynamic occupancy ----------
const offs = (r: number) => { const o: number[] = [], n = Math.ceil(r / P); for (let dj = -n; dj <= n; dj++) for (let di = -n; di <= n; di++) if (Math.hypot(di, dj) * P < r - 1e-6) o.push(di, dj); return o }
const O2 = offs(W + CLR), O3 = offs(VIA_D / 2 + CLR + W / 2), O4 = offs(VIA_D + CLR)
const tNear2 = LAYERS.map(() => new Int16Array(NN)), tNear3 = LAYERS.map(() => new Int16Array(NN)), vNear3 = new Int16Array(NN), vNear4 = new Int16Array(NN)
const hist = LAYERS.map(() => new Float32Array(NN)), histV = new Float32Array(NN)
const add = (a: Int16Array, c: number, o: number[], d: number) => { const i = c % NX, j = (c / NX) | 0; for (let k = 0; k < o.length; k += 2) { const ii = i + o[k], jj = j + o[k + 1]; if (ii >= 0 && jj >= 0 && ii < NX && jj < NY) a[jj * NX + ii] += d } }
// a path is a list of nodes n = layer * NN + cell; consecutive nodes on the same cell = a via; -1 separates the branches of a tree
function stampNet(n: Net, d: number) { const p = n.path; if (!p) return
  for (let k = 0; k < p.length; k++) { if (p[k] < 0) continue; const l = (p[k] / NN) | 0, c = p[k] % NN; add(tNear2[l], c, O2, d); add(tNear3[l], c, O3, d)
    if (k + 1 < p.length && p[k + 1] >= 0 && p[k + 1] % NN === c) { add(vNear3, c, O3, d); add(vNear4, c, O4, d) } } }
// ---------- search ----------
const VIA_COST = +(process.env.VIA_COST ?? 6)
let pres = 0.6
const gScore = new Float32Array(NL * NN), from = new Int32Array(NL * NN), seen = new Int32Array(NL * NN), goal = new Int32Array(NL * NN); let stampId = 0, goalId = 0
const heap: number[] = [], hkey: number[] = []
const hpush = (k: number, n: number) => { let i = heap.length; heap.push(n); hkey.push(k); while (i > 0) { const p = (i - 1) >> 1; if (hkey[p] <= hkey[i]) break; [heap[p], heap[i]] = [heap[i], heap[p]]; [hkey[p], hkey[i]] = [hkey[i], hkey[p]]; i = p } }
const hpop = () => { const top = heap[0], n = heap.pop()!, k = hkey.pop()!; if (heap.length) { heap[0] = n; hkey[0] = k; let i = 0; for (;;) { const a = 2 * i + 1, b = a + 1; let m = i; if (a < heap.length && hkey[a] < hkey[m]) m = a; if (b < heap.length && hkey[b] < hkey[m]) m = b; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; [hkey[m], hkey[i]] = [hkey[i], hkey[m]]; i = m } } return top }
const D8 = [1, 0, -1, 0, 0, 1, 0, -1, 1, 1, 1, -1, -1, 1, -1, -1]
/** one tree: terminal 0 first, then each remaining terminal joins the tree by the cheapest path. Returns false if one cannot. */
function route(n: Net): boolean { const id = n.id, tcs = TC.get(n)!, okT = (l: number, c: number) => { const s = statT[l][c]; return s === 0 || s === id }
  const order = [...tcs.keys()]; const bi = MODE === "inner" ? ballVia(n) : -1; if (bi > 0) { order.splice(order.indexOf(bi), 1); order.unshift(bi) }
  const tree: number[] = [], path: number[] = []
  const seed = (k: number) => { const tc = tcs[k]; for (const [l, cs] of tc.onLayer) for (const c of cs) tree.push(l * NN + c)
    if (bi === k) { const c = gy(n.terms[k].y) * NX + gx(n.terms[k].x); for (let l = 0; l < NL; l++) tree.push(l * NN + c) } }
  seed(order[0])
  for (const k of order.slice(1)) { const tc = tcs[k]; stampId++; goalId++; heap.length = 0; hkey.length = 0
    for (const [l, cs] of tc.onLayer) for (const c of cs) goal[l * NN + c] = goalId
    const viaGoal = new Set(tc.via); const tx = n.terms[k].x, ty = n.terms[k].y, h = (c: number) => Math.hypot(wx(c % NX) - tx, wy((c / NX) | 0) - ty) / P
    for (const u of tree) { seen[u] = stampId; gScore[u] = 0; from[u] = -1; hpush(h(u % NN), u) }
    let end = -1
    while (heap.length) { const u = hpop(), l = (u / NN) | 0, c = u % NN, i = c % NX, j = (c / NX) | 0, g = gScore[u]
      if (goal[u] === goalId) { end = u; break }
      const relax = (v: number, cost: number) => { const ng = g + cost; if (seen[v] !== stampId || ng < gScore[v]) { seen[v] = stampId; gScore[v] = ng; from[v] = u; hpush(ng + h(v % NN), v) } }
      for (let q = 0; q < 16; q += 2) { const ii = i + D8[q], jj = j + D8[q + 1]; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY) continue; const c2 = jj * NX + ii
        if (!okT(l, c2)) continue
        if (D8[q] !== 0 && D8[q + 1] !== 0 && (!okT(l, j * NX + ii) || !okT(l, jj * NX + i))) continue
        const occ = tNear2[l][c2] + vNear3[c2] > 0 ? 1 : 0
        relax(l * NN + c2, (D8[q] !== 0 && D8[q + 1] !== 0 ? 1.4142 : 1) * (1 + hist[l][c2]) * (1 + pres * occ) + pres * 4 * occ) }
      // via to every other layer here: anywhere legal, or into the target pad (via-in-pad); not beside the inner pass's ball via
      const legal = viaGoal.has(c) || ((statV[c] === 0 || statV[c] === id) && !offBall[c] && LAYERS.every((_, k2) => okT(k2, c)))
      if (legal) { const occ = vNear4[c] + LAYERS.reduce((s, _, k2) => s + tNear3[k2][c], 0) > 0 ? 1 : 0
        for (let l2 = 0; l2 < NL; l2++) if (l2 !== l) { const v = l2 * NN + c; relax(v, VIA_COST * (1 + histV[c]) * (1 + pres * occ) + pres * 8 * occ); if (viaGoal.has(c)) goal[v] = goalId } } }
    if (end < 0) { failTerm = `${n.terms[k].ref}: ${[...tc.onLayer].map(([l, cs]) => LAYERS[l] + " " + cs.length).join(", ")} cells, ${tc.via.length} via cells`; return false }
    const seg: number[] = []; for (let u = end; u !== -1; u = from[u]) seg.unshift(u)
    if (path.length) path.push(-1); path.push(...seg); tree.push(...seg); seed(k) }
  n.path = path; return true }
let failTerm = ""
const offBall = new Uint8Array(NN); for (let c = 0; c < NN; c++) offBall[c] = offBallAt(wx(c % NX), wy((c / NX) | 0)) ? 1 : 0
// ---------- negotiation ----------
function conflicts(n: Net) { stampNet(n, -1); const bad: number[] = [], p = n.path!
  for (let k = 0; k < p.length; k++) { if (p[k] < 0) continue; const l = (p[k] / NN) | 0, c = p[k] % NN, via = k + 1 < p.length && p[k + 1] >= 0 && p[k + 1] % NN === c
    if (tNear2[l][c] + vNear3[c] > 0 || (via && vNear4[c] + LAYERS.reduce((s, _, k2) => s + tNear3[k2][c], 0) > 0)) bad.push(p[k]) }
  stampNet(n, 1); return bad }
let rs = +(process.env.SEED ?? 1) >>> 0; const rnd = () => { rs = (rs + 0x6d2b79f5) >>> 0; let t = Math.imul(rs ^ (rs >>> 15), 1 | rs); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296 }
const t0 = performance.now(); let order = nets.map((_, i) => i)
const MAXIT = +(process.env.MAXIT ?? 80); let solved = false
for (let it = 1; it <= MAXIT; it++) { let failed = 0
  for (const k of order) { const n = nets[k], t1 = performance.now(); stampNet(n, -1); n.path = undefined; if (!route(n)) { failed++; if (it === 1) console.log(`  ${n.name}: no path (${failTerm})`) } stampNet(n, 1); if (it === 1 && process.env.VERBOSE) console.log(`  ${n.name} ${((performance.now() - t1) / 1e3).toFixed(2)}s`) }
  let nbad = 0; const badNets: string[] = []
  for (const n of nets) { if (!n.path) { nbad++; badNets.push(n.name + "(unrouted)"); continue } const bad = conflicts(n)
    for (const u of bad) { const l = (u / NN) | 0, c = u % NN; hist[l][c] = Math.min(hist[l][c] + 0.4, 6); histV[c] = Math.min(histV[c] + 0.2, 3) }
    if (bad.length) { nbad++; badNets.push(n.name) } }
  if (it % 5 === 0 || nbad === 0 || it === 1) console.log(`iter ${it}: ${nbad} nets in conflict, ${failed} unrouted, pres ${pres.toFixed(2)}, ${((performance.now() - t0) / 1e3).toFixed(0)}s ${nbad && nbad < 10 ? badNets.join(" ") : ""}`)
  if (nbad === 0) { solved = true; break }
  pres = Math.min(pres * 1.25, 25); for (let i = order.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [order[i], order[j]] = [order[j], order[i]] } }
// ---------- output ----------
const out: any = { solved, nets: { ...prev.nets } as Record<string, any> }
const known = new Set<string>(); for (const v of plan.vias) known.add(`${(+v.x).toFixed(3)},${(+v.y).toFixed(3)}`)
for (const n of nets) { if (!n.path) continue; const segs: { layer: string; pts: Pt[] }[] = [], vias: any[] = [], seenV = new Set<string>()
  let cur: Pt[] = [], curL = -1
  const flush = () => { if (cur.length > 1) { const pts = cur.filter((p, i) => i === 0 || i === cur.length - 1 || Math.abs((p.x - cur[i - 1].x) * (cur[i + 1].y - p.y) - (p.y - cur[i - 1].y) * (cur[i + 1].x - p.x)) > 1e-9); segs.push({ layer: LAYERS[curL], pts }) } cur = [] }
  for (let k = 0; k < n.path.length; k++) { const u = n.path[k]; if (u < 0) { flush(); curL = -1; continue }
    const l = (u / NN) | 0, c = u % NN, p = { x: +wx(c % NX).toFixed(4), y: +wy((c / NX) | 0).toFixed(4) }
    if (curL >= 0 && l !== curL) { flush(); const key = `${p.x.toFixed(3)},${p.y.toFixed(3)}`; if (!known.has(key) && !seenV.has(key)) { seenV.add(key); vias.push({ ...p, d: VIA_D, hole: 0.1 }) } }
    curL = l; cur.push(p) }
  flush()
  out.nets[n.name] = { terms: n.terms.map((t) => t.ref), segs, vias, length: +segs.reduce((s, g) => s + g.pts.slice(1).reduce((t, p, i) => t + Math.hypot(p.x - g.pts[i].x, p.y - g.pts[i].y), 0), 0).toFixed(2) } }
if (solved || process.env.KEEP) await Bun.write(dir + "/routes.json", JSON.stringify(out))
const R = nets.filter((n) => n.path).map((n) => out.nets[n.name]) as any[]
console.log(`${solved ? "SOLVED" : "NOT SOLVED"}: ${R.length}/${nets.length} nets, ${R.reduce((s, n) => s + n.vias.length, 0)} vias, total ${R.reduce((s, n) => s + n.length, 0).toFixed(0)} mm, longest ${Math.max(...R.map((n) => n.length))} mm`)
const un = nets.filter((n) => !n.path).map((n) => n.name); if (un.length) console.log("unrouted:", un.join(" "))
