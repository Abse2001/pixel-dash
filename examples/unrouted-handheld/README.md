# Pixel Dash full-board autorouter example

Open [board.circuit.json](board.circuit.json) in a Circuit JSON viewer to inspect the four-layer handheld. It contains the AM3354, the 1 GiB DDR3L package, the other populated footprints, their original placements, pins, schematic connections, board outline, cutouts and keepouts. It starts with zero routed PCB tracks, routing vias or filled pours. Plated component holes and mechanical holes are part of the board geometry.

Use [simple-route.json](simple-route.json) directly as the input to `BusLanesPipelineSolver`. It contains 365 routing requests, 1,207 obstacles, six buses and three differential pairs. The requests collectively cover all 206 multi-pin electrical nets and 972 terminals. All 50 CPU-to-RAM connections retain their package endpoints. Several requests can belong to the same electrical net.

To exercise your local solver changes, install that checkout's dependencies and run the following from this folder. The optional final argument saves the solver output on success.

```sh
bun route.ts /path/to/bus-lanes-solver /tmp/pixel-dash-routed.json
```

The runner calls the full pipeline with its default routing configuration. An unsuccessful solve reports the solver error and exits nonzero. The two checked-in inputs stay unrouted.

## Reference solver run

BusLanes commit `55d5f2b` reached `native_fallback_assignment` and reported “No collision-free local dogbone assignment” on attempt 3, after 109 cohort trials, with `fixedTraces=0`. This gives solver changes a reproducible full-board comparison. Completing that stage still leaves electrical and manufacturing checks to run on the routed output.

## Regenerate and verify

The fixture was extracted from the complete handheld copper checkpoint `25bb680`. From the repo root, with the project dependencies installed, run:

```sh
bun run build
python examples/unrouted-handheld/prepare.py dist/index.circuit.json
bun examples/unrouted-handheld/export-srj.ts
python examples/unrouted-handheld/verify.py dist/index.circuit.json
```

Extraction removes manual via bodies, their artificial pins, route hints, copper tracks, solved pours and old routing diagnostics. Real component pins keep their net memberships. The verifier compares the complete physical pin partition with the assembled design, as well as placements, holes, pads, buses and DDR endpoints. The snapshot uses the native core converter for obstacles and connection geometry. The export script restores the bus and pair constraints from Circuit JSON because core normally obtains them from live JSX components.
