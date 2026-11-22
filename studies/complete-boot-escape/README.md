# Boot escape study on the 50-link board

This build connects all 21 DCDC4 CPU lands through the added P6–P5–N5 copper. CPU V2 reaches the low SYSBOOT12 resistor, bringing the physical strap count to five. The new strap uses L1–L4, L2–L3 and L1–L2 drills. All 50 DDR links and seven MMC0 signals remain distinct. The whole-board 0.102 mm copper, 0.1524 mm via-edge, hole spacing and full-width DDR/MMC0 reference checks pass. The copper contact and return results are reproducible with the normal build. The [CAM land report](cam.txt) lists remaining opens.

**The common DDR envelope fails.** The N5/P5 power traces enter the outer-layer reserved region. SYSBOOT12 stays outside the convex hull but enters its 0.408 mm margin. The earlier SYSBOOT12 path also interrupted the MMC0 DAT3 and DETECT returns. The saved route restores both. [Exported envelope violations](ddr-envelope.csv) · [Raster reference findings including straps](raster-reference.txt) · [Provisional hot-load model](hot-rail.txt)

The minimum required envelope with the bytes and CK/CKn locked is the convex hull of those nets' L1/L4 copper and the DRAM footprint copper, expanded by four trace widths. The N5 and P5 land centers lie 0.2176 and 0.2016 mm inside even that reduced boundary. Their copper radius is 0.179997 mm, so neither land can touch a new trace or via wholly outside it. Moving command routes alone cannot expose these pads. The closest hull edge at N5 follows the D12 bottom trace. At P5 it joins D12 bottom copper to D1 top copper. Signed distances to the outside boundary are positive in the [land measurements](pad-centers.csv).

48969b3 preserves all 50 links and a clear common envelope with N5 and P5 open. This boot escape is a separate electrical study under fabrication hold.
