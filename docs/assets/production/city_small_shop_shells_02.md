# city_small_shop_shells.02 — Wide standalone shell

9 October 2026. **Source, export and linked-prefab production candidate delivered;
independent acceptance and world placement pending.** Current production dispatch and
[commission](commission.md) supersede the family brief's historical concept-only restriction.
Original model/source, integration and self-checks: commissioned implementation worker.
The supervising production lead approved the dimensions and collision scope below;
independent reviewers remain the acceptance owners. No shared tracker or world scene changed.

Family: [small shop shells](../city_small_shop_shells.md). References inspected:
[Signal Row B04](../../concepts/districts-v1/signal-row-assets.md),
[Signal Row / Broadlot identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and accepted
[narrow inline shell .01](city_small_shop_shells_01.md) and fitting prefabs.

## Design and approved dimensions

A wide, shallow, single-storey ordinary shop with two frontage bays under **one
continuous roof**. The broad quiet roof, transverse standing folds, wrapped coping,
wrapped plinth and side/rear head courses distinguish it from the deep, narrow inline
shell. There is no central party wall or interior tenant division: either one business
or two small tenants can dress the frontage. Exposed side/rear walls intentionally stay
quiet; this is not a district landmark or a recolour of .01.

The production lead explicitly approved a reversible **12.8 m wide × 9 m deep**
structural footprint, **5.05 m** front parapet, two **6.4 m** frontage modules reusing
.01's fitting interfaces, .01's palette/heights, a bare and fitted prefab, and a single
solid exterior footprint collider. These are authored measurements, **not dimensions
inferred from a generated concept**. Flat terrain; no interior or rooftop gameplay.

| Measurement | Metres |
| --- | --- |
| Structural footprint, Blender X/Y | [-6.4, 6.4] × [-4.5, 4.5] |
| Full Blender mesh AABB | (-6.48, -4.58, 0) → (6.48, 4.62, 5.05) |
| Full Godot mesh AABB | (-6.48, 0, -4.62) → (6.48, 5.05, 4.58) |
| Full Godot X width / Y height / Z depth | 12.96 / 5.05 / 9.20 |
| Front wall plane / thickness | Blender Y=4.5 / 0.28 |
| Deck underside / top | 4.14 / 4.30 |
| Side/rear wall top / coping top | 4.60 / 4.70 |
| Front parapet coping top | 5.05 |
| Front / rear / lateral visual projections | 0.12 / 0.08 / 0.08 |
| Source/export envelope tolerance | ±0.001 per bound; raw GLB comparison 0.00001 |

Ground-centred structural footprint pivot `(0,0,0)`; root and mesh transforms are
identity, geometry contains component offsets. Metre units, unit scale. Blender +Y
is the frontage and +Z is up; one glTF conversion produces Godot -Z front / +Y up.
No corrective import or prefab transform. A hidden, excluded 1 m reference cube is
saved in `authoring_excluded`, never in the export. The shell is closed component
geometry with real facade holes, not a fused engineering/weatherproof building.

## Source, exports and materials

- Source: `art/source/models/environment/city_small_shop_shells_02/city_small_shop_shells_02.blend`.
- Collection: `export_city_small_shop_shells_02`; root: `city_small_shop_shells_02`.
- Export: `art/models/environment/city_small_shop_shells_02/city_small_shop_shells_02.glb`
  and its committed `.glb.import`.
- Reproducible construction/export/audit/render/manifest tools:
  `tools/asset_production/city_small_shop_shells_02/`.
- Original editable Blender construction; no downloaded/purchased/generated-from-image
  geometry, brands, external fonts, or textures. No external attribution obligations.
- Shared `tools/assets/blender/export_settings.json` owns export options. This asset
  explicitly filters its named collection and disables animations/skins. Source
  modifiers are applied. Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF **5.2.40**.
- No cameras/lights, studio geometry, reference cube, fittings, collision meshes,
  rigs, clips, destruction states, or embedded images enter the shell GLB.

Five opaque, back-culled Principled/glTF PBR materials, matching .01's names and
linearized swatches. Each semantic mesh has one surface. No UV-dependent effect,
texture, Godot material override or separate `.tres` is needed.

| Material | sRGB reference | Metallic / roughness |
| --- | --- | --- |
| `shell_muted_plum_render` | #81777C | 0 / .78 |
| `shell_quiet_blue_roof` | #405B68 | .12 / .65 |
| `shell_warm_structural_trim` | #BBB6A8 | 0 / .70 |
| `shell_slate_plinth` | #4A5358 | 0 / .78 |
| `shell_dark_drain_coping` | #334950 | .35 / .48 |

Godot's asset-local default automatic LOD, shadow-mesh and compression settings remain
unchanged. No device budget or measured repeated-building rendering cost is claimed.

## Fitting interfaces and prefabs

`scenes/prefabs/environment/city_small_shop_shells_02.tscn` is the reusable **bare
shell part**; it needs frontage fittings before presentation as a complete building.
`city_small_shop_shells_02_fitted.tscn` inherits it and instances ten unchanged accepted
fitting prefabs: two each of canopy .01, fascia .02, single surround .03, display
window .05 and single closed door .06. It is the complete static visual candidate.
Both use identity `Visuals/Model` linked to the shell GLB. No meshes are copied into
scenes, no fitting is stretched, and no scene is constructed at runtime.

All markers below are children of the source root and are preserved by name. The
saved fitted scene uses their exact transforms; `check.gd` rejects placement drift.
Frontage modules are centred at X=-3.2 and +3.2. Marker rotations are identity and
scales are one. Names take `mount_left_` or `mount_right_` prefixes.

| Marker suffix | Godot left translation | Godot right translation | Consumer |
| --- | --- | --- | --- |
| `entrance_single` | (-1.25, 0, -4.5) | (5.15, 0, -4.5) | .03 single |
| `door_single` | (-1.25, 0, -4.5) | (5.15, 0, -4.5) | .06 single |
| `display_window` | (-4.15, .48, -4.5) | (2.25, .48, -4.5) | .05 |
| `canopy` | (-4.15, 3, -4.5) | (2.25, 3, -4.5) | .01 |
| `fascia` | (-4.15, 3.8, -4.5) | (2.25, 3.8, -4.5) | .02 |

Additional `mount_roof_detail` is `(0,4.3,0)` in Godot, on the deck between folds.
No roof equipment is embedded. Fitting producers own later mounting-envelope review.
No inline party-wall joining contract is exposed on this standalone variant.

Entrance holes are 1.42 × 2.45 m at X [-1.96,-.54] and [4.44,5.86], height [0,2.45].
Window holes are 3.04 × 1.88 m at X [-5.67,-2.63] and [.73,3.77], height [.54,2.42].
The clear insertion zone extends at least 0.55 m behind the front plane. Actual
unchanged entrance/leaf/window GLBs pass **3,604 rear-vertex inclusion checks** and
900 hole rays plus eight adjacent wall-hit checks. Existing nominal interfaces retain
10 mm entrance jamb/head gaps and 20 mm window sleeve gaps. Fitted canopy bottom is
2.58 m, 100 mm above window top; fascia bottom is 3.40 m, 160 mm above canopy top.
Mount tolerance remains ±2 mm; gaps are nominal, not guarantees under arbitrary offsets.

The canopy reaches 1.10 m beyond the facade: fitted front reaches Godot Z=-5.60.
Reserve its existing 1.20 m installation depth (through Z=-5.70). Do not derive
walkway widths from the bare-shell AABB alone. Facade graphics are deliberately blank:
commercial artwork is a separate asset owner, not missing model geometry.

### Deliberate exterior-only collision

One `Collision/Body` StaticBody3D, layer 1 / mask 0, owns a **12.8 × 4.3 × 9 m** box
centred at `(0,2.15,0)`. It makes the whole exterior footprint solid, including nominal
entrance recesses and bare apertures. It intentionally differs from .01's wall-span
colliders; do not use this prefab for entry or interior traversal. Coping, folds,
canopies and signs do not expand collision. The six inherited door/window shapes
are disabled, and their bodies have layer 0, using explicit saved fitting-level
editable overrides; imported visual children are not overridden. Shared fitting
prefabs and identities are untouched. No opening mechanic or gameplay rule is added.

Native headless tests query the **actual saved fitted prefab**: three rays hit the
shell body, one side bypass is clear, a 0.38 m radius / 1.8 m capsule overlaps the
solid footprint once and is clear on the front walkway. This is bounded physics
resource evidence, not production actor motion, transport, prediction or placement
acceptance. Those checks remain downstream.

## Validation and visual evidence

[`validation.json`](city_small_shop_shells_02-evidence/validation.json) records:

- **4,188 triangles; 2,140 source vertices; 2,320 exported split vertices; 25 meshes /
  25 material surfaces; five materials; 11 mounts plus one root; 73,616-byte GLB.**
- Zero degenerate source faces, zero raw GLB degenerate triangles, zero non-manifold
  edges; closed consistently wound components and positive signed volumes.
- Finite geometry and unit-length source corner / exported normals; raw index winding
  agrees with normals. Applied mesh transforms, exact collection membership, excluded
  studio/reference, declared metre bounds and ground datum pass.
- Fresh-process saved-source reexport is **byte-identical** to the committed GLB.
  Regenerating the `.blend` itself is not claimed byte-identical.
- Pinned Godot **4.8.dev7.official.c971f93e7** import and fresh-runtime dependency loads
  resolve model/material/prefab resources and saved UIDs. Both scene save/reload
  roundtrips are byte-stable. Measured bounds agree within 0.001 m; all ten fitting
  mounts agree with actual imported markers with zero placement error.

Four lean, isolated Blender renders (Cycles CPU, 32 samples, AgX, broad studio fill):
[hero, fitted](city_small_shop_shells_02-evidence/hero.png),
[side/rear, bare](city_small_shop_shells_02-evidence/side.png),
[frontage detail, fitted](city_small_shop_shells_02-evidence/detail.png), and
[47 m / 42° overhead, fitted](city_small_shop_shells_02-evidence/overhead_47m_42deg.png).
All are 1280×800. The overhead is vertical-down perspective, fixed north-up, camera
at `(0,0,47)` in Blender, 42° **vertical** FOV. Self-inspected all four: the broad roof
and two frontage projections remain distinct at gameplay scale; door/window faces
and fascia copy are substantially roof-occluded, as in .01. Do not rely on wall copy
for essential overhead navigation. No actual engine screenshot, combat occlusion,
visual placement or target-device acceptance is claimed. Fittings are temporary
unchanged GLB imports for renders, never saved into this source or shell export.

[`manifest.json`](city_small_shop_shells_02-evidence/manifest.json) hashes every final
produced payload (except itself), plus read-only shared fitting dependencies.
One concise [`final.log`](city_small_shop_shells_02-evidence/final.log) retains command
outcomes and diagnostic classification. Raw retries, full logs and scratch exports
stay outside Git in `C:/tmp/ft/assets/city_small_shop_shells_02/`.

## Exact reproduction (Git Bash, repository root)

No live Blender/Godot sessions or connector tools are used. Windowed editor unavailable;
text prefab authoring was explicitly permitted, then normalized headlessly. Import does
not synchronize any separate open editor scene; no live editor was touched.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=C:/tmp/ft/assets/city_small_shop_shells_02
mkdir -p "$T"
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_02/author.py
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_02/export.py
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_02/export.py -- "$T/reexport.glb"
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_02/validate.py -- "$T/reexport.glb"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_02/render.py
timeout 300 "$(mise which godot)" --headless --editor --path . --import --quit
timeout 180 "$(mise which godot)" --headless --editor --path . --script res://tools/asset_production/city_small_shop_shells_02/check.gd -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script res://tools/asset_production/city_small_shop_shells_02/check.gd
timeout 30 "$(mise which gdstyle)" --max-warnings 0 tools/asset_production/city_small_shop_shells_02/check.gd
timeout 30 "$(mise which gdstyle)" fmt --check tools/asset_production/city_small_shop_shells_02/check.gd
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks"
python tools/asset_production/city_small_shop_shells_02/manifest.py --verify
```

For read-only verification skip `author.py` and the production export; export only to
scratch. Verify the manifest **before** regenerating evidence, since regeneration
legitimately changes hashes. Canonical check output must be a fresh directory; final
reviewed run used `checks-reviewed`. After an intentional rebuild and review, run
`manifest.py` without `--verify` to refresh the exact payload inventory.

### Checks and diagnostics, without blanket suppression

Final owned GDScript lint and formatting: **pass**, zero issues. Explicit compilation:
**pass**. Canonical production check exits **1**, solely for the common brief's known
pre-existing five `tests/fixtures/asset_production/*.gd` compile failures and formatting
of `batch_observation.gd`, integration `batch03_author.gd` and `inspector.gd`. Final
46-script lint passes. Python repository tests: **9/9**. GUT: **9/9**, 70 asserts;
negative-control failure detection passes. None of those unrelated files was edited.

Initial owned version assertions incorrectly treated `Engine.get_version_info().string`
as the CLI version spelling; it actually returns `4.8-dev7 (official)`. Corrected to
major/minor plus pinned commit hash. Initial checks timed out after the assertion;
these are not counted as successful runs. The checker now retains failure state across
helper calls rather than relying on Godot's per-function assertion abort. Initial lint
spacing/length and intentional tool-only editor-polling warnings were corrected; final
scoped checks and canonical lint are clean.

Editor-mode normalization exits 0 with stable scene bytes/UIDs but logs editor/plugin
shutdown **RID/ObjectDB leak diagnostics** (plus the plugin's untested-4.8 warning).
These remain a tooling limitation, not a clean-editor-exit claim. Initial normalization
also checked a newly saved UID before registration; explicit registration plus startup
scan waiting resolved that dependency finding. The final separate **runtime** check
exits 0 with no warnings/errors and passes dependency, bounds, mounts and physics checks.
Headless import exits 0 with only the existing plugin-version warning. Blender author,
export, reexport, numeric validation and renders exit 0; the standalone Blender version
query alone emitted its one-small-block shutdown diagnostic. No broad error filter or
vendor patch was used, and no unrelated process was terminated.

## Remaining acceptance

Independent source/art/prefab review; actual production actor motion/aim and corner
clearance; authoritative/predicted/multiplayer behavior; native gameplay-camera combat
readability; district placement/derived data; shared artwork; sustained repeated-instance
GPU/device/Deck and packaged-build checks remain **pending**. Bare-shell apertures are
not traversable entrances under this approved collider. Roof access, door animation,
destruction, lights and gameplay interiors are out of scope. This package does not
mark a shared register row READY or authorize placement.
