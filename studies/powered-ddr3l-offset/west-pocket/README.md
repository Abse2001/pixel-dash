# D5 tuning pocket with the D7 trunk reserved

At the west placement, the known 21.271217 mm D7 reservation and a D5 pocket can each clear the installed D0/DQM0 and strobe screens. Both routes use two full-depth transitions totaling 2.8400 mm. The placement and installed-peer joint window is 20.9125–21.5729 mm. The threshold of ±3.663315 ps is a reference-stack flight model. The TI planar data matching limit is 0.635 mm.

| Candidate | Prior sampled length (mm) | Current (mm) | Flight (ps) | Worst signed skew (ps) | Model headroom (ps) | Largest mismatch to D0/DQM0 (mm) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| D5 to former RAM DQ2 | 19.869278 | 21.169495 | 140.870818 | −2.013163 | 1.650152 | 0.377984 |
| D7 to former RAM DQ3 | 21.561181 | 21.271217 | 141.457650 | +1.922722 | 1.740593 | 0.276262 |

The selected D5 pocket holds both D7 via sites and its bottom-layer trunk available. Five alternative RAM DQ destinations were routable for D5 with those reservations, yielding nine sampled tuning pockets in the interior length band. Independent direct copper checks found no spacing violations against installed objects on either example. The two examples overlap each other on the top side. In the CPU launch they coincide for 3.735 mm. Their RAM launches intersect twice. The two candidates cannot be installed together.

Holding the complete D7 fixed, each of the six remaining legal D5 RAM assignments has some reachable landing area on each end. None shares a connected bottom corridor between the two landing regions. Reversing the reservation with the tuned D5 fixed gives the same result for all six D7 assignments. This continuous polygon check uses the pinned envelope, full-width reference, obstacle guards and each assignment’s length ellipse. The centerline passage at x = −50.8 mm on the shared CPU launch is 0.132075 mm wide against 0.204 mm required for two 0.102 mm traces separated by 0.102 mm of copper clearance. The two launches require coordinated changes. No coupled timing or full-byte pass is credited.

[Per-route measurements](measure.txt) · [D5 pocket](d5-pocket.json) · [Reserved D7](d7-reservation.json) · [Continuous landing areas and common corridor counts](continuous.txt) · [CPU passage widths and bounding objects](throat.txt)
