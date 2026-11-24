# JLC06161H-1080B on the routed six-layer module

**Decision: retain JLC06161H-1080 on the accepted board.** This study uses the 3ae2502 artwork and its 0.102 mm DDR routes. The alternative fits the nominal single-ended impedance target. Across the wider etch sensitivity case there is no common TI nominal impedance that fits both layers. Fabrication and receiver qualification remain open.

## Construction and process assumptions

JLCPCB's public 1.6 mm JLC06161H-1080B entry lists 0.035 mm outer copper, 0.0152 mm inner copper, 0.0764 mm outer 1080 prepreg, and 0.100 mm L2–L3 and L4–L5 cores. Between L3 and L4 it lists 0.2104 mm 7628 prepreg, 0.700 mm core and 0.2104 mm prepreg. L2 and L5 carry ground. The artwork comparison represents the middle sandwich as a single 1.1208 mm spacing. The field model resolves its three dielectrics separately. [JLCPCB stack catalog](https://jlcpcb.com/impedance)

The model assumes relative permittivities of 3.91 for outer prepreg, 4.4 for 7628 and 4.6 for core, with fixed mask dimensions. The low/high impedance cases vary pressed spacings by ±5%, foil by ±10% and dielectric constant by ±4%, jointly in adverse directions. The tight case varies finished trace width by ±0.008 mm. The wide case uses ±0.0204 mm. These are engineering sensitivity cases. Supplier limits for these quantities on this build are unverified. Sidewall taper, frequency dependence and stitching inductance are outside the model.

## Results

| Isolated single-ended sections | Impedance range across both meshes | Common nominal allowed by TI Table 7-62 |
| --- | ---: | ---: |
| Nominal construction | 52.952–53.552 Ω | 50.000–57.952 Ω |
| Tight etch and material corners | 48.6485–58.0909 Ω | 53.0909–53.6485 Ω |
| Wide etch and material corners | 46.3444–61.2457 Ω | Empty |

The best-centered tight-case nominal is 53.3697 Ω, leaving 0.2788 Ω to the ±5 Ω boundary. The wide case exceeds the permitted 10 Ω total spread by 4.9013 Ω. The outer clock odd-mode calculation uses a 0.1505 mm nominal edge gap measured at the midpoint of a long bottom-layer run, with center spacing held fixed as the traces etch. The pair fans apart elsewhere. The modeled nominal odd-mode impedance is 46.9015 Ω on the finer mesh. [TI AM335x datasheet](https://www.ti.com/lit/ds/symlink/am3354.pdf)

The candidate has 1.5694 mm between the centers of its outer foils, with nominal L3 and L4 depths of 0.2167 and 1.3527 mm below the L1 center. flight.csv uses the actual contact layers of every via on all 50 links. The screening calculation retains the accepted barrel delay of 6.600 ps/mm and its existing strobe/clock coupling correction. Both byte groups and clock pair pass the project flight-matching limits across the five modeled corners. Actual package flight, individual discontinuities, coupling at bends and return-current loops require extraction.

receiver.csv intersects modeled command capture windows for 25 commands. Each stack corner includes nine DRAM rail/VREF combinations, 32 edge/load cases and four combinations of uniform CA and clock impedance. It uses the TI IOCTRL 0x318 typical source fixture and the stack-specific flight times. The CA line is evaluated at outer and inner impedances, and the clock at outer isolated and odd-mode impedances. The common capture interval across all cases is 746.741–1943.416 ps. An intersection means the modeled receiver permits a sampling phase in that interval. The programmed controller launch phase, CPU rail and driver corners, distributed changes in impedance, and read/write DQ capture remain unqualified.

Fresh KiCad 9 copper and plated-drill exports reproduced the accepted pad islands and clearance results: 50/50 DDR signals, 18/18 DRAM supply balls, 7/7 CPU DDR supply balls, 183/183 returns, zero native DRC violations and zero 0.1524 mm via-edge findings. There are still 23 intended opens. Full-width checked ground references pass outside the launch exclusions. The existing 45.4482 mm² DDR projection without connected L3 supply remains a blocker. A stack change alone cannot add missing copper.

## Reproduction

From this directory, run with the same Python dependencies as the module verification and TI's SPRM552C IBIS archive:

```sh
OPENBLAS_NUM_THREADS=1 python screen.py > /tmp/1080b-corners.csv
diff -u corners.csv /tmp/1080b-corners.csv
python flight.py ../../timing.csv > /tmp/1080b-flight.csv
diff -u flight.csv /tmp/1080b-flight.csv
OPENBLAS_NUM_THREADS=1 python receiver.py "$TI_IBIS_ARCHIVE" > /tmp/1080b-receiver.csv
diff -u receiver.csv /tmp/1080b-receiver.csv
./verify-artwork.sh
```
