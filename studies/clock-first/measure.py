"""Measure the partial bus from actual route and via geometry on the reference stack."""
import csv
import gzip
import json
import math
import runpy
import sys
from pathlib import Path

from shapely.geometry import LineString
from shapely.ops import unary_union

checks = Path(__file__).resolve().parents[2] / "checks"
sys.path.insert(0, str(checks))
model = runpy.run_path(str(checks / "audit-ddr-flight.py"))
depth = model["DEPTH"]
clock = ("DDR_CK", "DDR_CKn")

def load(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt") as f:
            return json.load(f)
    return json.loads(path.read_bytes())

def measure(board):
    sources = {e["source_trace_id"]: e for e in board if e["type"] == "source_trace"}
    ports = {e["source_port_id"]: e for e in board if e["type"] == "pcb_port" and e.get("source_port_id")}
    names = {k: e["name"] for k, e in sources.items() if (e.get("name") or "").startswith("DDR_")
             and not e["name"].startswith("DDR_D")}
    spans = {}
    paths = {}
    vias = {}
    for k, n in names.items():
        a, b = [ports[i] for i in sources[k]["connected_source_port_ids"]]
        spans[n] = abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])
    for trace in board:
        if trace["type"] != "pcb_trace" or trace["source_trace_id"] not in names:
            continue
        n = names[trace["source_trace_id"]]
        if n in paths:
            raise ValueError(f"Multiple traces on {n}")
        paths[n] = {}
        vias[n] = []
        for p in trace["route"]:
            if p["route_type"] == "via":
                vias[n].append((p["from_layer"], p["to_layer"]))
        for a, b in zip(trace["route"], trace["route"][1:]):
            x, y = (a["x"], a["y"]), (b["x"], b["y"])
            if x == y:
                continue
            l = a.get("layer", a.get("to_layer"))
            if l != b.get("layer", b.get("from_layer")):
                raise ValueError(f"Layer change without drill on {n}")
            paths[n].setdefault(l, []).append(LineString([x,y]))
    results = {}
    for n, sections in paths.items():
        outer = sum(s.length for l, ss in sections.items() if l in ("top","bottom") for s in ss)
        inner = sum(s.length for l, ss in sections.items() if l in ("inner1","inner2") for s in ss)
        barrel = sum(abs(depth[a] - depth[b]) for a,b in vias[n])
        near = 0
        if n in clock:
            mate = paths[clock[1 - clock.index(n)]]
            for l, segs in sections.items():
                envelope = unary_union(mate.get(l, [])).buffer(.42, quad_segs=48)
                near += sum(s.intersection(envelope).length for s in segs)
        # Inner traces use a homogeneous Dk=4.0 sensitivity pending a layer-specific field solve.
        flight = (outer - near)*model["SINGLE"] + near*model["ODD"] + inner*2/.299792458 + barrel*model["BARREL"]
        results[n] = dict(length=outer+inner, barrel=barrel, near=near, inner=inner, flight=flight,
                          spans="/".join(a+">"+b for a,b in vias[n]))
    nominal = max(v for n,v in spans.items() if n != "DDR_RESETn") + 7.62
    return spans, results, nominal

names, now, nominal = measure(load(Path(sys.argv[1])))
_, prior, _ = measure(load(Path(sys.argv[2])))
lo, hi = nominal-1.27, nominal+1.27
ck_mean = sum(now[n]["flight"] for n in clock)/2
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(["net","prior_mm","current_mm","contact_spans","total_barrel_mm","inner_mm","within_0.42mm_of_mate_mm",
                 "estimated_flight_ps","signed_ps_to_mate_or_CK_mean","placement_window_mm","window_excess_mm",
                 "pair_limit_mm","pair_excess_mm","receiver_timing"])
for n in sorted(names):
    old = round(prior[n]["length"],4) if n in prior else "open"
    if n not in now:
        writer.writerow([n,old,"open",*([""]*10),"OPEN"])
        continue
    r = now[n]
    other = now[clock[1-clock.index(n)]] if n in clock else None
    excess = max(lo-r["length"],r["length"]-hi,0)
    writer.writerow([n,old,round(r["length"],5),r["spans"],round(r["barrel"],4),round(r["inner"],4),
                     round(r["near"],4) if other else "",round(r["flight"],3),
                     round(r["flight"]-(other["flight"] if other else ck_mean),3),
                     f"{lo:.5f}..{hi:.5f}" if n!="DDR_RESETn" else "",round(excess,5) if n!="DDR_RESETn" else "",
                     .127 if other else "",round(max(0,abs(r["length"]-other["length"])-.127),5) if other else "",
                     "clock" if other else "OPEN"])
if any(not lo <= now[n]["length"] <= hi for n in clock) or abs(now[clock[0]]["length"]-now[clock[1]]["length"])>.127:
    sys.exit("Clock length or pair mismatch exceeds limit")
