# Common DDR impedance and stack sensitivity

TI Table 7-62 permits one nominal between 50 and 75 Ω and ±5 Ω about that nominal for every segment. Across the previous two uniform meshes the 47.005–55.090 Ω range gives a best common nominal of 51.0475 Ω and 0.9575 Ω model headroom. Those endpoints represent two numerical meshes at the published dimensions.

The candidate retains 0.102 mm inner traces and widens outer traces to 0.115 mm. The interface-aligned electrostatic mesh places nodes exactly at foil edges and material interfaces, including the core and prepregs on the far side of an inner trace. The symmetry plane has zero normal field. The other boundaries are ideal AC grounds. Only the full-width uniform cross-section is modeled. The actual L3/L4 reference discontinuities, coupled strobe and clock geometries, outer BGA launches, bends and barrels require separate extraction.

At 0.0025 mm mesh the nominal outer and inner sections are 50.337 and 46.650 Ω. The nominal common 50 Ω window is 45–55 Ω. For sensitivity, vary finished width by ±0.008 mm, pressed dielectric thickness by ±5%, foil thickness by ±10%, and relative permittivity by ±4% together in the two adverse directions. These bounds are engineering assumptions. Mask thickness is held fixed. Across both meshes the proposed geometry reaches 42.658–54.707 Ω. The low inner corner misses 45 Ω by 2.342 Ω. Increasing the outer width further cannot recover the inner corner. Any subsequent stack change must preserve coverage and pass the separate delay and receiver checks on routed copper.

Run `python module/studies/1080c/corners.py` with NumPy and SciPy to reproduce corners.csv. This branch holds a cross-section study. The accepted PCB still has its original widths.

[TI AM335x datasheet, Table 7-62](https://www.ti.com/lit/ds/symlink/am3354.pdf)

## Alternate published 1.6 mm build

On JLC06161H-1080 the L2–L3 and L4–L5 separations are 0.550 mm and the L3–L4 separation is 0.2104 mm. The 0.230 mm inner and 0.115 mm outer trial gives 47.650–54.367 Ω inner and 46.241–54.707 Ω outer, across the same two meshes and model corners. A common 50.5 Ω nominal allows 45.5–55.5 Ω and leaves about 0.74 Ω of modeled margin. At nominal dimensions the finer mesh gives 50.972 Ω inner and 50.337 Ω outer. These are isolated uniform line sections with ideal AC reference planes and assumed process bounds.

Applying those widths to the actual module from a4d726c exposes a layout failure. KiCad 9 reports 212 copper clearances, 75 hole clearances, seven shorting items, two edge clearances and 38 unconnected items after refill. Independent Gerber and drill reconstruction joins A2, A5, A11, CASn and ODT on a single copper island. Full-width ground projection outside all launch exclusions misses 0.0053 mm² on L4. The area of DDR projection without connected L3 DDR supply copper increases to 93.4167 mm². Those figures come from the widened export. The accepted board keeps its original copper widths.

Receiver setup and hold **fail qualification** on this layout. The five joined inputs cannot receive independent command waveforms at any sampling phase. Propagation estimates for isolated uniform sections cannot recover a valid command bus. Routing must provide lateral spacing and continuous references before extracting the coupled clock, strobes, launches and individual receiver waveforms.

To reproduce the field sweep run `python alternate.py` in this directory. To reproduce the physical trial, check out module revision a4d726c in a separate directory, copy its KiCad project settings beside the output board, and run `/usr/bin/python3 apply-alternate.py path/to/module/pixel-dash-module.kicad_pcb trial/pixel-dash-module.kicad_pcb`. Run KiCad DRC, export the six copper layers and plated drill file, and use that revision's extract-geometry.py and check-cam.py. The ordinary CAM gate fails on the joined nets.
