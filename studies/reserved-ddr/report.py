"""Compute signed study flight and length screens for routed nets; mark every open net."""
import argparse
import csv
import json
import math
import runpy
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
checks = here.parents[1] / "checks"
sys.path.insert(0,str(checks))
from hdi_build import WURTH
from shapely.ops import unary_union

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("circuit",type=Path)
parser.add_argument("baseline_csv",type=Path)
args = parser.parse_args()
base = {r["signal"]: r for r in csv.DictReader(args.baseline_csv.open())}
board = json.loads(args.circuit.read_text())
src = {e["source_trace_id"]:e for e in board if e["type"]=="source_trace" and (e.get("name") or "").startswith("DDR_")}
ports = {e["source_port_id"]:e for e in board if e["type"]=="pcb_port" and "source_port_id" in e}
spans = {}
for tr in src.values():
    a,b = [ports[p] for p in tr["connected_source_port_ids"]]
    spans[tr["name"]] = abs(a["x"]-b["x"]) + abs(a["y"]-b["y"])
assert len(spans)==50
pair_lib = runpy.run_path(str(checks/"measure-ddr-pair-spacing.py"))
segs = pair_lib["pair_segments"](board)
mate = {n:m for a,b in pair_lib["PAIRS"] for n,m in [(a,b),(b,a)]}
rows = {}
for tr in board:
    if tr["type"]!="pcb_trace" or tr["source_trace_id"] not in src:continue
    n = src[tr["source_trace_id"]]["name"]
    path = tr["route"]
    length = sum(math.dist((a["x"],a["y"]),(b["x"],b["y"])) for a,b in zip(path,path[1:]))
    vias = [p for p in path if p["route_type"]=="via"]
    assert all({v["from_layer"],v["to_layer"]}=={"top","bottom"} for v in vias)
    depth = len(vias)*WURTH.outer_to_outer
    near = 0.
    if n in mate:
        for l,sections in segs[n].items():
            region = unary_union(segs[mate[n]].get(l,[])).buffer(.42,quad_segs=48)
            near += sum(e.intersection(region).length for e in sections)
    isolated = length*5.769+depth*6.600
    rows[n] = length,depth,isolated,isolated-near*.152,isolated-(length*.152 if n in mate else 0)
lane_nets = [[f"DDR_D{j}" for j in range(8*i,8*i+8)] + [f"DDR_DQM{i}",f"DDR_DQS{i}",f"DDR_DQSn{i}"] for i in (0,1)]
out = csv.writer(sys.stdout,lineterminator="\n")
out.writerow(["signal","study_status","baseline_length_mm","study_length_mm","barrel_mm","mixed_flight_ps","signed_mixed_vs_reference_ps","signed_worst_scenario_ps","model_limit_ps","model_excess_ps","nominal_min_mm","nominal_max_mm","nominal_excess_mm","TI_peer_excess_among_routed_mm","TI_strobe_or_pair_excess_mm","required_source_setup_1866_ps","required_source_hold_1866_ps","receiver_slack_ps"])
for n in sorted(spans):
    old=float(base[n]["planar_mm"])
    if n not in rows:
        out.writerow([n,"open",old]+[""]*15)
        continue
    length,depth,isolated,flight,odd=rows[n]
    lane=next((nets for nets in lane_nets if n in nets),None)
    prefix=[n,"routed",old,length,depth,flight]
    if n=="DDR_RESETn":
        out.writerow(prefix+[""]*12)
        continue
    if lane or n in ("DDR_CK","DDR_CKn"):
        pair=lane[-2:] if lane else ["DDR_CK","DDR_CKn"]
        peers=[q for q in pair if q!=n]
        mixed=max((flight-rows[q][3] for q in peers),key=abs)
        worst=max((rows[n][k]-rows[q][k] for q in peers for k in (2,3,4)),key=abs)
        mm=.127 if n in pair else .635
        dl=max(abs(length-rows[q][0]) for q in peers)
        peer=max(0,max(abs(length-rows[q][0]) for q in lane[:-2] if q in rows)-.635) if lane and n not in pair else ""
        limit=mm*(5.617 if n in pair else 5.769)
        timing=[mixed,worst,limit,max(0,abs(worst)-limit)]
        extra=[peer,max(0,dl-mm),"","",""]
    else:
        skew=flight-(rows["DDR_CK"][3]+rows["DDR_CKn"][3])/2
        timing=[skew,"","",""]
        extra=["","",65+skew,110-skew,"unknown"]
    if lane:
        lo,hi=0.,max(spans[q] for q in lane)
    else:
        longest=max(v for q,v in spans.items() if q!="DDR_RESETn" and not any(q in lane for lane in lane_nets))
        lo,hi=longest+6.35,longest+8.89
    vals=prefix+timing+[lo,hi,max(0,lo-length,length-hi)]+extra
    out.writerow([round(v,4) if isinstance(v,float) else v for v in vals])
