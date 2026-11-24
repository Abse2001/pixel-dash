"""Render both outside copper layers in board coordinates using the exported outline."""
import argparse
import json
import math
from pathlib import Path

from gerbonara import GerberFile
from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("geometry", type=Path)
parser.add_argument("edge_cuts", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
objects = json.loads(args.geometry.read_text())
edges = GerberFile.open(args.edge_cuts).objects
vertices = [(edge.x1, -edge.y1) for edge in edges] + [(edge.x2, -edge.y2) for edge in edges]
left, top = map(min, zip(*vertices))
right, bottom = map(max, zip(*vertices))
width, height = right - left, bottom - top
scale = 12
width_px = math.ceil(width * scale)
height_px = math.ceil(height * scale)
margin = 48
image = Image.new("RGB", (2 * width_px + 3 * margin, height_px + 122), "#f6f7f5")
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("DejaVuSans.ttf", 15)
labels = {"U1": "AM3354", "U_DDR": "DDR3L", "U_PMIC": "PMIC", "J_CARRIER": "Carrier connector"}

for column, (layer, title) in enumerate([("F.Cu", "Component side"), ("B.Cu", "Carrier side · viewed from above")]):
    offset = margin + column * (width_px + margin)
    def pixel(point):
        return offset + (point[0] - left) * scale, 55 + (point[1] - top) * scale
    draw.text((offset, 20), title, font=font, fill="#152e28")
    # The module has a rectangular outline. Check for a changed contour before using the bounds.
    corners = {(left, top), (right, top), (left, bottom), (right, bottom)}
    assert len(edges) == 4 and set(vertices) == corners
    draw.rectangle((pixel((left, top)), pixel((right, bottom))), fill="#164636", outline="#203d33", width=2)
    for item in objects:
        if item["kind"] == "track" and item["layer"] == layer:
            color = "#edb15a" if item["net"].startswith("DDR_") else "#92b38c"
            draw.line([pixel(item["start"]), pixel(item["end"])], fill=color, width=max(1, round(scale * item["width"])))
        if item["kind"] == "via":
            x, y = pixel(item["pos"])
            radius = item["diam"] * scale / 2
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill="#915b30", outline="#dfba75")
    pads = [item for item in objects if item["kind"] == "pad" and item["layer"] == layer]
    for pad in pads:
        x, y = pixel(pad["pos"])
        w, h = [size * scale / 2 for size in pad["size"]]
        if pad["shape"] == 0:
            draw.ellipse((x-w, y-h, x+w, y+h), fill="#e3c989")
        else:
            a = math.radians(-pad["rot"])
            corners = [(x + u*math.cos(a) - v*math.sin(a), y + u*math.sin(a) + v*math.cos(a))
                       for u, v in ((-w,-h), (-w,h), (w,h), (w,-h))]
            draw.polygon(corners, fill="#c9c6a9")
    for ref, label in labels.items():
        points = [pad["pos"] for pad in pads if pad["ref"] == ref]
        if points:
            center = pixel([sum(axis) / len(points) for axis in zip(*points)])
            draw.rectangle(draw.textbbox(center, label, font=font, anchor="mm"), fill="#163328")
            draw.text(center, label, font=font, anchor="mm", fill="white")
draw.text((margin, height_px + 78), f"Pixel Dash   /   {width:.2f} × {height:.2f} mm   /   six-layer module",
          font=font, fill="#263f36")
image.save(args.output)
