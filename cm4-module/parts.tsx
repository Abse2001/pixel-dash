// Footprints written for this module.

/** CM4 plug (Hirose DF40C-100DP-0.4V(51) land pattern; fitted: G-Switch GT-B0403MSV11-100B1101, same drawing) with CM4 pin numbering (pin n of 100: odd pins on one row, even on the other,
 *  pins 1/2 at one end). Land pattern as JLCPCB/LCSC C531031 (0.2 x 0.66 mm pads at 0.4 mm pitch, rows 2.71 mm apart,
 *  0.3 x 0.66 mm fixing pads at +/-10.265 mm). Local frame: pin 1 at x = -9.8, odd row at y = +1.355.
 *  On the bottom side (mirrored in x) at rotation 0 this puts pin 1 at +9.8 and the odd row at +1.355. */
export function cm4HeaderFootprint() {
  const pads: any[] = []
  for (let n = 1; n <= 100; n++) {
    const k = (n - 1) >> 1, x = -(9.8 - 0.4 * k), y = n % 2 ? 1.355 : -1.355
    pads.push(<smtpad key={n} portHints={[`pin${n}`]} pcbX={`${x}mm`} pcbY={`${y}mm`} width="0.2mm" height="0.66mm" shape="rect" />)
  }
  for (const [i, [x, y]] of [[-10.265, -1.355], [10.265, -1.355], [-10.265, 1.355], [10.265, 1.355]].entries())
    pads.push(<smtpad key={"m" + i} portHints={[`pin${101 + i}`]} pcbX={`${x}mm`} pcbY={`${y}mm`} width="0.3mm" height="0.66mm" shape="rect" />)
  return <footprint>{pads}<courtyardoutline outline={[{ x: -11.0, y: -1.93 }, { x: 11.0, y: -1.93 }, { x: 11.0, y: 1.93 }, { x: -11.0, y: 1.93 }, { x: -11.0, y: -1.93 }]} /></footprint>
}

/** TPS65217 VQFN-48 (RSL): the imported land pattern without its 0.3 mm thermal-via holes; the exposed pad gets the
 *  board's own filled 0.1 mm vias instead. */
export const PMIC_FP = "qfn48_thermalpad4.05mmx3.6mm_p0.4mm_h6.68mm_pw0.22mm_pl0.66mm"
