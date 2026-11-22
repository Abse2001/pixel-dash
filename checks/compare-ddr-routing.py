"""Compare two routed interfaces against TI layout limits and the board delay model."""
import argparse
import csv
import json
import runpy
import sys
from pathlib import Path

audit = runpy.run_path(str(Path(__file__).with_name("audit-ddr-flight.py")))
single, odd, barrel = [audit[key] for key in ("SINGLE", "ODD", "BARREL")]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("before", type=Path)
parser.add_argument("after", type=Path)
args = parser.parse_args()
before, board = (json.loads(path.read_text()) for path in (args.before, args.after))
prior, now = (audit["flights"](b, .42) for b in (before, board))
names = set(now)
assert names == set(prior)
ports = {e["source_port_id"]: e for e in board if e["type"] == "pcb_port" and e.get("source_port_id")}
manhattan = {}
for trace in board:
    if trace["type"] == "source_trace" and trace.get("name") in names:
        a, b = [ports[k] for k in trace["connected_source_port_ids"]]
        manhattan[trace["name"]] = abs(a["x"]-b["x"]) + abs(a["y"]-b["y"])

def worst(values):
    return max(values, key=abs)

def residual(value, low, high):
    return max(0, low-value, value-high)

def cases(row):
    length, _, _, _, isolated, mixed = row
    return {"isolated": isolated, "mixed": mixed, "odd": isolated-length*(single-odd)}

writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(["signal","prior_length_mm","current_length_mm","prior_vias","current_vias","prior_barrel_mm",
                 "current_barrel_mm","prior_mixed_flight_ps","current_mixed_flight_ps","TI_nominal_min_mm",
                 "TI_nominal_max_mm","TI_nominal_excess_mm","geometry_plus_barrels_nominal_excess_mm_provisional",
                 "TI_max_abs_DQ_peer_delta_mm","TI_DQ_peer_limit_mm","TI_DQ_peer_excess_mm","TI_max_abs_strobe_or_pair_delta_mm",
                 "TI_strobe_or_pair_limit_mm","TI_strobe_or_pair_excess_mm","reference","prior_signed_mixed_skew_ps",
                 "current_signed_mixed_skew_ps","prior_signed_worst_scenario_ps","current_signed_worst_scenario_ps",
                 "prior_worst_scenario","current_worst_scenario","model_abs_skew_limit_ps","model_skew_excess_ps","model_flight_min_ps",
                 "model_flight_max_ps","model_flight_window_excess_ps","joint_length_min_current_span_mm",
                 "joint_length_max_current_span_mm","current_span_window_feasible","joint_length_min_2_full_vias_mm",
                 "joint_length_max_2_full_vias_mm","two_full_vias_window_feasible"])
lanes = []
for i in (0,1):
    data = [f"DDR_D{j}" for j in range(8*i, 8*i+8)] + [f"DDR_DQM{i}"]
    lanes.append((data,[f"DDR_DQS{i}",f"DDR_DQSn{i}"]))
controls = names - {n for data, pair in lanes for n in data+pair} - {"DDR_RESETn"}
clock = ["DDR_CK","DDR_CKn"]
for name, current in sorted(now.items()):
    old = prior[name]
    row = [name,old[0],current[0],old[1],current[1],old[2],current[2],old[5],current[5]]
    if name == "DDR_RESETn":
        writer.writerow([*row,*([""]*28)])
        continue
    lane = next(((data,pair) for data,pair in lanes if name in data+pair),None)
    if lane:
        data,pair = lane
        lo,hi = 0.,max(manhattan[n] for n in data+pair)
    else:
        center = max(manhattan[n] for n in controls) + 7.62
        lo,hi = center-1.27,center+1.27
        data,pair = [],clock
    row.extend([lo,hi,residual(current[0],lo,hi),residual(current[0]+current[2],lo,hi)])
    if name in data:
        spread = max(abs(current[0]-now[n][0]) for n in data)
        row.extend([spread,.635,max(0,spread-.635)])
    else:
        row.extend([""]*3)
    if name in data or name in pair:
        peers = [n for n in pair if n!=name]
        mm = .635 if name in data else .127
        delta = max(abs(current[0]-now[n][0]) for n in peers)
        row.extend([delta, mm, max(0,delta-mm),"/".join(peers)])
        def skew(source):
            diff = [(cases(source[name])[mode]-cases(source[n])[mode],mode,n)
                    for mode in ("isolated","mixed","odd") for n in peers]
            # An unpaired DQ always uses the isolated rate, including in the odd-strobe case.
            if name in data:
                diff = [(source[name][4]-cases(source[n])[mode],mode,n)
                        for mode in ("isolated","mixed","odd") for n in peers]
            signed,mode,n = max(diff,key=lambda x: abs(x[0]))
            mixed = worst([v for v,m,_ in diff if m=="mixed"])
            return mixed,signed,mode+"/"+n
        om,ow,prior_scenario = skew(prior)
        cm,cw,scenario = skew(now)
        limit = mm*(single if name in data else odd)
        lower = max(now[n][5] for n in peers)-limit
        upper = min(now[n][5] for n in peers)+limit
        row.extend([om,cm,ow,cw,prior_scenario,scenario,limit,max(0,abs(cw)-limit),lower,upper,residual(current[5],lower,upper)])
    else:
        def relative(source):
            return source[name][5]-sum(source[n][5] for n in clock)/2
        lower,upper = [x*single+current[2]*barrel for x in (lo,hi)]
        row.extend(["","","","CK pair mean",relative(prior),relative(now),"","","","","","",
                    lower,upper,residual(current[4],lower,upper)])
    if name in data:
        peer_times = [t for n in pair for t in cases(now[n]).values()]
        # Each bound must satisfy both strobe legs, every delay scenario, and TI geometry.
        # Data-to-data matching remains an additional group constraint.
        for span_mm in (current[2], 2*audit["WURTH"].outer_to_outer):
            minimum = max(lo, max(now[n][0] for n in pair)-.635,
                          (max(peer_times)-.635*single-span_mm*barrel)/single)
            maximum = min(hi, min(now[n][0] for n in pair)+.635,
                          (min(peer_times)+.635*single-span_mm*barrel)/single)
            row.extend([minimum,maximum,"yes" if minimum<=maximum else "no"])
    else:
        row.extend([""]*6)
    assert len(row)==37
    writer.writerow([f"{x:.4f}" if isinstance(x,float) else x for x in row])
