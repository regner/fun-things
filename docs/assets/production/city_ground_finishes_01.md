# city_ground_finishes.01 — Plain plaza paving

10 October 2026. **Material, source/export and linked swatch delivered; independent review and
world/gameplay/device acceptance pending.** Output type: Material study. Commissioned by
Regner under the [production commission](commission.md) and current lane brief, superseding
the earlier concept-only restriction in [city_ground_finishes](../city_ground_finishes.md).
Original author: commissioned Codex production worker; accepting reviewer remains pending.
No downloaded imagery, external fonts, generated-image textures, brands or third-party geometry.

## Design and dimensions

A quiet, matte slate paving field near the Petrol & Coral sidewalk reference `#85929D`.
Four broad **2 × 2 m slabs** occupy one seamless **4 × 4 m repeat**. The joints have a
16 mm low-contrast core and 8 mm feather on each side; there is no geometric groove,
bump/displacement, grit, crack noise, decorative motif or district-specific marking.
Albedo channel ranges are only R 125–134, G 138–147, B 149–158 (8-bit sRGB).
These are provisional authored material dimensions, not measurements from concept art.

This shared appearance supports the recorded Northpoint, Terrace Ward, Glassward, Old Quay,
Signal Row and Broadlot demand. It follows the approved district identities and Stage 4's
unequal courts/forecourts without defining any new plot, roadway or district boundary.
Applied district motifs remain their separate owners' deliverables. There were no earlier
completed ground-finish siblings in this lane to modify or duplicate.

The small portable swatch is **not a plaza floor module for world placement**:

- Godot dimensions X/Y/Z: **4.000 × 0.080 × 4.000 m**.
- AABB: **(-2, -0.08, -2) → (2, 0, 2) m**; tolerance ±0.000001 m.
- Surface-centred pivot at (0, 0, 0), with the walk surface at **Y=0**; thickness extends down.
  This uses the surface-datum exception for ground samples, not a raised slab/curb datum.
- Source metres, applied unit scale/rotation, root and mesh origins at zero.
  Blender +Z becomes Godot +Y; Blender +Y becomes Godot -Z.
- One closed mesh, one material surface, **8 Blender vertices / 24 exported vertices /
  12 triangles**. Hard face normals explain the exported corner splits.
- No rig, animation, sockets, destruction states, real lights or LODs. Automatic LOD is disabled
  only for this already-minimal twelve-triangle review swatch.

## Source, export and material mapping

| Deliverable | Path |
| --- | --- |
| Editable Blender source | `art/source/models/environment/city_ground_finishes_01/city_ground_finishes_01.blend` |
| Explicit GLB and retained importer metadata | `art/models/environment/city_ground_finishes_01/city_ground_finishes_01.glb` + `.import` |
| Reusable material | `art/materials/environment/city_ground_finishes_01/plain_plaza_paving.tres` |
| Original runtime texture | `art/textures/environment/city_ground_finishes_01/plain_plaza_paving_albedo.png` + `.import` |
| Linked review prefab | `scenes/prefabs/environment/city_ground_finishes_01.tscn` |
| Reproduction and checks | `tools/asset_production/city_ground_finishes_01/` |

Collection `export_city_ground_finishes_01` contains root `CityGroundFinishes01` and
`CityGroundFinishes01_Mesh`, mesh data `PlainPlazaSwatch`. `texture.py` is the editable,
deterministic texture source; `author.py` constructs the original Blender swatch. The saved
Blender Principled material links the committed PNG through a relative path, never packs it.
`export.py` loads the shared `tools/assets/blender/export_settings.json`, disables static
animation/skin export, temporarily disconnects the albedo link and restores it after export.
The exported `plain_plaza_paving` slot is remapped to the external `.tres` by committed GLB
import settings. Thus the GLB has **zero embedded images** and no divergent runtime texture.
The source remains textured in Blender, and the linked imported mesh uses the same delivered
texture through the external Godot material. No disposable cache material edits or prefab
editable-child overrides are involved.

Material: opaque, backface culled, nonmetallic, roughness **0.88**, white albedo multiplier,
512 × 512 RGB sRGB albedo, linear mipmap filtering and repeat enabled. PNG import is lossless,
mipmaps enabled, no automatic 3D compression conversion; this 4,447-byte low-complexity texture
needs no normal/ORM/emission map. No tangent-space normal convention is applicable.

### Surface-tool / UV interface

**Use the material and texture on the surface owner's geometry, not instances of the swatch.**
Decision 42 keeps generated road/sidewalk/curb/intersection surfaces with the road tool;
this delivery neither replaces that owner nor builds hand-placed road meshes.

UV0 is planar and **one UV unit represents 4 m** in either direction. Godot material UV scale
is (1,1,1). For a flat site, supply UV0 = `(local_x - anchor_x, local_z - anchor_z) / 4`.
U increases east/+X, V south/+Z; the centred sample anchor is (-2,-2). Preserve common anchors
across neighbouring patches and uniform metre density through bends/triangulation. Any
normalized 0–1-per-segment road UVs must be adapted by that owner to this physical tile scale;
node scaling is not the integration mechanism. No triplanar shader or world-state dependency
is added. Source edge samples match exactly in both directions.

The actual road addon/UV adapter is not present in this checkout, so live generated-surface
compatibility is **pending**, not silently asserted. Current site shapes, flat ground datums,
collision and layout ownership remain unchanged. This 4 m / 512 px interface provides a
concrete reference for subsequent family materials without changing their briefs.

## Prefab and collision

The saved wrapper keeps `Visuals/Model` as an identity-transform imported PackedScene instance,
with a saved model UID and no embedded replacement render mesh. The material and texture UIDs
are retained. Godot embeds scene/resource UIDs in the `.tscn`/`.tres`; the check script also has
its generated `.gd.uid` sidecar.

The review swatch has **one continuous 4 × 0.08 × 4 m box** at (0,-0.04,0), under
`Collision/SwatchBody/Shape`, static-world layer 1 / mask 0. It supplies a walkable sample with
no visual grout collision seams. Real generated/site surfaces keep their own existing collision;
do not add duplicate swatch colliders or overlay this sample on an existing floor.

Headless public physics rays hit the centre and four inset corners at Y=0 with +Y normals;
a ray outside the sample misses. These six checks establish the saved collider/datum only,
not production ActorMotion, car handling, scene seams or network behavior.

## Evidence and validation

- [Hero](city_ground_finishes_01-evidence/hero.png),
  [side](city_ground_finishes_01-evidence/side.png),
  [paving detail](city_ground_finishes_01-evidence/paving_detail.png): 960 × 640.
- [47 m / 42° overhead](city_ground_finishes_01-evidence/overhead_47m_42deg.png): 1280 × 720,
  vertical-down perspective, north up. The current brief's 720-pixel evidence cap supersedes
  the historical 800-pixel height, without changing height or vertical FOV.
- All four are isolated Blender Cycles CPU/24-sample/AgX renders, PNG compression 100,
  dithering disabled; individual files are 24–90 KB. They are **not Godot screenshots**.
- The overhead uses 48 linked, temporary swatch repetitions over 32 × 24 m. The unchanged
  Coral Courier and Latch GLBs are read-only, original-source-backed scale references.
  They are not saved into this asset or re-exported. All four final images were inspected:
  large quiet joints, no visible repeat-boundary breaks, and the coral car/ivory-coral person
  separate from the midtone field. The person's small true-overhead footprint and moving
  gameplay readability still need actual engine review.

[validation.json](city_ground_finishes_01-evidence/validation.json) records measured bounds,
counts, unit normals, outward winding, **zero degenerate faces / zero non-manifold edges**,
UV bounds and **fresh re-export byte identity**. Blender **5.2.2 LTS**, build `d13f752e3b9c`;
glTF exporter **5.2.40**. Godot **4.8.dev7.official.c971f93e7** imports dependencies and loads
and probes the prefab. Two headless save/reload rounds preserve exact prefab bytes/IDs.
An isolated compiler-project normalization also preserved the production `.tscn` and `.tres`
bytes. Final standalone load/physics and explicit script compilation exit 0 with no warnings/errors.

Five independent Python texture tests pass: committed pixels, opposite borders, bounded
midtone contrast, sparse slab rhythm and minified quietness. Pinned gdstyle passes. Full
production checks pass formatting/lint and **all 163 script compilations**, **14 repository
Python tests**, GUT import and the negative-test harness. **The full suite does not pass:**
GUT reports **136/137 tests**, with the unrelated audio one-shot release test failing at
`tests/unit/audio/test_audio_voice_policy.gd:113,114,120`. No audio code/resources were changed,
and this result is not covered up as the brief's historical fixture exception.

Diagnostic disposition is retained in [final_log.txt](city_ground_finishes_01-evidence/final_log.txt).
Headless editor `--script` normalization produces RID/ObjectDB shutdown diagnostics, also
reproduced by an empty SceneTree with no asset loading in the plugin-free compiler mirror.
The full-project import adds the existing MCP version warning. These are distinguished from
the clean standalone asset check; normalization is a saved-byte observation, not a clean-log
claim. Initial texture-edge quantization and texture-filter enum mistakes were corrected and
retested. The initial false-success helper receipt was replaced after adding completion guards.
The producer [manifest](city_ground_finishes_01-evidence/manifest.json) hashes every delivered
file except itself; scratch logs/retries stay outside the repository.

## Exact reproduction

From repository root, Git Bash; Python with Pillow 12.3.0 and the pinned mise tools available.
Use a fresh output directory for the full checks (the tool rejects an existing nonempty one).
Never connect to an owner's live Blender/Godot session.

```sh
N=city_ground_finishes_01
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="tools/asset_production/$N"
S="C:/tmp/ft/assets/$N"
mkdir -p "$S"
python "$T/texture.py"
timeout 120 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/preview.py"
timeout 300 "$G" --headless --editor --path . --import --quit
# Inspect the log: editor shutdown diagnostics are discussed above, not suppressed.
timeout 180 "$G" --headless --editor --path . --script "res://$T/check_prefab.gd" -- --normalize
cp "$S/prefab.json" "$S/prefab_normalized.json"
timeout 180 "$G" --headless --path . --script "res://$T/check_prefab.gd"
timeout 180 "$G" --headless --path . --check-only --script "res://$T/check_prefab.gd"
"$(mise which gdstyle)" fmt --check "$T/check_prefab.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd"
python -m unittest discover -s "$T" -p 'test_*.py' -v
timeout 1800 mise exec -- python tools/production_checks.py --output "$S/checks"
timeout 120 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py"
# validate.py opens the saved source in a fresh process and reexports into scratch.
python "$T/manifest.py" --write
python "$T/manifest.py"
```

Editor-managed files used direct text authoring followed by the required pinned headless
load/pack/resave because live sessions are prohibited and the windowed editor is unavailable.
No claim is made that a separate open editor scene was refreshed or synchronized.

## Remaining acceptance

Independent technical/art review; actual road-tool UV/tiling adaptation; saved world placement
and district motif composition; production-camera motion/shadow/actor-and-car separation;
actual movement and multiplayer checks if a site collider changes; sustained GPU/frame pacing,
packaged builds and Deck validation. No shared queue, progress, brief, project setting, gameplay
code, other family asset, world placement or TODO was changed. No generic whole-game READY claim.
