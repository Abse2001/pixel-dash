// Assembles the module: tscircuit renders the board, the two BGAs, the fixed DDR traces and every placed part;
// the planner's vias and local traces, the routed handheld signals and the inner-layer copper are then added to the
// circuit JSON as plain PCB elements. Output: module/dist/module.circuit.json
import { Circuit } from "@tscircuit/core"
import { AM3354BZCZD80 } from "../am3354/imports/AM3354BZCZD80"
import { MT41K512M16VRP_107_IT_P } from "../am3354/imports/MT41K512M16VRP_107_IT_P"
import { TMK063ABJ104KP_F } from "../am3354/imports/TMK063ABJ104KP_F"
import { RC0201FR_07240RL } from "../am3354/imports/RC0201FR_07240RL"
import { A_0402WGF499JTCE } from "../am3354/imports/A_0402WGF499JTCE"
import { CL05B104KO5NNNC } from "../imports/CL05B104KO5NNNC"
import { CL10A106KP8NNNC } from "../imports/CL10A106KP8NNNC"
import { A_0402CG150F500NT } from "../imports/A_0402CG150F500NT"
import { A_0402WGF1001TCE } from "../imports/A_0402WGF1001TCE"
import { S3B24_000000F1210F30 } from "../imports/S3B24_000000F1210F30"
import { CL05A105KA5NQNC } from "./imports/CL05A105KA5NQNC"
import { DF40C_100DS_0_4V_51_ } from "./imports/DF40C_100DS_0_4V_51_"
import plan from "./plan.json"
const COMP: Record<string, any> = { TMK063ABJ104KP_F, RC0201FR_07240RL, A_0402WGF499JTCE, CL05B104KO5NNNC, CL10A106KP8NNNC, A_0402CG150F500NT, A_0402WGF1001TCE, S3B24_000000F1210F30, CL05A105KA5NQNC, DF40C_100DS_0_4V_51_ }
const PART: Record<string, string> = { C100N_0201: "TMK063ABJ104KP_F", C100N_0402: "CL05B104KO5NNNC", C1U_0402: "CL05A105KA5NQNC", C10U_0603: "CL10A106KP8NNNC", C15P_0402: "A_0402CG150F500NT", R240_0201: "RC0201FR_07240RL", R49R9_0402: "A_0402WGF499JTCE", R1K_0402: "A_0402WGF1001TCE", XTAL_24M: "S3B24_000000F1210F30", DF40_100: "DF40C_100DS_0_4V_51_" }
const dir = import.meta.dir, E = plan.edge, CX = (E.x0 + E.x1) / 2, CY = (E.y0 + E.y1) / 2
const routes = (await Bun.file(dir + "/routes.json").exists()) ? await Bun.file(dir + "/routes.json").json() : { nets: {} }
const pours: any[] = (await Bun.file(dir + "/pours.json").exists()) ? await Bun.file(dir + "/pours.json").json() : []
const t0 = performance.now(), circuit = new Circuit()
circuit.add(
  <board width={E.x1 - E.x0} height={E.y1 - E.y0} layers={6} thickness={1.0} routingDisabled schAutoLayoutEnabled={false} minTraceWidth={0.09} minTraceToPadEdgeClearance={0.1} minViaHoleDiameter={0.1} minViaPadDiameter={0.25} isViaInPadAllowed={true} title="AM3354 DDR3L compute module">
    <group pcbX={-CX} pcbY={-CY}>
      <AM3354BZCZD80 name="U1" pcbX={-44.8} pcbY={15.15} />
      <MT41K512M16VRP_107_IT_P name="U_DDR" pcbX={-70} pcbY={15.15} pcbRotation={270} />
      {(plan.parts as any[]).map((p) => { const C = COMP[PART[p.part]]; return <C key={p.name} name={p.name} pcbX={p.x} pcbY={p.y} pcbRotation={p.rot} layer={p.layer} {...(p.part === "XTAL_24M" ? { loadCapacitance: "12pF" } : {})} /> })}
      {(plan.holes as any[]).map((h, i) => <hole key={i} name={"H" + (i + 1)} pcbX={h.x} pcbY={h.y} diameter={h.d} />)}
    </group>
  </board>,
)
await circuit.renderUntilSettled()
const cj: any[] = circuit.getCircuitJson().filter((e: any) => e.type !== "pcb_silkscreen_text" || ["U1", "U_DDR"].includes(e.text)) // 0402 designators do not fit; the assembly data carries them
const errs = cj.filter((e) => e.type.includes("error")); const kinds: Record<string, number> = {}; for (const e of errs) kinds[e.type] = (kinds[e.type] ?? 0) + 1
// ---------- add the planned copper ----------
const ALL = ["top", "inner1", "inner2", "inner3", "inner4", "bottom"]; let n = 0
const via = (v: any, net: string) => cj.push({ type: "pcb_via", pcb_via_id: `m_via_${n++}`, x: v.x - CX, y: v.y - CY, hole_diameter: 0.1, outer_diameter: v.d, layers: ALL, from_layer: "top", to_layer: "bottom", net_name: net })
const trace = (pts: any[], layer: string, w: number, net: string) => cj.push({ type: "pcb_trace", pcb_trace_id: `m_trace_${n++}`, net_name: net, route: pts.map((p) => ({ route_type: "wire", x: p.x - CX, y: p.y - CY, width: w, layer })) })
// the DDR block exactly as routed and verified (ddr-route/out/module6)
{ const ddr = await Bun.file(process.env.DDR ?? "/home/user/ddr-route/out/module9/ddr-cpu-ram.routed.json").json(), names: Record<string, string> = await Bun.file("/home/user/ddr-route/net-names.json").json()
  for (const t of ddr.traces) { if (!t.pcb_trace_id.startsWith("ddr_lane_")) continue; const net = names[t.connection_name]; let cur: any[] = [], layer = t.route[0].layer
    const flush = () => { if (cur.length > 1) trace(cur, layer, 0.102, net); cur = [] }
    for (const p of t.route) { if (p.route_type === "via") { cur.push(p); flush(); via({ x: p.x, y: p.y, d: p.via_diameter ?? 0.3, hole: p.via_hole_diameter ?? 0.15 }, net); layer = p.to_layer === layer ? p.from_layer : p.to_layer; cur = [p]; continue }
      if (p.layer !== layer) { flush(); layer = p.layer } cur.push(p) }
    flush() } }
for (const v of plan.vias as any[]) via(v, v.net)
for (const p of plan.paths as any[]) trace(p.pts, p.layer, p.w, p.net)
for (const [name, r] of Object.entries(routes.nets) as any) { for (const s of r.segs) trace(s.pts, s.layer, 0.1, name); for (const v of r.vias) via(v, name) }
// big shapes first: a Gerber consumer draws each shape dark and then clears its holes, which would wipe a small shape drawn earlier inside such a hole
for (const p of [...pours].sort((a, b) => b.area - a.area)) cj.push({ type: "pcb_copper_pour", pcb_copper_pour_id: `m_pour_${n++}`, shape: "brep", layer: p.layer, net_name: p.net, covered_with_solder_mask: true,
  brep_shape: { outer_ring: { vertices: p.outer.map((q: any) => ({ x: q.x - CX, y: q.y - CY })) }, inner_rings: p.holes.map((h: any[]) => ({ vertices: h.map((q) => ({ x: q.x - CX, y: q.y - CY })) })) } })
await Bun.write(dir + "/dist/module.circuit.json", JSON.stringify(cj))
const count = (t: string) => cj.filter((e) => e.type === t).length
console.log(`rendered in ${((performance.now() - t0) / 1e3).toFixed(0)}s: components ${count("pcb_component")}, pads ${count("pcb_smtpad")}, traces ${count("pcb_trace")}, vias ${count("pcb_via")}, pours ${count("pcb_copper_pour")}; errors ${JSON.stringify(kinds)}`)
for (const e of errs.slice(0, 5)) console.log("  ", (e.message ?? "").slice(0, 200))
