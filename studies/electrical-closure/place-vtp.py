"""Place the existing reverse-side VTP resistor at its verified escape and remove the former ground stub."""
import json
import math
import runpy
import sys

from shapely.ops import unary_union
from pathlib import Path
b=json.loads(Path(sys.argv[1]).read_bytes());plan=json.loads(Path(sys.argv[3]).read_bytes());ids={e.get(e['type']+'_id'):e for e in b}
r,=[e for e in b if e['type']=='pcb_component' and ids[e['source_component_id']].get('name')=='R_VTP'];cx,cy=r['center']['x'],r['center']['y']
if r['layer']!='bottom' or r['rotation']!=135:raise ValueError('Unexpected VTP footprint pose')
a,z=plan['a'],plan['z'];nx,ny=(a[0]+z[0])/2,(a[1]+z[1])/2;angle=plan['angle']+45;sn,cs=math.sin(math.radians(angle)),math.cos(math.radians(angle))
def transform(p):
 x,y=p['x']-cx,p['y']-cy;p.update(x=nx+cs*x-sn*y,y=ny+sn*x+cs*y)
for e in b:
 if e.get('pcb_component_id')!=r['pcb_component_id']:continue
 if 'x' in e and 'y' in e:transform(e)
 for k in ('center','footprint_origin','position','anchor_position'):
  if k in e:transform(e[k])
 for k in ('outline','route','points'):
  for p in e.get(k,[]):transform(p)
 for k in ('ccw_rotation','rect_ccw_rotation','rotation'):
  if isinstance(e.get(k),(float,int)):e[k]=(e[k]+angle)%360
 if e['type']=='cad_component':e['rotation']['z']=(e['rotation']['z']-angle)%360
for k,delta in [('x',nx-cx),('y',ny-cy)]:
 f='display_offset_'+k
 if f in r:r[f]=f"{float(r[f].removesuffix('mm'))+delta:.9f}mm"
for pid,want in [('channel_pcb_port_784',a),('channel_pcb_port_785',z)]:
 if math.dist([ids[pid]['x'],ids[pid]['y']],want)>1e-7:raise ValueError('VTP pin pose mismatch')
stub=ids['pcb_support_R_VTP_pin2_wire_0']
if stub['type']!='pcb_trace' or stub['route'][0]['layer']!='bottom':raise ValueError('Unexpected legacy VTP stub')
b.remove(stub)
# The baseline pours predate the placement change. Re-clear the two actual lands.
root = Path(__file__).resolve().parents[2]
checks = root / 'checks'
copper = runpy.run_path(str(checks/'audit-copper-contacts.py'))['copper'](b)['bottom']
fill = runpy.run_path(str(root/'studies/command-routing/plane_fill.py'))['connected_fill']
pads = [(k,sh) for oid,k,sh in copper if ids[oid].get('pcb_component_id')==r['pcb_component_id'] and ids[oid]['type']=='pcb_smtpad']
for oid,k,sh in copper:
 pour=ids[oid]
 if pour['type']!='pcb_copper_pour':continue
 avoid=unary_union([p.buffer(.16,quad_segs=96) for net,p in pads if k!=net])
 if not sh.intersects(avoid):continue
 poly=fill(sh.difference(avoid),pour,b)
 def ring(edge):return {'vertices':[dict(x=x,y=y) for x,y in list(edge.coords)[:-1]]}
 pour['brep_shape']=dict(outer_ring=ring(poly.exterior),inner_rings=[ring(e) for e in poly.interiors])
Path(sys.argv[2]).write_text(json.dumps(b,separators=(',',':')))
