import type { CrystalProps } from "@tscircuit/props"

type ImportedCrystalProps = Omit<CrystalProps, "frequency" | "pinVariant">

// JLCPCB import of C362341 (drop-in for C439045, out of stock); land pattern kept identical to the board (JLCPCB's own pads differ by 0.025 mm)
export const TXM24M0004322DBCDO00T = (props: ImportedCrystalProps) => {
  const { name = "X1", ...restProps } = props

  return (
    <crystal
      name={name}
      frequency="24MHz"
      pinVariant="four_pin"
      supplierPartNumbers={{
  "jlcpcb": [
    "C362341"
  ]
}}
      manufacturerPartNumber="TXM24M0004322DBCDO00T"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-1.100074mm" pcbY="-0.850011mm" width="1.3999972mm" height="1.1999976mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="1.100074mm" pcbY="-0.850011mm" width="1.3999972mm" height="1.1999976mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="1.100074mm" pcbY="0.850011mm" width="1.3999972mm" height="1.1999976mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-1.100074mm" pcbY="0.850011mm" width="1.3999972mm" height="1.1999976mm" shape="rect" />
<silkscreenpath route={[{"x":-2.028596400000083,"y":-1.6784827999999834},{"x":-2.028596400000083,"y":1.678736800000138},{"x":2.0285963999999694,"y":1.678736800000138},{"x":2.0285963999999694,"y":-1.6784827999999834},{"x":-2.028596400000083,"y":-1.6784827999999834}]} />
<silkscreenpath route={[{"x":-2.257196399999998,"y":-0.24988519999988057},{"x":-2.257196399999998,"y":-1.9070827999998983},{"x":-0.39999920000002476,"y":-1.9070827999998983}]} />
<silkscreentext text="{NAME}" pcbX="-0.1143mm" pcbY="2.676527mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-2.0500725999999077,"y":1.7000097999999753},{"x":2.0500725999999077,"y":1.7000097999999753},{"x":2.0500725999999077,"y":-1.7000097999999753},{"x":-2.0500725999999077,"y":-1.7000097999999753},{"x":-2.0500725999999077,"y":1.7000097999999753}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C362341.obj?uuid=da128905ee8b4374ad5860b9e47f474a",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C362341.step?uuid=da128905ee8b4374ad5860b9e47f474a",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: -0.000012699999956566899, z: -0.01 },
      }}
      {...restProps}
    />
  )
}