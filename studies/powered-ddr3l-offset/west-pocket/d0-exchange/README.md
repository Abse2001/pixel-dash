# D0 exchange with D5 and D7 installed together

Lifting D0 with D5 fixed opens a common bottom-layer component for five D7 RAM assignments. This assembled west-placement trial uses CPU D5 to the old RAM DQ2 and CPU D7 to the old RAM DQ6. The partial remap completes the permutation for the remaining open data lands. Drilled CAM reports 39 distinct DDR links, including D5 and D7, with zero shorts among mapped nets over 1,172 plated barrels. D0 stays open. Sixty order and cost variations restored at most one of D0 and D7 alongside D5.

| Installed signal | Prior standalone sample (mm) | Current (mm) | Via count / total span | Flight (ps) | Worst signed skew (ps) | Model limit (ps) | TI strobe mismatch / limit (mm) | Recomputed project length excess (mm) |
| --- | ---: | ---: | --- | ---: | ---: | ---: | --- | ---: |
| D5 | 21.1695 | 21.1695 | 2 / 2.840 mm | 140.8708 | −2.0132 | ±3.6633 | 0.3490 / 0.6350 | 0.5694 |
| D7 | 21.2712 | 21.2056 | 2 / 2.840 mm | 141.0793 | −1.8046 | ±3.6633 | 0.3128 / 0.6350 | 0.6055 |

The 0.0361 mm pairwise DQ difference fits the 0.635 mm peer limit. The incomplete byte has no full-peer result. Both routes and DQM0 pass modeled skew, but the completed test permutation changes the longest Manhattan ball-to-ball distance and therefore the placement-derived project maximum to 20.6001 mm. The strobe/model combination needs at least 20.8835 mm at two full transitions. Their joint window is empty even before testing additional peers. The earlier west-window result applies to its original ball assignments. TI does not specify an absolute 20.6001 mm maximum.

The export has ten copper findings below 0.102 mm and four reference gaps, including 0.0000102 mm² under D7. The via-edge and hole-spacing screens pass. This pair remains on the study branch. [All-net measured timing and limits](study-timing.csv) · [Physical connectivity](cam.out) · [Full-width reference](study-reference.csv) · [Assembled board](assembled.circuit.json.gz)
