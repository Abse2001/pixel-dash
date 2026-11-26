// pb/import.ts <pb routes file>: converts a routing of pb/route.ts into cm4-module/routes.json (the format planes.ts,
// build.tsx, check.ts and export.ts read). Plane-drop nets keep their vias and stubs like any other net.
const root = import.meta.dir + "/.."
const plan = await Bun.file(root + "/plan.json").json()
const src = process.argv[2] ?? import.meta.dir + "/routes.json"
const rj = await Bun.file(src).json()
const out: any = { solved: !rj.failed?.length && !rj.conflicts?.length, router: "pb/route.ts (negotiated congestion, routing playbook)", source: src, nets: {} }
for (const [name, r] of Object.entries(rj.nets) as [string, any][]) {
  const terms = ((plan.nets as any[]).find((n) => n.name === name)?.terms ?? []).map((t: any) => t.ref)
  const segs = r.segs.map((s: any) => ({ layer: s.layer, w: s.w, pts: s.pts }))
  const length = +segs.reduce((a: number, g: any) => a + g.pts.slice(1).reduce((b: number, p: any, i: number) => b + Math.hypot(p.x - g.pts[i].x, p.y - g.pts[i].y), 0), 0).toFixed(2)
  out.nets[name] = { terms, segs, vias: r.vias.map((v: any) => ({ x: v.x, y: v.y, d: v.d, hole: v.hole })), length }
}
await Bun.write(root + "/routes.json", JSON.stringify(out))
console.log(`routes.json from ${src}: ${Object.keys(out.nets).length} nets, ${Object.values(out.nets).reduce((s: number, r: any) => s + r.vias.length, 0)} vias; failed ${rj.failed?.length ?? 0}, in conflict ${rj.conflicts?.length ?? 0}`)
