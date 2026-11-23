# SYSBOOT0 and both byte strobes on the rotated placement

Drilled CAM verifies SYSBOOT0 high through its bias resistor at CPU ball R1. The routed raster net also reaches the panel. The 0.408 mm DDR margin and both full-width references pass with this strap installed. On the original placement even the bare DDR lands preclude the required R1 escape.

All seven installed DDR routes use two L1–L4 vias per net. The added DQS1 pair measures 16.81407 mm per leg. Its worst modeled signed skews are −0.01250 and +0.01250 ps against ±0.71336 ps. Both differential pairs pass the TI 0.127 mm match rule. D2, D3 and D4 retain the previous verified geometry. The remaining 43 DDR signals are open on this isolated study. The 45-link powered and previous 50-link boards remain separate fallbacks.

[Assembled board](handheld.circuit.json.gz) · [Lower-byte lengths and timing](byte0.csv) · [Upper-byte lengths and timing](byte1.csv) · [Physical CAM](drilled-cam.txt) · [Geometry checks](geometry-checks.txt)
