// Whole-board check of module/dist/module.circuit.json, from the rendered geometry (not the planner's model):
// 1. every pad sits where the planner assumed, 2. copper of different nets keeps its clearance on every layer,
// 3. every net is one connected piece (outer copper, vias, inner pours), 4. nothing is left unconnected.
import { Board, disc, seg, rect, gap, type Item, type Layer } from "./geom"
const dir = import.meta.dir
const cj: any[] = await Bun.file(dir + "/dist/module.circuit.json").json(), plan = await Bun.file(dir + "/plan.json").json()
const routes = await Bun.file(dir + "/routes.json").json(), names: Record<string, string> = await Bun.file("/home/user/ddr-route/net-names.json").json()
const E = plan.edge, CX = (E.x0 + E.x1) / 2, CY = (E.y0 + E.y1) / 2, MIN = +(process.env.MIN ?? 0.09)
const out: string[] = []; let fail = 0; const bad = (m: string) => { out.push("FAIL  " + m); fail++ }, ok = (m: string) => out.push("PASS  " + m)
// ---------- nets of pads ----------
const sc = new Map(cj.filter((e) => e.type === "source_component").map((e) => [e.source_component_id, e.name])), pc = new Map(cj.filter((e) => e.type === "pcb_component").map((e) => [e.pcb_component_id, sc.get(e.source_component_id)]))
const sp = new Map(cj.filter((e) => e.type === "source_port").map((e) => [e.source_port_id, e])), pp = new Map(cj.filter((e) => e.type === "pcb_port").map((e) => [e.pcb_port_id, sp.get(e.source_port_id)]))
const padNet = new Map<string, string>() // "REF.pin" -> net
for (const [k, n] of Object.entries(plan.ballNet as Record<string, string>)) padNet.set(k, n)
for (const p of plan.parts) for (const [pin, n] of Object.entries(p.nets as Record<string, string>)) padNet.set(`${p.name}.${pin}`, n)
for (const p of plan.pins) if (p.role !== "SIG") padNet.set(`${p.conn}.${p.pin}`, p.role)
for (const [n, r] of Object.entries(routes.nets) as any) padNet.set(`${r.conn}.${r.pin}`, n)
const B = new Board(), LAY = ["top", "inner1", "inner2", "inner3", "inner4", "bottom"]
type It = Item & { id: number }; const all: It[] = []; const add = (s: any, layers: string[], net: string, kind: string, ref = "") => { const it = B.add({ ...s, layers: layers as Layer[], net, kind, ref }) as It; it.id = all.length; all.push(it); return it }
// pads
const labelOf = (port: any) => { const hints: string[] = port?.port_hints ?? []; return hints.find((h) => /^[A-Z]{1,2}\d+$/.test(h)) ?? hints.find((h) => /^pin\d+$/.test(h)) ?? port?.name }
let padCount = 0, open = 0
for (const p of cj.filter((e) => e.type === "pcb_smtpad")) { const ref = pc.get(p.pcb_component_id), port = pp.get(p.pcb_port_id), isBga = ref === "U1" || ref === "U_DDR", key = `${ref}.${isBga ? labelOf(port) : (port?.port_hints ?? []).find((h: string) => /^pin\d+$/.test(h)) ?? port?.name}`
  const net = padNet.get(key) ?? `open:${key}`; if (!padNet.has(key)) open++
  const x = p.x + CX, y = p.y + CY, s = p.shape === "circle" ? disc(x, y, p.radius) : rect(x, y, p.width, p.height, p.ccw_rotation ?? 0)
  add(s, [p.layer], net, "pad", key); padCount++ }
// planner's assumption about pad positions
{ let worst = 0; const items: Item[] = (await Bun.file(dir + "/plan-items.json").json()).items
  for (const it of all) { const m = items.find((q) => q.ref === it.ref && q.layers.length && (q.kind === "pad" || q.kind === "ball")); if (!m) continue; const c = (s: any) => ({ x: s.pts.reduce((a: number, p: any) => a + p.x, 0) / s.pts.length, y: s.pts.reduce((a: number, p: any) => a + p.y, 0) / s.pts.length }), a = c(it), b = c(m); worst = Math.max(worst, Math.hypot(a.x - b.x, a.y - b.y)); if (m.layers[0] !== it.layers[0]) bad(`pad ${it.ref} on ${it.layers[0]}, planned ${m.layers[0]}`) }
  ;(worst < 0.002 ? ok : bad)(`rendered pads match the planned positions (${padCount} pads, worst offset ${worst.toFixed(4)} mm; ${open} pads without a net)`) }
// traces and vias
const ddrNet = (t: any) => { const st = cj.find((e) => e.type === "source_trace" && e.source_trace_id === t.source_trace_id); return st?.name ?? st?.display_name }
for (const t of cj.filter((e) => e.type === "pcb_trace")) { const net = t.net_name ?? ddrNet(t) ?? "?:" + t.pcb_trace_id
  for (let i = 0; i < t.route.length; i++) { const a = t.route[i], b = t.route[i + 1]
    if (a.route_type === "via") { add(disc(a.x + CX, a.y + CY, (a.outer_diameter ?? a.via_diameter ?? 0.3) / 2), LAY, net, "via"); continue }
    if (b && b.route_type === "wire" && b.layer === a.layer) add(seg({ x: a.x + CX, y: a.y + CY }, { x: b.x + CX, y: b.y + CY }, a.width), [a.layer], net, "trace") } }
for (const v of cj.filter((e) => e.type === "pcb_via")) { let net = v.net_name
  if (!net) { const near = all.find((i) => i.kind === "via" && Math.hypot(i.pts[0].x - v.x - CX, i.pts[0].y - v.y - CY) < 0.01); if (near) continue; net = "?:" + v.pcb_via_id }
  add(disc(v.x + CX, v.y + CY, v.outer_diameter / 2), LAY, net, "via") }
{ // nothing required may be missing, and no ball that needs a part may be left as a one-pad net
  const names = new Set([...pc.values()]), miss = (plan.required ?? []).filter((n: string) => !names.has(n)).concat(["C_VREF_CPU"].filter((n) => !names.has(n)))
  ;(miss.length ? bad : ok)(`required parts present (${(plan.required ?? []).length + 1} checked)${miss.length ? ": MISSING " + miss.join(" ") : ""}`)
  const cnt = new Map<string, number>(); for (const it of all) if (it.kind === "pad") cnt.set(it.net, (cnt.get(it.net) ?? 0) + 1)
  const lone = [...cnt].filter(([n, k]) => k === 1 && !n.startsWith("open:") && !n.startsWith("NC:")).map(([n]) => n)
  ;(lone.length ? bad : ok)(`no net ends at a single pad: ${lone.length ? lone.join(" ") : "none"}`) }
// ---------- clearance ----------
{ let min = 9, n = 0; const worst: string[] = []
  for (const a of all) for (const b of B.near(a, 0.2) as It[]) { if (b.id <= a.id || a.net === b.net || !a.layers.some((l) => b.layers.includes(l))) continue
    const g = gap(a, b); if (g < min) min = g; if (g < MIN - 1e-6) { n++; if (worst.length < 12) worst.push(`${g.toFixed(3)} ${a.net}(${a.kind}) / ${b.net}(${b.kind}) at (${a.pts[0].x.toFixed(2)}, ${a.pts[0].y.toFixed(2)})`) } }
  ;(n ? bad : ok)(`outer and via copper of different nets >= ${MIN} mm apart: ${n} below, minimum ${min.toFixed(3)} mm`); out.push(...worst.map((w) => "        " + w)) }
{ let min = 9, where = ""; const pads = all.filter((i) => i.kind === "pad") // assembly: pads of different parts on one side
  for (const a of pads) for (const b of B.near(a, 0.3) as It[]) { if (b.kind !== "pad" || b.id <= a.id || a.layers[0] !== b.layers[0] || a.ref!.split(".")[0] === b.ref!.split(".")[0]) continue; const g = gap(a, b); if (g < min) { min = g; where = `${a.ref} / ${b.ref}` } }
  ;(min < 0.18 - 1e-6 ? bad : ok)(`pads of different parts on the same side >= 0.18 mm apart (JLCPCB 0402-0402 spacing; 0.15 mm pad rule): minimum ${min.toFixed(3)} mm (${where})`) }
{ const hs = all.filter((i) => i.kind === "via"); let min = 9, n = 0, where = "" // drill hits: none doubled, none closer than 0.2 mm wall to wall
  for (const a of hs) for (const b of B.near(a, 0.3) as It[]) { if (b.kind !== "via" || b.id <= a.id) continue; const dd = Math.hypot(a.pts[0].x - b.pts[0].x, a.pts[0].y - b.pts[0].y) - 0.1; if (dd < min) { min = dd; where = `(${(a.pts[0].x - CX).toFixed(2)}, ${(a.pts[0].y - CY).toFixed(2)}) ${a.net}/${b.net}` } if (dd < 0.2 - 1e-6) n++ }
  ;(n ? bad : ok)(`drill holes >= 0.20 mm wall to wall: ${n} pairs closer, minimum ${min.toFixed(3)} mm at ${where} (${hs.length} holes)`) }
{ const vs = cj.filter((e) => e.type === "pcb_via"), part = vs.filter((v) => (v.layers ?? []).length !== 6 || v.from_layer !== "top" || v.to_layer !== "bottom").length, inTrace = cj.filter((e) => e.type === "pcb_trace").flatMap((t) => t.route).filter((p: any) => p.route_type === "via").length
  ;(part || inTrace ? bad : ok)(`through vias only (no blind or buried vias): ${vs.length} vias, ${part + inTrace} that do not span top to bottom`) }
{ let min = 9, n = 0, where = "" // JLCPCB: via hole to other copper >= 0.2 mm (holes are 0.1 mm)
  for (const v of all.filter((i) => i.kind === "via")) { const hole = disc(v.pts[0].x, v.pts[0].y, 0.05); for (const o of B.near(hole, 0.25) as It[]) { if (o.net === v.net) continue; const g = gap(hole, o); if (g < min) { min = g; where = `(${(v.pts[0].x - CX).toFixed(2)}, ${(v.pts[0].y - CY).toFixed(2)}) ${v.net} / ${o.net} ${o.kind}` } if (g < 0.2 - 1e-6) n++ } }
  ;(n ? bad : ok)(`via hole wall to copper of other nets >= 0.20 mm (outer layers and via pads): ${n} below, minimum ${min.toFixed(3)} mm at ${where}`) }
{ let min = 9, where = "" // JLCPCB assembly: other parts on the BGA side stay 1 mm from the BGA bodies
  const bga = [rect(-44.8, 15.15, 15, 15), rect(-70, 15.15, 14, 9)]
  for (const a of all.filter((i) => i.kind === "pad" && i.layers[0] === "top" && !/^U(1|_DDR)\./.test(i.ref!))) for (const b of bga) { const g = gap(a, b); if (g < min) { min = g; where = a.ref! } }
  ;(min < 1.0 - 1e-6 ? bad : ok)(`top-side parts >= 1.0 mm from the BGA bodies: minimum ${min.toFixed(2)} mm (${where})`) }
// ---------- pours ----------
const pours = cj.filter((e) => e.type === "pcb_copper_pour").map((p) => ({ layer: p.layer, net: p.net_name, outer: p.brep_shape.outer_ring.vertices.map((v: any) => ({ x: v.x + CX, y: v.y + CY })), holes: p.brep_shape.inner_rings.map((r: any) => r.vertices.map((v: any) => ({ x: v.x + CX, y: v.y + CY }))) }))
const pip = (q: any, poly: any[]) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) if ((poly[i].y > q.y) !== (poly[j].y > q.y) && q.x < ((poly[j].x - poly[i].x) * (q.y - poly[i].y)) / (poly[j].y - poly[i].y) + poly[i].x) c = !c; return c }
const pb = pours.map((p) => ({ x0: Math.min(...p.outer.map((v: any) => v.x)), x1: Math.max(...p.outer.map((v: any) => v.x)), y0: Math.min(...p.outer.map((v: any) => v.y)), y1: Math.max(...p.outer.map((v: any) => v.y)) }))
const inPour = (q: any, k: number) => q.x > pb[k].x0 && q.x < pb[k].x1 && q.y > pb[k].y0 && q.y < pb[k].y1 && pip(q, pours[k].outer) && !pours[k].holes.some((h: any[]) => pip(q, h))
{ let n = 0; const ex: string[] = []
  for (const v of all.filter((i) => i.kind === "via")) for (let k = 0; k < pours.length; k++) { if (pours[k].net === v.net) continue; const c = v.pts[0], R = v.r + 0.1
    if (c.x < pb[k].x0 - R || c.x > pb[k].x1 + R || c.y < pb[k].y0 - R || c.y > pb[k].y1 + R) continue
    for (let a = 0; a < 16; a++) if (inPour({ x: c.x + R * Math.cos(a * Math.PI / 8), y: c.y + R * Math.sin(a * Math.PI / 8) }, k)) { n++; if (ex.length < 6) ex.push(`${v.net} via at (${c.x.toFixed(2)}, ${c.y.toFixed(2)}) vs ${pours[k].net} on ${pours[k].layer}`); break } }
  ;(n ? bad : ok)(`inner copper keeps >= 0.10 mm from the via pads of other nets: ${n} violations (${pours.length} copper shapes)`); out.push(...ex.map((w) => "        " + w)) }
{ let n = 0; const ex: string[] = [] // inner-layer signal traces against the plane copper
  for (const t of all.filter((i) => i.kind === "trace" && i.layers[0].startsWith("inner"))) for (let k = 0; k < pours.length; k++) { if (pours[k].layer !== t.layers[0] || pours[k].net === t.net) continue
    const [a, b] = t.pts, L = Math.hypot(b.x - a.x, b.y - a.y) || 1, ux = (b.x - a.x) / L, uy = (b.y - a.y) / L, R = t.r + 0.1; let hit = false
    for (let s = 0; s <= L && !hit; s += 0.05) for (const sg of [-1, 1]) if (inPour({ x: a.x + ux * s - uy * R * sg, y: a.y + uy * s + ux * R * sg }, k)) hit = true
    if (hit) { n++; if (ex.length < 6) ex.push(`${t.net} at (${a.x.toFixed(2)}, ${a.y.toFixed(2)}) vs ${pours[k].net} on ${pours[k].layer}`) } }
  ;(n ? bad : ok)(`inner-layer signal traces keep >= 0.10 mm from plane copper: ${n} violations`); out.push(...ex.map((w) => "        " + w)) }
// ---------- connectivity ----------
{ const par = new Int32Array(all.length + pours.length).map((_, i) => i), find = (a: number): number => { while (par[a] !== a) { par[a] = par[par[a]]; a = par[a] } return a }, uni = (a: number, b: number) => { par[find(a)] = find(b) }
  let shorts = 0
  for (const a of all) for (const b of B.near(a, 0.01) as It[]) { if (b.id <= a.id || !a.layers.some((l) => b.layers.includes(l)) || gap(a, b) > 1e-6) continue; if (a.net === b.net) uni(a.id, b.id); else shorts++ }
  for (const v of all.filter((i) => i.kind === "via")) for (let k = 0; k < pours.length; k++) if (pours[k].net === v.net && inPour(v.pts[0], k)) uni(v.id, all.length + k)
  const byNet = new Map<string, Set<number>>(); for (const it of all) { if (!byNet.has(it.net)) byNet.set(it.net, new Set()); byNet.get(it.net)!.add(find(it.id)) }
  const split = [...byNet].filter(([n, s]) => s.size > 1 && !n.startsWith("open:") && !n.startsWith("NC:")), single = [...byNet].filter(([n]) => !n.startsWith("open:")).length
  ;(shorts ? bad : ok)(`no copper of different nets touches (${shorts} contacts)`)
  ;(split.length ? bad : ok)(`every net is one connected piece: ${single - split.length}/${single} nets${split.length ? "; split: " + split.slice(0, 14).map(([n, s]) => `${n}(${s.size})`).join(" ") : ""}`)
  const want = new Set([...Object.values(plan.ballNet as Record<string, string>)]); const missing = [...want].filter((n) => !byNet.has(n)); if (missing.length) bad("nets without copper: " + missing.join(" "))
  // nets that must reach the connector
  const noPin = (plan.signals as any[]).filter((s) => !routes.nets[s.name]).map((s) => s.name); (noPin.length ? bad : ok)(`all ${plan.signals.length} handheld signals reach a connector pin${noPin.length ? " - missing: " + noPin.join(" ") : ""}`) }
console.log(out.join("\n")); console.log(fail ? `MODULE RESULT: FAIL (${fail})` : "MODULE RESULT: PASS")
