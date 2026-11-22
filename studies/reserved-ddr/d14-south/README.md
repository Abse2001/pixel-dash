# Rejected D14 escape from the complete 66b9fc9 layout

The reference candidate connects all 50 DDR ball pairs and routes D14 at 23.3728 mm. With two 1.420 mm transitions, the 22.0900–22.6736 mm project window on this placement combines TI length matching to both DQS1 legs with the independent stack-delay screen. Moving the CPU- and RAM-side vias puts D14 at 22.4439 mm, with 148.2227 ps estimated flight and +2.3379 ps worst skew. This leaves 1.3254 ps to the modeled limit and 0.3539 mm to the 0.635 mm data-to-strobe mismatch limit. The peer mismatch to D12 still exceeds TI's 0.635 mm limit by 0.6189 mm.

The candidate fails physical verification. D14 copper touches D5, D10, D11 and D13. Eight unrelated copper pairs have zero edge clearance. The all-layer Gerber check detected 17 short locations. The new RAM-side via overlaps D5 on the bottom layer. The CPU-side via overlaps D11 on bottom and D13 on top. The complete branch retains its previously verified D14 path.

For reproduction, assemble 66b9fc9 and run the study builder with `--d14-south BASELINE.json TRIAL.json`. Run the copper contact checker with `--clearance-mm .102`, the via-clearance checker, and `tsci check shorts TRIAL.json --mode gerber --layer all` on the trial. The placement, ball assignment and both strobes are identical to the baseline.

[Timing and residuals](timing.csv) · [Copper contacts](clearance.csv) · [Via-edge findings](via-clearance.csv) · [Gerber shorts](gerber-shorts.txt)
