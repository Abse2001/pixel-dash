# Renders every copper layer of dist/module.circuit.json to fab/views/<layer>.png (bottom-side views are NOT mirrored).
import json, os
from PIL import Image, ImageDraw
d = os.path.dirname(os.path.abspath(__file__)); cj = json.load(open(d + '/dist/module.circuit.json'))
b = [e for e in cj if e['type'] == 'pcb_board'][0]; W, H = b['width'], b['height']; S = 40
X = lambda x: (x + W / 2) * S; Y = lambda y: (H / 2 - y) * S
os.makedirs(d + '/fab/views', exist_ok=True)
COL = {'top': (200, 50, 50), 'inner1': (60, 150, 60), 'inner2': (210, 140, 40), 'inner3': (170, 80, 200), 'inner4': (60, 150, 60), 'bottom': (60, 110, 230)}
import math
for layer, col in COL.items():
    img = Image.new('RGB', (int(W * S), int(H * S)), (10, 10, 10)); dr = ImageDraw.Draw(img)
    for p in cj:
        if p['type'] == 'pcb_copper_pour' and p['layer'] == layer:
            m = Image.new('L', img.size, 0); md = ImageDraw.Draw(m)
            md.polygon([(X(v['x']), Y(v['y'])) for v in p['brep_shape']['outer_ring']['vertices']], fill=255)
            for h in p['brep_shape']['inner_rings']: md.polygon([(X(v['x']), Y(v['y'])) for v in h['vertices']], fill=0)
            n = p.get('net_name', ''); c = {'GND': (40, 110, 40), 'VDDS_DDR': (190, 120, 30), 'VDD_3V3': (60, 170, 190), 'VDD_1V8': (170, 70, 170), 'VDD_CORE': (200, 110, 110), 'VDD_MPU': (200, 200, 200), 'DDR_VREF': (70, 110, 220)}.get(n, (230, 230, 60))
            img.paste(c, (0, 0), m)
    dr = ImageDraw.Draw(img)
    for t in cj:
        if t['type'] != 'pcb_trace': continue
        r = t['route']
        for i in range(len(r) - 1):
            a, c2 = r[i], r[i + 1]
            if a.get('layer') == layer and c2.get('layer') == layer and a['route_type'] == 'wire' and c2['route_type'] == 'wire':
                w = max(1, int(round(a['width'] * S))); dr.line([X(a['x']), Y(a['y']), X(c2['x']), Y(c2['y'])], fill=col if layer in ('top', 'bottom') else (255, 255, 0), width=w)
    for p in cj:
        if p['type'] == 'pcb_smtpad' and p['layer'] == layer:
            if p['shape'] == 'circle': r = p['radius'] * S; dr.ellipse([X(p['x']) - r, Y(p['y']) - r, X(p['x']) + r, Y(p['y']) + r], fill=(235, 190, 120))
            else:
                a = math.radians(p.get('ccw_rotation', 0)); w, h = p['width'] / 2, p['height'] / 2
                dr.polygon([(X(p['x'] + i * w * math.cos(a) - j * h * math.sin(a)), Y(p['y'] + i * w * math.sin(a) + j * h * math.cos(a))) for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))], fill=(235, 190, 120))
    for v in cj:
        if v['type'] == 'pcb_via': r = v['outer_diameter'] / 2 * S; dr.ellipse([X(v['x']) - r, Y(v['y']) - r, X(v['x']) + r, Y(v['y']) + r], fill=(240, 240, 240)); r = v['hole_diameter'] / 2 * S; dr.ellipse([X(v['x']) - r, Y(v['y']) - r, X(v['x']) + r, Y(v['y']) + r], fill=(0, 0, 0))
    for h in cj:
        if h['type'] == 'pcb_hole': r = h.get('hole_diameter', 2.2) / 2 * S; dr.ellipse([X(h['x']) - r, Y(h['y']) - r, X(h['x']) + r, Y(h['y']) + r], outline=(255, 255, 255))
    img.save(f"{d}/fab/views/{layer}.png")
print('views written')
