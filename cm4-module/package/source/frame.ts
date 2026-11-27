// CM4 frame -> module frame.
// CM4 frame: Raspberry Pi CM4 datasheet Figure 4 / CM4IO KiCad footprint, top view with y up: board 40 x 55 mm,
// u in [-3.5, 36.5], v in [-3.5, 51.5], M2.5 holes at (0,0) (33,0) (0,48) (33,48); connector J1 (pins 1-100) centred at
// (-0.46, 21.5), J2 (pins 101-200) at (33.46, 21.5), both running along v with pin 1 / 101 at v = 31.3, odd pins on
// J1's outer row and on J2's inner row.
// Module frame: the routed DDR block's coordinates. The DDR block (40.0 mm long) runs along the CM4's 55 mm axis:
// x = X0 + v, y = Y0 - u, a rotation (no mirror), so the block is not changed at all.
export const X0 = -75.15, Y0 = 31.65
export const toModule = (u: number, v: number) => ({ x: +(X0 + v).toFixed(4), y: +(Y0 - u).toFixed(4) })
export const toCM4 = (x: number, y: number) => ({ u: +(Y0 - y).toFixed(4), v: +(x - X0).toFixed(4) })
const a = toModule(-3.5, -3.5), b = toModule(36.5, 51.5)
export const EDGE = { x0: Math.min(a.x, b.x), x1: Math.max(a.x, b.x), y0: Math.min(a.y, b.y), y1: Math.max(a.y, b.y) }
/** M2.5 mounting holes, 2.7 mm drill, non-plated */
export const HOLES = [[0, 0], [33, 0], [0, 48], [33, 48]].map(([u, v]) => ({ ...toModule(u, v), d: 2.7 }))
/** connector centres; the plug footprint (parts.tsx) on the bottom at rotation 0 puts pin 1 at +x and the odd row at +y */
export const J1 = toModule(-0.46, 21.5), J2 = toModule(33.46, 21.5)
