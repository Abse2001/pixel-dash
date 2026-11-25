import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["EN"],
  pin2: ["GND"],
  pin3: ["LX"],
  pin4: ["IN"],
  pin5: ["FB"]
} as const

const pinAttributes = {
  pin2: {requiresGround: true}
} as const

export const SY8089A1AAC = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C479074"
  ]
}}
      manufacturerPartNumber="SY8089A1AAC"
      footprint="sot25_w2.4mm_pl1mm_pin1location(rightside,bottom)"
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C479074.obj?uuid=c7fdf6dae3ca4abaabd1bafd2d31350d",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C479074.step?uuid=c7fdf6dae3ca4abaabd1bafd2d31350d",
        pcbRotationOffset: 180,
        modelOriginPosition: { x: 0, y: 0.0001142999999501626, z: 0.050795 },
      }}
      {...props}
    />
  )
}