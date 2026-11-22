export function UartDebug() {
  return <>
    <testpoint name="TP_UART_RX" footprintVariant="pad" padDiameter={1.0}
      layer="bottom" pcbX={-40.40} pcbY={19.05} />
    <testpoint name="TP_UART_TX" footprintVariant="pad" padDiameter={1.0}
      layer="bottom" pcbX={-40.40} pcbY={16.51} />
    <testpoint name="TP_UART_GND" footprintVariant="pad" padDiameter={1.0}
      layer="bottom" pcbX={-40.40} pcbY={13.97} />
    <trace name="DEBUG_UART0_RX" from=".U1 > .E15" to=".TP_UART_RX > .pin1" thickness={0.13}
      pcbPath={[{ x: 4.450042, y: 3.599942, via: true, fromLayer: "top", toLayer: "bottom" }]} />
    <trace name="DEBUG_UART0_TX" from=".U1 > .E16" to=".TP_UART_TX > .pin1" thickness={0.13}
      pcbPath={[{ x: 5.149888, y: 3.549942, via: true, fromLayer: "top", toLayer: "bottom" }]} />
    <trace from=".TP_UART_GND > .pin1" to=".V_C_DDR25_2 > .bottom" thickness={0.20} pcbStraightLine />
  </>
}
