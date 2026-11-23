"""Install the two A10 via-in-pad launches on a separate populated routing study."""
import csv
import json
import sys
from pathlib import Path

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

board = json.loads(Path(sys.argv[1]).read_bytes())
rows = list(csv.DictReader(Path(sys.argv[2]).open()))
source, = [e for e in board if e['type']=='source_trace' and e.get('name')=='DDR_A10']
ports = {e['source_port_id']: e for e in board if e['type']=='pcb_port' and e.get('source_port_id')}
layers = ['top','inner1','inner2','bottom']
reliefs = []
for pid in source['connected_source_port_ids']:
    port = ports[pid]
    side = 'U1' if port['x']>-57 else 'U_DDR'
    row, = [r for r in rows if r['net']=='DDR_A10' and r['span']=='L1-L4' and r['side']==side]
    if row['center_legal']=='True':
        x,y = port['x'],port['y']
    else:
        x,y = float(row['witness_x']),float(row['witness_y'])
    board.append(dict(type='pcb_via',pcb_via_id='vip_A10_'+side,x=x,y=y,
                      layers=layers,from_layer='top',to_layer='bottom',outer_diameter=.30,hole_diameter=.15,
                      source_trace_id=source['source_trace_id'],subcircuit_connectivity_map_key=source['subcircuit_connectivity_map_key']))
    reliefs.append(Point(x,y).buffer(.31,quad_segs=192))

def points(ring):
    return [(p['x'],p['y']) for p in ring['vertices']]

def ring(shape):
    return {'vertices':[dict(x=x,y=y) for x,y in list(shape.coords)[:-1]]}

for pour in board:
    if pour['type']!='pcb_copper_pour':
        continue
    brep=pour['brep_shape']
    original=Polygon(points(brep['outer_ring']),[points(h) for h in brep['inner_rings']])
    new=original.difference(unary_union(reliefs))
    if original.equals(new):
        continue
    assert new.geom_type=='Polygon', 'split reference pour'
    pour['brep_shape']=dict(outer_ring=ring(new.exterior),inner_rings=[ring(h) for h in new.interiors])
Path(sys.argv[3]).write_text(json.dumps(board,separators=(',',':')))
