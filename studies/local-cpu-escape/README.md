# CPU-side D12 and D14 escape trial

Run `bun run build:local-escape` to reproduce the trial from the populated board. The ordinary build produces the original byte geometry. The differential check compares all byte routes, keeps the original 44 vias and restricts edits to the first L1 sections on D12 and D14. Both data nets use two through transitions with 2.84 mm of contacted barrel.

D12 changed from 19.93994 to 19.93981 mm. Estimated flight is 133.777 ps and worst signed strobe skew is +1.664 ps. D14 changed from 19.93994 to 19.94089 mm. Estimated flight is 133.783 ps and skew is +1.670 ps. Both pass the ±3.663 ps model screen with zero excess. All 22 byte nets pass the TI 0.635 mm data and 0.127 mm pair matching checks and the placement limits. [Per-net timing on the reference stack](byte-timing.csv)

Gerber and Excellon checks found 36 distinct DDR links, 1,067 plated barrels, zero mapped-land shorts and zero full-width DDR reference findings. The 0.102 mm copper clearance, 0.1524 mm via-edge clearance, drill spacing, self-contact, four-layer stroke and MMC0 checks pass. CAM confirms 18/18 direct DRAM supply balls, 21/21 DRAM grounds, 7/7 switched CPU DDR supply balls, and PGOOD_BU to CPU B5. Fifty unrelated or incomplete board nets still have multiple copper islands.

The geometry opens possible first-via locations at J4, F1 and G2. Continuation to the divider, CPU bypass and RAM remains open. The landing-area calculation alone does not establish an electrical connection. [Escape window results](escape-windows.txt)
