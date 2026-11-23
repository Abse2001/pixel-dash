# A7 and A10 on the same populated routing trial

A7 and A10 both fit the 36.14999–38.68999 mm command length window on the same artwork. A7 measures 38.23230 mm with four L1/L4 transitions, 5.680 mm of contacted barrel, 258.050 ps of estimated flight and +21.580 ps to mean CK. A10 measures 36.47853 mm with two L1/L3 transitions, 2.650 mm of contacted barrel, 260.268 ps of estimated flight and +23.798 ps to mean CK. Receiver margin remains open on both.

A14 is open in this trial. Its original passing 38.67141 mm route remains on the accepted board. Attempts to restore A14 on the trial with the other installed signals fixed did not reach both terminals on the tested 0.03 mm grid. This checkpoint stays separate from the default build.

The Gerber and drill audit found 36 distinct DDR links, 1,116 plated barrels, 40 split board nets, and zero shorts between mapped lands. VREF, VTP, DDR and N5/P5 power lands, main ground, MMC0, trace-width reference coverage, both byte groups, copper, via-edge and drill-spacing checks reproduce here. [Physical endpoints](cam.txt) · [Clock-relative flight and source timing requirements](command-timing.csv) · [Both byte groups](bytes.txt)
