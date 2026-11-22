# Byte-lane breakout trial

This study reserves the clock pair, both DQS pairs, B4, B5, C5, N5,
P5, three new SYSBOOT sense traces and the capacitor returns before
placing any data or command lines. The production board and the
forty-link RTC study remain on their own branches.

Six newly routed data signals give 12/50 verified ball pairs. The
drilled export retains RTC regulator isolation, seven physical SYSBOOT
straps, 21/21 DCDC4 CPU and USB loads, the ground network and the
seven MMC0 connections. All twelve DDR signals pass full-width reference.
The conservative DDR envelope, routed LCD and SD references, 0.102 mm
copper, 0.1524 mm via-edge, drill spacing and native Gerber shorts pass.

D5 now measures 20.018 mm with two traversals, down from 26.383 mm
with two traversals in production. D0 and D3 use reserved length for
19.927 and 19.912 mm with two traversals each. D2 is still early.
D1 and D7 exceed their planar windows. Across the populated part of
byte 0, the worst odd-mode-strobe delay difference is 20.792 ps.
The independent isolated-strobe estimate is 23.866 ps. Both exclude
package and launch delay. The unpopulated links are listed in
`deferred.json`. This partial layout is unsuitable for fabrication.
