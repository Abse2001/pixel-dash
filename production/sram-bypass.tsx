import { Fragment } from "react"
import { CL10A105KB8NNNC } from "../imports/CL10A105KB8NNNC"
import { CL10A106KP8NNNC } from "../imports/CL10A106KP8NNNC"

// AM3354 SPRS717L Tables 5-14 and 5-15, ZCZ ballout.
const capacitors = [
  { name: "C_VBB_MPU", ball: "C10", x: -40.799950, y: 24.949912, rotation: 90, input: false },
  { name: "C_SRAM_CORE", ball: "D9", x: -45.050050, y: 26.400066, rotation: 90, input: false },
  { name: "C_SRAM_MPU", ball: "D11", x: -42.900080, y: 25.700042, rotation: 0, input: false },
  { name: "C_SRAM_MPU_IN", ball: "D10", x: -46.499950, y: 27.000066, rotation: 90, input: true },
  { name: "C_SRAM_CORE_IN", ball: "E9", x: -48.050050, y: 27.399966, rotation: 90, input: true },
]

export function SramBypass() {
  return <>{capacitors.map(({ name, ball, x, y, rotation, input }) => {
    const Capacitor = input ? CL10A106KP8NNNC : CL10A105KB8NNNC
    const groundX = x + (rotation === 0 ? 0.700024 : 0)
    const groundY = y + (rotation === 90 ? 0.700024 : 0)
    return <Fragment key={ball}>
      <Capacitor name={name} pcbX={x} pcbY={y} pcbRotation={rotation}/>
      <trace from={`.U1 > .${ball}`} to={`.${name} > .pin1`} name={`LOCAL_BYPASS_${ball}`}/>
      <trace from={`.${name} > .pin2`} to="net.GND"/>
      <via name={`V_RETURN_${ball}`} pcbX={groundX} pcbY={groundY}
        fromLayer="top" toLayer="inner1" outerDiameter={0.28} holeDiameter={0.125}
        connectsTo={[`.${name} > .pin2`, "net.GND"]}/>
    </Fragment>
  })}</>
}
