# Four-command CPU breakout

A3, A5, A6 and WEn share the CPU launch zone. The routing search retained the downstream paths past X = −54.5 mm and assigned all four launches together. A small WEn corner cut shortened its path. All 37 populated-board DDR connections survive the exact Gerber and drill checks. The 13 open connections are identified by name in exact.log. The 36-link fallback remains at 618d9c6.

| Command | Prior length mm | Current length mm | Contacted depth mm | Flight ps | CK skew ps | Excess mm |
|---|---:|---:|---:|---:|---:|---:|
| A3 | open | 38.23341 | 5.30 | 270.201 | +33.731 | 0 |
| A5 | 37.53490 | 37.21347 | 5.30 | 263.668 | +27.197 | 0 |
| A6 | 36.11105 | 36.67605 | 7.76 | 279.092 | +42.622 | 0 |
| WEn | 40.53557 | 40.50792 | 2.84 | 270.856 | +34.385 | 1.81794 |

The project window is 36.14999–38.68999 mm. timing.log gives the layer spans, estimated arrival and residual for every connected command. Both frozen bytes and CK/CKn retain their exact copper. Full-width DDR and MMC0 reference coverage passes, as do the scoped DDR and MMC0 supplies, class spacing, 0.102 mm copper, 0.1524 mm via-edge, and drill spacing. The all-trace check matched 5,522 strokes against CAM.

The outer-layer four-width setback screen falls from 25 to 24 findings. The broader envelope retains 57 findings. Compared with 618d9c6 the area outside nominal via reliefs rises from 2.815 to 10.159 mm² on L2 and from 84.781 to 92.737 mm² on L3. These figures include channel clearances on the inner signal routes. Both D14 ground-return path measurements to C_DDR40 increase, including 6.5246 to 7.7132 mm. The existing bypass remains fitted. The study leaves loop impedance, actual receive setup and hold, unconnected nets and manufacturing release open.
