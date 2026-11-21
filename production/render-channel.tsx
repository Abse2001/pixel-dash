import { Circuit } from "@tscircuit/core"
import MemoryChannel from "../am3354/channel.circuit"
import { BootStraps } from "./boot-straps"

const circuit = new Circuit()
circuit.add(<MemoryChannel pcbOffsetX={-45}><BootStraps /></MemoryChannel>)
await circuit.renderUntilSettled()
await Bun.write("dist/channel.circuit.json", JSON.stringify(circuit.getCircuitJson()))
