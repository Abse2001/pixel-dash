import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["VIN1"],
  pin2: ["VIN2"],
  pin3: ["ON"],
  pin4: ["VBIAS"],
  pin5: ["GND"],
  pin6: ["CT"],
  pin7: ["VOUT1"],
  pin8: ["VOUT2"],
  pin9: ["EP"]
} as const

const pinAttributes = {
  pin1: {requiresPower: true},
  pin2: {requiresPower: true},
  pin5: {requiresGround: true}
} as const

export const TPS22975DSGR = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C524777"
  ]
}}
      manufacturerPartNumber="TPS22975DSGR"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-0.94996mm" pcbY="0.750062mm" width="0.5210048mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-0.94996mm" pcbY="0.249936mm" width="0.5210048mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="-0.94996mm" pcbY="-0.249936mm" width="0.5210048mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-0.94996mm" pcbY="-0.750062mm" width="0.5210048mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="0.94996mm" pcbY="-0.750062mm" width="0.5210048mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="0.94996mm" pcbY="-0.249936mm" width="0.5210048mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin7"]} pcbX="0.94996mm" pcbY="0.249936mm" width="0.5210048mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin8"]} pcbX="0.94996mm" pcbY="0.750062mm" width="0.5210048mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin9"]} pcbX="0mm" pcbY="0mm" width="0.8999982mm" height="1.5999968mm" shape="rect" />
<silkscreenpath route={[{"x":-1.040002999999956,"y":-1.0599928000000318},{"x":1.059052999999949,"y":-1.0599928000000318}]} />
<silkscreenpath route={[{"x":1.0500359999998636,"y":1.0627359999999726},{"x":-1.0500359999999773,"y":1.0627359999999726}]} />
<silkscreencircle pcbX="-1.397mm" pcbY="1.143mm" radius="0.0762mm" />
<silkscreentext text="{NAME}" pcbX="-0.127mm" pcbY="2.2319mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-1.460462399999983,"y":1.249998000000005},{"x":1.460462399999983,"y":1.249998000000005},{"x":1.460462399999983,"y":-1.249998000000005},{"x":-1.460462399999983,"y":-1.249998000000005},{"x":-1.460462399999983,"y":1.249998000000005}]} />
      </footprint>}

      {...props}
    />
  )
}