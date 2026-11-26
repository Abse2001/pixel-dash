// Layer-4 supply feeds: fixed copper strips from each regulator's output vias into the processor's power core, laid
// out before the signals are routed (the router routes around them; the plane builder grows its planes from them).
// The core itself carries no signal copper (see the keep-outs in autoroute.ts), so a feed only has to cross the BGA's
// signal rings and the area between the processor and the regulators. A strip keeps 0.1 mm from every foreign via
// and from the DDR block's layer-4 copper, and inside the ball field it keeps every ball's via site free, so it runs in
// the channels between ball rows. Output: design/feeds.json [{ net, w, pts }] in board coordinates, layer 4.
import type { Pt } from "./geom"
const dir = import.meta.dir
const plan = await Bun.file(dir + "/plan.json").json(), items = (await Bun.file(dir + "/plan-items.json").json()).items as any[]
const W = 0.24, CLR = 0.1, VIA_D = 0.3, P = 0.05 // 0.24 mm: between 0.8 mm-pitch ball rows a strip needs via 0.15 + 0.1 + w/2 <= 0.4
// the processor's power core (keep-out 0 in autoroute.ts): a feed is done once it is inside
const CORE = { x0: -48.8, y0: 11.15, x1: -40.8, y1: 19.15 }
// feeds: net and its source vias (regulator output, plan via names). A feed ends as soon as it is inside the core (the
// plane builder spreads each supply over its balls there); a second feed of a net takes a separate path.
const FEEDS: { net: string; source: RegExp }[] = [
  { net: "VDD_CORE", source: /^V_L_DCDC3_pin2/ }, { net: "VDD_MPU", source: /^V_L_DCDC2_pin2/ }, { net: "VDD_1V8", source: /^V_L_1V8_pin2/ },
  { net: "VDD_CORE", source: /^V_L_DCDC3_pin2/ }, { net: "VDD_MPU", source: /^V_L_DCDC2_pin2/ },
]
const E = plan.edge, NX = Math.round((E.x1 - E.x0) / P), NY = Math.round((E.y1 - E.y0) / P)
const cx = (i: number) => E.x0 + (i + 0.5) * P, cy = (j: number) => E.y0 + (j + 0.5) * P, ci = (x: number) => Math.floor((x - E.x0) / P), cj = (y: number) => Math.floor((y - E.y0) / P)
// layer-4 copper already fixed: every via (planner, DDR block) and the DDR block's layer-4 sections
type Disc = { x: number; y: number; r: number; net: string }
const discs: Disc[] = plan.vias.map((v: any) => ({ x: v.x, y: v.y, r: v.d / 2, net: v.net }))
for (const it of items) if (it.kind === "ddrvia") discs.push({ x: it.pts[0].x, y: it.pts[0].y, r: it.r, net: it.net })
const segs: { a: Pt; b: Pt; r: number; net: string }[] = (plan.ddrInner ?? []).map((g: any) => ({ a: g.a, b: g.b, r: 0.051, net: g.net }))
// every processor ball keeps a via site (a 0.3 mm via in its pad), whatever its net
const balls: Disc[] = items.filter((i) => i.kind === "ball" && i.ref.startsWith("U1.")).map((i) => ({ x: i.pts[0].x, y: i.pts[0].y, r: VIA_D / 2, net: i.net ?? "" }))
const segDist = (x: number, y: number, a: Pt, b: Pt) => { const dx = b.x - a.x, dy = b.y - a.y, L2 = dx * dx + dy * dy, t = L2 ? Math.max(0, Math.min(1, ((x - a.x) * dx + (y - a.y) * dy) / L2)) : 0; return Math.hypot(x - a.x - t * dx, y - a.y - t * dy) }
const blocked = new Uint8Array(NX * NY) // 1: no strip centre of the current net may lie here
function blockAround(x: number, y: number, R: number) { for (let j = Math.max(0, cj(y - R) - 1); j <= Math.min(NY - 1, cj(y + R) + 1); j++) for (let i = Math.max(0, ci(x - R) - 1); i <= Math.min(NX - 1, ci(x + R) + 1); i++) if (Math.hypot(cx(i) - x, cy(j) - y) < R) blocked[j * NX + i] = 1 }
const out: { net: string; w: number; pts: Pt[] }[] = []
const report: string[] = []
for (const f of FEEDS) {
  blocked.fill(0)
  for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) { const x = cx(i), y = cy(j); if (x < E.x0 + 0.5 || x > E.x1 - 0.5 || y < E.y0 + 0.5 || y > E.y1 - 0.5) blocked[j * NX + i] = 1 }
  for (const d of discs) if (d.net !== f.net) blockAround(d.x, d.y, d.r + CLR + W / 2)
  for (const b of balls) if (b.net !== f.net) blockAround(b.x, b.y, b.r + CLR + W / 2)
  for (const s of segs) if (s.net !== f.net) { const R = s.r + CLR + W / 2
    for (let j = Math.max(0, cj(Math.min(s.a.y, s.b.y) - R)); j <= Math.min(NY - 1, cj(Math.max(s.a.y, s.b.y) + R)); j++) for (let i = Math.max(0, ci(Math.min(s.a.x, s.b.x) - R)); i <= Math.min(NX - 1, ci(Math.max(s.a.x, s.b.x) + R)); i++) if (segDist(cx(i), cy(j), s.a, s.b) < R) blocked[j * NX + i] = 1 }
  // other nets' feeds with clearance; this net's earlier feed too, beyond 1 mm from its source (a separate path)
  for (const o of out) for (let k = 0; k + 1 < o.pts.length; k++) { const a = o.pts[k], b = o.pts[k + 1], R = o.net === f.net ? o.w / 2 + 0.6 : o.w / 2 + CLR + W / 2
    if (o.net === f.net && Math.hypot(a.x - o.pts[0].x, a.y - o.pts[0].y) < 1 && Math.hypot(b.x - o.pts[0].x, b.y - o.pts[0].y) < 1) continue
    for (let j = Math.max(0, cj(Math.min(a.y, b.y) - R)); j <= Math.min(NY - 1, cj(Math.max(a.y, b.y) + R)); j++) for (let i = Math.max(0, ci(Math.min(a.x, b.x) - R)); i <= Math.min(NX - 1, ci(Math.max(a.x, b.x) + R)); i++) if (segDist(cx(i), cy(j), a, b) < R) blocked[j * NX + i] = 1 }
  // start: the source vias; goal: inside the core at the requested rows
  const src = plan.vias.filter((v: any) => f.source.test(v.name) && v.net === f.net)
  if (!src.length) { report.push(`!! ${f.net}: no source via matches ${f.source}`); continue }
  const goal = (i: number, j: number) => { const x = cx(i), y = cy(j); return x > CORE.x0 + 0.2 && x < CORE.x1 - 0.2 && y > CORE.y0 + 0.2 && y < CORE.y1 - 0.2 }
  // A* over 8 directions with a turn penalty (clean, mostly straight strips)
  const N = NX * NY, dist = new Float64Array(N * 8).fill(1e18), prev = new Int32Array(N * 8).fill(-1), heap: [number, number][] = []
  const push = (k: number, d: number) => { heap.push([d, k]); let i = heap.length - 1; while (i > 0) { const p = (i - 1) >> 1; if (heap[p][0] <= heap[i][0]) break; [heap[p], heap[i]] = [heap[i], heap[p]]; i = p } }
  const pop = () => { const top = heap[0], last = heap.pop()!; if (heap.length) { heap[0] = last; let i = 0; for (;;) { const a = 2 * i + 1, b = a + 1; let m = i; if (a < heap.length && heap[a][0] < heap[m][0]) m = a; if (b < heap.length && heap[b][0] < heap[m][0]) m = b; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; i = m } } return top }
  const D = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
  const h = (i: number, j: number) => Math.hypot(Math.max(0, CORE.x0 + 0.2 - cx(i), cx(i) - CORE.x1 + 0.2), Math.max(0, CORE.y0 + 0.2 - cy(j), cy(j) - CORE.y1 + 0.2)) * 0.999
  for (const v of src) { const i = ci(v.x), j = cj(v.y); for (let d = 0; d < 8; d++) { const k = (j * NX + i) * 8 + d; dist[k] = 0; push(k, h(i, j)) } }
  let end = -1
  while (heap.length) { const [fk, k] = pop(), c = k >> 3, dir = k & 7, i = c % NX, j = (c / NX) | 0, g = dist[k]; if (fk - h(i, j) > g + 1e-9) continue
    if (goal(i, j)) { end = k; break }
    for (let nd = 0; nd < 8; nd++) { const ii = i + D[nd][0], jj = j + D[nd][1]; if (ii < 0 || jj < 0 || ii >= NX || jj >= NY) continue
      const c2 = jj * NX + ii, src0 = dist[k] === 0; if (blocked[c2] && !src0) continue
      const turn = nd === dir ? 0 : Math.min((nd - dir + 8) % 8, (dir - nd + 8) % 8)
      const g2 = g + Math.hypot(D[nd][0], D[nd][1]) * P + (src0 ? 0 : turn * 0.3), k2 = c2 * 8 + nd
      if (g2 < dist[k2]) { dist[k2] = g2; prev[k2] = k; push(k2, g2 + h(ii, jj)) } } }
  if (end < 0) { report.push(`!! ${f.net} -> core: no path`); continue }
  const cells: Pt[] = []; for (let k = end; k !== -1; k = prev[k]) cells.unshift({ x: +cx((k >> 3) % NX).toFixed(4), y: +cy(((k >> 3) / NX) | 0).toFixed(4) })
  // keep only the corners
  const pts = cells.filter((p, n) => n === 0 || n === cells.length - 1 || Math.abs((p.x - cells[n - 1].x) * (cells[n + 1].y - p.y) - (p.y - cells[n - 1].y) * (cells[n + 1].x - p.x)) > 1e-9)
  // start exactly at the nearest source via centre
  const s0 = src.reduce((a: any, b: any) => Math.hypot(a.x - pts[0].x, a.y - pts[0].y) < Math.hypot(b.x - pts[0].x, b.y - pts[0].y) ? a : b); pts.unshift({ x: s0.x, y: s0.y })
  const len = pts.slice(1).reduce((s, p, n) => s + Math.hypot(p.x - pts[n].x, p.y - pts[n].y), 0)
  out.push({ net: f.net, w: W, pts }); report.push(`${f.net} -> core: ${len.toFixed(1)} mm, ${pts.length - 1} segments, enters at (${pts.at(-1)!.x}, ${pts.at(-1)!.y})`)
}
await Bun.write(dir + "/design/feeds.json", JSON.stringify(out, null, 1))
console.log(report.join("\n"))
