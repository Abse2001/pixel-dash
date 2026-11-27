import type { CrystalProps } from "@tscircuit/props"

type ImportedCrystalProps = Omit<CrystalProps, "frequency" | "pinVariant">

export const K3A250001210 = (props: ImportedCrystalProps) => {
  const { name = "X1", ...restProps } = props

  return (
    <crystal
      name={name}
      frequency="25MHz"
      pinVariant="four_pin"
      supplierPartNumbers={{
  "jlcpcb": [
    "C18213377"
  ]
}}
      manufacturerPartNumber="K3A250001210"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-1.099947mm" pcbY="-0.799973mm" width="1.3999972mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="1.099947mm" pcbY="-0.799973mm" width="1.3999972mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="1.099947mm" pcbY="0.799973mm" width="1.3999972mm" height="1.1500104mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-1.099947mm" pcbY="0.799973mm" width="1.3999972mm" height="1.1500104mm" shape="rect" />
<silkscreenpath route={[{"x":-2.5401015999998435,"y":-1.0158983999997417},{"x":-2.5401015999998435,"y":-1.777898399999799},{"x":-2.5401015999998435,"y":-1.9048983999998654}]} />
<silkscreenpath route={[{"x":-2.0296123999999054,"y":-1.6786097999998901},{"x":-2.286177799999905,"y":-1.6786097999998901},{"x":-2.286177799999905,"y":1.6512286000000813},{"x":2.2858222000002115,"y":1.6512286000000813},{"x":2.2858222000002115,"y":0.00022860000012769888},{"x":2.2858222000002115,"y":-1.650771399999826},{"x":-2.0296123999999054,"y":-1.6786097999998901}]} />
<silkscreenpath route={[{"x":-2.5401015999998435,"y":-1.9048983999998654},{"x":-1.6511015999999472,"y":-1.9048983999998654}]} />
<silkscreentext text="{NAME}" pcbX="-0.124587mm" pcbY="2.648587mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-2.049945600000001,"y":1.6249781999999868},{"x":2.0499456000002283,"y":1.6249781999999868},{"x":2.0499456000002283,"y":-1.6249781999998731},{"x":-2.049945600000001,"y":-1.6249781999998731},{"x":-2.049945600000001,"y":1.6249781999999868}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C18213377.obj?uuid=4272a6fc4bf14604b2238eb7f7bac6e5",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C18213377.step?uuid=4272a6fc4bf14604b2238eb7f7bac6e5",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0.00057619999996672, y: 0.000012699999842880061, z: -0.01 },
      }}
      {...restProps}
    />
  )
}