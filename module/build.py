"""Build the module placement and DDR routing study from the pinned handheld circuit."""
import csv
import gzip
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
import pcbnew as k

here = Path(__file__).resolve().parent
root = here.parent
sys.path.insert(0, str(root / "production"))
from connectivity import trace_net_keys

with gzip.open(root / "studies/four-layer-through/board.circuit.json.gz") as stream:
    source = json.load(stream)
ids = {e.get(e["type"] + "_id"): e for e in source}
traces, keys = trace_net_keys(source)
ports = {p: keys[i] for i, t in traces.items() for p in t["connected_source_port_ids"]}
labels = {keys[i]: t["name"] for i, t in traces.items() if t.get("name")}
labels.update({e["subcircuit_connectivity_map_key"]: e["name"] for e in source
               if e["type"] == "source_net" and e.get("subcircuit_connectivity_map_key")})
balls = {(ids[p["source_component_id"]].get("name"), p["name"]): ports.get(p["source_port_id"])
         for p in source if p["type"] == "source_port" and p.get("source_component_id") in ids}
parts = {}
for c in source:
    if c["type"] != "pcb_component":
        continue
    s = ids.get(c.get("source_component_id"), {})
    ref = s.get("name", "")
    if (s.get("manufacturer_part_number") and c["pcb_component_id"].startswith("channel_")
            and ref not in {"SW_POWER", "U_JOY_ADC", "C_JOY_ADC"}):
        parts[ref] = (s, c)
for copy, original in (("R_CPU_VREF_HIGH", "R_VREF_HIGH"), ("R_CPU_VREF_LOW", "R_VREF_LOW")):
    parts[copy] = parts[original]

# Keep the memory, bypass and clock islands rigid. Compact support islands independently.
def group(ref):
    if ref.startswith("R_CPU_VREF_"): return "cpu_ref"
    if ref.startswith("R_SYSBOOT"): return "straps"
    if "PMIC" in ref or ref in {"R_POWER_PB", "R_DDR_VSEL"}: return "pmic"
    if ref in {"C_DDR_SW_LOAD", "R_DDR_SW_OUT"}: return "memory"
    if "DDR_SW" in ref or ref == "U_DDR_SWITCH": return "switch"
    return "memory"

def rectangle(ref):
    _, c = parts[ref]
    x, y = c["center"].values()
    w, h = c["width"], c["height"]
    if ref == "U1": w = h = 15
    if ref == "U_DDR": w, h = max(w, 8), max(h, 14)
    if ref in {"R_CPU_VREF_LOW", "R_CPU_VREF_HIGH"}:
        x, y = (0 if ref.endswith("LOW") else 2.2), 0
    return x-w/2, y-h/2, x+w/2, y+h/2, c["layer"]

def shift(rect, x, y):
    a,b,c,d,side = rect
    return a+x,b+y,c+x,d+y,side

def bounds(rects):
    return (min(r[0] for r in rects),min(r[1] for r in rects),
            max(r[2] for r in rects),max(r[3] for r in rects))

groups = defaultdict(list)
for ref in parts: groups[group(ref)].append(rectangle(ref))
# Connector envelope includes both rows and registration pegs.
groups["connector"] = [(-9.5,-2.1,9.5,2.1,"bottom")]
placed = list(groups["memory"])
offset = {"memory": (0,0)}
for name in ("pmic","connector","straps","switch","cpu_ref"):
    fixed = bounds(placed)
    moving = bounds(groups[name])
    best = None
    for x in range(math.floor(fixed[0]-moving[2]-3), math.ceil(fixed[2]-moving[0]+3)):
        for y in range(math.floor(fixed[1]-moving[3]-3), math.ceil(fixed[3]-moving[1]+3)):
            rects = [shift(r,x,y) for r in groups[name]]
            a,b,c,d = bounds([fixed,*rects])
            score = ((c-a+2)*(d-b+2),max(c-a,d-b),abs(x)+abs(y))
            if best and score >= best[0]: continue
            if any(r[4]==q[4] and r[0]<q[2]+.5 and q[0]<r[2]+.5 and
                   r[1]<q[3]+.5 and q[1]<r[3]+.5 for r in rects for q in placed): continue
            best = score,(x,y),rects
    assert best, name
    _,offset[name],rects=best
    placed.extend(rects)
left,low,right,high=bounds(placed)
left,low,right,high=math.floor(left-1),math.floor(low-1),math.ceil(right+1),math.ceil(high+1)
mm=k.FromMM
def xy(x,y): return k.VECTOR2I(mm(x-left),mm(high-y))
board=k.BOARD()
board.SetCopperLayerCount(6)
board.GetDesignSettings().SetBoardThickness(mm(1.6))
board.GetDesignSettings().m_MinClearance=mm(.102)
nets={}
def net(name):
    if name not in nets:
        nets[name]=k.NETINFO_ITEM(board,name)
        board.Add(nets[name])
    return nets[name]
def netname(key): return labels.get(key,key)
def zone(layer, rail=None, corners=None, priority=0):
    z=k.ZONE(board);z.SetLayer(layer);z.SetNet(net(rail or netname(balls["SW_POWER","pin1"])));z.SetLocalClearance(mm(.13))
    z.SetAssignedPriority(priority)
    z.SetMinThickness(mm(.102));z.SetPadConnection(k.ZONE_CONNECTION_FULL)
    boundary=z.Outline();boundary.NewOutline()
    points = [xy(x,y) for x,y in ((left,low),(left,high),(right,high),(right,low))] if corners is None else [at(p) for p in corners]
    for p in points:
        boundary.Append(p.x,p.y)
    board.Add(z)
for a,b in zip([(left,low),(left,high),(right,high),(right,low)],[(left,high),(right,high),(right,low),(left,low)]):
    e=k.PCB_SHAPE();e.SetShape(k.SHAPE_T_SEGMENT);e.SetLayer(k.Edge_Cuts);e.SetWidth(mm(.05));e.SetStart(xy(*a));e.SetEnd(xy(*b));board.Add(e)

pad_by_comp=defaultdict(list)
for p in source:
    if p["type"]=="pcb_smtpad": pad_by_comp[p["pcb_component_id"]].append(p)
# Underside 100 nF bypass spanning the H1 reference via and its adjacent ground via.
parts["C_H1_VREF"] = parts["C_CPU_VREF"]
h1_bypass = {"pin1": (4.800107, 36.049949), "pin2": (4.942108, 35.519994)}
# TI Table 5-13 recommends one 10 µF and five 10 nF capacitors on VDD_MPU.
parts["C_MPU_LOCAL"] = parts["C_SRAM_CORE_IN"]
for index in range(1, 6):
    donor, geometry = parts["C_DDR3"]
    parts[f"C_MPU_HF{index}"] = (
        dict(donor, manufacturer_part_number="CL05B103KB5NNNC",
             supplier_part_numbers={"jlcpcb": ["C15195"]}), geometry)
local_bypasses = json.loads((here/"local-bypass-placements.json").read_text())
for ref,(s,c) in parts.items():
    dx,dy=offset[group(ref)]
    cx,cy=c["center"]["x"],c["center"]["y"]
    if ref == "C_CPU_VREF":
        dx += 0.085
        dy -= 0.145
    if ref == "R_PMIC_POR":
        # Put the reset pull on the existing sequenced IO feed outside the DDR region.
        dx += 4.5543119
        dy += 4.8198588
    if ref == "L_PMIC_IO":
        dx += .95
        dy -= .15
    if ref == "R_VREF_LOW":
        dx += 1.37
        dy -= 6.06
    if ref == "C_DDR34":
        # Reserve R7 and R8 for address escapes. Give the bulk capacitor dedicated feed vias.
        dx += 2.70
        dy -= 2.34
    if ref == "C_DDR6":
        # Align the underside bypass supply pad to the DRAM N1 through via.
        dx -= .720008
        dy += .150058
    if group(ref)=="cpu_ref":
        dx+=(0 if ref.endswith("LOW") else 2.2)-cx
        dy-=cy
    fp=k.FOOTPRINT(board);fp.SetReference(ref);fp.SetValue(s["manufacturer_part_number"])
    bot=c["layer"]=="bottom" or ref=="C_DDR12" or ref.startswith("C_MPU_")
    fp.SetLayer(k.B_Cu if bot else k.F_Cu);fp.SetPosition(xy(cx+dx,cy+dy))
    if ref in local_bypasses:
        site = local_bypasses[ref]
        center = [(a+b)/2 for a,b in zip(site["pin1"], site["pin2"])]
        fp.SetPosition(k.VECTOR2I(mm(center[0]), mm(center[1])))
    if ref == "R_ZQ":
        fp.SetPosition(k.VECTOR2I(mm(10.825285),mm(38.956776)))
    if ref == "C_DDR12":
        fp.SetPosition(k.VECTOR2I(mm(3.412306),mm(37.691513)))
    if ref == "C_H1_VREF":
        mid = [(a+b)/2 for a,b in zip(*h1_bypass.values())]
        fp.SetPosition(k.VECTOR2I(mm(mid[0]), mm(mid[1])))
    fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
    for p in pad_by_comp[c["pcb_component_id"]]:
        pp=ids.get(p.get("pcb_port_id"),{})
        sp=ids.get(pp.get("source_port_id"),{})
        pname=sp.get("name",p.get("port_hints",[""])[0])
        pad=k.PAD(fp);pad.SetNumber(pname);pad.SetAttribute(k.PAD_ATTRIB_SMD)
        layers=k.LSET()
        for layer in ((k.B_Cu,k.B_Mask,k.B_Paste) if bot else (k.F_Cu,k.F_Mask,k.F_Paste)):layers.AddLayer(layer)
        pad.SetLayerSet(layers)
        shape=p["shape"];w=p.get("width",2*p.get("radius",0));h=p.get("height",w)
        pad.SetShape({"rect":k.PAD_SHAPE_RECT,"rotated_rect":k.PAD_SHAPE_RECT,"pill":k.PAD_SHAPE_OVAL,"circle":k.PAD_SHAPE_CIRCLE}[shape])
        pad.SetSize(k.VECTOR2I(mm(w),mm(h)));pad.SetPosition(xy(p["x"]+dx,p["y"]+dy))
        pad.SetOrientationDegrees(p.get("rect_ccw_rotation",p.get("ccw_rotation",0)))
        key=ports.get(sp.get("source_port_id"))
        name=netname(key)
        if (ref,pname) in {("U1","J4"),("C_CPU_VREF","pin1")} or (group(ref)=="cpu_ref" and pname=="pin1"):name="CPU_DDR_VREF"
        if ref=="R_CPU_VREF_HIGH" and pname=="pin2":name=netname(balls["U_DDR_SWITCH","VOUT1"])
        if (ref,pname)==("U1","P15"):name="USB0_VBUS_SENSE"
        if ref == "R_ZQ":
            positions = {"pin1": (10.670017,38.771735), "pin2": (10.980553,39.141817)}
            x,y = positions[pname]
            pad.SetPosition(k.VECTOR2I(mm(x),mm(y)))
            pad.SetOrientationDegrees(-50)
        if ref == "C_DDR12":
            positions = {"pin1": (3.519901, 38.097617), "pin2": (3.304710, 37.285409)}
            x,y = positions[pname]
            pad.SetPosition(k.VECTOR2I(mm(x),mm(y)))
            pad.SetOrientationDegrees(194.839306)
        if ref.startswith("C_MPU_"):
            name = "VDD_MPU" if pname == "pin1" else "GND_INTERNAL"
        if ref in local_bypasses:
            x,y = local_bypasses[ref][pname]
            pad.SetPosition(k.VECTOR2I(mm(x),mm(y)))
            pad.SetOrientationDegrees(local_bypasses[ref]["rotation"])
        if ref == "C_H1_VREF":
            x,y = h1_bypass[pname]
            pad.SetPosition(k.VECTOR2I(mm(x),mm(y)))
            pad.SetOrientationDegrees(-15)
            name = "DDR_VREF" if pname == "pin1" else "GND_INTERNAL"
        if name:pad.SetNet(net(name))
        fp.Add(pad)
    board.Add(fp)

# The module mezzanine carries host I/O only. DDR and its references terminate locally.
with (root/"production/interface.csv").open() as f:
    interface=[(r["Signal"],balls["U1",r["Ball"]],f'U1.{r["Ball"]}') for r in csv.DictReader(f)]
extra=[("UART_RX","U1","E15"),("UART_TX","U1","E16"),("POWER_KEY","U_PMIC","PB")]
interface.extend((s,balls[r,p],r+"."+p) for s,r,p in extra)
gnd=("GND",balls["SW_POWER","pin1"],"U_PMIC.EP")
vsys=("VSYS",balls["U_PMIC","IN_DCDC1"],"U_PMIC.IN_DCDC1")
io=("3V3_SEQ",balls["U_PMIC","DCDC4"],"U_PMIC.DCDC4")
assert len({key for _,key,_ in interface})==len(interface) and all(k for _,k,_ in interface)
pins=[]
for signal in interface:
    if signal[0] in {"SD_CLK","USB0_DP","LCD_PCLK","TOUCH_SDA"}:pins.append(gnd)
    pins.append(signal)
    if signal[0] in {"SD_DAT3","USB0_DM","LCD_DE"}:pins.append(gnd)
pins.extend([vsys,gnd,vsys,io,gnd,vsys,io,gnd,vsys,io,gnd,vsys])
assert len(pins)<=80,len(pins)
assert len(pins)==79
pins.append(("USB0_VBUS_SENSE","USB0_VBUS_SENSE","U1.P15"))
# Manufacturer land pattern in the plug-side view. Pin 1 is at the
# left end of the lower row. Flip the complete footprint for backside assembly.
fp=k.FOOTPRINT(board);fp.SetReference("J_CARRIER");fp.SetValue("DF40C-80DP-0.4V(51)")
fp.SetPosition(xy(*offset["connector"]))
for i,(_,key,_) in enumerate(pins,1):
    col=i-1 if i<=40 else 80-i
    px=(col-19.5)*.4
    py=1.355 if i<=40 else -1.355
    pad=k.PAD(fp);pad.SetNumber(str(i));pad.SetAttribute(k.PAD_ATTRIB_SMD)
    pad.SetShape(k.PAD_SHAPE_RECT);pad.SetSize(k.VECTOR2I(mm(.20),mm(1.0)))
    copper=k.LSET()
    for layer in (k.F_Cu,k.F_Mask,k.F_Paste): copper.AddLayer(layer)
    pad.SetLayerSet(copper);pad.SetPosition(fp.GetPosition()+k.VECTOR2I(mm(px),mm(py)))
    pad.SetNet(net(netname(key)));fp.Add(pad)
board.Add(fp);fp.Flip(fp.GetPosition(),k.FLIP_DIRECTION_TOP_BOTTOM)
def write_csv(name,header,rows):
    with (here/name).open("w") as stream:
        writer=csv.writer(stream,lineterminator="\n");writer.writerow(header);writer.writerows(rows)
write_csv("carrier-pinout.csv",["contact","signal","module_net","module_terminal"],[(i,s,netname(key),t) for i,(s,key,t) in enumerate(pins,1)])
write_csv("module-bom.csv",["reference","MPN","JLCPCB"],[(r,s["manufacturer_part_number"],",".join(s.get("supplier_part_numbers",{}).get("jlcpcb",[]))) for r,(s,c) in parts.items()]+[("J_CARRIER","DF40C-80DP-0.4V(51)","C294544")])

route_vias={(round(v["x"],6),round(v["y"],6)):v for v in source if v["type"]=="pcb_via"}
routed=[]
for t in source:
    if t["type"]!="pcb_trace":continue
    st=traces[t["source_trace_id"]];name=st.get("name") or ""
    if not name.startswith("DDR_"):continue
    r=t["route"]
    if any(p.get("layer",p.get("to_layer")) not in ("top","bottom") for p in r):continue
    n=net(netname(keys[t["source_trace_id"]]))
    for p,q in zip(r,r[1:]):
        a,b=xy(p["x"],p["y"]),xy(q["x"],q["y"])
        if a==b:continue
        w=k.PCB_TRACK(board);w.SetStart(a);w.SetEnd(b);w.SetNet(n)
        w.SetWidth(mm(p.get("width",q.get("width",.102))));w.SetLayer(k.F_Cu if p.get("layer",p.get("to_layer"))=="top" else k.B_Cu);board.Add(w)
    for p in r:
        if p["route_type"]!="via":continue
        v=route_vias[round(p["x"],6),round(p["y"],6)];via=k.PCB_VIA(board)
        via.SetPosition(xy(p["x"],p["y"]));via.SetFrontWidth(mm(v["outer_diameter"]));via.SetDrill(mm(v["hole_diameter"]));via.SetNet(n);board.Add(via)
    routed.append(name)
# Saved module coordinates use KiCad's Y-down frame.
def at(p):
    return k.VECTOR2I(mm(p[0]),mm(p[1]))
def add_segment(a,b,layer,n,width):
    if at(a)==at(b):return
    t=k.PCB_TRACK(board);t.SetStart(at(a));t.SetEnd(at(b));t.SetLayer(layer)
    t.SetWidth(mm(width));t.SetNet(n);board.Add(t)
def add_barrel(v,n):
    t=k.PCB_VIA(board);t.SetPosition(at(v));t.SetFrontWidth(mm(v[3]));t.SetDrill(mm(v[2]));t.SetNet(n);board.Add(t)
for path in json.loads((here/"command-routes.json").read_text()):
    n=net(path["net"])
    leads = path.get("leads") or [[endpoint, via[:2]] for endpoint, via in zip(path["ends"], path["vias"])]
    for lead, via in zip(leads, path["vias"]):
        for start, end in zip(lead, lead[1:]):
            add_segment(start, end, k.F_Cu, n, .102)
        add_barrel(via, n)
    if "sections" in path:
        for via in path.get("extra_vias", [path.get("middle")]):
            add_barrel(via, n)
        sections = path["sections"]
    else:
        sections = [{"layer": path["inner"], "points": path["path"]}]
    for section in sections:
        layer = {"F.Cu": k.F_Cu, "In2.Cu": k.In2_Cu, "In3.Cu": k.In3_Cu, "B.Cu": k.B_Cu}[section["layer"]]
        for start, end in zip(section["points"], section["points"][1:]):
            add_segment(start, end, layer, n, .102)
    routed.append(path["net"])
for adjustment in json.loads((here/"via-adjustments.json").read_text()):
    old=at(adjustment["old"]);new=at(adjustment["new"])
    hits=0
    for item in board.GetTracks():
        if item.GetNetname()!=adjustment["net"]:continue
        if isinstance(item,k.PCB_VIA):
            if (item.GetPosition()-old).EuclideanNorm()>3:continue
            item.SetPosition(new);item.SetFrontWidth(mm(adjustment["diam"]))
            item.SetDrill(mm(adjustment["drill"]));hits+=1
        else:
            if (item.GetStart()-old).EuclideanNorm()<=3:item.SetStart(new)
            if (item.GetEnd()-old).EuclideanNorm()<=3:item.SetEnd(new)
    assert hits==1,adjustment
for edit in json.loads((here/"escape-edits.json").read_text()):
    layer = {"F.Cu":k.F_Cu, "B.Cu":k.B_Cu, "In2.Cu":k.In2_Cu, "In3.Cu":k.In3_Cu}[edit["layer"]]
    tracks = [t for t in board.GetTracks() if not isinstance(t,k.PCB_VIA)
              and t.GetLayer()==layer and t.GetNetname()==edit["net"]]
    for start, end in zip(edit["old"],edit["old"][1:]):
        def near(x, y):
            return (x-at(y)).EuclideanNorm() <= 3
        track, = [t for t in tracks if
                  (near(t.GetStart(),start) and near(t.GetEnd(),end)) or
                  (near(t.GetEnd(),start) and near(t.GetStart(),end))]
        tracks.remove(track)
        board.Remove(track)
    if "destination_layer" in edit:
        layer = {"F.Cu":k.F_Cu, "B.Cu":k.B_Cu, "In2.Cu":k.In2_Cu, "In3.Cu":k.In3_Cu}[edit["destination_layer"]]
    replacement = edit.get("new", edit["old"])
    for start,end in zip(replacement,replacement[1:]):
        add_segment(start,end,layer,net(edit["net"]),.102)
# Both launch traces have already been rebuilt to the center of U1.D1.
# Move only the matching plated barrel after replacing the two track ends.
clock_pad = next(p for p in board.GetPads() if p.GetParentFootprint().GetReference() == "U1" and p.GetNumber() == "D1")
clock_barrel, = [v for v in board.GetTracks() if isinstance(v, k.PCB_VIA)
                 and v.GetNetname() == clock_pad.GetNetname()
                 and (v.GetPosition() - at([21.262094, 28.387825])).EuclideanNorm() <= 3]
clock_barrel.SetPosition(clock_pad.GetPosition())
for feed in json.loads((here/"local-vias.json").read_text()):
    add_barrel([*feed["pos"], feed["drill"], feed["diam"]], net(feed["net"]))
for branch in json.loads((here/"carrier-strap-routes.json").read_text()):
    signal = net(branch["net"])
    for section in branch["sections"]:
        layer = {"F.Cu":k.F_Cu,"B.Cu":k.B_Cu,"In2.Cu":k.In2_Cu,"In3.Cu":k.In3_Cu}[section["layer"]]
        for a, b in zip(section["points"], section["points"][1:]):
            add_segment(a, b, layer, signal, section.get("width", .14))
    for x, y in branch["vias"]:
        add_barrel([x, y, branch["drill"], branch["diam"]], signal)
for path in json.loads((here/"ground-escapes.json").read_text()):
    n=net(netname(balls["SW_POWER","pin1"]))
    add_segment(path["start"],path["end"],k.F_Cu if path["layer"]=="F.Cu" else k.B_Cu,n,path.get("width", .20))
    add_barrel([*path["end"],path.get("drill", .20),path.get("diam", .45)],n)
for link in json.loads((here/"local-links.json").read_text()):
    for a,b in zip(link["points"],link["points"][1:]):
        add_segment(a,b,{"F.Cu":k.F_Cu,"B.Cu":k.B_Cu,"In2.Cu":k.In2_Cu,"In3.Cu":k.In3_Cu}[link["layer"]],net(link["net"]),link["width"])
for name, file in (("VDDS_DDR","ddr-plane-feeds.json"), ("VDDS_DDR_CPU","cpu-ddr-plane-feeds.json")):
    rail = net(name)
    for feed in json.loads((here/file).read_text()):
        layer = k.F_Cu if feed["layer"] == "F.Cu" else k.B_Cu
        points = feed.get("points", [feed["start"], feed["end"]])
        for start, end in zip(points, points[1:]):
            add_segment(start, end, layer, rail, feed.get("width", .32))
        add_barrel([*feed["end"], feed.get("drill", .20), feed.get("diam", .45)], rail)
# A wide trunk carries the post-inductor DCDC3 output to the DDR area.
zone(k.In2_Cu, "VDDS_DDR", [(6,3),(22,3),(22,18),(36.6,18),(36.6,45.6),(.4,45.6),(.4,18),(6,18)])
zone(k.In3_Cu, "VDDS_DDR_CPU", [(13,3.5),(19,3.5),(26.0,20.8),(36.5,20.8),(36.5,45.6),(19.5,45.6),(19.5,22.2),(13,9)])
zone(k.In3_Cu, "VDD_MPU", json.loads((here/"mpu-plane.json").read_text()), priority=1)
for layer in (k.In1_Cu,k.In4_Cu):zone(layer)

board_path=here/"pixel-dash-module.kicad_pcb"
k.SaveBoard(str(board_path), board)
# Foil and pressed dielectric thicknesses from JLC06161H-1080, in mm.
foils=(.035,.0152,.0152,.0152,.0152,.035)
dielectrics=(.0764,.55,.2104,.55,.0764)
stack=[]
for i,foil in enumerate(foils):
    label=("F.Cu","In1.Cu","In2.Cu","In3.Cu","In4.Cu","B.Cu")[i]
    stack.append(f'(layer "{label}" (type "copper") (thickness {foil}))')
    if i<len(dielectrics):
        kind="core" if i in (1,3) else "prepreg"
        stack.append(f'(layer "dielectric {i+1}" (type "{kind}") (thickness {dielectrics[i]}) (material "FR4"))')
board_path.write_text(board_path.read_text().replace("(setup\n", "(setup\n\t\t(stackup "+"\n".join(stack)+")\n",1))
print(right-left,high-low,len(parts)+1,len(routed),sorted(routed))
project=here/"pixel-dash-module.kicad_pro"
settings=json.loads(project.read_text())
settings["board"]["design_settings"]["rules"].update(
    min_clearance=.102,min_track_width=.102,min_via_annular_width=.075,
    min_via_diameter=.30,min_through_hole_diameter=.15,min_hole_clearance=.20,min_hole_to_hole=.25)
settings["net_settings"]["classes"][0].update(clearance=.102,track_width=.15,via_diameter=.45,via_drill=.2)
project.write_text(json.dumps(settings,indent=2)+"\n")

# Start a fresh KiCad session so the filler reads the actual project rules.
import subprocess
subprocess.run([sys.executable,str(here/"fill-planes.py"),str(board_path)],check=True)
