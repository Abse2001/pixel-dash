# Routing the CM4 module with the tscircuit autorouter

The CM4 module's signal nets are routed by the official tscircuit autorouter (`@tscircuit/capacity-autorouter`,
default pipeline `AutoroutingPipelineSolver`), driven by `autoroute.ts`. This file records how the board is handed to
the solver, every limitation found in the solvers while routing it, the cause, the local fix, and the upstream
repro / fix PRs. Fixes are general (no special cases for this board, no relaxed rules).

## How the board is handed to the solver (`autoroute.ts`)

- **Input** is built from the planner's copper model (`plan.json`, `plan-items.json`), the same model the whole-board
  check (`check.ts`) verifies. The exact input is saved as `autoroute.srj.json` for reproducing issues.
- **Signal layers.** The board has six copper layers; layers 2, 3 and 5 are planes and carry no traces. The solver gets
  `layerCount: 3`: `top`, `inner1` (= board layer 4) and `bottom`. Through vias are obstacles on all three. The plane
  builder (`planes.ts`) fills layers 2-5 around the vias and the layer-4 traces after routing.
- **Obstacles**: every pad, BGA ball, via, the routed DDR block (outer and layer-4 sections), the planner's fixed
  traces (switch nodes, supply stubs) and the mounting holes (`isNonPlatedHole`).
- **DDR spacing.** TI SPRS717 Tables 7-68/7-69 ask other signals to keep four trace widths (0.31 mm here) from DDR copper
  outside the processor's ball field. The DDR obstacles there are given as their copper grown by 0.21 mm, so the
  solver's 0.10 mm clearance adds up to 0.31 mm.
- **Rules**: 0.10 mm traces and clearance, 0.1/0.3 mm vias, via-in-pad allowed (filled and capped vias are ordered),
  0.20 mm to the board edge, 0.20 mm hole to hole.
- **Layer-4 keep-outs** (`KEEPOUT_L4`, obstacles on layer 4 only with no net): the processor's and the memory's ball
  fields (except the two processor corners where the boxed-in balls leave on layer 4), the east power column and the strip
  under J1. Layer 4 is plane copper there (core/MPU, +5 V, 1.8 V/3.3 V feeds). Because a through via crosses layer 4, the same
  keep-out stops new vias there: in a 0.8 mm-pitch ball field the plane webs between the ball vias are about 0.25 mm wide and
  a via between the balls cuts them (first autorouted board: GND, VDDS_DDR, core, MPU and 1.8 V all split into several
  pieces). The outer layers stay open for the escape traces. This is the same rule module 0.4.4's router applied (a via in
  the ball field only on a ball centre or >= 0.45 mm from all of them), expressed with plain SRJ obstacles.
- **Connections**: every signal net with all its terminals (processor balls, part pads, CM4 connector pins). A ball
  whose via-in-pad the planner already drilled (the balls boxed in by the DDR copper) is a terminal on all three layers.

## Local setup

The autorouter source checkout needs its git-hosted dependencies. In this environment the proxy refuses GitHub's
tarball endpoints (`api.github.com`, `codeload.github.com`: HTTP 403), so `bun install` cannot fetch them. They are
cloned with git at their pinned commits into `/home/user/ar-deps/` and the local `package.json` points at the clones
(`file:`), devDependencies of the dependency clones dropped (datasets, not needed to run the solver). This only changes
the local checkout; nothing of it is committed upstream.

## Issues found and fixes

| # | Solver / stage | Symptom on this board | Cause | Local fix | Upstream |
|---|---|---|---|---|---|
| 1 | Input (this board), port-point pathing | With layer-4 keep-outs over the east power column, `PreparedPortPointRoutingSolver ran out of iterations` (37 s at effort 1, 41 s at effort 4, 172 s with effort let through, see 3). | **My approach, not the solver.** A keep-out on layer 4 also forbids vias (a through via crosses layer 4), so the whole PMIC/buck column had no place to change layers. Found by bisecting the keep-out groups (only the east column fails). | Keep-outs only where blocking vias is the point (processor and memory ball fields). | none |
| 2 | SRJ input model | No way to say "this layer is a plane here: no traces, vias allowed", or "use this layer only as a last resort". Obstacles block traces and vias together; layer preferences exist only for buses (`preferredLayer`, `allowedLayers`). | Missing feature. On a 6-layer board with planes the router either gets fewer layers than the board has or may route anywhere on a plane. | none yet: the plane builder carves around layer-4 traces and the plane check verifies the supplies | candidate repro PR |
| 3 | Pipeline 9, `getPipeline9PortPointPathingInput.ts` | `effort` above 1 does not raise the port-point pathing budget. | `effort: Math.min(1, pipeline.effort)` (from #4046, no stated reason), while the pipeline's own comment says budgets scale with effort. | Tried locally on branch `local/cm4-module`; did not help here (issue 1 was the cause), so not used. | candidate PR, low priority |
| 4 | `high-density-repair01`, `lib/utils/high-density-force-improve-topology.ts` (used by `Pipeline9HighDensityForceImproveSolver`) | Force-improve never finished on this board: the run sat on one node for over 80 minutes. Per-node timing on the dumped stage input: 912 of 923 nodes take 448 s in total, node 898 (37 routes, 5147 points) takes 344 s, node 912 (43 routes, 11 087 points) more than 10 min. | **Solver.** `getRoutePairClearanceViolations` and `findNewProperSegmentCrossings` test every segment against every other segment (O(n²)). `findAlignedTopologyCandidate` calls the first once per candidate move, up to 16 moves per residual crossing, so a node with thousands of segments and many crossings does billions of pair tests. Profile: 41 % in `getRoutePairClearanceViolations`. | Find candidate pairs with an x sweep over segment bounding boxes plus the same y test the loops already apply; sort the pairs back into loop order where order matters (crossing selectors). Exact: the same pairs are tested, the same results come out. Verified by hashing the improved routes of nodes 909 and 797, old vs new code: identical. Node 909: 11.8 s → 6.7 s; node 898: 344 s → 189 s. | repro PR to `tscircuit/high-density-repair01` (pending) |
| 5 | Pipeline 9, regional fallback → `RegionalForceImproveSolver` | Routes from the regional fallback are 30–90 % sub-micron segments (e.g. node `cmn_2041__sub_2_0`: 10 routes, 3944 points in a 0.44 × 2 mm cell, one route 10.8 mm long). Whole force-improve input: 80 450 segments, 14 400 under 1 µm, mostly 0.1–1 µm. They inflate every later per-point stage. | Every such node is one the regular solver failed with "impossible single-layer crossing" and the regional fallback then solved. Counting sub-µm segments after each cleanup step (local diagnostic, `HD_DEGEN_LOG=1`, not for upstream): the raw intra-node routes have none, and after regional force-improve the same point count is 60–90 % sub-µm (e.g. 359 points: 0 → 318). The force step pulls the grid router's oversampled vertices into near-coincident clusters and keeps them. | see 6 | candidate issue |
| 6 | Pipeline 9, `simplifyPipeline9CollinearRoutePoints.ts` | The simplifier added upstream for an AM3352 stall (#2681) did nothing on this board: 82 519 points in, 82 519 out. | It only collapses straight runs of 64 or more grid steps. Here the grid solvers (A01/A03) emit staircases with straight runs of 5–8 steps of 6–25 µm, and the fallback adds the clusters from 5. | Same scope as upstream (only regions with ≥ 4096 points, where the existing comment already accepts the approximation): (a) thin short straight runs to control points at least one trace width apart, instead of keeping every grid step; (b) drop plain interior vertices within 1 µm of their predecessor on the same layer, never vias or layer changes. Copper is unchanged: every original vertex lies within 4e-15 mm of the simplified route. Big regions: 11 087 → 5387, 7949 → 5514, 5147 → 3088 points. Together with 4, node 898 takes 56 s (was 344 s) and node 912 takes 413 s (did not finish before). | candidate PR to `tscircuit/tscircuit-autorouter` |
| 7 | Pipeline 9, `Pipeline9HighDensityForceImproveSolver.validateImprovedSample` | On 7 of 10 sampled nodes, including every dense one, the improved routes are thrown away because they worsen clearance to fixed vias, after minutes of work. | Observation only. | none | note for upstream |
## Runs

| Date | Solver revision | Input | Result |
|---|---|---|---|
| 2026-11-25 | npm 0.0.1156, default pipeline | 2 signal layers (top/bottom) | failed after 33 s: `No path for 37 (SYSBOOT2_mst1) after allowing movable routes to be rerouted`. Expected: SYSBOOT2 starts at a ball the DDR copper boxes in on both outer layers; 0.4.4 routed those nets on layer 4. Not a solver issue: the input lacked layer 4. |
| 2026-11-25 | npm 0.0.1156, default pipeline | 3 signal layers (top / layer 4 / bottom), 100 nets, 234 terminals, 8084 obstacles | killed by the out-of-memory killer after 856 s at about 9 GB resident, in a late stage (minified class name `solverClass`). Not pursued: the current source does not show it (next row). |
| 2026-11-25 | source `dc19141` (v0.0.1164), default pipeline | same input | **solved in 1104 s**: 100 nets, 134 traces, 602 vias, 2829 mm (top 286, layer 4 217, bottom 232 segments). |
