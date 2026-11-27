// Part types of the CM4 module: footprint key (plan.ts FP), imported component or value + LCSC number.
/** part type -> footprint and either the imported tscircuit component (as module 0.4.4) or value + LCSC number */
export const PARTS: Record<string, { fp: string; comp?: string; file?: string; value?: string; lcsc?: string }> = {
  C100N_0201: { fp: "C0201", comp: "TMK063ABJ104KP_F", file: "../am3354/imports/TMK063ABJ104KP_F" },
  C100N_0402: { fp: "C0402", comp: "CL05B104KO5NNNC", file: "../imports/CL05B104KO5NNNC" },
  C1U_0402: { fp: "C0402", comp: "CL05A105KA5NQNC", file: "./imports/CL05A105KA5NQNC" },
  C10U_0603: { fp: "C0603", comp: "CL10A106KP8NNNC", file: "../imports/CL10A106KP8NNNC" },
  C15P_0402: { fp: "C0402", comp: "A_0402CG150F500NT", file: "../imports/A_0402CG150F500NT" },
  R240_0201: { fp: "R0201", comp: "RC0201FR_07240RL", file: "../am3354/imports/RC0201FR_07240RL" },
  R49R9_0402: { fp: "R0402", comp: "A_0402WGF499JTCE", file: "../am3354/imports/A_0402WGF499JTCE" },
  R1K_0402: { fp: "R0402", comp: "A_0402WGF1001TCE", file: "../imports/A_0402WGF1001TCE" },
  XTAL_24M: { fp: "XTAL3225", comp: "TXM24M0004322DBCDO00T", file: "./imports/TXM24M0004322DBCDO00T" },
  // new on the CM4 module
  PMIC: { fp: "PMIC", value: "TPS65217DRSLR", lcsc: "C702315" }, BUCK: { fp: "BUCK", value: "SY8089A1AAC", lcsc: "C479074" },
  NFET: { fp: "NFET", value: "Si2302CDS-T1-GE3", lcsc: "C10488" },
  IND: { fp: "IND", value: "2.2uH WIP201610P-2R2ML", lcsc: "C315717" },
  // CM4 connectors: genuine Hirose DF40C-100DP-0.4V(58) (LCSC C6021443), the same part as DF40C-100DP-0.4V(51)
  // (C531031, out of stock) on a different reel; fallback for volume: G-Switch GT-B0403MSV11-100B1101 (C42376235), whose
  // drawing matches Hirose's on every published dimension (README, before ordering)
  CM4_HDR: { fp: "CM4_HDR", value: "DF40C-100DP-0.4V(58)", lcsc: "C6021443" },
  R100K: { fp: "G0402", value: "100k", lcsc: "C25741" }, R10K: { fp: "G0402", value: "10k", lcsc: "C25744" }, R1K: { fp: "G0402", value: "1k", lcsc: "C11702" },
  R2K2: { fp: "G0402", value: "2.2k", lcsc: "C25879" }, R4K7: { fp: "G0402", value: "4.7k", lcsc: "C25900" }, R1K5: { fp: "G0402", value: "1.5k", lcsc: "C25867" },
  R12K1: { fp: "G0402", value: "12.1k 1%", lcsc: "C25852" }, R22K: { fp: "G0402", value: "22k 1%", lcsc: "C25768" }, R200K: { fp: "G0402", value: "200k 1%", lcsc: "C25764" },
  R49R9: { fp: "G0402", value: "49.9 1%", lcsc: "C25120" }, R0: { fp: "G0402", value: "0", lcsc: "C17168" },
  C22U_0603: { fp: "G0603", value: "22uF 6.3V", lcsc: "C59461" }, C22U_0805: { fp: "G0805", value: "22uF 25V", lcsc: "C45783" }, C4U7_0603: { fp: "G0603", value: "4.7uF 16V", lcsc: "C19666" },
  C4U7_0402: { fp: "G0402", value: "4.7uF 10V", lcsc: "C23733" }, C2U2_0402: { fp: "G0402", value: "2.2uF 6.3V", lcsc: "C12530" }, C10U_0402: { fp: "G0402", value: "10uF 6.3V", lcsc: "C15525" },
  C470P_0402: { fp: "G0402", value: "470pF", lcsc: "C1537" },
}
