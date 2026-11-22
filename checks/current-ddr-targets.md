# AM3354 DDR3L routing and board-flight targets

Lengths are in mm and flight times in ps. TI SPRS717L Table 7-69 lists DQLM0/1 under MAX for nominal length. The project computes each byte ceiling from this placement. Table 7-68 gives the command nominal-length window. The separate delay estimate uses the 1.491 mm reference build, 5.769 ps/mm isolated, 5.617 ps/mm odd mode and 6.600 ps/mm of traversed barrel. A full L1–L4 passage adds 1.420 mm and 9.372 ps. Mixed mode estimates same-layer pair proximity within 0.42 mm. The 3.663 ps data-skew screen converts 0.635 mm at the isolated rate. TI specifies a length limit. Package delay, actual fabrication tolerances, impedance discontinuities, controller setup/hold and memory training remain outside this estimate.

## Byte 0

Placement-derived project maximum ≤ 20.600 mm. Data-to-data and data-to-either-strobe mismatch ≤ 0.635 mm each. Strobe positive-to-negative mismatch ≤ 0.127 mm. Each modeled delta below is the worst absolute difference to either strobe leg. The model screen checks isolated, mixed and uniform odd-mode strobe cases.

With the present mixed-mode strobe times, the common data-flight target is 129.360–136.118 ps to satisfy both strobe legs. The other delay scenarios are evaluated against their own strobe times.

| Signal | Planar / max mm | Via count | Mixed flight ps | Worst planar Δ to DQS mm | Mixed Δ ps | Worst modeled Δ ps / 3.663 | Failed screens |
|---|---|---|---|---|---|---|---|
| D0 | 20.286 / 20.600 | 2 | 135.772 | 0.171 | 3.317 | 4.045 | modeled skew; data length vs D1, D3, D4, D5, D7 |
| D1 | 23.765 / 20.600 | 2 | 155.846 | 3.651 | 23.391 | 24.118 | project length; strobe length; modeled skew; data length vs D0, D2, D3, D4, D5, D6, DQM0 |
| D2 | 20.238 / 20.600 | 4 | 154.243 | 0.124 | 21.788 | 22.515 | modeled skew; data length vs D1, D3, D4, D5, D7 |
| D3 | 22.535 / 20.600 | 4 | 167.491 | 2.420 | 35.036 | 35.764 | project length; strobe length; modeled skew; data length vs D0, D1, D2, D5, D6, D7, DQM0 |
| D4 | 22.221 / 20.600 | 4 | 165.680 | 2.106 | 33.225 | 33.953 | project length; strobe length; modeled skew; data length vs D0, D1, D2, D5, D6, D7, DQM0 |
| D5 | 26.383 / 20.600 | 2 | 170.949 | 6.269 | 38.494 | 39.222 | project length; strobe length; modeled skew; data length vs D0, D1, D2, D3, D4, D6, D7, DQM0 |
| D6 | 20.255 / 20.600 | 2 | 135.595 | 0.140 | 3.140 | 3.867 | modeled skew; data length vs D1, D3, D4, D5, D7 |
| D7 | 23.222 / 20.600 | 4 | 171.457 | 3.108 | 39.002 | 39.729 | project length; strobe length; modeled skew; data length vs D0, D2, D3, D4, D5, D6, DQM0 |
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

Placement-derived project maximum ≤ 23.000 mm. Data-to-data and data-to-either-strobe mismatch ≤ 0.635 mm each. Strobe positive-to-negative mismatch ≤ 0.127 mm. Each modeled delta below is the worst absolute difference to either strobe leg. The model screen checks isolated, mixed and uniform odd-mode strobe cases.

With the present mixed-mode strobe times, the common data-flight target is 143.223–150.101 ps to satisfy both strobe legs. The other delay scenarios are evaluated against their own strobe times.

| Signal | Planar / max mm | Via count | Mixed flight ps | Worst planar Δ to DQS mm | Mixed Δ ps | Worst modeled Δ ps / 3.663 | Failed screens |
|---|---|---|---|---|---|---|---|
| D8 | 22.430 / 23.000 | 2 | 148.143 | 0.295 | 1.705 | 2.258 | data length vs D12, D14 |
| D9 | 22.430 / 23.000 | 2 | 148.140 | 0.295 | 1.702 | 2.256 | data length vs D12, D14 |
| D10 | 22.581 / 23.000 | 2 | 149.013 | 0.144 | 2.575 | 3.128 | data length vs D12, D14 |
| D11 | 22.578 / 23.000 | 2 | 148.997 | 0.147 | 2.559 | 3.112 | data length vs D12, D14 |
| D12 | 23.808 / 23.000 | 2 | 156.090 | 1.173 | 9.652 | 10.205 | project length; strobe length; modeled skew; data length vs D8, D9, D10, D11, D13, D15, DQM1 |
| D13 | 22.586 / 23.000 | 2 | 149.044 | 0.139 | 2.606 | 3.159 | data length vs D12, D14 |
| D14 | 23.373 / 23.000 | 2 | 153.582 | 0.738 | 7.144 | 7.697 | project length; strobe length; modeled skew; data length vs D8, D9, D10, D11, D13, D15, DQM1 |
| D15 | 22.428 / 23.000 | 2 | 148.129 | 0.297 | 1.691 | 2.244 | data length vs D12, D14 |
| DQM1 | 22.568 / 23.000 | 2 | 148.937 | 0.157 | 2.499 | 3.052 | data length vs D12, D14 |

- DQS1 measures 22.635 mm with 2 vias and 146.438 ps of mixed-mode flight.
- DQSn1 measures 22.725 mm with 2 vias and 146.886 ps of mixed-mode flight.
- Strobe pair mismatch is 0.090 mm against 0.127 mm. Mixed flight difference is 0.448 ps.
- Data-to-data board flight spread is 7.961 ps (D12, D15) against the 3.663 ps model screen.
- Data-to-data planar mismatch is 1.380 mm (D12, D15) against 0.635 mm.
- Data-to-data including barrel depth mismatch is 1.380 mm (D12, D15) against 0.635 mm.
- Data-to-strobe planar mismatch is 1.173 mm (D12, DQS1) against 0.635 mm.
- Data-to-strobe including barrel depth mismatch is 1.173 mm (D12, DQS1) against 0.635 mm.

## Address, control and clock

The longest Manhattan distance plus 7.620 mm gives CACLM = 29.820 mm. Target range is 28.550–31.090 mm. The receiver captures control/address relative to the rising CK differential crossing. Board skew Δ uses the mixed signal flight minus the CK-pair mean. Positive Δ consumes setup time and increases hold time.

The populated MT41K512M16VRP-107 has two x8 dies in one package on the board's single rank. The values below use the Micron 4Gb x8 Table 60 DDR3L-1866 speed-bin bases at AC135/DC90, 65 ps setup and 110 ps hold. The minimum CPU-ball valid intervals before and after the clock are 65 + Δ and 110 − Δ ps at the reference slew. For the conservative DDR3L-800 AC135/DC90 screening case substitute 365 and 285 ps. Actual margin also needs controller earliest/latest launch relative to CK, receiver slew derating, jitter, threshold crossings and package/die loading. These margins remain open. Command protocol timings for CKE, ODT and chip select are additional checks.

| Net | Planar mm | Via span mm | Flight ps | Δ to CK ps | Required source setup ps | Required source hold ps | Receiver margin | Nominal length result |
|---|---|---|---|---|---|---|---|---|
| A0 | 28.632 | 2.840 | 183.919 | +4.079 | 69.079 | 105.921 | open | pass |
| A1 | 28.721 | 5.680 | 203.179 | +23.339 | 88.339 | 86.661 | open | pass |
| A10 | 39.131 | 2.840 | 244.490 | +64.650 | 129.650 | 45.350 | open | -8.041 mm needed |
| A11 | 28.592 | 5.680 | 202.435 | +22.595 | 87.595 | 87.405 | open | pass |
| A12 | 28.660 | 2.840 | 184.086 | +4.246 | 69.246 | 105.754 | open | pass |
| A13 | 28.680 | 2.840 | 184.199 | +4.359 | 69.359 | 105.641 | open | pass |
| A14 | 28.590 | 2.840 | 183.680 | +3.840 | 68.840 | 106.160 | open | pass |
| A15 | 28.580 | 2.840 | 183.621 | +3.781 | 68.781 | 106.219 | open | pass |
| A2 | 28.660 | 2.840 | 184.084 | +4.244 | 69.244 | 105.756 | open | pass |
| A3 | 28.650 | 2.840 | 184.025 | +4.185 | 69.185 | 105.815 | open | pass |
| A4 | 28.720 | 2.840 | 184.430 | +4.590 | 69.590 | 105.410 | open | pass |
| A5 | 28.943 | 2.840 | 185.716 | +5.876 | 70.876 | 104.124 | open | pass |
| A6 | 25.350 | 5.680 | 183.732 | +3.892 | 68.892 | 106.108 | open | +3.200 mm needed |
| A7 | 28.606 | 2.840 | 183.774 | +3.934 | 68.934 | 106.066 | open | pass |
| A8 | 28.719 | 2.840 | 184.422 | +4.582 | 69.582 | 105.418 | open | pass |
| A9 | 28.718 | 2.840 | 184.416 | +4.576 | 69.576 | 105.424 | open | pass |
| BA0 | 28.683 | 2.840 | 184.214 | +4.374 | 69.374 | 105.626 | open | pass |
| BA1 | 28.693 | 2.840 | 184.271 | +4.431 | 69.431 | 105.569 | open | pass |
| BA2 | 29.791 | 2.840 | 190.610 | +10.771 | 75.771 | 99.229 | open | pass |
| CASn | 28.707 | 2.840 | 184.356 | +4.516 | 69.516 | 105.484 | open | pass |
| CK | 28.648 | 2.840 | 180.089 | +0.249 | — | — | clock | pass |
| CKE | 33.673 | 5.680 | 231.748 | +51.908 | 116.908 | 58.092 | open | -2.583 mm needed |
| CKn | 28.553 | 2.840 | 179.591 | -0.249 | — | — | clock | pass |
| CSn0 | 28.690 | 2.840 | 184.257 | +4.417 | 69.417 | 105.583 | open | pass |
| ODT | 28.575 | 2.840 | 183.591 | +3.751 | 68.751 | 106.249 | open | pass |
| RASn | 28.715 | 2.840 | 184.401 | +4.561 | 69.561 | 105.439 | open | pass |
| WEn | 28.766 | 2.840 | 184.697 | +4.857 | 69.857 | 105.143 | open | pass |

[Micron x8 base-die timing, Tables 60–64](https://media.digikey.com/pdf/Data%20Sheets/Micron%20Technology%20Inc%20PDFs/MT41K_DDR3L_4Gb_Rev.Q_Dec2017_DS.pdf#page=102) · [TwinDie topology and part data](https://datasheet.datasheet.lcsc.com/datasheet/pdf/1a552aaada9c9cb5685b5fb937531c2e.pdf)

CK pair mismatch is 0.095 mm against 0.127 mm. Its mixed flight difference is 0.498 ps.

RESETn measures 16.522 mm with 2 vias and 114.059 ps of modeled flight. It is assessed with reset sequencing.

[TI AM335x datasheet](https://www.ti.com/lit/ds/symlink/am3354.pdf) · [Barrel-inclusive nominal-window sensitivity](current-timing.txt)
