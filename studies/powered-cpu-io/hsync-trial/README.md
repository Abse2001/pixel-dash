# HSYNC trial on the powered data-enable checkpoint

U1.R5 could reach J_LCD pin 11 when the SYSBOOT7 sense route was temporarily lifted. With that route installed, drilled CAM joins HSYNC to LCD D7 on the top layer near (−49.52, 9.34) mm. There are two raster reference gaps, 0.0253640 mm² on L2 and 0.0237580 mm² on L3. Both the drill-spacing and separate via-edge checks pass. A bounded 0.020 mm search for two top-layer launch paths with fixed downstream endpoints found no clean pair. The powered design retains its original SYSBOOT7 copper and its verified data-enable route. HSYNC is open.

The isolated route file is a fragment for the powered assembly's system-paths input at 7ac53c5. The committed production input excludes this trial. [Route](trial-route.json) · [Drilled short](drilled-check.txt) · [Copper](copper.csv) · [Raster return](reference.csv)
