# Unterminated ADDR/CTRL and CK: analysis for TI's Figure 7-48 topology

SPRS717L section 7.7.2.3.3.9 allows one DDR3 device without VTT termination (Figure 7-48, the topology of this
module) and asks for an analysis with the actual board. Two levels of analysis are here.

## Trace impedance (`zo_fd.py`, `zo_results.txt`)

2D finite-difference field solution of the outer DDR trace as routed: 0.102 mm wide, 35 um copper, 15 um solder mask,
over the layer-2 ground. JLCPCB publishes no impedance-controlled 1.0 mm 6-layer stack, so every prepreg they use is
computed:

| L1-L2 prepreg | Z0 single | CK pair (0.1 mm gap) Zdiff |
|---|---|---|
| 1080, 0.0764 mm, er 3.91 | 56.1 ohm | 91 ohm |
| 3313, 0.0994 mm, er 4.10 | 63.3 ohm | 97 ohm |
| 2116, 0.1194 mm, er 4.16 | 69.1 ohm | 101 ohm |
| 7628, 0.2104 mm, er 4.40 | 88.8 ohm (outside TI's 50-75) | 109 ohm |

**Order note: the L1-L2 and L5-L6 prepreg must be 1080 or 3313 (2116 acceptable), not 7628.**

## Coupled-line simulation (`addr_si2.py`, `results2.txt`)

- worst net (A1): 42.31 mm, of which 18.07 mm at the 0.1 mm minimum gap between two aggressors (the 1250-mil
  allowance), the rest at 4w; L and C matrices from the field solver for each prepreg;
- lossy lines (skin effect at 400 MHz; dielectric loss left out, which under-damps: conservative), the two through
  vias per net, processor ball/package capacitance, memory package (1.5 nH, 0.5 pF) and die input (1.5 or 3.0 pF);
- DDR3-800, PRBS7 on the victim, aggressors switching against it, with it, and independently;
- judged at the memory ball against JESD79-3-1A DDR3L address/command levels: AC135 reached with setup time to
  spare, DC90 held, overshoot/undershoot <= 0.4 V; CK/CKn against VIHdiff(AC) 0.27 V.

Result: every case passes with the processor's ADDR/CTRL/CK output impedance at 40 ohm or weaker, on 1080, 3313
and 2116. 34 ohm also passes on 1080 and 3313; on 2116 it overshoots to 0.45 V. Worst valid time 0.42 ns of the
2.5 ns bit; levels never ring back through DC90. **Bring-up setting: DDR command/address drive 40 ohm or weaker.**

`addr_si.py` / `results.txt` is the earlier first-order version (single lossless line).
Limits: no IBIS models (the driver is a ramped source behind its output impedance, which is how TI specifies the
AM335x DDR drive settings). It supports the topology; it does not replace a measurement on the first boards.
