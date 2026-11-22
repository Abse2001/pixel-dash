// Run against a local bus-lanes-solver checkout to exercise uncommitted solver changes.
import { resolve } from "node:path"
import { pathToFileURL } from "node:url"

const [checkout, output] = process.argv.slice(2)
if (!checkout) throw new Error("Usage: bun route.ts PATH_TO_BUS_LANES_SOLVER [OUTPUT.json]")
const { BusLanesPipelineSolver } = await import(pathToFileURL(resolve(checkout, "lib/index.ts")).href)
const input = await Bun.file(new URL("simple-route.json", import.meta.url)).json()
const solver = new BusLanesPipelineSolver(input)
solver.solve()
if (!solver.solved) throw new Error(solver.error ?? "Full-board routing did not finish")
if (output) await Bun.write(output, JSON.stringify(solver.getOutput()))
console.log("Full-board solver completed")
