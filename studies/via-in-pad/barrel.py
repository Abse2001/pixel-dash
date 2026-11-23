"""Independently verify the two A10 filled-via locations against artwork and Excellon."""
import json, sys
from pathlib import Path
from zipfile import ZipFile
from shapely.geometry import Point
from gerbonara import ExcellonFile
from ddr_cam import artwork
from gerbonara.utils import MM

board=json.loads(Path(sys.argv[1]).read_bytes())
archive=Path(sys.argv[2])
vias=[e for e in board if e['type']=='pcb_via' and e['pcb_via_id'].startswith('vip_A10_')]
assert len(vias)==2
net,=[e for e in board if e['type']=='source_trace' and e.get('name')=='DDR_A10']
ports={e['source_port_id']:e for e in board if e['type']=='pcb_port' and e.get('source_port_id')}
faces=[artwork(archive, name) for name in ('F_Cu.gbr','In1_Cu.gbr','In2_Cu.gbr','B_Cu.gbr')]
with ZipFile(archive) as z:
    hits=ExcellonFile.from_string(z.read('drill-L1-L4.drl').decode()).objects
for via in vias:
    p=Point(via['x'],via['y'])
    port=min((ports[pid] for pid in net['connected_source_port_ids']),key=lambda e:p.distance(Point(e['x'],e['y'])))
    pad,=[e for e in board if e['type']=='pcb_smtpad' and e.get('pcb_port_id')==port['pcb_port_id']]
    # Inside the electrical land near the perimeter even after the 0.15 mm bore.
    anchor=Point(port['x']+.135,port['y'])
    hit,=[o for o in hits if hasattr(o,'x') and p.distance(Point(o.unit.convert_to(MM,o.x),o.unit.convert_to(MM,o.y)))<.003]
    assert abs(hit.tool.equivalent_width(MM)-.15)<1e-6
    center=Point(hit.unit.convert_to(MM,hit.x),hit.unit.convert_to(MM,hit.y))
    wall=center.buffer(.075,quad_segs=64).boundary
    top_pieces=None
    for index,face in enumerate(faces):
        # Only copper physically touching this plated wall qualifies.
        local=face.intersection(center.buffer(.28)).difference(center.buffer(.075,quad_segs=64))
        joined=[part for part in getattr(local,'geoms',[local]) if part.intersection(wall).length>.40]
        assert len(joined)==1,(via,index)
        if index==0:assert joined[0].covers(anchor),(via,'CPU or memory land')
    print(via['pcb_via_id'], 'four copper layers meet 0.150 mm plated bore; top BGA land joins wall')
