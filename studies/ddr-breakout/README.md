# Populated DDR breakout trials

The exported copper and plated barrels connect all 15 designated reference bypass capacitors to direct DCDC3 and ground. At the ODT transition the farther via of the nearest verified capacitor pair is 9.504 mm away. This geometric distance does not establish return inductance or receiver margin. [Distance at every DDR layer change](transition-returns.csv)

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

### D5 forces both byte-1 detours at the current via sites

Using byte-0 D5 as the sole obstacle gives a 23.18303 mm lower bound for D12 and 23.33316 mm for D14. These exceed the byte-1 window by 0.18493 mm and 0.33506 mm respectively. With D1 alone the bounds are 21.92024 mm and 22.08984 mm. All lengths use the physical CPU and RAM ball centers and the two existing through-via locations.

Even a legal DQ remap within byte 1 cannot reach the present D14 RAM escape within 22.9981 mm while retaining D5 and the eight CPU escape sites. The table holds the RAM-side via and ball fixed and allows each CPU source its shortest possible paths around D5. The calculation omits every other obstacle and allows arbitrary bends.

| CPU DQ | Lower bound to the D14 receiver escape (mm) |
|---|---:|
| D8 | 34.53192 |
| D9 | 32.78802 |
| D10 | 24.78926 |
| D11 | 24.33099 |
| D12 | 24.13282 |
| D13 | 23.73134 |
| D14 | 23.33316 |
| D15 | 33.46996 |

To reproduce any row, select the corresponding CPU signal:

```sh
python studies/ddr-breakout/fixed-via-bound.py dist/index.circuit.json DDR_D13 --ram-signal DDR_D14 --keep-only DDR_D5
```

A separate two-transition routing experiment released the CPU and RAM via locations for D5, D12 and D14 together. It also tried releasing D1 and swapping D1/D5 and D12/D14 within their respective bytes. The 0.032–0.033 mm grid candidates retained either clearance overlaps or excess length. The production design keeps all 50 original endpoints and its previously verified copper. The current length, flight estimate, signed skew, applicable limit and residual for every routed signal are in the [timing ledger](../../checks/current-ddr-change.csv).
