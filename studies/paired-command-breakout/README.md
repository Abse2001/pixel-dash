# Paired command breakout study

The complete populated board in `board.circuit.json.gz` retains all 22 byte routes, 44 byte vias, both clock traces and all four clock vias. The 36-link build at 618d9c6 remains available. This first 37-link reconstruction is a fallback for the four-command breakout experiment.

| Command | Prior mm | Current mm | Contacted depth mm | Estimated flight ps | Relative to CK ps | Outside length window mm |
|---|---:|---:|---:|---:|---:|---:|
| A3 | open | 36.55549 | 13.25 | 321.634 | +85.164 | 0 |
| A5 | 37.53490 | 36.89304 | 5.30 | 261.111 | +24.641 | 0 |
| A6 | 36.11105 | 50.44564 | 0.38 | 300.123 | +63.653 | 11.75565 |

The project command window is 36.14999–38.68999 mm. Signed flight refers to board delay relative to the installed clock. The receiver calculation in `arrival.csv` estimates required launch setup and hold under the stated fixture and load model. Guaranteed launch, package and receiver margins remain open.

The A11/A14 search contested the CPU escape near (−55.05, 20.60) mm. On A3/A5, A3 on L2 competes with the L2 reference under A5 on L1 near the CPU. Temporarily releasing A6 allowed A3 and A5 to coexist. The first complete restoration sent A6 on a long L1/L2 detour. Releasing each bypass assembly in turn on the search grid left that path at about 50.45 mm. Even ignoring all forty assemblies together yielded 47.67 mm. These are bounded graph results.

The exact export confirmed 37 separate DDR links and all specified DDR power lands, N5/P5 and sequenced MMC0. Copper at 0.102 mm, via edge at 0.1524 mm, drill spacing and full-width coverage of routed DDR and MMC0 passed. The broader DDR envelope and the whole-board connectivity report still record release blockers. The C41 bypass experiment remains separate.

Decompress the board, export four-layer Gerbers using the repository CLI and run the project CAM checks against that circuit and export. The study includes per-check outputs and explicit waypoints. The exact physical open list is in `exact.log`. The authenticated production build continues to use its own frozen input.
