# Pixel Dash

AM3354 handheld with a 1 GiB Micron DDR3L, four-layer HDI board and the existing LiPo tub. Engineering development only.

The retained handheld was extracted from checkpoint `5b7d96d`. The coupled DDR channel starts at `611f7d9`. The original dual-RP2350 hardware and historical routing branches are separate fallbacks.

The first production checkpoint removes 91 old processor and support designators. The peripheral snapshot omits ground pours pending integration. Nine local trace edits eliminate the nine 6 mil via-to-unrelated-trace findings on this retained subset. Future work on the integrated board must rerun the audit including the AM3354 and memory.

`python production/build-retained.py /tmp/retained.circuit.json` materializes the retained copper. Run `python checks/audit-via-clearance.py /tmp/retained.circuit.json` with Shapely 2.
