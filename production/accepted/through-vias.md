## Four-layer through-via target

Use mechanically drilled L1–L4 plated through vias on the cost-reduction branch. Use a 0.20 mm hole with a 0.45 mm land where space permits. For solderable BGA lands requiring via-in-pad, specify nonconductive epoxy fill, planarization and copper cap on both ends (IPC-4761 Type VII). Ordinary off-pad vias do not require that solderable cap. JLCPCB lists four-layer via-in-pad as a paid process. Its capability table also lists a surcharge for 0.15 mm drill at any land diameter and for 0.20/0.25 mm drill below 0.45 mm land. A fixed unit price and an accepted stackup are still open. [JLCPCB published fabrication capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)

The accepted ca10e34 board has 307 L1–L2 blind vias, 44 L3–L4 blind vias and 34 L2–L3 buried vias. It also uses 544 existing 0.15/0.30 mm through vias. All 44 locked data vias and the four clock vias already pass through all four layers. Replacing the HDI stack with a standard four-layer stack changes trace delay, impedance and return geometry even with identical XY routes. The present timing reports use the pinned engineering stack.

The centered-land screen covers 26 endpoints on the 13 open DDR links. At 0.20/0.45 mm, the via land projects beyond every existing CPU and DRAM solder land. At 0.15/0.30 mm, all 13 CPU sites have a physical copper conflict, and four DRAM sites clear the local copper, peer projection and drill screens. Those RAM balls are L7 (A10), N7 (A12), T3 (A13), and T2 (RESETn). Screening preserves existing land geometry. CPU dogbones, displaced neighbors on a separate board or a footprint revision would require their own checks. Nominal containment does not establish registration, finished ring, plated cap quality or supplier acceptance. [Per-ball coordinates and obstructions](centered-through-vias.csv)

The screening script uses a 0.102 mm unrelated-copper rule and a separate 0.1524 mm via-edge-to-unrelated-trace rule. The drill-edge check allows 0.20 mm for through-to-through and requires 0.24 mm for an unrelated existing blind via. It flags overlaps between the new relief and the full width of installed DDR strokes on the referenced layer. This conservative projection check precedes any routed-candidate Gerber comparison. An accepted route requires connectivity, power feed and return continuity, drill and copper spacing, unchanged passing bytes/commands and receiver checks on the final board.

```sh
python checks/screen-centered-ddr-vias.py dist/index.circuit.json
```
