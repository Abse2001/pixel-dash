"""Test the assembled key cap with the retained handheld meshes and supplier OBJ."""
import argparse
import json
from pathlib import Path

import numpy as np
import trimesh

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("cap", type=Path, help="STL exported from mechanical/power-button.scad")
parser.add_argument("switch", type=Path, help="imported JLCPCB C110293 OBJ")
parser.add_argument("handheld", type=Path, help="retained handheld checkout at 5b7d96d")
args = parser.parse_args()
cap = trimesh.load_mesh(args.cap)
assert cap.is_volume
case = trimesh.collision.CollisionManager()
manifest = args.handheld / "mechanical/slim-lipo/manifest.json"
shells = set()
for part in json.loads(manifest.read_text()):
    if part["id"].startswith("J_PWR_SW"):
        continue
    mesh = trimesh.load_scene(args.handheld / part["model"]).to_geometry()
    if np.all(np.minimum(cap.bounds[1]+1, mesh.bounds[1]) > np.maximum(cap.bounds[0]-1, mesh.bounds[0])):
        case.add_object(part["id"], mesh)
        shells.add(part["id"])
assert "front-shell" in shells
key = trimesh.load_scene(args.switch)
for displacement in (0, -0.25, 0.15):
    sample = cap.copy()
    sample.apply_translation([0, displacement, 0])
    assert not case.in_collision_single(sample)
    distances = []
    for part in key.geometry.values():
        moving = np.isclose(part.bounds[0,1], -2.05, atol=0.001)
        mesh = part.copy()
        mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi,[0,0,1]))
        mesh.apply_translation([-25.35, 38.85-(0.20 if moving and displacement<0 else 0), 0.85])
        item = trimesh.collision.CollisionManager()
        item.add_object("switch", mesh)
        assert not item.in_collision_single(sample)
        if moving:
            distances.append(item.min_distance_single(sample))
    assert len(distances) == 1
    assert np.isclose(distances[0], {0:0.05, -0.25:0.0, 0.15:0.20}[displacement], atol=0.001)
    print(f"Cap translation {displacement:+.2f} mm, nearest enclosure/handheld clearance {case.min_distance_single(sample):.3f} mm")
