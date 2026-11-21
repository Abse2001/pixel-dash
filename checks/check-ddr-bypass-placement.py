"""Check the high-speed capacitor population and distances in TI's AM335x DDR3 bypass table."""
import json
import math
import sys
from pathlib import Path

board = json.loads(Path(sys.argv[1]).read_text())
parts = {e["name"]: e for e in board if e["type"] == "source_component"}
placed = {e["source_component_id"]: e for e in board if e["type"] == "pcb_component"}
ports = {e["source_port_id"]: e for e in board if e["type"] == "pcb_port" and e.get("source_port_id")}
ddr = Path(__file__).resolve().parents[1] / "am3354"
assignments = json.loads((ddr / "bypass-placement.json").read_text())
configs = [
    ("U1", "processor-balls.json", {"VDDS_DDR"}, {"VSS"}, 20, 1.0e-6, 10.16),
    ("U_DDR", "memory-balls.json", {"VDD", "VDDQ"}, {"VSS", "VSSQ"}, 12, 0.85e-6, 3.81),
]
for ref, ball_file, rails, grounds, min_count, min_farads, limit in configs:
    balls = json.loads((ddr / ball_file).read_text())
    chip_id = parts[ref]["source_component_id"]
    terminals = [(balls[e["name"]], ports[e["source_port_id"]]) for e in board
                 if e["type"] == "source_port" and e["source_component_id"] == chip_id]
    locations = [[(p["x"], p["y"]) for label, p in terminals if label in signals] for signals in (rails, grounds)]
    capacitance = 0
    distances = {}
    for number, assignment in enumerate(assignments, 1):
        if assignment["kind"] != "highSpeed" or assignment["chip"] != ref:
            continue
        name = f"C_DDR{number}"
        cap = parts[name]
        if cap.get("manufacturer_part_number") != "CL05B104KO5NNNC":
            raise ValueError(f"Verify package size and value for new bypass part {name}")
        center = placed[cap["source_component_id"]]["center"]
        point = center["x"], center["y"]
        capacitance += cap["capacitance"]
        distances[name] = max(min(math.dist(point, terminal) for terminal in group) for group in locations)
    if len(distances) < min_count or capacitance + 1e-14 < min_farads:
        raise ValueError(f"{ref}: {len(distances)} high-speed capacitors totaling {capacitance*1e6:g} uF")
    violations = {name: gap for name, gap in distances.items() if gap > limit}
    if violations:
        raise ValueError(f"{ref}: capacitor-to-ball distance exceeds {limit:g} mm: {violations}")
    farthest = max(distances, key=distances.get)
    print(f"{ref}: {len(distances)} high-speed 0402 capacitors, {capacitance*1e6:.2f} uF nominal; "
          f"maximum distance to nearest supply and ground balls {distances[farthest]:.3f} mm "
          f"at {farthest} (limit {limit:g} mm).")
