# Five-link lower-byte timing study

The rotated RAM and same-byte remap make D2, D3 and D4 reachable together with one transition down and one back on each signal. The routed DQS0 and DQSn0 traces each measure 15.32894 mm with 2.840 mm total barrel depth. They differ by less than 0.00001 mm against the 0.127 mm TI differential-pair limit. Mixed-mode proximity within 0.42 mm of the mate is 8.910 and 9.462 mm respectively. The model screens isolated, mixed and odd-mode propagation. Impedance and receiver waveform signoff remain open.

Each routed data trace satisfies the 0.635 mm TI strobe and present-peer length rules, and ±3.66332 ps modeled worst-case skew. With these new strobes and the pinned stack, the strobe-based window for two full vias is approximately 14.694–15.560 mm before the data-peer constraint. The powered 45-link placement uses a different strobe geometry and window. All added routes stay inside an envelope that reserves escape space for R1 and other startup balls.

Independent CAM reports five distinct CPU–RAM links, no mapped shorts and 993 plated barrels. All 71 reference terminals, 21 DCDC4 lands, seven switched DDR supply lands, 18 direct memory supply lands, calibration, VREF and MMC0 pass. Whole-board connectivity is incomplete. This is an isolated routing study.

The separate raw 14-link trial connected all eight lower-byte data lines and six upper-byte data lines simultaneously. It brought upper-byte D10, D11, D12 and D14 through the shared corridor, with zero mapped shorts and all 71 returns. Its expanded signal envelope left only 0.315 mm available on R1 against the 0.408 mm clearance requirement, so that routing was rejected. No timing from that trial has been used here.

To regenerate the local timing report, decompress the assembled circuit, then run the following command from the repository root.

```sh
d=studies/quarter-turn/timed-d234
gzip -dc "$d/handheld.circuit.json.gz" > /tmp/pixel-dash-d234.json
python checks/report-partial-ddr-byte.py /tmp/pixel-dash-d234.json studies/powered-byte1/d5-d7-timing.csv --byte 0 --study-open $(cat "$d/open-signals.txt")
```

[Prior/current lengths, flight and signed skew](byte0.csv) · [Independent drilled CAM](drilled-cam.txt) · [Spacing, reference and copper checks](geometry-checks.txt)
