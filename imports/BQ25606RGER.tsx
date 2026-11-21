import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["VAC"],
  pin2: ["NC"],
  pin3: ["D_POS"],
  pin4: ["D_NEG"],
  pin5: ["STAT"],
  pin6: ["OTG"],
  pin7: ["N_PG"],
  pin8: ["ILIM"],
  pin9: ["N_CE"],
  pin10: ["ICHG"],
  pin11: ["TS"],
  pin12: ["VSET"],
  pin13: ["BAT2"],
  pin14: ["BAT1"],
  pin15: ["SYS2"],
  pin16: ["SYS1"],
  pin17: ["GND2"],
  pin18: ["GND1"],
  pin19: ["SW2"],
  pin20: ["SW1"],
  pin21: ["BTST"],
  pin22: ["REGN"],
  pin23: ["PMID"],
  pin24: ["VBUS"],
  pin25: ["EP"]
} as const

const pinAttributes = {
  pin2: {doNotConnect: true},
  pin17: {requiresGround: true},
  pin18: {requiresGround: true},
  pin24: {requiresPower: true}
} as const

export const BQ25606RGER = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C374063"
  ]
}}
      manufacturerPartNumber="BQ25606RGER"
      footprint={<footprint>
        <smtpad portHints={["pin25"]} pcbX="-0.001016mm" pcbY="-0.000889mm" width="2.7999944mm" height="2.7999944mm" shape="rect" />
<smtpad portHints={["pin24"]} pcbX="-1.250188mm" pcbY="2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin23"]} pcbX="-0.750316mm" pcbY="2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin22"]} pcbX="-0.25019mm" pcbY="2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin21"]} pcbX="0.249682mm" pcbY="2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin20"]} pcbX="0.749808mm" pcbY="2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin19"]} pcbX="1.24968mm" pcbY="2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin18"]} pcbX="2.041652mm" pcbY="1.250061mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<smtpad portHints={["pin17"]} pcbX="2.041652mm" pcbY="0.749935mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<smtpad portHints={["pin16"]} pcbX="2.041652mm" pcbY="0.250063mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<smtpad portHints={["pin15"]} pcbX="2.041652mm" pcbY="-0.250063mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<smtpad portHints={["pin14"]} pcbX="2.041652mm" pcbY="-0.749935mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<smtpad portHints={["pin13"]} pcbX="2.041652mm" pcbY="-1.250061mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<smtpad portHints={["pin12"]} pcbX="1.24968mm" pcbY="-2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin11"]} pcbX="0.749808mm" pcbY="-2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin10"]} pcbX="0.249682mm" pcbY="-2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin9"]} pcbX="-0.25019mm" pcbY="-2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin8"]} pcbX="-0.750316mm" pcbY="-2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin7"]} pcbX="-1.250188mm" pcbY="-2.048129mm" width="0.299974mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="-2.041652mm" pcbY="-1.249807mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="-2.041652mm" pcbY="-0.749935mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-2.041652mm" pcbY="-0.249809mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="-2.041652mm" pcbY="0.250063mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-2.041652mm" pcbY="0.750189mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-2.041652mm" pcbY="1.250061mm" width="0.7999984mm" height="0.2999994mm" shape="rect" />
<silkscreenpath route={[{"x":-2.104491600000074,"y":1.7001743999999235},{"x":-2.104491600000074,"y":2.1001481999999214},{"x":-1.7001743999999235,"y":2.1000212000000147}]} />
<silkscreenpath route={[{"x":-2.1001990000000887,"y":-1.6998696000000564},{"x":-2.1001990000000887,"y":-2.099970399999961},{"x":-1.7001743999999235,"y":-2.099970399999961}]} />
<silkscreenpath route={[{"x":2.0997926000000007,"y":-1.5999460000000454},{"x":2.0997926000000007,"y":-2.099970399999961},{"x":1.699818799999889,"y":-2.099970399999961}]} />
<silkscreenpath route={[{"x":1.6954753999999639,"y":2.1001481999999214},{"x":2.095449199999962,"y":2.1001481999999214},{"x":2.095449199999962,"y":1.7001743999999235}]} />
<silkscreencircle pcbX="-2.540254mm" pcbY="1.905127mm" radius="0.127mm" />
<silkscreentext text="{NAME}" pcbX="-0.126238mm" pcbY="3.448687mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-2.691651200000024,"y":2.698128200000042},{"x":2.69165119999991,"y":2.698128200000042},{"x":2.69165119999991,"y":-2.698128200000042},{"x":-2.691651200000024,"y":-2.698128200000042},{"x":-2.691651200000024,"y":2.698128200000042}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C374063.obj?uuid=f9f49049b1e946aebac8a4ca9e490364",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C374063.step?uuid=f9f49049b1e946aebac8a4ca9e490364",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0.00013970000009067007, y: -0.00005079999993995443, z: -0.02 },
      }}
      {...props}
    />
  )
}