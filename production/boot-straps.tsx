import { Fragment } from "react"
import { A_0402WGF1002TCE as Pull10k } from "../imports/A_0402WGF1002TCE"

// TI SPRUH73Q Table 26-7. SYSBOOT[15:14] = 01 selects 24 MHz.
// SYSBOOT[4:0] = 10111 selects MMC0, SPI0, UART0, USB0.
const strapWord = 0x4017

export function BootStraps() {
  return <>
    <net name="VDD_IO_3V3_SEQ" />
    {Array.from({ length: 16 }, (_, bit) => {
      const name = `R_SYSBOOT${bit}`
      const rail = (strapWord & (1 << bit)) ? "VDD_IO_3V3_SEQ" : "GND"
      return <Fragment key={name}>
        <Pull10k name={name} pcbX={bit === 1 ? -35.52 : -34 + (bit % 8) * 1.25}
          pcbY={bit === 1 ? 5.28 : 6 + Math.floor(bit / 8) * 2.25}
          pcbRotation={bit === 1 ? 180 : 90} />
        <trace name={`SYSBOOT${bit}_BIAS`} from={`.${name} > .pin1`} to={`net.${rail}`} />
      </Fragment>
    })}
  </>
}
