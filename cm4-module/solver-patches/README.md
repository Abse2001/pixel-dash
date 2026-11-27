# Solver changes made while routing the CM4 module

These are local changes to tscircuit's routing libraries made during this board's routing. They are not in the
upstream repositories (this session can push only to this repository), so they live here as `git format-patch` series,
with the commit each series applies to. Apply with `git checkout <base> && git am <dir>/*.patch`.

The board itself is **not** routed with these: its signals come from our own negotiated-congestion router
(`../pb/route.ts`, from the RK3566 CM4 module's routing playbook) and its DDR block from
`tscircuit/bus-lanes-solver`, branch `feat/negotiated-lane-solver`, commit `4cd438f` (already on GitHub). The patches
below are from the earlier attempt with the tscircuit autorouter; `../AUTOROUTER-NOTES.md` describes every issue found
and what each patch fixes, and `PR-DRAFTS.md` has upstream pull-request texts for two of them.

| Directory | Upstream | Base commit | Ours |
|---|---|---|---|
| `tscircuit-autorouter/` | tscircuit/tscircuit-autorouter | `dc19141bc92b21a52cb42aced8699e7ddb978924` (v0.0.1164) | all 7; `0002` is diagnostics only (LOCAL ONLY, not for upstream) |
| `high-density-repair01/` | tscircuit/high-density-repair01 | `54abc98791d6300c4071476890818187da6d5e1a` | `0007`, `0008` (+ the uncommitted test `uncommitted/segment-pair-sweep.test.ts`); `0001`-`0006` are the escape-preservation branch the autorouter build used |
| `tiny-hypergraph/` | tscircuit/tiny-hypergraph | `c5a37f9ce2381233366048de693c4f74e754c108` | `0009`; `0001`-`0008` are the crossing-constraint branch the autorouter build used |
