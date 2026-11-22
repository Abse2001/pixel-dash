# Pixel Dash byte 0 routing study

All eight byte 0 data balls, DQM0, DQS0 and DQSn0 connect through the exported Gerbers and plated drill spans. All eleven pass the TI board matching checks and the project's three stack-delay scenarios. The data/mask peer spread is 0.180 mm and the largest mismatch to either strobe is 0.475 mm (limit 0.635 mm). Strobe pair mismatch is 0.111 mm (limit 0.127 mm). The placement-based routing ceiling is 20.600 mm. The separate modeled skew limit is ±3.663 ps. See byte0-timing.csv for individual lengths, barrel depths, delays and residuals.

Run bun run build with the project dependencies and Python geometry dependencies. The study overlays the channel on the populated board and postpones conflicting copper. dist/index.circuit.json contains the result, and dist/deferred.csv identifies the removed physical objects. All components and schematic connections remain present. The complete routed fallback is bf75444.

The export has 36 of 50 distinct DDR connections with no shorts between mapped lands. All eleven upper-byte nets plus A1, CK and ODT are open. The exported full-width reference check passed for all 36 connected signals. The 0.102 mm copper, 0.1524 mm via-edge and drill-spacing checks each reported zero findings. System opens remain. This branch is a timing study.
