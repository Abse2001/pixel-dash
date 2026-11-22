"""Add named support connections, retaining each existing rail and all locked data copper."""
import json
import sys
from pathlib import Path
from plane_fill import connected_fill
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

board=json.loads(Path(sys.argv[1]).read_bytes())
sys.path.insert(0,str(Path(__file__).resolve().parents[2] / "production"))
from connectivity import trace_net_keys
_, trace_keys=trace_net_keys(board)
plan_file = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).with_name("support-paths.json")
plans = json.loads(plan_file.read_bytes())
ids={e.get(e["type"]+"_id"):e for e in board}
ports={}
for p in board:
    if p["type"]=="pcb_port" and p.get("source_port_id"):
        source=ids[p["source_port_id"]]
        name=ids[source["source_component_id"]].get("name")
        if name:
            ports[name+"."+source["name"]]=p
cuts=[]
for plan in plans:
    start=ports[plan["start"]]
    sources=[s for s in board if s["type"]=="source_trace" and start["source_port_id"] in s["connected_source_port_ids"]]
    keys={trace_keys[s["source_trace_id"]] for s in sources}
    if len(keys)!=1:
        raise ValueError(f"Unexpected net on {plan['start']}")
    key=keys.pop()
    if "rail" in plan:
        rail,=(e for e in board if e["type"]=="source_net" and e["name"]==plan["rail"])
        if key!=rail["subcircuit_connectivity_map_key"]:
            raise ValueError(f"Wrong rail on {plan['start']}")
    if "end" in plan:
        end=ports[plan["end"]]
        if not any(s["type"]=="source_trace" and end["source_port_id"] in s["connected_source_port_ids"] and trace_keys[s["source_trace_id"]]==key for s in board):
            raise ValueError(f"Wrong destination net on {plan['end']}")
    prefix="pcb_support_"+plan["start"].replace(".","_")
    for i,(layer,width,points) in enumerate(plan["sections"]):
        if len(set(map(tuple,points)))==1:continue
        path=[dict(route_type="wire",x=x,y=y,layer=layer,width=width) for x,y in points]
        board.append(dict(type="pcb_trace",pcb_trace_id=f"{prefix}_wire_{i}",source_trace_id=sources[0]["source_trace_id"],subcircuit_connectivity_map_key=key,route=path))
        cuts.append((key,[layer],LineString(points).buffer(width/2+.16,quad_segs=96)))
    for i,((x,y),layers,diam,drill) in enumerate(plan["vias"]):
        board.append(dict(type="pcb_via",pcb_via_id=f"{prefix}_via_{i}",x=x,y=y,from_layer=layers[0],to_layer=layers[-1],
                          layers=layers,outer_diameter=diam,hole_diameter=drill,subcircuit_connectivity_map_key=key,source_trace_id=sources[0]["source_trace_id"]))
        cuts.append((key,layers,Point(x,y).buffer(diam/2+.16,quad_segs=192)))
for pour in board:
    if pour["type"]!="pcb_copper_pour":continue
    key=ids[pour["source_net_id"]]["subcircuit_connectivity_map_key"]
    avoid=unary_union([g for k,ls,g in cuts if key!=k and pour["layer"] in ls])
    shape=pour["brep_shape"]
    def coords(r):
        return [(p["x"],p["y"]) for p in r["vertices"]]
    original=Polygon(coords(shape["outer_ring"]),[coords(r) for r in shape["inner_rings"]])
    if not original.intersects(avoid):continue
    result=original.difference(avoid)
    result = connected_fill(result, pour, board)
    def ring(r):
        return {"vertices":[dict(x=x,y=y) for x,y in list(r.coords)[:-1]]}
    pour["brep_shape"]=dict(outer_ring=ring(result.exterior),inner_rings=[ring(r) for r in result.interiors])
Path(sys.argv[2]).write_text(json.dumps(board,separators=(",",":")))
