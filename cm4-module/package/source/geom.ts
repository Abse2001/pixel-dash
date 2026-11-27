// Shared geometry model for the module planner, router and checker.
// Every piece of copper is a convex "rounded polygon": a point set (1 = disc, 2 = track, 4 = rectangle) plus a radius.
export type Pt = { x: number; y: number }
export type Layer = "top" | "bottom"
export type Item = { pts: Pt[]; r: number; layers: Layer[]; net: string; kind: string; ref?: string }
export const disc = (x: number, y: number, r: number): Pick<Item, "pts" | "r"> => ({ pts: [{ x, y }], r })
export const seg = (a: Pt, b: Pt, w: number): Pick<Item, "pts" | "r"> => ({ pts: [{ x: a.x, y: a.y }, { x: b.x, y: b.y }], r: w / 2 })
export const rect = (x: number, y: number, w: number, h: number, rotDeg = 0): Pick<Item, "pts" | "r"> => {
  const c = Math.cos((rotDeg * Math.PI) / 180), s = Math.sin((rotDeg * Math.PI) / 180)
  return { pts: [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([i, j]) => ({ x: x + (i * w / 2) * c - (j * h / 2) * s, y: y + (i * w / 2) * s + (j * h / 2) * c })), r: 0 }
}
const ptSeg = (p: Pt, a: Pt, b: Pt) => { const dx = b.x - a.x, dy = b.y - a.y, l = dx * dx + dy * dy; let t = l ? ((p.x - a.x) * dx + (p.y - a.y) * dy) / l : 0; t = Math.max(0, Math.min(1, t)); return Math.hypot(p.x - a.x - t * dx, p.y - a.y - t * dy) }
const cross = (o: Pt, a: Pt, b: Pt) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)
const segsCross = (a: Pt, b: Pt, c: Pt, d: Pt) => { const d1 = cross(c, d, a), d2 = cross(c, d, b), d3 = cross(a, b, c), d4 = cross(a, b, d); return ((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) && ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0)) }
const segSeg = (a: Pt, b: Pt, c: Pt, d: Pt) => segsCross(a, b, c, d) ? 0 : Math.min(ptSeg(a, c, d), ptSeg(b, c, d), ptSeg(c, a, b), ptSeg(d, a, b))
const inside = (p: Pt, poly: Pt[]) => { if (poly.length < 3) return false; let s = 0; for (let i = 0; i < poly.length; i++) { const c = cross(poly[i], poly[(i + 1) % poly.length], p); if (c === 0) continue; if (s === 0) s = Math.sign(c); else if (Math.sign(c) !== s) return false } return true }
const edges = (p: Pt[]): [Pt, Pt][] => p.length === 1 ? [[p[0], p[0]]] : p.length === 2 ? [[p[0], p[1]]] : p.map((q, i) => [q, p[(i + 1) % p.length]] as [Pt, Pt])
/** copper-to-copper gap between two shapes (negative = overlap) */
export function gap(a: Pick<Item, "pts" | "r">, b: Pick<Item, "pts" | "r">) {
  if (inside(a.pts[0], b.pts) || inside(b.pts[0], a.pts)) return -a.r - b.r - 1
  let m = Infinity; for (const [p, q] of edges(a.pts)) for (const [u, v] of edges(b.pts)) { const d = segSeg(p, q, u, v); if (d < m) m = d }
  return m - a.r - b.r
}
export const bbox = (s: Pick<Item, "pts" | "r">) => ({ x0: Math.min(...s.pts.map((p) => p.x)) - s.r, x1: Math.max(...s.pts.map((p) => p.x)) + s.r, y0: Math.min(...s.pts.map((p) => p.y)) - s.r, y1: Math.max(...s.pts.map((p) => p.y)) + s.r })
/** spatial index of copper items */
export class Board {
  items: Item[] = []; private cells = new Map<number, number[]>(); private C = 1
  private key = (i: number, j: number) => (i + 5000) * 20000 + (j + 5000)
  add(it: Item) { const id = this.items.push(it) - 1, b = bbox(it)
    for (let i = Math.floor(b.x0 / this.C); i <= Math.floor(b.x1 / this.C); i++) for (let j = Math.floor(b.y0 / this.C); j <= Math.floor(b.y1 / this.C); j++) { const k = this.key(i, j); let a = this.cells.get(k); if (!a) this.cells.set(k, (a = [])); a.push(id) }
    return it }
  near(s: Pick<Item, "pts" | "r">, margin: number): Item[] { const b = bbox(s), seen = new Set<number>(), out: Item[] = []
    for (let i = Math.floor((b.x0 - margin) / this.C); i <= Math.floor((b.x1 + margin) / this.C); i++) for (let j = Math.floor((b.y0 - margin) / this.C); j <= Math.floor((b.y1 + margin) / this.C); j++) for (const id of this.cells.get(this.key(i, j)) ?? []) if (!seen.has(id)) { seen.add(id); out.push(this.items[id]) }
    return out }
  /** foreign copper closer than `clear(item)` to the shape on any of the layers */
  hits(s: Pick<Item, "pts" | "r">, layers: Layer[], net: string, clear: number | ((it: Item) => number), maxClear = 0.5): Item[] {
    return this.near(s, typeof clear === "number" ? clear : maxClear).filter((it) => it.net !== net && it.layers.some((l) => layers.includes(l)) && gap(s, it) < (typeof clear === "number" ? clear : clear(it)) - 1e-9) }
}
