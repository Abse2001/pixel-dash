"""Joint constrained seed for a seven-net escape trial. Run once on the parent checkpoint."""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

root = Path(__file__).resolve().parents[2]
source = root / "am3354/connectivity-paths.json"
routes = json.loads(source.read_text())
board = json.loads(Path(sys.argv[1]).read_text())
sources = {s["source_trace_id"]: s["name"] for s in board if s["type"] == "source_trace" and s.get("name")}
traces = {sources[t["source_trace_id"]]: t["route"] for t in board if t["type"] == "pcb_trace" and t["source_trace_id"] in sources}
offset = np.array([-44.8, 15.15])
def flight(path):
    return sum(math.dist((a["x"],a["y"]), (b["x"],b["y"])) for a,b in zip(path,path[1:])) * 5.769 + sum(p["route_type"]=="via" for p in path)*1.420*6.60

def pair_delay(n):
    paths = [traces["DDR_"+s] for s in n]
    return np.mean([sum(math.dist((a["x"],a["y"]),(b["x"],b["y"])) for a,b in zip(p,p[1:])) * 5.617 + sum(q["route_type"]=="via" for q in p)*1.420*6.60 for p in paths])

with (root/"checks/current-boot-escape-corridors.csv").open() as handle:
    corridors = [row for row in csv.DictReader(handle) if row["ball"] in ("B5","N5")]
names = sorted(set(n for row in corridors for n in row["interfering_routes"].split()))
for name in names:
    route = routes[name]
    path = traces[name]
    anchors = [np.array([p["x"],p["y"]]) for p in (path[0],path[-1])]
    start = np.array([[p["x"],p["y"]] for p in route]) + offset
    vias = np.array([bool(p.get("via")) for p in route])
    radii = np.where(vias, .150, .051)
    lane = 0 if name=="DDR_D1" else 1
    target = pair_delay(("DQS"+str(lane),"DQSn"+str(lane))) if name in ("DDR_D1","DDR_D12","DDR_D14") else pair_delay(("CK","CKn"))
    def delay(x):
        points=np.vstack([anchors[0],x.reshape(-1,2),anchors[1]])
        return np.linalg.norm(np.diff(points,axis=0),axis=1).sum()*5.769+vias.sum()*1.420*6.60
    def objective(x):
        return ((delay(x)-target)/3.0)**2 + .12*np.sum((x.reshape(-1,2)-start)**2)
    constraints=[]
    for row in corridors:
        angle=math.radians(float(row["direction_degrees_from_positive_x"]))
        normal=np.array([math.cos(angle),math.sin(angle)])
        launch=np.array([float(row["launch_x_mm"]),float(row["launch_y_mm"])])
        limit=launch@normal - .408 - .051 - .005
        constraints.append(dict(type="ineq",fun=lambda x,n=normal,k=limit:k-x.reshape(-1,2)@n-radii))
    result=minimize(objective,start.flatten(),constraints=constraints,method="SLSQP",options={"maxiter":250,"ftol":1e-7})
    if not result.success:
        raise ValueError(name+" "+result.message)
    print(name, "vias", vias.sum(), "target_ps",round(target,3), "baseline_ps",round(flight(path),3),"trial_ps",round(delay(result.x),3))
    for item,pt in zip(route,result.x.reshape(-1,2)-offset):
        item.update(x=round(pt[0],7),y=round(pt[1],7))
lines=['{']
for i,(net,path) in enumerate(routes.items()):
    lines.append(f'  "{net}": [')
    lines.extend('    '+json.dumps(p)+(',' if j+1<len(path) else '') for j,p in enumerate(path))
    lines.append('  ]'+(',' if i+1<len(routes) else ''))
source.write_text('\n'.join(lines+['}'])+'\n')
