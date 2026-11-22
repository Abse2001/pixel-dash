import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"]
} as const

export const LQM21FN100M80L = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      symbol={
        <symbol>
          <port name="pin2" pinNumber={2} aliases={["2"]} direction="right" schX={0.4} schY={0} schStemLength={0.06} />
          <port name="pin1" pinNumber={1} aliases={["1"]} direction="left" schX={-0.4} schY={0} schStemLength={0.06} />
          <schematicpath svgPath="M -0.33766 0.00136 A 0.08 0.078 0 1 0 -0.17836 0.00128" strokeColor="#880000" />
          <schematicpath svgPath="M -0.168 0.00142 A 0.08 0.078 0 1 0 -0.0087 0.00132" strokeColor="#880000" />
          <schematicpath svgPath="M 0.00134 0.00142 A 0.08 0.078 0 1 0 0.16064 0.00132" strokeColor="#880000" />
          <schematicpath svgPath="M 0.174 0.00138 A 0.08 0.078 0 1 0 0.3333 0.00128" strokeColor="#880000" />
          <schematictext schX={0} schY={0.286} text="{NAME}" fontSize={0.2} anchor="bottom_center" />
        </symbol>
      }
      supplierPartNumbers={{
  "jlcpcb": [
    "C162582"
  ]
}}
      manufacturerPartNumber="LQM21FN100M80L"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-0.966216mm" pcbY="0mm" width="1.1325352mm" height="1.3770102mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="0.966216mm" pcbY="0mm" width="1.1325352mm" height="1.3770102mm" shape="rect" />
<silkscreenpath route={[{"x":-0.4212590000000773,"y":1.015949199999909},{"x":-1.5642590000001064,"y":1.015949199999909},{"x":-1.6912590000000591,"y":1.015949199999909},{"x":-1.9452590000000782,"y":0.76194919999989},{"x":-1.9452590000000782,"y":-0.6350507999999309},{"x":-1.9452590000000782,"y":-0.7620508000001109},{"x":-1.6912590000000591,"y":-1.0160508000000164},{"x":-0.4212590000000773,"y":-1.0160508000000164}]} />
<silkscreenpath route={[{"x":0.34074099999998,"y":-1.0160508000000164},{"x":1.4837409999998954,"y":-1.0160508000000164},{"x":1.6107409999999618,"y":-1.0160508000000164},{"x":1.8647409999998672,"y":-0.7620508000001109},{"x":1.8647409999998672,"y":0.6349491999999373},{"x":1.8647409999998672,"y":0.76194919999989},{"x":1.6107409999999618,"y":1.015949199999909},{"x":0.34074099999998,"y":1.015949199999909}]} />
<silkscreentext text="{NAME}" pcbX="-0.04191mm" pcbY="2.019302mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-1.782483599999864,"y":0.9385051000000431},{"x":1.7824835999999777,"y":0.9385051000000431},{"x":1.7824835999999777,"y":-0.9385051000000431},{"x":-1.782483599999864,"y":-0.9385051000000431},{"x":-1.782483599999864,"y":0.9385051000000431}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C162582.obj?uuid=c7acac53bcbc44d68fbab8f60a747688",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C162582.step?uuid=c7acac53bcbc44d68fbab8f60a747688",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: -0.000038099999983387534, z: 0 },
      }}
      {...props}
    />
  )
}