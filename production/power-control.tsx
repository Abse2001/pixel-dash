import { CL10A105KB8NNNC as HoldUpCapacitor } from "../imports/CL10A105KB8NNNC"
import { SKRTLAE010 } from "../imports/SKRTLAE010"
import { TPS65218D0PHPR } from "../imports/TPS65218D0PHPR"
import { A_0603WAF1003T5E as Pull100k } from "../imports/A_0603WAF1003T5E"
import { A_0402WGF1002TCE as Pull10k } from "../imports/A_0402WGF1002TCE"

import { RT0402BRD0712K1L as DdrSelect } from "../imports/RT0402BRD0712K1L"
import processorBalls from "../am3354/processor-balls.json"
import { FRC0402J222_TS as I2cPullup } from "../imports/FRC0402J222_TS"

// 0.6 mm pitch under the exposed pad. Omitted sites clear the retained bottom VBUS trace.
const thermalColumns = [
  [-3, 2, 3], [-3, -2, 3], [-3, -2, -1], [-3, -2, -1, 0],
  [-3, -2, -1, 0, 1], [-3, -2, -1, 2], [-3, 0, 3],
]

export function PowerControl() {
  return <>
    <TPS65218D0PHPR name="U_PMIC" pcbX={-20.5} pcbY={25}/>
    <SKRTLAE010 name="SW_POWER" pcbX={-25.35} pcbY={38.85} pcbRotation={180}
      internallyConnectedPins={[["pin1","pin3"]]}/>
    <Pull100k name="R_POWER_PB" pcbX={-25.35} pcbY={35.9}/>
    <Pull100k name="R_PMIC_WAKE" pcbX={-28} pcbY={25}/>
    <Pull10k name="R_PMIC_IRQ" pcbX={-27} pcbY={27}/>
    <net name="VSYS"/><net name="VDDS_RTC_1V8"/>
    <trace name="POWER_KEY" from=".U_PMIC > .PB" to=".SW_POWER > .pin2" thickness={0.15}
      pcbPath={[{x:-5.05,y:-0.60},{x:-5.20,y:-0.45},{x:-5.20,y:2.35}]}/>
    <trace name="POWER_KEY_BIAS" from=".SW_POWER > .pin2" to=".R_POWER_PB > .pin1" thickness={0.15} pcbStraightLine/>
    <trace from=".R_POWER_PB > .pin2" to="net.VSYS"/>
    {[[1, -24.125], [3, -26.575]].map(([pin, x]) => (
      <>
        <via name={`V_POWER_KEY_GND_${pin}`} pcbX={x} pcbY={36.75} fromLayer="top" toLayer="inner1"
          holeDiameter={0.125} outerDiameter={0.28} connectsTo="net.GND"/>
        <trace from={`.SW_POWER > .pin${pin}`} to={`.V_POWER_KEY_GND_${pin} > .top`}
          thickness={0.2} pcbStraightLine/>
        <trace from={`.SW_POWER > .pin${pin}`} to="net.GND"/>
      </>
    ))}
    <trace name="PMIC_INPUT" from=".U_PMIC > .IN_BIAS" to="net.VSYS"/>
    <trace name="RTC_POWER_HOLD" from=".U1 > .C6" to=".U_PMIC > .PWR_EN"/>
    <trace name="RTC_WAKE" from=".U_PMIC > .nWAKEUP" to=".U1 > .C5"/>
    <trace from=".R_PMIC_WAKE > .pin1" to=".U_PMIC > .nWAKEUP"/>
    <trace from=".R_PMIC_WAKE > .pin2" to="net.VDDS_RTC_1V8"/>
    <trace name="PMIC_IRQ" from=".U_PMIC > .nINT" to=".U1 > .T14"/>
    <trace from=".R_PMIC_IRQ > .pin1" to=".U_PMIC > .nINT"/>
    <trace from=".R_PMIC_IRQ > .pin2" to="net.VDD_IO_3V3_SEQ"/>
    <trace name="PMIC_I2C_SCL" from=".U_PMIC > .SCL" to=".U1 > .C16"/>
    <trace name="PMIC_I2C_SDA" from=".U_PMIC > .SDA" to=".U1 > .C17"/>
    <I2cPullup name="R_PMIC_SCL" pcbX={-21.25} pcbY={19.03}/>
    <I2cPullup name="R_PMIC_SDA" pcbX={-23.75} pcbY={19.03} pcbRotation={180}/>
    <trace from=".U_PMIC > .SCL" to=".R_PMIC_SCL > .pin1" thickness={0.15} pcbPath={[{x:-1.75006,y:-5.1}]}/>
    <trace from=".U_PMIC > .SDA" to=".R_PMIC_SDA > .pin1" thickness={0.15} pcbPath={[{x:-2.249932,y:-5.1}]}/>
    <trace from=".R_PMIC_SCL > .pin2" to=".R_PMIC_SDA > .pin2" thickness={0.2}
      pcbPath={[{x:0.432816,y:-0.63},{x:-2.932816,y:-0.63}]}/>
    <trace from=".R_PMIC_SDA > .pin2" to="net.VDD_IO_3V3_SEQ"/>
    {Object.entries(processorBalls).filter(([, supply]) => supply === "VDDSHV6").map(([ball]) => (
      <trace key={ball} from={".U1 > ." + ball} to="net.VDD_IO_3V3_SEQ"/>
    ))}
    <DdrSelect name="R_DDR_VSEL" pcbX={-14.4} pcbY={24.25}/>
    <trace from=".U_PMIC > .DC34_SEL" to=".R_DDR_VSEL > .pin1" pcbPath={[{x:4.8,y:-0.750062}]} thickness={0.15}/>
    <trace from=".R_DDR_VSEL > .pin2" to="net.GND"/>
    <via name="V_DDR_VSEL_GND" pcbX={-13.967184} pcbY={24.25} fromLayer="top" toLayer="inner1"
      holeDiameter={0.125} outerDiameter={0.28} connectsTo={[".R_DDR_VSEL > .pin2", "net.GND"]}/>
    {thermalColumns.flatMap((columns, row) => columns.map(column => (
      <via key={row + "_" + column} name={`V_PMIC_EP_${row}_${column + 3}`}
        pcbX={-20.5 + column * 0.6} pcbY={25 + (row - 3) * 0.6}
        holeDiameter={0.254} outerDiameter={0.4572} connectsTo="net.GND"/>
    )))}
    <trace from=".U_PMIC > .EP" to="net.GND"/>
    <HoldUpCapacitor name="C_PMIC_INT_LDO" pcbX={-22.049908} pcbY={30.79989}/>
    <trace name="PMIC_INTERNAL_LDO" from=".U_PMIC > .INT_LDO" to=".C_PMIC_INT_LDO > .pin1"
      thickness={0.20} pcbStraightLine/>
    <trace from=".C_PMIC_INT_LDO > .pin2" to="net.GND"/>
    <via name="V_PMIC_INT_RETURN" pcbX={-21.349884} pcbY={30.79989}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28}
      connectsTo={[".C_PMIC_INT_LDO > .pin2", "net.GND"]}/>
  </>
}
