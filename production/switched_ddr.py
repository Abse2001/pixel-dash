"""Route the LS1 output to the processor DDR balls and their dedicated L4 bypass copper."""
from pathlib import Path
import runpy

from shapely.geometry import box
from shapely.ops import unary_union


def add_switched_ddr_feeds(board, port):
    rail, = (e for e in board if e['type'] == 'source_net' and e['name'] == 'VDDS_DDR_CPU')
    key = rail['subcircuit_connectivity_map_key']
    def trace(label, terminal, layer, width, points, starts_on_land=False):
        pin = port(*terminal.split('.'))
        source, = (e for e in board if e['type'] == 'source_trace' and pin['source_port_id'] in e['connected_source_port_ids']
                   and rail['source_net_id'] in e['connected_source_net_ids'])
        wires = [dict(route_type='wire', x=x, y=y, width=width, layer=layer) for x, y in points]
        if starts_on_land:
            land, = (e for e in board if e['type'] == 'pcb_port' and e.get('source_port_id') == pin['source_port_id'])
            if abs(land['x']-points[0][0]) + abs(land['y']-points[0][1]) > .00001:
                raise ValueError(f'Switched DDR feed moved off {terminal}')
            wires[0]['start_pcb_port_id'] = land['pcb_port_id']
        board.append(dict(type='pcb_trace', pcb_trace_id='pcb_ddr_supply_'+label, source_trace_id=source['source_trace_id'],
                          subcircuit_connectivity_map_key=key, route=wires))
    def via(label, x, y, diameter, drill):
        board.append(dict(type='pcb_via', pcb_via_id='via_ddr_supply_'+label, x=x, y=y, source_net_id=rail['source_net_id'],
                          subcircuit_connectivity_map_key=key, layers=['top','inner1','inner2','bottom'],
                          from_layer='top', to_layer='bottom', outer_diameter=diameter, hole_diameter=drill))

    trace('ls1', 'U_PMIC.LS1', 'top', .22, [(-20.250064,29.19989),(-20.085,30.055),(-19.805,30.265)], True)
    trace('ls1_flare', 'U_PMIC.LS1', 'top', .28, [(-19.805,30.265),(-18.055,30.685)])
    via('output', -18.055,30.685,.38,.18)
    trace('regulator', 'U_PMIC.LS1', 'inner2', .80, [(-18.055,30.685),(-19.079545,31.932273)])
    trace('regulator_neck', 'U_PMIC.LS1', 'inner2', .46, [(-19.079545,31.932273),(-19.665,32.645),(-20.05,32.75),(-22.255,32.75)])
    trace('regulator_exit', 'U_PMIC.LS1', 'inner2', .60, [(-22.255,32.75),(-22.689,32.554)])
    trace('regulator_trunk', 'U_PMIC.LS1', 'inner2', 1.00, [(-22.689,32.554),(-24.208,31.868)])
    trace('regulator_bend', 'U_PMIC.LS1', 'inner2', .60, [(-24.208,31.868),(-24.859,31.574)])
    trace('regulator_landing', 'U_PMIC.LS1', 'inner2', .80, [(-24.859,31.574),(-26.595,30.79)])
    via('upper', -26.595,30.79,.38,.18)
    trace('bypass_bridge','U_PMIC.LS1','inner2',.60,[(-45.11,23.475),(-46.405,21.62)])
    via('bridge_upper',-45.11,23.475,.45,.20)
    via('bridge_lower',-46.405,21.62,.45,.20)
    trace('cpu','U1.L5','top',.18,[(-48.399942,13.950104),(-47.994942,13.200104),(-47.994942,12.115104),(-47.924942,11.940104)],True)
    via('balls',-47.924942,11.940104,.38,.18)


def add_switched_ddr_pours(board):
    geometry = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'checks/audit-copper-contacts.py'))
    copper = geometry['copper'](board)
    ids = {e[e['type']+'_id']:e for e in board if e['type']+'_id' in e}
    rail, = (e for e in board if e['type']=='source_net' and e['name']=='VDDS_DDR_CPU')
    key = rail['subcircuit_connectivity_map_key']
    signals = {e['subcircuit_connectivity_map_key'] for e in board if e['type']=='source_trace' and (e.get('name') or '').startswith('DDR_')}
    ram, = (e for e in board if e['type']=='source_component' and e.get('name')=='U_DDR')
    ram_body, = (e['pcb_component_id'] for e in board if e['type']=='pcb_component' and e['source_component_id']==ram['source_component_id'])
    region = unary_union([g for l in ('top','bottom') for oid,n,g in copper[l]
                          if n in signals or ids[oid].get('pcb_component_id')==ram_body]).convex_hull
    window = box(-55,3,-17,35)
    relief = [g.buffer(.16,quad_segs=48) for oid,n,g in copper['bottom'] if n!=key and g.intersects(window)]
    area = window.difference(unary_union([region.buffer(.409),*relief]))
    parts = [p for p in area.geoms if any(p.intersection(g).area>.02 for oid,n,g in copper['bottom']
                                         if n==key and ids[oid]['type']=='pcb_smtpad')]
    def ring(boundary):
        return {'vertices':[{'x':x,'y':y} for x,y in list(boundary.coords)[:-1]]}
    for i,part in enumerate(parts):
        board.append(dict(type='pcb_copper_pour',pcb_copper_pour_id=f'switched_ddr_{i}',source_net_id=rail['source_net_id'],
                          shape='brep',layer='bottom',covered_with_solder_mask=True,
                          brep_shape={'outer_ring':ring(part.exterior),'inner_rings':[ring(r) for r in part.interiors]}))
