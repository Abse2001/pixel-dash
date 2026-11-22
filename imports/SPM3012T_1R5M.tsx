import type { InductorProps } from "@tscircuit/props"

export const SPM3012T_1R5M = (props: Omit<InductorProps, "inductance">) => {
  return (
    <inductor
      inductance="1.5uH"
      supplierPartNumbers={{
  "jlcpcb": [
    "C3221570"
  ]
}}
      manufacturerPartNumber="SPM3012T-1R5M"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-1.299972mm" pcbY="0mm" width="1.0999978mm" height="1.7999964mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="1.299972mm" pcbY="0mm" width="1.0999978mm" height="1.7999964mm" shape="rect" />
<silkscreenpath route={[{"x":1.6000222000000122,"y":-1.4999970000000076},{"x":-1.6000222000000122,"y":-1.4999970000000076}]} />
<silkscreenpath route={[{"x":-1.6000222000000122,"y":1.4999969999998939},{"x":1.6000222000000122,"y":1.4999969999998939}]} />
<silkscreenpath route={[{"x":-1.6000222000000122,"y":1.4999969999998939},{"x":-1.6000222000000122,"y":1.131138200000123}]} />
<silkscreenpath route={[{"x":-1.6000222000000122,"y":-1.1311382000000094},{"x":-1.6000222000000122,"y":-1.4999970000000076}]} />
<silkscreenpath route={[{"x":1.6000222000000122,"y":-1.4999970000000076},{"x":1.6000222000000122,"y":-1.1311382000000094}]} />
<silkscreenpath route={[{"x":1.6000222000000122,"y":1.131138200000123},{"x":1.6000222000000122,"y":1.4999969999998939}]} />
<silkscreentext text="{NAME}" pcbX="0mm" pcbY="2.4986mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-2.0999709000000166,"y":1.7499969999998939},{"x":2.099970899999903,"y":1.7499969999998939},{"x":2.099970899999903,"y":-1.7499970000000076},{"x":-2.0999709000000166,"y":-1.7499970000000076},{"x":-2.0999709000000166,"y":1.7499969999998939}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C3221570.obj?uuid=e335a0114ae04b7c89ce09fa44b9fb39",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C3221570.step?uuid=e335a0114ae04b7c89ce09fa44b9fb39",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: 0, z: 0 },
      }}
      {...props}
    />
  )
}