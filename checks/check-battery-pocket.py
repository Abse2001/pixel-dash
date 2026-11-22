"""Screen exported wide-shell pocket solids against pack envelopes and PCB mounts."""
import json
import sys

import numpy as np
import trimesh
from shapely.geometry import Point, box

board_path, flat_mesh, compact_mesh, carrier_mesh = sys.argv[1:]
with open(board_path) as stream:
    board = json.load(stream)
mounts = [(p["x"], p["y"]) for p in board if p["type"] == "pcb_hole" and p["hole_diameter"] == 3.3]
if set(mounts) != {(-70,-29), (70,-29), (-60,31), (60,31)} or len(mounts) != 4:
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
    overlap = mesh.intersection(cell, engine="manifold")
    if not overlap.is_empty and overlap.volume > 1e-6:
        raise ValueError(f"{name} body intersects pocket walls")
    outer = box(*mesh.bounds[0][:2], *mesh.bounds[1][:2])
    conflicts = [p for p in mounts if outer.distance(Point(p)) < 4.1]
    if conflicts:
        raise ValueError(f"Pack pocket collides with bosses at {conflicts}")
    print(f"{name}: closed pocket solid, maximum pack body clears walls. "
          f"Overlapping 8.2 mm boss envelopes in plan: {conflicts}")

# Verify actual material and voids through the exported rear carrier at each PCB seat.
carrier = trimesh.load_mesh(carrier_mesh)
if not carrier.is_volume or len(carrier.split()) != 1:
    raise ValueError("Rear carrier must be one closed solid")
if not np.allclose(carrier.bounds, [[-119.5,-51,-20.3],[119.5,51,-0.8]], atol=1e-5):
    raise ValueError("Unexpected carrier extent")
for x, y in mounts:
    for z, bore in ((-1.0, 1.65), (-6.0, 3.1)):
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            probes = [[x+dx*r, y+dy*r, z] for r in (bore-.03, bore+.03, 4.07, 4.13)]
            if carrier.contains(probes).tolist() != [False,True,True,False]:
                raise ValueError(f"Incorrect seat, head relief or outside wall at {(x,y,z)}")
print("All four rear-carrier screw bores and head recesses align with the current PCB holes.")
