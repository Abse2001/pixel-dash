"""Fill both ground planes with the project's saved clearance rules loaded."""
from pathlib import Path
import sys
import pcbnew as k

board_path=Path(sys.argv[1]).resolve()
project=board_path.with_suffix(".kicad_pro")
settings=project.read_bytes()
manager=k.GetSettingsManager()
assert manager.LoadProject(str(project))
board=k.LoadBoard(str(board_path))
board.SetProject(manager.GetProject(str(project)))
board.BuildConnectivity()
k.ZONE_FILLER(board).Fill(board.Zones())
k.SaveBoard(str(board_path),board)
project.write_bytes(settings)
