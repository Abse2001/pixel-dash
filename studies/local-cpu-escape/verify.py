"""Compare both byte lanes to the signed-off layout across the complete physical trace and attached via arrays."""
import json
import runpy
import sys
from pathlib import Path

study = Path(__file__).resolve().parent
locks = runpy.run_path(str(study.parent / "data-bytes/check-locked-routes.py"))
baseline, trial = [json.loads(Path(p).read_bytes()) for p in sys.argv[1:3]]
expected = json.loads(locks["LOCK"].read_bytes())
if locks["fingerprints"](baseline) != expected:
    raise ValueError("Baseline data-byte fingerprint mismatch")
actual = locks["fingerprints"](trial)
changed = {n for n in expected if expected[n] != actual[n]}
if changed != {"DDR_D12", "DDR_D14"}:
    raise ValueError(f"Unexpected changed byte routes: {changed}")

def objects(board):
    return {e[e["type"]+"_id"]: e for e in board if e["type"]+"_id" in e}

before, after = objects(baseline), objects(trial)
points = json.loads((study / "waypoints.json").read_bytes())
for trace in baseline:
    if trace["type"] != "pcb_trace":
        continue
    name = before[trace["source_trace_id"]].get("name")
    if name not in changed:
        continue
    approved = points[name]
    if len(approved) > {"DDR_D12":7, "DDR_D14":10}[name]:
        raise ValueError(f"CPU-side span expanded on {name}")
    restored = dict(after[trace["pcb_trace_id"]])
    restored["route"] = [dict(p) for p in restored["route"]]
    for j,(x,y) in enumerate(approved):
        new, old = restored["route"][j], trace["route"][j]
        if new["route_type"] != "wire" or new["layer"] != "top" or (new["x"],new["y"]) != (x,y):
            raise ValueError(f"Unexpected trial waypoint on {name}")
        if j in (0,len(approved)-1) and (old["x"],old["y"]) != (x,y):
            raise ValueError(f"Changed terminal or downstream splice on {name}")
        new.update(x=old["x"], y=old["y"])
    if restored != trace:
        raise ValueError(f"Changed geometry outside the approved prefix on {name}")
    for v in baseline:
        if v["type"] == "pcb_via" and v.get("pcb_trace_id") == trace["pcb_trace_id"] and v != after[v["pcb_via_id"]]:
            raise ValueError(f"Changed data via on {name}")
print("20 original byte fingerprints match. Only approved CPU-side D12 and D14 wire coordinates differ. All 44 data vias are retained.")
