"""Match each byte conductor on the actual board against its mapped ball, peers and strobe."""
import csv
import json
import math
import runpy
import sys
from pathlib import Path

from shapely.geometry import LineString
from shapely import union_all

root = Path(__file__).resolve().parents[2]
flight = runpy.run_path(str(root / "checks/audit-ddr-flight.py"))
single, odd, barrel = (flight[k] for k in ("SINGLE", "ODD", "BARREL"))
depth = flight["DEPTH"]
names = [f"DDR_D{i}" for i in range(16)] + [f"DDR_{s}{i}" for i in (0,1) for s in ("DQS","DQSn","DQM")]

def extract(board):
    links = {e["source_trace_id"]: e for e in board if e["type"] == "source_trace" and e.get("name") in names}
    ports = {p["source_port_id"]: (p["x"],p["y"]) for p in board if p["type"] == "pcb_port" and p.get("source_port_id")}
    results = {}
    for t in board:
        if t["type"] != "pcb_trace" or t["source_trace_id"] not in links:
            continue
        link = links[t["source_trace_id"]]
        name = link["name"]
        if name in results:
            raise ValueError(f"Multiple signal paths on {name}")
        a,b = (ports[k] for k in link["connected_source_port_ids"])
        path = t["route"]
        xy = [(p["x"],p["y"]) for p in path]
        if math.dist(a,xy[0]) >= .0001 or math.dist(b,xy[-1]) >= .0001:
            raise ValueError(f"Ball endpoint mismatch on {name}")
        layers = {}
        for p,q,start,end in zip(path,path[1:],xy,xy[1:]):
            if start == end:
                continue
            layer = p.get("layer",p.get("to_layer"))
            if layer != q.get("layer",q.get("from_layer")):
                raise ValueError(f"Undrilled layer change on {name}")
            layers.setdefault(layer,[]).append(LineString([start,end]))
        vias = [p for p in path if p["route_type"] == "via"]
        vertical = sum(abs(depth[p["from_layer"]]-depth[p["to_layer"]]) for p in vias)
        length = sum(math.dist(x,y) for x,y in zip(xy,xy[1:]))
        results[name] = dict(length=length, barrel=vertical, vias='/'.join(p['from_layer']+'-'+p['to_layer'] for p in vias),
                             layers=layers, manhattan=abs(a[0]-b[0])+abs(a[1]-b[1]), flight=length*single+vertical*barrel)
    missing = sorted(set(names) - results.keys())
    if missing:
        raise ValueError("Missing byte routes: " + ", ".join(missing))
    return results

old,cur = [extract(json.loads(Path(p).read_bytes())) for p in sys.argv[1:]]
w = csv.writer(sys.stdout, lineterminator="\n")
w.writerow(["signal","prior_mm","current_mm","prior_via_spans","current_via_spans","barrel_mm","flight_mixed_ps","signed_worst_skew_ps","model_limit_ps","model_excess_ps","TI_peer_delta_mm","TI_peer_limit_mm","TI_strobe_or_pair_delta_mm","TI_strobe_or_pair_limit_mm","TI_excess_mm","placement_ceiling_mm","placement_excess_mm","matching_and_model","placement"])
failed = False
for lane in (0,1):
    data = [f"DDR_D{i}" for i in range(8*lane,8*lane+8)]+[f"DDR_DQM{lane}"]
    pair = [f"DDR_DQS{lane}",f"DDR_DQSn{lane}"]
    ceiling = max(cur[n]['manhattan'] for n in data+pair)
    for n,m in [pair,pair[::-1]]:
        r=cur[n]
        near=sum(line.intersection(union_all(cur[m]['layers'].get(layer,[])).buffer(.42,quad_segs=48)).length for layer,lines in r['layers'].items() for line in lines)
        r['modes']=[r['flight'],r['flight']-near*(single-odd),r['flight']-r['length']*(single-odd)]
    for n in data+pair:
        r=cur[n]; st=[p for p in pair if p!=n]; isdata=n in data
        peer=max(abs(r['length']-cur[d]['length']) for d in data) if isdata else 0
        mm=.635 if isdata else .127; ps=mm*(single if isdata else odd)
        delta=max(abs(r['length']-cur[p]['length']) for p in st)
        modes=r.get('modes',[r['flight']]*3)
        signed=max((x-y for p in st for x,y in zip(modes,cur[p]['modes'])),key=abs)
        err=max(0,abs(signed)-ps); ti=max(0,delta-mm,peer-.635); place=max(0,r['length']-ceiling)
        failed |= max(err, ti, place) > 1e-6
        vals=[n,old[n]['length'],r['length'],old[n]['vias'],r['vias'],r['barrel'],modes[1],signed,ps,err,peer if isdata else '',.635 if isdata else '',delta,mm,ti,ceiling,place,'FAIL' if max(err,ti)>1e-6 else 'PASS','FAIL' if place>1e-6 else 'PASS']
        w.writerow(round(v,5) if isinstance(v,float) else v for v in vals)
sys.exit(int(failed))
