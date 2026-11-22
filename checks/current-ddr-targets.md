# AM3354 DDR3L routing and board-flight targets

Lengths are in mm and flight times in ps. The nominal length and skew screens use TI SPRS717L Tables 7-68 and 7-69. The separate delay estimate uses the 1.491 mm reference build, 5.769 ps/mm isolated, 5.617 ps/mm odd mode and 6.600 ps/mm of traversed barrel. A full L1–L4 passage adds 1.420 mm and 9.372 ps. Mixed mode estimates same-layer pair proximity within 0.42 mm. The 3.663 ps data-skew screen converts 0.635 mm at the isolated rate. TI specifies a length limit. Package delay, actual fabrication tolerances, impedance discontinuities, controller setup/hold and memory training remain outside this estimate.

## Byte 0

Nominal planar length ≤ 20.600 mm. Data-to-data and data-to-either-strobe mismatch ≤ 0.635 mm each. Strobe positive-to-negative mismatch ≤ 0.127 mm. Each modeled delta below is the worst absolute difference to either strobe leg. The model screen checks isolated, mixed and uniform odd-mode strobe cases.

With the present mixed-mode strobe times, the common data-flight target is 129.360–136.118 ps to satisfy both strobe legs. The other delay scenarios are evaluated against their own strobe times.

| Signal | Planar / max mm | Via count | Mixed flight ps | Worst planar Δ to DQS mm | Mixed Δ ps | Worst modeled Δ ps / 3.663 | Failed screens |
|---|---|---|---|---|---|---|---|
| D0 | 20.286 / 20.600 | 2 | 135.772 | 0.171 | 3.317 | 4.045 | modeled skew; data length vs D1, D3, D4, D5, D7 |
| D1 | 23.765 / 20.600 | 2 | 155.846 | 3.651 | 23.391 | 24.118 | nominal; strobe length; modeled skew; data length vs D0, D2, D3, D4, D5, D6, DQM0 |
| D2 | 20.238 / 20.600 | 4 | 154.243 | 0.124 | 21.788 | 22.515 | modeled skew; data length vs D1, D3, D4, D5, D7 |
| D3 | 22.535 / 20.600 | 4 | 167.491 | 2.420 | 35.036 | 35.764 | nominal; strobe length; modeled skew; data length vs D0, D1, D2, D4, D5, D6, D7, DQM0 |
| D4 | 21.894 / 20.600 | 4 | 163.796 | 1.780 | 31.341 | 32.069 | nominal; strobe length; modeled skew; data length vs D0, D1, D2, D3, D5, D6, D7, DQM0 |
| D5 | 26.383 / 20.600 | 2 | 170.949 | 6.269 | 38.494 | 39.222 | nominal; strobe length; modeled skew; data length vs D0, D1, D2, D3, D4, D6, D7, DQM0 |
| D6 | 20.255 / 20.600 | 2 | 135.595 | 0.140 | 3.140 | 3.867 | modeled skew; data length vs D1, D3, D4, D5, D7 |
| D7 | 23.222 / 20.600 | 4 | 171.457 | 3.108 | 39.002 | 39.729 | nominal; strobe length; modeled skew; data length vs D0, D2, D3, D4, D5, D6, DQM0 |
| DQM0 | 20.259 / 20.600 | 2 | 135.615 | 0.144 | 3.160 | 3.888 | modeled skew; data length vs D1, D3, D4, D5, D7 |

- DQS0 measures 20.225 mm with 2 vias and 133.023 ps of mixed-mode flight.
- DQSn0 measures 20.115 mm with 2 vias and 132.455 ps of mixed-mode flight.
- Strobe pair mismatch is 0.110 mm against 0.127 mm. Mixed flight difference is 0.568 ps.
- Data-to-data board flight spread is 35.862 ps (D7, D6) against the 3.663 ps model screen.
- Data-to-data planar mismatch is 6.145 mm (D2, D5) against 0.635 mm.
- Data-to-data including barrel depth mismatch is 6.128 mm (D5, D6) against 0.635 mm.
- Data-to-strobe planar mismatch is 6.269 mm (D5, DQSn0) against 0.635 mm.
- Data-to-strobe including barrel depth mismatch is 6.269 mm (D5, DQSn0) against 0.635 mm.

## Byte 1

Nominal planar length ≤ 23.000 mm. Data-to-data and data-to-either-strobe mismatch ≤ 0.635 mm each. Strobe positive-to-negative mismatch ≤ 0.127 mm. Each modeled delta below is the worst absolute difference to either strobe leg. The model screen checks isolated, mixed and uniform odd-mode strobe cases.

With the present mixed-mode strobe times, the common data-flight target is 143.223–150.101 ps to satisfy both strobe legs. The other delay scenarios are evaluated against their own strobe times.

| Signal | Planar / max mm | Via count | Mixed flight ps | Worst planar Δ to DQS mm | Mixed Δ ps | Worst modeled Δ ps / 3.663 | Failed screens |
|---|---|---|---|---|---|---|---|
| D8 | 19.315 / 23.000 | 4 | 148.916 | 3.410 | 2.478 | 3.031 | strobe length; data length vs D10, D11, D12, D13, D14, D15, DQM1 |
| D9 | 19.316 / 23.000 | 4 | 148.922 | 3.409 | 2.484 | 3.037 | strobe length; data length vs D10, D11, D12, D13, D14, D15, DQM1 |
| D10 | 22.581 / 23.000 | 2 | 149.013 | 0.144 | 2.575 | 3.128 | data length vs D8, D9, D12, D14 |
| D11 | 22.578 / 23.000 | 2 | 148.997 | 0.147 | 2.559 | 3.112 | data length vs D8, D9, D12, D14 |
| D12 | 23.843 / 23.000 | 2 | 156.295 | 1.208 | 9.858 | 10.411 | nominal; strobe length; modeled skew; data length vs D8, D9, D10, D11, D13, D15, DQM1 |
| D13 | 22.586 / 23.000 | 2 | 149.044 | 0.139 | 2.606 | 3.159 | data length vs D8, D9, D12, D14 |
| D14 | 23.459 / 23.000 | 2 | 154.082 | 0.824 | 7.644 | 8.197 | nominal; strobe length; modeled skew; data length vs D8, D9, D10, D11, D13, D15, DQM1 |
| D15 | 22.564 / 23.000 | 2 | 148.917 | 0.161 | 2.479 | 3.032 | data length vs D8, D9, D12, D14 |
| DQM1 | 22.568 / 23.000 | 2 | 148.937 | 0.157 | 2.499 | 3.052 | data length vs D8, D9, D12, D14 |

- DQS1 measures 22.635 mm with 2 vias and 146.438 ps of mixed-mode flight.
- DQSn1 measures 22.725 mm with 2 vias and 146.886 ps of mixed-mode flight.
- Strobe pair mismatch is 0.090 mm against 0.127 mm. Mixed flight difference is 0.448 ps.
- Data-to-data board flight spread is 7.379 ps (D12, D8) against the 3.663 ps model screen.
- Data-to-data planar mismatch is 4.528 mm (D8, D12) against 0.635 mm.
- Data-to-data including barrel depth mismatch is 1.688 mm (D8, D12) against 0.635 mm.
- Data-to-strobe planar mismatch is 3.410 mm (D8, DQSn1) against 0.635 mm.
- Data-to-strobe including barrel depth mismatch is 1.208 mm (D12, DQS1) against 0.635 mm.

## Address, control and clock

The longest Manhattan distance plus 7.620 mm gives CACLM = 29.820 mm. Target range is 28.550–31.090 mm. Each isolated-flight target below converts the length window at that net’s actual via depth. The signed mixed-mode difference uses the mean of CK and CKn. The data-byte 3.663 ps screen does not apply to this group.

| Net | Planar mm | Via count | Isolated flight ps | Isolated target ps | Mixed Δ to CK mean ps | Nominal length result |
|---|---|---|---|---|---|---|
| A0 | 28.632 | 2 | 183.919 | 183.449–198.102 | +4.079 | pass |
| A1 | 28.721 | 4 | 203.179 | 202.193–216.846 | +23.339 | pass |
| A10 | 39.232 | 2 | 245.071 | 183.449–198.102 | +65.231 | -8.142 mm needed |
| A11 | 28.592 | 4 | 202.435 | 202.193–216.846 | +22.595 | pass |
| A12 | 28.660 | 2 | 184.086 | 183.449–198.102 | +4.246 | pass |
| A13 | 23.573 | 2 | 154.737 | 183.449–198.102 | -25.103 | +4.977 mm needed |
| A14 | 27.916 | 2 | 179.794 | 183.449–198.102 | -0.046 | +0.634 mm needed |
| A15 | 28.580 | 2 | 183.621 | 183.449–198.102 | +3.781 | pass |
| A2 | 28.660 | 2 | 184.084 | 183.449–198.102 | +4.244 | pass |
| A3 | 28.650 | 2 | 184.025 | 183.449–198.102 | +4.185 | pass |
| A4 | 28.720 | 2 | 184.430 | 183.449–198.102 | +4.590 | pass |
| A5 | 28.943 | 2 | 185.716 | 183.449–198.102 | +5.876 | pass |
| A6 | 25.350 | 4 | 183.732 | 202.193–216.846 | +3.892 | +3.200 mm needed |
| A7 | 28.606 | 2 | 183.774 | 183.449–198.102 | +3.934 | pass |
| A8 | 28.719 | 2 | 184.422 | 183.449–198.102 | +4.582 | pass |
| A9 | 28.718 | 2 | 184.416 | 183.449–198.102 | +4.576 | pass |
| BA0 | 28.683 | 2 | 184.214 | 183.449–198.102 | +4.374 | pass |
| BA1 | 28.693 | 2 | 184.271 | 183.449–198.102 | +4.431 | pass |
| BA2 | 29.791 | 2 | 190.610 | 183.449–198.102 | +10.771 | pass |
| CASn | 28.707 | 2 | 184.356 | 183.449–198.102 | +4.516 | pass |
| CK | 28.648 | 2 | 184.012 | 183.449–198.102 | +0.249 | pass |
| CKE | 33.841 | 4 | 232.718 | 202.193–216.846 | +52.878 | -2.751 mm needed |
| CKn | 28.553 | 2 | 183.464 | 183.449–198.102 | -0.249 | pass |
| CSn0 | 28.690 | 2 | 184.257 | 183.449–198.102 | +4.417 | pass |
| ODT | 28.575 | 2 | 183.591 | 183.449–198.102 | +3.751 | pass |
| RASn | 28.715 | 2 | 184.401 | 183.449–198.102 | +4.561 | pass |
| WEn | 28.766 | 2 | 184.697 | 183.449–198.102 | +4.857 | pass |

CK pair mismatch is 0.095 mm against 0.127 mm. Its mixed flight difference is 0.498 ps.

RESETn measures 16.522 mm with 2 vias and 114.059 ps of modeled flight. It is assessed with reset sequencing.

[TI AM335x datasheet](https://www.ti.com/lit/ds/symlink/am3354.pdf) · [Barrel-inclusive nominal-window sensitivity](current-timing.txt)
