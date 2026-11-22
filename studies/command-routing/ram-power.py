"""Connect the selected DDR3L supply and return balls to their own inner planes."""
import json
import sys
from pathlib import Path
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

board = json.loads(Path(sys.argv[1]).read_bytes())
spec = json.loads(Path(__file__).with_name("supply-vias.json").read_bytes())
ids = {e.get(e['type']+'_id'): e for e in board}
nets = {e['name']:e for e in board if e['type']=='source_net'}
ram, = [e for e in board if e['type']=='source_component' and e.get('name')=='U_DDR']
reliefs = []
for ball, feed in spec.items():
    source, = [e for e in board if e['type']=='source_port' and e['source_component_id']==ram['source_component_id'] and e['name']==ball]
    land, = [e for e in board if e['type']=='pcb_port' and e.get('source_port_id')==source['source_port_id']]
    rail = nets[feed['rail']]
    key = rail['subcircuit_connectivity_map_key']
    x,y = feed['via']
    start = [land['x'], land['y']]
    if start != feed['at'] or source['subcircuit_connectivity_map_key'] != key:
        raise ValueError(f'Unexpected U_DDR.{ball} placement or rail')
    via_id = 'pcb_ram_feed_'+ball
    layers = ['top','inner1'] if feed['rail']=='GND' else ['top','inner1','inner2','bottom']
    via = dict(type='pcb_via',pcb_via_id=via_id,x=x,y=y,layers=layers,from_layer='top',to_layer=layers[-1],
               outer_diameter=feed['diameter'],hole_diameter=feed['drill'],source_net_id=rail['source_net_id'],subcircuit_connectivity_map_key=key)
    board.append(via)
    if start != [x,y]:
        sources = [e for e in board if e['type']=='source_trace' and source['source_port_id'] in e['connected_source_port_ids'] and e['subcircuit_connectivity_map_key']==key]
        board.append(dict(type='pcb_trace',pcb_trace_id=via_id+'_stub',source_trace_id=sources[0]['source_trace_id'],
                          subcircuit_connectivity_map_key=key,route=[
                             dict(route_type='wire',x=start[0],y=start[1],layer='top',width=.13,start_pcb_port_id=land['pcb_port_id']),
                             dict(route_type='wire',x=x,y=y,layer='top',width=.13)]))
    reliefs.append((rail['source_net_id'],layers,Point(x,y).buffer(feed['diameter']/2+.16,quad_segs=192)))
for p in board:
    if p['type']!='pcb_copper_pour':continue
    holes = unary_union([g for net,layers,g in reliefs if net!=p['source_net_id'] and p['layer'] in layers])
    shape=p['brep_shape']
    def coords(r):
        return [(v['x'],v['y']) for v in r['vertices']]
    original=Polygon(coords(shape['outer_ring']),[coords(r) for r in shape['inner_rings']])
    if not original.intersects(holes):continue
    cut=original.difference(holes)
    if cut.geom_type!='Polygon':raise ValueError(f"RAM via splits {p['pcb_copper_pour_id']}")
    def ring(r):
        return {'vertices':[dict(x=x,y=y) for x,y in list(r.coords)[:-1]]}
    p['brep_shape']=dict(outer_ring=ring(cut.exterior),inner_rings=[ring(r) for r in cut.interiors])
Path(sys.argv[2]).write_text(json.dumps(board,separators=(',',':')))
