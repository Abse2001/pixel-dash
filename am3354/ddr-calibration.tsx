import { RC0201FR_07240RL } from "./imports/RC0201FR_07240RL";
import { A_0402WGF499JTCE } from "./imports/A_0402WGF499JTCE";

export function DdrCalibration() {
	return (
		<>
			<A_0402WGF499JTCE
				name="R_VTP"
				pcbX={-4.81984087}
				pcbY={15.28600287}
				pcbRotation={135}
				layer="bottom"
			/>
			<via
				name="V_VTP"
				pcbX={-4.879888}
				pcbY={15.65505}
				holeDiameter={0.2}
				outerDiameter={0.35}
				connectsTo="net.DDR_VTP"
			/>
			<trace
				from=".U1 > .J3"
				to=".V_VTP > .top"
				thickness={0.15}
				pcbStraightLine
			/>
			<trace
				from=".V_VTP > .bottom"
				to=".R_VTP > .pin1"
				thickness={0.15}
				pcbStraightLine
			/>
			<trace
				from=".V_C_DDR39_2 > .bottom"
				to=".R_VTP > .pin2"
				thickness={0.13}
				pcbPath={[{ x: -1.24579374, y: -0.05204426 }]}
			/>
			<RC0201FR_07240RL
				name="R_ZQ"
				pcbX={-23.638492}
				pcbY={17.919996}
				pcbRotation={180}
				layer="bottom"
			/>
			<via
				name="V_ZQ"
				pcbX={-23.900046}
				pcbY={18.149996}
				holeDiameter={0.2}
				outerDiameter={0.36}
				connectsTo="net.DDR_ZQ"
			/>
			<trace
				from=".U_DDR > .L8"
				to=".V_ZQ > .top"
				thickness={0.102}
				pcbStraightLine
			/>
			<trace
				from=".V_ZQ > .bottom"
				to=".R_ZQ > .pin1"
				thickness={0.102}
				pcbStraightLine
			/>
			<via
				name="V_RZQ_GND"
				pcbX={-23.396938}
				pcbY={17.919996}
				fromLayer="bottom"
				toLayer="inner2"
				holeDiameter={0.125}
				outerDiameter={0.28}
				connectsTo={[".R_ZQ > .pin2", "net.GND"]}
			/>
			<via
				name="V_RZQ_BURIED"
				pcbX={-23.576938}
				pcbY={17.60822685}
				fromLayer="inner2"
				toLayer="inner1"
				holeDiameter={0.2}
				outerDiameter={0.36}
				connectsTo="net.GND"
			/>
			<trace
				from=".V_RZQ_GND > .inner2"
				to=".V_RZQ_BURIED > .inner2"
				thickness={0.2}
				pcbStraightLine
			/>
		</>
	);
}
