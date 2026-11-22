import type { ResistorProps } from "@tscircuit/props"

export const A_0805W8F470JT5E = (props: Omit<ResistorProps, "resistance">) => {
  const { name = "R1", ...restProps } = props

  return (
    <resistor
      name={name}
      resistance="47ohm"
      supplierPartNumbers={{
  "jlcpcb": [
    "C17714"
  ]
}}
      manufacturerPartNumber="0805W8F470JT5E"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="0.999998mm" pcbY="0mm" width="1.1325352mm" height="1.3770102mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-0.999998mm" pcbY="0mm" width="1.1325352mm" height="1.3770102mm" shape="rect" />
<silkscreenpath route={[{"x":0.4761991999999964,"y":-0.9170924000000014},{"x":1.7611343999999463,"y":-0.9170924000000014},{"x":1.7611343999999463,"y":0.9170924000000014},{"x":0.4761991999999964,"y":0.9170924000000014}]} />
<silkscreenpath route={[{"x":-0.47619920000011007,"y":-0.9170924000000014},{"x":-1.7611343999999463,"y":-0.9170924000000014},{"x":-1.7611343999999463,"y":0.9170924000000014},{"x":-0.47619920000011007,"y":0.9170924000000014}]} />
<silkscreentext text="{NAME}" pcbX="0.0127mm" pcbY="1.9144mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-1.8162655999998378,"y":0.9385051000000431},{"x":1.8162655999998378,"y":0.9385051000000431},{"x":1.8162655999998378,"y":-0.9385051000000431},{"x":-1.8162655999998378,"y":-0.9385051000000431},{"x":-1.8162655999998378,"y":0.9385051000000431}]} />
      </footprint>}

      {...restProps}
    />
  )
}