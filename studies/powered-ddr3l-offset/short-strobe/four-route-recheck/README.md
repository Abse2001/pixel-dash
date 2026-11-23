# Four-route west trial with the upper byte installed

The lower-byte trial keeps the original strobe pair and the 20.600104 mm mapping-derived limit. It installs CPU D1, D2, D4 and D6 and assigns the remaining D3 destination in the netlist. The stored permutation uses the original RAM positions in the order 6, 2, 4, 3, 1 for CPU D1, D2, D3, D4, D6 respectively. D2 uses its original RAM position here. The earlier D2-to-F8 trial has a different mapping and is recorded separately. All installed upper-byte routes and their real drill spans were present in both exports.

| Export | Copper pairs under 0.102 mm | Via-edge exceptions under 0.1524 mm | Drill-spacing findings | Full-width reference findings |
| --- | ---: | ---: | ---: | ---: |
| Four lower data routes with the original upper byte | 25 | 9 | 0 | 7 |
| Same four with local D12/D14 changes | 24 | 8 | 0 | 6 |
| Earlier D2-to-F8 mapping with local D12/D14 changes | 2 | 1 | 0 | 1 |

The upper-byte edit changes D12 from 23.7632 to 23.5896 mm and D14 from 23.6585 to 23.7121 mm on the four-route trial. Drilled CAM still identifies a connected copper island carrying multiple signals. Several crosses involve the upper strobes, D9, D15 and the mask, beyond the two edited neighbors. Both byte timing groups and receiver setup/hold remain open. The saved circuit is a failing fixture. Continue using the separate 40-link checkpoint for clean geometry.

On the earlier D2-to-F8 trial, the top D2/D14 short, the 0.0738568 mm D2/D12 gap and the 0.1171545 mm via-edge gap remain. With both upper routes lifted for search and all other copper fixed, each upper signal could find a new two-via escape in isolation. Ordered and weighted searches tested multiple landing configurations and found no complete pair.

To reproduce the four-route CAM export, decompress the circuit, run the repository's tscircuit Gerber exporter and run the existing audit scripts against the resulting circuit and ZIP. Use `checks/audit-cam-connectivity.py`, `checks/check-ddr-gerber-strokes.py --all-traces`, `checks/audit-copper-contacts.py --clearance-mm 0.102`, `checks/audit-via-clearance.py`, `checks/audit-via-hole-spacing.py` and `checks/audit-ddr-reference-planes.py --full-width` with the explicitly missing nets supplied to the study gate. The parent directory's `screen.py` reconstructs the mapping-derived timing window directly from that circuit. Individual contact and timing reports are grouped by export below.

[Four-route circuit](four-route-trial.circuit.json.gz) · [Pin map and receiver requirements](four-byte-window.csv) · [Original four-route export](west-four-exact) · [Edited four-route export](west-four-local) · [Earlier D2 mapping](west-d2-local) · [Landing search](alternate-landings.txt)
