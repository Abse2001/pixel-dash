import { DdrVref } from "./ddr-vref";
import { DdrCalibration } from "./ddr-calibration";
import { DdrBypass } from "./ddr-bypass";
import { ReferencePlanes } from "./reference-planes";
import {
	packages,
	signals,
	byteLanes,
	pairs,
	differentialTraceGap,
	addressAndClock,
} from "./channel";

import routes from "./connectivity-paths.json";
import type { TraceProps } from "@tscircuit/props";
import placement from "./outline.json";

import { AM3354BZCZD80 } from "./imports/AM3354BZCZD80";
import { MT41K512M16VRP_107_IT_P } from "./imports/MT41K512M16VRP_107_IT_P";

const [cpu, ram] = packages;

// TI SPRS717L tables 7-68 and 7-69. RESETn is asynchronous.
function processorPin(signal: string) {
	const connection = signals.find((item) => item.name === signal);
	if (!connection) throw Error("Missing DDR signal " + signal);
	return ".U1 > ." + connection.cpuBall;
}

export default function MemoryChannel({ pcbOffsetX = 0, children }: {
    pcbOffsetX?: number
    children?: import("react").ReactNode
} = {}) {
	return (
		<board
			schAutoLayoutEnabled={false}
			routeRemaining={false}
			width={144.5}
			height={82}
			layers={4}
			thickness={1.6}
			outline={placement.outline}
			pcbStyle={{ viaPadDiameter: 0.4572, viaHoleDiameter: 0.254 }}
			minTraceWidth={0.102}
			minTraceToPadEdgeClearance={0.102}
			minViaHoleDiameter={0.125}
			minViaPadDiameter={0.28}
			allowBlindAndBuriedVias={true}
			isViaInPadAllowed={true}
			title="AM3354 DDR3L channel development"
		>
			<group pcbX={pcbOffsetX} pcbY={0}>
				<AM3354BZCZD80
					name={cpu.name}
					pcbX={cpu.x}
					pcbY={cpu.y}
					pcbRotation={cpu.rotation}
				/>
				<MT41K512M16VRP_107_IT_P
					name={ram.name}
					pcbX={ram.x}
					pcbY={ram.y}
					pcbRotation={ram.rotation}
				/>
				{signals.map((s) => (
					<trace
						key={s.name}
						name={s.name}
						thickness={0.102}
						pcbPath={
							routes[s.name as keyof typeof routes] as TraceProps["pcbPath"]
						}
						from={".U1 > ." + s.cpuBall}
						to={".U_DDR > ." + s.ramBall}
					/>
				))}
				{byteLanes.map((names, i) => (
					<bus
						key={i}
						name={"DDR_BYTE" + i}
						connections={names.map(processorPin)}
						targetImpedance="50±5ohm"
						maxLengthSkew={0.635}
						maxLength={{ reference: "longest_manhattan" }}
						preferredLayers={["bottom"]}
					/>
				))}
				<bus
					name="DDR_ADDR_CTRL_CK"
					targetImpedance="50±5ohm"
					connections={addressAndClock.map(processorPin)}
					targetLength={{ reference: "longest_manhattan", offset: 7.62 }}
					lengthTolerance={1.27}
				/>
				{pairs.map(([pos, neg]) => (
					<differentialpair
						key={pos}
						name={pos + "_PAIR"}
						positiveConnection={processorPin(pos)}
						negativeConnection={processorPin(neg)}
						maxLengthSkew={0.127}
						pcbTraceGap={differentialTraceGap}
						targetDifferentialImpedance="100±10ohm"
					/>
				))}
				<ReferencePlanes pcbOffsetX={pcbOffsetX} />
				<DdrBypass />
				<DdrCalibration />
				<DdrVref />
			</group>
		{children}
		</board>
	);
}
