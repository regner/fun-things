# d06_entertainment_hall.03 — Entry canopy

**Source/export and linked prefab delivered; independent review and full gameplay acceptance pending.**
Production follows the resumed per-asset commission and [family brief](../d06_entertainment_hall.md).
Original Blender construction by the commissioned production worker. The preceding
[.01 shell](d06_entertainment_hall_01.md) and [.02 ring](d06_entertainment_hall_02.md)
remain unchanged from lane predecessor `6e8a438`. No external geometry, textures,
brands, generated-image meshes, prototype references or runtime render-mesh construction.

## Design and provisional dimensions

A low cantilever canopy covers the hall's central closed entrance. One cyan shoulder
wraps the front and rounded corners, returning along the sides; the rear and broad
roof centre remain petrol. The dark lower lip gives the thin slab a manufactured
section. This repeats the ring's soft shoulder and restrained material treatment
without adding another magenta ring, signs, hardware noise, posts or roof equipment.

The supervisor explicitly approved the following **provisional authored envelope**
before production: width 10 m, total depth 2.95 m (2.8 m forward of the entry datum
plus 0.15 m rear allowance), underside 3.6 m, top 4.05 m, hall-ground identity pivot,
rounded front corners, one modest cyan emission appearance, no posts/collision/lights.
These are not dimensions inferred from an image or accepted world-clearance measurements.

| Measurement | Godot-local metres |
| --- | --- |
| Visual AABB minimum | (-5, 3.6, -11.8) |
| Visual AABB maximum | (5, 4.05, -8.85) |
| Width / height / depth | 10 / 0.45 / 2.95 |
| Construction wall-contact datum | (0, 3.6, -9) |
| Rear planar mounting face | Z=-8.85, matching .01 main wall |
| Front projection from entry datum | 2.8 |
| Front plan corner radius | 0.8, 12 segments per quarter |
| Upper/lower bevel inset and rise | 0.08 / 0.08 |
| Top cyan border width | 0.42 beyond the top centre panel |
| Gap below .02 ring underside | 2.70 |
| Root / mesh pivot | (0,0,0), hall ground datum, not canopy underside |
| Envelope tolerance | ±0.001 |

### Family interface and placement

Instance this prefab at **exactly the same transform as .01 and .02**. Do not add
another Y=3.6 or Z=-9 translation. Blender +Y front / +Z up converts once to Godot
-Z front / +Y up. Root and mesh are identity; there is no compensating prefab scale
or rotation. The canopy has no ground contact; its ground-centred origin is the
approved family alignment datum, not a geometry error. Construction datums are
not runtime sockets or gameplay APIs.

The rear face meets the actual planar wall at Z=-8.85. The layered closed entry
extends towards Z=-9 below the slab. The bottom rear bevel ends slightly forward
of the main face, avoiding a hard exposed back corner. Width 10 m covers the 8.8 m
entry backing with 0.6 m each side. Nothing changes the shell's closed doors or
introduces an interior, traversal, animation, destruction or interaction state.

The canopy is **visual-only**. No collision, navigation or actual light nodes are
created. The existing shell remains the sole collision owner; no new posts obstruct
the plaza. The visual underside is 3.6 m above the hall ground, but actual actor/car
movement and sightline acceptance remain downstream. The family now extends to
Z=-11.8 in front; its combined visual bounds are (-13.95,0,-11.8) to
(13.95,9.6,9.95). Preserve plaza, boundary streets and at least one side passage
when placing it. No saved world, road, greybox or neighbouring asset is changed.

## Source, export, materials and prefab

- Source: `art/source/models/environment/d06_entertainment_hall_03/d06_entertainment_hall_03.blend`.
- Export collection: `export_d06_entertainment_hall_03`.
- Root / mesh: `D06EntertainmentHall03` / `D06EntertainmentHall03_Mesh`.
- GLB: `art/models/environment/d06_entertainment_hall_03/d06_entertainment_hall_03.glb`.
- Prefab: `scenes/prefabs/environment/d06_entertainment_hall_03.tscn`.
- Reproduction/check scripts: `tools/asset_production/d06_entertainment_hall_03/`.

One connected editable closed mesh, including its connected U-shaped diffuser
surface. Five profile loops and two caps define the slab; normals are recalculated
outwards and an applied weighted-normal modifier retains smooth manufactured edges.
No modifiers remain. There are no stacked coplanar render surfaces or open back.
Studio camera/ground/lights are outside the export collection. The unchanged .01
and .02 sources are appended **after source save/export** for evidence only; neither
is duplicated into this source or GLB. Their SHA-256 values are in validation.json.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export uses
`tools/assets/blender/export_settings.json`, named-collection filtering, Y-up,
no animations/skins/extras/cameras/lights/morphs. No rig, textures, embedded images,
external material resources, sockets, variants or explicit LODs are required.
Godot default generated LODs/shadow meshes remain enabled; LOD/performance review
is pending, not inferred from this small triangle count.

Opaque back-culled Principled materials in source/GLB/import order:

| Slot | Name | Base linear RGB | Metallic / roughness | Emission |
| --- | --- | --- | --- | --- |
| 0 | `canopy_housing_petrol` | .035, .105, .125 | .25 / .43 | None |
| 1 | `canopy_diffuser_cyan` | .015, .58, .68 | 0 / .38 | Same RGB × .45 |

GLB emissive factor is (.00675,.261,.306), without HDR strength extension or light
nodes. Imported Godot emission colour is approximately (.07646,.54782,.58912),
reflecting colour-space conversion. This is an appearance accent, not calibrated
illumination, bloom or an accepted emissive-signage setting.

The text-authored prefab was loaded/packed/resaved twice using pinned headless
Godot. `Visuals/Model` retains the identity-transform imported instance; there are
no imported-child overrides or embedded render meshes. Prefab UID
`uid://cp36vl7qdg5us`; model UID `uid://c61jmg86cdijr`. Importer metadata and owned
check-script `.uid` are retained; the `.tscn` stores its UID internally.

## Evidence and validation

[Hero, complete family](d06_entertainment_hall_03-evidence/hero.png) ·
[Isolated oblique side](d06_entertainment_hall_03-evidence/side.png) ·
[Installed entry detail](d06_entertainment_hall_03-evidence/entry_detail.png) ·
[47 m / 42° overhead](d06_entertainment_hall_03-evidence/overhead_47m_42deg.png).

All four are isolated Blender Cycles CPU renders, 32 samples, AgX, 1280×800. The
overhead is vertical-down perspective at 47 m, 42° **vertical** FOV, +Y/north at
image top. All were inspected: the cyan front shoulder remains visible beyond the
ring, the quiet canopy centre does not compete with the dome, and the entry detail
shows coherent wall contact and coverage. From the centred gameplay camera most
of the canopy rear is hidden by the roof/ring; its exposed cyan leading edge is
an entrance cue, not readable signage. A scratch-only comparison with both cyan
and magenta emission set to zero was also inspected: shape/base colour still read.
These are **not** Godot lighting, populated-city occlusion or device acceptance.

[validation.json](d06_entertainment_hall_03-evidence/validation.json) records:

- **276 triangles**, **140 source vertices**, **200 GLB vertices** including
  normal/material splits; **one mesh, two surfaces**.
- **Zero degenerate source faces**, **zero nonmanifold source edges**, **zero
  degenerate exported triangles**; positive signed volume/outward winding and
  connected slab/diffuser. Maximum unit-normal error: source 1.14e-7, GLB 8.58e-8.
- Literal independent source, GLB accessor and Godot AABB expectations match within
  0.001 m. Source transforms are identity and coordinate values finite.
- Three camera rays aimed at independent front-shoulder samples hit cyan before
  either actual preceding family mesh. A centre ray misses this canopy, preserving
  the quiet roof. Rear-face ray hits Z=-8.850000381. These bounded geometry checks
  do not accept off-centre camera occlusion or world placement.
- Fresh export from reopened saved source is **byte-identical**, **8,432 bytes**,
  SHA-256 `0e8eb94b52293043eb5dc5d09cfb201068957c1fbca573f680bb0682d6d90866`.
- Pinned headless import succeeds. Two normalized prefab saves are byte-stable;
  a fresh process resolves both UIDs, all dependencies, linked geometry, bounds,
  opaque back-culling materials, cyan emission and absence of collision/light nodes.
- Owned GDScript passes gdstyle **0.3.0** lint/format and explicit compilation.
  Production checks exit **1 solely for known existing failures**: five fixture
  compilation errors under `tests/fixtures/asset_production/`, formatting in
  `batch_observation.gd`, integration `batch03_author.gd` and `inspector.gd`.
  All **48** discovered scripts lint-clean; this asset compiles. Python **9/9**,
  GUT **9/9**, **70 assertions**, and negative-control detection pass.

### Diagnostics and limitations

Authoring and validation exit 0; Blender authoring emits 5.2 API deprecation notices.
The initial `--version` probe also reports one unfreed 23-byte block; the actual
asset author/validator do not report that diagnostic. Headless import emits the
existing MCP plugin 4.8 compatibility warning. Editor-mode normalization exits 0
and produces valid stable resources, but reports RID/ObjectDB shutdown leaks, as
both preceding family assets did. These diagnostics remain recorded, not fixed or
suppressed. Fresh non-editor resource load and explicit compilation exit 0 with
**no ERROR/WARNING diagnostics**. No unchanged failing steps were repeated.

The common brief prohibits live/windowed editor use; saved text plus isolated
headless normalization is the deliberate fallback. No owner's live Blender/Godot
session was used or modified. Existing project plugin startup was left unchanged.
No headless import is claimed to synchronize a separate live editor scene.

[final.log](d06_entertainment_hall_03-evidence/final.log) retains a concise final
receipt and diagnostic lines. [manifest.json](d06_entertainment_hall_03-evidence/manifest.json)
hashes all delivered payloads except itself. Raw CLI logs, full production-suite
logs and the extra unlit render stay outside Git at
`C:/tmp/ft/assets/d06_entertainment_hall_03/`.

## Exact reproduction

Run from the worktree in Bash. `mise` supplies the pinned engine/gdstyle. The
production-check output directory must be fresh; no windowed/live editor launches.

```sh
NID=d06_entertainment_hall_03
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py" > "$T/author.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py" > "$T/validate.log" 2>&1

timeout 300 "$G" --headless --editor --path . --import --quit > "$T/import.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize \
  > "$T/normalize.log" 2>&1
timeout 180 "$G" --headless --path . --check-only \
  --script "res://tools/asset_production/$NID/check_prefab.gd" > "$T/compile.log" 2>&1
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-fresh.json" > "$T/prefab-fresh.log" 2>&1

timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd"
timeout 60 "$(mise which gdstyle)" fmt --check "tools/asset_production/$NID/check_prefab.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks" \
  > "$T/production-checks.log" 2>&1
python "tools/asset_production/$NID/record.py"
```

`author.py` reconstructs the mesh/four renders and scratch unlit comparison.
`validate.py` reopens source, checks topology and actual GLB accessors, reexports
to scratch, compares bytes and tests family visibility. `export.py` is also an
independent entrypoint, accepting an output directory after `--`. `check_prefab.gd`
uses real Godot resource APIs. `record.py` consolidates existing receipts and hashes;
it does not substitute for running validation. Preceding .01/.02 sources are needed
only for combined evidence and visibility tests, not canopy export or prefab loading.

## Remaining handoffs

1. Independent art/technical review of the exact committed candidate.
2. Saved city placement preserving plaza/passages, decorative overhang allowances,
   actual actor/car movement and sightlines with the shell's collision owner.
3. Actual Godot camera/lighting/emission calibration, off-centre occlusion and LOD review.
4. Packaged dependencies, repeated-instance GPU/frame pacing, sustained Deck/device
   performance and any affected authoritative/predicted/multiplayer placement checks.
5. Editor-mode CLI shutdown diagnostics remain integration/tooling investigation.

No shared queue, brief, progress, catalogue, TODO, world or project file changed.
No full-game readiness, independent review or pending placement gate is marked accepted.
