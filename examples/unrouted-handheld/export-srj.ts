import { getSimpleRouteJsonFromCircuitJson } from "@tscircuit/core"
import type { AnyCircuitElement } from "circuit-json"

const circuit = (await Bun.file(new URL("board.circuit.json", import.meta.url)).json()) as AnyCircuitElement[]
const board = circuit.find(e => e.type === "pcb_board")
if (!board) throw new Error("Missing PCB board")
const { simpleRouteJson: input } = getSimpleRouteJsonFromCircuitJson({
  circuitJson: circuit,
  minTraceWidth: board.min_trace_width,
  minViaHoleDiameter: board.min_via_hole_diameter,
  minViaPadDiameter: board.min_via_pad_diameter,
  minTraceToPadEdgeClearance: board.min_trace_to_pad_edge_clearance,
})

// The core converter normally reads these constraints from live JSX instances.
// This fixture starts with the assembled board, where they live in source_bus.
const byTrace = new Map(input.connections.map(c => [c.source_trace_id, c]))
const buses = []
const differentialPairs = []
for (const bus of circuit.filter(e => e.type === "source_bus")) {
  const members = bus.source_trace_ids.map(id => {
    const connection = byTrace.get(id)
    if (!connection) throw new Error(`Missing ${id} in ${bus.name}`)
    return connection
  })
  const connectionNames = members.map(c => c.name)
  if (bus.differential_pair) {
    const { positive_source_trace_id, negative_source_trace_id, trace_gap } = bus.differential_pair
    differentialPairs.push({
      connectionNames: [positive_source_trace_id, negative_source_trace_id].map(id => byTrace.get(id)!.name),
      lengthTolerance: bus.max_length_skew,
      traceGap: trace_gap,
    })
    continue
  }
  function length(rule: typeof bus.max_length) {
    if (rule === undefined || typeof rule === "number") return rule
    if (rule.reference !== "longest_manhattan") throw new Error(`Unknown length reference on ${bus.name}`)
    const spans = (rule.source_trace_ids ?? bus.source_trace_ids).map(id => {
      const points = byTrace.get(id)?.pointsToConnect
      if (points?.length !== 2) throw new Error(`Expected two endpoints for ${id}`)
      return Math.abs(points[0].x - points[1].x) + Math.abs(points[0].y - points[1].y)
    })
    return Math.max(...spans) + (rule.offset ?? 0)
  }
  const target = length(bus.target_length)
  buses.push({
    busId: bus.name, name: bus.name, connectionNames,
    minLength: target === undefined ? length(bus.min_length) : target - bus.length_tolerance!,
    maxLength: target === undefined ? length(bus.max_length) : target + bus.length_tolerance!,
    maxLengthSkew: bus.max_length_skew,
    preferredLayers: ["DDR_BYTE0", "DDR_BYTE1"].includes(bus.name) ? ["bottom"] : undefined,
  })
}
const file = new URL("simple-route.json", import.meta.url)
await Bun.write(file, JSON.stringify({ ...input, buses, differentialPairs, traces: [] }) + "\n")
console.log(`${input.connections.length} routing requests, ${buses.length} buses, ${differentialPairs.length} differential pairs`)
