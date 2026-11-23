# Touch I²C clock routing trial

The fitted AM3354 D15 (UART1_TXD, mux mode 3 for I2C1_SCL) now reaches R_TOUCH_SCL pin 1 on the populated handheld in this study. The 121.17542 mm route has 14 plated transitions. All mapped pad nets remain isolated from each other. Thirty-seven mapped nets remain physically split, down from 38 on f9cb35c. SDA is still open. This trial terminates at the retained pull-up. Panel operation and bus rise time remain open.

The independent CAM audit recovers the same 37 DDR links, both locked bytes and clocks, DDR power/calibration and the sequenced card supply and seven MMC0 signals. All prior raster reference areas are preserved to within the artwork polygon precision. The 0.102 mm copper, 0.1524 mm via-edge and drill spacing gates pass. The four-width and conservative DDR region screens retain the 24 and 57 existing findings respectively. [Whole-board audit](whole.log) · [DDR and card endpoints](exact.log) · [DDR references](ref.log)

The I²C clock itself has three signal-layer combinations with exposed trace area lacking adjacent connected ground. Those areas are 0.0944683 mm² on top, 0.1134530 mm² on L3 and 0.1680938 mm² on bottom. They were measured on the exported copper using the full-width raster ground-reference algorithm restricted to system_TOUCH_SCL. A strict four-layer escape search on a 50 µm grid found no complete path with full adjacent ground. The geometry is held on this branch for further routing. [Clock ground coverage](own-return.txt)

Decompress study.circuit.json.gz and export Gerbers from that circuit to reproduce the copper. The production build at this commit still loads the accepted handheld.
