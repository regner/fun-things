# Road tool spike evidence

This directory contains only compact evidence from a disposable project at
`C:/tmp/ft/road-spike/`; it does not vendor the addon or any generated mesh. The
capture uses the addon's reusable `4way_1x1.tscn` road/collision/lane prefab with
scratch-only boxes for four sidewalk corners, four crosswalks, four crossing anchors
and signal/light placeholders. Those boxes demonstrate attachment and automatic
placement only; they are not project assets. All timing measurements were collected on
the contended shared workstation; none are quiet-machine or hardware-certification
figures.

- `source-provenance.json`: exact upstream refs, archive digest and source inventory.
- `results.json`: compatibility, upstream-test, fixture and glTF-export observations.
- `observations.log`: compact command/output excerpts; large repetitive GUT traces are
  summarized rather than committed.
- `brackett-routes.json`: exact Brackett route input derived from the committed
  whole-city authoring plan, with a 0.5 m line simplification.
- `make-brackett-routes.py.txt`: derivation source; requires Shapely 2.x.
- `brackett-benchmark.gd.txt`: addon benchmark source.
- `brackett-downtown.json`: measured stage-04 downtown-grid slice.
- `brackett-whole-island.json`: measured road-only whole-island proxy, including the
  Harbour bridge stroke.
- `iteration-benchmark.gd.txt` / `iteration-result.json` /
  `iteration-run-windowed.log`: exact retained source, capped windowed result and raw
  pinned-engine receipt for point, type, prefab and dirty-bake operations.
- `iteration-headless-result.json` / `iteration-run-headless.log`: capped headless
  control rerun of the same retained source; report timings use the windowed receipt.
- `blender-roundtrip.json`: isolated timing of the current coarse Blender author,
  40-output export, fresh Godot import and 50-scene placement batch.
- `blender-loop-run.gd.txt`: isolated placement timing harness.
- `four-way-fixture.gd.txt`: screenshot fixture source.
- `four-way-prefab-prototype.png`: capped windowed 1280 x 800 capture.
- `export-test.gd.txt` / `export-inspect.gd.txt`: glTF export and addon-free content
  inspection sources.

## Reproduce

From Git Bash, with the repository root as the current directory:

```sh
export PATH="$(dirname "$(mise -C C:/GameDev/git/fun-things which godot)"):$PATH"
test "$(timeout 10 godot --version)" = "4.8.dev7.official.c971f93e7"
rm -rf C:/tmp/ft/road-spike/reproduction
mkdir -p C:/tmp/ft/road-spike/reproduction
cd C:/tmp/ft/road-spike/reproduction
git clone --depth 1 --branch 0.9.3 \
  https://github.com/TheDuckCow/godot-road-generator.git addon-source
cd addon-source
git rev-parse HEAD
# Expected: 980bc04c9f95a5c49b787f0a7a64a458156d5b9b
git archive --format=tar --output=../godot-road-generator-0.9.3.tar 0.9.3
sha256sum ../godot-road-generator-0.9.3.tar
# Expected: b3daf57e9b436dc8ceb56b3f1873fbd0fceb3e49d62270b791fec71e5ef3ef1f

rm -rf .godot
timeout 180 godot --headless --editor --path . --import > ../import.log 2>&1
timeout 60 godot --headless --path . \
  road_demos/intersections/intersection_demo.tscn --quit-after 10 > ../runtime.log 2>&1

timeout 120 godot -s addons/gut/gut_cmdln.gd --path . --headless \
  -gconfig=.gut_editor_config.json -gexit > ../upstream-tests.log 2>&1
```

The last command is expected to exit 1 on the pinned development engine: 67 of 73
tests pass, six use a GUT `assert_is` type argument rejected by this engine/GUT
combination, and GUT's static initializer reports a typed `Nil`. This is retained as
a compatibility risk, not normalized into success.

Copy the retained fixture/benchmark sources into the scratch project and create
one-node scenes:

```sh
EVIDENCE=/path/to/road-tool-evidence
REPO=/path/to/road-spike-worktree
cp "$EVIDENCE/brackett-benchmark.gd.txt" road_spike_brackett_benchmark.gd
cp "$EVIDENCE/iteration-benchmark.gd.txt" road_spike_iteration_benchmark.gd
cp "$EVIDENCE/four-way-fixture.gd.txt" road_spike_fixture.gd
python "$EVIDENCE/make-brackett-routes.py.txt" \
  "$REPO/art/source/models/brackett_greybox/authoring_plan.json" \
  brackett_routes.json
printf '%s\n' '[gd_scene load_steps=2 format=3]' '' \
  '[ext_resource path="res://road_spike_brackett_benchmark.gd" type="Script" id="1"]' '' \
  '[node name="RoadSpikeBrackettBenchmark" type="Node"]' \
  'script = ExtResource("1")' > road_spike_brackett_benchmark.tscn
printf '%s\n' '[gd_scene load_steps=2 format=3]' '' \
  '[ext_resource path="res://road_spike_iteration_benchmark.gd" type="Script" id="1"]' '' \
  '[node name="RoadSpikeIterationBenchmark" type="Node3D"]' \
  'script = ExtResource("1")' > road_spike_iteration_benchmark.tscn
printf '%s\n' '[gd_scene load_steps=2 format=3]' '' \
  '[ext_resource path="res://road_spike_fixture.gd" type="Script" id="1"]' '' \
  '[node name="RoadSpikeIntersectionFixture" type="Node3D"]' \
  'script = ExtResource("1")' > road_spike_fixture.tscn

timeout 300 godot --headless --path . road_spike_brackett_benchmark.tscn \
  -- --scenario=downtown > ../brackett-downtown.log 2>&1
timeout 600 godot --headless --path . road_spike_brackett_benchmark.tscn \
  -- --scenario=whole_island > ../brackett-whole-island.log 2>&1
timeout 180 godot --path . --max-fps 60 \
  road_spike_iteration_benchmark.tscn > ../iteration-run-windowed.log 2>&1
cp road_spike_iteration.json ../iteration-result.json
timeout 180 godot --headless --path . --max-fps 60 \
  road_spike_iteration_benchmark.tscn > ../iteration-run-headless.log 2>&1
cp road_spike_iteration.json ../iteration-headless-result.json
timeout 60 godot --path . --resolution 1280x800 --max-fps 60 \
  road_spike_fixture.tscn > ../fixture.log 2>&1
```

The benchmark converts actual stage-04 route polylines to native RoadPoint chains and
applies the five real road widths/lane counts. Route crossings overlap without
RoadIntersection topology, so this is a road-ribbon generation envelope, not an
accepted traffic graph. It excludes sidewalk/crosswalk generation, the structural
bridge prefab, signals, props, buildings and serialization. The iteration run uses the
same downtown nodes and measures programmatic editor API mutations through native mesh
refresh plus two presented frames. It also times a narrow road-only dirty bake that
moves a point, rebuilds its affected container, copies the meshes to a plain addon-free
PackedScene, saves, cache-reloads and instances it. That probe excludes merging,
collision, semantic resources and manifest validation; prefab insertion is not
connected-junction rewiring.
The fixture is likewise visual/API evidence, not a movement, reservation or final
asset-workflow proof. The unchanged source emits its windowed-run limitation text in
the headless control result too; that control confirms execution/output fields only and
is not used as presented-frame timing.

The Blender baseline was measured in a clean directory containing the committed
`authoring_plan.json`, `author_blender.py`, `reexport.py`, `author_editor.gd`, export
settings and required placement/preview scripts. Blender 5.2.2 authored all 22 sources
and exported all 40 GLBs. The pinned Godot then performed a fresh import and the
retained `blender-loop-run.gd.txt` called the existing helper, which printed
`BRACKETT_EDITOR_AUTHORED 50`. Each phase ran as a separately timed subprocess; see
`blender-roundtrip.json`. This is the current coarse full batch, not a claim that a new
road-only Blender exporter could not be faster. It excludes human edit/inspection time
and, like every timing in this evidence set, ran under shared-workstation contention.

For the export probe, copy the two export sources similarly, create equivalent one-node
scenes, run the export scene, perform a headless editor import, then run the inspection
scene. The result must be read semantically: glTF retained one mesh, one static body and
one collision shape, but no `RoadLane` and no script. The generated `.glb` is intentionally
not committed.
