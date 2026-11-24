// Fabrication outputs for the module from module/dist/module.circuit.json and module/plan.json:
// Gerbers + drills (circuit-json-to-gerber), BOM and pick-and-place in JLCPCB's CSV layout.
import { convertCircuitJsonToGerberFiles } from "circuit-json-to-gerber"
import { mkdirSync, rmSync } from "node:fs"
const M = import.meta.dir, OUT = M + "/fab"
const cj = await Bun.file(M + "/dist/module.circuit.json").json(), plan = await Bun.file(M + "/plan.json").json()
rmSync(OUT + "/gerbers", { recursive: true, force: true }); mkdirSync(OUT + "/gerbers", { recursive: true })
const files = convertCircuitJsonToGerberFiles(cj)
for (const [name, text] of Object.entries(files)) await Bun.write(`${OUT}/gerbers/${name}`, text)
console.log("gerber files:", Object.entries(files).map(([n, t]) => `${n} (${(t.length / 1024).toFixed(0)}k)`).join(", "))
const INFO: Record<string, [string, string, string]> = { // value, package, LCSC part
  C100N_0201: ["100nF", "0201", "C76939"], C100N_0402: ["100nF", "0402", "C1525"], C1U_0402: ["1uF", "0402", "C52923"], C10U_0603: ["10uF", "0603", "C19702"], C15P_0402: ["15pF", "0402", "C285151"],
  R240_0201: ["240R 1%", "0201", ""], R49R9_0402: ["49.9R 1%", "0402", ""], R1K_0402: ["1k 1%", "0402", ""], XTAL_24M: ["24MHz 12pF", "SMD3225-4P", ""], DF40_100: ["DF40C-100DS-0.4V(51)", "DF40C-100DS", "C597931"] }
// LCSC numbers of the parts imported earlier come from their import files
const imp: Record<string, string> = { R240_0201: "../am3354/imports/RC0201FR_07240RL.tsx", R49R9_0402: "../am3354/imports/A_0402WGF499JTCE.tsx", R1K_0402: "../imports/A_0402WGF1001TCE.tsx", XTAL_24M: "../imports/S3B24_000000F1210F30.tsx", C100N_0201: "../am3354/imports/TMK063ABJ104KP_F.tsx", C10U_0603: "../imports/CL10A106KP8NNNC.tsx", C100N_0402: "../imports/CL05B104KO5NNNC.tsx", C15P_0402: "../imports/A_0402CG150F500NT.tsx" }
for (const [k, f] of Object.entries(imp)) { const m = (await Bun.file(`${M}/${f}`).text()).match(/jlcpcb"?\s*:\s*\[\s*"(C\d+)"/); if (m) INFO[k][2] = m[1] }
const E = plan.edge, CX = (E.x0 + E.x1) / 2, CY = (E.y0 + E.y1) / 2
const rows = [{ name: "U1", part: "CPU", x: -44.8, y: 15.15, rot: 0, layer: "top" }, { name: "U_DDR", part: "RAM", x: -70, y: 15.15, rot: 270, layer: "top" }, ...plan.parts]
INFO.CPU = ["AM3354BZCZD80", "NFBGA-324 15x15 0.8mm", "C128768"]; INFO.RAM = ["MT41K512M16VRP-107 IT:P", "FBGA-96 9x14 0.8mm", "C2831669"]
const groups = new Map<string, string[]>(); for (const r of rows) groups.set(r.part, [...(groups.get(r.part) ?? []), r.name])
await Bun.write(OUT + "/bom.csv", "Comment,Designator,Footprint,LCSC Part #\n" + [...groups].map(([p, d]) => `"${INFO[p][0]}","${d.join(",")}","${INFO[p][1]}",${INFO[p][2]}`).join("\n") + "\n")
await Bun.write(OUT + "/cpl.csv", "Designator,Mid X,Mid Y,Layer,Rotation\n" + rows.map((r) => `${r.name},${(r.x - CX).toFixed(4)}mm,${(r.y - CY).toFixed(4)}mm,${r.layer === "top" ? "Top" : "Bottom"},${((r.rot % 360) + 360) % 360}`).join("\n") + "\n")
console.log(`bom: ${groups.size} lines, ${rows.length} parts (${rows.filter((r) => r.layer === "top").length} top, ${rows.filter((r) => r.layer !== "top").length} bottom)`); console.log([...groups].map(([p, d]) => `${INFO[p][0]} x${d.length} ${INFO[p][2] || "NO LCSC#"}`).join("; "))

// connector pin map (positions in board coordinates, origin at the board centre, seen from the top side)
const routes = await Bun.file(M + "/routes.json").json()
const note: Record<string, string> = { SIG: "spare (not connected)", GND: "ground" }
await Bun.write(OUT + "/pinmap.csv", "Connector,Pin,Row,Net,CPU ball,X mm,Y mm,Trace mm\n" + (plan.pins as any[]).sort((a, b) => a.conn.localeCompare(b.conn) || +a.pin.slice(3) - +b.pin.slice(3)).map((p) => { const r = routes.nets[p.role]
  return `${p.conn},${p.pin.slice(3)},${p.row},${p.role === "SIG" ? "NC" : p.role},${r ? r.ball : ""},${(p.x - CX).toFixed(2)},${(p.y - CY).toFixed(2)},${r ? r.length : ""}` }).join("\n") + "\n")
const used = (plan.pins as any[]).filter((p) => routes.nets[p.role]).length
console.log(`pinmap: ${plan.pins.length} pins, ${used} signals, ${(plan.pins as any[]).filter((p) => p.role === "GND").length} ground, ${(plan.pins as any[]).filter((p) => p.role === "SIG").length} spare`)
