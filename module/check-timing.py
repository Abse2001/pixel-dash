"""Report per-signal geometry, layer-specific nominal flight and project matching gates."""
import collections
import csv
import json
import math
import re
import sys
from shapely.geometry import LineString
from shapely import union_all
from pathlib import Path
objs=json.loads(Path(sys.argv[1]).read_text())
data=collections.defaultdict(dict);pads=collections.defaultdict(list)
for o in objs:
    if o.get("ref") in ("U1","U_DDR"):pads[o["net"]].append(o["pos"])
for name,ends in pads.items():
    if not re.fullmatch(r'DDR_(?:A\d+|BA\d+|D\d+|DQ\w+|CKn?|CKE|CASn|RASn|WEn|CSn0|RESETn|ODT)',name):continue
    tracks=[o for o in objs if o["kind"]=="track" and o["net"]==name]
    layers=collections.defaultdict(list)
    for o in tracks:layers[o["layer"]].append(LineString([o["start"],o["end"]]))
    # Copper center depths from JLC06161H-1080.
    depth=[0,.0175+.0764+.0076]
    for d in (.55,.2104,.55):depth.append(depth[-1]+.0152+d)
    depth.append(depth[-1]+.0076+.0764+.0175)
    z=dict(zip(("F.Cu","In1.Cu","In2.Cu","In3.Cu","In4.Cu","B.Cu"),depth))
    spans=[];barrel=0
    for v in (o for o in objs if o["kind"]=="via" and o["net"]==name):
        sides={t["layer"] for t in tracks if any(math.dist(t[k],v["pos"])<.000005 for k in ("start","end"))}
        if any(math.dist(p,v["pos"])<.000005 for p in ends):sides.add("F.Cu")
        assert len(sides)==2,(name,v,sides)
        a,b=sorted(sides,key=z.get);spans.append(a+"/"+b);barrel+=z[b]-z[a]
    length=sum(g.length for a in layers.values() for g in a)
    inner=sum(g.length for l,gs in layers.items() if l.startswith("In") for g in gs)
    data[name]=dict(layers=layers,len=length,barrel=barrel,spans=spans,
                    nominal=(length-inner)*5.884+inner*6.671+barrel*6.600,
                    manhattan=sum(abs(x-y) for x,y in zip(*ends)),inner=inner)
assert len(data)==50
for n,r in data.items():
    mate=None
    for a,b in (("DDR_CK","DDR_CKn"),("DDR_DQS0","DDR_DQSn0"),("DDR_DQS1","DDR_DQSn1")):
        if n in (a,b):mate=b if n==a else a
    near=0
    if mate:
        for l,gs in r["layers"].items():
            env=union_all(data[mate]["layers"].get(l,[])).buffer(.42,quad_segs=48)
            near+=sum(g.intersection(env).length for g in gs)
    t=r["nominal"];r["times"]=(t,t-near*(5.884-5.739),t-r["len"]*(5.884-5.739) if mate else t)
out=csv.writer(sys.stdout,lineterminator="\n")
out.writerow(("net","length_mm","via_contacts","traversed_barrel_mm","inner_mm","flight_ps","signed_skew_ps","length_target_mm","length_excess_mm","TI_peer_or_pair_mismatch_mm","TI_limit_mm","model_limit_ps","model_excess_ps","screen"))
def row(n,skew,lo,hi,mismatch=None,mm=None,ps=None):
    r=data[n];length=r["len"]
    if not length:out.writerow([n]+[""]*12+["OPEN"]);return
    excess=max(0,lo-length,length-hi) if lo is not None else None
    err=max(0,abs(skew)-ps) if ps else None
    status="FAIL" if (excess or 0)>1e-6 or (mm and mismatch>mm+1e-6) or (err or 0)>1e-6 else "PASS"
    vals=(n,length,";".join(r["spans"]),r["barrel"],r["inner"],r["times"][1],skew,
          f"{lo:.4f}..{hi:.4f}" if lo is not None else "",excess,mismatch,mm,ps,err,status)
    out.writerow(round(v,5) if isinstance(v,float) else v for v in vals)
excluded=set()
for lane in range(2):
    ds=[f"DDR_D{i}" for i in range(8*lane,8*lane+8)]+[f"DDR_DQM{lane}"]
    pair=[f"DDR_DQS{lane}",f"DDR_DQSn{lane}"];hi=max(data[n]["manhattan"] for n in ds+pair)
    for n in ds+pair:
        isdata=n in ds;ref=[m for m in pair if m!=n]
        skew=max((a-b for m in ref for a,b in zip(data[n]["times"],data[m]["times"])),key=abs)
        mismatch=max(abs(data[n]["len"]-data[m]["len"]) for m in (ds+pair if isdata else ref))
        row(n,skew,0.,hi,mismatch,.635 if isdata else .127,3.663315 if isdata else .713359)
        excluded.add(n)
cmd=set(data)-excluded-{"DDR_RESETn"};mid=max(data[n]["manhattan"] for n in cmd)+7.62
clock=sum(data[m]["times"][1] for m in ("DDR_CK","DDR_CKn"))/2
for n in sorted(cmd):
    if n in ("DDR_CK","DDR_CKn"):
        mate="DDR_CK" if n=="DDR_CKn" else "DDR_CKn"
        skew=data[n]["times"][1]-data[mate]["times"][1]
        row(n,skew,mid-1.27,mid+1.27,abs(data[n]["len"]-data[mate]["len"]),.127,.713359)
    else:row(n,data[n]["times"][1]-clock,mid-1.27,mid+1.27)
row("DDR_RESETn",None,None,None)
