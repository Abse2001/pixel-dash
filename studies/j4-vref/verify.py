"""Verify all byte copper against the protected build, allowing only two L1 prefixes."""
import json
import runpy
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
locked = runpy.run_path(str(here.parent / "data-bytes/check-locked-routes.py"))
base, trial = [json.loads(Path(p).read_bytes()) for p in sys.argv[1:3]]
expected = json.loads(locked["LOCK"].read_bytes())
if locked["fingerprints"](base) != expected:
    raise ValueError("Protected route fingerprint mismatch")
changed = {n for n, digest in locked["fingerprints"](trial).items() if expected[n] != digest}
if changed != {"DDR_D12", "DDR_D14"}:
    raise ValueError(f"Unexpected changed byte nets {changed}")
old = {e.get(e["type"]+"_id"): e for e in base}
new = {e.get(e["type"]+"_id"): e for e in trial}
points = json.loads((here / "waypoints.json").read_bytes())
for trace in base:
    if trace["type"] != "pcb_trace":
        continue
    name = old[trace["source_trace_id"]].get("name")
    if name not in changed:
        continue
    tid = trace["pcb_trace_id"]
    size = {"DDR_D12": 7, "DDR_D14": 10}[name]
    prefix = [dict(trace["route"][1], x=x, y=y) for x,y in points[name][1:-1]]
    approved = [trace["route"][0], *prefix, *trace["route"][size-1:]]
    if new[tid] != dict(trace, route=approved):
        raise ValueError(f"Unapproved {name} geometry")
    before = [v for v in base if v["type"] == "pcb_via" and v.get("pcb_trace_id") == tid]
    after = [v for v in trial if v["type"] == "pcb_via" and v.get("pcb_trace_id") == tid]
    if before != after:
        raise ValueError(f"Changed {name} via")
print("20 original byte fingerprints match. Both edited prefixes match the approved waypoints. All 44 data vias match.")
