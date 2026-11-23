# RTC reset and the powered command escape

The primary board is unchanged by these trials. Both use the powered D12 assembly as their parent.

**B4.** Removing A6 and A8 entirely still leaves B4's center 0.654024 mm inside the recomputed protected DDR margin, with zero legal launch-center area. Considering only the fixed CPU and RAM DDR lands leaves 0.008273 mm². A separating-axis screen at 0.1° increments needs at least six movable signal geometries at its best sampled direction, A13, A2, A6, A8, BA2 and CKE. This is a necessary geometric screen for a launch, with no via or timing credit. [B4 bounds](startup.txt) · [Fixed lands](fixed.txt) · [Sampled direction](startup-axis.txt)

**B5.** Lifting A6 and A8 allows a physical U_PMIC.PGOOD_BU to U1.B5 reset path. The 43-link export passes net isolation, the DDR envelope and references, copper, via-edge and drill spacing. Widening the command routing region restores both A6 and A8. The resulting 45-link drilled export verifies B5 reset and all prior DDR links together and passes individual full-width DDR reference, copper and drill checks. However the reset trace intrudes by 0.044295 mm² into the DDR convex hull and by 0.273705 mm² into the hull plus prescribed margin. B5 has zero launch area with both restored paths held fixed.

**Restored command timing.** A6 changed from 25.3500 mm and four through-transitions to 28.3944 mm and two. Its modeled flight is 182.5512 ps, +2.7112 ps to the CK-pair mean. A8 changed from 28.7187 to 25.6098 mm with two through-transitions. Its modeled flight is 166.4870 ps, −13.3530 ps to CK. Each new route spans 2.840 mm of barrel in the reference model. They miss the 28.5500–31.0900 mm project command window by 0.1556 and 2.9402 mm respectively. Receiver waveform setup/hold remains open. A new B5 launch search with both commands held fixed found no legal in-pad start. These trials remain outside the primary design.

[43-link reset CAM](cam-43.txt) · [45-link reset CAM](cam-45.txt) · [45-link envelope finding](envelope-45.csv) · [All-net timing](timing-45.csv) · [Reset route](rtc-reset.json) · [Two command routes](restored-commands.json)

An additional search reserved a directional B5 launch before command routing. A two-transition sweep at 3° steps gave no paired restoration. Around the 15° and 18° directions where both CPU lands could reach via sites, a 0.75° sweep tested mixed two- and four-transition command topologies. None restored both signals within the sampled launch constraints. [Four-transition search](four-transition-search.txt)
