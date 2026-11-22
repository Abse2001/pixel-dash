import { CL05B104KO5NNNC } from "../imports/CL05B104KO5NNNC";
import { GRM21BC81C226ME44L } from "../imports/GRM21BC81C226ME44L";
import { CL21A226MAQNNNE } from "../imports/CL21A226MAQNNNE";
import placement from "./bypass-placement.json";

export function DdrBypass() {
	return (
		<>
			{placement.map(({ chip, x, y, rotation, layer, kind, bodyOffsetY = 0, supplyViaDistance, buriedSupplyOffset }, i) => {
				const isBulk = kind === "bulk";
				const bulkCapacitor = chip === "U1" ? CL21A226MAQNNNE : GRM21BC81C226ME44L;
				const Capacitor = isBulk ? bulkCapacitor : CL05B104KO5NNNC;
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
						if (chip === "U1" && pin === 1) return [<trace key={name + "_supply"} from={"." + name + " > .pin1"} to="net.VDDS_DDR_CPU" />];
						const adjacentPlane = side === "top" ? net === "GND" : net === "VDDS_DDR";
						const planeLayer = side === "top" ? "inner1" : "inner2";
						const via = "V_" + name + "_" + pin;
						const distance = p === 0 ? supplyViaDistance ?? viaDistance : viaDistance;
						const staggered = p === 0 && buriedSupplyOffset !== undefined;
						const blind = adjacentPlane || staggered;
						const offset =
							(p === 0 ? -distance : distance) *
							(side === "bottom" ? -1 : 1);
						const viaX = x + (rotation === 0 ? offset : 0);
						const viaY = y + (rotation === 90 ? offset : 0);
						return [
							<via
								key={via}
								name={via}
								pcbX={viaX}
								pcbY={viaY}
								fromLayer={blind ? side : undefined}
								toLayer={blind ? planeLayer : undefined}
								holeDiameter={blind ? 0.125 : 0.254}
								outerDiameter={blind ? 0.28 : 0.4572}
								connectsTo={"net." + net}
							/>,
							<trace
								key={via + "_trace"}
								from={"." + name + " > .pin" + pin}
								to={"." + via + " > ." + side}
								pcbStraightLine
								thickness={0.22}
							/>,
							...(staggered ? [
								<via key={via + "_B"} name={via + "_B"}
									pcbX={viaX + buriedSupplyOffset[0]} pcbY={viaY + buriedSupplyOffset[1]}
									fromLayer="inner1" toLayer="inner2" holeDiameter={0.2} outerDiameter={0.36}
									connectsTo={"net." + net} />,
								<trace key={via + "_buried_link"} from={"." + via + " > ." + planeLayer}
									to={"." + via + "_B > ." + planeLayer} pcbStraightLine thickness={0.11} />,
							] : []),
						];
					}),
				];
			})}
		</>
	);
}
