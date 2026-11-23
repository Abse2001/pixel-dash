# A10 routing study

This populated circuit starts from the accepted MMC0 repair, preserves both DDR bytes, and exchanges A7 for A10. The default board on pixel-dash-wide retains A7. This study has 36 physically distinct links and 14 opens. Its native circuit and A10 layer waypoints are included for subsequent routing.

A10 joins U1.F4 to U_DDR.L7 with two top-to-inner2 transitions. Its planar length is 36.47853 mm in the 36.14999–38.68999 mm project window. Contacted barrel totals 2.650 mm and estimated flight is 260.268 ps, 23.798 ps later than mean CK. At the reference-slew DDR3L-800 screen, the source must provide 388.798 ps of setup and 261.202 ps of hold. Receiver margin is open.

The longer discarded tuning pocket separated 2.356215 mm² of L3 ground. The saved pocket preserves the connected ground and supply fills. The export reproduces both byte timings and their exact copper, both clock fingerprints, all DDR supply and return connections, sequenced MMC0, 40 split whole-board nets, and zero mapped-land shorts. The exact 14 DDR opens are in the CAM report. Full-width DDR and MMC0 checks report zero uncovered areas. Copper, 6 mil via-edge and drilled-hole checks are clean. Fabrication is on hold.

[Drilled connectivity](cam.txt) · [Byte matching and skew](bytes.txt) · [Command and receiver calculations](timing.txt) · [Supply lands](power.txt)
