# Populated DDR breakout trials

The input was the native assembled handheld at c28dc8c. Each path uses board coordinates in millimetres. The first section runs on L1. Successive sections alternate between L4 and L1, with a full-depth via at their shared endpoint. These alternatives are isolated from the board generator.

The byte-1 trials protected the original byte-0 escape and the handheld components, signals and reference planes. Routing orders started with either D8/D9 or the strobe pair. The byte-0 trials reserved a separate set of paths for D7, D5, D3, D4, D2 and both strobe legs. The southern and command trials included A10 and CKE. A separate pin-and-repair pass tried to restore the conductors displaced by promising escapes. The finite pool produced no jointly clear 50-link alternative with a better via topology. Both byte-1 strobe legs also lacked a straight opposite-layer excursion with two legal new via sites in the tested fixed-copper corridor.

Run `python studies/ddr-breakout/check-corridors.py path/to/c28dc8c/index.circuit.json` to reproduce the conflicts against the retained DDR paths. The comparison checks end-ball identity by coordinates, signal-to-signal spacing, via-to-signal spacing, via-land spacing and drill spacing. The accepted routing uses the whole-handheld audits and native Gerbers.

[Candidate paths](trial-paths.json) · [Conflicting nets](corridor-conflicts.csv)

## Byte 1 with the two existing via locations fixed

On routed checkpoint `25bb680`, D12 measures 23.6978 mm and D14 measures 23.3728 mm. Each uses two 1.420 mm L1–L4 passages. The current strobes give a joint two-transition length window of 22.3342–22.9981 mm for the strobe and modeled flight checks. Peer matching imposes an additional constraint.

The study computes the shortest planar path through fixed via centers on each route layer, treating the other DDR tracks and vias as obstacles. A visibility graph uses the vertices of inscribed clearance polygons. The octagonal polygons, slightly reduced radii and omission of non-DDR copper, drill restrictions and reference planes relax the manufacturing constraints. A lower bound above the target rules out that escape. A lower bound inside the window only identifies a candidate for physical routing.

| Signal | Additional track lifted in the study | Planar lower bound (mm) | Excess above 22.9981 mm |
|---|---|---:|---:|
| D12 | None | 23.6151 | 0.6170 |
| D12 | D14 | 23.1830 | 0.1849 |
| D12 | D14 and D10 | 23.1830 | 0.1849 |
| D12 | D14 and D11 | 23.1830 | 0.1849 |
| D12 | D14 and D13 | 23.1830 | 0.1849 |
| D14 | None | 23.3362 | 0.3381 |
| D14 | D12 | 23.3362 | 0.3381 |

Lifting D12 and D14 together still requires moving at least one via or another neighbor to bring each signal into the window. A separate 0.040 mm grid trial retained the CPU escapes and allowed the two RAM-side through-vias to move. Four trials released 8.2, 10.4, 12.6 or 14.4 mm of each bottom-layer tail. Only the 12.6 mm trial found both paths. Its best conflict score still had overlapping clearance envelopes and the paths measured 23.553 and 23.992 mm. All four trials were rejected. The established strobes, mask and all 50 connections remain in the routed checkpoint. To reproduce an individual bound with Python and Shapely 2, run from the repository root:

```sh
python studies/ddr-breakout/fixed-via-bound.py dist/index.circuit.json DDR_D12 --lift DDR_D14
```
