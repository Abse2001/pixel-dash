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
        widths = width if isinstance(width, list) else [width] * (len(points) - 1)
        if len(widths) != len(points) - 1:
            raise ValueError(f"Wrong width count for {label}")
        wires = [dict(route_type='wire', x=x, y=y, width=w, layer=layer)
                 for (x, y), w in zip(points, [*widths, widths[-1]])]
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

    trace('ls1', 'U_PMIC.LS1', 'top',
          [0.34, 0.37, 0.3, 0.24, 0.23, 0.22, 0.22],
          [(-20.250064, 29.19989), (-20.217051, 29.370912), (-20.184038, 29.541934), (-20.151026, 29.712956), (-20.118013, 29.883978), (-20.085, 30.055), (-19.945, 30.16), (-19.805, 30.265)], starts_on_land=True)
    trace('ls1_flare', 'U_PMIC.LS1', 'top',
          [0.32, 0.42, 0.55, 0.4, 0.3, 0.29, 0.31, 0.45, 0.49, 0.41],
          [(-19.805, 30.265), (-19.63, 30.307), (-19.455, 30.349), (-19.28, 30.391), (-19.105, 30.433), (-18.93, 30.475), (-18.755, 30.517), (-18.58, 30.559), (-18.405, 30.601), (-18.23, 30.643), (-18.055, 30.685)])
    via('output', -18.055,30.685,.38,.18)
    trace('regulator', 'U_PMIC.LS1', 'inner2', .80, [(-18.055,30.685),(-19.079545,31.932273)])
    trace('regulator_neck', 'U_PMIC.LS1', 'inner2', .46, [(-19.079545,31.932273),(-19.665,32.645),(-20.05,32.75),(-22.255,32.75)])
    trace('regulator_exit', 'U_PMIC.LS1', 'inner2', .60, [(-22.255,32.75),(-22.689,32.554)])
    trace('regulator_trunk', 'U_PMIC.LS1', 'inner2', 1.00, [(-22.689,32.554),(-24.208,31.868)])
    trace('regulator_bend', 'U_PMIC.LS1', 'inner2', .60, [(-24.208,31.868),(-24.859,31.574)])
    trace('regulator_landing', 'U_PMIC.LS1', 'inner2', .80, [(-24.859,31.574),(-26.595,30.79)])
    # Feed the lower L4 bank from the source barrel without interrupting the DDR reference island.
    for index, (width, path) in enumerate([
        (0.85, [(-18.055, 30.685), (-18.23, 30.8725)]),
        (1.1, [(-18.23, 30.8725), (-18.405, 31.06)]),
        (1.5, [(-18.405, 31.06), (-18.405, 31.808)]),
        (2, [(-18.405, 31.808), (-18.405, 32.556)]),
        (2.5, [(-18.405, 32.556), (-18.405, 32.93), (-18.735, 34.745)]),
        (3.2, [(-18.735, 34.745), (-19.659, 35.669)]),
        (4, [(-19.659, 35.669), (-19.89, 35.9), (-21.843448, 35.9)]),
        (5, [(-21.843448, 35.9), (-31.22, 35.9), (-35.003, 32.088)]),
    ]):
        trace(f'lower_bank_{index}', 'U_PMIC.LS1', 'inner2', width, path)
    via('lower_bank', -35.003, 32.088, .60, .30)
    via('upper', -26.595,30.79,.38,.18)
    trace('bypass_bridge','U_PMIC.LS1','inner2',.60,[(-45.11,23.475),(-46.405,21.62)])
    via('bridge_upper',-45.11,23.475,.45,.20)
    via('bridge_lower',-46.405,21.62,.45,.20)
    trace('cpu', 'U1.L5', 'top',
          [0.36, 0.36, 0.27, 0.18, 0.18, 0.21, 0.24, 0.33, 0.24, 0.22, 0.21, 0.22, 0.34, 0.36],
          [(-48.399942, 13.950104), (-48.318942, 13.800104), (-48.237942, 13.650104), (-48.156942, 13.500104), (-48.075942, 13.350104), (-47.994942, 13.200104), (-47.994942, 13.045104), (-47.994942, 12.890104), (-47.994942, 12.735104), (-47.994942, 12.580104), (-47.994942, 12.425104), (-47.994942, 12.270104), (-47.994942, 12.115104), (-47.959942, 12.027604), (-47.924942, 11.940104)], starts_on_land=True)
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
