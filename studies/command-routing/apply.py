"""Install the checked outer-layer DDR command routes on the locked populated board."""
import json
import math
import sys
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

folder = Path(__file__).resolve().parent
routes = json.loads((folder / 'routes.json').read_bytes())
board = json.loads(Path(sys.argv[1]).read_bytes())
ports = {p['source_port_id']: p for p in board if p['type'] == 'pcb_port' and p.get('source_port_id')}
sources = {s.get('name'): s for s in board if s['type'] == 'source_trace' and s.get('name')}
existing = {t['source_trace_id'] for t in board if t['type'] == 'pcb_trace'}
inner_routes = json.loads((folder / "inner-routes.json").read_bytes())
if inner_routes.keys() & routes.keys():
    raise ValueError("Duplicate command route")
routes.update(inner_routes)
holes = []
inner_reliefs = []
for name, sections in routes.items():
    source = sources[name]
    if name.startswith('DDR_D') or source['source_trace_id'] in existing:
        raise ValueError(f'Occupied signal: {name}')
    ends = [ports[k] for k in source['connected_source_port_ids']]
    for point, end in zip([sections[0][0], sections[-1][-1]], ends):
        if math.dist(point, (end['x'], end['y'])) > 0.00001:
            raise ValueError(f'{name} misses {end["pcb_port_id"]}')
    trace_id = 'pcb_command_' + name
    key = source['subcircuit_connectivity_map_key']
    steps = []
    carrier = 'inner2' if name in inner_routes else 'bottom'
    for i, section in enumerate(sections):
        layer = ('top', carrier)[i % 2]
        if i:
            x, y = section[0]
            if section[0] != sections[i-1][-1]:
                raise ValueError(f'Disconnected via on {name}')
            prev_layer = (carrier, 'top')[i % 2]
            steps.append(dict(route_type='via', x=x, y=y, from_layer=prev_layer, to_layer=layer))
            board.append(dict(type='pcb_via', pcb_via_id=f'{trace_id}_via_{i}', pcb_trace_id=trace_id,
                              x=x, y=y, from_layer='top', to_layer='bottom',
                              layers=['top','inner1','inner2','bottom'], outer_diameter=.30, hole_diameter=.15,
                              subcircuit_connectivity_map_key=key))
            holes.append(Point(x, y).buffer(.31, quad_segs=192))
        if layer == 'inner2' and len(section)>1:
            inner_reliefs.append(LineString(section).buffer(.051+.16, quad_segs=96))
        steps.extend(dict(route_type='wire', x=x, y=y, layer=layer, width=.102) for x,y in section)
    steps[0]['start_pcb_port_id'] = ends[0]['pcb_port_id']
    steps[-1]['end_pcb_port_id'] = ends[1]['pcb_port_id']
    board.append(dict(type='pcb_trace', pcb_trace_id=trace_id, source_trace_id=source['source_trace_id'],
                      subcircuit_connectivity_map_key=key, route=steps))
reliefs = unary_union(holes)
for pour in board:
    if pour['type'] != 'pcb_copper_pour' or pour['layer'] not in ('inner1','inner2'):
        continue
    shape = pour['brep_shape']
    def xy(ring):
        return [(p['x'], p['y']) for p in ring['vertices']]
    original = Polygon(xy(shape['outer_ring']), [xy(r) for r in shape['inner_rings']])
    cuts = unary_union([reliefs, *inner_reliefs]) if pour["layer"] == "inner2" else reliefs
    if not original.intersects(cuts):
        continue
    copper = original.difference(cuts)
    if copper.geom_type != 'Polygon':
        ids_key = next(e["subcircuit_connectivity_map_key"] for e in board if e["type"]=="source_net" and e["source_net_id"]==pour["source_net_id"])
        pieces = sorted(copper.geoms, key=lambda part: part.area, reverse=True)
        detached = unary_union(pieces[1:])
        contacts = [v for v in board if v["type"]=="pcb_via" and pour["layer"] in v["layers"] and
                    (v.get("source_net_id")==pour["source_net_id"] or
                     v.get("subcircuit_connectivity_map_key")==ids_key) and
                    detached.intersects(Point(v["x"],v["y"]).buffer(v["outer_diameter"]/2))]
        if contacts or detached.area > 0.25:
            raise ValueError(f'Plane split on {pour["pcb_copper_pour_id"]}, {detached.area:.6f} mm2 with {len(contacts)} via lands')
        copper = pieces[0]
    def ring(boundary):
        return {'vertices': [dict(x=x, y=y) for x,y in list(boundary.coords)[:-1]]}
    pour['brep_shape'] = dict(outer_ring=ring(copper.exterior), inner_rings=[ring(r) for r in copper.interiors])
Path(sys.argv[2]).write_text(json.dumps(board,separators=(',',':')))
