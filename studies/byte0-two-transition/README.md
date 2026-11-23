# Powered byte-0 two-transition topology

The reference is the 45-link board at e5fd49f. D2, D3 and D4 each have four L1–L4 transitions and 5.6800 mm total barrel. With the present DQS0 pair, the minimum planar strobe-match length of 19.7115 mm exceeds the four-transition modeled upper window of 17.1823 mm. Two full-depth transitions reduce total barrel to 2.8400 mm and give a joint project window of 19.7115–20.4313 mm. TI’s data-to-strobe matching limit is 0.635 mm. The separate stack-dependent worst signed skew screen is ±3.6633 ps.

| Signal | Routed planar mm | Estimated flight ps | Worst signed skew ps | Model excess ps | Worst strobe mismatch mm | TI excess mm |
|---|---:|---:|---:|---:|---:|---:|
| D2 | 20.2383 | 154.2428 | +21.2937 | 17.6304 | 0.1082 | 0 |
| D3 | 25.9353 | 187.1085 | +54.1593 | 50.4960 | 5.6032 | 4.9682 |
| D4 | 21.7026 | 162.6904 | +29.7413 | 26.0780 | 1.3706 | 0.7356 |

With all three lifts and every other route fixed, all nine same-byte pin assignments are disconnected in an optimistic two-transition screen. Any path with planar length ≤20.4313 mm lies in the ellipse whose foci are its two package lands and whose major diameter is 20.4313 mm. The two top launch regions must overlap legal via landings in a common L4 component inside that ellipse. The check circumscribes the ellipse, relaxes metal and hole clearance by 2 µm, and ignores plane coverage, routing-envelope restrictions, mutual interference and precise path length within the ellipse. Even those relaxed conditions fail. This conclusion applies to the fixed placement, center-land endpoints, 0.102 mm traces and 0.30/0.15 mm full-through vias. It does not exclude a different via construction, package placement or coordinated neighboring change.

Freeing D0 alone in addition to the trio restores optimistic access in all nine pairings. Freeing A1 instead also restores access in all nine. Neither result proves that four or five simultaneous traces fit. In the A1 study, sampled same-pin D2 paths reached the RAM with only A1 displaced. The sampled return search for A1 then failed to find a two-transition path. The 45-link copper is retained.

Run the check on an assembled board from e5fd49f. Add `--also-move DDR_D0` or `--also-move DDR_A1` to reproduce the neighbor screens.

```sh
python checks/screen-ddr-two-transition.py dist/index.circuit.json --bits DDR_D2 DDR_D3 DDR_D4 --limit-mm 20.4313
```

[Fixed-neighbor screen](fixed.csv) · [D0 movable](D0.csv) · [A1 movable](A1.csv) · [Independent sampled route lengths](sampled-two-via-lengths.csv)
