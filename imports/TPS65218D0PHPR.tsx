import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["IN_DCDC1"],
  pin2: ["SDA"],
  pin3: ["SCL"],
  pin4: ["LDO1"],
  pin5: ["IN_LDO1"],
  pin6: ["IN_LS3"],
  pin7: ["LS3"],
  pin8: ["PGOOD"],
  pin9: ["AC_DET"],
  pin10: ["nPFO"],
  pin11: ["GPIO1"],
  pin12: ["IN_DCDC4"],
  pin13: ["L4A"],
  pin14: ["L4B"],
  pin15: ["DCDC4"],
  pin16: ["PFI"],
  pin17: ["DC34_SEL"],
  pin18: ["IN_nCC"],
  pin19: ["PGOOD_BU"],
  pin20: ["L5"],
  pin21: ["FB5"],
  pin22: ["FB6"],
  pin23: ["L6"],
  pin24: ["SYS_BU"],
  pin25: ["CC"],
  pin26: ["GPIO3"],
  pin27: ["IN_BU"],
  pin28: ["NC1"],
  pin29: ["NC2"],
  pin30: ["LS1"],
  pin31: ["IN_LS1"],
  pin32: ["IN_LS2"],
  pin33: ["LS2"],
  pin34: ["GPO2"],
  pin35: ["INT_LDO"],
  pin36: ["IN_BIAS"],
  pin37: ["IN_DCDC3"],
  pin38: ["L3"],
  pin39: ["FB3"],
  pin40: ["nWAKEUP"],
  pin41: ["FB2"],
  pin42: ["L2"],
  pin43: ["IN_DCDC2"],
  pin44: ["PB"],
  pin45: ["nINT"],
  pin46: ["PWR_EN"],
  pin47: ["FB1"],
  pin48: ["L1"],
  pin49: ["EP"]
} as const

const pinAttributes = {
  pin28: {doNotConnect: true},
  pin29: {doNotConnect: true}
} as const

export const TPS65218D0PHPR = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C2659099"
  ]
}}
      manufacturerPartNumber="TPS65218D0PHPR"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-2.750058mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin2"]} pcbX="-2.249932mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin3"]} pcbX="-1.75006mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin4"]} pcbX="-1.249934mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin5"]} pcbX="-0.750062mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin6"]} pcbX="-0.249936mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin7"]} pcbX="0.249936mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin8"]} pcbX="0.750062mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin9"]} pcbX="1.249934mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin10"]} pcbX="1.75006mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin11"]} pcbX="2.249932mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin12"]} pcbX="2.750058mm" pcbY="-4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin13"]} pcbX="4.19989mm" pcbY="-2.750058mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin14"]} pcbX="4.19989mm" pcbY="-2.249932mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin15"]} pcbX="4.19989mm" pcbY="-1.75006mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin16"]} pcbX="4.19989mm" pcbY="-1.249934mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin17"]} pcbX="4.19989mm" pcbY="-0.750062mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin18"]} pcbX="4.19989mm" pcbY="-0.249936mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin19"]} pcbX="4.19989mm" pcbY="0.249936mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin20"]} pcbX="4.19989mm" pcbY="0.750062mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin21"]} pcbX="4.19989mm" pcbY="1.249934mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin22"]} pcbX="4.19989mm" pcbY="1.75006mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin23"]} pcbX="4.19989mm" pcbY="2.249932mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin24"]} pcbX="4.19989mm" pcbY="2.750058mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin25"]} pcbX="2.750058mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin26"]} pcbX="2.249932mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin27"]} pcbX="1.75006mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin28"]} pcbX="1.249934mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin29"]} pcbX="0.750062mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin30"]} pcbX="0.249936mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin31"]} pcbX="-0.249936mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin32"]} pcbX="-0.750062mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin33"]} pcbX="-1.249934mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin34"]} pcbX="-1.75006mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin35"]} pcbX="-2.249932mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin36"]} pcbX="-2.750058mm" pcbY="4.19989mm" width="0.2800096mm" height="1.5999968mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin37"]} pcbX="-4.19989mm" pcbY="2.750058mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin38"]} pcbX="-4.19989mm" pcbY="2.249932mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin39"]} pcbX="-4.19989mm" pcbY="1.75006mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin40"]} pcbX="-4.19989mm" pcbY="1.249934mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin41"]} pcbX="-4.19989mm" pcbY="0.750062mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin42"]} pcbX="-4.19989mm" pcbY="0.249936mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin43"]} pcbX="-4.19989mm" pcbY="-0.249936mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin44"]} pcbX="-4.19989mm" pcbY="-0.750062mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin45"]} pcbX="-4.19989mm" pcbY="-1.249934mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin46"]} pcbX="-4.19989mm" pcbY="-1.75006mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin47"]} pcbX="-4.19989mm" pcbY="-2.249932mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin48"]} pcbX="-4.19989mm" pcbY="-2.750058mm" width="1.5999968mm" height="0.2800096mm" radius="0.1400048mm" shape="pill" />
<smtpad portHints={["pin49"]} pcbX="0mm" pcbY="0mm" width="4.3999912mm" height="4.3999912mm" shape="rect" />
<silkscreenpath route={[{"x":-3.576218400000016,"y":3.080486599999972},{"x":-3.576218400000016,"y":3.576218400000016},{"x":-3.0804865999998583,"y":3.576218400000016}]} />
<silkscreenpath route={[{"x":3.576218400000016,"y":3.080486599999972},{"x":3.576218400000016,"y":3.576218400000016},{"x":3.0804866000000857,"y":3.576218400000016}]} />
<silkscreenpath route={[{"x":-3.576218400000016,"y":-3.080486599999972},{"x":-3.576218400000016,"y":-3.576218400000016},{"x":-3.0804865999998583,"y":-3.576218400000016}]} />
<silkscreenpath route={[{"x":3.576218400000016,"y":-3.080486599999972},{"x":3.576218400000016,"y":-3.576218400000016},{"x":3.0804866000000857,"y":-3.576218400000016}]} />
<silkscreenpath route={[{"x":-3.1713931999998977,"y":-3.1713931999998977},{"x":-3.1713931999998977,"y":3.1713932000000113},{"x":3.1713932000000113,"y":3.1713932000000113},{"x":3.1713932000000113,"y":-3.1713931999998977},{"x":-3.1713931999998977,"y":-3.1713931999998977}]} />
<silkscreencircle pcbX="-3.302mm" pcbY="-4.064mm" radius="0.100076mm" />
<silkscreentext text="{NAME}" pcbX="0.0127mm" pcbY="5.8514mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-5.101400000000012,"y":5.101399999999899},{"x":5.126800000000003,"y":5.101399999999899},{"x":5.126800000000003,"y":-5.304599999999937},{"x":-5.101400000000012,"y":-5.304599999999937},{"x":-5.101400000000012,"y":5.101399999999899}]} />
      </footprint>}
      
      {...props}
    />
  )
}