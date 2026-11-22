# Populated DDR breakout trials

The input was the native assembled handheld at c28dc8c. Each path uses board coordinates in millimetres. The first section runs on L1. Successive sections alternate between L4 and L1, with a full-depth via at their shared endpoint. These alternatives are isolated from the board generator.

The byte-1 trials protected the original byte-0 escape and the handheld components, signals and reference planes. Routing orders started with either D8/D9 or the strobe pair. The byte-0 trials reserved a separate set of paths for D7, D5, D3, D4, D2 and both strobe legs. The southern and command trials included A10 and CKE. A separate pin-and-repair pass tried to restore the conductors displaced by promising escapes. The finite pool produced no jointly clear 50-link alternative with a better via topology. Both byte-1 strobe legs also lacked a straight opposite-layer excursion with two legal new via sites in the tested fixed-copper corridor.

Run `python studies/ddr-breakout/check-corridors.py path/to/c28dc8c/index.circuit.json` to reproduce the conflicts against the retained DDR paths. The comparison checks end-ball identity by coordinates, signal-to-signal spacing, via-to-signal spacing, via-land spacing and drill spacing. The accepted routing uses the whole-handheld audits and native Gerbers.

[Candidate paths](trial-paths.json) · [Conflicting nets](corridor-conflicts.csv)
