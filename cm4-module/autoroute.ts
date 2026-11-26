// Routes the CM4 module's signal nets with the tscircuit autorouter (@tscircuit/capacity-autorouter, default pipeline).
// Input: plan.json / plan-items.json (every piece of copper the planner placed, the DDR block, the nets and their
// terminals). Output: routes.json (same format the plane builder, the renderer and the checker read) and
// autoroute.srj.json (the exact SimpleRouteJson given to the solver, for reproducing solver issues).
// AUTOROUTER=<path to a tscircuit-autorouter checkout> runs a local source tree instead of the installed package.
import type { Item, Pt } from "./geom"
const dir = import.meta.dir
const plan = await Bun.file(dir + "/plan.json").json(), { items }: { items: Item[] } = await Bun.file(dir + "/plan-items.json").json()
const mod = process.env.AUTOROUTER ? await import(process.env.AUTOROUTER + "/lib/index.ts") : await import("@tscircuit/capacity-autorouter")
const PIPELINE = process.env.PIPELINE ?? "AutoroutingPipelineSolver"
const E = plan.edge, W = 0.1, CLR = 0.1, DDR_EXTRA = 0.31 - CLR // TI Table 7-68/7-69: other signals keep four trace widths from DDR copper outside the processor's ball field
const inCpu = (x: number, y: number) => x > -52.4 && x < -37.2 && y > 7.55 && y < 22.75
// signal layers: top, layer 4 (inner3 on the board, "inner1" for the solver) and bottom; layers 2, 3 and 5 are planes,
// which the plane builder fills around the vias and the layer-4 traces afterwards
// Two passes, as a plane layer is normally used: PASS=escape routes only the nets whose balls the DDR copper boxes in on
// both outer layers (they need layer 4 to get out); PASS=main routes every other net on the outer layers only, so layer 4
// stays plane copper (vias may pierce it, the plane flows around them; no traces). Without PASS: one pass, three layers.
const PASS = process.env.PASS ?? "", TWO = PASS === "main"
const LAYERS = TWO ? ["top", "bottom"] : ["top", "inner1", "bottom"], toBoard: Record<string, string> = { top: "top", inner1: "inner3", bottom: "bottom" }
// layer-4 copper in the outer-layer pass: a via must not pierce it, and a two-layer problem can only say so by blocking both outer layers there
const toSolver: Record<string, string | string[]> = TWO ? { top: "top", inner3: ["top", "bottom"], bottom: "bottom" } : { top: "top", inner3: "inner1", bottom: "bottom" }
const r4 = (v: number) => +v.toFixed(4)
// ---------- obstacles: all copper already on the board ----------
const routedNets = new Set((plan.nets as any[]).map((n) => n.name))
const obstacles: any[] = []
function obstacle(it: Item, extra = 0) { const layers = it.layers.length === 2 && it.pts.length === 1 && (it.kind === "via" || it.kind === "ddrvia" || it.kind === "hole") ? LAYERS : [...new Set((it.layers as string[]).flatMap((l) => toSolver[l] ?? []))]; if (!layers.length) return
  const connectedTo = it.net.startsWith("NC:") || it.net === "HOLE" ? [] : [it.net], base = { layers, connectedTo, ...(it.kind === "hole" ? { isNonPlatedHole: true, connectedTo: [] } : {}) }
  const r = it.r + extra
  if (it.pts.length === 1) return obstacles.push({ ...base, type: "rect", shape: "circle", center: { x: r4(it.pts[0].x), y: r4(it.pts[0].y) }, width: r4(2 * r), height: r4(2 * r) })
  if (it.pts.length === 2) { const [a, b] = it.pts, L = Math.hypot(b.x - a.x, b.y - a.y) // a track: the rectangle that covers it and its round ends
    return obstacles.push({ ...base, type: "rect", center: { x: r4((a.x + b.x) / 2), y: r4((a.y + b.y) / 2) }, width: r4(L + 2 * r), height: r4(2 * r), ccwRotationDegrees: r4(Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI) }) }
  // a rotated rectangle (pad): centre, side lengths and angle from its corners
  const p = it.pts, c = { x: p.reduce((s, q) => s + q.x, 0) / 4, y: p.reduce((s, q) => s + q.y, 0) / 4 }, w = Math.hypot(p[1].x - p[0].x, p[1].y - p[0].y), h = Math.hypot(p[2].x - p[1].x, p[2].y - p[1].y)
  obstacles.push({ ...base, type: "rect", center: { x: r4(c.x), y: r4(c.y) }, width: r4(w + 2 * r), height: r4(h + 2 * r), ccwRotationDegrees: r4(Math.atan2(p[1].y - p[0].y, p[1].x - p[0].x) * 180 / Math.PI) }) }
for (const it of items) { if (!it.layers.length) continue
  const ddr = it.kind === "ddr" || it.kind === "ddrvia"
  obstacle(it, ddr && !it.pts.every((q) => inCpu(q.x, q.y)) ? DDR_EXTRA : 0) }
// the DDR block's sections on layer 4
for (const g of plan.ddrInner ?? []) obstacle({ pts: [g.a, g.b], r: 0.051, layers: ["inner3" as any], net: g.net, kind: "ddr" }, [g.a, g.b].every((q: Pt) => inCpu(q.x, q.y)) ? 0 : DDR_EXTRA)
// ---------- layer-4 keep-outs: where layer 4 is plane copper the board needs (no trace there, and no new via through it) ----------
// - the processor's ball field: its core/MPU (layer 4) and ground/supply (layers 2, 3, 5) plane webs run between the
//   0.8 mm-pitch ball vias; a via between the balls cuts them. Only the two corners where the balls the DDR copper boxes in
//   leave on layer 4 (LCD/SYSBOOT, south-west; RTC/PMIC control, north-west) stay open. The memory's ball field likewise.
// - the east power column (core/MPU feeds from the PMIC, +5 V) and the strip under J1 (+5 V, 1.8 V and 3.3 V to the CM4 pins).
const KEEPOUT_L4: [number, number, number, number, ("all" | undefined)?][] = [ // x0, y0, x1, y1, "all" = every routed layer
  // processor: the power/ground core (columns 5-14, rows 11.55-18.75) plus half a pitch, on every layer: no signal ball
  // lies there, so signals go around it through the outer signal rings, which keep their escape vias (dog-bones) as in
  // any BGA fan-out; no via may cut the core's plane webs and no crossing can be resolved inside it.
  [-48.8, 11.15, -40.8, 19.15, "all"],
  // the rest of the ball field on layer 4: every signal ball has its via in the pad (plan.ts), so no new via is needed
  // between the balls and none may go there, and no layer-4 trace cuts the plane mesh; the corners where the balls the
  // DDR copper boxes in leave on layer 4 stay open (they are routed in that corner before the plane is filled)
  [-52.0, 11.15, -37.6, 19.55], [-46.8, 19.55, -37.6, 22.35], [-46.8, 7.95, -37.6, 11.15],
  [-74.0, 11.55, -63.6, 18.75], // memory ball field
  [-37.6, 7.0, -35.0, 23.0], // the band between the ball field and the PMIC/bucks: the supplies' way into the field
  // Tried and dropped: a three-row east feed entry through the signal rings, the whole east power column and the strip
  // under J1 (signal balls and parts inside a no-via strip cannot leave the top layer: port-point pathing fails).
]
for (const [x0, y0, x1, y1, all] of KEEPOUT_L4.filter((_, i) => !process.env.KEEPOUTS || process.env.KEEPOUTS.split(",").includes(String(i)))) obstacles.push({ type: "rect", layers: all || TWO ? LAYERS : ["inner1"], connectedTo: [], center: { x: r4((x0 + x1) / 2), y: r4((y0 + y1) / 2) }, width: r4(x1 - x0), height: r4(y1 - y0) })
// layer-4 supply feeds (feeds.ts): fixed copper of their net, laid out before the signals
const FEEDS_FILE = dir + "/design/feeds.json"
for (const f of (await Bun.file(FEEDS_FILE).exists()) ? await Bun.file(FEEDS_FILE).json() : [] as any[]) for (let i = 0; i + 1 < f.pts.length; i++) obstacle({ pts: [f.pts[i], f.pts[i + 1]], r: f.w / 2, layers: ["inner3"], net: f.net, kind: "trace" } as any)
// the escape pass's copper is fixed in the main pass (its layer-4 sections block vias, see toSolver)
const ESCAPE_FILE = dir + "/routes-escape.json"
const escaped = TWO ? (await Bun.file(ESCAPE_FILE).json()).nets as Record<string, any> : {}
for (const [net, r] of Object.entries(escaped)) { for (const g of r.segs) for (let i = 0; i + 1 < g.pts.length; i++) obstacle({ pts: [g.pts[i], g.pts[i + 1]], r: (g.w ?? W) / 2, layers: [g.layer], net, kind: "trace" } as any)
  for (const v of r.vias) obstacle({ pts: [{ x: v.x, y: v.y }], r: v.d / 2, layers: ["top", "bottom"], net, kind: "via" } as any) }
// ---------- connections: every signal net with all its terminals ----------
function point(t: any) { const it = items.find((i) => i.ref === t.ref && i.layers.length)
  // a ball that already has its via in the pad (the planner drills one for every ball the DDR copper boxes in) is reachable on both layers
  const via = t.kind === "ball" && (plan.vias as any[]).some((v) => v.ball === t.ref && Math.hypot(v.x - t.x, v.y - t.y) < 1e-3)
  return { x: r4(t.x), y: r4(t.y), ...(via ? { layers: LAYERS } : { layer: t.layer }), pointId: t.ref, port_selector: t.ref, ...(it ? {} : {}) } }
const boxedNet = (n: any) => n.terms.some((t: any) => t.kind === "ball" && (plan.vias as any[]).some((v) => v.ball === t.ref && Math.hypot(v.x - t.x, v.y - t.y) < 1e-3))
// the escape cluster: the boxed-in nets and every net that shares a two-pin part (strap, pull-up) with one of them, since
// those parts sit in the same corner and the outer-layer pass cannot reach them across the escape copper
const partOf = (ref: string) => ref.split(".")[0], twoPin = (part: string) => /^[RCL]_/.test(part)
const boxedParts = new Set((plan.nets as any[]).filter(boxedNet).flatMap((n) => n.terms.map((t: any) => partOf(t.ref)).filter(twoPin)))
const escapeNet = (n: any) => boxedNet(n) || n.terms.some((t: any) => boxedParts.has(partOf(t.ref)))
const passNets = (plan.nets as any[]).filter((n) => PASS === "escape" ? escapeNet(n) : TWO ? !escapeNet(n) && !escaped[n.name] : true)
const connections = passNets.map((n) => ({ name: n.name, pointsToConnect: n.terms.map(point) }))
const srj = { layerCount: LAYERS.length, minTraceWidth: W, nominalTraceWidth: W, minViaHoleDiameter: 0.1, minViaPadDiameter: 0.3, defaultObstacleMargin: CLR, minTraceToPadEdgeClearance: CLR, minBoardEdgeClearance: 0.2,
  minViaHoleEdgeToViaHoleEdgeClearance: 0.2, minViaEdgeToPadEdgeClearance: CLR, allowViaInPad: true, obstacles, connections, bounds: { minX: E.x0, maxX: E.x1, minY: E.y0, maxY: E.y1 },
  outline: [{ x: E.x0, y: E.y0 }, { x: E.x1, y: E.y0 }, { x: E.x1, y: E.y1 }, { x: E.x0, y: E.y1 }] }
await Bun.write(process.env.SRJ_OUT ?? dir + "/autoroute.srj.json", JSON.stringify(srj))
console.log(`SRJ: ${obstacles.length} obstacles, ${connections.length} connections, ${connections.reduce((s, c) => s + c.pointsToConnect.length, 0)} terminals; pipeline ${PIPELINE}`)
if (process.env.SRJ_ONLY) process.exit(0)
// ---------- solve ----------
// FROM_TRACES=1: convert the saved solver output (autoroute.traces.json) again without solving
const solver: any = process.env.FROM_TRACES ? { solved: true, failed: false, getOutputSimplifiedPcbTraces: () => JSON.parse(require("node:fs").readFileSync(dir + "/autoroute.traces.json", "utf8")) } : new mod[PIPELINE](srj, process.env.EFFORT ? { effort: +process.env.EFFORT } : undefined)
const t0 = performance.now(); let last = 0
// VIA_AUDIT=1 (diagnostic): at each stage change, count the previous stage's vias that sit inside a layer-4 keep-out
let auditPrev: any = null
const keepRects = obstacles.filter((o: any) => o.layers.length === 1 && o.layers[0] === "inner1" && o.width * o.height > 20)
const auditVias = (out: any): number => { let n = 0; const seen = new Set<string>()
  const hit = (x: number, y: number) => { const k = `${x.toFixed(3)},${y.toFixed(3)}`; if (seen.has(k)) return; seen.add(k); if (keepRects.some((o: any) => Math.abs(x - o.center.x) < o.width / 2 && Math.abs(y - o.center.y) < o.height / 2)) n++ }
  for (const r of Array.isArray(out) ? out : []) { for (const v of r?.vias ?? []) hit(v.x, v.y)
    const pts = r?.route ?? []; for (let i = 0; i < pts.length; i++) { const p = pts[i]; if (p.route_type === "via") hit(p.x, p.y); else if (i && pts[i - 1].z !== undefined && p.z !== undefined && pts[i - 1].z !== p.z) hit(p.x, p.y) } }
  return n }
while (!solver.solved && !solver.failed) { solver.step()
  if (process.env.VIA_AUDIT && solver.activeSubSolver !== auditPrev) { if (auditPrev) { let out: any; try { out = auditPrev.getOutput?.() } catch { out = undefined }
      if (out === undefined && auditPrev.routes) out = auditPrev.routes
      console.log(`  [via-audit] ${auditPrev.constructor?.name}: ${Array.isArray(out) ? auditVias(out) + " vias inside layer-4 keep-outs (" + out.length + " routes)" : "output not inspectable"}`) }
    auditPrev = solver.activeSubSolver }
  // DUMP_STAGE=<solver class>: save that stage's constructor input (a stand-alone repro of the stage) and stop
  if (process.env.DUMP_STAGE && solver.activeSubSolver?.constructor?.name === process.env.DUMP_STAGE) { await Bun.write(process.env.DUMP_OUT ?? dir + "/stage-input.json", JSON.stringify(solver.activeSubSolver.getConstructorParams())); console.log("dumped " + process.env.DUMP_STAGE); process.exit(0) }
  const t = performance.now(); if (t - last > 30000) { last = t; console.log(`  ${((t - t0) / 1e3).toFixed(0)}s, iteration ${solver.iterations}, stage ${solver.activeSubSolver?.constructor?.name ?? solver.currentPipelineStepIndex ?? ""}${solver.activeSubSolver?.activeSubSolver ? " / " + solver.activeSubSolver.activeSubSolver.constructor?.name : ""}, rss ${(process.memoryUsage().rss / 2 ** 30).toFixed(1)} GB`) } }
console.log(`${solver.solved ? "solved" : "FAILED: " + solver.error} in ${((performance.now() - t0) / 1e3).toFixed(0)}s`)
if (!solver.solved) { // FAIL_DUMP=<file>: save the high-density node that failed (its port points and bounds) for diagnosis
  if (process.env.FAIL_DUMP) { const hd = solver.highDensityRouteSolver; const id = /Failed to solve 1 nodes, ([^.]+)\./.exec(solver.error ?? "")?.[1]; const all = [hd?.activeNode, ...(hd?.unsolvedNodePortPoints ?? []), ...(solver.highDensityNodePortPoints ?? [])].filter(Boolean); const node = all.find((n: any) => n.capacityMeshNodeId === id) ?? hd?.activeNode
    if (node) { await Bun.write(process.env.FAIL_DUMP, JSON.stringify(node)); console.log("failed node saved to " + process.env.FAIL_DUMP) }
    console.log("high-density stats: " + JSON.stringify(hd?.stats))
    // port-point pathing: the most re-ripped routes are the contested ones
    const pps = solver.portPointPathingSolver
    let pp: any = pps?.tinyPipelineSolver ?? pps?.primaryTinyPipelineSolver ?? solver.activeSubSolver ?? pps
    for (const f of pps?.failedSubSolvers ?? []) if (f?.routeAttemptCountByRouteId) pp = f
    for (let d = 0; pp && !pp.routeAttemptCountByRouteId && d < 6; d++) pp = pp.activeSubSolver ?? pp.failedSubSolvers?.at?.(-1) ?? pp.solver ?? Object.values(pp).find((v: any) => v && typeof v === "object" && "routeAttemptCountByRouteId" in v)
    if (!pp?.routeAttemptCountByRouteId) console.log("pathing solver fields: " + Object.keys(pp ?? {}).join(",") + " / stats " + JSON.stringify(pps?.stats))
    if (pp?.routeAttemptCountByRouteId) { const meta = pp.problem?.routeMetadata ?? []
      const top = [...pp.routeAttemptCountByRouteId].map((n: number, i: number) => [n, meta[i]?.connectionName ?? meta[i]?.name ?? i]).sort((a: any, b: any) => b[0] - a[0]).slice(0, 15)
      console.log("most re-ripped routes: " + JSON.stringify(top)); console.log("unrouted: " + JSON.stringify((pp.state?.unroutedRoutes ?? []).map((i: number) => meta[i]?.connectionName ?? i))) } }
  process.exit(1) }
// ---------- output: routes.json ----------
const traces: any[] = solver.getOutputSimplifiedPcbTraces()
if (!process.env.FROM_TRACES) await Bun.write(process.env.TRACES_OUT ?? dir + "/autoroute.traces.json", JSON.stringify(traces)) // the solver's raw output
const netOf = (name: string) => routedNets.has(name) ? name : [...routedNets].filter((n) => name.startsWith(n)).sort((a, b) => b.length - a.length)[0]
const out: any = { solved: true, router: `@tscircuit/capacity-autorouter ${PIPELINE}`, nets: {} }
for (const t of traces) { const net = netOf(t.connection_name); if (!net) throw Error("trace for an unknown connection " + t.connection_name)
  const r = (out.nets[net] ??= { terms: (plan.nets as any[]).find((n) => n.name === net).terms.map((q: any) => q.ref), segs: [], vias: [], length: 0 })
  let cur: Pt[] = [], layer = "", w = W
  const flush = () => { if (cur.length > 1) r.segs.push({ layer, w, pts: cur }); cur = [] }
  for (const p of t.route) { if (p.route_type === "via") { flush(); r.vias.push({ x: r4(p.x), y: r4(p.y), d: p.via_diameter ?? 0.3, hole: p.via_hole_diameter ?? 0.1 }); layer = ""; continue }
    if (p.route_type !== "wire") throw Error(`unexpected route element ${p.route_type} in ${t.connection_name}`)
    if ((p.width ?? W) < W - 1e-6) throw Error(`trace width ${p.width} below the minimum in ${t.connection_name}`)
    if (Math.abs((p.width ?? W) - w) > 1e-6) { const last = cur.at(-1); flush(); if (last) cur.push(last); w = p.width ?? W } // the solver may widen a trace where there is room
    const bl = toBoard[p.layer]; if (!bl) throw Error(`trace on layer ${p.layer}`)
    if (bl !== layer) { flush(); layer = bl } cur.push({ x: r4(p.x), y: r4(p.y) }) }
  flush() }
for (const r of Object.values(out.nets) as any[]) r.length = +r.segs.reduce((s: number, g: any) => s + g.pts.slice(1).reduce((a: number, p: Pt, i: number) => a + Math.hypot(p.x - g.pts[i].x, p.y - g.pts[i].y), 0), 0).toFixed(2)
const missing = passNets.map((n) => n.name).filter((n) => !out.nets[n]); if (missing.length) { console.log("!! no trace for", missing.join(" ")); process.exit(1) }
if (TWO) { Object.assign(out.nets, escaped); out.router += " (escape pass + outer-layer pass)" }
await Bun.write(process.env.OUT ?? (PASS === "escape" ? ESCAPE_FILE : dir + "/routes.json"), JSON.stringify(out))
console.log(`routes.json: ${Object.keys(out.nets).length} nets, ${traces.length} traces, ${(Object.values(out.nets) as any[]).reduce((s, r) => s + r.vias.length, 0)} vias`)
