# West CKE route

CKE changes from 34.9054 to 34.8683 mm. Its four L1–L4 transitions total 5.680 mm of barrel travel. Nominal flight changes from 238.8571 to 238.6432 ps and arrival relative to CK from 47.4947 to 47.2808 ps. The project window is 30.150–32.690 mm. CKE is 2.1783 mm above it. Receiver setup and hold remain open.

All other rows of the per-net timing report are identical. The export retains 40 distinct nets, full-width DDR reference, a clean return-plane envelope, local supplies and returns, MMC0 and raster references, and zero unrelated copper, via-edge, drill-spacing or same-net contact findings. A separate bounded search for a two-transition bypass found no common top or bottom reference corridor between the three tested pairs of existing route sections.

[CKE limits and receiver requirements](cke-comparison.csv) · [All timing rows](all-signals.csv) · [Geometry](geometry.txt) · [Drilled CAM](drilled-cam.txt) · [Assembled study](board.circuit.json.gz)

The RAM-side CKE through via moved from (−71.2500, 19.8700) to (−71.2220, 19.8020) mm. The return-aware search reserved each blind capacitor via's entire land plus the through-via antipad. The selected export retains all 71 local terminals through their 70 adjacent-plane vias, including C_DDR8. A further joint two-transition CKE/A6 search on a 0.035 mm grid found no individual legal path inside 32.690 mm with the other signals and rails fixed. [Revised CKE sections and vias](cke-route.json)
