// Hirose DF40C-100DS-0.4V(51): 100-pin 0.4 mm board-to-board receptacle (JLCPCB C597931, mates with DF40C-100DP, C531031).
// Land pattern from the LCSC footprint: 0.2 x 0.7 mm pads, two rows 3.2 mm apart.
import type { ChipProps } from "@tscircuit/props"
import pads from "./df40-pads.json"

export const DF40C_100DS = (props: ChipProps) => (
  <chip
    manufacturerPartNumber="DF40C-100DS-0.4V(51)"
    supplierPartNumbers={{ jlcpcb: ["C597931"] }}
    footprint={
      <footprint>
        {Object.entries(pads as Record<string, { x: number; y: number }>).map(([pin, p]) => (
          <smtpad key={pin} portHints={["pin" + pin]} pcbX={p.x} pcbY={p.y} width={0.2} height={0.7} shape="rect" />
        ))}
        <silkscreenpath route={[{ x: -11.3, y: -1.69 }, { x: 11.3, y: -1.69 }, { x: 11.3, y: 1.69 }, { x: -11.3, y: 1.69 }, { x: -11.3, y: -1.69 }]} />
        <courtyardoutline outline={[{ x: -11.55, y: -2.2 }, { x: 11.55, y: -2.2 }, { x: 11.55, y: 2.2 }, { x: -11.55, y: 2.2 }, { x: -11.55, y: -2.2 }]} />
      </footprint>
    }
    {...props}
  />
)
