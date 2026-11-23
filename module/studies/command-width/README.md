# A8 inner trace width study

The baseline is the 37 × 46 mm six-layer module at 4f03b57. Five straight portions of A8 on L4 have full-width L3 DCDC3 and L5 ground coverage in the drilled baseline. The trial changes 16.1824 mm from 0.102 to 0.220 mm. Planar length stays 36.7000 mm inside the 36.1500–38.6900 mm placement window. The two traversed F–L4 barrels total 1.7846 mm. There are no byte or clock edits.

Independent export checks find 50 distinct DDR links, zero mapped shorts, full adjacent ground coverage outside the launch antipads and zero 0.1524 mm via-edge findings. KiCad reports zero copper-rule violations and 88 unconnected items on both boards. The projected direct DDR plane deficit remains 55.6410 mm². The accepted module continues separately on the six-layer CPU module branch.

## Conditional A8 receiver result

Using nominal TI ZCZ transmit fixtures, the wider sections move the last AC threshold crossing **later** in all 20 combinations of line profile, edge polarity and command input capacitance. The delay increases by 18.66–24.48 ps for isolated inner conductors and by 28.17–32.36 ps for the coplanar profile. These results leave source launch, clock alignment and receiver setup and hold open. The study has no fabrication output package. [Baseline crossings](baseline.csv) · [Trial crossings](trial.csv)

The line model walks from the AM3354 ball to the DRAM ball on the extracted native conductor graph. Each impedance transition scatters waves according to the two line impedances. Each end applies the TI fixture-derived affine source model or a lumped capacitive receiver at 1 ps time resolution. A single 50 Ω line must reproduce the independent single-line echo model within 1 µV. Reported crossings use the final upward crossing of the normalized voltage change on each edge. Direct DRAM VREFCA is 0.675 V here. The screen uses nominal 1.35 V, assumed IOCTRL 0x318, five capacitive loads, and each edge’s own source-fixture time origin.

The two inner profiles assume ideal adjacent AC reference planes. The isolated 0.102/0.220 mm line impedances are 72.564/53.186 Ω. Holding coplanar copper at reference potential from 0.130 mm away on both sides gives 62.336/46.501 Ω. The finite-difference geometry uses the inner solver in check-impedance.py. For coplanar copper, fix the grid points in the trace foil thickness at zero potential where the absolute lateral coordinate exceeds half the width plus 0.130 mm. The narrow coplanar estimate uses a 0.005 mm mesh and the wide estimate uses a 0.003 mm mesh. A tighter 0.102 mm coplanar gap gives about 44.316 Ω at 0.220 mm width, below the 45 Ω screen. Actual fabricated cross sections, etch, dynamic coplanar signals, barrel and package parasitics, local VREF noise, PVT and clock launch still require qualification. The outer isolated estimate is 54.987 Ω. Barrels use an assumed 50 Ω and 6.6 ps/mm.

## Replay

Starting from the repository root, supply KiCad 9, its pcbnew Python, SciPy, Shapely, Gerbonara and TI's SPRM552C ZCZ IBIS ZIP. Use an empty scratch directory as OUT. A shared basename ensures KiCad reads the module's rule file.

```sh
study=module/studies/command-width
cp module/pixel-dash-module.kicad_pro "$OUT/"
/usr/bin/python3 "$study/apply.py" module/pixel-dash-module.kicad_pcb "$OUT/pixel-dash-module.kicad_pcb"
/usr/bin/python3 module/fill-planes.py "$OUT/pixel-dash-module.kicad_pcb"
kicad-cli pcb drc --format json -o "$OUT/drc.json" "$OUT/pixel-dash-module.kicad_pcb"
/usr/bin/python3 module/extract-geometry.py module/pixel-dash-module.kicad_pcb > "$OUT/baseline.json"
/usr/bin/python3 module/extract-geometry.py "$OUT/pixel-dash-module.kicad_pcb" > "$OUT/trial.json"
python "$study/screen.py" "$OUT/baseline.json" "$TI_ZCZ_IBIS" > "$OUT/baseline.csv"
python "$study/screen.py" "$OUT/trial.json" "$TI_ZCZ_IBIS" > "$OUT/trial.csv"
diff -u "$study/baseline.csv" "$OUT/baseline.csv"
diff -u "$study/trial.csv" "$OUT/trial.csv"
kicad-cli pcb export gerbers --disable-aperture-macros -o "$OUT/films/" -l F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,Edge.Cuts "$OUT/pixel-dash-module.kicad_pcb"
kicad-cli pcb export drill -o "$OUT/films/" "$OUT/pixel-dash-module.kicad_pcb"
python module/check-cam.py "$OUT/films" "$OUT/trial.json"
python module/check-timing.py "$OUT/trial.json" > "$OUT/timing.csv"
python module/check-signal-paths.py "$OUT/trial.json" "$OUT/timing.csv"
python module/check-via-spacing.py "$OUT/trial.json" > "$OUT/spacing.csv"
diff -u module/via-spacing-findings.csv "$OUT/spacing.csv"
```
