"""Screen mechanical through vias against the public JLCPCB HDI dimensions."""
import argparse
import json
import math
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("--board-thickness-mm", type=float, required=True)
    args = parser.parse_args()
    thickness = args.board_thickness_mm
    if not math.isfinite(thickness) or thickness <= 0:
        parser.error("Board thickness must be finite and positive")
    sizes = Counter()
    errors = []
    for via in json.loads(args.circuit.read_text()):
        if via["type"] != "pcb_via" or {via["from_layer"], via["to_layer"]} != {"top", "bottom"}:
            continue
        hole, pad = via["hole_diameter"], via["outer_diameter"]
        sizes[hole, pad] += 1
        if not (math.isfinite(hole) and math.isfinite(pad) and hole >= 0.15
                and pad - hole >= 0.10 - 1e-9 and thickness <= 16 * hole + 1e-9):
            errors.append(via["pcb_via_id"])
    if not sizes:
        raise ValueError("No through vias in input")
    print(f"Screened {sum(sizes.values())} mechanical through vias at {thickness:g} mm board thickness.")
    for (hole, pad), count in sorted(sizes.items()):
        print(f"{count:3d} with {hole:g} mm hole, {pad:g} mm pad, nominal ring {(pad-hole)/2:.4f} mm")
    if errors:
        raise SystemExit("Through-via dimension failures on " + ", ".join(errors))


if __name__ == "__main__":
    main()
