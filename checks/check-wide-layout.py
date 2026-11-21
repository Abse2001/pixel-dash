"""Check the rigid PCB contour, control spacing and moved mechanism clearances."""
import json
import sys
from pathlib import Path

import trimesh
from shapely.geometry import Polygon, box

a=json.loads(Path(sys.argv[1]).read_text())
board, = [p for p in a if p["type"]=="pcb_board"]
shape=Polygon([(p["x"],p["y"]) for p in board["outline"]])
assert shape.is_valid and shape.bounds==(-116,-41,116,41) and board["num_layers"]==4
assert sum(p["type"]=="pcb_cutout" for p in a)==3
names={e["source_component_id"]:e["name"] for e in a if e["type"]=="source_component"}
assert {"front_shell","rear_shell","lcd_body","lipo_battery"}.isdisjoint(names.values())
panel=box(-164.9/2,-50,164.9/2,50)
controls={"button_a","button_b","button_x","button_y","button_start","button_select","dpad","left_joystick","right_joystick"}
seen=set()
controls_3d=trimesh.collision.CollisionManager()
for e in a:
    if e["type"]!="cad_component":continue
    name=names.get(e.get("source_component_id"))
    if name in controls:
        model=Path(__file__).resolve().parents[1]/e["model_glb_url"]
        mesh=trimesh.load_scene(model).to_geometry()
        low,high=mesh.bounds
        dx,dy=e["position"]["x"],e["position"]["y"]
        rect=box(low[0]+dx,low[1]+dy,high[0]+dx,high[1]+dy)
        assert rect.disjoint(panel),name
        mesh.apply_translation([dx,dy,e["position"]["z"]])
        controls_3d.add_object(name,mesh)
        seen.add(name)
assert seen==controls
collision,hits=controls_3d.in_collision_internal(return_names=True)
assert not collision,hits
print(f"232 × 82 mm one-piece board and {len(seen)} control envelopes clear the centered bare LCD outline in plan view.")
