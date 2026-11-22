import { SramBypass } from "./sram-bypass"
import { UartDebug } from "./uart-debug"
import { JoystickAdc } from "./joystick-adc"
import { Circuit } from "@tscircuit/core"
import MemoryChannel from "../am3354/channel.circuit"
import { BootStraps } from "./boot-straps"
import { Oscillator } from "./oscillator"
import { PowerControl } from "./power-control"

const circuit = new Circuit()
circuit.add(<MemoryChannel pcbOffsetX={-45}><BootStraps /><Oscillator /><PowerControl /><JoystickAdc /><UartDebug /><SramBypass /></MemoryChannel>)
await circuit.renderUntilSettled()
await Bun.write("dist/channel.circuit.json", JSON.stringify(circuit.getCircuitJson()))
