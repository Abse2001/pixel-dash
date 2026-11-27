# Plot the planner's copper model (plan-items.json) and optional routes: python3 plot.py out.png [x0 y0 x1 y1] [scale]
import json, sys, math
from PIL import Image, ImageDraw
d = json.load(open(__file__.rsplit('/', 1)[0] + '/plan-items.json'))
a = sys.argv
x0, y0, x1, y1 = (float(a[2]), float(a[3]), float(a[4]), float(a[5])) if len(a) > 5 else (-78.65, -4.85, -23.65, 35.15)
S = float(a[6]) if len(a) > 6 else 36
W, H = int((x1 - x0) * S), int((y1 - y0) * S)
only = a[7] if len(a) > 7 else None
img = Image.new('RGB', (W, H), (0, 0, 0)); dr = ImageDraw.Draw(img, 'RGBA')
X = lambda x: (x - x0) * S; Y = lambda y: (y1 - y) * S
def draw(it, col):
    p = it['pts']; r = it['r'] * S
    if len(p) == 1: dr.ellipse([X(p[0]['x']) - r, Y(p[0]['y']) - r, X(p[0]['x']) + r, Y(p[0]['y']) + r], fill=col)
    elif len(p) == 2:
        dr.line([X(p[0]['x']), Y(p[0]['y']), X(p[1]['x']), Y(p[1]['y'])], fill=col, width=max(1, int(round(2 * r))))
        for q in p: dr.ellipse([X(q['x']) - r, Y(q['y']) - r, X(q['x']) + r, Y(q['y']) + r], fill=col)
    else: dr.polygon([(X(q['x']), Y(q['y'])) for q in p], fill=col)
for layer, col in (('bottom', (60, 120, 255, 170)), ('top', (255, 60, 60, 170))):
    if only and only != layer: continue
    for it in d['items']:
        if it['layers'] == [layer]: draw(it, col)
for it in d['items']:
    if len(it['layers']) == 2: draw(it, (60, 220, 90, 255) if it['net'] == 'GND' else (255, 210, 60, 255) if it['kind'] != 'ddrvia' else (255, 0, 255, 255))
for b in d['bodies']:
    if only and b['layer'] != only: continue
    pts = [(X(q['x']), Y(q['y'])) for q in b['s']['pts']]; dr.line(pts + [pts[0]], fill=(255, 255, 255, 200) if b['layer'] == 'top' else (150, 200, 255, 200), width=1)
dr.rectangle([X(-78.65), Y(35.15), X(-23.65), Y(-4.85)], outline=(200, 200, 200, 255))
img.save(a[1]); print(a[1], W, H)
