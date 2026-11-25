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

(filled in as issues are found)

## Runs

| Date | Solver revision | Input | Result |
|---|---|---|---|
| 2026-11-25 | npm 0.0.1156, default pipeline | 2 signal layers (top/bottom) | failed after 33 s: `No path for 37 (SYSBOOT2_mst1) after allowing movable routes to be rerouted`. Expected: SYSBOOT2 starts at a ball the DDR copper boxes in on both outer layers; 0.4.4 routed those nets on layer 4. Not a solver issue: the input lacked layer 4. |
| 2026-11-25 | npm 0.0.1156, default pipeline | 3 signal layers (top / layer 4 / bottom), 100 nets, 234 terminals, 8084 obstacles | killed by the out-of-memory killer after 856 s at about 9 GB resident, in a late stage (minified class name `solverClass`). Not pursued: the current source does not show it (next row). |
| 2026-11-25 | source `dc19141` (v0.0.1164), default pipeline | same input | **solved in 1104 s**: 100 nets, 134 traces, 602 vias, 2829 mm (top 286, layer 4 217, bottom 232 segments). |
