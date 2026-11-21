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
  pin17: ["U1"],
  pin18: ["V1"],
  pin19: ["A2"],
  pin20: ["B2"],
  pin21: ["C2"],
  pin22: ["D2"],
  pin23: ["E2"],
  pin24: ["F2"],
  pin25: ["G2"],
  pin26: ["H2"],
  pin27: ["J2"],
  pin28: ["K2"],
  pin29: ["L2"],
  pin30: ["M2"],
  pin31: ["N2"],
  pin32: ["P2"],
  pin33: ["R2"],
  pin34: ["T2"],
  pin35: ["U2"],
  pin36: ["V2"],
  pin37: ["A3"],
  pin38: ["B3"],
  pin39: ["C3"],
  pin40: ["D3"],
  pin41: ["E3"],
  pin42: ["F3"],
  pin43: ["G3"],
  pin44: ["H3"],
  pin45: ["J3"],
  pin46: ["K3"],
  pin47: ["L3"],
  pin48: ["M3"],
  pin49: ["N3"],
  pin50: ["P3"],
  pin51: ["R3"],
  pin52: ["T3"],
  pin53: ["U3"],
  pin54: ["V3"],
  pin55: ["A4"],
  pin56: ["B4"],
  pin57: ["C4"],
  pin58: ["D4"],
  pin59: ["E4"],
  pin60: ["F4"],
  pin61: ["G4"],
  pin62: ["H4"],
  pin63: ["J4"],
  pin64: ["K4"],
  pin65: ["L4"],
  pin66: ["M4"],
  pin67: ["N4"],
  pin68: ["P4"],
  pin69: ["R4"],
  pin70: ["T4"],
  pin71: ["U4"],
  pin72: ["V4"],
  pin73: ["A5"],
  pin74: ["B5"],
  pin75: ["C5"],
  pin76: ["D5"],
  pin77: ["E5"],
  pin78: ["F5"],
  pin79: ["G5"],
  pin80: ["H5"],
  pin81: ["J5"],
  pin82: ["K5"],
  pin83: ["L5"],
  pin84: ["M5"],
  pin85: ["N5"],
  pin86: ["P5"],
  pin87: ["R5"],
  pin88: ["T5"],
  pin89: ["U5"],
  pin90: ["V5"],
  pin91: ["A6"],
  pin92: ["B6"],
  pin93: ["C6"],
  pin94: ["D6"],
  pin95: ["E6"],
  pin96: ["F6"],
  pin97: ["G6"],
  pin98: ["H6"],
  pin99: ["J6"],
  pin100: ["K6"],
  pin101: ["L6"],
  pin102: ["M6"],
  pin103: ["N6"],
  pin104: ["P6"],
  pin105: ["R6"],
  pin106: ["T6"],
  pin107: ["U6"],
  pin108: ["V6"],
  pin109: ["A7"],
  pin110: ["B7"],
  pin111: ["C7"],
  pin112: ["D7"],
  pin113: ["E7"],
  pin114: ["F7"],
  pin115: ["G7"],
  pin116: ["H7"],
  pin117: ["J7"],
  pin118: ["K7"],
  pin119: ["L7"],
  pin120: ["M7"],
  pin121: ["N7"],
  pin122: ["P7"],
  pin123: ["R7"],
  pin124: ["T7"],
  pin125: ["U7"],
  pin126: ["V7"],
  pin127: ["A8"],
  pin128: ["B8"],
  pin129: ["C8"],
  pin130: ["D8"],
  pin131: ["E8"],
  pin132: ["F8"],
  pin133: ["G8"],
  pin134: ["H8"],
  pin135: ["J8"],
  pin136: ["K8"],
  pin137: ["L8"],
  pin138: ["M8"],
  pin139: ["N8"],
  pin140: ["P8"],
  pin141: ["R8"],
  pin142: ["T8"],
  pin143: ["U8"],
  pin144: ["V8"],
  pin145: ["A9"],
  pin146: ["B9"],
  pin147: ["C9"],
  pin148: ["D9"],
  pin149: ["E9"],
  pin150: ["F9"],
  pin151: ["G9"],
  pin152: ["H9"],
  pin153: ["J9"],
  pin154: ["K9"],
  pin155: ["L9"],
  pin156: ["M9"],
  pin157: ["N9"],
  pin158: ["P9"],
  pin159: ["R9"],
  pin160: ["T9"],
  pin161: ["U9"],
  pin162: ["V9"],
  pin163: ["A10"],
  pin164: ["B10"],
  pin165: ["C10"],
  pin166: ["D10"],
  pin167: ["E10"],
  pin168: ["F10"],
  pin169: ["G10"],
  pin170: ["H10"],
  pin171: ["J10"],
  pin172: ["K10"],
  pin173: ["L10"],
  pin174: ["M10"],
  pin175: ["N10"],
  pin176: ["P10"],
  pin177: ["R10"],
  pin178: ["T10"],
  pin179: ["U10"],
  pin180: ["V10"],
  pin181: ["A11"],
  pin182: ["B11"],
  pin183: ["C11"],
  pin184: ["D11"],
  pin185: ["E11"],
  pin186: ["F11"],
  pin187: ["G11"],
  pin188: ["H11"],
  pin189: ["J11"],
  pin190: ["K11"],
  pin191: ["L11"],
  pin192: ["M11"],
  pin193: ["N11"],
  pin194: ["P11"],
  pin195: ["R11"],
  pin196: ["T11"],
  pin197: ["U11"],
  pin198: ["V11"],
  pin199: ["A12"],
  pin200: ["B12"],
  pin201: ["C12"],
  pin202: ["D12"],
  pin203: ["E12"],
  pin204: ["F12"],
  pin205: ["G12"],
  pin206: ["H12"],
  pin207: ["J12"],
  pin208: ["K12"],
  pin209: ["L12"],
  pin210: ["M12"],
  pin211: ["N12"],
  pin212: ["P12"],
  pin213: ["R12"],
  pin214: ["T12"],
  pin215: ["U12"],
  pin216: ["V12"],
  pin217: ["A13"],
  pin218: ["B13"],
  pin219: ["C13"],
  pin220: ["D13"],
  pin221: ["E13"],
  pin222: ["F13"],
  pin223: ["G13"],
  pin224: ["H13"],
  pin225: ["J13"],
  pin226: ["K13"],
  pin227: ["L13"],
  pin228: ["M13"],
  pin229: ["N13"],
  pin230: ["P13"],
  pin231: ["R13"],
  pin232: ["T13"],
  pin233: ["U13"],
  pin234: ["V13"],
  pin235: ["A14"],
  pin236: ["B14"],
  pin237: ["C14"],
  pin238: ["D14"],
  pin239: ["E14"],
  pin240: ["F14"],
  pin241: ["G14"],
  pin242: ["H14"],
  pin243: ["J14"],
  pin244: ["K14"],
  pin245: ["L14"],
  pin246: ["M14"],
  pin247: ["N14"],
  pin248: ["P14"],
  pin249: ["R14"],
  pin250: ["T14"],
  pin251: ["U14"],
  pin252: ["V14"],
  pin253: ["A15"],
  pin254: ["B15"],
  pin255: ["C15"],
  pin256: ["D15"],
  pin257: ["E15"],
  pin258: ["F15"],
  pin259: ["G15"],
  pin260: ["H15"],
  pin261: ["J15"],
  pin262: ["K15"],
  pin263: ["L15"],
  pin264: ["M15"],
  pin265: ["N15"],
  pin266: ["P15"],
  pin267: ["R15"],
  pin268: ["T15"],
  pin269: ["U15"],
  pin270: ["V15"],
  pin271: ["A16"],
  pin272: ["B16"],
  pin273: ["C16"],
  pin274: ["D16"],
  pin275: ["E16"],
  pin276: ["F16"],
  pin277: ["G16"],
  pin278: ["H16"],
  pin279: ["J16"],
  pin280: ["K16"],
  pin281: ["L16"],
  pin282: ["M16"],
  pin283: ["N16"],
  pin284: ["P16"],
  pin285: ["R16"],
  pin286: ["T16"],
  pin287: ["U16"],
  pin288: ["V16"],
  pin289: ["A17"],
  pin290: ["B17"],
  pin291: ["C17"],
  pin292: ["D17"],
  pin293: ["E17"],
  pin294: ["F17"],
  pin295: ["G17"],
  pin296: ["H17"],
  pin297: ["J17"],
  pin298: ["K17"],
  pin299: ["L17"],
  pin300: ["M17"],
  pin301: ["N17"],
  pin302: ["P17"],
  pin303: ["R17"],
  pin304: ["T17"],
  pin305: ["U17"],
  pin306: ["V17"],
  pin307: ["A18"],
  pin308: ["B18"],
  pin309: ["C18"],
  pin310: ["D18"],
  pin311: ["E18"],
  pin312: ["F18"],
  pin313: ["G18"],
  pin314: ["H18"],
  pin315: ["J18"],
  pin316: ["K18"],
  pin317: ["L18"],
  pin318: ["M18"],
  pin319: ["N18"],
  pin320: ["P18"],
  pin321: ["R18"],
  pin322: ["T18"],
  pin323: ["U18"],
  pin324: ["V18"]
} as const

export const AM3354BZCZD80 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C128768"
  ]
}}
      manufacturerPartNumber="AM3354BZCZD80"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-6.800088mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin2"]} pcbX="-6.800088mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin3"]} pcbX="-6.800088mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin4"]} pcbX="-6.800088mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin5"]} pcbX="-6.800088mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin6"]} pcbX="-6.800088mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin7"]} pcbX="-6.800088mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin8"]} pcbX="-6.800088mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin9"]} pcbX="-6.800088mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin10"]} pcbX="-6.800088mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin11"]} pcbX="-6.800088mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin12"]} pcbX="-6.800088mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin13"]} pcbX="-6.800088mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin14"]} pcbX="-6.800088mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin15"]} pcbX="-6.800088mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin16"]} pcbX="-6.800088mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin17"]} pcbX="-6.800088mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin18"]} pcbX="-6.800088mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin19"]} pcbX="-5.999988mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin20"]} pcbX="-5.999988mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin21"]} pcbX="-5.999988mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin22"]} pcbX="-5.999988mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin23"]} pcbX="-5.999988mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin24"]} pcbX="-5.999988mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin25"]} pcbX="-5.999988mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin26"]} pcbX="-5.999988mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin27"]} pcbX="-5.999988mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin28"]} pcbX="-5.999988mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin29"]} pcbX="-5.999988mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin30"]} pcbX="-5.999988mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin31"]} pcbX="-5.999988mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin32"]} pcbX="-5.999988mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin33"]} pcbX="-5.999988mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin34"]} pcbX="-5.999988mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin35"]} pcbX="-5.999988mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin36"]} pcbX="-5.999988mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin37"]} pcbX="-5.199888mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin38"]} pcbX="-5.199888mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin39"]} pcbX="-5.199888mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin40"]} pcbX="-5.199888mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin41"]} pcbX="-5.199888mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin42"]} pcbX="-5.199888mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin43"]} pcbX="-5.199888mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin44"]} pcbX="-5.199888mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin45"]} pcbX="-5.199888mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin46"]} pcbX="-5.199888mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin47"]} pcbX="-5.199888mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin48"]} pcbX="-5.199888mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin49"]} pcbX="-5.199888mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin50"]} pcbX="-5.199888mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin51"]} pcbX="-5.199888mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin52"]} pcbX="-5.199888mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin53"]} pcbX="-5.199888mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin54"]} pcbX="-5.199888mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin55"]} pcbX="-4.400042mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin56"]} pcbX="-4.400042mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin57"]} pcbX="-4.400042mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin58"]} pcbX="-4.400042mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin59"]} pcbX="-4.400042mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin60"]} pcbX="-4.400042mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin61"]} pcbX="-4.400042mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin62"]} pcbX="-4.400042mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin63"]} pcbX="-4.400042mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin64"]} pcbX="-4.400042mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin65"]} pcbX="-4.400042mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin66"]} pcbX="-4.400042mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin67"]} pcbX="-4.400042mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin68"]} pcbX="-4.400042mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin69"]} pcbX="-4.400042mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin70"]} pcbX="-4.400042mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin71"]} pcbX="-4.400042mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin72"]} pcbX="-4.400042mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin73"]} pcbX="-3.599942mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin74"]} pcbX="-3.599942mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin75"]} pcbX="-3.599942mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin76"]} pcbX="-3.599942mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin77"]} pcbX="-3.599942mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin78"]} pcbX="-3.599942mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin79"]} pcbX="-3.599942mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin80"]} pcbX="-3.599942mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin81"]} pcbX="-3.599942mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin82"]} pcbX="-3.599942mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin83"]} pcbX="-3.599942mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin84"]} pcbX="-3.599942mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin85"]} pcbX="-3.599942mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin86"]} pcbX="-3.599942mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin87"]} pcbX="-3.599942mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin88"]} pcbX="-3.599942mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin89"]} pcbX="-3.599942mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin90"]} pcbX="-3.599942mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin91"]} pcbX="-2.800096mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin92"]} pcbX="-2.800096mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin93"]} pcbX="-2.800096mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin94"]} pcbX="-2.800096mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin95"]} pcbX="-2.800096mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin96"]} pcbX="-2.800096mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin97"]} pcbX="-2.800096mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin98"]} pcbX="-2.800096mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin99"]} pcbX="-2.800096mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin100"]} pcbX="-2.800096mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin101"]} pcbX="-2.800096mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin102"]} pcbX="-2.800096mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin103"]} pcbX="-2.800096mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin104"]} pcbX="-2.800096mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin105"]} pcbX="-2.800096mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin106"]} pcbX="-2.800096mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin107"]} pcbX="-2.800096mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin108"]} pcbX="-2.800096mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin109"]} pcbX="-1.999996mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin110"]} pcbX="-1.999996mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin111"]} pcbX="-1.999996mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin112"]} pcbX="-1.999996mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin113"]} pcbX="-1.999996mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin114"]} pcbX="-1.999996mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin115"]} pcbX="-1.999996mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin116"]} pcbX="-1.999996mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin117"]} pcbX="-1.999996mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin118"]} pcbX="-1.999996mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin119"]} pcbX="-1.999996mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin120"]} pcbX="-1.999996mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin121"]} pcbX="-1.999996mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin122"]} pcbX="-1.999996mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin123"]} pcbX="-1.999996mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin124"]} pcbX="-1.999996mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin125"]} pcbX="-1.999996mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin126"]} pcbX="-1.999996mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin127"]} pcbX="-1.199896mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin128"]} pcbX="-1.199896mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin129"]} pcbX="-1.199896mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin130"]} pcbX="-1.199896mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin131"]} pcbX="-1.199896mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin132"]} pcbX="-1.199896mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin133"]} pcbX="-1.199896mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin134"]} pcbX="-1.199896mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin135"]} pcbX="-1.199896mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin136"]} pcbX="-1.199896mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin137"]} pcbX="-1.199896mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin138"]} pcbX="-1.199896mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin139"]} pcbX="-1.199896mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin140"]} pcbX="-1.199896mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin141"]} pcbX="-1.199896mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin142"]} pcbX="-1.199896mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin143"]} pcbX="-1.199896mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin144"]} pcbX="-1.199896mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin145"]} pcbX="-0.40005mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin146"]} pcbX="-0.40005mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin147"]} pcbX="-0.40005mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin148"]} pcbX="-0.40005mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin149"]} pcbX="-0.40005mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin150"]} pcbX="-0.40005mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin151"]} pcbX="-0.40005mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin152"]} pcbX="-0.40005mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin153"]} pcbX="-0.40005mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin154"]} pcbX="-0.40005mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin155"]} pcbX="-0.40005mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin156"]} pcbX="-0.40005mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin157"]} pcbX="-0.40005mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin158"]} pcbX="-0.40005mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin159"]} pcbX="-0.40005mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin160"]} pcbX="-0.40005mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin161"]} pcbX="-0.40005mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin162"]} pcbX="-0.40005mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin163"]} pcbX="0.40005mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin164"]} pcbX="0.40005mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin165"]} pcbX="0.40005mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin166"]} pcbX="0.40005mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin167"]} pcbX="0.40005mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin168"]} pcbX="0.40005mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin169"]} pcbX="0.40005mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin170"]} pcbX="0.40005mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin171"]} pcbX="0.40005mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin172"]} pcbX="0.40005mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin173"]} pcbX="0.40005mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin174"]} pcbX="0.40005mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin175"]} pcbX="0.40005mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin176"]} pcbX="0.40005mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin177"]} pcbX="0.40005mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin178"]} pcbX="0.40005mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin179"]} pcbX="0.40005mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin180"]} pcbX="0.40005mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin181"]} pcbX="1.199896mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin182"]} pcbX="1.199896mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin183"]} pcbX="1.199896mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin184"]} pcbX="1.199896mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin185"]} pcbX="1.199896mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin186"]} pcbX="1.199896mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin187"]} pcbX="1.199896mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin188"]} pcbX="1.199896mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin189"]} pcbX="1.199896mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin190"]} pcbX="1.199896mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin191"]} pcbX="1.199896mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin192"]} pcbX="1.199896mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin193"]} pcbX="1.199896mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin194"]} pcbX="1.199896mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin195"]} pcbX="1.199896mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin196"]} pcbX="1.199896mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin197"]} pcbX="1.199896mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin198"]} pcbX="1.199896mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin199"]} pcbX="1.999996mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin200"]} pcbX="1.999996mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin201"]} pcbX="1.999996mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin202"]} pcbX="1.999996mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin203"]} pcbX="1.999996mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin204"]} pcbX="1.999996mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin205"]} pcbX="1.999996mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin206"]} pcbX="1.999996mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin207"]} pcbX="1.999996mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin208"]} pcbX="1.999996mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin209"]} pcbX="1.999996mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin210"]} pcbX="1.999996mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin211"]} pcbX="1.999996mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin212"]} pcbX="1.999996mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin213"]} pcbX="1.999996mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin214"]} pcbX="1.999996mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin215"]} pcbX="1.999996mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin216"]} pcbX="1.999996mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin217"]} pcbX="2.800096mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin218"]} pcbX="2.800096mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin219"]} pcbX="2.800096mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin220"]} pcbX="2.800096mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin221"]} pcbX="2.800096mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin222"]} pcbX="2.800096mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin223"]} pcbX="2.800096mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin224"]} pcbX="2.800096mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin225"]} pcbX="2.800096mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin226"]} pcbX="2.800096mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin227"]} pcbX="2.800096mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin228"]} pcbX="2.800096mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin229"]} pcbX="2.800096mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin230"]} pcbX="2.800096mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin231"]} pcbX="2.800096mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin232"]} pcbX="2.800096mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin233"]} pcbX="2.800096mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin234"]} pcbX="2.800096mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin235"]} pcbX="3.599942mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin236"]} pcbX="3.599942mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin237"]} pcbX="3.599942mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin238"]} pcbX="3.599942mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin239"]} pcbX="3.599942mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin240"]} pcbX="3.599942mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin241"]} pcbX="3.599942mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin242"]} pcbX="3.599942mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin243"]} pcbX="3.599942mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin244"]} pcbX="3.599942mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin245"]} pcbX="3.599942mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin246"]} pcbX="3.599942mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin247"]} pcbX="3.599942mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin248"]} pcbX="3.599942mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin249"]} pcbX="3.599942mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin250"]} pcbX="3.599942mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin251"]} pcbX="3.599942mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin252"]} pcbX="3.599942mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin253"]} pcbX="4.400042mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin254"]} pcbX="4.400042mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin255"]} pcbX="4.400042mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin256"]} pcbX="4.400042mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin257"]} pcbX="4.400042mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin258"]} pcbX="4.400042mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin259"]} pcbX="4.400042mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin260"]} pcbX="4.400042mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin261"]} pcbX="4.400042mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin262"]} pcbX="4.400042mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin263"]} pcbX="4.400042mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin264"]} pcbX="4.400042mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin265"]} pcbX="4.400042mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin266"]} pcbX="4.400042mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin267"]} pcbX="4.400042mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin268"]} pcbX="4.400042mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin269"]} pcbX="4.400042mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin270"]} pcbX="4.400042mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin271"]} pcbX="5.199888mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin272"]} pcbX="5.199888mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin273"]} pcbX="5.199888mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin274"]} pcbX="5.199888mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin275"]} pcbX="5.199888mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin276"]} pcbX="5.199888mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin277"]} pcbX="5.199888mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin278"]} pcbX="5.199888mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin279"]} pcbX="5.199888mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin280"]} pcbX="5.199888mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin281"]} pcbX="5.199888mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin282"]} pcbX="5.199888mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin283"]} pcbX="5.199888mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin284"]} pcbX="5.199888mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin285"]} pcbX="5.199888mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin286"]} pcbX="5.199888mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin287"]} pcbX="5.199888mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin288"]} pcbX="5.199888mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin289"]} pcbX="5.999988mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin290"]} pcbX="5.999988mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin291"]} pcbX="5.999988mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin292"]} pcbX="5.999988mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin293"]} pcbX="5.999988mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin294"]} pcbX="5.999988mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin295"]} pcbX="5.999988mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin296"]} pcbX="5.999988mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin297"]} pcbX="5.999988mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin298"]} pcbX="5.999988mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin299"]} pcbX="5.999988mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin300"]} pcbX="5.999988mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin301"]} pcbX="5.999988mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin302"]} pcbX="5.999988mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin303"]} pcbX="5.999988mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin304"]} pcbX="5.999988mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin305"]} pcbX="5.999988mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin306"]} pcbX="5.999988mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin307"]} pcbX="6.800088mm" pcbY="6.800088mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin308"]} pcbX="6.800088mm" pcbY="5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin309"]} pcbX="6.800088mm" pcbY="5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin310"]} pcbX="6.800088mm" pcbY="4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin311"]} pcbX="6.800088mm" pcbY="3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin312"]} pcbX="6.800088mm" pcbY="2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin313"]} pcbX="6.800088mm" pcbY="1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin314"]} pcbX="6.800088mm" pcbY="1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin315"]} pcbX="6.800088mm" pcbY="0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin316"]} pcbX="6.800088mm" pcbY="-0.40005mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin317"]} pcbX="6.800088mm" pcbY="-1.199896mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin318"]} pcbX="6.800088mm" pcbY="-1.999996mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin319"]} pcbX="6.800088mm" pcbY="-2.800096mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin320"]} pcbX="6.800088mm" pcbY="-3.599942mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin321"]} pcbX="6.800088mm" pcbY="-4.400042mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin322"]} pcbX="6.800088mm" pcbY="-5.199888mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin323"]} pcbX="6.800088mm" pcbY="-5.999988mm" radius="0.1799971mm" shape="circle" />
<smtpad portHints={["pin324"]} pcbX="6.800088mm" pcbY="-6.800088mm" radius="0.1799971mm" shape="circle" />
<silkscreenpath route={[{"x":-7.576184999999981,"y":7.576184999999995},{"x":7.5761850000000095,"y":7.576184999999995},{"x":7.5761850000000095,"y":-7.576184999999995},{"x":-7.576184999999981,"y":-7.576184999999995},{"x":-7.576184999999981,"y":7.576184999999995}]} />
<silkscreenpath route={[{"x":-7.80478500000001,"y":7.016191199999994},{"x":-7.80478500000001,"y":7.804784999999995},{"x":-7.016191199999994,"y":7.804784999999995}]} />
<silkscreencircle pcbX="-8.076184mm" pcbY="6.800088mm" radius="0.050038mm" />
<silkscreentext text="{NAME}" pcbX="-0.2794mm" pcbY="8.7978mm" anchorAlignment="center" fontSize="1mm" />
<fabricationnotepath route={[{"x":-7.6200000000000045,"y":7.61999999999999},{"x":-7.6200000000000045,"y":6.603999999999985},{"x":-6.603999999999999,"y":7.61999999999999},{"x":-7.6200000000000045,"y":7.61999999999999},{"x":-7.6200000000000045,"y":6.603999999999985},{"x":-7.6200000000000045,"y":7.61999999999999}]} strokeWidth="0mm" isFilled hasStroke={false} />
<courtyardoutline outline={[{"x":-7.749984999999995,"y":7.749984999999981},{"x":7.749984999999995,"y":7.749984999999981},{"x":7.749984999999995,"y":-7.7499850000000094},{"x":-7.749984999999995,"y":-7.7499850000000094},{"x":-7.749984999999995,"y":7.749984999999981}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C128768.obj?uuid=3b75b8b2cced455fa1f667b7a736aeb1",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C128768.step?uuid=3b75b8b2cced455fa1f667b7a736aeb1",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: 0, z: -0.5 },
      }}
      {...props}
    />
  )
}