# S07 primary T — sustained saved-reload route driver

8 October 2026. Bounded prerequisite for [primary technical card T](s07-run-cards.md#t--technical-two-sector-calibration-blocked-not-representative-capacity),
**not graphical calibration or representative capacity acceptance**. Base
`233493abc7d2e3c106fb620105cfb766f542813b`, branch `s07-sustained-route-reset-driver`,
workspace `wks_08760af59ce23966`. Direct implementer: Sol6.1 HIGH; ROOT coordinates
only. [Complete commission, declarations and raw evidence](s07-sustained-driver-evidence/README.md).
Full S07 and P0-GATE remain OPEN.

## Ownership and executable recipe

The new saved `tests/fixtures/s07_driver/intersection.tscn` inherits the unchanged
[S06 intersection](s06.md)/[body/topology contract](s06-contracts.md)/[source handoff](s06-source-handoff.md).
Its only override is root script `S07DriverFixture extends S06Fixture`. No new
nodes, geometry, transforms, routes, bake or body rules. Original S02/S04/S06,
source/GLB/import/UID/config bytes stay unchanged. The inherited owner still calls
the real body `step` once per physics callback, admitting only one moving body.

`begin_route(case)` refuses passive authority, unknown case, stale/missing content,
wrong saved starts/yaws/velocities/collision roles or an already-used fixture.
The executable SceneTree driver assigns standalone authority **before tree entry**;
S06 configures its bodies passive before child entry. Admission revalidates the
actual S06 fingerprint and all three saved starts before calling `start_route`.
`cancel_owned()` clears the producer/route and neutralizes all bodies. Completion
requires stopped motion/passive collision before notification. Then queue/free,
observe retirement, instantiate the saved scene anew and revalidate before binding
next foot/east_to_north/west_to_south route. This is safe saved-fixture reload,
not a new in-place reset API, pose teleport, production Match reset or traffic AI.
One-shot fencing prevents the old empty immediate completion at the destination.

No S06 coordinated API extension was necessary. Scripts never write starting pose,
sector placement or topology. Existing1200/1800-tick timeouts remain failures.
The saved scene's genuine engine UID/node/inheritance identity and three genuine
script sidecars were recovered from the private editor, not fabricated.

Reproduction requires a separately authorized fresh runtime envelope; do not rerun
the exhausted historical editor/sustained attempt. The public repository tools are:

```sh
# Exactly pinned executable is byte-checked by the runner; fresh external output.
python3 tools/s07_driver/run.py /tmp/s07-new-authorized-run import
python3 tools/s07_driver/run.py /tmp/s07-new-authorized-run development
python3 tools/s07_driver/analyze.py /tmp/s07-new-authorized-run/development-1 /tmp/s07-dev-analysis.json
python3 tools/s07_driver/run.py /tmp/s07-new-authorized-run sustained
python3 tools/s07_driver/analyze.py /tmp/s07-new-authorized-run/sustained-1 /tmp/s07-sustained-analysis.json
# Offline checks only; no engine/editor invocation:
python3 tools/s07_driver/check_resources.py /tmp/s07-preservation.json
python3 tools/s07_driver/test_offline.py
```

`run.py` retains exact argv/exit/streams, uses no addon/autoload/native initialization,
fresh private XDG roots per phase, HOME unchanged, persistent attempt counts and
absolute phase caps with owned cleanup reserved. It never implicitly retries.
Minimal closure is46 saved/script/model/sidecar/settings files, five linked GLBs.
Only three new GDScripts are explicitly compiled; this is not whole-project
all-script validation. `author.py` and draft inputs preserve the commissioned
failed authoring recipe; **they are not a ready retry instruction**.

## Observed results and timing boundaries

| Separately assessed phase | Actual result |
| --- | --- |
| Private author supervisor | **FAILED**; one editor,6.55s from launch through reap. Correct seed/boost=false and authenticated project/PID/auto-allocated endpoint/token binding; three scripts/genuine sidecars and inherited scene saved. Strict preservation guard rejected private Toolkit/settings changes. Two headless thumbnail dummy-texture errors. Bridge exit0, owned editor terminated/reaped exit-15; no claimed clean shutdown or retry. |
| Saved-resource recovery | Narrow positive: inherited scene save/close/reopen/save stays380 bytes/SHA fdc552fd9e798c72326301eb1797f79e182ebdfae58f727f1694e5097c6e52f2. Exact seven-file mirror/recovery/candidate ledger; formatting-only new-script fallback afterward, no changed scene/UID. Full original-file readback and saved ancestry/dependency checks pass. Not full author-phase acceptance. |
| Addon-free closure import | One attempt,2.72s, exit0; complete stdout/stderr/engine streams, no diagnostics, saved inputs unchanged. |
| First development group |65.77s including explicit all3 new-script compiles,15 public-boundary lifecycle/ownership/stale/cancel/reload guards and six actual traversals. Two successive traversals each; guards/outcomes/independent analysis have no failures. |
| Sustained interval | One group608.95s including owned process cleanup, exit0, no runtime diagnostics. Declared600 actual seconds; driver interval608.639614s with57 full traversals,19 per route,36,461 actual physics samples; no timeout, contact, seam/footprint/continuity/destination/heading failure. |

Each foot traversal477 ticks/7.95 simulation seconds; each car721 ticks/12.0167s.
Independent literal destination <=0.5m, exit heading <=10°, nonempty progress,
zero solid contact, one seam crossing, max step <=0.15m and source-derived whole
footprint/route error <=1m pass on **every** traversal. Maximum route error0.201861m.
Source-derived discrete footprint checks reuse accepted immutable S06 geometry;
this is not a new source reexport, continuous swept-volume proof or final-body gate.

Sustained actual simulation delta is607.683333333109s. Load/instantiate/tree-ready
phases total0.199533 wall seconds; post-notification cancellation/queue/free/observed
retirement phases total0.046146s. Every receipt carries the monotonic load-start,
ready-before-admission, completion and retirement boundaries; gaps include JSON
serialization/loop work. The field `traversal_start_seconds` is the **ready-before-
admission** boundary: its wall span includes signature/route/admission work and
S06's internal stopped-before-notification completion, not just movement. That
internal S06 stop is not separately instrumented. The reported reload reset cycle
is post-notification cancel/retire plus next saved load; new instances restore all
starts/yaws/neutral velocity. All these timings are simulation/lifecycle observations,
**not normal traversal/performance costs, FPS, GPU or graphical capacity**.
No callback/command survives fixture retirement; repeated authoritative admission
preserves the same static source/derived/topology fingerprint each time.

## Limits and next gates

The authoring attempt remains failed with exact diagnostics and settings diff;
ROOT granted offline artifact recovery, not error suppression or another editor.
The exact settings diff shows automatic Toolkit runtime-autoload registration and
section reordering only; no private config is installed into the repository. No shared editor
was touched. The editor is gone, so no post-format editor synchronization is claimed;
the fresh import/explicit compilation/runtime read the actual saved candidate.

Primary T now has an executable sustained **simulation-only** driver receipt;
independent exact-candidate review is a separate retained disposition, not implied
by these observations. Graphical T still needs named hardware/build/telemetry and
an authorized drawable surface, its original warmup/repeats/cap modes and attributable
graphical costs. S05 effect comparator/reset/draw remains blocked and unimplemented.
Six-block content, population/network integration, four graphical views, representative
loads/growth/headroom/optimization, Steam/Deck/device/feel/final dimensions and full
S02/S03-R/S04/S05/S06/S07/S08/P0/M1/production gates remain open. No renderer,
streaming, budget, capacity maximum or product decision follows from this driver.
