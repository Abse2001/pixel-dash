"""Route the LS1 output to the processor DDR balls and their dedicated L4 bypass copper."""
from pathlib import Path
import runpy

from shapely.geometry import LineString, box
from shapely.ops import unary_union


def add_switched_ddr_feeds(board, port):
    rail, = (e for e in board if e['type'] == 'source_net' and e['name'] == 'VDDS_DDR_CPU')
    key = rail['subcircuit_connectivity_map_key']
    def trace(label, terminal, layer, width, points, starts_on_land=False):
        pin = port(*terminal.split('.'))
        source, = (e for e in board if e['type'] == 'source_trace' and e['connected_source_port_ids'] == [pin['source_port_id']]
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

    # The buffered output enters the existing L4 CPU bypass bank at its east feed.
    trace('switch_output', 'U_DDR_SWITCH.VOUT1', 'top', .28,
          [(-35.003, 31.968), (-35.003, 32.088)], starts_on_land=True)
    via('lower_bank', -35.003, 32.088, .60, .30)
    trace('bypass_bridge', 'U1.L5', 'inner2', .60, [(-45.11,23.475),(-46.405,21.62)])
    via('bridge_upper',-45.11,23.475,.45,.20)
    via('bridge_lower',-46.405,21.62,.45,.20)
    # Feed the seven switched balls from L5. Leave N5 and P5 accessible to DCDC4.
    trace('cpu', 'U1.L5', 'top', .26, [[-48.399941999999996, 13.950104], [-47.96493303735835, 13.499862670136817]], starts_on_land=True)
    via('balls', -47.96493303735835, 13.499862670136817, .38, .18)
    trace('cpu_barrel_feed', 'U1.L5', 'bottom', .40, [[-47.96493303735835, 13.499862670136817], [-47.630848090324925, 13.441043040292573]])



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

    # Spread the supply along the seven CPU DDR lands and out to the L4
    # feed. Use the stored escape as the spine, so it follows placement.
    cpu, = (e for e in board if e['type'] == 'source_component' and e.get('name') == 'U1')
    balls = {p['name']: p['source_port_id'] for p in board if p['type'] == 'source_port'
             and p.get('source_component_id') == cpu['source_component_id']}
    pads = {p['source_port_id']: (p['x'], p['y']) for p in board if p['type'] == 'pcb_port' and p.get('source_port_id')}
    feed = ids['pcb_ddr_supply_cpu']['route']
    spine = LineString([pads[balls['E5']], *[(p['x'], p['y']) for p in feed]])
    window = spine.buffer(.53, quad_segs=48)
    search_area = window.buffer(.42)
    relief = []
    for oid, net, shape in copper['top']:
        if net == key or not shape.intersects(search_area):
            continue
        # Keep four DDR trace widths from signal copper and six mil from
        # unrelated via lands. Existing routed links are preserved.
        gap = .410 if net in signals else .155 if ids[oid]['type'] == 'pcb_via' else .110
        relief.append(shape.buffer(gap, quad_segs=48))
    usable = window.difference(unary_union(relief))
    usable = usable.buffer(-.065, quad_segs=32).buffer(.065, quad_segs=32)
    pieces = getattr(usable, 'geoms', (usable,))
    for i, part in enumerate(pieces):
        if not part.intersects(spine) or part.area < .1:
            continue
        board.append(dict(type='pcb_copper_pour', pcb_copper_pour_id=f'cpu_ddr_row_{i}',
                          source_net_id=rail['source_net_id'], layer='top', shape='brep', covered_with_solder_mask=True,
                          brep_shape={'outer_ring':ring(part.exterior),'inner_rings':[ring(r) for r in part.interiors]}))

    # Spread the DCDC3 feed on its own net between the regulator capacitor
    # and the switch input. Keep the load side and all other copper isolated.
    dcdc3, = (e for e in board if e['type'] == 'source_net' and e['name'] == 'VDDS_DDR')
    input_key = dcdc3['subcircuit_connectivity_map_key']
    feeds = [ids['pcb_ddr_switch_input_' + suffix] for suffix in ('trunk', 'local')]
    if any(t['subcircuit_connectivity_map_key'] != input_key for t in feeds):
        raise ValueError('Unexpected switch input net')
    spine = unary_union([LineString([(p['x'], p['y']) for p in t['route']]) for t in feeds])
    window = spine.buffer(2.4, quad_segs=48)
    relief = [shape.buffer(.410 if net in signals else .155 if ids[oid]['type'] == 'pcb_via' else .110,
                           quad_segs=48)
              for oid, net, shape in copper['top'] if net != input_key and shape.distance(window) < .42]
    usable = window.difference(unary_union(relief)).buffer(-.12, quad_segs=32).buffer(.12, quad_segs=32)
    for i, part in enumerate(getattr(usable, 'geoms', (usable,))):
        if not part.intersects(spine) or part.area < .1:
            continue
        board.append(dict(type='pcb_copper_pour', pcb_copper_pour_id=f'ddr_switch_input_{i}',
                          source_net_id=dcdc3['source_net_id'], layer='top', shape='brep', covered_with_solder_mask=True,
                          brep_shape={'outer_ring':ring(part.exterior),'inner_rings':[ring(r) for r in part.interiors]}))
