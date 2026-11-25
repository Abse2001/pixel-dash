// Renders every part type of the CM4 module once (top side, rotation 0, at the origin) and writes the pad geometry
// tscircuit produces for it: design/pads.json { PART: { pads: [{pin, x, y, w, h}], body: [w, h] } }.
// plan.ts places parts with these pads, check.ts compares the rendered board against them.
import { Circuit } from "@tscircuit/core"
import { TPS65217DRSLR } from "../imports/TPS65217DRSLR"
import { LAN8720A_CP_TR } from "../imports/LAN8720A_CP_TR"
import { SY8089A1AAC } from "../imports/SY8089A1AAC"
import { WIP201610P_2R2ML } from "../imports/WIP201610P_2R2ML"
import { K3A250001210 } from "../imports/K3A250001210"
import { cm4HeaderFootprint, PMIC_FP } from "../parts"

const items: Record<string, any> = {
  PMIC: <TPS65217DRSLR name="U" footprint={PMIC_FP} />,
  PHY: <LAN8720A_CP_TR name="U" />,
  BUCK: <SY8089A1AAC name="U" />,
  L2U2: <WIP201610P_2R2ML name="U" />,
  XTAL_25M: <K3A250001210 name="U" />,
  CM4_HDR: <chip name="U" footprint={cm4HeaderFootprint()} />,
  R0402: <resistor name="U" resistance="10k" footprint="0402" />,
  C0402: <capacitor name="U" capacitance="100nF" footprint="0402" />,
  C0603: <capacitor name="U" capacitance="10uF" footprint="0603" />,
  C0805: <capacitor name="U" capacitance="22uF" footprint="0805" />,
}
const out: Record<string, any> = {}
for (const [k, el] of Object.entries(items)) {
  const c = new Circuit()
  c.add(<board width={30} height={30} routingDisabled>{el}</board>)
  await c.renderUntilSettled()
  const cj: any[] = c.getCircuitJson()
  const sp = new Map(cj.filter((e) => e.type === "source_port").map((e) => [e.source_port_id, e]))
  const pp = new Map(cj.filter((e) => e.type === "pcb_port").map((e) => [e.pcb_port_id, sp.get(e.source_port_id)]))
  const pads = cj.filter((e) => e.type === "pcb_smtpad").map((p) => { const port: any = pp.get(p.pcb_port_id); const pin = (port?.port_hints ?? []).find((h: string) => /^pin\d+$/.test(h)) ?? port?.name
    const turned = Math.round(((p.ccw_rotation ?? 0) % 180 + 180) % 180) === 90, w = p.width ?? 2 * p.radius, h = p.height ?? 2 * p.radius // tscircuit reports rotated pads with their unrotated size
    return { pin, x: +p.x.toFixed(4), y: +p.y.toFixed(4), w: +(turned ? h : w).toFixed(4), h: +(turned ? w : h).toFixed(4) } })
  const holes = cj.filter((e) => e.type === "pcb_plated_hole" || e.type === "pcb_hole").length
  const xs = pads.flatMap((p) => [p.x - p.w / 2, p.x + p.w / 2]), ys = pads.flatMap((p) => [p.y - p.h / 2, p.y + p.h / 2])
  out[k] = { pads, body: [+(Math.max(...xs) - Math.min(...xs)).toFixed(3), +(Math.max(...ys) - Math.min(...ys)).toFixed(3)], holes }
  console.log(k, pads.length, "pads", holes, "holes", out[k].body)
}
await Bun.write(import.meta.dir + "/pads.json", JSON.stringify(out, null, 1))
