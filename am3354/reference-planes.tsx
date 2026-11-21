import microvias from "./selective-microvias.json";
import { packages } from "./channel";
import fanout from "./reference-fanout.json";

const supplyOutline = [
	{ x: -27, y: 5 },
	{ x: 10, y: 5 },
	{ x: 10, y: 29 },
	{ x: -27, y: 29 },
];

const assigned = new Set(fanout.map(({ chip, ball }) => chip + "." + ball));
for (const { chip, ball } of microvias) assigned.add(chip + "." + ball);
const pending = packages.flatMap(({ name, balls }) =>
	Object.entries(balls).flatMap(([ball, label]) => {
		if (assigned.has(name + "." + ball)) return [];
		if (label === "VSS" || label === "VSSQ")
			return [{ name, ball, net: "GND" }];
		if (
			label === "VDDS_DDR" ||
			(name === "U_DDR" && (label === "VDD" || label === "VDDQ"))
		) {
			return [{ name, ball, net: "VDDS_DDR" }];
		}
		return [];
	}),
);

export function ReferencePlanes({ pcbOffsetX }: { pcbOffsetX: number }) {
	return (
		<>
			<net name="GND" />
			<net name="VDDS_DDR" />
			<copperpour
				connectsTo="net.GND"
				layer="inner1"
				clearance={0.16}
				boardEdgeMargin={0.3}
			/>
			<copperpour
				connectsTo="net.VDDS_DDR"
				layer="inner2"
				outline={supplyOutline.map(({ x, y }) => ({ x: x + pcbOffsetX, y }))}
				clearance={0.16}
			/>
			{microvias.map(
				({ chip, ball, net, x, y, buriedX, buriedY, usesStub }) => {
					const via = "M_" + chip + "_" + ball;
					const buried = via + "_B";
					const pin = "." + chip + " > ." + ball;
					return [
						<via
							key={via}
							name={via}
							pcbX={x}
							pcbY={y}
							fromLayer="top"
							toLayer="inner1"
							outerDiameter={0.28}
							holeDiameter={0.125}
							connectsTo={usesStub ? "net." + net : [pin, "net." + net]}
						/>,
						...(usesStub
							? [
									<trace
										key={via + "_stub"}
										from={pin}
										to={"." + via + " > .top"}
										thickness={0.102}
										pcbStraightLine
									/>,
								]
							: []),
						...(buriedX === undefined || buriedY === undefined
							? []
							: [
									<via
										key={buried}
										name={buried}
										pcbX={buriedX}
										pcbY={buriedY}
										fromLayer="inner1"
										toLayer="inner2"
										outerDiameter={0.36}
										holeDiameter={0.2}
										connectsTo={"net." + net}
									/>,
									<trace
										key={buried + "_link"}
										from={"." + via + " > .inner1"}
										to={"." + buried + " > .inner1"}
										pcbStraightLine
										thickness={0.2}
									/>,
								]),
					];
				},
			)}
			{pending.map(({ name, ball, net }) => (
				<trace
					key={name + ball}
					from={"." + name + " > ." + ball}
					to={"net." + net}
				/>
			))}
			{fanout.map(({ chip, ball, net, x, y, path, width, shareWith }) => {
				const via = "V_" + chip + "_" + (shareWith ?? ball);
				const localGround = net === "GND";
				const compactSupplyVia = via === "V_U_DDR_N9";
				const pin = "." + chip + " > ." + ball;
				const route = path
					?.slice()
					.reverse()
					.map((p) => ({ x: p.x - x, y: p.y - y }));
				return [
					!shareWith && (
						<via
							key={via}
							name={via}
							pcbX={x}
							pcbY={y}
							fromLayer={localGround ? "top" : undefined}
							toLayer={localGround ? "inner1" : undefined}
							holeDiameter={localGround ? 0.125 : compactSupplyVia ? 0.2 : 0.254}
							outerDiameter={localGround ? 0.28 : compactSupplyVia ? 0.35 : 0.4572}
							connectsTo={"net." + net}
						/>
					),
					<trace
						key={chip + ball + "_stub"}
						from={"." + via + " > .top"}
						to={pin}
						thickness={width ?? 0.22}
						pcbPath={route}
						pcbStraightLine={!route}
					/>,
				];
			})}
		</>
	);
}
