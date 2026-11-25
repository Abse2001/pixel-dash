import type { InductorProps } from "@tscircuit/props"

export const WIP201610P_2R2ML = (props: Omit<InductorProps, "inductance">) => {
  return (
    <inductor
      inductance="2.2uH"
      supplierPartNumbers={{
  "jlcpcb": [
    "C315717"
  ]
}}
      manufacturerPartNumber="WIP201610P-2R2ML"
      footprint="smdpads2_p1.7998mm_pw0.8mm_ph2mm_cyw3.0998mm_cyh2.5mm"
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C315717.obj?uuid=84510a2326f14fa7994472a46feb64ad",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C315717.step?uuid=84510a2326f14fa7994472a46feb64ad",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: 0, z: -0.01 },
      }}
      {...props}
    />
  )
}