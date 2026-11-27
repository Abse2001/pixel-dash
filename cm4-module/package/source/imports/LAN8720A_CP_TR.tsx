import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["VDD2A"],
  pin2: ["LED2","nINTSEL"],
  pin3: ["LED1","REGOFF"],
  pin4: ["XTAL2"],
  pin5: ["XTAL1","CLKIN"],
  pin6: ["VDDCR"],
  pin7: ["RXD1","MODE1"],
  pin8: ["RXD0","MODE0"],
  pin9: ["VDDIO"],
  pin10: ["RXER","PHYAD0"],
  pin11: ["CRS_DV","MODE2"],
  pin12: ["MDIO"],
  pin13: ["MDC"],
  pin14: ["nINT","REFCLKO"],
  pin15: ["nRST"],
  pin16: ["TXEN"],
  pin17: ["TXD0"],
  pin18: ["TXD1"],
  pin19: ["VDD1A"],
  pin20: ["TXN"],
  pin21: ["TXP"],
  pin22: ["RXN"],
  pin23: ["RXP"],
  pin24: ["RBIAS"],
  pin25: ["EP"]
} as const

const pinAttributes = {
  pin1: {requiresPower: true, requiresVoltage: "3.3V", shouldHaveDecouplingCapacitor: true},
  pin2: {isBidirectional: true, canUseInternalPullup: true},
  pin3: {isBidirectional: true, canUseInternalPulldown: true},
  pin4: {isOutput: true},
  pin5: {isInput: true},
  pin6: {isOutput: true, requiresPower: true, shouldHaveDecouplingCapacitor: true, recommendedDecouplingCapacitorCapacitance: "1uF"},
  pin7: {isBidirectional: true, canUseInternalPullup: true},
  pin8: {isBidirectional: true, canUseInternalPullup: true},
  pin9: {requiresPower: true, shouldHaveDecouplingCapacitor: true},
  pin10: {isBidirectional: true, canUseInternalPulldown: true},
  pin11: {isBidirectional: true, canUseInternalPullup: true},
  pin12: {isBidirectional: true, needsExternalPullup: true, canUseOpenDrain: true},
  pin13: {isInput: true},
  pin14: {isOutput: true, canUseInternalPullup: true, canUseOpenDrain: true, canUsePushPull: true},
  pin15: {isInput: true, canUseInternalPullup: true},
  pin16: {isInput: true},
  pin17: {isInput: true},
  pin18: {isInput: true},
  pin19: {requiresPower: true, requiresVoltage: "3.3V", shouldHaveDecouplingCapacitor: true},
  pin20: {isBidirectional: true},
  pin21: {isBidirectional: true},
  pin22: {isBidirectional: true},
  pin23: {isBidirectional: true},
  pin24: {isInput: true, mustBeConnected: true},
  pin25: {requiresGround: true, mustBeConnected: true}
} satisfies NonNullable<ChipProps["pinAttributes"]>

const footprinterPinLabels = {
  ...pinLabels,
  "pin25": [...pinLabels["pin25"], "thermalpad"],
} as const

export const LAN8720A_CP_TR = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={footprinterPinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C45223"
  ]
}}
      manufacturerPartNumber="LAN8720A-CP-TR"
      footprint="qfn24_thermalpad2.55mmx2.55mm_h4.68mm_pw0.28mm_pl0.66mm_pin1location(bottomside,left)"
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C45223.obj?uuid=95b00662192d4d1baf684c34174076f8",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C45223.step?uuid=95b00662192d4d1baf684c34174076f8",
        pcbRotationOffset: 90,
        modelOriginPosition: { x: 0, y: 0, z: 0 },
      }}
      {...props}
    />
  )
}