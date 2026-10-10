# d07_sign_island.01 — Low circular island base

10 October 2026. **Source/export and linked prefab delivered; independent review and
world/gameplay acceptance pending.** Commissioned implementation worker on `lane/a-d07`
owns original construction and bounded technical integration; supervisor/reviewer owns
acceptance, world integrator owns placement. No prior same-lane sibling delivery existed.
The resumed production commission supersedes the historical concept-only restriction.

Inputs: [family brief](../d07_sign_island.md),
[Broadlot district concept](../../concepts/districts-v1/broadlot.md),
[selected district 07](../../concepts/districts-v1/map-context.md#district-07),
[approved identity](../../concepts/world-v1/stage-03-district-identities/README.md#broadlot--big-roofs-bigger-empty-spaces)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md).
These establish a detached low orientation cue, quiet body, simple circle and sparse lime;
they do not ratify parcel dimensions, a new traffic island rule or city placement.

## Design and provisional dimensions

One low monolithic circular sign plinth: slate perimeter, quiet petrol centre, shallow
side reveal and one **30° lime sector** toward local -Z. Broad rounded/chamfered edges and
continuous circular shading keep the silhouette simple. The visible centre is a solid flat
deck, not a planting hole. No sign tower, foliage, bolts, copy or invented interactions.
This is reusable sign-support hardware, **not a hand-authored road/sidewalk/curb kit**.
Roads, parking surfaces, routes and generated infrastructure remain with the road tool.

All dimensions are **provisional authored choices**, not raster measurements. They fit the
large low retail / broad forecourt language without assigning any district land or replacing
an existing placement. District gross area 6.84 ha / 474.5 × 234.8 m is context, not allocation.

- Godot width / height / depth: **6.000 × 0.280 × 6.000 m**.
- Godot AABB: **(-3, 0, -3) → (3, 0.28, 3)**, dimensional tolerance ±0.001 m.
- Ground-centred root and mesh origins **(0,0,0)**; metre units, applied rotation/scale.
- Blender +Z up / +Y front maps once to Godot +Y up / -Z front. No wrapper correction.
- Maximum radius 3 m; lower edge chamfer ends at radius 2.96 m on ground.
- Upper edge rolls from radius 3 m at Y=0.22 to radius 2.94 m at Y=0.28.
- Flat top from centre to radius 2.94 m; petrol centre radius **2.58 m** and a
  **0.36 m slate rim**. Both are coplanar at Y=0.28, not layered overlapping faces.
- Side reveal is 0.015 m deep, between Y=0.06 and 0.12 m; purely visual.
- Ninety-six radial segments form one closed manifold mesh, not intersecting rings.

### Family mounting handoff

The flat **Y=0.28 m** deck is the mounting datum for an independently authored sign support.
Place its ground/mounting root at **(0,0.28,0)** relative to this base, identity yaw when its
front should match the lime sector (-Z). The unobstructed petrol centre has radius 2.58 m;
keep its attachment footprint inside that circle. This is available space, not a demand
to fill it or a sign-height decision. The base adds no socket API, marker or runtime assembly.
Parents coordinate any future saved composition by this documented datum. Materials below
provide the family palette; no other record's geometry is duplicated or modified.

## Source, export and materials

- Source: `art/source/models/environment/d07_sign_island_01/d07_sign_island_01.blend`.
- Collection: `export_d07_sign_island_01`; root **D07SignIsland01**, mesh **D07SignIsland01_Mesh**.
- Export: `art/models/environment/d07_sign_island_01/d07_sign_island_01.glb` plus `.import`.
- Prefab: `scenes/prefabs/environment/d07_sign_island_01.tscn`.
- Recipe / exporter / validator / engine check / receipt writer:
  `tools/asset_production/d07_sign_island_01/`.

Original Blender construction only: no downloaded meshes, image-to-mesh, real brands,
external textures, embedded images or prototype dependencies. Editable profile and material
assignments are retained in source; `author.py` is the parametric recipe. The studio ground,
camera and lights are excluded from the export collection. Weighted normals are applied
before saving. glTF triangulates the closed source. No rig, animation, destruction state,
UV-dependent artwork, lights or custom LODs are needed. Default import LOD/shadow settings
are retained, but actual repeated-placement cost and LOD appearance remain unaccepted.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**;
`export.py` loads `tools/assets/blender/export_settings.json`, explicitly filters the named
collection and disables animations/skins. No copied private shared-export configuration.

Three opaque back-culled Principled surfaces, actual source/GLB/Godot order:

| Slot | Material | Linear base RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `island_body_slate` | .24, .32, .36 | .05 / .65 |
| 1 | `island_deck_petrol` | .028, .067, .092 | .10 / .60 |
| 2 | `island_wayfinding_lime` | .48, .72, .16 | 0 / .50 |

The petrol colour matches the delivered retail building's trim family. No emission or
transparent layers. Lime is a restrained orientation accent, not essential legible copy.

## Prefab and deliberate collision

**Visuals/Model** is the identity-transform linked GLB instance. No copied render mesh,
editable imported children, material overrides or runtime-built hierarchy. Pinned headless
Godot generated/preserved inline scene UID `uid://bm1c3kh0lgf2t`, imported GLB UID
`uid://t4nehl2wo150`, scene node identities and the check script's `.uid` sidecar.
The TSCN carries its scene UID inline; it does not need a separate TSCN UID sidecar.

**Collision/Body/Base** is one CylinderShape3D on a StaticBody3D, radius **3 m**, height
**0.28 m**, centre **(0,0.14,0)**, layer 1 / mask 0. This continuous solid follows the
freestanding-prop standing collision rule and supports the complete flat deck. The smooth
cylinder ignores small chamfers/reveal: at most 0.06 m radial conservatism at the upper
edge, 0.04 m at the ground edge, and about 0.00161 m over the radial facet chords. No gaps,
separate rim snags, invisible tall blocker or duplicate ground plane. Ground datum is zero.

This collider does not create traffic priority, auto-step, ramp, climbing, navmesh or
interior behavior. A bare capsule sweep hits the raised edge; actual ActorMotion/car
handling and navigation must be tested when a world placement is proposed.

## Evidence and measured validation

[Hero](d07_sign_island_01-evidence/hero.png) ·
[Side](d07_sign_island_01-evidence/side.png) ·
[Rim/reveal detail](d07_sign_island_01-evidence/detail.png) ·
[Gameplay-camera overhead](d07_sign_island_01-evidence/overhead_47m_42deg.png).

All four final views were inspected. Isolated Blender Cycles CPU, 24 samples, denoised,
AgX, **1280×720**, PNG compression **95**, no image quantization or post-render painting.
Each is below 400 KB. Side view has a slight downward angle to show the low section.
The overhead is genuinely vertical-down perspective at **47 m / 42° vertical FOV**,
Blender camera (0,0,47), north/+Y at image top, fixed yaw. The circle is about 120 pixels
across and the broad rim survives at that scale; the shallow side reveal is intentionally
not important overhead information. These are not Godot lighting/visibility captures.

[validation.json](d07_sign_island_01-evidence/validation.json) records:

- **1,916 triangles**, **960 source vertices**, **866 source faces**, **1,457 GLB vertices**
  after material/normal splits; **one mesh / three surfaces**.
- **Zero degenerate faces/triangles**, **zero nonmanifold edges**; positive closed volume
  **7.860997 m³**, finite coordinates and unit-length source/export normals.
- Maximum normal-length errors: source **1.34e-7**, GLB **1.30e-7**.
- Source, binary GLB accessors and Godot bounds match the literal expected AABB;
  source-to-export mapping tolerance 0.00001 m; ground minimum exactly zero.
- Reopened-source fresh export is **byte-identical**, **49,056 bytes**, SHA-256
  `db6885400a731b1cca66e1cfa63d58008faa0ee932665e6a13d20481eb164ca6`.
- Pinned Godot **4.8.dev7.official.c971f93e7** import passes with no ERROR/SCRIPT ERROR.
  Headless editor pack/save/reload/resave is byte-stable, with saved scene/dependency UIDs.
  Fresh non-editor load proves linked dependency, identity transform, materials and collider.
- **Ten shape queries** cover the solid centre, four rims and clear exterior/above/below.
  **Three downward rays** at centre and separated diagonal top points all hit Y≈0.28 m.
- Real CharacterBody3D capsule (**radius 0.35 m / height 1.8 m**) using `move_and_collide`
  stops against the edge at **Z=-3.34228515625**, bypasses at X=3.5 to **Z=5**, and is
  supported at centre **Y=1.181640625**. Contact tolerance is **5 mm**, separately from
  the 1 mm geometry/ray tolerance; no duplicated gameplay movement formula is tested.
- Owned GDScript check-only compilation, gdstyle lint (100 columns / zero warnings),
  and `gdstyle fmt --check` pass. No full-project production suite was run.

[final.log](d07_sign_island_01-evidence/final.log) is the concise check/diagnostic receipt;
[manifest.json](d07_sign_island_01-evidence/manifest.json) hashes every delivered payload
except itself. Raw logs and scratch exports stay at `C:/tmp/ft/assets/d07_sign_island_01/`.

### Corrections and limitations

The first side render exposed the studio ground clipping at the bottom of the frame.
Moving the orthographic camera farther along the same sightline put all primary-ray
origins above ground; final evidence is continuous. No export geometry changed.
An initial capsule support assertion incorrectly applied the 1 mm dimensional tolerance
to Jolt's contact result (1.64 mm offset); the test now names a 5 mm contact tolerance,
while exact top ray and visual dimensional assertions remain 1 mm.

An uncommitted non-editor pack/save trial dropped the inline prefab UID. Normalization
now rejects use without `--editor`, asserts a saved inline UID and byte stability, and
was rerun in headless editor mode. Final import/fresh-load UIDs match the saved bytes.
All newly authored identities were stabilized before this first delivery.

Headless editor normalization exits 0 and passes assertions but retains the existing
plugin/pinned-engine shutdown RID/ObjectDB leaks; all exact ERROR/WARNING lines are in
the receipt, not described as a clean editor exit. Import emits the known MCP Godot 4.8
compatibility warning but **no errors**. Fresh runtime/compile checks are error-free.
The Blender version probe reported one tiny shutdown allocation; author/export/validator
runs exit 0 without that allocation error (only Blender future-API deprecation notices).
No engine, addon, project setting or live Blender/Godot session was modified. CLI-only
instructions required direct-file authoring followed by the bounded headless save checks;
this does not claim synchronization of any separate live editor.

## Exact reproduction

Run from repository root in Bash. Every Blender/Godot invocation is pinned and bounded.
Skip `author-final` for receipt-only refresh of unchanged source/export/renders. Never
normalize without `--editor`; fresh non-editor checks deliberately do not save scenes.

```sh
set -e
NID=d07_sign_island_01
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="$(mise which gdstyle)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
run_check() {
  local name="$1" code=0
  shift
  "$@" > "$T/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$T/$name.exit"
  return "$code"
}
run_check author-final timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
run_check validate timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# Validator reopens the source, reexports to scratch, and compares actual GLB bytes.
run_check import-final timeout 300 "$G" --headless --path . --import
run_check prefab-normalize-final timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --normalize --output "$T/prefab-normalize-final.json"
run_check compile timeout 180 "$G" --headless --path . --check-only \
  --script "res://tools/asset_production/$NID/check_prefab.gd"
run_check prefab-fresh timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-fresh.json"
run_check gdstyle-lint timeout 60 "$S" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd"
run_check gdstyle-format timeout 60 "$S" fmt --check \
  "tools/asset_production/$NID/check_prefab.gd"
# Before commit, rerun import to retain any final engine-normalized sidecars.
run_check import-final timeout 300 "$G" --headless --path . --import
python "tools/asset_production/$NID/record.py"
```

`export.py` also accepts a scratch output directory after `--` when run on the saved
source in pinned Blender. `record.py` checks final GLB size/hash, final scene UID/hash,
actual command exits/diagnostics, evidence dimensions, then regenerates the manifest last.

## Remaining acceptance

1. Independent art/technical review of this exact candidate; no self-acceptance.
2. Saved world placement with broad forecourt separation, clear routes/parking, actor/car
   clearance, actual production movement/weapon queries and network/prediction checks.
3. Actual Godot gameplay-camera lighting/contrast and assembled-support occlusion review.
4. Import LOD appearance, packaged dependencies, repeated-instance costs and sustained
   target-device performance. These are not established by isolated renders/headless checks.
5. Pinned editor/plugin shutdown leaks remain a tooling limitation, not a modified addon.

No queue, shared progress/brief, catalogue, sibling, world scene, global project file or
TODO was changed. No unproduced family record is tracked as a pending task here.
