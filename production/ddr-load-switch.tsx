import { A_0805W8F470JT5E as OutputBleed } from "../imports/A_0805W8F470JT5E"
import { CL31A476MPHNNNE as LoadCap } from "../imports/CL31A476MPHNNNE"
import { TPS22975DSGR } from "../imports/TPS22975DSGR"
import { CL10A106KP8NNNC as InputCap } from "../imports/CL10A106KP8NNNC"
import { CL21A226MAQNNNE as EnableCap } from "../imports/CL21A226MAQNNNE"
import { CL05B104KO5NNNC as BiasCap } from "../imports/CL05B104KO5NNNC"
import { A_0402B102K500NT as SlewCap } from "../imports/A_0402B102K500NT"
import { A_0402WGF2200TCE as Bleed } from "../imports/A_0402WGF2200TCE"

export function DdrLoadSwitch() {
  return <>
    <TPS22975DSGR name="U_DDR_SWITCH" pcbX={-35.95296} pcbY={31.718064} />
    <InputCap name="C_DDR_SW_IN" pcbX={-38.4} pcbY={33.72} pcbRotation={180} />
    <BiasCap name="C_DDR_SW_BIAS" pcbX={-38.85} pcbY={30.22} pcbRotation={180} />
    <SlewCap name="C_DDR_SW_CT" pcbX={-33.35} pcbY={31.42} />
    <EnableCap name="C_DDR_SW_EN" pcbX={-42.15} pcbY={35.9} />
    <Bleed name="R_DDR_SW_EN" pcbX={-39.1} pcbY={35.35} />
    <LoadCap name="C_DDR_SW_LOAD" pcbX={-54.5} pcbY={7.75} pcbRotation={90} layer="bottom" />
    <OutputBleed name="R_DDR_SW_OUT" pcbX={-41.75} pcbY={8} layer="bottom" />
    <trace from=".U_DDR_SWITCH > .VIN1" to="net.VDDS_DDR" />
    <trace from=".U_DDR_SWITCH > .VIN2" to="net.VDDS_DDR" />
    <trace from=".U_DDR_SWITCH > .VOUT1" to="net.VDDS_DDR_CPU" />
    <trace from=".U_DDR_SWITCH > .VOUT2" to="net.VDDS_DDR_CPU" />
    <trace from=".U_DDR_SWITCH > .GND" to="net.GND" />
    <trace from=".U_DDR_SWITCH > .EP" to="net.GND" />
    <trace from=".U_DDR_SWITCH > .VBIAS" to="net.VSYS" />
    <trace from=".U_DDR_SWITCH > .ON" to="net.DDR_SWITCH_ENABLE" />
    <trace from=".U_DDR_SWITCH > .CT" to=".C_DDR_SW_CT > .pin1" thickness={0.15} pcbStraightLine />
    {[
      ["C_DDR_SW_IN", "VDDS_DDR"], ["C_DDR_SW_BIAS", "VSYS"],
      ["C_DDR_SW_EN", "DDR_SWITCH_ENABLE"], ["R_DDR_SW_EN", "DDR_SWITCH_ENABLE"],
      ["R_DDR_SW_OUT", "VDDS_DDR_CPU"], ["C_DDR_SW_LOAD", "VDDS_DDR_CPU"],
    ].map(([name, net]) => <trace key={name} from={"." + name + " > .pin1"} to={"net." + net} />)}
    {["C_DDR_SW_IN", "C_DDR_SW_BIAS", "C_DDR_SW_EN", "C_DDR_SW_CT", "C_DDR_SW_LOAD", "R_DDR_SW_EN", "R_DDR_SW_OUT"].map(
      name => <trace key={name} from={"." + name + " > .pin2"} to="net.GND" />
    )}
  </>
}
