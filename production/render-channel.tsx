import { Circuit } from "@tscircuit/core"
import Channel from "../am3354/handheld-channel.circuit"

const circuit = new Circuit()
circuit.add(<Channel />)
await circuit.renderUntilSettled()
await Bun.write("dist/channel.circuit.json", JSON.stringify(circuit.getCircuitJson()))
