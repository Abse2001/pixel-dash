# python3 plot-planes.py out-prefix : one PNG per inner layer from planes-raster.json
import json, sys, base64
from PIL import Image
d = json.load(open(__file__.rsplit('/', 1)[0] + '/planes-raster.json'))
cols = [(0, 0, 0), (70, 160, 70), (230, 120, 40), (220, 60, 60), (240, 200, 60), (80, 140, 240), (200, 90, 220), (90, 220, 220), (255, 255, 255), (255, 150, 150), (150, 255, 150)]
for l, b in enumerate(d['layers']):
    raw = base64.b64decode(b); img = Image.new('RGB', (d['NX'], d['NY']))
    img.putdata([cols[v % len(cols)] for v in raw]); img = img.transpose(Image.FLIP_TOP_BOTTOM).resize((d['NX'] * 2, d['NY'] * 2), Image.NEAREST)
    img.save(f"{sys.argv[1]}-L{l + 2}.png")
print(d['nets'])
