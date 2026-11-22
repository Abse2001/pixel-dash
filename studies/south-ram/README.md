# RAM placement trial, 1.5 mm south

This experimental layout translates the RAM center from (−65.0, 15.15) to (−65.0, 13.65) mm, carries its local fanout and reshapes the 50 saved signal paths between packages. Native build, Gerber and plated drill export completed. Keep the routed D15 board as the working baseline.

| Measure | D15 baseline | Trial | Limit |
|---|---:|---:|---:|
| D12 planar length | 23.6978 mm | 24.0725 mm | Trial joint range 22.2614–22.8587 mm |
| D14 planar length | 23.3728 mm | 23.7479 mm | Same range |
| D12 worst modeled skew | +9.5717 ps | +10.6658 ps | ±3.6633 ps |
| D14 worst modeled skew | +7.6971 ps | +8.7931 ps | ±3.6633 ps |
| DQS1 intra-pair planar mismatch | 0.0900 mm | 0.0713 mm | TI 0.127 mm |

D12 and D14 each traverse two full-depth vias totaling 2.840 mm on the nominal 1.491 mm reference build. Mixed flight estimates are 157.6184 ps and 155.7458 ps respectively. The larger signed skews above use the fully coupled strobe scenario. The two data nets exceed the model limit by 7.0024 ps and 5.1298 ps respectively. Their worst peer mismatches exceed TI’s 0.635 mm by 0.9904 mm and 0.6658 mm. These are reference-stack estimates. Component, process and receiver timing margins remain open.

The copper audit found 67 unrelated pairs below 0.102 mm. The via-edge audit found 38 unrelated-net pairs below 0.1524 mm. Drill spacing passed. Exported full-width reference geometry had 29 signal/layer findings. Drilled CAM joined unrelated mapped nets. This also prevents an independent MMC0 pass and disqualifies the placement from adoption.

[All 50 timing rows](timing.csv) include previous and trial lengths, via counts and depths, signed flight-time scenarios, nominal placement windows, TI mismatch limits and residuals. See [copper clearance](copper-clearance.csv), [via clearance](via-clearance.csv) and [reference coverage](reference.csv) for locations.
