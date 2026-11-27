// Writes the board in the routing-playbook router's input format (pb/route.ts, from the RK3566 module):
//   pb/pads.json   board box, holes, every copper pad (part pads, processor/memory balls, connector pins)
//   pb/fixed.json  copper that is already there: the DDR block, the planner's traces, every via
//   pb/nets.json   which nets the router routes (plan.json nets + small rails) and which are plane nets
// Pads of nets the planner already finished keep their net only for clearance: the router does not route them.
import type { Item } from "../geom"
const root = import.meta.dir + "/.."
const plan = await Bun.file(root + "/plan.json").json(), items: Item[] = (await Bun.file(root + "/plan-items.json").json()).items
const E = plan.edge
// TI Table 7-68/7-69: other signals keep four trace widths (0.31 mm) from the DDR copper outside the processor's ball
// field; the router keeps 0.1 mm from everything, so DDR copper there is handed over widened by the difference
const DDR_EXTRA = 0.31 - 0.1, inCpu = (x: number, y: number) => x > -52.4 && x < -37.2 && y > 7.55 && y < 22.75
// plane nets: each pad only needs a via to its plane (planes.ts STACK=pb); VDDS_RTC is a small rail routed as a trace
const planes = (plan.planeNets as string[]).filter((n) => n !== "VDDS_RTC").concat(plan.innerNets)
const routed = [...(plan.nets as any[]).map((n) => n.name), "VDDS_RTC"]
const r4 = (v: number) => +v.toFixed(4)
const pads: any[] = []
for (const it of items) {
  if ((it.kind !== "pad" && it.kind !== "ball") || !it.layers.length) continue
  const [ref, name] = (it as any).ref.split(".")
  if (it.pts.length === 1) { pads.push({ ref, names: [name], net: it.net, layer: it.layers[0], shape: "circle", x: r4(it.pts[0].x), y: r4(it.pts[0].y), w: r4(2 * it.r), h: r4(2 * it.r) }); continue }
  // rectangles (a few are rotated: their axis-aligned bounding box, which only adds clearance)
  const xs = it.pts.map((p) => p.x), ys = it.pts.map((p) => p.y), x0 = Math.min(...xs) - it.r, x1 = Math.max(...xs) + it.r, y0 = Math.min(...ys) - it.r, y1 = Math.max(...ys) + it.r
  pads.push({ ref, names: [name], net: it.net, layer: it.layers[0], shape: "rect", x: r4((x0 + x1) / 2), y: r4((y0 + y1) / 2), w: r4(x1 - x0), h: r4(y1 - y0) })
}
const traces: any[] = [], vias: any[] = []
for (const it of items) {
  if ((it.kind === "ddr" || it.kind === "trace") && it.pts.length === 2 && it.layers.length === 1) {
    const extra = it.kind === "ddr" && !it.pts.every((p) => inCpu(p.x, p.y)) ? DDR_EXTRA : 0
    traces.push({ net: it.net, layer: it.layers[0], w: r4(2 * (it.r + extra)), pts: it.pts.map((p) => ({ x: r4(p.x), y: r4(p.y) })) })
  } else if (it.kind === "ddrvia") vias.push({ net: it.net, x: r4(it.pts[0].x), y: r4(it.pts[0].y), d: r4(2 * it.r + (inCpu(it.pts[0].x, it.pts[0].y) ? 0 : 2 * DDR_EXTRA)) })
}
for (const v of plan.vias) vias.push({ net: v.net, x: r4(v.x), y: r4(v.y), d: v.d })
for (const g of plan.ddrInner ?? []) traces.push({ net: g.net, layer: "inner3", w: 0.102 + 2 * DDR_EXTRA, pts: [g.a, g.b] })
await Bun.write(import.meta.dir + "/pads.json", JSON.stringify({ board: { x0: E.x0, y0: E.y0, x1: E.x1, y1: E.y1 }, holes: plan.holes.map((h: any) => ({ x: h.x, y: h.y, r: h.d / 2 })), pads, footprintVias: [] }))
await Bun.write(import.meta.dir + "/fixed.json", JSON.stringify({ traces, vias }))
await Bun.write(import.meta.dir + "/nets.json", JSON.stringify({ routed, planes }))
console.log(`pads ${pads.length}, fixed traces ${traces.length}, fixed vias ${vias.length}, routed nets ${routed.length}, plane nets ${planes.length}`)
