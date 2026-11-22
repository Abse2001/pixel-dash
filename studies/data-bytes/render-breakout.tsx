import { Circuit } from "@tscircuit/core"
import { AM3354BZCZD80 } from "../../am3354/imports/AM3354BZCZD80"
import { MT41K512M16VRP_107_IT_P } from "../../am3354/imports/MT41K512M16VRP_107_IT_P"
import { packages, signals } from "../../am3354/channel"
import routes from "../../am3354/connectivity-paths.json"
import type { TraceProps } from "@tscircuit/props"

const circuit = new Circuit()
const [cpu, ram] = packages
circuit.add(
  <board width={45} height={32} layers={4} thickness={1.491} pcbX={-54} pcbY={14} routeRemaining={false} pcbStyle={{viaPadDiameter:0.30,viaHoleDiameter:0.15}}>
    <AM3354BZCZD80 name="U1" pcbX={cpu.x+9} pcbY={cpu.y-14} pcbRotation={cpu.rotation}/>
    <MT41K512M16VRP_107_IT_P name="U_DDR" pcbX={ram.x+9} pcbY={ram.y-14} pcbRotation={ram.rotation}/>
    {signals.filter(s=>s.name in routes).map(s=><trace key={s.name} name={s.name} from={".U1 > ."+s.cpuBall} to={".U_DDR > ."+s.ramBall} thickness={0.102} pcbPath={routes[s.name as keyof typeof routes] as TraceProps["pcbPath"]}/>)}
  </board>
)
await circuit.renderUntilSettled()
await Bun.write(process.argv[2],JSON.stringify(circuit.getCircuitJson()))
