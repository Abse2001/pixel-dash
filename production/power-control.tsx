import { Fragment } from "react"
import { CL10A475KO8NNNC as BackupInputCapacitor } from "../imports/CL10A475KO8NNNC"
import { CL10A105KB8NNNC as HoldUpCapacitor } from "../imports/CL10A105KB8NNNC"
import { SKRTLAE010 } from "../imports/SKRTLAE010"
import { TPS65218D0PHPR } from "../imports/TPS65218D0PHPR"
import { A_0603WAF1003T5E as Pull100k } from "../imports/A_0603WAF1003T5E"
import { A_0402WGF1002TCE as Pull10k } from "../imports/A_0402WGF1002TCE"

import { RT0402BRD0712K1L as DdrSelect } from "../imports/RT0402BRD0712K1L"
import { LQM21FN100M80L as BackupInductor } from "../imports/LQM21FN100M80L"
import { CL31A476MPHNNNE as BackupOutputCapacitor } from "../imports/CL31A476MPHNNNE"
import { SPM3012T_1R5M as MainInductor } from "../imports/SPM3012T_1R5M"
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
    <Pull100k name="R_PMIC_WAKE" pcbX={-28} pcbY={25} layer="bottom"/>
    <Pull10k name="R_PMIC_IRQ" pcbX={-27} pcbY={27} layer="bottom"/>
    <net name="VSYS"/><net name="VDDS_RTC_1V8"/>
    <trace name="POWER_KEY" from=".U_PMIC > .PB" to=".SW_POWER > .pin2" thickness={0.15}/>
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
    {Object.entries(processorBalls).filter(([, supply]) => ["VDDSHV3", "VDDSHV5", "VDDSHV6"].includes(supply)).map(([ball]) => (
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
    <BackupInputCapacitor name="C_PMIC_IN_BU" pcbX={-18.049916} pcbY={30.84989} pcbRotation={180} layer="bottom"/>
    <via name="V_PMIC_BU_FEED" pcbX={-18.74994} pcbY={29.99989}
      holeDiameter={0.20} outerDiameter={0.40} connectsTo="net.VSYS"/>
    <trace name="PMIC_BACKUP_INPUT" from=".U_PMIC > .IN_BU" to=".V_PMIC_BU_FEED > .top"
      thickness={0.23} pcbStraightLine/>
    <trace from=".V_PMIC_BU_FEED > .bottom" to=".C_PMIC_IN_BU > .pin1"
      thickness={0.23} pcbStraightLine/>
    <trace from=".C_PMIC_IN_BU > .pin1" to="net.VSYS"/>
    <trace from=".C_PMIC_IN_BU > .pin2" to="net.GND"/>
    <via name="V_PMIC_IN_BU_RETURN" pcbX={-17.349892} pcbY={30.84989}
      fromLayer="bottom" toLayer="inner2" holeDiameter={0.125} outerDiameter={0.28}
      connectsTo={[".C_PMIC_IN_BU > .pin2", "net.GND"]}/>
    <HoldUpCapacitor name="C_PMIC_SYS_BU" pcbX={-14.000086} pcbY={27.750058}/>
    <trace name="PMIC_BACKUP_SYSTEM" from=".U_PMIC > .SYS_BU" to=".C_PMIC_SYS_BU > .pin1"
      thickness={0.20} pcbStraightLine/>
    <trace from=".C_PMIC_SYS_BU > .pin2" to="net.GND"/>
    <via name="V_PMIC_SYS_BU_RETURN" pcbX={-13.300062} pcbY={27.750058}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28}
      connectsTo={[".C_PMIC_SYS_BU > .pin2", "net.GND"]}/>
    <trace from=".U_PMIC > .CC" to="net.GND"/>
    <via name="V_PMIC_CC_GND" pcbX={-17.749942} pcbY={29.19989}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28}
      connectsTo={[".U_PMIC > .CC", "net.GND"]}/>
    <HoldUpCapacitor name="C_PMIC_INT_LDO" pcbX={-22.049908} pcbY={30.94989}/>
    <trace name="PMIC_INTERNAL_LDO" from=".U_PMIC > .INT_LDO" to=".C_PMIC_INT_LDO > .pin1"
      thickness={0.20} pcbStraightLine/>
    <trace from=".C_PMIC_INT_LDO > .pin2" to="net.GND"/>
    <via name="V_PMIC_INT_RETURN" pcbX={-21.349884} pcbY={30.94989}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28}
      connectsTo={[".C_PMIC_INT_LDO > .pin2", "net.GND"]}/>
    <MainInductor name="L_PMIC_DDR" pcbX={-27.74989} pcbY={28.249932} pcbRotation={180}/>
    <BackupOutputCapacitor name="C_PMIC_DDR" pcbX={-31.04989} pcbY={29.249932} pcbRotation={90}/>
    <trace from=".U_PMIC > .L3" to=".L_PMIC_DDR > .pin1" thickness={0.36}
      pcbPath={[{x:-5.09989,y:2.249932}]}/>
    <trace from=".L_PMIC_DDR > .pin2" to=".C_PMIC_DDR > .pin1" thickness={0.60} pcbStraightLine/>
    <trace from=".U_PMIC > .FB3" to=".C_PMIC_DDR > .pin1" thickness={0.15} pcbPath={[{x:-4.5998892,y:1.80721214}]}/>
    <trace from=".C_PMIC_DDR > .pin1" to="net.VDDS_DDR"/>
    <trace from=".U_PMIC > .LS1" to="net.VDDS_DDR_CPU"/>
    <trace from=".U_PMIC > .IN_LS1" to="net.VDDS_DDR"/>
    <trace from=".U_PMIC > .IN_DCDC3" to="net.VSYS"/>
    <trace from=".C_PMIC_DDR > .pin2" to="net.GND"/>
    {[-0.24, 0.24].flatMap(x => [-0.24, 0.24].map(y => (
      <via key={`${x}_${y}`} name={`V_DDR_REG_RETURN_${x < 0 ? 0 : 1}_${y < 0 ? 0 : 1}`}
        pcbX={-31.04989+x} pcbY={30.842512+y} fromLayer="top" toLayer="inner1"
        holeDiameter={0.125} outerDiameter={0.28} connectsTo={[".C_PMIC_DDR > .pin2","net.GND"]}/>
    )))}
    <net name="VDD_RTC_CORE_1V0"/>
    <BackupInductor name="L_PMIC_RTC_CORE" pcbX={-11.55011} pcbY={24.250062}/>
    <BackupOutputCapacitor name="C_PMIC_RTC_CORE" pcbX={-8.25011} pcbY={24.250062} pcbRotation={90}/>
    <trace from=".U_PMIC > .L5" to=".L_PMIC_RTC_CORE > .pin1" thickness={0.23}
      pcbPath={[{x:5.09989,y:0.750062}]}/>
    <trace from=".L_PMIC_RTC_CORE > .pin2" to=".C_PMIC_RTC_CORE > .pin1" thickness={0.28} pcbStraightLine/>
    <BackupInductor name="L_PMIC_RTC_IO" pcbX={-11.05011} pcbY={27.249932} pcbRotation={90}/>
    <BackupOutputCapacitor name="C_PMIC_RTC_IO" pcbX={-7.25011} pcbY={28.249932}/>
    <trace from=".U_PMIC > .L6" to=".L_PMIC_RTC_IO > .pin1" thickness={0.23} pcbPath={[{x:4.58025278,y:2.1799296}]}/>
    <trace from=".L_PMIC_RTC_IO > .pin2" to=".C_PMIC_RTC_IO > .pin1" thickness={0.28} pcbStraightLine/>
    <Pull10k name="R_PMIC_POR" pcbX={-26.9} pcbY={28.05} layer="bottom"/>
    <trace name="CPU_COLD_RESET" from=".U_PMIC > .PGOOD" to=".U1 > .B15"/>
    <trace name="CPU_WARM_RESET" from=".U_PMIC > .GPIO3" to=".U1 > .A10"/>
    <trace from=".U_PMIC > .PGOOD" to=".R_PMIC_POR > .pin1"/>
    <trace from=".R_PMIC_POR > .pin2" to=".R_PMIC_IRQ > .pin2" thickness={0.15} pcbStraightLine/>
    <trace from=".U1 > .B5" to=".U_PMIC > .PGOOD_BU"/>
    {[
      ["CORE", "FB5", "VDD_RTC_CORE_1V0", -15.35, 26.249934, -8.25011, 22.657482, -8.25011, 25.842642],
      ["IO", "FB6", "VDDS_RTC_1V8", -15.75, 26.70506, -8.84269, 28.249932, -5.65753, 28.249932],
    ].map(([rail, fb, supply, x, y, cx, cy, gx, gy]) => (
      <Fragment key={rail}>
        <via name={`V_FB_${rail}`} pcbX={Number(x)} pcbY={Number(y)}
          holeDiameter={0.15} outerDiameter={0.30} connectsTo={`net.${supply}`}/>
        <via name={`V_SENSE_${rail}`} pcbX={Number(cx)} pcbY={Number(cy)}
          holeDiameter={0.15} outerDiameter={0.30} connectsTo={`net.${supply}`}/>
        <trace from={`.U_PMIC > .${fb}`} to={`.V_FB_${rail} > .top`} thickness={0.15} pcbStraightLine/>
        <trace from={`.V_FB_${rail} > .bottom`} to={`.V_SENSE_${rail} > .bottom`} thickness={0.15} pcbStraightLine/>
        <trace from={`.C_PMIC_RTC_${rail} > .pin1`} to={`net.${supply}`}/>
        <trace from={`.C_PMIC_RTC_${rail} > .pin2`} to="net.GND"/>
        <via name={`V_RTC_${rail}_RETURN`} pcbX={Number(gx)} pcbY={Number(gy)}
          fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28}
          connectsTo={[`.C_PMIC_RTC_${rail} > .pin2`, "net.GND"]}/>
      </Fragment>
    ))}
    <trace from=".U1 > .D6" to="net.VDD_RTC_CORE_1V0"/>
    {/* SPRS717L Fig. 6-5 note B: disable the internal RTC LDO with VDDS_RTC. */}
    <trace from=".U1 > .B4" to="net.VDDS_RTC_1V8"/>
    <trace from=".U1 > .D7" to="net.VDDS_RTC_1V8"/>
    <net name="VDD_CORE"/>
    <MainInductor name="L_PMIC_CORE" pcbX={-28.199890} pcbY={19.949942} pcbRotation={180}/>
    <BackupOutputCapacitor name="C_PMIC_CORE" pcbX={-32.499890} pcbY={19.949942} pcbRotation={270}/>
    <trace from=".U_PMIC > .L1" to=".L_PMIC_CORE > .pin1" thickness={0.36} pcbStraightLine/>
    <trace from=".L_PMIC_CORE > .pin2" to=".C_PMIC_CORE > .pin1" thickness={0.60} pcbStraightLine/>
    <trace from=".U_PMIC > .FB1" to=".C_PMIC_CORE > .pin1" thickness={0.15} pcbPath={[{x:-4.5998892,y:-2.31185731}]}/>
    <trace from=".C_PMIC_CORE > .pin1" to="net.VDD_CORE"/>
    <trace from=".C_PMIC_CORE > .pin2" to="net.GND"/>
    <trace from=".U_PMIC > .IN_DCDC1" to="net.VSYS"/>
    <via name="V_PMIC_CORE_GND_00" pcbX={-32.739890} pcbY={18.117362}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28} connectsTo={[".C_PMIC_CORE > .pin2","net.GND"]}/>
    <via name="V_PMIC_CORE_GND_01" pcbX={-32.739890} pcbY={18.597362}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28} connectsTo={[".C_PMIC_CORE > .pin2","net.GND"]}/>
    <via name="V_PMIC_CORE_GND_10" pcbX={-32.259890} pcbY={18.117362}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28} connectsTo={[".C_PMIC_CORE > .pin2","net.GND"]}/>
    <via name="V_PMIC_CORE_GND_11" pcbX={-32.259890} pcbY={18.597362}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28} connectsTo={[".C_PMIC_CORE > .pin2","net.GND"]}/>
    <net name="VDD_MPU"/>
    <MainInductor name="L_PMIC_MPU" pcbX={-28.199890} pcbY={24.149936} pcbRotation={180}/>
    <BackupOutputCapacitor name="C_PMIC_MPU" pcbX={-32.999890} pcbY={24.149936} pcbRotation={180}/>
    <trace from=".U_PMIC > .L2" to=".L_PMIC_MPU > .pin1" thickness={0.36} pcbPath={[{"x": -5.09989, "y": 0.249936}]}/>
    <trace from=".L_PMIC_MPU > .pin2" to=".C_PMIC_MPU > .pin1" thickness={0.60} pcbStraightLine/>
    <trace from=".U_PMIC > .FB2" to=".C_PMIC_MPU > .pin1" thickness={0.15} pcbPath={[{"x": -5.09989, "y": 0.750062}]}/>
    <trace from=".C_PMIC_MPU > .pin1" to="net.VDD_MPU"/>
    <trace from=".C_PMIC_MPU > .pin2" to="net.GND"/>
    <trace from=".U_PMIC > .IN_DCDC2" to="net.VSYS"/>
    <via name="V_PMIC_MPU_GND_00" pcbX={-34.832470} pcbY={23.909936}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28} connectsTo={[".C_PMIC_MPU > .pin2","net.GND"]}/>
    <via name="V_PMIC_MPU_GND_01" pcbX={-34.832470} pcbY={24.389936}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28} connectsTo={[".C_PMIC_MPU > .pin2","net.GND"]}/>
    <via name="V_PMIC_MPU_GND_10" pcbX={-34.352470} pcbY={23.909936}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28} connectsTo={[".C_PMIC_MPU > .pin2","net.GND"]}/>
    <via name="V_PMIC_MPU_GND_11" pcbX={-34.352470} pcbY={24.389936}
      fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28} connectsTo={[".C_PMIC_MPU > .pin2","net.GND"]}/>
    {Object.entries(processorBalls).filter(([, pad]) => pad === "VDD_CORE" || pad === "VDD_MPU").map(([ball, rail]) => (
      <trace key={ball} from={".U1 > ." + ball} to={"net." + rail}/>
    ))}
    {[
      { ball: "A5", x: -48.409942, y: 21.940088 }, // VSS_RTC
      { ball: "E8", x: -45.999896, y: 18.749942 }, // VSSA_ADC
      { ball: "M14", x: -41.200058, y: 13.150004 }, // VSSA_USB
      { ball: "N14", x: -41.200058, y: 12.349904 }, // VSSA_USB
    ].map(({ ball, x, y }) => (
      <via key={ball} name={`V_ANALOG_RETURN_${ball}`} pcbX={x} pcbY={y}
        fromLayer="top" toLayer="inner1" holeDiameter={0.125} outerDiameter={0.28}
        connectsTo={[`.U1 > .${ball}`, "net.GND"]}/>
    ))}
    <via name="V_DRAM_OUTPUT" pcbX={-34.81} pcbY={27.355}
      outerDiameter={0.30} holeDiameter={0.15} connectsTo="net.VDDS_DDR"/>
    <via name="V_DRAM_PLANE" pcbX={-39.395} pcbY={25.395}
      outerDiameter={0.30} holeDiameter={0.15} connectsTo="net.VDDS_DDR"/>
    <trace from=".C_PMIC_DDR > .pin1" to=".V_DRAM_OUTPUT > .top" thickness={0.45} pcbStraightLine/>
    <trace from=".V_DRAM_OUTPUT > .bottom" to=".V_DRAM_PLANE > .bottom" thickness={0.45} pcbStraightLine/>
    <trace from=".U_PMIC > .IN_DCDC4" to="net.VSYS"/>
    <trace from=".U_PMIC > .DCDC4" to="net.VDD_IO_3V3_SEQ"/>
    {Object.entries(processorBalls).filter(([, rail]) => rail === "VDDA3P3V_USB0" || rail === "VDDA3P3V_USB1").map(([ball]) => (
      <trace key={ball} from={".U1 > ." + ball} to="net.VDD_IO_3V3_SEQ"/>
    ))}
  </>
}
