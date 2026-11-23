## A4 escape across the BA0 CPU fanout

These five rejected BA0 dogbones use two conventional off-pad L1–L2 blind vias (0.125 mm drill, 0.28 mm land). The RAM end of BA0 retains its accepted copper. Each path fits the project’s planar command window of 36.14999–38.68999 mm. The 0.102 mm trace and both via lands require 0.16 mm plane relief. In all five cases, that relief cuts off the L2 ground connection to the existing blind via at (−51.600088, 21.950088) mm. A4 remains open. Both bytes, clocks and BA0 retain their production geometry.

The connectivity screen uses the continuous drilled L2 ground island from the populated 6099a41 Gerber and the candidate’s two circles and line relief. It records the resulting isolated area touching the existing via annulus. The original BA0 is on L1 and contributes no L2 relief. The calculation rejects a route before manufacturing export. It does not qualify alternate builds or other topologies.

From this worktree, regenerate the board and Gerber archive with the project’s pinned exporter. Run the screen with the board JSON and corresponding archive as arguments.

```sh
python production/accepted/build.py
python studies/a4-bypass/check.py dist/index.circuit.json path/to/gerbers.zip > /tmp/a4-results.csv
diff -u studies/a4-bypass/results.csv /tmp/a4-results.csv
```
