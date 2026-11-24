// Routes the handheld signals (processor ball -> any free connector pin) on the two outer layers around the fixed
// DDR block and the placed parts. Negotiated congestion on a 0.1 mm grid: every net is ripped up and re-routed with
// rising penalties for shared space until no two nets conflict. Output: module/routes.json.
import { gap, disc, rect, type Item, type Pt } from "./geom"
const dir = import.meta.dir
const plan = await Bun.file(dir + "/plan.json").json(), { items, bodies }: { items: Item[]; bodies: any[] } = await Bun.file(dir + "/plan-items.json").json()
const P = 0.1, X0 = -56.6, Y0 = -1.75, NX = Math.round((-32.95 - X0) / P) + 1, NY = Math.round((33.75 - Y0) / P) + 1, NN = NX * NY
const W = 0.1, CLR = 0.1, CLR_DDR = +(process.env.CLR_DDR ?? 0.31), VIA_D = 0.3, PADVIA_D = 0.3
const gx = (x: number) => Math.round((x - X0) / P), gy = (y: number) => Math.round((y - Y0) / P), wx = (i: number) => X0 + i * P, wy = (j: number) => Y0 + j * P
const MODE = process.env.MODE ?? "outer" // "inner": the balls the DDR copper boxes in - via-in-pad, then layer 4 (inner3) and the bottom layer
const LAYERS = [MODE === "inner" ? "inner3" : "top", "bottom"] as const
const isInner = (ball: string) => /^[RTUV][1-6]$/.test(ball) || ["B5", "C5", "C6"].includes(ball)
const prev = MODE === "outer" && (await Bun.file(dir + "/routes.json").exists()) ? await Bun.file(dir + "/routes.json").json() : { nets: {} }
for (const [name, r] of Object.entries(prev.nets) as any) { if (!isInner(r.ball)) { delete prev.nets[name]; continue }
  plan.pins.find((p: any) => p.conn === r.conn && p.pin === r.pin).role = "USED"
  for (const g of r.segs) if (g.layer !== "inner3") for (let i = 0; i + 1 < g.pts.length; i++) items.push({ pts: [g.pts[i], g.pts[i + 1]], r: 0.05, layers: [g.layer], net: name, kind: "trace" } as any)
  for (const v of r.vias) items.push({ pts: [{ x: v.x, y: v.y }], r: v.d / 2, layers: ["top", "bottom"], net: name, kind: "via" } as any) }
// ---------- nets ----------
type Net = { name: string; src: number; fixedPad?: number; path?: number[]; pad?: number }
const sigPads = (plan.pins as any[]).filter((p) => p.role === "SIG" || p.role === "USB0_DP" || p.role === "USB0_DM")
const nets: Net[] = (plan.signals as any[]).filter((s) => isInner(s.ball) === (MODE === "inner")).map((s) => { const b = plan.ball["U1." + s.ball]; return { name: s.name, src: gy(b.y) * NX + gx(b.x), fixedPad: sigPads.findIndex((p) => p.role === s.name) } })
for (const n of nets) if (n.fixedPad! < 0) delete n.fixedPad
const netId = new Map<string, number>(); const idOf = (n: string) => { let i = netId.get(n); if (!i) netId.set(n, (i = netId.size + 1)); return i }
nets.forEach((n) => idOf(n.name))
// ---------- static masks: 0 free, id = only that net, -1 nobody ----------
const statT = [new Int32Array(NN), new Int32Array(NN)], statV = new Int32Array(NN)
const mark = (a: Int32Array, c: number, id: number) => { a[c] = a[c] === 0 || a[c] === id ? id : -1 }
const inCpu = (x: number, y: number) => x > -52.4 && x < -37.2 && y > 7.55 && y < 22.75
function stamp(it: Pick<Item, "pts" | "r">, a: Int32Array, id: number, reach: number, only?: (x: number, y: number) => boolean) { const xs = it.pts.map((p) => p.x), ys = it.pts.map((p) => p.y), R = it.r + reach
  for (let j = Math.max(0, gy(Math.min(...ys) - R)); j <= Math.min(NY - 1, gy(Math.max(...ys) + R)); j++) for (let i = Math.max(0, gx(Math.min(...xs) - R)); i <= Math.min(NX - 1, gx(Math.max(...xs) + R)); i++) if ((!only || only(wx(i), wy(j))) && gap(disc(wx(i), wy(j), 0), it) < reach - 1e-6) mark(a, j * NX + i, id) }
for (const it of items) { if (!it.layers.length) continue
  const ddr = it.kind === "ddr" || it.kind === "ddrvia", id = it.net.startsWith("NC:") ? -1 : idOf(it.net)
  // DDR nets keep four trace widths to other signals outside the processor breakout (Table 7-68/7-69 spacing)
  // four trace widths to DDR copper everywhere outside the processor's ball field; inside it (breakout) the normal clearance
  const out = (x: number, y: number) => !inCpu(x, y)
  for (const l of it.layers) { if (l === "top" && MODE === "inner") continue; stamp(it, statT[l === "top" ? 0 : 1], id, CLR + W / 2 + 0.005); if (ddr) stamp(it, statT[l === "top" ? 0 : 1], id, CLR_DDR + W / 2 + 0.005, MODE === "inner" ? undefined : out) }
  if (MODE === "inner" && it.layers.length === 2) stamp(it, statT[0], id, 0.1 + W / 2 + 0.005) // layer 4 sees only the via pads: 0.1 mm to the pad keeps 0.2 mm to the 0.1 mm hole
  stamp(it, statV, id, CLR + VIA_D / 2 + 0.005); if (ddr) stamp(it, statV, id, CLR_DDR + VIA_D / 2 + 0.005, out) }
// vias with a pad smaller than 0.3 mm (layer-4 dips of the DDR block): keep the same distance to the hole as for a 0.3 mm pad
for (const it of items) if (it.layers.length === 2 && it.pts.length === 1 && it.r < 0.149) { const big = { pts: it.pts, r: 0.15 }, id = idOf(it.net); for (const l of [0, 1]) if (!(MODE === "inner" && l === 0)) stamp(big, statT[l], id, CLR + W / 2 + 0.005) }
// vias of this pass stay clear of the layer-4 traces of the first pass
for (const [name, n] of Object.entries(prev.nets) as any) for (const g of n.segs) if (g.layer === "inner3") for (let i = 0; i + 1 < g.pts.length; i++) stamp({ pts: [g.pts[i], g.pts[i + 1]], r: 0.05 }, statV, idOf(name), 0.13 + VIA_D / 2 + 0.005)
// DDR sections that run on layer 4: closed to vias, and to the layer-4 signals of the first pass
for (const g of plan.ddrInner ?? []) { const it = { pts: [g.a, g.b], r: 0.051 }; stamp(it, statV, idOf(g.net), 0.13 + VIA_D / 2 + 0.005); if (MODE === "inner") stamp(it, statT[0], idOf(g.net), (g.a.x > -56 ? 0.13 : CLR_DDR) + W / 2 + 0.005) }
// no tracks or vias under the small parts and the crystal (processor, memory and connector bodies excepted)
for (const b of bodies) { if (b.ref === "U1" || b.ref === "U_DDR" || b.ref.startsWith("J")) continue; const l = b.layer === "top" ? 0 : 1
  if (!(MODE === "inner" && l === 0)) stamp({ pts: b.s.pts, r: 0 }, statT[l], -1, W / 2 + 0.05); stamp({ pts: b.s.pts, r: 0 }, statV, -1, VIA_D / 2 + 0.05) }
// board edge
for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) if (wx(i) < plan.edge.x0 + 0.35 || wx(i) > plan.edge.x1 - 0.35 || wy(j) < plan.edge.y0 + 0.35 || wy(j) > plan.edge.y1 - 0.35) { statT[0][j * NX + i] = statT[1][j * NX + i] = statV[j * NX + i] = -1 }
// connector signal pads: closed to everybody except through their terminal nodes (pad centreline)
const term = new Int32Array(NN) // pad index + 1 on the bottom layer
const termVia = new Uint8Array(NN) // a pad via (0.25 mm) may sit here
const topItems = items.filter((i) => i.layers.includes("top"))
sigPads.forEach((p, k) => { const i = gx(p.x), jc = gy(p.y)
  for (let dj = -5; dj <= 5; dj++) { const c = (jc + dj) * NX + i; term[c] = k + 1
    if (Math.abs(dj) <= 2) { const s = disc(wx(i), wy(jc + dj), PADVIA_D / 2); if (!topItems.some((t) => gap(s, t) < CLR) && statV[c] !== -1 && !(Object.entries(prev.nets) as any).some(([, n]: any) => n.segs.some((g: any) => g.layer === "inner3" && g.pts.some((q: any, i: number) => i + 1 < g.pts.length && gap(s, { pts: [q, g.pts[i + 1]], r: 0.05 }) < 0.13)))) termVia[c] = 1 } } })
// ---------- dynamic occupancy ----------
const offs = (r: number) => { const o: number[] = [], n = Math.ceil(r / P); for (let dj = -n; dj <= n; dj++) for (let di = -n; di <= n; di++) if (Math.hypot(di, dj) * P < r - 1e-6) o.push(di, dj); return o }
const O2 = offs(W + CLR), O3 = offs(VIA_D / 2 + CLR + W / 2), O4 = offs(VIA_D + CLR)
const tNear2 = [new Int16Array(NN), new Int16Array(NN)], tNear3 = [new Int16Array(NN), new Int16Array(NN)], vNear3 = new Int16Array(NN), vNear4 = new Int16Array(NN)
const padUse = new Int16Array(sigPads.length), hist = [new Float32Array(NN), new Float32Array(NN)], histV = new Float32Array(NN), histPad = new Float32Array(sigPads.length)
const add = (a: Int16Array, c: number, o: number[], d: number) => { const i = c % NX, j = (c / NX) | 0; for (let k = 0; k < o.length; k += 2) { const ii = i + o[k], jj = j + o[k + 1]; if (ii >= 0 && jj >= 0 && ii < NX && jj < NY) a[jj * NX + ii] += d } }
// a path is a list of nodes n = layer * NN + cell; a layer change between consecutive nodes with the same cell is a via
function stampNet(n: Net, d: number) { if (!n.path) return; const p = n.path
  for (let k = 0; k < p.length; k++) { const l = p[k] >= NN ? 1 : 0, c = p[k] % NN; add(tNear2[l], c, O2, d); add(tNear3[l], c, O3, d)
    if (k + 1 < p.length && p[k + 1] % NN === c) { add(vNear3, c, O3, d); add(vNear4, c, O4, d) } }
  if (n.pad !== undefined) padUse[n.pad] += d }
// ---------- search ----------
const J1Y = [-1.15, 2.05], J2Y = [29.95, 33.15]
const hOf = (i: number, j: number, fixed?: any) => { const x = wx(i), y = wy(j); if (fixed) return Math.hypot(x - fixed.x, y - fixed.y) / P
  const dx = Math.max(-53.2 - x, 0, x - -35.2); return Math.min(Math.hypot(dx, Math.max(J1Y[0] - y, 0, y - J1Y[1])), Math.hypot(dx, Math.max(J2Y[0] - y, 0, y - J2Y[1]))) / P }
const VIA_COST = +(process.env.VIA_COST ?? 6)
let pres = 0.6
const gScore = new Float32Array(2 * NN), from = new Int32Array(2 * NN), seen = new Int32Array(2 * NN); let stampId = 0
const heap: number[] = [], hkey: number[] = []
const hpush = (k: number, n: number) => { let i = heap.length; heap.push(n); hkey.push(k); while (i > 0) { const p = (i - 1) >> 1; if (hkey[p] <= hkey[i]) break; [heap[p], heap[i]] = [heap[i], heap[p]]; [hkey[p], hkey[i]] = [hkey[i], hkey[p]]; i = p } }
const hpop = () => { const top = heap[0], n = heap.pop()!, k = hkey.pop()!; if (heap.length) { heap[0] = n; hkey[0] = k; let i = 0; for (;;) { const a = 2 * i + 1, b = a + 1; let m = i; if (a < heap.length && hkey[a] < hkey[m]) m = a; if (b < heap.length && hkey[b] < hkey[m]) m = b; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; [hkey[m], hkey[i]] = [hkey[i], hkey[m]]; i = m } } return top }
const D8 = [1, 0, -1, 0, 0, 1, 0, -1, 1, 1, 1, -1, -1, 1, -1, -1]
function route(n: Net): boolean { const id = idOf(n.name), fixed = n.fixedPad !== undefined ? sigPads[n.fixedPad] : undefined
  stampId++; heap.length = 0; hkey.length = 0
  const okT = (l: number, c: number) => { const s = statT[l][c]; return s === 0 || s === id }
  gScore[n.src] = 0; seen[n.src] = stampId; from[n.src] = -1; hpush(hOf(n.src % NX, (n.src / NX) | 0, fixed), n.src)
  if (MODE === "inner") { if (!(statV[n.src] === 0 || statV[n.src] === id)) return false; from[n.src] = NN + n.src; from[NN + n.src] = -1; seen[NN + n.src] = stampId; gScore[NN + n.src] = 0 } // starts as a via in the ball pad
  let end = -1, endPad = -1
  while (heap.length) { const u = hpop(), l = u >= NN ? 1 : 0, c = u % NN, i = c % NX, j = (c / NX) | 0, g = gScore[u]
    if (l === 1 && term[c] && (n.fixedPad === undefined ? sigPads[term[c] - 1].role === "SIG" : term[c] - 1 === n.fixedPad)) { end = u; endPad = term[c] - 1; break }
    const relax = (v: number, cost: number) => { const ng = g + cost; if (seen[v] !== stampId || ng < gScore[v]) { seen[v] = stampId; gScore[v] = ng; from[v] = u; const cv = v % NN; hpush(ng + hOf(cv % NX, (cv / NX) | 0, fixed), v) } }
    for (let k = 0; k < 16; k += 2) { const ii = i + D8[k], jj = j + D8[k + 1]; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY) continue; const c2 = jj * NX + ii
      if (l === 1 && term[c2]) { const pk = term[c2] - 1; if (n.fixedPad === undefined ? sigPads[pk].role !== "SIG" : pk !== n.fixedPad) continue
        if (D8[k] !== 0 && D8[k + 1] !== 0) continue // enter a pad square on
        relax(NN + c2, 1 + pres * 8 * padUse[pk] + histPad[pk]); continue }
      if (!okT(l, c2)) continue
      if (D8[k] !== 0 && D8[k + 1] !== 0 && (!okT(l, j * NX + ii) || !okT(l, jj * NX + i))) continue
      const occ = tNear2[l][c2] + vNear3[c2] > 0 ? 1 : 0
      relax(l * NN + c2, (D8[k] !== 0 && D8[k + 1] !== 0 ? 1.4142 : 1) * (1 + hist[l][c2]) * (1 + pres * occ) + pres * 4 * occ) }
    // via: anywhere legal, or a pad via on a connector terminal
    const o = (1 - l) * NN + c
    if (l === 0 && term[c]) { const pk = term[c] - 1; if (termVia[c] && (n.fixedPad === undefined ? sigPads[pk].role === "SIG" : pk === n.fixedPad)) { const occ = tNear3[0][c] + vNear4[c] > 0 ? 1 : 0; relax(o, VIA_COST * (1 + histV[c]) * (1 + pres * occ) + pres * 8 * (occ + padUse[pk]) + histPad[pk]) } }
    else if ((statV[c] === 0 || statV[c] === id) && okT(1 - l, c) && !term[c] && !(MODE === "inner" && c !== n.src && Math.hypot((c % NX) - (n.src % NX), ((c / NX) | 0) - ((n.src / NX) | 0)) < 4.5)) { const occ = tNear3[0][c] + tNear3[1][c] + vNear4[c] > 0 ? 1 : 0; relax(o, VIA_COST * (1 + histV[c]) * (1 + pres * occ) + pres * 8 * occ) } }
  if (end < 0) return false
  const path: number[] = []; for (let u = end; u !== -1; u = from[u]) path.unshift(u)
  n.path = path; n.pad = endPad; return true }
// ---------- negotiation ----------
function conflicts(n: Net) { stampNet(n, -1); const bad: number[] = []; const p = n.path!
  for (let k = 0; k < p.length; k++) { const l = p[k] >= NN ? 1 : 0, c = p[k] % NN, via = k + 1 < p.length && p[k + 1] % NN === c
    if (tNear2[l][c] + vNear3[c] > 0 || (via && tNear3[0][c] + tNear3[1][c] + vNear4[c] > 0)) bad.push(p[k]) }
  const padClash = padUse[n.pad!] > 0; stampNet(n, 1); return { bad, padClash } }
let rs = +(process.env.SEED ?? 1) >>> 0; const rnd = () => { rs = (rs + 0x6d2b79f5) >>> 0; let t = Math.imul(rs ^ (rs >>> 15), 1 | rs); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296 }
const t0 = performance.now(); let order = nets.map((_, i) => i)
// short, outer-row nets first
const MAXIT = +(process.env.MAXIT ?? 120); let solved = false
for (let it = 1; it <= MAXIT; it++) { let failed = 0
  for (const k of order) { const n = nets[k]; stampNet(n, -1); n.path = undefined; if (!route(n)) failed++; stampNet(n, 1) }
  let nbad = 0; const badNets: string[] = []
  for (const n of nets) { if (!n.path) { nbad++; badNets.push(n.name + "(unrouted)"); continue } const { bad, padClash } = conflicts(n)
    for (const u of bad) { const l = u >= NN ? 1 : 0, c = u % NN; hist[l][c] = Math.min(hist[l][c] + 0.4, 6); histV[c] = Math.min(histV[c] + 0.2, 3) } if (padClash) histPad[n.pad!] += 1.5
    if (bad.length || padClash) { nbad++; badNets.push(n.name) } }
  if (it % 5 === 0 || nbad === 0) console.log(`iter ${it}: ${nbad} nets in conflict, ${failed} unrouted, pres ${pres.toFixed(2)}, ${((performance.now() - t0) / 1e3).toFixed(0)}s ${nbad && nbad < 8 ? badNets.join(" ") : ""}`)
  if (nbad === 0) { solved = true; break }
  pres = Math.min(pres * 1.25, 25); for (let i = order.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [order[i], order[j]] = [order[j], order[i]] } }
// ---------- output ----------
const out: any = { solved, nets: { ...prev.nets } as Record<string, any> }
for (const n of nets) { if (!n.path) continue; const pad = sigPads[n.pad!], segs: { layer: string; pts: Pt[] }[] = [], vias: any[] = []
  let cur: Pt[] = [], curL = n.path[0] >= NN ? 1 : 0
  const flush = () => { if (cur.length > 1) { const pts = cur.filter((p, i) => i === 0 || i === cur.length - 1 || Math.abs((p.x - cur[i - 1].x) * (cur[i + 1].y - p.y) - (p.y - cur[i - 1].y) * (cur[i + 1].x - p.x)) > 1e-9); segs.push({ layer: LAYERS[curL], pts }) } cur = [] }
  for (let k = 0; k < n.path.length; k++) { const l = n.path[k] >= NN ? 1 : 0, c = n.path[k] % NN, p = { x: +wx(c % NX).toFixed(4), y: +wy((c / NX) | 0).toFixed(4) }
    if (l !== curL) { flush(); if (!plan.vias.some((v: any) => Math.abs(v.x - p.x) < 1e-3 && Math.abs(v.y - p.y) < 1e-3)) vias.push({ ...p, d: term[c] ? PADVIA_D : VIA_D, hole: 0.1 }); curL = l }
    cur.push(p) }
  // run on to the pad centre along the pad's centreline
  const last = cur.at(-1)!; if (Math.abs(last.y - pad.y) > 1e-6 && !vias.some((v) => Math.abs(v.x - last.x) < 1e-6 && Math.abs(v.y - last.y) < 1e-6 && cur.length === 1)) cur.push({ x: pad.x, y: pad.y })
  flush()
  // the ball's via may sit slightly off the pad centre (planner): the layer-4 / bottom copper starts at that via, and no second via is drilled
  { const ballName = plan.signals.find((s: any) => s.name === n.name).ball, b0 = plan.ball["U1." + ballName], pv = (plan.vias as any[]).find((v) => v.ball === "U1." + ballName)
    if (MODE === "inner" && pv && Math.hypot(pv.x - b0.x, pv.y - b0.y) > 1e-3) { for (let k = vias.length - 1; k >= 0; k--) if (Math.hypot(vias[k].x - b0.x, vias[k].y - b0.y) < 0.02) vias.splice(k, 1)
      for (const g of segs) for (const q of g.pts) if (Math.hypot(q.x - b0.x, q.y - b0.y) < 0.02) { q.x = pv.x; q.y = pv.y } } }
  out.nets[n.name] = { ball: plan.signals.find((s: any) => s.name === n.name).ball, conn: pad.conn, pin: pad.pin, segs, vias, length: +segs.reduce((s, g) => s + g.pts.slice(1).reduce((t, p, i) => t + Math.hypot(p.x - g.pts[i].x, p.y - g.pts[i].y), 0), 0).toFixed(2) } }
if (solved || process.env.KEEP) await Bun.write(dir + "/routes.json", JSON.stringify(out))
const L = nets.filter((n) => n.path).map((n) => out.nets[n.name]) as any[]
console.log(`${solved ? "SOLVED" : "NOT SOLVED"}: ${L.length}/${nets.length} nets, ${L.reduce((s, n) => s + n.vias.length, 0)} vias, total ${L.reduce((s, n) => s + n.length, 0).toFixed(0)} mm, longest ${Math.max(...L.map((n) => n.length))} mm; J1 ${L.filter((n) => n.conn === "J1").length}, J2 ${L.filter((n) => n.conn === "J2").length}`)
console.log("unrouted:", nets.filter((n) => !n.path).map((n) => `${n.name}(${plan.signals.find((s: any) => s.name === n.name).ball})`).join(" "))
if (process.env.PROBE) { const n = nets.find((n) => n.name === process.env.PROBE)!, id = idOf(n.name), i0 = n.src % NX, j0 = (n.src / NX) | 0
  for (const l of [0, 1]) { console.log(LAYERS[l]); for (let dj = 8; dj >= -8; dj--) { let s = ""; for (let di = -8; di <= 8; di++) { const c = (j0 + dj) * NX + i0 + di, v = statT[l][c]; s += v === 0 ? "." : v === id ? "o" : v === -1 ? "#" : "x" } console.log(s + "   " + Array.from({ length: 17 }, (_, k) => { const v = statV[(j0 + dj) * NX + i0 + k - 8]; return v === 0 ? "." : v === id ? "o" : "x" }).join("")) } } }
if (process.env.MAP) { const [l, x0, y0, x1, y1] = process.env.MAP.split(",").map(Number), n = nets.find((n) => n.name === (process.env.PROBE ?? "LCD_D0"))!, id = idOf(n.name)
  for (let j = gy(y1); j >= gy(y0); j--) { let s = ""; for (let i = gx(x0); i <= gx(x1); i++) { const c = j * NX + i, v = l === 2 ? statV[c] : statT[l][c]; s += term[c] && l === 1 ? "T" : v === 0 ? "." : v === id ? "o" : v === -1 ? "#" : "x" } console.log(s) } }
if (process.env.SHOWBAD) for (const n of nets) { if (!n.path) continue; const { bad, padClash } = conflicts(n); if (bad.length || padClash) console.log(n.name, "pad", sigPads[n.pad!].conn, sigPads[n.pad!].pin, padClash ? "PAD CLASH" : "", "bad nodes:", bad.slice(0, 8).map((u) => `${LAYERS[u >= NN ? 1 : 0]}(${wx((u % NN) % NX).toFixed(1)},${wy(((u % NN) / NX) | 0).toFixed(2)})`).join(" "), "| path:", n.path.filter((_, i) => i % 6 === 0).map((u) => `${u >= NN ? "b" : "i"}(${wx((u % NN) % NX).toFixed(1)},${wy(((u % NN) / NX) | 0).toFixed(1)})`).join(" ").slice(0, 400)) }
if (process.env.WHYV) for (const n of nets.filter((n) => !n.path)) { const x = wx(n.src % NX), y = wy((n.src / NX) | 0), id = idOf(n.name); console.log(n.name, "statV at ball", statV[n.src], "own id", id, "blockers:", items.filter((it) => it.layers.length && idOf(it.net.startsWith("NC:") ? "x" : it.net) !== id && gap(disc(x, y, 0), it) < (it.kind === "ddr" || it.kind === "ddrvia" ? (it.pts.every((p) => inCpu(p.x, p.y)) ? CLR : CLR_DDR) : CLR) + VIA_D / 2 + 0.005).map((it) => `${it.net} ${it.kind} ${it.layers.join("+")} ${gap(disc(x, y, 0), it).toFixed(3)}`).slice(0, 4).join(" | ")) }
