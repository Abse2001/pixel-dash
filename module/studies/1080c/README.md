# Common DDR impedance and stack sensitivity

TI Table 7-62 permits one nominal between 50 and 75 Ω and ±5 Ω about that nominal for every segment. Across the previous two uniform meshes the 47.005–55.090 Ω range gives a best common nominal of 51.0475 Ω and 0.9575 Ω model headroom. Those endpoints represent two numerical meshes at the published dimensions.

The candidate retains 0.102 mm inner traces and widens outer traces to 0.115 mm. The interface-aligned electrostatic mesh places nodes exactly at foil edges and material interfaces, including the core and prepregs on the far side of an inner trace. The symmetry plane has zero normal field. The other boundaries are ideal AC grounds. Only the full-width uniform cross-section is modeled. The actual L3/L4 reference discontinuities, coupled strobe and clock geometries, outer BGA launches, bends and barrels require separate extraction.

At 0.0025 mm mesh the nominal outer and inner sections are 50.337 and 46.650 Ω. The nominal common 50 Ω window is 45–55 Ω. For sensitivity, vary finished width by ±0.008 mm, pressed dielectric thickness by ±5%, foil thickness by ±10%, and relative permittivity by ±4% together in the two adverse directions. These bounds are engineering assumptions. Mask thickness is held fixed. Across both meshes the proposed geometry reaches 42.658–54.707 Ω. The low inner corner misses 45 Ω by 2.342 Ω. Increasing the outer width further cannot recover the inner corner. Any subsequent stack change must preserve coverage and pass the separate delay and receiver checks on routed copper.

Run `python module/studies/1080c/corners.py` with NumPy and SciPy to reproduce corners.csv. This branch holds a cross-section study. The accepted PCB still has its original widths.

[TI AM335x datasheet, Table 7-62](https://www.ti.com/lit/ds/symlink/am3354.pdf)
