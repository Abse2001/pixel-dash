"""Write the per-net timing ledger for the complete native AM3354 DDR channel."""
import argparse
import itertools
import json
import runpy
from pathlib import Path

flight = runpy.run_path(str(Path(__file__).with_name("audit-ddr-flight.py")))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("circuit", type=Path)
args = parser.parse_args()
board = json.loads(args.circuit.read_text())
rows = flight["flights"](board, .42)
ports = {p["source_port_id"]: p for p in board if p["type"] == "pcb_port" and p.get("source_port_id")}
spans = {}
for s in board:
    if s["type"] == "source_trace" and s.get("name") in rows:
        a, b = (ports[i] for i in s["connected_source_port_ids"])
        spans[s["name"]] = abs(a["x"]-b["x"]) + abs(a["y"]-b["y"])
single, odd, barrel = (flight[k] for k in ("SINGLE", "ODD", "BARREL"))
skew = .635
delay_limit = single * skew
byte_nets = set()
def label(n):
    return n.removeprefix("DDR_")
def header(*cols):
    print("| " + " | ".join(cols) + " |")
    print("|" + "|".join(["---"]*len(cols)) + "|")
def line(*cells):
    print("| " + " | ".join(map(str, cells)) + " |")
def delays(n):
    xy, _, _, _, iso, mixed = rows[n]
    return iso, mixed, iso-xy*(single-odd)

print("# AM3354 DDR3L routing and board-flight targets\n")
print("Lengths are in mm and flight times in ps. The nominal length and skew screens use TI SPRS717L Tables 7-68 and 7-69. "
      "The separate delay estimate uses the 1.491 mm reference build, 5.769 ps/mm isolated, 5.617 ps/mm odd mode and 6.600 ps/mm of traversed barrel. "
      "A full L1–L4 passage adds 1.420 mm and 9.372 ps. Mixed mode estimates same-layer pair proximity within 0.42 mm. "
      "The 3.663 ps data-skew screen converts 0.635 mm at the isolated rate. TI specifies a length limit. "
      "Package delay, actual fabrication tolerances, impedance discontinuities, controller setup/hold and memory training remain outside this estimate.\n")
for i in range(2):
    dq = [f"DDR_D{k}" for k in range(i*8,i*8+8)] + [f"DDR_DQM{i}"]
    strobes = [f"DDR_DQS{i}", f"DDR_DQSn{i}"]
    byte_nets.update(dq + strobes)
    maximum = max(spans[n] for n in dq + strobes)
    print(f"## Byte {i}\n")
    print(f"Nominal planar length ≤ {maximum:.3f} mm. Data-to-data and data-to-either-strobe mismatch ≤ 0.635 mm each. "
          "Strobe positive-to-negative mismatch ≤ 0.127 mm. Each modeled delta below is the worst absolute difference to either strobe leg. "
          "The model screen checks isolated, mixed and uniform odd-mode strobe cases.\n")
    ref_times = [rows[n][5] for n in strobes]
    tol_lo = max(ref_times)-delay_limit
    tol_hi = min(ref_times)+delay_limit
    print(f"With the present mixed-mode strobe times, the common data-flight target is "
          f"{tol_lo:.3f}–{tol_hi:.3f} ps to satisfy both strobe legs. "
          "The other delay scenarios are evaluated against their own strobe times.\n")
    header("Signal","Planar / max mm","Via count","Mixed flight ps","Worst planar Δ to DQS mm","Mixed Δ ps","Worst modeled Δ ps / 3.663","Failed screens")
    for n in dq:
        length, count, _, _, iso, mixed = rows[n]
        pd = max(abs(length-rows[q][0]) for q in strobes)
        peer = [label(q) for q in dq if abs(length-rows[q][0])>skew]
        md = max(abs(mixed-rows[q][5]) for q in strobes)
        worst = max(abs(iso-t) for q in strobes for t in delays(q))
        fails = []
        if length>maximum:fails.append("nominal")
        if pd>skew:fails.append("strobe length")
        if worst>delay_limit:fails.append("modeled skew")
        if peer:fails.append("data length vs " + ", ".join(peer))
        line(label(n),f"{length:.3f} / {maximum:.3f}",count,f"{mixed:.3f}",f"{pd:.3f}",f"{md:.3f}",f"{worst:.3f}", "; ".join(fails) or "pass")
    print()
    a,b=strobes
    for n in strobes:
        print(f"- {label(n)} measures {rows[n][0]:.3f} mm with {rows[n][1]} vias and {rows[n][5]:.3f} ps of mixed-mode flight.")
    print(f"- Strobe pair mismatch is {abs(rows[a][0]-rows[b][0]):.3f} mm against 0.127 mm. Mixed flight difference is {abs(rows[a][5]-rows[b][5]):.3f} ps.")
    low = min(dq, key=lambda n: rows[n][5])
    high = max(dq, key=lambda n: rows[n][5])
    print(f"- Data-to-data board flight spread is {rows[high][5]-rows[low][5]:.3f} ps ({label(high)}, {label(low)}) against the {delay_limit:.3f} ps model screen.")
    for desc,pairs in (("Data-to-data",list(itertools.combinations(dq,2))),("Data-to-strobe",list(itertools.product(dq,strobes)))):
        for barrels in (False,True):
            def length(n):
                return rows[n][0] + (rows[n][2] if barrels else 0.)
            delta,a,b=max((abs(length(a)-length(b)),a,b) for a,b in pairs)
            print(f"- {desc} {'including barrel depth' if barrels else 'planar'} mismatch is {delta:.3f} mm ({label(a)}, {label(b)}) against 0.635 mm.")
    print()
control = sorted(set(rows)-byte_nets-{"DDR_RESETn"})
nom = max(spans[n] for n in control)+7.62
lo,hi=nom-1.27,nom+1.27
print("## Address, control and clock\n")
print(f"The longest Manhattan distance plus 7.620 mm gives CACLM = {nom:.3f} mm. Target range is {lo:.3f}–{hi:.3f} mm. "
      "Each isolated-flight target below converts the length window at that net’s actual via depth. "
      "The signed mixed-mode difference uses the mean of CK and CKn. The data-byte 3.663 ps screen does not apply to this group.\n")
header("Net","Planar mm","Via count","Isolated flight ps","Isolated target ps","Mixed Δ to CK mean ps","Nominal length result")
mean=sum(rows[n][5] for n in ("DDR_CK","DDR_CKn"))/2
for n in control:
    length,count,depth,_,iso,mixed=rows[n]
    corr=lo-length if length<lo else hi-length if length>hi else 0.
    line(label(n),f"{length:.3f}",count,f"{iso:.3f}",f"{lo*single+depth*barrel:.3f}–{hi*single+depth*barrel:.3f}",f"{mixed-mean:+.3f}",f"{corr:+.3f} mm needed" if corr else "pass")
a,b=(rows[n] for n in ("DDR_CK","DDR_CKn"))
print(f"\nCK pair mismatch is {abs(a[0]-b[0]):.3f} mm against 0.127 mm. Its mixed flight difference is {abs(a[5]-b[5]):.3f} ps.\n")
r=rows["DDR_RESETn"]
print(f"RESETn measures {r[0]:.3f} mm with {r[1]} vias and {r[5]:.3f} ps of modeled flight. It is assessed with reset sequencing.\n")
print("[TI AM335x datasheet](https://www.ti.com/lit/ds/symlink/am3354.pdf) · [Barrel-inclusive nominal-window sensitivity](current-timing.txt)")
