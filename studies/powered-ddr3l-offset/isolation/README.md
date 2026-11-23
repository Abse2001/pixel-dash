# Shifted RAM supply isolation

This is the partial six-barrel study at RAM center (−64.2, 16.75) mm. It has twelve intentionally lifted DDR signals and predates the powered touch/panel additions. The powered board remains at 4ee21e6.

The top-layer SELECT trace from (−51.04, 26.76) to (−62.64, 29.16) mm intersected both pads, both fanout traces and both vias of C_DDR37. The pad centers were (−57.305437, 27.948895) and (−58.042256, 28.155721) mm. The new SELECT centerline detours north of the capacitor. Neither supply nor ground was disconnected to clear it.

There were also bottom-layer contacts involving CK/DQM1, RESETn/CASn and RESETn/A12. Long segments crossing the two displacement boundaries had been redrawn as a single straight chord between shifted vertices. Explicit bends at each crossed boundary, including wire-to-via transitions, restore the piecewise image of the original path.

Drilled Gerber CAM verifies 38 distinct DDR links and 1,129 plated barrels with zero shorts between mapped land nets. All 22 switched CPU and 14 direct DRAM bypasses have the correct supplies, all mapped grounds reach the probe, and 71 local reference terminals connect. D2/D3/D4 retain all six holes and 24 land inspections. Minimum center spacing is 1.207477 mm against 0.4020 mm. These are barrel witnesses only.

Full study placement checks still find 37 unrelated copper pairs below 0.102 mm, 29 via-to-unrelated-trace findings below 0.1524 mm, one drill-edge gap of 0.199343 mm against 0.200 mm, and 16 full-width reference findings. Consequently the study remains separate. The circuit JSON can be decompressed and exported with the repository's tscircuit CLI using the .circuit.json filename extension.

[Original copper contacts](original-contacts.csv) · [Repaired study](repaired.circuit.json.gz) · [Drilled CAM](cam2.txt) · [Six barrels](final-barrels.txt) · [Copper](clearance.csv) · [Via edges](via.csv) · [Drills](drill.csv) · [Reference coverage](refs.csv)
