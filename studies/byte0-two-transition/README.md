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

## Simultaneous landing bound on powered d8461d7

The two-transition data search on the populated 45-link board uses a 20.4313 mm upper limit, 0.30 mm full-through lands, center launches and every same-byte permutation among the lifted bits. Removing A1 completely allows any subsequent four-transition A1 geometry. D0 remains fixed. The RAM-side landing regions of two different data conductors have a maximum possible center spacing of 0.233563 mm in every permutation. Two 0.30 mm lands with the required 0.102 mm copper gap need 0.402000 mm. The deficit is at least 0.168437 mm even before attempting to insert A1. A separate sampled four-transition A1 restoration with its original outer launch sections and a replacement D2 installed found zero common L1 bridge options. The geometric data bound is independent of that sampling result and of the choice of A1 launches.

The calculation intersects each terminal's L1 land region with L4 components accessible to its mate, then bounds the distance between distinct vias using their enclosing boxes. It ignores return-plane obstacles, exact path cost and mutual trace interference. The individual two-transition screen can therefore pass while simultaneous placement is impossible. This result applies to the published center-launch and full-through construction.

In the independent D0 fallback, A1 is fixed and all four data nets move. All 24 assignments survive this necessary spacing test. Survival is inconclusive. The production D0 route remains in place.

Run the original command on d8461d7 with the additional flags `--also-move DDR_A1 --packing`. For the D0 fallback use `--bits DDR_D0 DDR_D2 DDR_D3 DDR_D4 --packing` with the same length limit. [A1 released, six permutations](powered-packing-A1.csv) · [D0 released, 24 permutations](powered-packing-D0.csv)

With A1 fixed and D0 lifted alongside D2/D3/D4, a sampled search across all 16 CPU/RAM combinations produced 425 distinct two-transition routes after deduplication by via position. At most two can coexist in this pool. None reaches the original D3 RAM land within the cap. This search sampled up to 100 via pairs per pairing, prioritizing the shortest straight-line lower bounds before calculating routed lengths. This is a sampled failure, not an impossibility proof for D0. [Per-pair trials and lengths](D0-sampled-pairs.csv)

The installed peers independently constrain the study. At 25.7789 mm, fixed D5 requires a new data trace at least 25.1439 mm long to meet the TI 0.635 mm peer mismatch. That exceeds the 20.4313 mm strobe/model ceiling by 4.7126 mm. D7 at 22.6639 mm misses the joint window by at least 1.5976 mm. An all-installed-peer pass therefore requires changing D5 and D7 as well. This applies even if a new escape solves D2/D3/D4 individually. [Per-peer length intervals](fixed-peer-window.csv)

With D0 held fixed, extending the original study to D5 and D7 still excludes all 120 data assignments on the landing bound. Releasing only the existing D6 copper in addition makes all 120 pass this necessary test. Adding the open D1 terminals while leaving D6 fixed excludes all 720 assignments instead. D6 occupies relevant routing space despite its own passing skew. A run that must restore D6 alongside D2/D3/D4/D5/D7 allows all 720 assignments through the optimistic screen. [Group results, including full byte permutations](extended-landing-screen.csv)

On a separate repoured copy with A1 and those six data signals lifted, a 0.045 mm routing grid tested all 36 CPU/RAM pairs and eight negotiated assignments. None of the sampled paths into the original RAM D5 land met 20.4313 mm. The largest sampled disjoint subset inside the length window was one route. No new DDR geometry was adopted. This grid result depends on its discretization, reference and obstacle guards and search strategy. The length and skew results on the powered board remain unchanged.
