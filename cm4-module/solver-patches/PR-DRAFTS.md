# Draft 1: tscircuit/high-density-repair01

**Title:** Find nearby segment pairs with a sweep instead of testing all pairs

`getRoutePairClearanceViolations` and `findNewProperSegmentCrossings` tested every segment against every other one.
`findAlignedTopologyCandidate` calls `getRoutePairClearanceViolations` for each candidate move: up to 16 per residual crossing.
On dense nodes (thousands of short grid-router segments) this dominated force improvement. The profile showed 41 % of the time in `getRoutePairClearanceViolations`, and one node ran for minutes.

The change:
- Candidate pairs come from an x sweep over segment bounding boxes plus the y test the loops already applied (`getNearbySameLayerSegmentPairs` in `force-improve-segment-helpers.ts`).
- Pairs are sorted back into nested-loop order where order matters (crossing selectors). The set of violating route pairs ignores order, so it skips the sort.
- The same pairs are tested, so the results are unchanged. On a real 6-layer board (AM335x module), hashing the improved routes of 10 nodes gives identical results before and after. Node times: 11.8 s → 6.7 s and 344 s → 189 s.

Repro / test:
- `tests/segment-pair-sweep.test.ts` checks the sweep against brute force (pairs and order) on dense staircase routes.
- Fixture: one node of that board, 37 routes and 5147 points (`fi-node-898.json`, 325 kB).

# Draft 2: tscircuit/tscircuit-autorouter

**Title:** Thin short grid runs and merge coincident vertices in dense force regions

`simplifyPipeline9CollinearRoutePoints` (added for the AM3352 stall, #2681) only collapses straight runs of 64 or more grid steps.
On an AM335x CM4-format board, the A01/A03 staircase output has straight runs of 5–8 steps of 6–25 µm. The regional fallback's force step also leaves clusters of vertices 0.1–1 µm apart: 0 → 318 of 359 segments in one node.
As a result, the simplifier removed nothing (82 519 → 82 519 points), and force improvement ran for over 80 minutes without finishing.

The change only applies in the same dense regions (≥ 4096 points):
- Keep short straight runs' vertices only at trace-width spacing.
- Drop plain interior vertices within 1 µm of their predecessor on the same layer. Vias, layer changes and vertices with extra keys are kept.

Copper is unchanged: every original vertex lies within 4e-15 mm of the simplified route. Dense regions: 11 087 → 5387, 7949 → 5514 and 5147 → 3088 points.
Together with draft 1, node 898 takes 344 s → 56 s.

Also worth a look: `Pipeline9HighDensityForceImproveSolver.validateImprovedSample` rejects the result on 7 of 10 sampled nodes, including every dense one, after the full force work.
