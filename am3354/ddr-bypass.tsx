import { CL05B104KO5NNNC } from "../imports/CL05B104KO5NNNC";
import { GRM21BC81C226ME44L } from "../imports/GRM21BC81C226ME44L";
import placement from "./bypass-placement.json";

export function DdrBypass() {
	return (
		<>
			{placement.map(({ x, y, rotation, layer, kind }, i) => {
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
						pcbY={y}
						layer={side}
						pcbRotation={rotation}
					/>,
					...["VDDS_DDR", "GND"].flatMap((net, p) => {
						const pin = p + 1;
						const localGround = name === "C_DDR12" && side === "top" && net === "GND";
						const via = "V_" + name + "_" + pin;
						const offset =
							(p === 0 ? -viaDistance : viaDistance) *
							(side === "bottom" ? -1 : 1);
						return [
							<via
								key={via}
								name={via}
								pcbX={x + (rotation === 0 ? offset : 0)}
								pcbY={y + (rotation === 90 ? offset : 0)}
								fromLayer={localGround ? "top" : undefined}
								toLayer={localGround ? "inner1" : undefined}
								holeDiameter={localGround ? 0.125 : 0.254}
								outerDiameter={localGround ? 0.28 : 0.4572}
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
