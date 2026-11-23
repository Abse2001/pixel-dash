"""Screen fully captured via-in-pad center regions on the populated Pixel Dash board."""
import csv
import json
from pathlib import Path
import runpy
import sys

from shapely.geometry import Point
from shapely.ops import unary_union

board = json.loads(Path(sys.argv[1]).read_bytes())
checks = Path(sys.argv[2])
elements = {e.get(e['type'] + '_id'): e for e in board}
ports = {e['source_port_id']: e for e in board if e['type'] == 'pcb_port' and e.get('source_port_id')}
pads = {e['pcb_port_id']: e for e in board if e['type'] == 'pcb_smtpad' and e.get('pcb_port_id')}
geometry = runpy.run_path(str(checks / 'audit-copper-contacts.py'))
layers = ('top', 'inner1', 'inner2', 'bottom')
reference = dict(zip(layers, ('inner1', 'inner2', 'inner1', 'inner2')))
copper = geometry['copper'](board)
sources = {e['source_trace_id']: e for e in board if e['type'] == 'source_trace'}
ddr = {e.get('subcircuit_connectivity_map_key') for e in sources.values() if (e.get('name') or '').startswith('DDR_')}
routed = {e['source_trace_id'] for e in board if e['type'] == 'pcb_trace'}
writer = csv.writer(sys.stdout, lineterminator='\n')
writer.writerow(('net','ball','side','span','pad_diameter_mm','captured_area_mm2','copper_drill_area_mm2','protected_area_mm2','witness_x','witness_y','center_legal','dominant_obstacle'))
for sid, source in sorted(sources.items()):
    name = source.get('name') or ''
    boot = name in {f'SYSBOOT{i}_SENSE' for i in (1,2,3,4,5,6,7,10)}
    if not boot and (not name.startswith('DDR_') or sid in routed):
        continue
    key = source['subcircuit_connectivity_map_key']
    for pid in source['connected_source_port_ids']:
        port = ports[pid]
        pad = pads[port['pcb_port_id']]
        side = elements[elements[pad['pcb_component_id']]['source_component_id']]['name']
        if side not in ('U1','U_DDR'):
            continue
        ball = elements[pid]['name']
        metal = geometry['pad_shape'](pad)
        center = Point(port['x'],port['y'])
        # Center the stacked buried via under the top blind. Its larger L2 land is internal.
        for label, radii, drills in (
            ('L1-L2', (.14,.14), ((0,1,.125),)),
            ('L1-L4', (.15,.15,.15,.15), ((0,3,.15),)),
            ('L1-L2+L2-L3', (.14,.18,.18), ((0,1,.125),(1,2,.20))),
        ):
            capture = metal.buffer(-radii[0],quad_segs=96)
            blocks, shadows = [], []
            for i,radius in enumerate(radii):
                for oid,peer,shape in copper[layers[i]]:
                    typ = elements[oid]['type']
                    if peer == key or typ == 'pcb_copper_pour' or shape.distance(center) > .95:
                        continue
                    clearance = .1524 if typ == 'pcb_trace' else .102
                    if boot and i in (0,3) and peer in ddr and typ in ('pcb_trace','pcb_via'):
                        clearance = max(clearance,.408)
                    blocks.append((oid,shape.buffer(radius+clearance,quad_segs=96)))
                for layer,ref in reference.items():
                    if ref != layers[i]:
                        continue
                    for oid,peer,shape in copper[layer]:
                        e = elements[oid]
                        if peer == key or e['type'] != 'pcb_trace' or shape.distance(center) > .95:
                            continue
                        if peer in ddr or e['source_trace_id'].startswith(('system_SD_','system_LCD_','system_boot_tap_')):
                            shadows.append((oid,shape.buffer(radius+.16,quad_segs=96)))
            for via in board:
                if via['type'] != 'pcb_via':
                    continue
                v = Point(via['x'],via['y'])
                if v.distance(center) > .95:
                    continue
                for first,last,drill in drills:
                    if set(layers[first:last+1]).isdisjoint(via['layers']):
                        continue
                    blind = (last-first==1 and first in (0,2)) or (len(via['layers'])==2 and bool(set(via['layers']) & {'top','bottom'}))
                    gap = .24 if blind else .20
                    blocks.append((via['pcb_via_id'],v.buffer(gap+(drill+via['hole_diameter'])/2,quad_segs=96)))
            physical = capture.difference(unary_union([s for _,s in blocks]))
            region = physical.difference(unary_union([s for _,s in shadows]))
            witness = region.representative_point() if region.area else None
            largest = max(blocks+shadows,key=lambda entry: capture.intersection(entry[1]).area,default=None)
            writer.writerow((name,ball,side,label,round(metal.bounds[2]-metal.bounds[0],5),
                             round(capture.area,9),round(physical.area,9),round(region.area,9),
                             round(witness.x,6) if witness else '',round(witness.y,6) if witness else '',
                             region.covers(center),largest[0] if largest and capture.intersects(largest[1]) else ''))
