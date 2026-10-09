# d06_commercial_graphics.01 — Hall title graphic

9 October 2026. **Artwork/material/linked-prefab candidate delivered; independent review
and world/gameplay/device acceptance pending.** Commission: [production](commission.md).
Family: [Signal Row graphics](../d06_commercial_graphics.md). Producer: assigned lane
worker on `lane/a-d06gfx`; supervisor approved the implementation direction and retains
acceptance authority. No other family records or shared hardware were edited.

## Design, provenance and scope decision

**AFTER HOURS / HALL**, with the proposed district line **OPEN LATE. DECISIONS EARLY.**
A large split magenta/cyan clock-ring is the primary graphic, with ivory clock hands,
rounded original capital lettering, a quiet petrol field and restrained paired end bars.
The title, emblem and provisional fictional copy were approved by the supervisor for
this production pass. No real brand, downloaded font, texture or generated image was used.
Every letter skeleton and graphic stroke is explicitly authored in the committed
Python/Pillow recipe; no external font files or attribution dependencies exist.

Followed the accepted district identities, Signal Row v03 and stage-04 streets:
frontage accents, quiet roofs/roads, no inferred building dimensions or world placement.
This is a **decorative title**, not mandatory text-dependent navigation.

The supervisor explicitly resolved the family/common-brief interface conflict:
**reuse the unchanged accepted fascia; do not export another carrier or add a coplanar
panel.** The artwork set's Blender-sourced face requirement is satisfied by the existing
`city_shop_fittings_02` source → GLB → linked prefab chain. Consequently there is no
redundant per-ID `.blend`, GLB or `export.py`. Source verification/reexport uses the
existing hardware owner's validator/exporter. New deliverables are the reproducible
artwork, PNG/import settings, material, face-only prefab override and lean evidence.

### Family palette and graphic grammar

| Role | sRGB | Treatment |
| --- | --- | --- |
| Field | `#102C3C` | Quiet petrol, over 65% of the artwork |
| Hall top arc / accent | `#F54BBA` | Magenta |
| Hall lower arc / divider | `#45DFE5` | Cyan |
| Copy / hands | `#F6F1DC` | Warm ivory |

The split clock-ring belongs to the hall. Later shop/poster/wayfinding records should
retain this palette family and smooth broad shapes while using different dominant
symbols/layouts; they should not duplicate the hall identity. No neon light nodes,
bloom-dependent details, alpha overlays, grime or roof graphics were introduced.

## Source, runtime outputs and dimensions

- Editable art source: `tools/asset_production/d06_commercial_graphics_01/author.py`.
  Python 3.14.2, Pillow 12.3.0. It supersamples original paths at 3× and downsamples once.
- Runtime: `art/textures/environment/d06_commercial_graphics_01/hall_title_albedo.png`
  plus `.import`, **2000 × 400 RGB**, 5:1 aspect, opaque sRGB albedo.
- Material: `art/materials/environment/d06_commercial_graphics_01/hall_title.tres`.
  White multiplier, roughness 0.56, metallic 0, opaque, backface culling, no emission.
  Linear mipmapped filtering (Godot default enum 3), clamp/no repeat; lossless texture
  import, mipmaps on, automatic 3D compression changes disabled. No extra maps.
- Prefab: `scenes/prefabs/environment/d06_commercial_graphics_01.tscn`.
  `Visuals/Model` is the unchanged linked shared GLB at identity transform.
- Existing geometry source:
  `art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend`.
  Collection `export_city_shop_fittings_02`; root `city_shop_fittings_02`.
- Existing runtime model:
  `art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb`.
  Original hardware source/export contract and material slots:
  [fascia handoff](city_shop_fittings_02.md).

| Interface | Inherited measurement |
| --- | --- |
| Whole fascia X/Y/Z (Godot) | **3.200 × 0.800 × 0.140 m** |
| Godot local AABB | min **(-1.600, -0.400, -0.140)**, max **(1.600, 0.400, 0)** m |
| Mounting pivot | Wall-contact centre `(0,0,0)`, not ground-centred |
| Face | **3.000 × 0.600 m**, Godot Z=-0.128 |
| Safe content | Centred **2.940 × 0.540 m**; outer 20 px margins stay petrol |
| UV0 | U grows toward Blender -X; V toward +Z; glTF flips V storage |
| Mounting proposal | Centre 3.8 m above ground, flat vertical bay; unchanged shared contract |
| Bound tolerance | ±0.001 m; actual source validator enforces tighter 1e-6 |

No additional geometry, rig, animation, LOD, collider, navigation, interaction or
world-placement writer. The facade owns blocking collision. Keep this prefab separate
from structural walls and do not stack it with another fascia at the same position.

## Saved override and identity contract

The headless importer adds an outer root. The actual override is exactly:

`Visuals/Model/city_shop_fittings_02/fascia_artwork_carrier`

Only `surface_material_override/0` changes, checked against the original slot name
`fascia_artwork_face`. The back/sides remain `fascia_mount_metal`; the other six meshes
and all transforms remain untouched. No mesh data or global `material_override` is
embedded in the wrapper. The linked model is not made local.

The supervisor approved this **saved editable-child surface override** for this lane.
This is an explicit narrow exception to the ordinary preference for wrapper-level
appearance APIs. No runtime material-application script was added. Godot stored the
prefab/material UIDs inline, the texture UID in `.import`, and the test script UID in
its `.uid`; separate scene/material `.uid` sidecars are not generated by this engine.
The prefab retains imported parent-ID paths and child identity. Two successive
load/pack/save cycles and a subsequent invocation preserved the exact scene bytes.
Future shared-hardware reexports must recheck this override path/identity; this pass
proves the current unchanged GLB, not arbitrary hierarchy migrations.

Editor tools/live MCP were intentionally not used under the common production brief.
Authored text was loaded, packed and saved by the pinned headless editor only; no
separate owner's open scene was accessed, refreshed or claimed synchronized.

## Evidence and measured validation

[Hero](d06_commercial_graphics_01-evidence/hero.png),
[side](d06_commercial_graphics_01-evidence/side.png),
[detail](d06_commercial_graphics_01-evidence/detail.png),
[47 m / 42° overhead](d06_commercial_graphics_01-evidence/overhead_47m_42deg.png).
All four are isolated **Blender** renders, 1280×800, Cycles CPU 32 samples, AgX,
with no source save and no duplicated hardware. Camera transforms/light values are
in `preview.py`. The overhead camera is vertical/north-up at Blender `(0,10,47)`;
the vertical fascia is temporarily translated to mounting height 3.8 m, not tilted
or enlarged. All other render transforms are unchanged source coordinates.

Self-inspected all four images and the source PNG. Hero/side/detail show upright,
unmirrored lettering, the full split emblem, clean inset seating and no unwanted
hardware recolouring. The real-scale overhead gives only an approximately **75×7 px**
strip; **neither emblem nor title reliably identifies the hall at that camera**.
This limitation was reported to the supervisor. It is not solved by increasing
texture resolution. A separately owned hall roof-ring/architectural cue and actual
world placement must carry gameplay identity. No text or symbol readability acceptance
is claimed for the overhead view.

[validation.json](d06_commercial_graphics_01-evidence/validation.json) records:

- Existing geometry: **836 source vertices, 1,072 GLB vertices, 1,656 triangles,
  seven meshes, eight surfaces**, five unchanged hardware materials.
- **Zero degenerate faces/triangles, zero non-manifold edges**, consistently wound
  closed solids and unit-length corner normals; applied transforms and metre units.
- Independent headless Godot checks: seven identical imported mesh resources, one
  face-only override, exact inherited bounds, no collisions, loaded texture/material
  dependencies, identity `Visuals/Model`, and stable saved scene bytes/IDs.
- Blender **5.2.2 LTS**, build `d13f752e3b9c`, exporter **5.2.40**: fresh saved-source
  shared GLB reexport **byte-identical**, 45,616 bytes, SHA-256
  `4fd2106f09ef4a35edafbcf3a3a68ea94983e721fd84d852a406e2d26de6552f`.
- Four artwork tests: exact size/opaque RGB, safe margins/quiet field, independent
  emblem colour/gap pixels and fresh scripted PNG byte identity. All pass.
- Pinned gdstyle 0.3.0: owned script lint and format pass. Production checks pass:
  owned formatting/style/explicit compilation, nine Python tool tests, 23 GUT tests
  / 196 assertions, import, and the intentional negative diagnostic test.

[manifest.json](d06_commercial_graphics_01-evidence/manifest.json) hashes every produced
payload, including import metadata, scripts, this record, four renders and validation;
only the manifest itself and uncommitted Python cache are excluded. Shared dependencies
are hashed separately in validation and remain unchanged. Lean final outcomes are in
[final_checks.log](d06_commercial_graphics_01-evidence/final_checks.log); scratch exports,
full logs and intermediate receipts remain outside Git in `C:/tmp/ft/assets/d06_commercial_graphics_01/`.

## Reproduction

From this worktree root, with Python 3.14.2 / Pillow 12.3.0 available:

```sh
python tools/asset_production/d06_commercial_graphics_01/author.py
python -m unittest discover -s tools/asset_production/d06_commercial_graphics_01 -p 'test_*.py' -v

# Source audit calls the existing hardware exporter, writing ONLY scratch outputs.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/d06_commercial_graphics_01/validate.py

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/d06_commercial_graphics_01/preview.py

timeout 300 "$(mise which godot)" --headless --editor --path . --import
# Only use normalization when intentionally saving the owned resources.
timeout 180 "$(mise which godot)" --headless --editor --path . \
  --script res://tools/asset_production/d06_commercial_graphics_01/check_prefab.gd -- --normalize
# Non-mutating runtime dependency/override check:
timeout 180 "$(mise which godot)" --headless --path . \
  --script res://tools/asset_production/d06_commercial_graphics_01/check_prefab.gd
"$(mise which gdstyle)" check tools/asset_production/d06_commercial_graphics_01/check_prefab.gd
"$(mise which gdstyle)" fmt --check tools/asset_production/d06_commercial_graphics_01/check_prefab.gd
# Choose a fresh output directory for every full suite run.
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/d06_commercial_graphics_01/checks_reproduce
python tools/asset_production/d06_commercial_graphics_01/manifest.py
```

The retained validation.json combines source, engine, artwork and production receipts.
Re-running `validate.py` refreshes its source/export section; retain the separate engine
receipt at the scratch `prefab.json` and normalization receipt before assembling a new
review record. `manifest.py --write` is an explicit producer operation after such changes;
plain invocation verifies the current retained record without rewriting it.

## Diagnostics, corrections and remaining gates

- Initial prefab override omitted the importer-added root; Godot warned that the
  child had vanished, then the validator assertion failed and the bounded invocation
  timed out. Corrected to the actual imported path above, not to duplicate geometry.
  Current non-mutating headless load passes with **no ERROR/WARNING/SCRIPT ERROR**.
- Initial owned GDScript formatting/complexity warnings made the first production
  suite fail; factored named validation helpers and fixed formatting. The corrected
  full suite passes all layers; no failures were ignored as pre-existing.
- Headless editor normalization returns 0 and passes byte/UID checks but emits the
  addon 4.8-versus-4.7 warning and editor shutdown scan/RID/ObjectDB leak diagnostics.
  These are retained in the concise log, not hidden or counted as a clean editor exit.
  Full import and non-editor load are separately checked. No live MCP calls were made.
- Blender render node API deprecation warnings remain; pinned renders and validator
  exit 0. The `--version` probe alone emitted a tiny shutdown allocation diagnostic;
  actual production render/validation runs did not.

Pending: independent art/technical review, final copy selection, hall/flat-bay placement,
actual renderer/gameplay camera and populated-world visibility, future shared-hardware
reexport identity retention, packaged target-device filtering/performance and sustained
Deck tests. No world, collision, multiplayer or gameplay behaviour was changed, so this
asset does not claim new movement/network evidence or authorize a hall placement.
