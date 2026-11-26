// Inner-layer copper for the module: L2 GND, L3 VDDS_DDR (west) + 3V3 / 1V8 (east), L4 core / MPU / VREF and the
// few local nets that cannot run on the outer layers, L5 GND.
// Every net first gets a 0.15 mm skeleton that reaches each of its vias (so connectivity never depends on the
// fill), then the free copper is filled, kept clear of other nets and stripped of slivers and islands.
// Output: module/pours.json (polygons with holes per layer/net) and a connectivity + clearance report.
import type { Pt } from "./geom"
const dir = import.meta.dir
const plan = await Bun.file(dir + "/plan.json").json(), items = (await Bun.file(dir + "/plan-items.json").json()).items as any[]
const ROUTES = process.env.ROUTES ?? dir + "/routes.json" // ROUTES=none: planes from the fixed copper only
const routes = ROUTES !== "none" && (await Bun.file(ROUTES).exists()) ? await Bun.file(ROUTES).json() : { nets: {} }
const P = 0.05, E = plan.edge, NX = Math.round((E.x1 - E.x0) / P), NY = Math.round((E.y1 - E.y0) / P), NN = NX * NY
const cx = (i: number) => E.x0 + (i + 0.5) * P, cy = (j: number) => E.y0 + (j + 0.5) * P
const LAYERS = ["inner1", "inner2", "inner3", "inner4"] as const
const XB = +(process.env.XB ?? -46.4) // layer 3: VDDS_DDR west of this, 3V3 / 1V8 east of it
// trunk order, with the layers a net may use (first = preferred) and where it is filled
// skeleton order: the nets with the fewest ways through first, the big planes last
// the 3V3 balls N5, P5, P6, P7 sit west of the layer-3 split: this corner of layer 3 is 3V3 too
// layer 3 north and south of the processor's 3V3/1V8 rows carries VDDS_DDR too, so DDR bypass capacitors there sit on their plane
// north strip under J1 (VIN5 and the J1 supply pins), the PMIC's SYS node, the east power column
const NORTH = 29.4, SYSBOX = (x: number, y: number) => x > -34.8 && x < -25.4 && y > 8.7 && y < 18.3, EAST = -36.5
const DDRBAND = (x: number, y: number) => (x < -37.6 && ((y > 19.25 && y < NORTH) || y < 10.15)) || (x < -41.6 && y > 12.0 && y < 18.35) || (x >= -37.6 && y < 8.5) // + the core-ball interior (no 3V3 balls there) + DCDC1's output south of the PMIC
const SW = (x: number, y: number) => x > -49.1 && x < XB && y > 10.9 && y < 12.0 // row P only: N6 above it is a 1V8 ball
const NETS: { name: string; layers: number[]; fill: Record<number, (x: number, y: number) => boolean> }[] = [
  { name: "GND", layers: [0], fill: { 0: () => true, 3: () => true } },
  ...["VDDS_RTC", ...plan.innerNets].map((name: string) => ({ name, layers: [2, 1], fill: {} })),
  { name: "DDR_VREF", layers: [1, 2], fill: { 2: (x: number, y: number) => x < -53 && x > -76 && y > 9 && y < 21 } }, // the channel between the two chips
  { name: "SYS", layers: [1, 2], fill: { 1: (x: number, y: number) => SYSBOX(x, y) } }, // PMIC power-path output: under the PMIC on layer 3
  { name: "VIN5", layers: [1, 2], fill: { 1: (x: number, y: number) => y > NORTH, 2: (x: number, y: number) => y > 31.6 || (x > EAST && y > 19.0) } }, // +5 V from J1: the north strip on layers 3 and 4, down the east column on layer 4
  { name: "VDD_3V3", layers: [1, 2], fill: { 1: (x: number, y: number) => y < NORTH && !SYSBOX(x, y) && (((x >= XB || SW(x, y)) && !DDRBAND(x, y)) || (x > EAST && y > 8.5)) } },
  { name: "VDD_1V8", layers: [1, 2], fill: { 2: (x: number, y: number) => (x >= XB && x < EAST && y < 13) || (y > NORTH && y < 31.6) } }, // processor 1V8 balls, J1's 1.8 V pins
  { name: "VDDS_DDR", layers: [1, 2], fill: { 1: (x: number, y: number) => y < NORTH && ((x < XB && !SW(x, y)) || DDRBAND(x, y)) } },
  { name: "VDD_MPU", layers: [2, 1], fill: { 2: (x: number, y: number) => y < NORTH && !(x > EAST && y > 19.0) } },
  { name: "VDD_CORE", layers: [2, 1], fill: { 2: (x: number, y: number) => y < NORTH && !(x > EAST && y > 19.0) } },
]
// STACK=pb (routing playbook): every supply is an island on layer 3; layers 2 and 5 ground; layer 4 carries signals only
const PB = (process.env.STACK ?? "pb") === "pb" // STACK=old: the earlier layout (core/MPU/1V8 on layer 4 as planes)
const CORE_AREA = (x: number, y: number) => y < NORTH && x >= XB && !SYSBOX(x, y)
if (PB) NETS.splice(0, NETS.length,
  { name: "GND", layers: [0, 3], fill: { 0: () => true, 3: () => true } },
  // VDDS_RTC is a small rail: routed as a trace by the signal router (playbook), not a plane island
  ...plan.innerNets.map((name: string) => ({ name, layers: [1], fill: {} })),
  { name: "DDR_VREF", layers: [1], fill: { 1: (x: number, y: number) => x < -53 && x > -76 && y > 9 && y < 21 } },
  { name: "SYS", layers: [1], fill: { 1: (x: number, y: number) => SYSBOX(x, y) } },
  { name: "VIN5", layers: [1], fill: { 1: (x: number, y: number) => y > NORTH } },
  // core and MPU: layer-4 islands under the processor and their feeds from the PMIC (the AM335x ball map interleaves
  // five supplies in its core; one layer cannot keep them all in one piece each); everything else on layer 3
  { name: "VDD_MPU", layers: [2], fill: { 2: (x: number, y: number) => CORE_AREA(x, y) || SYSBOX(x, y) } }, // also the PMIC's SYS area on layer 4 (SYS is on layer 3 only): the 1 A feed from DCDC2 runs through it
  { name: "VDD_CORE", layers: [2], fill: { 2: CORE_AREA } },
  { name: "VDD_3V3", layers: [1, 2], fill: { 1: CORE_AREA } }, // like 1.8 V: a thin link on layer 4 where layer 3 is walled in
  { name: "VDD_1V8", layers: [1, 2], fill: { 1: CORE_AREA } }) // low current (I/O, PLL, USB PHY): may link through layer 4 where layer 3 is taken
if (PB) NETS.splice(NETS.findIndex((n) => n.name === "VDD_MPU"), 0,
  { name: "VDDS_DDR", layers: [1], fill: { 1: (x: number, y: number) => y < NORTH && ((x < XB && !SW(x, y)) || DDRBAND(x, y)) } })
/** where each supply comes from: the feed-width check starts there */
const SOURCE: Record<string, RegExp> = { VIN5: /^V_J1_/, SYS: /^V_U_PMIC_pin(7|8)$/, VDDS_DDR: /^V_L_DCDC1_pin2/, VDD_MPU: /^V_L_DCDC2_pin2/, VDD_CORE: /^V_L_DCDC3_pin2/, VDD_3V3: /^V_L_3V3_pin2/, VDD_1V8: /^V_L_1V8_pin2/, VDDS_RTC: /^V_U_PMIC_pin3$/ }
const isSource = (net: string, v: { x: number; y: number }) => !!SOURCE[net] && plan.vias.some((p: any) => SOURCE[net].test(p.name) && p.net === net && p.x === v.x && p.y === v.y)
const CENTRE4 = new Set(["VDD_CORE", "VDD_MPU"]), CENTRE3 = new Set(PB ? ["VDD_1V8", "VDD_3V3"] : ["VDDS_DDR"]) // PB: layer 3 inside the processor core belongs to 1.8 V and 3.3 V (VDDS_DDR reaches its west column from the west) // who may cross the middle of the processor on layers 4 / 3 cheaply (layer 3 there is VDDS_DDR copper for the DDR bypass capacitors)
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
for (const h of plan.holes) { const R = h.d / 2 + 0.4 + P * 0.75 /* a cell closes when any part of it, not only its centre, is within 0.4 mm */; for (let j = cj(h.y - R); j <= cj(h.y + R); j++) for (let i = ci(h.x - R); i <= ci(h.x + R); i++) if (i >= 0 && j >= 0 && i < NX && j < NY && Math.hypot(cx(i) - h.x, cy(j) - h.y) < R) stat[j * NX + i] = 127 }
for (const v of vias) { const R = Math.max(v.d, 0.3) / 2 + ANTI, k = idx.get(v.net) ?? 127 // exact: a cell is closed when any part of its square is nearer than R
  for (let j = Math.max(0, cj(v.y - R) - 1); j <= Math.min(NY - 1, cj(v.y + R) + 1); j++) for (let i = Math.max(0, ci(v.x - R) - 1); i <= Math.min(NX - 1, ci(v.x + R) + 1); i++) if (Math.hypot(Math.max(Math.abs(cx(i) - v.x) - P / 2, 0), Math.max(Math.abs(cy(j) - v.y) - P / 2, 0)) < R - 1e-9) { const c = j * NX + i; stat[c] = stat[c] === 0 || stat[c] === k ? k : 127 } }
// signal traces on an inner layer: no plane copper within 0.15 mm of them
const blockL = LAYERS.map(() => new Uint8Array(NN))
for (const n of Object.values(routes.nets) as any[]) for (const g of n.segs) { const l = LAYERS.indexOf(g.layer); if (l < 0) continue
  for (let i = 0; i + 1 < g.pts.length; i++) { const a = g.pts[i], b = g.pts[i + 1], R = (g.w ?? 0.1) / 2 + 0.15 + P / 2, dx = b.x - a.x, dy = b.y - a.y, len2 = dx * dx + dy * dy
    for (let j = Math.max(0, cj(Math.min(a.y, b.y) - R)); j <= Math.min(NY - 1, cj(Math.max(a.y, b.y) + R)); j++) for (let i2 = Math.max(0, ci(Math.min(a.x, b.x) - R)); i2 <= Math.min(NX - 1, ci(Math.max(a.x, b.x) + R)); i2++) { const t = len2 ? Math.max(0, Math.min(1, ((cx(i2) - a.x) * dx + (cy(j) - a.y) * dy) / len2)) : 0
      if (Math.hypot(cx(i2) - a.x - t * dx, cy(j) - a.y - t * dy) < R) blockL[l][j * NX + i2] = 1 } } }
for (const g of plan.ddrInner ?? []) { const l = 2, a = g.a, b = g.b, R = 0.051 + 0.15 + P / 2, dx = b.x - a.x, dy = b.y - a.y, len2 = dx * dx + dy * dy // DDR sections on layer 4
  for (let j = Math.max(0, cj(Math.min(a.y, b.y) - R)); j <= Math.min(NY - 1, cj(Math.max(a.y, b.y) + R)); j++) for (let i2 = Math.max(0, ci(Math.min(a.x, b.x) - R)); i2 <= Math.min(NX - 1, ci(Math.max(a.x, b.x) + R)); i2++) { const t = len2 ? Math.max(0, Math.min(1, ((cx(i2) - a.x) * dx + (cy(j) - a.y) * dy) / len2)) : 0; if (Math.hypot(cx(i2) - a.x - t * dx, cy(j) - a.y - t * dy) < R) blockL[l][j * NX + i2] = 1 } }
// ---------- per-layer ownership ----------
const owner = LAYERS.map(() => new Int8Array(NN)), trunk = LAYERS.map(() => new Uint8Array(NN))
const report: string[] = []
// ---------- supply feeds (feeds.ts): fixed layer-4 strips from the regulators into the processor core ----------
const feeds: { net: string; w: number; pts: Pt[] }[] = (await Bun.file(dir + "/design/feeds.json").exists()) ? await Bun.file(dir + "/design/feeds.json").json() : []
const feedNet = new Int8Array(NN) // net index + 1 of the layer-4 feed copper in a cell
for (const f of feeds) { const k = idx.get(f.net); if (!k) throw Error("feed for a net without a plane: " + f.net)
  for (let n = 0; n + 1 < f.pts.length; n++) { const a = f.pts[n], b = f.pts[n + 1], R = f.w / 2, dx = b.x - a.x, dy = b.y - a.y, len2 = dx * dx + dy * dy
    for (let j = Math.max(0, cj(Math.min(a.y, b.y) - R)); j <= Math.min(NY - 1, cj(Math.max(a.y, b.y) + R)); j++) for (let i = Math.max(0, ci(Math.min(a.x, b.x) - R)); i <= Math.min(NX - 1, ci(Math.max(a.x, b.x) + R)); i++) {
      const t = len2 ? Math.max(0, Math.min(1, ((cx(i) - a.x) * dx + (cy(j) - a.y) * dy) / len2)) : 0
      if (Math.hypot(cx(i) - a.x - t * dx, cy(j) - a.y - t * dy) <= R) { const c = j * NX + i; if (stat[c] !== 0 && stat[c] !== k) throw Error(`feed ${f.net} crosses foreign copper at (${cx(i).toFixed(2)}, ${cy(j).toFixed(2)})`); feedNet[c] = k; owner[2][c] = k; trunk[2][c] = 1 } } } }
/** cells where a (2k+1) square of the given predicate is all true */
function boxAll(pred: (c: number) => boolean, k: number): Uint8Array { const S = new Int32Array((NX + 1) * (NY + 1))
  for (let j = 0; j < NY; j++) { let row = 0; for (let i = 0; i < NX; i++) { row += pred(j * NX + i) ? 0 : 1; S[(j + 1) * (NX + 1) + i + 1] = S[j * (NX + 1) + i + 1] + row } }
  const out = new Uint8Array(NN)
  for (let j = k; j < NY - k; j++) for (let i = k; i < NX - k; i++) { const a = S[(j - k) * (NX + 1) + i - k], b = S[(j - k) * (NX + 1) + i + k + 1], c = S[(j + k + 1) * (NX + 1) + i - k], d = S[(j + k + 1) * (NX + 1) + i + k + 1]; if (d - b - c + a === 0) out[j * NX + i] = 1 }
  return out }
const TK = 1, GAPK = 4 // skeleton half-width (cells) and its distance to other nets' copper (cells)
// wide trunks (half-width in cells, 0.05 mm each) for the supplies that carry the most current from a regulator on
// this module: VDD_MPU (up to 1 A, PMIC to the processor core on layer 4) and VIN5 (5 V from the CM4 pins to the PMIC
// and the bucks). FAT=0 turns them off.
const FAT: Record<string, number> = process.env.FAT === "0" ? {} : { VDD_MPU: 5, VIN5: 4 }
// where a trunk must also reach besides the vias it can get to at its width: VDD_MPU's copper just east of the ball
// field (its balls are inside the field, where no wide trunk fits), through the band between the field and the PMIC
const FAT_TO: Record<string, Pt[]> = { VDD_MPU: [{ x: -36.0, y: 16.5 }] }
const D8 = [1, 0, -1, 0, 0, 1, 0, -1, 1, 1, 1, -1, -1, 1, -1, -1]
for (const [ni, net] of NETS.entries()) { const k = ni + 1, mine = vias.filter((v) => v.net === net.name); if (!mine.length) continue
  const cellOf = (v: V) => cj(v.y) * NX + ci(v.x)
  const connected = new Uint8Array(mine.length), byCell = new Map<number, number[]>(); mine.forEach((v, m) => { const c = cellOf(v); byCell.set(c, [...(byCell.get(c) ?? []), m]) })
  // start at a connector pin of the net when it has one
  const start = Math.max(0, mine.findIndex((v) => isSource(net.name, v)))
  // high-current supplies: first a wide trunk to every via it can reach at that width, then the thin skeleton for the
  // rest, grown from the trunk
  for (const [pass, tk] of (FAT[net.name] ? [FAT[net.name], TK] : [TK]).entries()) {
  const valid = net.layers.map((l) => { const a = boxAll((c) => (stat[c] === 0 || stat[c] === k) && !blockL[l][c], tk), b = boxAll((c) => owner[l][c] === 0 || owner[l][c] === k, GAPK + tk - TK); for (let c = 0; c < NN; c++) a[c] &= b[c]; return a })
  const claim = (l: number, c: number) => { const i = c % NX, j = (c / NX) | 0; for (let dj = -tk; dj <= tk; dj++) for (let di = -tk; di <= tk; di++) { const c2 = (j + dj) * NX + i + di; owner[l][c2] = k; trunk[l][c2] = 1 } }
  // cheapest-first search over every allowed layer at once; a reached via feeds all layers and the search goes on
  { const L = net.layers, dist = L.map(() => new Float32Array(NN).fill(1e9)), pred = L.map(() => new Int32Array(NN).fill(-1)), heap: number[] = [], key: number[] = []
    const hpush = (kk: number, n: number) => { let i = heap.length; heap.push(n); key.push(kk); while (i > 0) { const p = (i - 1) >> 1; if (key[p] <= key[i]) break; [heap[p], heap[i]] = [heap[i], heap[p]]; [key[p], key[i]] = [key[i], key[p]]; i = p } }
    const hpop = () => { const top = heap[0], tk = key[0], n = heap.pop()!, kk = key.pop()!; if (heap.length) { heap[0] = n; key[0] = kk; let i = 0; for (;;) { const a = 2 * i + 1, b = a + 1; let m = i; if (a < heap.length && key[a] < key[m]) m = a; if (b < heap.length && key[b] < key[m]) m = b; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; [key[m], key[i]] = [key[i], key[m]]; i = m } } return [top, tk] }
    const factor = (s: number, c: number) => { const l = L[s], x = cx(c % NX), y = cy((c / NX) | 0), centre = x > -48.0 && x < -41.6 && y > 11.9 && y < 18.4
      return (s === 0 ? 1 : 4) * (centre && l === 2 && !CENTRE4.has(net.name) ? 30 : 1) * (centre && l === 1 && !CENTRE3.has(net.name) ? 8 : 1) }
    const feed = (m: number) => { connected[m] = 1; const c = cellOf(mine[m]); L.forEach((_, s) => { if (valid[s][c]) { dist[s][c] = 0; pred[s][c] = -1; hpush(0, s * NN + c) } }) }
    // a wide trunk starts and ends within STUB of a via (the cells right at a via are usually too tight for it); the
    // thin pass then joins every via to the trunk with a short stub
    const wide = tk > TK, near = new Map<number, number[]>(), STUB = Math.round(0.8 / P)
    const goals: { x: number; y: number }[] = wide ? [...mine, ...(FAT_TO[net.name] ?? [])] : []
    goals.forEach((v, m) => { const i0 = ci(v.x), j0 = cj(v.y); for (let dj = -STUB; dj <= STUB; dj++) for (let di = -STUB; di <= STUB; di++) { if (Math.hypot(di, dj) > STUB) continue; const c = (j0 + dj) * NX + i0 + di; if (c >= 0 && c < NN) near.set(c, [...(near.get(c) ?? []), m]) } })
    const reached = new Uint8Array(goals.length)
    if (wide) { reached[start] = 1; for (const [c, ms] of near) if (ms.includes(start)) L.forEach((_, s) => { if (valid[s][c]) { dist[s][c] = 0; pred[s][c] = -1; hpush(0, s * NN + c) } }) }
    else if (pass === 0 || !L.some((l) => trunk[l].some((t, c) => t && owner[l][c] === k))) feed(start)
    else { mine.forEach((_, m) => { if (connected[m]) feed(m) }); L.forEach((l, s) => { for (let c = 0; c < NN; c++) if (trunk[l][c] && owner[l][c] === k && valid[s][c]) { dist[s][c] = 0; pred[s][c] = -1; hpush(0, s * NN + c) } }) }
    while (heap.length) { const [u, du] = hpop(), s = (u / NN) | 0, c = u % NN, l = L[s]; if (du > dist[s][c]) continue
      const i = c % NX, j = (c / NX) | 0
      if (wide) { for (const m of near.get(c) ?? []) if (!reached[m]) { reached[m] = 1; for (let b = c; b !== -1; b = pred[s][b]) { claim(l, b); if (dist[s][b] === 0) break } dist[s][c] = 0 } }
      else for (const m of byCell.get(c) ?? []) if (!connected[m]) { const way: number[] = []; for (let b = c; b !== -1; b = pred[s][b]) { way.push(b); if (trunk[l][b] && owner[l][b] === k) break }
        for (const b of way) claim(l, b); feed(m) }
      for (let d = 0; d < 16; d += 2) { const ii = i + D8[d], jj = j + D8[d + 1]; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY) continue; const c2 = jj * NX + ii; if (!valid[s][c2]) continue
        const nd = Math.fround(dist[s][c] + (d < 8 ? 1 : 1.4142) * factor(s, c2)); if (nd < dist[s][c2]) { dist[s][c2] = nd; pred[s][c2] = c; hpush(nd, s * NN + c2) } } } } }
  const miss = mine.filter((_, m) => !connected[m])
  report.push(`${net.name}: ${mine.length - miss.length}/${mine.length} vias on the skeleton${miss.length ? " !! missing " + miss.slice(0, 6).map((v) => `(${v.x.toFixed(2)}, ${v.y.toFixed(2)})`).join(" ") : ""}`) }
// CORRIDORS_OUT=<file>: every supply's skeleton cells per layer (the router keeps foreign vias off them, and foreign
// traces off them on their layer), from a run without signal routes
if (process.env.CORRIDORS_OUT) { const out: { net: string; layer: string; cells: [number, number][] }[] = []
  for (const [l, layer] of LAYERS.entries()) for (const [ni, net] of NETS.entries()) { const k = ni + 1, cells: [number, number][] = []
    for (let c = 0; c < NN; c++) if (trunk[l][c] && owner[l][c] === k) cells.push([+cx(c % NX).toFixed(3), +cy((c / NX) | 0).toFixed(3)])
    if (cells.length) out.push({ net: net.name, layer, cells }) }
  await Bun.write(process.env.CORRIDORS_OUT, JSON.stringify(out)); console.log(`corridors: ${out.length} net/layer sets, ${out.reduce((s, o) => s + o.cells.length, 0)} cells -> ${process.env.CORRIDORS_OUT}`) }
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
  for (const [ni, net] of NETS.entries()) { const k = ni + 1; if (!["VDD_3V3", "VDD_1V8", "VDD_CORE", "VDD_MPU", "VDDS_DDR", "VIN5", "SYS"].includes(net.name)) continue
    const mine = vias.filter((v) => v.net === net.name), wide = LAYERS.map((_, l) => { const core = new Uint8Array(NN), w = new Uint8Array(NN) // opening with a 4x4 square
      for (let j = 0; j < NY - 3; j++) for (let i = 0; i < NX - 3; i++) { let ok = true; for (let dj = 0; dj < 4 && ok; dj++) for (let di = 0; di < 4; di++) if (owner[l][(j + dj) * NX + i + di] !== k) { ok = false; break } if (ok) core[j * NX + i] = 1 }
      for (let c = 0; c < NN; c++) if (core[c]) { const i = c % NX, j = (c / NX) | 0; for (let dj = 0; dj < 4; dj++) for (let di = 0; di < 4; di++) w[(j + dj) * NX + i + di] = 1 }
      return w })
    const seen = LAYERS.map(() => new Uint8Array(NN)), st: number[] = [], hit = new Set<number>()
    const near = (l: number, v: V) => { const c0 = cj(v.y) * NX + ci(v.x); for (let dj = -3; dj <= 3; dj++) for (let di = -3; di <= 3; di++) { const c = c0 + dj * NX + di; if (c >= 0 && c < NN && wide[l][c]) return c } return -1 }
    const enter = (m: number) => { if (hit.has(m)) return; hit.add(m); LAYERS.forEach((_, l) => { const c = near(l, mine[m]); if (c >= 0 && !seen[l][c]) { seen[l][c] = 1; st.push(l * NN + c) } }) }
    mine.forEach((v, m) => { if (isSource(net.name, v)) enter(m) })
    const at = new Map<number, number[]>(); mine.forEach((v, m) => LAYERS.forEach((_, l) => { const c = near(l, v); if (c >= 0) at.set(l * NN + c, [...(at.get(l * NN + c) ?? []), m]) }))
    while (st.length) { const u = st.pop()!, l = (u / NN) | 0, c = u % NN, i = c % NX, j = (c / NX) | 0; for (const m of at.get(u) ?? []) enter(m)
      for (let d = 0; d < 8; d += 2) { const ii = i + D8[d], jj = j + D8[d + 1]; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY) continue; const c2 = jj * NX + ii; if (wide[l][c2] && !seen[l][c2]) { seen[l][c2] = 1; st.push(l * NN + c2) } } }
    report.push(`feed width ${net.name}: ${hit.size}/${mine.length} vias reached from the source (regulator output / connector) through copper >= 0.2 mm wide` + (hit.size < mine.length ? ` (not: ${mine.map((v, m) => hit.has(m) ? '' : (v as any).name ?? '').filter(Boolean).slice(0, 14).join(' ')})` : '')) } }
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
