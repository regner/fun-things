# city_seating.01 — Straight bench

10 October 2026. **Source/export and bounded headless prefab checks delivered;
independent review and world/gameplay acceptance pending.** Commissioned production
specialist: `worker` on `lane/a-seating`. The active asset-production common brief
supersedes the historical concept-only and lead-only integration/Git restrictions in
[commission](commission.md) and [family brief](../city_seating.md). No shared register,
progress, family, project or world files changed. This is the first seating-family delivery.

## Design and dimensions

An original straight civic bench: broad uninterrupted ivory seat and back, two slate
piers, inset slate back supports and a restrained petrol rim. Soft three-segment
roundovers and weighted normals preserve smooth highlights without slats, bolts,
logos or texture noise. No downloads, brands, generated-image geometry or external
art. All visible asset geometry was constructed in the pinned Blender CLI.

The quiet palette suits Northpoint, Terrace Ward, Glassward and Old Quay, following
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md). Other
recorded district uses remain unconfirmed. No sibling assets existed when this
member was built. Later seating members can reuse the named palette and .46 m seat
height while keeping their distinct short/low and corner silhouettes.

Dimensions are **provisional authored values**, not inferred from concept imagery:

| Measurement | Metres |
| --- | --- |
| Godot width X / height Y / depth Z | 2.40 / .92 / .68 |
| Whole visual AABB minimum | (-1.20, 0, -.34) |
| Whole visual AABB maximum | (1.20, .92, .34) |
| Seat top / seat thickness | .46 / .09 |
| Back bottom / top / thickness | .49 / .92 / .17 |
| Ground piers, each X / Y / Z | .18 / .37 / .49 |
| Pier centres X | ±.82 |
| Footprint area | 1.632 square metres |

Acceptance tolerance: .001 m for dimensions, origin and datum. Root and mesh pivots
are (0,0,0), at the ground-centred footprint; both foot bottoms contact Y=0. Blender
+Y is the seating/front side, mapping to Godot -Z; Blender +Z maps to Godot +Y.
All object transforms are applied, unit scale, metric units. Back occupies the
Godot +Z/rear edge. No corrective prefab rotation or scale.

This is intact, static furniture, not a seat interaction. No arm divisions,
animations, rigs, sockets, destruction or interiors. Placement must preserve passage
mouths and car exits; this delivery does not select district positions or usable
walking widths.

## Source, export and materials

- Source: `art/source/models/environment/city_seating_01/city_seating_01.blend`.
- Export collection: `export_city_seating_01`; root `CitySeating01`, mesh
  `CitySeating01_Mesh`. Seven closed components joined into one export mesh.
- Export: `art/models/environment/city_seating_01/city_seating_01.glb`, retained
  `.glb.import` identity. No studio objects, lamps or cameras in source/export.
- Tools: `tools/asset_production/city_seating_01/`: parametric `author.py`, explicit
  `export.py`, binary/source `validate.py`, isolated `render.py`, engine `check.gd`,
  saved `physics_check.tscn`, and lean evidence `manifest.py`.

Three opaque, backface-culled Principled material surfaces, actual export order:

| Slot | Name | Linear base RGB | Metallic | Roughness |
| --- | --- | --- | --- | --- |
| 0 | `seating_ivory` | (.82, .80, .67) | 0 | .48 |
| 1 | `seating_petrol_trim` | (.045, .10, .115) | .35 | .40 |
| 2 | `seating_slate` | (.23, .30, .34) | .15 | .48 |

No textures or embedded images needed. No material override/remap. Blender
**5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; export loads the shared
`tools/assets/blender/export_settings.json`, selects only the named collection,
and disables skins/animations. Modifiers are baked before saving, glTF triangulates.
Godot **4.8.dev7.official.c971f93e7** imports at scale 1, with default generated
LODs/shadow meshes. No manually authored LOD or platform performance claim.

## Prefab and collision

`scenes/prefabs/environment/city_seating_01.tscn` has a linked identity-transform
`Visuals/Model` imported instance, with no embedded mesh or runtime composition.
Root UID `uid://c3ailcxgje5bn`; import UID `uid://djjt56ofiyf27`. Node IDs and
resource dependency UIDs were generated/retained by headless Godot normalization.
Scene UIDs live in the scene headers; the engine-generated GDScript UID sidecar is
retained with `check.gd`.

One static-world body at `Collision/Body`, layer 1 / mask 0, owns a minimal two-box
compound, separate from decoration:

- `Seat`: size (2.40, .46, .68), centre (0, .23, 0). A deliberate ground-to-seat
  blocking envelope fills the space under/between the piers; no crawling mechanic.
- `Back`: size (2.40, .46, .17), centre (0, .69, .255). Ends at .92 m and closes the
  .03 m decorative seat/back gap. The air above the front seat remains clear.

Bevels/support details do not make snaggy collision. Fixture floor is test-only
collision, not a new visible mesh or world placement. A .35 m-radius / 1.8 m-high
capsule exercises the production `ActorMotion.step` API, not copied motion formulas.

## Evidence and validation

[Hero](city_seating_01-evidence/hero.png), [side](city_seating_01-evidence/side.png),
[seat/rim/support detail](city_seating_01-evidence/detail.png),
[47 m / 42° overhead](city_seating_01-evidence/overhead_47m_42deg.png).
All are isolated Blender Cycles CPU renders, 32 samples with denoising, AgX,
1280×720 maximum, losslessly compressed PNG after 7-bit-per-channel RGB quantization
(361–400 KiB). Overhead is vertical-down perspective, fixed north-up, 47 m height,
42° vertical FOV; the active production cleanliness rule supersedes historical
1280×800 evidence dimensions. Studio illumination is not a city lighting result.

Self-inspection: the broad back and seat read as low public furniture; the dark
under-rim and piers provide separation at close range. The side framing was widened
to retain margins. At gameplay scale the roughly 49×14-pixel pale footprint remains
visible, with a rear ridge, while the fine support/rim detail appropriately recedes.
Actual engine populated-scene readability remains pending, especially against pale
paving. The small overhead evidence is not enlarged or substituted with a hero view.

Measured source and actual binary GLB results in
[validation.json](city_seating_01-evidence/validation.json):

- **1,316 triangles, 672 source vertices, 805 exported vertices, one mesh, three
  surfaces; GLB 36,804 bytes.** Exported splits reflect shading/material seams.
- Zero degenerate faces/triangles and zero non-manifold edges; consistent winding,
  finite positions, unit-length corner/export normals, positive source volume.
- Source, binary GLB and engine AABBs agree within .001 m, with ground datum zero.
- Fresh independent export is **byte-identical** to the delivered GLB; SHA-256
  `d2277391bf1a89d4f539b537944421523deccb40f3f49f4832851cc917343727`.
- Headless import, dependency resolution, imported identity transforms, opaque
  materials and stable prefab/fixture save/reload pass.
- Three physics rays confirm the solid seat, the rear backrest at height .70 m,
  and unobstructed air at 1.10 m.
- Six 60-tick actor movement cases: authority and replay each block from front
  (Z=-.690065 m), block from rear (Z=.690172 m), and bypass at X=1.70 m to Z=3.0 m.
  Corresponding authority/replay outcomes are equal. These are local simulation
  cases, **not multiplayer transport or vehicle contact acceptance**.
- Full production checks passed: owned-script formatting/style/compilation,
  14 Python tests, GUT 86/86 tests (2,178 assertions), and expected negative-test
  failure detection. No pre-existing failures needed exemption.

Diagnostics: Blender emits `Material.use_nodes` deprecation notices under the
required pin. Headless editor normalization passed its assertions but emitted
editor shutdown RID/ObjectDB leak diagnostics plus the MCP plugin's 4.8-version
warning. Standalone asset physics and the isolated production-check mirror passed
without error/warning diagnostics. These editor-only diagnostics are recorded,
not counted as a clean editor log. No live owner session was accessed. No windowed
editor synchronization or inherited-scene claim is made.

## Exact reproduction

From repository root in Bash; scratch output is outside the checkout. `mise exec`
exposes the pinned engine/style tools for the canonical checks. All Blender calls
use isolated factory startup, four threads, disabled audio, and bounded timeouts.

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
ASSET=city_seating_01
TOOLS=tools/asset_production/$ASSET
TMP=C:/tmp/ft/assets/$ASSET
mkdir -p "$TMP"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/author.py"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/export.py"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/export.py" -- "$TMP/reexport"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/validate.py" -- "$TMP/reexport/$ASSET.glb"
timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/render.py"
timeout 300 "$(mise which godot)" --headless --editor --path . --import --quit
timeout 180 "$(mise which godot)" --headless --editor --path . --script "res://$TOOLS/check.gd" -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script "res://$TOOLS/check.gd"
"$(mise which gdstyle)" fmt --check "$TOOLS/check.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$TOOLS/check.gd"
# Checks require a fresh empty output path; use a new suffix on repeated reviews.
timeout 1800 mise exec -- python tools/production_checks.py --output "$TMP/checks"
python "$TOOLS/manifest.py" "$TMP/checks"
```

The manifest command compacts the four renders, adds check/render receipts to
validation.json and hashes every produced payload (excluding the manifest itself).
[manifest.json](city_seating_01-evidence/manifest.json) is producer evidence, not an
independent acceptance verdict. Raw scratch logs remain under `C:/tmp/ft/assets/`
and are not repository payloads.

## Remaining acceptance

Independent art/technical review remains pending. World integration owns actual
placement, street-furniture zones, passage/exit clearance and physics/aim behavior
in context. Vehicle contact/turning, real-process multiplayer collision and
transport/prediction, populated engine camera readability, package/device checks
and repeated-placement GPU/frame cost are not performed. No Deck/performance,
world placement or whole-register READY claim; no sitting interaction requested.
