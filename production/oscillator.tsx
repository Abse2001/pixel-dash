import { S3B24_000000F1210F30 as Crystal } from "../imports/S3B24_000000F1210F30"
import { A_0402CG150F500NT as LoadCap } from "../imports/A_0402CG150F500NT"
import { A_0603WAF0000T5E as SeriesLink } from "../imports/A_0603WAF0000T5E"
import { RTT021004BTH as Bias } from "../imports/RTT021004BTH"

// TI SPRS717L Fig 6-9. Default series link is fitted and optional bias is DNP.
export function Oscillator() {
  return <>
    <Crystal name="Y_OSC0" loadCapacitance="12pF" pcbX={-44.1} pcbY={4.65}/>
    <LoadCap name="C_OSC0_IN" pcbX={-47.2} pcbY={3.8} pcbRotation={90}/>
    <LoadCap name="C_OSC0_OUT" pcbX={-41.0} pcbY={4.5} pcbRotation={-90}/>
    <SeriesLink name="R_OSC0_DRIVE" pcbX={-40.05} pcbY={6.4}/>
    <Bias name="R_OSC0_BIAS" pcbX={-47.25} pcbY={6.1} doNotPlace/>
    <trace name="OSC0_INPUT" from=".U1 > .V10" to=".Y_OSC0 > .pin1" thickness={0.15}
      pcbPath={[{ x: 0.4, y: -8.85 }, { x: 0.5, y: -9 }, { x: 0.5, y: -10.35 }]}/>
    <trace name="OSC0_OUTPUT" from=".U1 > .U11" to=".R_OSC0_DRIVE > .pin1" thickness={0.15}
      pcbPath={[{ x: 1.95, y: -5.6 }, { x: 2.25, y: -5.7 }, { x: 2.4, y: -5.95 }, { x: 2.4, y: -6.85 }, { x: 2.55, y: -7.1 }]}/>
    <trace name="OSC0_DRIVE" from=".R_OSC0_DRIVE > .pin2" to=".Y_OSC0 > .pin3" thickness={0.15}
      pcbPath={[{ x: -0.35, y: -0.65 }]}/>
    <trace name="OSC0_IN_LOAD" from=".Y_OSC0 > .pin1" to=".C_OSC0_IN > .pin1" thickness={0.15}
      pcbStraightLine/>
    <trace name="OSC0_OUT_LOAD" from=".Y_OSC0 > .pin3" to=".C_OSC0_OUT > .pin1" thickness={0.15}
      pcbStraightLine/>
    <trace name="OSC0_BIAS_IN" from=".R_OSC0_BIAS > .pin1" to=".U1 > .V10" thickness={0.15}
      pcbPath={[{ x: 0.1, y: 0.5 }]}/>
    <trace name="OSC0_BIAS_OUT" from=".R_OSC0_BIAS > .pin2" to=".U1 > .U11" thickness={0.15}
      pcbPath={[{ x: -0.05, y: -0.45 }, { x: -0.7, y: -0.5 }, { x: -0.8, y: -0.45 }, { x: -0.9, y: -0.35 }, { x: -0.9, y: 0.35 }, { x: 0.45, y: 1.6 }, { x: 1.5, y: 1.95 }, { x: 1.65, y: 2.2 }, { x: 1.75, y: 2.5 }, { x: 2, y: 2.65 }, { x: 2.9, y: 2.65 }]}/>
    {[
      { name: "VSS", pin: ".U1 > .V11", x: -43.600104, y: 8.349912 },
      { name: "CIN", pin: ".C_OSC0_IN > .pin2", x: -47.2, y: 4.220116 },
      { name: "COUT", pin: ".C_OSC0_OUT > .pin2", x: -41, y: 4.18 },
      { name: "CASE2", pin: ".Y_OSC0 > .pin2", x: -42.999926, y: 4.2 },
      { name: "CASE4", pin: ".Y_OSC0 > .pin4", x: -45.200074, y: 5.500011 },
    ].map(({name, pin, x, y}) => (
      <via key={name} name={"M_OSC0_" + name} pcbX={x} pcbY={y}
        fromLayer="top" toLayer="inner1" outerDiameter={0.28}
        holeDiameter={0.125} connectsTo={[pin, "net.GND"]}/>
    ))}
  </>
}
