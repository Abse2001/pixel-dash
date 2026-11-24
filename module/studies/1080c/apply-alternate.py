import argparse
import csv
from pathlib import Path
import pcbnew as k
parser=argparse.ArgumentParser(description="Apply study widths to DDR line bodies on a copy of a KiCad module.")
parser.add_argument('board',type=Path)
parser.add_argument('output',type=Path)
args=parser.parse_args()
if args.board.resolve()==args.output.resolve():raise ValueError("Use a separate output board")
with args.board.with_name('timing.csv').open() as f:names={r['net'] for r in csv.DictReader(f)}
board=k.LoadBoard(str(args.board))
for track in board.GetTracks():
    if not isinstance(track,k.PCB_VIA) and track.GetNetname() in names:
        track.SetWidth(k.FromMM(.115 if track.GetLayer() in (k.F_Cu,k.B_Cu) else .230))
k.ZONE_FILLER(board).Fill(board.Zones())
k.SaveBoard(str(args.output),board)
