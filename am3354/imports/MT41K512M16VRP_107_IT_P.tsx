import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["A1"],
  pin2: ["B1"],
  pin3: ["C1"],
  pin4: ["D1"],
  pin5: ["E1"],
  pin6: ["F1"],
  pin7: ["G1"],
  pin8: ["H1"],
  pin9: ["J1"],
  pin10: ["K1"],
  pin11: ["L1"],
  pin12: ["M1"],
  pin13: ["N1"],
  pin14: ["P1"],
  pin15: ["R1"],
  pin16: ["T1"],
  pin17: ["A2"],
  pin18: ["B2"],
  pin19: ["C2"],
  pin20: ["D2"],
  pin21: ["E2"],
  pin22: ["F2"],
  pin23: ["G2"],
  pin24: ["H2"],
  pin25: ["J2"],
  pin26: ["K2"],
  pin27: ["L2"],
  pin28: ["M2"],
  pin29: ["N2"],
  pin30: ["P2"],
  pin31: ["R2"],
  pin32: ["T2"],
  pin33: ["A3"],
  pin34: ["B3"],
  pin35: ["C3"],
  pin36: ["D3"],
  pin37: ["E3"],
  pin38: ["F3"],
  pin39: ["G3"],
  pin40: ["H3"],
  pin41: ["J3"],
  pin42: ["K3"],
  pin43: ["L3"],
  pin44: ["M3"],
  pin45: ["N3"],
  pin46: ["P3"],
  pin47: ["R3"],
  pin48: ["T3"],
  pin49: ["A7"],
  pin50: ["B7"],
  pin51: ["C7"],
  pin52: ["D7"],
  pin53: ["E7"],
  pin54: ["F7"],
  pin55: ["G7"],
  pin56: ["H7"],
  pin57: ["J7"],
  pin58: ["K7"],
  pin59: ["L7"],
  pin60: ["M7"],
  pin61: ["N7"],
  pin62: ["P7"],
  pin63: ["R7"],
  pin64: ["T7"],
  pin65: ["A8"],
  pin66: ["B8"],
  pin67: ["C8"],
  pin68: ["D8"],
  pin69: ["E8"],
  pin70: ["F8"],
  pin71: ["G8"],
  pin72: ["H8"],
  pin73: ["J8"],
  pin74: ["K8"],
  pin75: ["L8"],
  pin76: ["M8"],
  pin77: ["N8"],
  pin78: ["P8"],
  pin79: ["R8"],
  pin80: ["T8"],
  pin81: ["A9"],
  pin82: ["B9"],
  pin83: ["C9"],
  pin84: ["D9"],
  pin85: ["E9"],
  pin86: ["F9"],
  pin87: ["G9"],
  pin88: ["H9"],
  pin89: ["J9"],
  pin90: ["K9"],
  pin91: ["L9"],
  pin92: ["M9"],
  pin93: ["N9"],
  pin94: ["P9"],
  pin95: ["R9"],
  pin96: ["T9"]
} as const

export const MT41K512M16VRP_107_IT_P = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C2831669"
  ]
}}
      manufacturerPartNumber="MT41K512M16VRP-107 IT:P"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-3.199892mm" pcbY="5.999988mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin2"]} pcbX="-3.199892mm" pcbY="5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin3"]} pcbX="-3.199892mm" pcbY="4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin4"]} pcbX="-3.199892mm" pcbY="3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin5"]} pcbX="-3.199892mm" pcbY="2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin6"]} pcbX="-3.199892mm" pcbY="1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin7"]} pcbX="-3.199892mm" pcbY="1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin8"]} pcbX="-3.199892mm" pcbY="0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin9"]} pcbX="-3.199892mm" pcbY="-0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin10"]} pcbX="-3.199892mm" pcbY="-1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin11"]} pcbX="-3.199892mm" pcbY="-1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin12"]} pcbX="-3.199892mm" pcbY="-2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin13"]} pcbX="-3.199892mm" pcbY="-3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin14"]} pcbX="-3.199892mm" pcbY="-4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin15"]} pcbX="-3.199892mm" pcbY="-5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin16"]} pcbX="-3.199892mm" pcbY="-5.999988mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin17"]} pcbX="-2.400046mm" pcbY="5.999988mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin18"]} pcbX="-2.400046mm" pcbY="5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin19"]} pcbX="-2.400046mm" pcbY="4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin20"]} pcbX="-2.400046mm" pcbY="3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin21"]} pcbX="-2.400046mm" pcbY="2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin22"]} pcbX="-2.400046mm" pcbY="1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin23"]} pcbX="-2.400046mm" pcbY="1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin24"]} pcbX="-2.400046mm" pcbY="0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin25"]} pcbX="-2.400046mm" pcbY="-0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin26"]} pcbX="-2.400046mm" pcbY="-1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin27"]} pcbX="-2.400046mm" pcbY="-1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin28"]} pcbX="-2.400046mm" pcbY="-2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin29"]} pcbX="-2.400046mm" pcbY="-3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin30"]} pcbX="-2.400046mm" pcbY="-4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin31"]} pcbX="-2.400046mm" pcbY="-5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin32"]} pcbX="-2.400046mm" pcbY="-5.999988mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin33"]} pcbX="-1.599946mm" pcbY="5.999988mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin34"]} pcbX="-1.599946mm" pcbY="5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin35"]} pcbX="-1.599946mm" pcbY="4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin36"]} pcbX="-1.599946mm" pcbY="3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin37"]} pcbX="-1.599946mm" pcbY="2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin38"]} pcbX="-1.599946mm" pcbY="1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin39"]} pcbX="-1.599946mm" pcbY="1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin40"]} pcbX="-1.599946mm" pcbY="0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin41"]} pcbX="-1.599946mm" pcbY="-0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin42"]} pcbX="-1.599946mm" pcbY="-1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin43"]} pcbX="-1.599946mm" pcbY="-1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin44"]} pcbX="-1.599946mm" pcbY="-2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin45"]} pcbX="-1.599946mm" pcbY="-3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin46"]} pcbX="-1.599946mm" pcbY="-4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin47"]} pcbX="-1.599946mm" pcbY="-5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin48"]} pcbX="-1.599946mm" pcbY="-5.999988mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin49"]} pcbX="1.599946mm" pcbY="5.999988mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin50"]} pcbX="1.599946mm" pcbY="5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin51"]} pcbX="1.599946mm" pcbY="4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin52"]} pcbX="1.599946mm" pcbY="3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin53"]} pcbX="1.599946mm" pcbY="2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin54"]} pcbX="1.599946mm" pcbY="1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin55"]} pcbX="1.599946mm" pcbY="1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin56"]} pcbX="1.599946mm" pcbY="0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin57"]} pcbX="1.599946mm" pcbY="-0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin58"]} pcbX="1.599946mm" pcbY="-1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin59"]} pcbX="1.599946mm" pcbY="-1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin60"]} pcbX="1.599946mm" pcbY="-2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin61"]} pcbX="1.599946mm" pcbY="-3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin62"]} pcbX="1.599946mm" pcbY="-4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin63"]} pcbX="1.599946mm" pcbY="-5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin64"]} pcbX="1.599946mm" pcbY="-5.999988mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin65"]} pcbX="2.400046mm" pcbY="5.999988mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin66"]} pcbX="2.400046mm" pcbY="5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin67"]} pcbX="2.400046mm" pcbY="4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin68"]} pcbX="2.400046mm" pcbY="3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin69"]} pcbX="2.400046mm" pcbY="2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin70"]} pcbX="2.400046mm" pcbY="1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin71"]} pcbX="2.400046mm" pcbY="1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin72"]} pcbX="2.400046mm" pcbY="0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin73"]} pcbX="2.400046mm" pcbY="-0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin74"]} pcbX="2.400046mm" pcbY="-1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin75"]} pcbX="2.400046mm" pcbY="-1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin76"]} pcbX="2.400046mm" pcbY="-2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin77"]} pcbX="2.400046mm" pcbY="-3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin78"]} pcbX="2.400046mm" pcbY="-4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin79"]} pcbX="2.400046mm" pcbY="-5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin80"]} pcbX="2.400046mm" pcbY="-5.999988mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin81"]} pcbX="3.199892mm" pcbY="5.999988mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin82"]} pcbX="3.199892mm" pcbY="5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin83"]} pcbX="3.199892mm" pcbY="4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin84"]} pcbX="3.199892mm" pcbY="3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin85"]} pcbX="3.199892mm" pcbY="2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin86"]} pcbX="3.199892mm" pcbY="1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin87"]} pcbX="3.199892mm" pcbY="1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin88"]} pcbX="3.199892mm" pcbY="0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin89"]} pcbX="3.199892mm" pcbY="-0.40005mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin90"]} pcbX="3.199892mm" pcbY="-1.199896mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin91"]} pcbX="3.199892mm" pcbY="-1.999996mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin92"]} pcbX="3.199892mm" pcbY="-2.800096mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin93"]} pcbX="3.199892mm" pcbY="-3.599942mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin94"]} pcbX="3.199892mm" pcbY="-4.400042mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin95"]} pcbX="3.199892mm" pcbY="-5.199888mm" radius="0.1970024mm" shape="circle" />
<smtpad portHints={["pin96"]} pcbX="3.199892mm" pcbY="-5.999988mm" radius="0.1970024mm" shape="circle" />
<silkscreenpath route={[{"x":-4.076191999999992,"y":7.0762114000001475},{"x":4.076191999999992,"y":7.0762114000001475},{"x":4.076191999999992,"y":-7.076211400000034},{"x":-4.076191999999992,"y":-7.076211400000034},{"x":-4.076191999999992,"y":7.0762114000001475}]} />
<silkscreenpath route={[{"x":-3.4361882000000605,"y":7.304811400000062},{"x":-4.30479200000002,"y":7.304811400000062},{"x":-4.30479200000002,"y":6.436207599999989}]} />
<silkscreencircle pcbX="-4.445mm" pcbY="6.477mm" radius="0.100076mm" />
<silkscreentext text="{NAME}" pcbX="-0.2413mm" pcbY="8.3152mm" anchorAlignment="center" fontSize="1mm" />
<fabricationnotepath route={[{"x":-3.436188199999947,"y":7.076211400000034},{"x":-4.076191999999992,"y":6.436207599999989},{"x":-4.076191999999992,"y":7.076211400000034},{"x":-3.436188199999947,"y":7.076211400000034}]} strokeWidth="0mm" isFilled hasStroke={false} />
<courtyardoutline outline={[{"x":-4.24999200000002,"y":7.249986000000149},{"x":4.2499919999999065,"y":7.249986000000149},{"x":4.2499919999999065,"y":-7.249986000000035},{"x":-4.24999200000002,"y":-7.249986000000035},{"x":-4.24999200000002,"y":7.249986000000149}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C2831669.obj?uuid=725f4b734fb64131b17d53834ab96bec",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C2831669.step?uuid=725f4b734fb64131b17d53834ab96bec",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: 0, z: 0 },
      }}
      {...props}
    />
  )
}