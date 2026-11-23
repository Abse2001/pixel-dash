"""Build an isolated A8 copper-width trial from the pinned native module board."""
import argparse
import json
from pathlib import Path
import pcbnew

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("baseline", type=Path)
parser.add_argument("trial", type=Path)
args = parser.parse_args()
if args.baseline.resolve() == args.trial.resolve():
    parser.error("Choose a separate output board for the study.")
board = pcbnew.LoadBoard(str(args.baseline))
intervals = json.loads(Path(__file__).with_name("a8-intervals.json").read_text())
groups = {}
for item in intervals:
    key = (item["net"], item["layer"], tuple(map(tuple, item["old"])))
    groups.setdefault(key, []).append(item["wide"])

def position(xy):
    return pcbnew.VECTOR2I(*(pcbnew.FromMM(v) for v in xy))

for (net, layer_name, (start, end)), spans in groups.items():
    layer = board.GetLayerID(layer_name)
    start, end = position(start), position(end)
    matches = []
    for track in board.GetTracks():
        if isinstance(track, pcbnew.PCB_VIA) or track.GetLayer() != layer or track.GetNetname() != net:
            continue
        a, b = track.GetStart(), track.GetEnd()
        if min((a-start).EuclideanNorm()+(b-end).EuclideanNorm(),
               (a-end).EuclideanNorm()+(b-start).EuclideanNorm()) <= 5:
            matches.append(track)
    original, = matches
    net_code = original.GetNetCode()
    board.Remove(original)
    sections = []
    cursor = start
    ranges = [sorted(map(position, span), key=lambda p: (p-start).EuclideanNorm()) for span in spans]
    for a,b in sorted(ranges, key=lambda ab: (ab[0]-start).EuclideanNorm()):
        sections.extend([(cursor,a,.102), (a,b,.220)])
        cursor = b
    sections.append((cursor,end,.102))
    for a,b,width in sections:
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(a)
        track.SetEnd(b)
        track.SetLayer(layer)
        track.SetWidth(pcbnew.FromMM(width))
        track.SetNetCode(net_code)
        board.Add(track)
pcbnew.SaveBoard(str(args.trial),board)
