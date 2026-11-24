# Unterminated ADDR/CTRL and CK: analysis for TI's Figure 7-48 topology

SPRS717L section 7.7.2.3.3.9 allows one DDR3 device without VTT termination (Figure 7-48, the topology of this
module) and asks for an analysis with the actual board. `addr_si.py` is a first-order one: ramped driver behind an
output resistance, lossless 42.3 mm line, capacitive receiver (two dice plus ball and via), pseudo-random data at
DDR3-800 timing, judged at the memory ball against the DDR3L address/command levels (AC135 / DC90, 0.4 V
overshoot amplitude). Results: `results.txt`.

What it shows:

- The levels are reached about 0.25-0.4 ns after the edge arrives and never ring back through the DC level, for
  every line impedance between 50 and 75 ohm and every driver setting tried.
- Overshoot is the only thing that depends on the set-up: it stays inside 0.4 V when the processor's ADDR/CTRL/CK
  output impedance is about 40 ohm or more on a 60 ohm line (34 ohm is enough at 50 ohm; a 75 ohm line wants 40-48).
  The AM335x DDR drive strength is a register setting (`ddr_cmdX_ioctrl`), so this is a bring-up setting, not a
  board change. Order the board with 0.102 mm outer traces as drawn (about 60 ohm over the 0.1 mm prepreg of JLCPCB's
  1.2 mm 6-layer stack; TI Table 7-61 asks for 50-75 ohm).

Limits of this analysis: no IBIS models, no losses, no crosstalk, no package model. It supports the topology; it
does not replace a measurement on the first boards.
