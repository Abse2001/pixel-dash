// Placement planner for the CM4 module. Loads the fixed, verified DDR block (unchanged, same coordinates) and adds
// everything else: processor/memory support parts as in module 0.4.4, the CM4 connectors, power, Ethernet PHY,
// boot straps and pull-ups. Output: cm4-module/plan.json (+ plan-items.json for the router, plots and checks).
// Frame: the DDR block's coordinates (mm). The CM4 frame (top view, y up, holes at (0,0) (33,0) (0,48) (33,48))
// maps to it by a pure rotation: x = CM4.x0 + v, y = CM4.y0 - u (see frame.ts).
import { Board, disc, seg, rect, gap, type Item, type Layer, type Pt } from "./geom"
import { EDGE, HOLES, J1, J2 } from "./frame"
import { CM4, SIGNALS, GPIO_PINS, POOL, EXTRA_GPIO, PARTS as NETLIST, PLANE_NETS } from "./design/netlist"
const EXT = import.meta.dir + "/../external/ddr-route"
const DDR = EXT + "/out/module9/ddr-cpu-ram.routed.json"
const srj = await Bun.file(DDR).json(), names: Record<string, string> = await Bun.file(EXT + "/net-names.json").json()
const powerBalls: { chip: string; ball: string; net: string; x: number; y: number }[] = await Bun.file(import.meta.dir + "/power-balls.json").json()
const PADS: Record<string, { pads: { pin: string; x: number; y: number; w: number; h: number }[]; body: [number, number] }> = await Bun.file(import.meta.dir + "/design/pads.json").json()
export { EDGE }
const BOTH: Layer[] = ["top", "bottom"]
const B = new Board()
const bodies: { layer: Layer; s: ReturnType<typeof rect>; ref: string }[] = []
const r3 = (v: number) => +v.toFixed(4)

// ---------- balls ----------
const ball: Record<string, Pt & { r: number }> = {}
for (const o of srj.obstacles) { const m = o.circuitJsonMetadata; ball[`${m.source_component_name}.${m.source_port_name}`] = { x: o.center.x, y: o.center.y, r: o.width / 2 } }
const ballNet: Record<string, string> = {}
for (const c of srj.connections) for (const p of c.pointsToConnect) if (p.port_selector && names[c.name]) ballNet[p.port_selector] = names[c.name]
for (const t of srj.traces) if (t.pcb_trace_id.startsWith("ddr_lane_")) { const n = names[t.connection_name]; for (const e of [t.route[0], t.route.at(-1)]) { const k = Object.keys(ball).find((b) => Math.hypot(ball[b].x - e.x, ball[b].y - e.y) < 0.01); if (k) ballNet[k] = n } }
// supplies: the merged rails of the reference design, with the RTC domain on the processor's internal LDO
const RENAME: Record<string, string> = { VDD_LDO1_1V8: "VDD_1V8", VDD_IO_3V3_SEQ: "VDD_3V3", VDDS_DDR_CPU: "VDDS_DDR", VDDS_RTC_1V8: "VDDS_RTC", VDD_RTC_CORE_1V0: "CAP_VDD_RTC" }
for (const p of powerBalls) ballNet[`${p.chip}.${p.ball}`] = RENAME[p.net] ?? p.net
Object.assign(ballNet, {
  "U1.B4": "GND", // RTC_KALDO_ENn low: internal RTC LDO on, CAP_VDD_RTC only needs its capacitor
  "U1.B9": "VDD_1V8", "U1.A9": "GND", // VREFP / VREFN of the unused ADC
  "U1.C10": "CAP_VBB_MPU", "U1.D9": "CAP_VDD_SRAM_CORE", "U1.D11": "CAP_VDD_SRAM_MPU",
  "U1.V10": "OSC0_IN", "U1.U11": "OSC0_OUT", "U1.J4": "DDR_VREF", "U1.J3": "DDR_VTP",
  "U_DDR.H1": "DDR_VREF", "U_DDR.M8": "DDR_VREF", "U_DDR.L8": "DDR_ZQ",
})
// signals: processor balls with a fixed function (design/netlist.ts), plus the plain GPIOs, whose balls are picked
// from POOL by the shortest total ball-to-pin distance (an optimal assignment)
const cm4PinXY = (n: number) => { const c = n <= 100 ? J1 : J2, m = (n - 1) % 100 + 1, k = (m - 1) >> 1; return { x: c.x + 9.8 - 0.4 * k, y: c.y + (m % 2 ? 1.355 : -1.355) } }
const signals: { name: string; ball: string; mode: number; fn: string }[] = SIGNALS.map((s) => ({ name: s.net, ball: s.ball, mode: s.mode, fn: s.fn }))
{ const want = [...Object.entries(GPIO_PINS).map(([n, p]) => ({ n, at: cm4PinXY(p) })), ...EXTRA_GPIO.map((n) => ({ n, at: { x: -38.5, y: 27 } }))] // PHY_nRST: at the PHY
  const cost = want.map((w) => POOL.map((b) => { const q = ball["U1." + b]; return Math.hypot(q.x - w.at.x, q.y - w.at.y) }))
  for (const [i, j] of hungarian(cost)) signals.push({ name: want[i].n, ball: POOL[j], mode: 7, fn: "GPIO" }) }
for (const s of signals) { if (ballNet["U1." + s.ball]) throw Error(`ball ${s.ball} used twice: ${s.name} / ${ballNet["U1." + s.ball]}`); ballNet["U1." + s.ball] = s.name }
const PLANE = new Set(PLANE_NETS)
/** minimum-cost assignment rows -> columns (rows <= columns), Kuhn-Munkres with potentials */
function hungarian(a: number[][]): [number, number][] { const n = a.length, m = a[0].length, INF = 1e18, u = new Array(n + 1).fill(0), v = new Array(m + 1).fill(0), p = new Array(m + 1).fill(0), way = new Array(m + 1).fill(0)
  for (let i = 1; i <= n; i++) { p[0] = i; let j0 = 0; const minv = new Array(m + 1).fill(INF), used = new Array(m + 1).fill(false)
    do { used[j0] = true; const i0 = p[j0]; let delta = INF, j1 = 0
      for (let j = 1; j <= m; j++) if (!used[j]) { const cur = a[i0 - 1][j - 1] - u[i0] - v[j]; if (cur < minv[j]) { minv[j] = cur; way[j] = j0 } if (minv[j] < delta) { delta = minv[j]; j1 = j } }
      for (let j = 0; j <= m; j++) if (used[j]) { u[p[j]] += delta; v[j] -= delta } else minv[j] -= delta
      j0 = j1 } while (p[j0] !== 0)
    do { const j1 = way[j0]; p[j0] = p[j1]; j0 = j1 } while (j0) }
  const out: [number, number][] = []; for (let j = 1; j <= m; j++) if (p[j]) out.push([p[j] - 1, j - 1]); return out }

// copper on layer 4 (DDR sections moved there, later the routed layer-4 signals): no new via through it
const innerSegs: Item[] = [], ddrInner: { net: string; a: Pt; b: Pt }[] = []
// ---------- existing copper ----------
for (const [k, b] of Object.entries(ball)) B.add({ ...disc(b.x, b.y, b.r), layers: ["top"], net: ballNet[k] ?? "NC:" + k, kind: "ball", ref: k })
type Via = { name: string; x: number; y: number; net: string; d: number; hole: number; ball?: string }
const vias: Via[] = []
const addVia = (v: Via) => { const same = vias.find((o) => o.net === v.net && Math.hypot(o.x - v.x, o.y - v.y) <= 0.02); if (same) return same; vias.push(v); B.add({ ...disc(v.x, v.y, v.d / 2), layers: BOTH, net: v.net, kind: "via", ref: v.name }); return v }
for (const t of srj.traces) {
  if (t.pcb_trace_id.startsWith("ddr_lane_")) { const net = names[t.connection_name]
    for (let i = 0; i < t.route.length; i++) { const a = t.route[i], b = t.route[i + 1]
      if (a.route_type === "via") { B.add({ ...disc(a.x, a.y, (a.via_diameter ?? 0.3) / 2), layers: BOTH, net, kind: "ddrvia" }); continue }
      if (b && b.route_type === "wire" && b.layer === a.layer) { if (a.layer === "top" || a.layer === "bottom") B.add({ ...seg(a, b, a.width ?? 0.102), layers: [a.layer], net, kind: "ddr" }); else { innerSegs.push({ ...seg(a, b, 0.102), layers: [], net, kind: "ddr" }); ddrInner.push({ net, a: { x: a.x, y: a.y }, b: { x: b.x, y: b.y } }) } } }
  } else { const v = t.route.find((p: any) => p.route_type === "via"), k = Object.keys(ball).find((b) => Math.hypot(ball[b].x - v.x, ball[b].y - v.y) < 0.01)!
    addVia({ name: "P_" + k.replace(".", "_"), x: v.x, y: v.y, net: ballNet[k], d: 0.3, hole: 0.1, ball: k }) } }
type Part = { name: string; part: string; x: number; y: number; rot: number; layer: Layer; nets: Record<string, string>; dnp?: boolean }
const parts: Part[] = []
const paths: { net: string; layer: Layer; pts: Pt[]; w: number; from: string; to: string }[] = []
const links: { net: string; layer: Layer; a: Pt; b: Pt; w: number; from: string; to: string }[] = []
// footprints: pad offsets for the part's own frame (pin1 first)
const FP: Record<string, { pads: { pin: string; x: number; y: number; w: number; h: number }[]; body: [number, number] }> = {
  C0201: { pads: [{ pin: "pin1", x: -0.27432, y: 0, w: 0.368427, h: 0.324 }, { pin: "pin2", x: 0.27432, y: 0, w: 0.368427, h: 0.324 }], body: [0.95, 0.36] },
  R0201: { pads: [{ pin: "pin1", x: -0.241554, y: 0, w: 0.3031, h: 0.324 }, { pin: "pin2", x: 0.241554, y: 0, w: 0.3031, h: 0.324 }], body: [0.82, 0.36] },
  C0402: { pads: [{ pin: "pin1", x: -0.420116, y: 0, w: 0.5, h: 0.54 }, { pin: "pin2", x: 0.420116, y: 0, w: 0.5, h: 0.54 }], body: [1.36, 0.56] },
  R0402: { pads: [{ pin: "pin1", x: -0.432816, y: 0, w: 0.565658, h: 0.54 }, { pin: "pin2", x: 0.432816, y: 0, w: 0.565658, h: 0.54 }], body: [1.45, 0.56] },
  C0603: { pads: [{ pin: "pin1", x: -0.700024, y: 0, w: 0.8, h: 0.9 }, { pin: "pin2", x: 0.700024, y: 0, w: 0.8, h: 0.9 }], body: [2.24, 0.94] },
  XTAL3225: { pads: [{ pin: "pin1", x: -1.100074, y: -0.850011, w: 1.4, h: 1.2 }, { pin: "pin2", x: 1.100074, y: -0.850011, w: 1.4, h: 1.2 }, { pin: "pin3", x: 1.100074, y: 0.850011, w: 1.4, h: 1.2 }, { pin: "pin4", x: -1.100074, y: 0.850011, w: 1.4, h: 1.2 }], body: [3.7, 3.0] },
}
// parts new on this module: pad geometry as tscircuit renders them (design/pads.tsx -> design/pads.json)
const G = (k: string) => { const p = PADS[k]; return { pads: p.pads.map((q) => ({ ...q })), body: [p.body[0] + 0.2, p.body[1] + 0.2] as [number, number] } }
Object.assign(FP, { PMIC: G("PMIC"), PHY: G("PHY"), BUCK: G("BUCK"), IND: G("L2U2"), CM4_HDR: { ...G("CM4_HDR"), body: [22.0, 3.86] }, G0402: G("R0402"), G0603: G("C0603"), G0805: G("C0805"),
  XTAL25: { pads: [[-1.1, -0.8, 1], [1.1, -0.8, 2], [1.1, 0.8, 3], [-1.1, 0.8, 4]].map(([x, y, n]) => ({ pin: "pin" + n, x, y, w: 1.4, h: 1.15 })), body: [3.7, 3.0] } })
/** part type -> footprint and either the imported tscircuit component (as module 0.4.4) or value + LCSC number */
export const PARTS: Record<string, { fp: string; comp?: string; file?: string; value?: string; lcsc?: string }> = {
  C100N_0201: { fp: "C0201", comp: "TMK063ABJ104KP_F", file: "../am3354/imports/TMK063ABJ104KP_F" },
  C100N_0402: { fp: "C0402", comp: "CL05B104KO5NNNC", file: "../imports/CL05B104KO5NNNC" },
  C1U_0402: { fp: "C0402", comp: "CL05A105KA5NQNC", file: "./imports/CL05A105KA5NQNC" },
  C10U_0603: { fp: "C0603", comp: "CL10A106KP8NNNC", file: "../imports/CL10A106KP8NNNC" },
  C15P_0402: { fp: "C0402", comp: "A_0402CG150F500NT", file: "../imports/A_0402CG150F500NT" },
  R240_0201: { fp: "R0201", comp: "RC0201FR_07240RL", file: "../am3354/imports/RC0201FR_07240RL" },
  R49R9_0402: { fp: "R0402", comp: "A_0402WGF499JTCE", file: "../am3354/imports/A_0402WGF499JTCE" },
  R1K_0402: { fp: "R0402", comp: "A_0402WGF1001TCE", file: "../imports/A_0402WGF1001TCE" },
  XTAL_24M: { fp: "XTAL3225", comp: "TXM24M0004322DBCDO00T", file: "./imports/TXM24M0004322DBCDO00T" },
  // new on the CM4 module
  PMIC: { fp: "PMIC", value: "TPS65217DRSLR", lcsc: "C702315" }, PHY: { fp: "PHY", value: "LAN8720A-CP-TR", lcsc: "C45223" }, BUCK: { fp: "BUCK", value: "SY8089A1AAC", lcsc: "C479074" },
  IND: { fp: "IND", value: "2.2uH WIP201610P-2R2ML", lcsc: "C315717" }, XTAL_25M: { fp: "XTAL25", value: "25MHz K3A250001210", lcsc: "C18213377" },
  CM4_HDR: { fp: "CM4_HDR", value: "DF40C-100DP-0.4V(51)", lcsc: "C531031" },
  R100K: { fp: "G0402", value: "100k", lcsc: "C25741" }, R10K: { fp: "G0402", value: "10k", lcsc: "C25744" }, R1K: { fp: "G0402", value: "1k", lcsc: "C11702" },
  R2K2: { fp: "G0402", value: "2.2k", lcsc: "C25879" }, R4K7: { fp: "G0402", value: "4.7k", lcsc: "C25900" }, R1K5: { fp: "G0402", value: "1.5k", lcsc: "C25867" },
  R12K1: { fp: "G0402", value: "12.1k 1%", lcsc: "C25852" }, R22K: { fp: "G0402", value: "22k 1%", lcsc: "C25768" }, R200K: { fp: "G0402", value: "200k 1%", lcsc: "C25764" },
  R49R9: { fp: "G0402", value: "49.9 1%", lcsc: "C25120" }, R0: { fp: "G0402", value: "0", lcsc: "C17168" },
  C22U_0603: { fp: "G0603", value: "22uF 6.3V", lcsc: "C59461" }, C22U_0805: { fp: "G0805", value: "22uF 25V", lcsc: "C45783" }, C4U7_0603: { fp: "G0603", value: "4.7uF 16V", lcsc: "C19666" },
  C4U7_0402: { fp: "G0402", value: "4.7uF 10V", lcsc: "C23733" }, C2U2_0402: { fp: "G0402", value: "2.2uF 6.3V", lcsc: "C12530" }, C10U_0402: { fp: "G0402", value: "10uF 6.3V", lcsc: "C15525" },
  C470P_0402: { fp: "G0402", value: "470pF", lcsc: "C1537" },
}
/** world pads of a part (bottom side parts are mirrored, as tscircuit renders them) */
export const padsOf = (p: { part: string; x: number; y: number; rot: number; layer: Layer }) => { const f = FP[PARTS[p.part].fp], c = Math.cos(p.rot * Math.PI / 180), s = Math.sin(p.rot * Math.PI / 180), m = p.layer === "bottom" ? -1 : 1
  return f.pads.map((q) => ({ pin: q.pin, x: p.x + m * q.x * c - q.y * s, y: p.y + m * q.x * s + q.y * c, shape: rect(p.x + m * q.x * c - q.y * s, p.y + m * q.x * s + q.y * c, q.w, q.h, p.rot) })) }
const bodyOf = (p: { part: string; x: number; y: number; rot: number }) => { const [w, h] = FP[PARTS[p.part].fp].body; return rect(p.x, p.y, w, h, p.rot) }
const CLR = (it: Item) => it.kind === "ddr" || it.kind === "ddrvia" || it.kind === "pad" ? 0.18 : 0.1 // clearance of new static copper (JLCPCB: 0.15 mm between pads of different nets, 0.18 mm between 0402 parts)
/** can this part sit here? returns the reason it cannot */
function partBlocked(p: Omit<Part, "name">, bodyGap = 0.1): string | null {
  const body = bodyOf(p); for (const q of body.pts) if (q.x < EDGE.x0 + 0.4 || q.x > EDGE.x1 - 0.4 || q.y < EDGE.y0 + 0.4 || q.y > EDGE.y1 - 0.4) return "edge"
  for (const o of bodies) if (o.layer === p.layer && gap(body, o.s) < (o.ref === "U1" || o.ref === "U_DDR" ? 0.9 : bodyGap)) return "body " + o.ref // JLCPCB: 1 mm from a BGA on the same side
  for (const q of padsOf(p)) { const h = B.hits(q.shape, [p.layer], p.nets[q.pin] ?? "?", CLR); if (h.length) return `pad ${q.pin} vs ${h[0].net} ${h[0].kind}` }
  return null }
function commitPart(p: Part) { parts.push(p); bodies.push({ layer: p.layer, s: bodyOf(p), ref: p.name }); for (const q of padsOf(p)) B.add({ ...q.shape, layers: [p.layer], net: p.nets[q.pin] ?? "NC:" + p.name + "." + q.pin, kind: "pad", ref: p.name + "." + q.pin }); return p }
const viaBlocked = (x: number, y: number, net: string, d = 0.3) => { if (innerSegs.some((s) => s.net !== net && gap(disc(x, y, d / 2), s) < 0.13)) return "inner trace"; if (B.near(disc(x, y, 0.45), 0).some((it) => it.layers.length === 2 && it.net === net && Math.hypot(it.pts[0].x - x, it.pts[0].y - y) > 0.02 && Math.hypot(it.pts[0].x - x, it.pts[0].y - y) < 0.45)) return "own via too close"; if (x < EDGE.x0 + 0.45 || x > EDGE.x1 - 0.45 || y < EDGE.y0 + 0.45 || y > EDGE.y1 - 0.45) return "edge"; const h = B.hits(disc(x, y, d / 2), BOTH, net, CLR); return h.length ? `${h[0].net} ${h[0].kind}` : null }
const viaAt = (x: number, y: number, net: string, tol = 0.02) => vias.find((v) => v.net === net && Math.hypot(v.x - x, v.y - y) <= tol)
// chip bodies
bodies.push({ layer: "top", s: rect(-44.8, 15.15, 15.3, 15.3), ref: "U1" }, { layer: "top", s: rect(-70, 15.15, 14.3, 9.3), ref: "U_DDR" })
// mounting holes: nothing within 0.4 mm of the hole on any layer, no part body within 1 mm (screw head / washer)
for (const h of HOLES) { B.add({ ...disc(h.x, h.y, h.d / 2 + 0.3), layers: BOTH, net: "HOLE", kind: "hole" }); for (const layer of BOTH) bodies.push({ layer, s: rect(h.x, h.y, h.d + 2, h.d + 2), ref: "HOLE" }) }
// ---------- connectors (bottom side, via-in-pad at every used pin) ----------
type Pin = { conn: string; pin: string; cm4: number; x: number; y: number; k: number; role: string }
const pins: Pin[] = []
// the CM4 plugs: J1 = CM4 pins 1-100, J2 = 101-200 (footprint pins 101-104 are the fixing tabs)
for (const [name, c, base] of [["J1", J1, 0], ["J2", J2, 100]] as const) {
  const p = commitPart({ name, part: "CM4_HDR", x: c.x, y: c.y, rot: 0, layer: "bottom", nets: {} })
  for (const q of padsOf(p)) { const n = +q.pin.slice(3); if (n > 100) continue
    pins.push({ conn: name, pin: q.pin, cm4: base + n, x: r3(q.x), y: r3(q.y), k: (n - 1) >> 1, role: CM4[base + n] || "NC" }) } }
// check the CM4 geometry: pin 1 / 101 at the +x end, odd pins on J1's outer and J2's inner row
for (const n of [1, 2, 99, 101, 102]) { const p = pins.find((q) => q.cm4 === n)!, e = cm4PinXY(n); if (Math.hypot(p.x - e.x, p.y - e.y) > 1e-3) throw Error(`CM4 pin ${n} at (${p.x}, ${p.y}), expected (${e.x}, ${e.y})`) }
// connector pads get their nets; every supply/ground pin gets a via in its pad (staggered along the pad)
for (const p of pins) { const it = B.items.find((i) => i.ref === `${p.conn}.${p.pin}`)!
  if (p.role === "NC") continue
  it.net = p.role
  if (!PLANE.has(p.role)) continue
  addVia({ name: `V_${p.conn}_${p.pin}`, x: p.x, y: r3(p.y + (p.k % 2 ? 0.2 : -0.2)), net: p.role, d: 0.3, hole: 0.1 }) }
for (const v of vias.filter((v) => /^V_J/.test(v.name))) { const h = B.hits(disc(v.x, v.y, v.d / 2), BOTH, v.net, 0.1); if (h.length) throw Error(`connector via ${v.name} hits ${h[0].net} ${h[0].kind} ${h[0].ref}`) }

// ---------- helpers ----------
const report: string[] = []
const T0 = performance.now(), tick = (m: string) => console.error(`[${((performance.now() - T0) / 1e3).toFixed(1)}s] ${m}`)
const U1 = (b: string) => ball["U1." + b], RAMB = (b: string) => ball["U_DDR." + b]
const underPart = (x: number, y: number, r: number) => bodies.some((b) => b.ref !== "U1" && b.ref !== "U_DDR" && !b.ref.startsWith("J") && gap(disc(x, y, r), b.s) < 0.05)
/** where the handheld signals leave the processor: the outer ball rows on the non-DDR sides and a strip outside them. No new via or free part goes here. */
const escapeZone = (x: number, y: number) => (x > -49.0 && x < -36.3 && y > 19.95 && y < 23.9) || (x > -40.85 && x < -36.3 && y > 6.4 && y < 23.9) || (x > -52.5 && x < -36.3 && y > 6.4 && y < 11.2)
/** small two-layer maze router for the handful of local nets (calibration resistors, regulator capacitors, VREF escapes) */
function maze(net: string, start: Pt & { layer: Layer }, goal: (x: number, y: number, l: Layer) => boolean, w: number, o: { clr?: number; win?: number; viaCost?: number; from: string; to: string; layers?: Layer[]; startVia?: boolean; quiet?: boolean }) {
  const P = 0.05, win = o.win ?? 5, N = Math.round(2 * win / P) + 1, clr = o.clr ?? 0.1, L: Layer[] = ["top", "bottom"], allowed = o.layers ?? L
  const X = (i: number) => start.x - win + i * P, Y = (j: number) => start.y - win + j * P
  const okc = new Map<number, boolean>(), ok = (i: number, j: number, l: number) => { const k = (l * N + j) * N + i; let v = okc.get(k); if (v === undefined) { v = i >= 0 && j >= 0 && i < N && j < N && X(i) > EDGE.x0 + 0.3 && X(i) < EDGE.x1 - 0.3 && Y(j) > EDGE.y0 + 0.3 && Y(j) < EDGE.y1 - 0.3 && !B.hits(disc(X(i), Y(j), w / 2), [L[l]], net, clr + 0.012).length; okc.set(k, v) } return v }
  const s0 = (L.indexOf(start.layer) * N + Math.round(win / P)) * N + Math.round(win / P), dist = new Map<number, number>([[s0, 0]]), prev = new Map<number, number>(), open: [number, number][] = [[0, s0]]
  const sOther = ((1 - L.indexOf(start.layer)) * N + Math.round(win / P)) * N + Math.round(win / P); if (o.startVia && allowed.length > 1) { dist.set(sOther, 0); open.push([0, sOther]) }
  let end = -1
  const hpush = (e: [number, number]) => { open.push(e); let i = open.length - 1; while (i > 0) { const p = (i - 1) >> 1; if (open[p][0] <= open[i][0]) break; [open[p], open[i]] = [open[i], open[p]]; i = p } }
  const hpop = () => { const top = open[0], last = open.pop()!; if (open.length) { open[0] = last; let i = 0; for (;;) { const a = 2 * i + 1, b = a + 1; let m = i; if (a < open.length && open[a][0] < open[m][0]) m = a; if (b < open.length && open[b][0] < open[m][0]) m = b; if (m === i) break; [open[m], open[i]] = [open[i], open[m]]; i = m } } return top }
  while (open.length) { const [d, k] = hpop(); if (d > (dist.get(k) ?? 1e9)) continue
    const i = k % N, j = Math.floor(k / N) % N, l = Math.floor(k / N / N)
    if (goal(X(i), Y(j), L[l])) { end = k; break }
    const push = (k2: number, c: number) => { if (d + c < (dist.get(k2) ?? 1e9)) { dist.set(k2, d + c); prev.set(k2, k); hpush([d + c, k2]) } }
    for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) if (allowed.includes(L[l]) && ok(i + di, j + dj, l)) push((l * N + j + dj) * N + i + di, Math.hypot(di, dj) * P)
    if (allowed.length > 1 && (k === s0 || k === sOther ? false : (!viaBlocked(X(i), Y(j), net) && !underPart(X(i), Y(j), 0.15) && !escapeZone(X(i), Y(j)))) && ok(i, j, 1 - l)) push(((1 - l) * N + j) * N + i, o.viaCost ?? 1.5) }
  if (end < 0) { if (!o.quiet) report.push(`!! maze ${net} ${o.from} -> ${o.to}: no path`); return null }
  const nodes: number[] = []; for (let k = end; k !== undefined; k = prev.get(k)!) { nodes.unshift(k); if (k === s0 || (o.startVia && k === sOther)) break }
  // split into single-layer polylines with vias between them
  let cur: Pt[] = [], curL = Math.floor(nodes[0] / N / N); const flush = () => { if (cur.length > 1) { const pts = cur.filter((p, i) => i === 0 || i === cur.length - 1 || Math.abs((cur[i].x - cur[i - 1].x) * (cur[i + 1].y - cur[i].y) - (cur[i].y - cur[i - 1].y) * (cur[i + 1].x - cur[i].x)) > 1e-9)
      for (let i = 0; i + 1 < pts.length; i++) B.add({ ...seg(pts[i], pts[i + 1], w), layers: [L[curL]], net, kind: "trace" }); paths.push({ net, layer: L[curL], pts, w, from: o.from, to: o.to }) } cur = [] }
  for (const k of nodes) { const i = k % N, j = Math.floor(k / N) % N, l = Math.floor(k / N / N), p = { x: r3(X(i)), y: r3(Y(j)) }
    if (l !== curL) { flush(); if (!viaAt(p.x, p.y, net)) addVia({ name: `V_${net}_${vias.length}`, x: p.x, y: p.y, net, d: 0.3, hole: 0.1 }); curL = l }
    cur.push(p) }
  flush(); return { x: r3(X(end % N)), y: r3(Y(Math.floor(end / N) % N)), layer: L[Math.floor(end / N / N)] } }
/** via for a ball: in the pad when the other side is free, otherwise a short top-layer escape to the nearest legal via site */
function ballVia(k: string): Via | null { const b = ball[k], net = ballNet[k]; const have = vias.find((v) => v.ball === k); if (have) return have
  // a via centred in its own ball pad is smaller than the pad, so only the far side decides
  if (!viaBlocked(b.x, b.y, net) || (!B.hits(disc(b.x, b.y, 0.15), ["bottom"], net, 0.1).length && !B.near(disc(b.x, b.y, 0.5), 0).some((it) => it.layers.length === 2 && Math.hypot(it.pts[0].x - b.x, it.pts[0].y - b.y) < 0.45))) return addVia({ name: "P_" + k.replace(".", "_"), x: b.x, y: b.y, net, d: 0.3, hole: 0.1, ball: k })
  if (process.env.DBG) console.error(`   ${k}: centred via blocked by ${viaBlocked(b.x, b.y, net)}`)
  // the other side is occupied under the ball centre: an off-centre via-in-pad (filled and capped), centre still on the pad
  for (const [d, need] of [[0.3, 0.1], [0.25, 0.09]] as const) { let best = { g: -9, x: 0, y: 0 }
    for (let dx = -0.2; dx <= 0.2001; dx += 0.01) for (let dy = -0.2; dy <= 0.2001; dy += 0.01) { if (Math.hypot(dx, dy) > b.r) continue
      const s = disc(b.x + dx, b.y + dy, d / 2); let g = 9; for (const it of B.near(s, 0.3)) if (it.net !== net) g = Math.min(g, gap(s, it)); if (g > best.g) best = { g, x: r3(b.x + dx), y: r3(b.y + dy) } }
    if (best.g >= need) { report.push(`${k} (${net}): via-in-pad ${Math.hypot(best.x - b.x, best.y - b.y).toFixed(2)} mm off centre, pad ${d} mm, ${best.g.toFixed(3)} mm to the nearest other copper`); return addVia({ name: "P_" + k.replace(".", "_"), x: best.x, y: best.y, net, d, hole: 0.1, ball: k }) } }
  report.push(`!! ${k} (${net}): no via possible`); return null }
/** two-pad part straight across two vias (pin1 on a, pin2 on b) */
function pairPart(name: string, part: string, a: Pt, b: Pt, net1: string, net2: string, layer: Layer): Part | null {
  const ang = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI, rot = (((layer === "bottom" ? ang + 180 : ang) % 360) + 360) % 360
  const p: Part = { name, part, x: r3((a.x + b.x) / 2), y: r3((a.y + b.y) / 2), rot: r3(rot), layer, nets: { pin1: net1, pin2: net2 } }
  const why = partBlocked(p, 0.18); if (why && process.env.DBG) console.error(`   pair ${name} L=${Math.hypot(b.x - a.x, b.y - a.y).toFixed(2)}: ${why}`); return why ? null : p }
const reach = (part: string) => { const f = FP[PARTS[part].fp], off = Math.abs(f.pads[0].x), m = f.pads[0].w / 2 - 0.04; return [Math.max(2 * (off - m), 0.45), 2 * (off + m)] }
/** a two-pad part with pin1 on an existing via; pin2 on an existing via of net2 in reach, else on a new via */
function anchored(name: string, part: string, at: Pt, net1: string, net2: string, layer: Layer = "bottom", existingOnly = false): Part | null {
  const [lo, hi] = reach(part), ideal = 2 * Math.abs(FP[PARTS[part].fp].pads[0].x); let best: { p: Part; nv: Pt | null; cost: number } | null = null
  for (const v of vias) { const L = Math.hypot(v.x - at.x, v.y - at.y); if (v.net !== net2 || L < lo || L > hi) continue
    const p = pairPart(name, part, at, v, net1, net2, layer); if (p && (!best || Math.abs(L - ideal) < best.cost)) best = { p, nv: null, cost: Math.abs(L - ideal) } }
  if (!best && !existingOnly) for (let dx = -hi; dx <= hi + 1e-9; dx += 0.05) for (let dy = -hi; dy <= hi + 1e-9; dy += 0.05) { const L = Math.hypot(dx, dy); if (L < lo || L > hi) continue
    const nv = { x: r3(at.x + dx), y: r3(at.y + dy) }, cost = 1 + Math.abs(L - ideal) + (escapeZone(nv.x, nv.y) ? 50 : 0); if (best && cost >= best.cost) continue
    if (viaBlocked(nv.x, nv.y, net2) || underPart(nv.x, nv.y, 0.15)) continue
    const p = pairPart(name, part, at, nv, net1, net2, layer); if (p) best = { p, nv, cost } }
  if (!best) return null
  commitPart(best.p); if (best.nv) addVia({ name: `V_${name}_2`, x: best.nv.x, y: best.nv.y, net: net2, d: 0.3, hole: 0.1 }); return best.p }
/** a two-pad part anywhere near a point, with its own via(s) inside the pads listed in `viaPins` */
function free(name: string, part: string, near: Pt, net1: string, net2: string, o: { layers?: Layer[]; maxDist?: number; viasPerPad?: number; step?: number; score?: (p: Part) => number; viaPins?: string[]; ok?: (p: Part) => boolean; anywhere?: boolean } = {}): Part | null {
  const n = o.viasPerPad ?? 1, R = o.maxDist ?? 6, st = o.step ?? 0.1, ls = o.layers ?? (["bottom", "top"] as Layer[]), cands: { p: Part; cost: number }[] = []
  for (const layer of ls) for (let dx = -R; dx <= R + 1e-9; dx += st) for (let dy = -R; dy <= R + 1e-9; dy += st) { const d = Math.hypot(dx, dy); if (d > R) continue
    for (const rot of [0, 90]) { const p: Part = { name, part, x: r3(near.x + dx), y: r3(near.y + dy), rot, layer, nets: { pin1: net1, pin2: net2 } }
      if ((o.ok && !o.ok(p)) || (!o.anywhere && [[0, 0], [0.9, 0], [-0.9, 0], [0, 0.9], [0, -0.9]].some(([ax, ay]) => escapeZone(p.x + ax, p.y + ay)))) continue
      cands.push({ p, cost: (o.score ? o.score(p) : d) + (layer === ls[0] ? 0 : 0.5) }) } }
  cands.sort((a, b) => a.cost - b.cost); tick(`${name}: ${cands.length} candidates`)
  for (const { p } of cands) { if (partBlocked(p, 0.2)) continue
    const vs: (Pt & { net: string })[] = []; let ok = true
    for (const q of padsOf(p)) { if (o.viaPins && !o.viaPins.includes(q.pin)) continue; const net = p.nets[q.pin]
      for (let i = 0; i < n && ok; i++) { const t = n === 1 ? 0 : (i - (n - 1) / 2) * 0.5, v = { x: r3(q.x + (p.rot === 0 ? 0 : t)), y: r3(q.y + (p.rot === 0 ? t : 0)), net }; if (viaBlocked(v.x, v.y, net)) ok = false; else vs.push(v) } if (!ok) break }
    if (!ok) continue
    commitPart(p); vs.forEach((v, i) => addVia({ name: `V_${name}_${i + 1}`, x: v.x, y: v.y, net: v.net, d: 0.3, hole: 0.1 })); return p }
  report.push(`!! ${name}: no free site within ${R} mm of (${near.x.toFixed(2)}, ${near.y.toFixed(2)})`); return null }
/** part on a ball's via if it fits there, otherwise close by with a routed link */
const innerNets: string[] = []
const todo: { name: string; part: string; k: string; net2: string }[] = []
const attach = (name: string, part: string, k: string, net2: string) => todo.push({ name, part, k, net2 })
function uncommit(name: string) { const i = parts.findIndex((p) => p.name === name); if (i >= 0) parts.splice(i, 1)
  for (let j = bodies.length - 1; j >= 0; j--) if (bodies[j].ref === name) bodies.splice(j, 1)
  for (const it of B.items) if (it.ref?.startsWith(name + ".") || it.ref?.startsWith(`V_${name}_`)) it.layers = []
  for (let j = vias.length - 1; j >= 0; j--) if (vias[j].name.startsWith(`V_${name}_`)) vias.splice(j, 1) }
function attachAll() {
  const open = todo.filter((t) => { const v = ballVia(t.k); if (!v) { report.push(`!! ${t.name}: ${t.k} has no via`); return false } return !anchored(t.name, t.part, v, ballNet[t.k], t.net2, "bottom", true) }) // first the ones that fit across two existing vias
  for (const t of open) { tick(t.name); const v = ballVia(t.k)!, net = ballNet[t.k]
    if (anchored(t.name, t.part, v, net, t.net2)) continue
    const tried = new Set<string>(); let done = false
    for (let n = 0; n < 8 && !done; n++) {
      const p = free(t.name, t.part, v, net, t.net2, { layers: ["bottom", "top"], maxDist: 8, viaPins: ["pin2"], ok: (q) => ![...tried].some((k) => { const [x, y, l] = k.split(","); return l === q.layer && Math.hypot(+x - q.x, +y - q.y) < 0.7 }) }); if (!p) break
      const pad = padsOf(p).find((q) => q.pin === "pin1")!
      const e = maze(net, { x: v.x, y: v.y, layer: "bottom" }, (x, y, l) => l === p.layer && gap(disc(x, y, 0.001), pad.shape) < -0.06, 0.102, { startVia: true, from: v.name, to: `${t.name}.pin1`, win: 9, quiet: true, clr: 0.1 })
      if (e) { done = true; report.push(`${t.name}: not on the via of ${t.k}; ${Math.hypot(p.x - v.x, p.y - v.y).toFixed(2)} mm away on the ${p.layer} side, linked by a routed trace (site ${n + 1})`) } else { tried.add(`${p.x},${p.y},${p.layer}`); uncommit(t.name) } }
    if (done) continue
    // boxed in by the DDR copper on both outer layers: the part gets a via in each pad and the net runs on an inner layer
    const p = free(t.name, t.part, v, net, t.net2, { layers: ["bottom", "top"], maxDist: 8 }) ?? free(t.name, t.part, v, net, t.net2, { layers: ["bottom", "top"], maxDist: 15, step: 0.15 }) ?? free(t.name, t.part, v, net, t.net2, { layers: ["bottom", "top"], maxDist: 15, step: 0.15, anywhere: true })
    if (p) { innerNets.push(net); report.push(`${t.name}: ${t.k} cannot be reached on the outer layers; part ${Math.hypot(p.x - v.x, p.y - v.y).toFixed(2)} mm away on the ${p.layer} side, net ${net} runs on an inner layer`) } else report.push(`!! ${t.name}: could not be linked to ${t.k}`) } }

// ---------- ball vias, regulator capacitors, calibration ----------
for (const k of ["U1.B9", "U1.A9", "U1.J4", "U_DDR.H1", "U_DDR.M8"]) ballVia(k)
// balls the DDR copper boxes in on both outer layers: via-in-pad now (the DDR route keeps the spot free), routed on layer 4 later
for (const s of signals) if (innerBall(s.ball)) { const v = ballVia("U1." + s.ball), b = ball["U1." + s.ball]; if (!v || Math.hypot(v.x - b.x, v.y - b.y) > 1e-3) report.push(`!! ${s.name} (${s.ball}): no centred via-in-pad`) }
// ---------- crystal (top side, below the processor) ----------
{ const Y = commitPart({ name: "Y_OSC0", part: "XTAL_24M", x: -43.55, y: 4.8, rot: 90, layer: "top", nets: { pin3: "OSC0_IN", pin1: "OSC0_OUT", pin2: "GND", pin4: "GND" } })
  const yp = Object.fromEntries(padsOf(Y).map((q) => [q.pin, q]))
  for (const g of ["pin2", "pin4"]) addVia({ name: `V_Y_OSC0_${g}`, x: r3(yp[g].x), y: r3(yp[g].y), net: "GND", d: 0.3, hole: 0.1 })
  const cin = commitPart({ name: "C_OSC0_IN", part: "C15P_0402", x: -45.95, y: 5.9, rot: 0, layer: "top", nets: { pin2: "OSC0_IN", pin1: "GND" } })
  const cout = commitPart({ name: "C_OSC0_OUT", part: "C15P_0402", x: -41.4, y: 3.7, rot: 90, layer: "top", nets: { pin2: "OSC0_OUT", pin1: "GND" } })
  const ci = Object.fromEntries(padsOf(cin).map((q) => [q.pin, q])), co = Object.fromEntries(padsOf(cout).map((q) => [q.pin, q]))
  addVia({ name: "V_C_OSC0_IN_1", x: r3(ci.pin1.x), y: r3(ci.pin1.y), net: "GND", d: 0.3, hole: 0.1 }); addVia({ name: "V_C_OSC0_OUT_1", x: r3(co.pin1.x), y: r3(co.pin1.y), net: "GND", d: 0.3, hole: 0.1 })
  const tr = (net: string, pts: Pt[], w: number, from: string, to: string) => { for (let i = 0; i + 1 < pts.length; i++) { const s = seg(pts[i], pts[i + 1], w), h = B.hits(s, ["top"], net, 0.1); if (h.length) report.push(`crystal trace ${net} hits ${h[0].net} ${h[0].kind} ${h[0].ref ?? ""}`); B.add({ ...s, layers: ["top"], net, kind: "trace" }) }; paths.push({ net, layer: "top", pts, w, from, to }) }
  tr("OSC0_IN", [U1("V10"), { x: U1("V10").x, y: 6.3 }], 0.15, "U1.V10", "Y_OSC0.pin3")
  tr("OSC0_IN", [{ x: ci.pin2.x, y: ci.pin2.y }, { x: yp.pin3.x - 0.3, y: yp.pin3.y }], 0.3, "C_OSC0_IN.pin2", "Y_OSC0.pin3")
  tr("OSC0_OUT", [U1("U11"), { x: -43.2, y: 8.75 }, { x: -43.2, y: 7.95 }, { x: -42.85, y: 7.6 }, { x: -41.75, y: 7.6 }, { x: co.pin2.x, y: 7.25 }, { x: co.pin2.x, y: co.pin2.y }], 0.15, "U1.U11", "C_OSC0_OUT.pin2")
  tr("OSC0_OUT", [{ x: co.pin2.x, y: co.pin2.y }, { x: yp.pin1.x + 0.3, y: co.pin2.y }], 0.3, "C_OSC0_OUT.pin2", "Y_OSC0.pin1") }

attach("C_CAP_RTC", "C1U_0402", "U1.D6", "GND"); attach("C_VBB_MPU", "C1U_0402", "U1.C10", "GND"); attach("C_SRAM_CORE", "C1U_0402", "U1.D9", "GND"); attach("C_SRAM_MPU", "C1U_0402", "U1.D11", "GND")
attach("R_ZQ", "R240_0201", "U_DDR.L8", "GND"); attach("R_VTP", "R49R9_0402", "U1.J3", "GND"); attach("C_VDDS_RTC", "C100N_0402", "U1.D7", "GND")
attachAll()
// DDR_VREF: a via per ball into the layer-4 VREF copper, and a 100 nF bypass next to each device connection
for (const [k, nm] of [["U1.J4", "C_VREF_CPU"], ["U_DDR.H1", "C_VREF_DQ"], ["U_DDR.M8", "C_VREF_CA"]] as const) { const v = ballVia(k); if (!v) continue
  if (!anchored(nm, "C100N_0201", v, "DDR_VREF", "GND")) { const p = free(nm, "C100N_0402", v, "DDR_VREF", "GND", { maxDist: 8 }); if (p) report.push(`${nm}: ${Math.hypot(p.x - v.x, p.y - v.y).toFixed(2)} mm from the VREF via of ${k} (own vias into the VREF copper)`) } }

// ---------- decoupling straight across supply/ground ball vias (100 nF 0402) ----------
function onBallVias(prefix: string, chip: string, nets: Record<string, number>, first: string[] = [], part = "C100N_0402", got: Record<string, number> = {}) { tick(prefix)
  const vs = vias.filter((v) => v.ball?.startsWith(chip + ".") && nets[v.net]).sort((a, b) => (first.indexOf(a.ball!.split(".")[1]) + 100) % 100 - (first.indexOf(b.ball!.split(".")[1]) + 100) % 100)
  for (const want of [0.8, 1.14]) for (let pass = 0; pass < 2; pass++) for (const v of vs) { const bn = v.ball!.split(".")[1], name = `${prefix}_${bn}`
    if ((got[v.net] ?? 0) >= nets[v.net] || (pass === 0 && !first.includes(bn)) || parts.some((p) => p.name === name)) continue
    for (const w of vias.filter((w) => w.net === "GND" && w.ball?.startsWith(chip + ".") && Math.abs(Math.hypot(w.x - v.x, w.y - v.y) - want) < 0.02)) { const p = pairPart(name, part, v, w, v.net, "GND", "bottom"); if (!p) continue
      commitPart(p); got[v.net] = (got[v.net] ?? 0) + 1; break } }
  return got }
report.push("processor decoupling on ball vias: " + JSON.stringify(onBallVias("C", "U1", { VDD_CORE: 10, VDD_MPU: 5, VDD_3V3: 8, VDD_1V8: 9 }, ["E7", "R10", "R11", "H15", "D8", "N16", "E9", "D10", "R16", "N15", "R15"])))
for (const b of ["D10", "R10", "R11", "H15", "N16", "E7", "D8", "E9"]) if (!parts.some((p) => p.name === "C_" + b)) { const v = viaAt(U1(b).x, U1(b).y, ballNet["U1." + b])!; if (!anchored("C_" + b, "C100N_0402", v, v.net, "GND")) report.push(`C_${b}: no site at the ball via (${v.net})`) }
// DDR high-speed bypass (Table 7-65): processor 20 within 400 mil, memory 12 within 150 mil
const ballsOf = new Map<string, Pt[]>()
const nearestBall = (chip: string, net: string, p: Pt) => { const key = chip + "/" + net; let a = ballsOf.get(key); if (!a) ballsOf.set(key, (a = Object.keys(ball).filter((k) => k.startsWith(chip + ".") && ballNet[k] === net).map((k) => ball[k]))); let m = 1e9; for (const b of a) { const d = Math.hypot(b.x - p.x, b.y - p.y); if (d < m) m = d } return m }
for (const [chip, tag, need, limit, c] of [["U_DDR", "RAM", 12, 3.81, { x: -70, y: 15.15 }], ["U1", "CPU", 20, 10.16, { x: -48.4, y: 15.55 }]] as const) {
  const hs = () => parts.filter((p) => p.name.startsWith("C_HS_" + tag)), dist = (p: Pt) => Math.max(nearestBall(chip, "VDDS_DDR", p), nearestBall(chip, "GND", p))
  // (a) on the opposite side, straight across a VDDS_DDR ball via and a ground ball via (via sharing allowed there: Table 7-65 note 7)
  const g0 = onBallVias("C_HS_" + tag, chip, { VDDS_DDR: need }), onVias = onBallVias("C_HS_" + tag, chip, { VDDS_DDR: need }, [], "C100N_0201", g0).VDDS_DDR ?? 0
  // (b) under the device: one end on a ground ball via, the other on a new VDDS_DDR via between the balls
  let under = 0
  for (const g of vias.filter((v) => v.ball?.startsWith(chip + ".") && v.net === "GND").sort((p, q) => nearestBall(chip, "VDDS_DDR", p) - nearestBall(chip, "VDDS_DDR", q))) { if (hs().length >= need) break
    if (nearestBall(chip, "VDDS_DDR", g) > (chip === "U1" ? 3.3 : 2.5)) break
    if (anchored(`C_HS_${tag}_U${under + 1}`, "C100N_0201", g, "GND", "VDDS_DDR")) under++ }
  // (c) anywhere else inside the distance limit, two vias of its own
  for (let n = hs().length; n < need; n++) if (!free(`C_HS_${tag}_X${n + 1}`, "C100N_0402", c, "VDDS_DDR", "GND", { maxDist: 9.5, step: 0.15, ok: (p) => dist(p) <= limit - 0.4 && !hs().some((o) => Math.hypot(o.x - p.x, o.y - p.y) < 1.0), score: dist })) break
  report.push(`DDR high-speed bypass ${tag}: ${hs().length}/${need} (${onVias} across ball vias, ${under} under the device on a ground ball via); worst distance to a supply/ground ball ${Math.max(...hs().map(dist)).toFixed(2)} mm (limit ${limit})`) }

// ---------- bulk capacitors (10 uF 0603, two vias in each pad) ----------
for (const [name, net, near, layers] of [
  ["C_BULK_DDR_CPU1", "VDDS_DDR", { x: -50.5, y: 24.5 }, ["bottom", "top"]], ["C_BULK_DDR_CPU2", "VDDS_DDR", { x: -50.5, y: 6.0 }, ["bottom", "top"]],
  ["C_BULK_DDR_RAM1", "VDDS_DDR", { x: -70, y: 21.5 }, ["bottom", "top"]], ["C_BULK_DDR_RAM2", "VDDS_DDR", { x: -70, y: 8.8 }, ["bottom", "top"]],
  // the other rails: next to where they come in from the connectors, clear of the signal escape
  ["C_BULK_CORE1", "VDD_CORE", { x: -55.2, y: 27.9 }, ["top", "bottom"]], ["C_BULK_CORE2", "VDD_CORE", { x: -53.6, y: 25.6 }, ["top", "bottom"]], ["C_BULK_MPU", "VDD_MPU", { x: -52.8, y: 27.9 }, ["top", "bottom"]],
  ["C_BULK_3V3", "VDD_3V3", { x: -36.2, y: 4.2 }, ["top", "bottom"]], ["C_BULK_1V8", "VDD_1V8", { x: -34.4, y: 6.0 }, ["top", "bottom"]],
] as const) free(name, "C10U_0603", near, net, "GND", { layers: [...layers], maxDist: 7, viasPerPad: 2, step: 0.1 })
// VREF divider: 1 k / 1 k from VDDS_DDR, with its own bypass, between the two chips
free("R_VREF_TOP", "R1K_0402", { x: -58, y: 5.5 }, "VDDS_DDR", "DDR_VREF", { maxDist: 8 })
{ const rt = parts.find((p) => p.name === "R_VREF_TOP"); if (rt) { free("R_VREF_BOT", "R1K_0402", rt, "DDR_VREF", "GND", { maxDist: 3, layers: [rt.layer] }); free("C_VREF_DIV", "C100N_0402", rt, "DDR_VREF", "GND", { maxDist: 3, layers: [rt.layer] }) } }

// ---------- CM4 module circuits: power, Ethernet PHY, straps, pull-ups (design/netlist.ts) ----------
const NL = Object.fromEntries(NETLIST.map((p) => [p.ref, p]))
const pad = (ref: string, pin: string) => { const p = parts.find((q) => q.name === ref)!; return padsOf(p).find((q) => q.pin === pin)! }
const ptrace = (net: string, layer: Layer, pts: Pt[], w: number, from: string, to: string) => { for (let i = 0; i + 1 < pts.length; i++) { const s = seg(pts[i], pts[i + 1], w), h = B.hits(s, [layer], net, 0.1); if (h.length) report.push(`!! trace ${net} ${from}->${to} hits ${h[0].net} ${h[0].kind} ${h[0].ref ?? ""}`); B.add({ ...s, layers: [layer], net, kind: "trace" }) } paths.push({ net, layer, pts, w, from, to }) }
/** a netlist part at a fixed spot */
function placeAt(ref: string, x: number, y: number, rot: number, layer: Layer = "top") { const n = NL[ref], p: Part = { name: ref, part: n.part, x: r3(x), y: r3(y), rot, layer, nets: Object.fromEntries(Object.entries(n.nets).filter(([, v]) => v)) }
  const why = partBlocked(p, 0.2); if (why) report.push(`!! ${ref} at (${x}, ${y}): ${why}`); return commitPart(p) }
/** a plane pin of a fixed part: a stub out of the pad along `dir` to the first legal via site */
function stubVia(ref: string, pin: string, dir: Pt, w = 0.2, from = 0.5) { const q = pad(ref, pin), p = parts.find((r) => r.name === ref)!, net = p.nets[pin], L = p.layer
  for (let d = from; d <= 2.0; d += 0.05) { const v = { x: r3(q.x + dir.x * d), y: r3(q.y + dir.y * d) }
    if (viaBlocked(v.x, v.y, net) || B.hits(seg(q, v, w), [L], net, 0.1).length) continue
    ptrace(net, L, [{ x: q.x, y: q.y }, v], w, `${ref}.${pin}`, "via"); return addVia({ name: `V_${ref}_${pin}`, x: v.x, y: v.y, net, d: 0.3, hole: 0.1 }) }
  report.push(`!! ${ref}.${pin} (${net}): no via site along (${dir.x}, ${dir.y})`); return null }
/** vias inside a pad (via-in-pad), as many as fit up to n */
function padVias(ref: string, pin: string, n: number) { const q = pad(ref, pin), p = parts.find((r) => r.name === ref)!, net = p.nets[pin], [x0, x1] = [Math.min(...q.shape.pts.map((t) => t.x)), Math.max(...q.shape.pts.map((t) => t.x))], [y0, y1] = [Math.min(...q.shape.pts.map((t) => t.y)), Math.max(...q.shape.pts.map((t) => t.y))]
  let k = 0; for (let y = y0 + 0.15; y <= y1 - 0.15 + 1e-9 && k < n; y += 0.5) for (let x = x0 + 0.15; x <= x1 - 0.15 + 1e-9 && k < n; x += 0.5) { if (viaBlocked(r3(x), r3(y), net)) continue; addVia({ name: `V_${ref}_${pin}_${k}`, x: r3(x), y: r3(y), net, d: 0.3, hole: 0.1 }); k++ }
  if (!k) report.push(`!! ${ref}.${pin}: no via fits in the pad`); return k }
/** a via at the inner end of a narrow (QFN) pad, half on the pad: 0.14 mm to the neighbouring pads, 0.24 mm from the hole to them */
function innerVia(ref: string, pin: string) { const q = pad(ref, pin), p = parts.find((r) => r.name === ref)!, net = p.nets[pin], side = Math.abs(q.x - p.x) > Math.abs(q.y - p.y), dx = side ? Math.sign(p.x - q.x) : 0, dy = side ? 0 : Math.sign(p.y - q.y), L = 1 // inward along the pad
  // fab rules only (copper >= 0.10 mm, i.e. hole wall >= 0.20 mm from other copper): this via is inside the part's own pad row
  const why = (x: number, y: number) => { if (innerSegs.some((s) => s.net !== net && gap(disc(x, y, 0.15), s) < 0.13)) return "inner trace"; if (vias.some((o) => Math.hypot(o.x - x, o.y - y) < 0.45)) return "via"; const h = B.hits(disc(x, y, 0.15), BOTH, net, 0.1); return h.length ? `${h[0].net} ${h[0].kind}` : null }
  for (const d of [0.18, 0.15, 0.12, 0.2, 0.1]) { const v = { x: r3(q.x + dx / L * d), y: r3(q.y + dy / L * d) }; if (why(v.x, v.y)) continue; return addVia({ name: `V_${ref}_${pin}`, x: v.x, y: v.y, net, d: 0.3, hole: 0.1 }) }
  report.push(`!! ${ref}.${pin} (${net}): no via at the pad's inner end (${why(r3(q.x + dx / L * 0.15), r3(q.y + dy / L * 0.15))})`); return null }
/** a ground pin next to the exposed pad: a trace inward onto it */
const toPad = (ref: string, pin: string, ep: string) => { const q = pad(ref, pin), e = pad(ref, ep), p = parts.find((r) => r.name === ref)!, ax = Math.abs(q.x - p.x) > Math.abs(q.y - p.y), c = ax ? { x: p.x, y: q.y } : { x: q.x, y: p.y }, d = Math.hypot(c.x - q.x, c.y - q.y)
  if (gap(disc(c.x, c.y, 0.001), e.shape) > 0) return innerVia(ref, pin); ptrace("GND", parts.find((r) => r.name === ref)!.layer, [{ x: q.x, y: q.y }, { x: r3(q.x + (c.x - q.x) / d * 1.0), y: r3(q.y + (c.y - q.y) / d * 1.0) }], 0.2, `${ref}.${pin}`, `${ref}.${ep}`) }
const at = (ref: string, pin: string) => { const q = pad(ref, pin); return { x: q.x, y: q.y } }
/** a two-pin netlist part near a point; vias in the pads whose net is a plane */
function near(ref: string, p: Pt, o: { layers?: Layer[]; maxDist?: number; anywhere?: boolean; vias?: number; ok?: (q: Part) => boolean } = {}) { const n = NL[ref], v = Object.entries(n.nets).filter(([, net]) => PLANE.has(net)).map(([pin]) => pin)
  return free(ref, n.part, p, n.nets.pin1, n.nets.pin2, { layers: o.layers ?? ["top", "bottom"], maxDist: o.maxDist ?? 6, viaPins: v, viasPerPad: o.vias ?? 1, anywhere: o.anywhere ?? true, ok: o.ok, step: 0.1 }) }
tick("power")
// TPS65217D on top, east of the processor. Rotation 0: pins 1-12 west side (top to bottom), 13-24 south, 25-36 east, 37-48 north.
const PM = { x: -30.65, y: 13.45 } // on the router grid (x0 + 0.1 i): the 0.4 mm pin pitch then lands on grid lines
placeAt("U_PMIC", PM.x, PM.y, 0)
// exposed pad: a 3 x 3 grid of ground vias
for (const dx of [-1.2, 0, 1.2]) for (const dy of [-1.0, 0, 1.0]) addVia({ name: `V_U_PMIC_EP_${dx}_${dy}`, x: r3(PM.x + dx), y: r3(PM.y + dy), net: "GND", d: 0.3, hole: 0.1 })
// battery pins tied together and left open (case 2)
ptrace("PMIC_BAT", "top", [at("U_PMIC", "pin4"), at("U_PMIC", "pin6")], 0.2, "U_PMIC.pin4", "U_PMIC.pin6")
const SIDE: Record<string, Pt> = { W: { x: -1, y: 0 }, S: { x: 0, y: -1 }, E: { x: 1, y: 0 }, N: { x: 0, y: 1 } }
const sideOf = (pin: number) => pin <= 12 ? "W" : pin <= 24 ? "S" : pin <= 36 ? "E" : "N"
// switch nodes: inductors next to their L pins, wide top-layer traces
placeAt("L_DCDC1", PM.x - 1.3, PM.y - 6.2, 90); placeAt("L_DCDC2", PM.x + 1.9, PM.y - 6.2, 90); placeAt("L_DCDC3", PM.x + 5.0, PM.y - 0.3, 90)
for (const [l, pin, L] of [["LX1", "pin20", "L_DCDC1"], ["LX2", "pin23", "L_DCDC2"], ["LX3", "pin31", "L_DCDC3"]] as const) { const q = pad(L, "pin1")
  if (!maze(l, { ...at("U_PMIC", pin), layer: "top" }, (x, y, ly) => ly === "top" && gap(disc(x, y, 0.001), q.shape) < -0.1, 0.3, { layers: ["top"], from: `U_PMIC.${pin}`, to: `${L}.pin1`, win: 7 })) report.push(`!! ${l}: no switch-node trace`) }
// plane pins of the PMIC: a short stub to a via (the supply pins get the most copper: two vias where they fit)
for (let n = 1; n <= 48; n++) { const net = NL.U_PMIC.nets["pin" + n]; if (!net || !PLANE.has(net)) continue
  if (net === "GND") { toPad("U_PMIC", "pin" + n, "pin49"); continue }
  const save = report.length; if (!stubVia("U_PMIC", "pin" + n, SIDE[sideOf(n)], ["SYS", "VIN5"].includes(net) ? 0.22 : 0.2)) { report.length = save; innerVia("U_PMIC", "pin" + n) } }
// inductor outputs and the converter capacitors
for (const L of ["L_DCDC1", "L_DCDC2", "L_DCDC3"]) padVias(L, "pin2", 3)
for (const [c, l] of [["C_DCDC1", "L_DCDC1"], ["C_DCDC2", "L_DCDC2"], ["C_DCDC3", "L_DCDC3"]]) near(c, at(l, "pin2"), { vias: 2, maxDist: 4 })
for (const [c, pin] of [["C_SYS", "pin7"], ["C_VIN12", "pin21"], ["C_VIN3", "pin32"], ["C_VINLDO", "pin2"], ["C_AC", "pin10"], ["C_LDO1", "pin3"], ["C_LDO2", "pin1"], ["C_LDO3", "pin40"], ["C_LDO4", "pin43"], ["C_INTLDO", "pin48"], ["C_BYPASS", "pin47"]])
  near(c, at("U_PMIC", pin), { vias: c === "C_SYS" || c.startsWith("C_VIN") ? 2 : 1, maxDist: 5 })
for (const [r, pin] of [["R_PB", "pin25"], ["R_GLOBAL_EN", "pin44"], ["R_WAKE", "pin13"], ["R_INT", "pin45"], ["R_PGOOD", "pin26"], ["R_SDA0", "pin27"], ["R_SCL0", "pin28"]]) near(r, at("U_PMIC", pin), { maxDist: 6 })
// 3.3 V and 1.8 V bucks, north of the PMIC. SY8089 rotation 0: EN (+1.2,-0.95), GND (+1.2,0), LX (+1.2,+0.95), IN (-1.2,+0.95), FB (-1.2,-0.95)
for (const [b, y] of [["3V3", 25.6], ["1V8", 21.3]] as const) { const U = `U_${b}`, L = `L_${b}`
  placeAt(U, -33.3, y, 0); placeAt(L, -29.6, y + 0.6, 0)
  padVias(U, "pin2", 1); padVias(L, "pin2", 3)
  if (!maze(`LX_${b}`, { ...at(U, "pin3"), layer: "top" }, (x, yy, ly) => ly === "top" && gap(disc(x, yy, 0.001), pad(L, "pin1").shape) < -0.1, 0.3, { layers: ["top"], from: `${U}.pin3`, to: `${L}.pin1`, win: 5 })) report.push(`!! LX_${b}: no switch-node trace`)
  stubVia(U, "pin4", { x: -1, y: 0 }, 0.3, 0.75)
  near(`C_IN_${b}`, at(U, "pin4"), { vias: 2, maxDist: 4 }); near(`C_OUT_${b}`, at(L, "pin2"), { vias: 2, maxDist: 4 })
  near(`R_FBT_${b}`, at(U, "pin5"), { maxDist: 4 }); near(`R_FBB_${b}`, at(U, "pin5"), { maxDist: 4 }) }
// LAN8720A north of the processor, rotation 270: MDI pins face J1 (north), RMII face the processor (south), crystal pins west
tick("phy")
const PH = { x: -39.0, y: 27.3 }
placeAt("U_PHY", PH.x, PH.y, 270)
for (const dx of [-0.6, 0.6]) for (const dy of [-0.6, 0.6]) addVia({ name: `V_U_PHY_EP_${dx}_${dy}`, x: r3(PH.x + dx), y: r3(PH.y + dy), net: "GND", d: 0.3, hole: 0.1 })
placeAt("Y_PHY", PH.x - 4.45, PH.y + 0.1, 90)
for (const g of ["pin2", "pin4"]) padVias("Y_PHY", g, 1)
for (const n of [1, 9, 19]) { const save = report.length; if (!stubVia("U_PHY", "pin" + n, ({ 1: { x: -1, y: 0 }, 9: { x: 0, y: -1 }, 19: { x: 0, y: 1 } } as any)[n], 0.2)) { report.length = save; innerVia("U_PHY", "pin" + n) } }
for (const [c, p] of [["C_PHY_XI", at("Y_PHY", "pin1")], ["C_PHY_XO", at("Y_PHY", "pin3")], ["C_PHY_1", at("U_PHY", "pin1")], ["C_PHY_2", at("U_PHY", "pin9")], ["C_PHY_3", at("U_PHY", "pin19")], ["C_PHY_BULK", at("U_PHY", "pin19")],
  ["C_PHY_VDDCR1", at("U_PHY", "pin6")], ["C_PHY_VDDCR2", at("U_PHY", "pin6")], ["R_PHY_RBIAS", at("U_PHY", "pin24")], ["R_PHY_LED2", at("U_PHY", "pin2")], ["R_PHY_RST", at("U_PHY", "pin15")], ["R_MDIO", at("U_PHY", "pin12")],
  ["R_ETH_TX_P", at("U_PHY", "pin21")], ["R_ETH_TX_N", at("U_PHY", "pin20")], ["R_ETH_RX_P", at("U_PHY", "pin23")], ["R_ETH_RX_N", at("U_PHY", "pin22")]] as [string, Pt][]) near(c, p, { maxDist: 6 })
// straps and pull-ups next to the processor ball (or the PMIC) of their net
tick("straps")
const ballOf = (net: string) => { const s = signals.find((q) => q.name === net)!; return ball["U1." + s.ball] }
for (let i = 0; i < 16; i++) near(`R_SB${i}`, ballOf(`SYSBOOT${i}`), { maxDist: 12, layers: ["bottom", "top"] })
for (const r of ["R_RPB0", "R_RPB2"]) near(r, at(r === "R_RPB0" ? "R_SB0" : "R_SB2", "pin1"), { maxDist: 8, layers: ["bottom", "top"] })
for (const n of ["SD_CMD", "SD_DAT0", "SD_DAT1", "SD_DAT2", "SD_DAT3", "SD_PWR_ON", "GPIO2_SDA1", "GPIO3_SCL1", "ID_SD", "ID_SC"]) { const r = NETLIST.find((p) => p.part.startsWith("R") && Object.values(p.nets).includes(n) && p.ref !== "R_PGOOD")!.ref; near(r, ballOf(n), { maxDist: 10 }) }
near("R_VBUS", ballOf("USB0_VBUS"), { maxDist: 10 })
for (const p of NETLIST) if (!parts.some((q) => q.name === p.ref)) report.push(`!! ${p.ref} (${p.part}) not placed`)
// ---------- nets for the router: every non-plane net of the circuit with all its terminals ----------
// (switch nodes and the PMIC battery tie are drawn above; they are not routed again)
function innerBall(b: string) { return /^[RTUV][1-6]$/.test(b) || ["B5", "C5", "C6"].includes(b) }
const done = new Set(["LX1", "LX2", "LX3", "LX_3V3", "LX_1V8", "PMIC_BAT"])
type Term = { ref: string; x: number; y: number; layer: Layer; shape: { pts: Pt[]; r: number }; kind: "ball" | "pad" | "pin" }
const netTerms = new Map<string, Term[]>()
const addTerm = (net: string, t: Term) => { if (!net || PLANE.has(net) || done.has(net) || net.startsWith("NC")) return; if (!netTerms.has(net)) netTerms.set(net, []); netTerms.get(net)!.push(t) }
for (const s of signals) { const b = ball["U1." + s.ball]; addTerm(s.name, { ref: "U1." + s.ball, x: b.x, y: b.y, layer: "top", shape: disc(b.x, b.y, b.r), kind: "ball" }) }
for (const n of NETLIST) { const p = parts.find((q) => q.name === n.ref); if (!p) continue; for (const q of padsOf(p)) addTerm(p.nets[q.pin], { ref: `${p.name}.${q.pin}`, x: r3(q.x), y: r3(q.y), layer: p.layer, shape: q.shape, kind: "pad" }) }
for (const p of pins) { const it = B.items.find((i) => i.ref === `${p.conn}.${p.pin}`)!; addTerm(p.role, { ref: `${p.conn}.${p.pin}`, x: p.x, y: p.y, layer: "bottom", shape: { pts: it.pts, r: it.r }, kind: "pin" }) }
const nets = [...netTerms].map(([name, terms]) => ({ name, terms, inner: terms.some((t) => t.kind === "ball" && innerBall(t.ref.slice(3))) }))
for (const n of nets) if (n.terms.length < 2) report.push(`!! net ${n.name} has ${n.terms.length} terminal`)
report.push(`router nets: ${nets.length} (${nets.filter((n) => n.inner).length} start at boxed-in balls), ${nets.reduce((s, n) => s + n.terms.length, 0)} terminals`)

// ---------- ground stitching next to DDR layer changes ----------
{ let added = 0, far = 0; const sv = B.items.filter((i, n, a) => i.kind === "ddrvia" && a.findIndex((j) => j.kind === "ddrvia" && Math.hypot(j.pts[0].x - i.pts[0].x, j.pts[0].y - i.pts[0].y) < 0.01) === n)
  for (const s of sv) { const c = s.pts[0]; if (vias.some((v) => v.net === "GND" && Math.hypot(v.x - c.x, v.y - c.y) <= 1.5)) continue
    let best: Pt | null = null, bd = 1e9
    for (let dx = -1.5; dx <= 1.5; dx += 0.1) for (let dy = -1.5; dy <= 1.5; dy += 0.1) { const d = Math.hypot(dx, dy); if (d > 1.5 || d < 0.5 || d >= bd) continue
      const p = { x: r3(c.x + dx), y: r3(c.y + dy) }; if (B.hits(disc(p.x, p.y, 0.15), BOTH, "GND", 0.13).length || viaBlocked(p.x, p.y, "GND")) continue
      if (underPart(p.x, p.y, 0.15) || escapeZone(p.x, p.y)) continue
      best = p; bd = d }
    if (best) { addVia({ name: `V_STITCH_${++added}`, x: best.x, y: best.y, net: "GND", d: 0.3, hole: 0.1 }) } else far++ }
  report.push(`ground stitching: ${added} vias added; ${far} DDR vias still have no ground via within 1.5 mm`) }

// ---------- top-up after the handheld signals are routed (TOPUP=1): what did not fit clear of the signal escape goes into the space the routes left ----------
if (process.env.TOPUP) { const routes = await Bun.file(import.meta.dir + "/routes.json").json(); let nseg = 0
  for (const [name, r] of Object.entries(routes.nets) as any) { for (const g of r.segs) for (let i = 0; i + 1 < g.pts.length; i++) { if (g.layer === "top" || g.layer === "bottom") B.add({ ...seg(g.pts[i], g.pts[i + 1], 0.1), layers: [g.layer], net: name, kind: "trace" }); else innerSegs.push({ ...seg(g.pts[i], g.pts[i + 1], 0.1), layers: [], net: name, kind: "trace" }); nseg++ }
    for (const v of r.vias) B.add({ ...disc(v.x, v.y, v.d / 2), layers: BOTH, net: name, kind: "via" })
    const pin = pins.find((p) => p.conn === r.conn && p.pin === r.pin)!; B.items.find((i) => i.ref === `${r.conn}.${r.pin}`)!.net = name; pin.role = name }
  // a high-speed DDR bypass capacitor must sit over solid VDDS_DDR copper (layer 3 west of the split, not the 3V3 corner of row P),
  // or its VDDS_DDR via reaches the processor's column-5 VDDS_DDR balls only through thin links around the other supplies
  // the capacitor's VDDS_DDR via must land in VDDS_DDR copper on layer 3 (same regions as planes.ts, 0.35 mm inside them)
  const inVdds = (x: number, y: number, m = 0.35) => (x < -46.4 - m && !(x > -49.1 - m && y > 10.9 - m && y < 12.0 + m)) || (x < -37.6 - m && (y > 19.25 + m || y < 10.15 - m)) || (x < -41.6 - m && y > 12.0 + m && y < 18.35 - m)
  const onDdrPlane = (p: Part | Pt) => "nets" in p ? padsOf(p as Part).filter((q) => (p as Part).nets[q.pin] === "VDDS_DDR").every((q) => inVdds(q.x, q.y)) : inVdds(p.x, p.y)
  const dist = (p: Pt) => Math.max(nearestBall("U1", "VDDS_DDR", p), nearestBall("U1", "GND", p)), hs = () => parts.filter((p) => p.name.startsWith("C_HS_CPU"))
  { // under the processor: 0201 from a ground ball via to a new VDDS_DDR via between the balls, inside the layer-3 VDDS_DDR interior
    let u = hs().filter((p) => p.name.startsWith("C_HS_CPU_U")).length
    const inner = (v: Pt) => inVdds(v.x, v.y)
    for (const g of vias.filter((v) => v.ball?.startsWith("U1.") && v.net === "GND" && inner(v)).sort((a, b) => nearestBall("U1", "VDDS_DDR", a) - nearestBall("U1", "VDDS_DDR", b))) { if (hs().length >= 20) break
      const name = `C_HS_CPU_U${u + 1}`, q = anchored(name, "C100N_0201", g, "GND", "VDDS_DDR"); if (!q) continue
      const nv = vias.find((v) => v.name === `V_${name}_2`), ok = dist(q) <= 10.16 - 0.4 && (!nv || inner(nv))
      if (ok) u++; else uncommit(name) }
    report.push(`top-up: ${u} high-speed DDR bypass capacitors under the processor on ground ball vias`) }
  for (let n = hs().length; n < 20; n++) if (!free(`C_HS_CPU_T${n + 1}`, "C100N_0402", { x: -48.4, y: 15.55 }, "VDDS_DDR", "GND", { anywhere: true, maxDist: 12.5, step: 0.1, ok: (p) => dist(p) <= 10.16 - 0.4 && onDdrPlane(p), score: dist })) break
  for (let n = hs().length; n < 20; n++) if (!free(`C_HS_CPU_T${n + 1}`, "C100N_0201", { x: -48.4, y: 15.55 }, "VDDS_DDR", "GND", { anywhere: true, maxDist: 12.5, step: 0.05, ok: (p) => dist(p) <= 10.16 - 0.4 && onDdrPlane(p), score: dist })) break
  { // TI Table 7-65 note 7: an additional HS bypass capacitor may share a capacitor's two connection vias when it sits on the
    // opposite side; top-side parts stay >= 1.0 mm (+ half their length) from both BGA bodies (JLCPCB assembly)
    const clearOfBga = (x: number, y: number) => [[-51.3, -38.3, 8.65, 21.65], [-77.1, -62.9, 10.65, 19.65]].every(([x0, x1, y0, y1]) => Math.hypot(Math.max(x0 - x, 0, x - x1), Math.max(y0 - y, 0, y - y1)) >= 1.0 + 0.6)
    let k = 0
    for (const h of hs().filter((h) => h.layer === "bottom").sort((a, b) => dist(a) - dist(b))) { if (hs().length >= 20) break
      const vv = vias.filter((v) => v.name.startsWith(`V_${h.name}_`) && v.net === "VDDS_DDR"); if (!vv.length || !clearOfBga(h.x, h.y) || !onDdrPlane(h)) continue
      for (const part of ["C100N_0201", "C100N_0402"]) { const q = anchored(`C_HS_CPU_S${++k}`, part, vv[0], "VDDS_DDR", "GND", "top", true); if (q) { report.push(`top-up: ${q.name} on top, sharing the vias of ${h.name} (note 7)`); break } } } }
  report.push(`top-up: DDR high-speed bypass CPU now ${hs().length}/20, worst distance ${Math.max(...hs().map(dist)).toFixed(2)} mm (limit 10.16)`)
  if (!parts.some((p) => p.name === "C_VREF_CPU")) { const v = vias.find((v) => v.ball === "U1.J4")!, p = free("C_VREF_CPU", "C100N_0201", v, "DDR_VREF", "GND", { anywhere: true, maxDist: 14, step: 0.05 }) ?? free("C_VREF_CPU", "C100N_0402", v, "DDR_VREF", "GND", { anywhere: true, maxDist: 14, step: 0.15 }); if (p) report.push(`top-up: C_VREF_CPU ${Math.hypot(p.x - v.x, p.y - v.y).toFixed(2)} mm from the VREF via of U1.J4`) }
  free("C_BULK_1V8_2", "C10U_0603", U1("D10"), "VDD_1V8", "GND", { anywhere: true, maxDist: 8, viasPerPad: 2, step: 0.15 })
  for (const [net, near, n] of [["VDD_MPU", U1("G13"), 2], ["VDD_1V8", U1("H15"), 2], ["VDD_1V8", U1("R11"), 1], ["VDD_3V3", U1("P12"), 2], ["VDD_3V3", U1("E12"), 1]] as const) for (let i = 0; i < n; i++) { const name = `C_X_${net.slice(4)}_${parts.filter((p) => p.name.startsWith("C_X_" + net.slice(4))).length + 1}`
    const p = free(name, "C100N_0402", near, net, "GND", { anywhere: true, maxDist: 6, step: 0.15 }); if (p) report.push(`top-up: ${name} (${net}) ${Math.hypot(p.x - near.x, p.y - near.y).toFixed(2)} mm from its ball`) } }

// ---------- checks and output ----------
const holes = HOLES
for (const h of holes) { const hit = B.hits(disc(h.x, h.y, h.d / 2), BOTH, "HOLE", 0.4); if (hit.length) report.push(`mounting hole at (${h.x}, ${h.y}) hits ${hit[0].net} ${hit[0].kind}`) }
const unassigned = Object.keys(ball).filter((k) => !ballNet[k])
report.push(`balls without a net (left open): U1 ${unassigned.filter((k) => k.startsWith("U1.")).length}, U_DDR ${unassigned.filter((k) => k.startsWith("U_DDR.")).map((k) => k.slice(6)).join(" ")}`)
for (const [k, n] of Object.entries(ballNet)) if (PLANE.has(n) && !vias.some((v) => v.ball === k)) report.push(`!! ${k} (${n}) has no via`)
const REQUIRED = ["R_VTP", "R_ZQ", "R_VREF_TOP", "R_VREF_BOT", "C_VREF_DIV", "C_VREF_DQ", "C_VREF_CA", "C_VBB_MPU", "C_SRAM_CORE", "C_SRAM_MPU", "C_CAP_RTC", "C_VDDS_RTC", "Y_OSC0", "C_OSC0_IN", "C_OSC0_OUT", "J1", "J2", "C_BULK_DDR_CPU1", "C_BULK_DDR_CPU2", "C_BULK_DDR_RAM1", "C_BULK_DDR_RAM2", ...(process.env.TOPUP ? ["C_VREF_CPU"] : [])]
const missing = REQUIRED.filter((n) => !parts.some((p) => p.name === n)); if (missing.length) report.push("!! REQUIRED PARTS NOT PLACED: " + missing.join(" "))
console.log(report.join("\n")); console.log(`${parts.length} parts, ${vias.length} vias, ${signals.length} signals, pins: ${pins.filter((p) => p.role === "SIG").length} free signal pins, ${pins.filter((p) => p.role === "GND").length} ground pins`)
await Bun.write(import.meta.dir + "/plan.json", JSON.stringify({ edge: EDGE, holes, required: REQUIRED, ddrInner, innerNets, planeNets: [...PLANE], ballNet, ball, signals, parts, vias, links, paths, pins, unassigned, nets }, null, 1))
await Bun.write(import.meta.dir + "/plan-items.json", JSON.stringify({ items: B.items, bodies }))
if (missing.length) process.exit(1)
