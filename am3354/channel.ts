// Top views from TI SPRS717L (ZCZ) and Micron CCМ005-1005363231-10357 Fig. 2.
// Relative BGA geometry and pad sizes cross-checked against EasyEDA C128768 and C2831669.
import processorBalls from "./processor-balls.json";
import memoryBalls from "./memory-balls.json";

export const packages = [
	{
		name: "U1",
		mpn: "AM3354BZCZD80",
		lcsc: "C128768",
		balls: processorBalls,
		rows: "ABCDEFGHJKLMNPRTUV",
		columns: 18,
		x: 0.2,
		y: 15.15,
		rotation: 0,
		diameter: 0.36,
		width: 15,
		height: 15,
	},
	{
		name: "U_DDR",
		mpn: "MT41K512M16VRP-107 IT:P",
		lcsc: "C2831669",
		balls: memoryBalls,
		rows: "ABCDEFGHJKLMNPRT",
		columns: 9,
		x: -21.5,
		y: 16.15,
		rotation: 180,
		diameter: 0.394,
		width: 8,
		height: 14,
	},
] as const;

const controls: Record<string, string> = {
	"CS#": "CSn0",
	"RAS#": "RASn",
	"CAS#": "CASn",
	"WE#": "WEn",
	"RESET#": "RESETn",
	"CK#": "CKn",
	CK: "CK",
	CKE: "CKE",
	ODT: "ODT",
	LDM: "DQM0",
	UDM: "DQM1",
	LDQS: "DQS0",
	"LDQS#": "DQSn0",
	UDQS: "DQS1",
	"UDQS#": "DQSn1",
};
// The AM335x allows data bit swaps inside a byte. Both pins use LDQS/LDM.
// Memory ball labels stay as marked on the Micron package.
const cpuBitForRamBit: Readonly<Record<string, number>> = { DQ3: 7, DQ7: 3 };

function memoryNet(signal: string) {
	const pin = signal.split("/")[0];
	if (/^(BA|A)\d+$/.test(pin)) return "DDR_" + pin;
	if (/^DQ\d+$/.test(pin)) return "DDR_D" + (cpuBitForRamBit[pin] ?? pin.slice(2));
	if (controls[pin]) return "DDR_" + controls[pin];
}
export const signals = Object.entries(memoryBalls).flatMap(
	([ramBall, signal]) => {
		const name = memoryNet(signal);
		if (!name) return [];
		const cpu = Object.entries(processorBalls).find(
			([, label]) => label === name,
		);
		if (!cpu) throw Error("Missing processor terminal for " + name);
		return [{ name, cpuBall: cpu[0], ramBall }];
	},
);

export function padPosition(ball: string, pkg: (typeof packages)[number]) {
	return {
		x: (Number(ball.slice(1)) - (pkg.columns + 1) / 2) * 0.8,
		y: ((pkg.rows.length - 1) / 2 - pkg.rows.indexOf(ball[0])) * 0.8,
	};
}

export const byteLanes = [0, 1].map((byte) => [
	...Array.from({ length: 8 }, (_, bit) => "DDR_D" + (byte * 8 + bit)),
	"DDR_DQM" + byte,
	"DDR_DQS" + byte,
	"DDR_DQSn" + byte,
]);
export const addressAndClock = signals
	.map(({ name }) => name)
	.filter(
		(name) =>
			name !== "DDR_RESETn" && !byteLanes.some((lane) => lane.includes(name)),
	);

export const pairs = [
	["DDR_CK", "DDR_CKn"],
	["DDR_DQS0", "DDR_DQSn0"],
	["DDR_DQS1", "DDR_DQSn1"],
];

// Provisional edge gap for the 50 Ω / 100 Ω four-layer design cross section.
export const differentialTraceGap = 0.18;
