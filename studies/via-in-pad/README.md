# Filled via-in-pad escape study

The populated d8b00c0 board has 37 physical DDR links. The isolated A10 trial installs two 0.150 mm L1–L4 drills with 0.300 mm lands. U1.F4 takes an offset via at (−49.224907, 17.934998) mm. The U_DDR.L7 via is centered on its ball. The study depends on filled, planarized and capped via-in-pad processing. Supplier acceptance, registration and solderability remain open.

Independent Gerber and Excellon reconstruction finds copper on all four layers contacting each plated barrel, with each top annulus connected to its BGA pad. The CPU and RAM pads still belong to separate CAM networks. The DDR supply, byte/clock guard, full-width routed DDR and MMC0 reference, shorts, drill, 0.102 mm copper and 0.1524 mm via-edge checks pass. The four panel taps added at d8b00c0 are retained. [Ball-to-barrel checks](barrel.txt) · [Independent drilled CAM](drilled-cam.txt) · [Reference check](ddr-reference.txt)

The screen intersects each entire via land with the unmoved package pad and excludes unrelated copper, bores and the projected return clearances of routed DDR, MMC0 and raster signals. It covers 13 open commands at both ends and eight open CPU boot taps. The last column identifies the largest single excluded area, which can be one of several overlapping obstacles. The stacked variant models the combined lands of an L1–L2 blind and L2–L3 buried drill. Legal local area is a geometric screen. An end-to-end trace additionally needs a route with continuous return, correct delay and verified power. [Per-land results](landings.csv)

To reproduce from the repository root, run the accepted board build and the following commands with the repository's CAM dependencies installed.

```sh
python production/accepted/build.py
python studies/via-in-pad/screen.py dist/index.circuit.json checks > /tmp/vip-landings.csv
python studies/via-in-pad/launch.py dist/index.circuit.json /tmp/vip-landings.csv /tmp/a10.circuit.json
tsci export /tmp/a10.circuit.json -f gerbers -o /tmp/a10.zip
PYTHONPATH=checks python studies/via-in-pad/barrel.py /tmp/a10.circuit.json /tmp/a10.zip
```
