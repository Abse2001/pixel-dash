import { TMK063ABJ104KP_F } from "./imports/TMK063ABJ104KP_F";
import { A_0603WAF0000T5E } from "../imports/A_0603WAF0000T5E";
import cpuPath from "./cpu-vref-path.json";
import { A_0402WGF1001TCE } from "../imports/A_0402WGF1001TCE";
import { CL05B104KO5NNNC } from "../imports/CL05B104KO5NNNC";
import placement from "./vref-placement.json";

export function DdrVref() {
	return (
		<>
			<net name="DDR_VREF" />
			<net name="DDR_VREF_CA" />
			<A_0603WAF0000T5E
				name="R_VREF_CA"
				pcbX={-10.87024}
				pcbY={9.08996}
				pcbRotation={-143.1301023542}
			/>
			<trace from=".R_VREF_CA > .pin1" to="net.DDR_VREF_CA" />
			<trace from=".R_VREF_CA > .pin2" to="net.DDR_VREF" />
			<via
				name="V_RAM_VREF_CA"
				pcbX={-22.335046}
				pcbY={18.215096}
				connectsTo="net.DDR_VREF_CA"
				outerDiameter={0.35}
				holeDiameter={0.2}
				tented={true}
			/>
			<trace
				from=".U_DDR > .M8"
				to=".V_RAM_VREF_CA > .top"
				thickness={0.102}
				pcbStraightLine
			/>
			<via
				name="V_REF_LINK_CA0"
				pcbX={-23.6}
				pcbY={18.3625}
				outerDiameter={0.36}
				holeDiameter={0.2}
				connectsTo="net.DDR_VREF_CA"
				tented
			/>
			<trace
				from=".V_RAM_VREF_CA > .bottom"
				to=".V_REF_LINK_CA0 > .bottom"
				thickness={0.102}
				pcbPath={[{ x: -0.402454, y: -0.377596 }]}
			/>
			<trace
				from=".V_REF_LINK_CA0 > .top"
				to=".R_VREF_CA > .pin1"
				thickness={0.4}
				pcbPath={[
					{ x: -0.747335, y: 0.260321 },
					{ x: -2.423543, y: -1.373929 },
					{ x: -2.383303, y: -9.475016 },
					{ x: -1.11, y: -12.135 },
					{ x: -0.3375, y: -12.675 },
					{ x: 8.1, y: -12.4875 },
					{ x: 12.6375, y: -11.2875 },
					{ x: 13.35, y: -10.0875 },
				]}
			/>
			<trace
				from=".C_VREF_DQ > .pin1"
				to=".R_VREF_CA > .pin2"
				thickness={0.102}
				pcbPath={[
					{ x: 0.1189412, y: -0.4330619 },
					{ x: 0.7553373, y: -0.4330619 },
					{ x: 1.0470188, y: 0.0177187 },
					{ x: 1.2326343, y: 1.5821924 },
				]}
			/>
			<CL05B104KO5NNNC
				name="C_VREF_CA"
				pcbX={-23.8}
				pcbY={18.75625}
				layer="bottom"
			/>
			<trace
				from=".C_VREF_CA > .pin1"
				to=".V_REF_LINK_CA0 > .bottom"
				thickness={0.152}
				pcbStraightLine
			/>
			<trace
				from=".C_VREF_CA > .pin2"
				to=".V_C_DDR3_2 > .bottom"
				thickness={0.152}
				pcbStraightLine
			/>
			<TMK063ABJ104KP_F
				name="C_CPU_VREF"
				pcbX={-8.8739735}
				pcbY={15.3660265}
				pcbRotation={225}
			/>
			<via
				name="V_CPU_VREF_GND"
				pcbX={-9.0679471}
				pcbY={15.1720529}
				fromLayer="top"
				toLayer="inner1"
				outerDiameter={0.28}
				holeDiameter={0.125}
				connectsTo="net.GND"
			/>
			<trace
				from=".V_CPU_VREF_4 > .top"
				to=".C_CPU_VREF > .pin1"
				thickness={0.102}
				pcbStraightLine
			/>
			<trace
				from=".C_CPU_VREF > .pin2"
				to=".V_CPU_VREF_GND > .top"
				thickness={0.102}
				pcbStraightLine
			/>
			{cpuPath.vias.map(({ name, at, through }) => (
				<via
					key={name}
					name={name}
					pcbX={at.x}
					pcbY={at.y}
					connectsTo="net.DDR_VREF"
					fromLayer="top"
					toLayer={through ? "bottom" : "inner1"}
					outerDiameter={through ? 0.3 : 0.28}
					holeDiameter={through ? 0.15 : 0.125}
				/>
			))}
			{cpuPath.traces.map(({ start, end, width, path }) => (
				<trace
					key={start}
					from={start}
					to={end}
					thickness={width}
					pcbPath={path.length ? path : undefined}
					pcbStraightLine={path.length === 0}
				/>
			))}
			{[".U1 > .J4", ".U_DDR > .H1"].map((pin) => (
				<trace key={pin} from={pin} to="net.DDR_VREF" />
			))}
			{placement.map(({ name, rail, center, rotation, via, buried, route }) => {
				const Device = name.startsWith("C_")
					? CL05B104KO5NNNC
					: A_0402WGF1001TCE;
				const laser = "V_" + name;
				// Manual paths start at H1. Its footprint is rotated 180 degrees.
				const path = route.map((p) => ({ x: -20 - p.x, y: 15.15 - p.y }));
				return [
					<Device
						key={name}
						name={name}
						pcbX={center.x}
						pcbY={center.y}
						pcbRotation={rotation}
					/>,
					<trace
						key={name + "_sense"}
						from=".U_DDR > .H1"
						to={"." + name + " > .pin1"}
						pcbPath={path}
						thickness={0.102}
					/>,
					<via
						key={laser}
						name={laser}
						pcbX={via.x}
						pcbY={via.y}
						fromLayer="top"
						toLayer="inner1"
						outerDiameter={0.28}
						holeDiameter={0.125}
						connectsTo={"net." + rail}
					/>,
					<trace
						key={name + "_feed"}
						from={"." + name + " > .pin2"}
						to={"." + laser + " > .top"}
						pcbStraightLine
						thickness={0.2}
					/>,
					...(buried
						? [
								<via
									key={laser + "_B"}
									name={laser + "_B"}
									pcbX={buried.x}
									pcbY={buried.y}
									fromLayer="inner1"
									toLayer="inner2"
									outerDiameter={0.36}
									holeDiameter={0.2}
									connectsTo={"net." + rail}
								/>,
								<trace
									key={laser + "_link"}
									from={"." + laser + " > .inner1"}
									to={"." + laser + "_B > .inner1"}
									pcbStraightLine
									thickness={0.2}
								/>,
							]
						: []),
				];
			})}
		</>
	);
}
