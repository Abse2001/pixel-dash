# Northward RAM and boot escape study

The RAM, its local bypass and reference fanout move 1.0 mm in +Y.
The CPU remains fixed. This study reserves the reset, power, ground and
boot routes before rebuilding either data lane. The only retained DDR
signals are CK and CKn. The two package-to-package clock paths and their
reference pass on the export. All other 48 memory signals are open.

The drilled export decodes all sixteen SYSBOOT straps as
`0100000000010111` (0x4017). R_SYSBOOT1 moved to (−35.52, 5.28) mm
at 180°. Its bias joins the sequenced high strap rail. A dedicated route
connects its sense land to R2. The populated courtyards, native Gerber
shorts, rail isolation and all sixteen sense-to-bias isolation checks pass.
Both RTC domains, reset, wake, hold, 21/21 DCDC4 CPU and USB supply
lands, all grounds, the seven MMC0 links and the card supply pass.
The crystal load capacitor and two strap resistors have new local ground
returns. Two controller traces move around the relocated RAM fanout.
VREF_CA clears the opposite zero-ohm resistor land.

The 0.102 mm copper screen, independent 0.1524 mm via-edge screen,
drill spacing, outer DDR envelope and connected full-width references
for the routed clock, SD and LCD all pass. The LCD still has 6/29
end-to-end links. This branch is a placement and escape study. The
production board retains 50 DDR links and its buffered DDR regulator.
