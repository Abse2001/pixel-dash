"""Materialize the isolated reserved-corridor study against the c9be947 handheld export."""
import argparse
import json
from pathlib import Path

from planes import reclaim_drills, replace_paths

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("baseline", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
board = json.loads(args.baseline.read_text())
here = Path(__file__).parent
paths = json.loads((here/"paths.json").read_text())
opened = set(json.loads((here/"open.json").read_text()))
if opened.intersection(paths):
    raise ValueError("Open and routed sets overlap")
sources = {e["name"]:e for e in board if e["type"]=="source_trace" and e.get("name") in opened.union(paths)}
keys = {s["subcircuit_connectivity_map_key"] for s in sources.values()}
trace_ids = {s["source_trace_id"] for s in sources.values()}
originals = {t["source_trace_id"]:t for t in board if t["type"]=="pcb_trace" and t["source_trace_id"] in trace_ids}
if len(originals)!=len(opened)+len(paths):
    raise ValueError("Use the complete baseline")
lifted = [v for v in board if v["type"]=="pcb_via" and v.get("subcircuit_connectivity_map_key") in keys]
board = [e for e in board if not (e["type"]=="pcb_trace" and e["source_trace_id"] in originals
                                   or e["type"]=="pcb_via" and e.get("subcircuit_connectivity_map_key") in keys)]
added = replace_paths(board, sources, paths, originals)
reclaim_drills(board, lifted, added)
args.output.write_text(json.dumps(board))
