# d06_entertainment_hall.01 — Rounded hall shell

**Source/export and linked prefab delivered; independent review and full gameplay acceptance pending.**
Production follows the resumed per-asset commission and
[family brief](../d06_entertainment_hall.md). Original Blender construction by the
commissioned production worker; no downloads, generated-image geometry, external
textures, brands or prototype dependencies. No preceding assets existed in this lane.
The next two records own the luminous ring and entry canopy, not this shell.

## Design and provisional dimensions

An exterior-only civic entertainment hall: a broad rounded-rectangle plan, low
emerald dome, petrol walls, dark grouped clerestory glazing, slate ground shoe and
restrained plum entry surround. Four opaque closed entry panes and sparse frames
provide ordinary architectural scale. The centre of the roof is deliberately empty.
There is no luminous ring, cyan canopy, tenant artwork, interior, roof traversal,
opening-door mechanic, animation, lighting node or destruction state in this asset.

The supervisor explicitly approved the 26 × 18 m fitting envelope, approximately
8 m walls, dome below 10 m, ground-centred pivot, simple solid static collision, and
family connector datums below. These are **provisional authored dimensions**, not
measurements inferred from the concept image or accepted city clearances.

| Measurement | Godot-local metres |
| --- | --- |
| Complete visual AABB minimum | (-13, 0, -9) |
| Complete visual AABB maximum | (13, 9.6, 9) |
| Width / height / depth | 26 / 9.6 / 18 |
| Wall crown / dome top | 8.0 / 9.6 |
| Ground shoe | 26 × 18 plan, 0–0.44 high; 6 m corner radius |
| Main wall plan | 25.7 × 17.7; 5.85 m corner radius |
| Roof spring | 7.91; outer plan matches main wall |
| Clerestory | 4.88–6.25; opaque dark glazing |
| Entry backing width / top | 8.8 / 3.6 |
| Pivot | (0, 0, 0), ground-centred footprint |
| Envelope/ground tolerance | ±0.001 |

Blender +Z up / +Y front converts once to Godot +Y up / -Z front. Both exported
nodes are at identity with unit scale; no corrective prefab scale or rotation.
The flat ground datum is Y=0. The slightly projecting decorative entrance remains
inside the 26 × 18 m envelope, including the small door pulls.

### Family connector contract for .02 and .03

These are construction datums, **not runtime sockets or gameplay APIs**. Source
root custom properties retain them, but export extras are disabled.

- **Roof-ring trim .02:** horizontal centre datum at Godot Y=7.2, centred X/Z=0.
  Its wall mounting contour is a 25.7 × 17.7 rounded rectangle with radius 5.85 m,
  corner centres (X,Z)=(±7,±3). Front straight runs X=-7…7 at Z=-8.85;
  side straights run Z=-3…3 at X=±12.85. The quiet mounting band is Y=6.33…7.92.
  Each source quarter arc has 16 segments. Match this perimeter rather than making
  a circle or measuring the dome image. The dome overhangs this datum in overhead
  projection: .02 must check its outward/top-facing ring visibility and its own
  overhang/route allowance; no ring section or additional footprint is approved here.
- **Entry canopy .03:** central wall-contact datum **(0, 3.6, -9)**, identity yaw;
  front is -Z, outward from the hall. Entry backing spans X=±4.4 and ends at Y=3.6.
  Main planar wall is Z=-8.85; layered closed entry faces extend almost to -9.
  Keep the canopy rear edge compatible with that 0.15 m layered face allowance.
  There are no columns, canopy meshes or canopy collision in this shell.
- Ring magenta emission and canopy cyan accent remain their owners' scope. This
  shell uses no emission, so its four renders explicitly test the unlit silhouette.

No saved world building is replaced. `brackett/district_06/building_0015` and the
proposed western plaza remain layout references only. Preserve the plaza, boundary
streets and at least one side passage in subsequent saved placement.

## Source, export, materials and prefab

- Source: `art/source/models/environment/d06_entertainment_hall_01/d06_entertainment_hall_01.blend`.
- Collection: `export_d06_entertainment_hall_01`.
- Root / mesh: `D06EntertainmentHall01` / `D06EntertainmentHall01_Mesh`.
- Linked export: `art/models/environment/d06_entertainment_hall_01/d06_entertainment_hall_01.glb`.
- Prefab: `scenes/prefabs/environment/d06_entertainment_hall_01.tscn`.
- Reproduction and checks: `tools/asset_production/d06_entertainment_hall_01/`.

One editable static mesh combines closed architectural components. Contact/intersection
between the base, wall, dome and applied fittings is intentional assembly overlap;
it does not produce open/nonmanifold component edges. Applied bevels soften fittings;
profile rings carry the wall/roof curvature. Studio ground, camera and lights are
outside the export collection. No rig, animation, texture images, explicit LODs or
external material resources are required. Import-generated LODs and shadow meshes
remain at their default settings; LOD silhouette/performance acceptance is pending.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. Export loads
`tools/assets/blender/export_settings.json`, sets the named collection and disables
animations/skins. Cameras, lights, extras and morphs stay out. glTF Y-up conversion
is applied once. No reference to archived prototype models or tools.

Six opaque back-culled Principled materials, actual GLB/imported order:

| Slot | Material | Base linear RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `hall_base_slate` | .13, .19, .21 | .10 / .60 |
| 1 | `hall_wall_petrol` | .035, .105, .125 | .12 / .53 |
| 2 | `hall_glazing_opaque` | .012, .038, .057 | .35 / .27 |
| 3 | `hall_frame_teal` | .09, .20, .22 | .50 / .38 |
| 4 | `hall_roof_emerald` | .027, .105, .091 | .20 / .43 |
| 5 | `hall_entry_plum` | .13, .055, .105 | .10 / .50 |

Flat colours only; no embedded images or unsupported procedural shaders. Glazing
is deliberately opaque for an exterior-only shell. Blank panels are architecture,
not accepted hall graphics or essential overhead-readable signage.

The saved prefab instances the GLB at **Visuals/Model**, identity transform, with
no embedded render mesh or imported-child overrides. Godot generated stable node
identities and prefab UID `uid://swp7op1xjew2`; model UID is `uid://dc7mv6ln78t2x`.
The GLB `.import` and check-script `.uid` are retained; `.tscn` stores its own UID.

### Deliberate collision

`Collision/Body` is a StaticBody3D, layer 1, mask 0. Two central boxes (14×8×18 and
26×8×6) plus four radius-6, height-8 cylinders at X=±7, Z=±3 form the rounded solid
footprint from Y=0 to 8. This conservatively follows the **ground-shoe envelope**:
most wall faces sit 0.15 m inside collision. Curved render chords differ from the
analytic cylinder by at most about 0.008 m. Overlapping convex shapes intentionally
make one solid, non-enterable hall; there is no hollow interior or door opening.
The dome above Y=8 and all applied fittings are visual-only, with no extra snag
colliders. Collision does not author navigation, interaction or roof traversal.

## Evidence and validation

[Hero](d06_entertainment_hall_01-evidence/hero.png) ·
[Side](d06_entertainment_hall_01-evidence/side.png) ·
[Entry detail](d06_entertainment_hall_01-evidence/entry_detail.png) ·
[47 m / 42° overhead](d06_entertainment_hall_01-evidence/overhead_47m_42deg.png).

All four are isolated Blender Cycles CPU renders, 32 samples, AgX, 1280×800. The
last camera is vertical-down perspective with 42° vertical FOV at 47 m, +Y north
at image top. All four were inspected: rounded plan and shallow dome read without
an illuminated ring; broad highlights retain smooth curvature; the centre remains
quiet; the closed entry is coherent in the detail view. This is **not** engine
lighting, populated-city camera or target-device visual acceptance.

Final measurements in [validation.json](d06_entertainment_hall_01-evidence/validation.json):

- **10,288 triangles**, **5,232 source vertices**, **6,283 GLB vertices** after
  surface/normal splits; **one mesh, six surfaces**.
- **Zero degenerate source faces**, **zero nonmanifold source edges**, **zero
  degenerate exported triangles**. Maximum unit-normal error: source 1.73e-7,
  export 1.36e-7. Normals and finite coordinates are explicitly asserted.
- Source, GLB and actual Godot AABB match the literal expectations within 0.001 m.
  Measured height is 9.600000381 m; ground minimum is exactly zero.
- Fresh export from the reopened saved source is **byte-identical**, 268,708 bytes,
  SHA-256 `93a817b58abcf59634cf8471d79c24d5a9d80af7e113cbfb8c8b345a389ad5e8`.
- Pinned Godot headless import succeeds. Saved prefab is packed/resaved twice with
  stable bytes. Fresh process resolves both UIDs, linked import, material surfaces,
  model identity transform and six collision shapes.
- Eight direct physics shape checks pass: solid interior, closed entry and rounded
  corner; clear front plaza sample, clipped corner, both outside-side samples and
  dome-above-wall-height sample. A forward ray hits (0,1,-9) exactly. These are
  **bounded resource/physics checks**, not accepted actor/car movement or city routes.
- Owned GDScript passes pinned gdstyle 0.3.0 lint/format and explicit compilation.
  Production checks ran twice (an initial owned await-in-loop lint warning was fixed).
  Final result remains exit 1 solely for the documented existing integration issues:
  five `tests/fixtures/asset_production/*.gd` compilation failures and formatting in
  `batch_observation.gd`, integration `batch03_author.gd` and `inspector.gd`.
  All 46 discovered scripts are lint-clean; this asset compiles. Python **9/9** and
  GUT **9/9**, **70 assertions**, pass; the negative control is detected correctly.

[final.log](d06_entertainment_hall_01-evidence/final.log) retains one concise receipt,
including diagnostics; [manifest.json](d06_entertainment_hall_01-evidence/manifest.json)
hashes every delivered payload except itself. Raw retries and full multi-project
logs remain only at `C:/tmp/ft/assets/d06_entertainment_hall_01/`.

### Diagnostic limits

Blender authoring emits 5.2 API deprecation notices, not errors. The project's
existing MCP plugin reports its 4.8 compatibility warning during headless import.
No live Blender/Godot sessions were used or modified; these were isolated CLI
processes with the existing project plugin configuration left unchanged.

Runtime-mode ResourceSaver initially omitted a new scene UID; normalization was
corrected to headless **editor-mode** saving. That custom-SceneTree editor process
saves stable resources but reports RID/ObjectDB leaks on shutdown (retained, not
claimed clean). Waiting for startup removed a scan-aborted warning but did not
remove those editor shutdown diagnostics, so that failing cleanup was not retried
unchanged. Fresh non-editor load/query and explicit compilation both exit 0 with
**no ERROR/WARNING diagnostics**. This distinction is part of the evidence, not a
broad suppression or a claim that editor teardown is clean.

## Exact reproduction

Run from this worktree in Bash; `mise` resolves the pinned engine and gdstyle.
The checks directories must be fresh because shared production tools reject reuse.
All Blender and Godot calls are timeout-bounded; no windowed editor is launched.

```sh
NID=d06_entertainment_hall_01
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# validate.py reopens the saved source, reexports into external scratch and compares bytes.

timeout 300 "$G" --headless --editor --path . --import --quit
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize \
  > "$T/prefab-normalize-final.log" 2>&1
timeout 180 "$G" --headless --path . --check-only \
  --script "res://tools/asset_production/$NID/check_prefab.gd"
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-fresh-final.json" > "$T/prefab-fresh-final.log" 2>&1

timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd"
timeout 60 "$(mise which gdstyle)" fmt --check "tools/asset_production/$NID/check_prefab.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks"
# Final recorded rerun after owned lint correction used the next fresh directory:
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks-final"
python "tools/asset_production/$NID/record.py"
```

`author.py` regenerates geometry and all four evidence renders; `export.py` is also
an independent entrypoint on the saved source and accepts an output directory after
`--`. `validate.py` checks actual GLB accessors, source topology and fresh-export
bytes. `check_prefab.gd` asserts imported resources and literal physics expectations.
`record.py` adds external final engine/check receipts and updates payload hashes.

## Remaining acceptance / handoff

1. Independent art/technical review of this exact committed candidate.
2. .02 ring and .03 canopy production using the connector datums above, including
   combined overhead visibility, final emission/light calibration and overhang fit.
3. Saved world placement preserving plaza/passages; actual player/car movement,
   turn/clearance, aiming and authoritative/predicted/multiplayer collision checks.
4. Actual Godot camera/lighting and LOD review, packaged build/dependency checks,
   repeated-instance GPU/frame pacing and sustained Deck/device performance.
5. Editor-mode CLI shutdown diagnostic investigation belongs to integration/tooling;
   no vendor patch or project-setting change is included here.

No queue, shared brief, progress, catalogue, world placement, prototype or global
project file is changed, and no pending whole-game gate is marked accepted.
