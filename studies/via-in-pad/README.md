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

### A12 corridor with BA1 temporarily removed

With the existing bytes and clocks held, the search connected A12 to RAM ball N7 by two different landings. The route using the L1–L2 blind landing measured 44.81553 mm. The through-via alternative measured 44.77700 mm. Their excess over the 38.68999 mm project placement ceiling was 6.12554 mm and 6.08701 mm respectively. The search also failed to restore BA1 alongside the blind-landing route. Both outcomes are exploratory and the accepted board retains BA1.

### Sharing the corridor between clock enable and bank address 1

A two-net trial removes CKE and BA1 from d8b00c0, preserves the bytes and clocks, and reinstalls both commands using the staged paths below. The CKE flight estimate changes from 214.830 to 240.383 ps, or +3.912 ps relative to CK. Its 27.94050 mm length falls 8.20949 mm short of the project window. BA1 rises to 49.12547 mm and 328.055 ps, or +91.585 ps relative to CK. It exceeds the 38.68999 mm ceiling by 10.43548 mm. The window starts at 36.14999 mm. The clock-relative flight values use the board model. Receiver setup and hold remain open. The pour rebuild also reported a floating L3 region of approximately 98.51 mm². The accepted board retains both original commands. [Trial lengths, layer spans and receiver screens](command-trials/paired-command-timing.csv) · [Trial path coordinates](command-trials/pair-1.json)

The reconstructed trial passes 0.102 mm unrelated-copper and 0.1524 mm via-edge clearance in the layout checks. BA1's first two drilled transitions overlap, with −0.121799 mm edge clearance against a required +0.130 mm. The hole collision is present even though those two checks report zero findings. [Drill-spacing result](command-trials/drill.txt)
