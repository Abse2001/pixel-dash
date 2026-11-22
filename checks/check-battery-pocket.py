"""Screen exported wide-shell pocket solids against pack envelopes and PCB mounts."""
import json
import sys

import numpy as np
import trimesh
from shapely.geometry import Point, box

board_path, flat_mesh, compact_mesh = sys.argv[1:]
with open(board_path) as stream:
    board = json.load(stream)
mounts = [(p["x"], p["y"]) for p in board if p["type"] == "pcb_hole" and p["hole_diameter"] == 3.3]
if len(mounts) != 4:
    raise ValueError("Expected four 3.3 mm mounting holes")
for name, mesh_path, dimensions, cy in (
    ("MakerFocus 9065115", flat_mesh, (114, 67, 10.8), -10.5),
    ("PKCELL 5035", compact_mesh, (69, 56.5, 19), 0),
):
    mesh = trimesh.load_mesh(mesh_path)
    x, y, z = dimensions
    if not mesh.is_volume or len(mesh.split()) != 1:
        raise ValueError(f"Invalid pocket solid for {name}")
    expected = [[-x/2-2.5, cy-y/2-2.5, -z-3.5], [x/2+2.5, cy+y/2+2.5, 0]]
    if not np.allclose(mesh.bounds, expected, atol=1e-5):
        raise ValueError(f"Incorrect outer envelope for {name}")
    # Stack the specified maximum pack on the pocket floor, allowing 0.01 mm
    # between surfaces for the intersection calculation.
    cell = trimesh.creation.box(dimensions)
    cell.apply_translation([0, cy, -z/2-1.99])
    if mesh.intersection(cell, engine="manifold").volume > 1e-6:
        raise ValueError(f"{name} body intersects pocket walls")
    outer = box(*mesh.bounds[0][:2], *mesh.bounds[1][:2])
    conflicts = [p for p in mounts if outer.distance(Point(p)) < 4.1]
    print(f"{name}: closed pocket solid, maximum pack body clears walls. "
          f"Overlapping 8.2 mm boss envelopes in plan: {conflicts}")
