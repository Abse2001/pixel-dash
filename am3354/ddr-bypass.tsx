import { CL05B104KO5NNNC } from "../imports/CL05B104KO5NNNC";
import { GRM21BC81C226ME44L } from "../imports/GRM21BC81C226ME44L";
import placement from "./bypass-placement.json";

export function DdrBypass() {
	return (
		<>
			{placement.map(({ x, y, rotation, layer, kind, bodyOffsetY = 0, supplyViaDistance }, i) => {
				const isBulk = kind === "bulk";
				const Capacitor = isBulk ? GRM21BC81C226ME44L : CL05B104KO5NNNC;
				const viaDistance = isBulk ? 2.08 : 1.2;
				const name = "C_DDR" + (i + 1);
				const side = layer === "top" ? "top" : "bottom";
				return [
					<Capacitor
						key={name}
						name={name}
						pcbX={x}
						pcbY={y + bodyOffsetY}
						layer={side}
						pcbRotation={rotation}
					/>,
					...["VDDS_DDR", "GND"].flatMap((net, p) => {
						const pin = p + 1;
						const adjacentPlane = side === "top" ? net === "GND" : net === "VDDS_DDR";
						const planeLayer = side === "top" ? "inner1" : "inner2";
						const via = "V_" + name + "_" + pin;
						const distance = p === 0 ? supplyViaDistance ?? viaDistance : viaDistance;
						const offset =
							(p === 0 ? -distance : distance) *
							(side === "bottom" ? -1 : 1);
						return [
							<via
								key={via}
								name={via}
								pcbX={x + (rotation === 0 ? offset : 0)}
								pcbY={y + (rotation === 90 ? offset : 0)}
								fromLayer={adjacentPlane ? side : undefined}
								toLayer={adjacentPlane ? planeLayer : undefined}
								holeDiameter={adjacentPlane ? 0.125 : 0.254}
								outerDiameter={adjacentPlane ? 0.28 : 0.4572}
								connectsTo={"net." + net}
							/>,
							<trace
								key={via + "_trace"}
								from={"." + name + " > .pin" + pin}
								to={"." + via + " > ." + side}
								pcbStraightLine
								thickness={0.22}
							/>,
						];
					}),
				];
			})}
		</>
	);
}
