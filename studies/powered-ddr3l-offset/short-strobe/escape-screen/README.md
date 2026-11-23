# D2 escape with the west strobe pair installed

The four-way assignment in the trial file preserves all byte-zero lands and keeps the placement limit at 20.600104 mm. CPU N1 (D2) uses RAM F8, with two 1.420 mm transitions. The 20.3296 mm route would arrive at 136.0257 ps with worst signed skew +1.9084 ps against ±3.6633 ps when electrically isolated.

**Rejected on copper.** Restoring all installed neighbors produced a top-layer short to D14 near (−63.57, 9.88) mm and a bottom-layer gap to D12 of 0.0738568 mm against 0.102 mm. The RAM-side D2 via edge is 0.1171545 mm from D12 against 0.1524 mm and cuts 0.0087971 mm² of its bottom reference. A scan of nearby alternative landings found 13 clearance-compatible samples within the bounded grid. None joined both existing approaches inside the length window. Sampling 84 alternative via pairs for each of the two accessible assignments with the neighbors fixed found shortest paths of 21.2437 and 21.1410 mm, both over the project cap. These are search results and do not establish a global length bound.

The powered board and the 40-link west checkpoint retain their verified copper. [Trial mapping and path](D2-trial-mapping.json) · [Fixed-neighbor paths](fixed-neighbor-search.txt) · [Drilled short](drilled-contact.txt) · [Copper](unrelated-copper.csv) · [Via edge](via-edge.csv) · [Reference](full-width.csv)
