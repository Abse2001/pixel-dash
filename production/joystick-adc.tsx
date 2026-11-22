import { ADS1115IDGSR } from "../imports/ADS1115IDGSR"
import { CL05B104KO5NNNC } from "../imports/CL05B104KO5NNNC"

export function JoystickAdc() {
  return <>
    <ADS1115IDGSR name="U_JOY_ADC" pcbX={-2.5} pcbY={15.75} />
    <CL05B104KO5NNNC name="C_JOY_ADC" pcbX={-2.079884} pcbY={19.57}/>
    <trace from=".U_JOY_ADC > .ADDR" to="net.GND"/>
    <trace from=".U_JOY_ADC > .GND" to="net.GND"/>
    <trace from=".U_JOY_ADC > .VDD" to=".C_JOY_ADC > .pin1" thickness={0.20} pcbStraightLine/>
    <trace from=".C_JOY_ADC > .pin1" to="net.VDD_IO_3V3_SEQ"/>
    <trace from=".C_JOY_ADC > .pin2" to="net.GND"/>
    <trace from=".U_JOY_ADC > .SCL" to=".U_PMIC > .SCL"/>
    <trace from=".U_JOY_ADC > .SDA" to=".U_PMIC > .SDA"/>
    <via name="V_JOY_ADC_GND" pcbX={-2.5} pcbY={13.640022}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28}
      connectsTo={[".U_JOY_ADC > .GND", "net.GND"]}/>
    <via name="V_JOY_ADC_ADDR" pcbX={-3.499998} pcbY={13.640022}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28}
      connectsTo={[".U_JOY_ADC > .ADDR", "net.GND"]}/>
    <via name="V_JOY_ADC_RETURN" pcbX={-1.659768} pcbY={19.57}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28}
      connectsTo={[".C_JOY_ADC > .pin2", "net.GND"]}/>
  </>
}
