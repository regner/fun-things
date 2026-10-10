# city_waste.03 — Service dumpster

**Source, export, linked prefab and bounded headless checks delivered; independent
review and world/gameplay acceptance pending.** Produced by the commissioned
implementation specialist on `lane/a-waste`. This task resumes the
[production commission](commission.md) and supersedes the concept-only status in
[city_waste](../city_waste.md). The supervisor owns acceptance and shared-register
updates; neither the queue nor shared progress was edited.

## Design and dimensions

An original closed service dumpster: wide tapered steel body, twin sage lids with
broad stiffeners, folded rim/base rails, open-ended side fork sleeves and two fixed
skids. Faded petrol paint and two small irregular rust islands on the lower front,
plus sleeve-edge wear, provide Ironreach's restrained worn finish without noisy
grime. No logos, text, bright hazard stripes or pickup-like accents.

The [public bin](city_waste_01.md) and [domestic wheelie bin](city_waste_02.md) were
read and visually inspected. This member retains their muted palette and soft
manufactured highlights, while its width, twin lid seam, steel sleeves and fixed
skids distinguish it from the stationary public crown and wheeled domestic taper.
Body paint is lighter and rougher than those siblings to suggest fading; the lid,
recess and hardware retain the family color references. No sibling was modified.

Direction follows [Petrol & Coral](../../art-direction.md), the
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [Ironreach revision 02](../../concepts/districts-v1/ironreach.md). Ironreach is
the required use; Broadlot/East Docks supporting uses and Old Quay/Signal Row
candidates remain unconfirmed. Place by workshop/fence edges, never inside gateways,
walking routes or the two-exit yard's foot bypass. The
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) is context,
not permission to narrow its routes.

Dimensions are **provisional authoring choices**, allowed by the production task,
not concept-image measurements or approved clearance specifications:

| Element | Metres |
| --- | --- |
| Overall Godot X / Y / Z size | 2.320 / 1.550 / 1.420 |
| Body bottom width / depth / height datum | 1.900 / 1.050 / .200 |
| Body top width / depth / height datum | 2.100 / 1.260 / 1.360 |
| Reinforced rim width / depth | 2.200 / 1.360 |
| Each lid width / depth / thickness | 1.075 / 1.420 / .100 |
| Lid top / stiffener top height | 1.500 / 1.550 |
| Central lid plan seam | .030 |
| Each ground skid width / depth / height | .180 / 1.120 / .180 |
| Skid center X | ±.730 |
| Sleeve outside width / length | .180 / .880 |
| Visual AABB minimum | (-1.160, 0, -.710) |
| Visual AABB maximum | (1.160, 1.550, .710) |
| Acceptance tolerance | .001 |

Root and mesh pivots are identity at the ground-centered body footprint; both skids
contact zero. Blender +Y is front (lid grips and localized rust), mapped once to
Godot -Z; +Z maps to Godot +Y. Metre units, unit scale, applied object transforms
and no corrective prefab transforms. There are no lift/hinge sockets: fork sleeves
and hinge barrels are static visual details, not a collection-system interface.

## Source, export and materials

- Source: `art/source/models/environment/city_waste_03/city_waste_03.blend`.
- Collection: `export_city_waste_03`; root `CityWaste03`; mesh `CityWaste03_Mesh`.
- Export: `art/models/environment/city_waste_03/city_waste_03.glb`, with retained
  Godot `.import` metadata. No prototype or external model dependencies.
- Authoring, export, render, validator, engine check and manifest scripts:
  `tools/asset_production/city_waste_03/`.
- Prefab: `scenes/prefabs/environment/city_waste_03.tscn`.

Entirely original Blender construction; no downloads, purchased meshes,
image-to-mesh, external textures or fonts. Closed solid subparts are joined into
one mesh, with deliberate internal manufacturing overlaps rather than a boolean
union. Each subpart is watertight and consistently wound. Three-segment bevels and
weighted normals provide broad highlights. Thin polygonal paint-loss islands use
flat normals so their narrow edge faces remain correctly shaded. Fork sleeves use
four closed bars with real open ends, rather than a painted black fake opening.
Studio plane/lights/cameras exist only in the temporary render scene, never in the
saved source/export. No visible node hierarchy is composed at runtime.

The tools follow the sibling authoring and asset-specific validation conventions.
The existing shared `tools/assets/blender/export_settings.json` and production
check runner are reused unchanged. There is no shared generic waste-model helper
API; no new shared framework or duplicated export-settings contract was introduced.
Five opaque, non-emissive, back-culled Principled surfaces, in exported slot order:

| Slot | Material | Linear RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `waste_body_petrol` | .060 / .115 / .115 | .25 / .64 |
| 1 | `waste_recess_charcoal` | .016 / .025 / .029 | .15 / .68 |
| 2 | `waste_hardware_slate` | .170 / .215 / .225 | .50 / .42 |
| 3 | `waste_lid_sage` | .100 / .165 / .155 | .20 / .57 |
| 4 | `waste_localized_rust` | .115 / .058 / .034 | 0 / .86 |

These are asset-local materials, not overrides of sibling materials. No textures,
embedded images, rig, animation, opening, loot, collection, rolling physics, debris
or destruction systems. No explicit LOD is authored; Godot's default asset-local
automatic LOD import is retained. Repeat-placement profiling remains pending; no
polygon/device budget is claimed.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. Export selects
only the named collection and disables skins/animations. Godot
**4.8.dev7.official.c971f93e7** is the only engine used.

## Prefab and bounded collision checks

`Visuals/Model` is an identity-transform linked GLB instance with no embedded mesh
replacement or material overrides. Separate `Collision/Body` is a static body,
layer 1 / mask 0, with **one box**: 2.320 × 1.550 × 1.420 m centered at
(0, .775, 0). It covers the complete closed prop, conservatively filling the taper,
skid underside and sleeve gaps to avoid tiny snag-producing colliders. No dynamic
body or interaction code was added.

The prefab and saved `collision_check.tscn` fixture were loaded, packed/resaved,
reloaded and resaved headlessly. Both second saves are byte-stable; resource UIDs,
imported ancestry, five materials, bounds and dependencies pass. Scene UIDs and
node IDs are embedded; the check script's `.gd.uid` is retained. The task excludes
live editor sessions and windowed editors, so direct text authoring plus pinned
headless normalization was the required fallback. No live Blender/Godot session
was used or claimed synchronized by these checks.

The fixture exercises production `ActorMotion.step` and `FootCommand` with the
0.35 m radius / 1.8 m capsule, 60 fixed ticks per case in authority and replay modes:

| Case | Observed | Independent expectation |
| --- | --- | --- |
| Rear (+Z) contact | Z 1.060065031 m | 1.060 ± .002 m |
| Side (+X) contact | X 1.510065079 m | 1.510 ± .002 m |
| Front (-Z) contact | Z -1.060065031 m | -1.060 ± .002 m |
| Clear bypass at X 1.600 m | Z -2.999999762 m | -3 ± .002 m |

Both modes give equal results. The body ray hits the actual dumpster static body
at rear Z .710 m; an above-lid ray at Y 1.650 m remains clear. These are bounded
local simulation/query checks, not car handling, placed-world movement or
multiplayer transport/admission/prediction acceptance.

## Evidence and reproduction

[Hero](city_waste_03-evidence/hero.png) · [side](city_waste_03-evidence/side.png) ·
[fork sleeve/wear detail](city_waste_03-evidence/detail.png) ·
[47 m / 42° overhead](city_waste_03-evidence/overhead_47m_42deg.png).
All four are isolated Blender CPU Cycles renders, 32 samples, AgX, 1280×720,
compressed PNG. Overhead is vertical-down perspective at 47 m with **42° vertical
FOV**, Blender +Y at image top. The latest 720-pixel evidence cap supersedes the
older 1280×800 requirement. Seven significant color bits reduce background entropy.

All final views were inspected against the sibling and accepted lamp evidence.
Hero and side framing was widened for breathing room. The initial binary-normal
validator caught inverted shading on thin rust-island edge triangles; those islands
were changed from weighted smoothing to flat normals, then the source, export and
all renders were regenerated. Final geometry passes the unchanged winding criterion.
At gameplay distance the twin lid seam and broad rectangular footprint remain quiet
and distinct; fine rust and sleeve details disappear intentionally. This is not an
in-engine character-contrast or populated-street readability proof.

Final source/export: **6,056 triangles; 3,096 Blender vertices; 3,744 GLB vertices;
one mesh; five surfaces; zero degenerate faces and zero non-manifold edges**.
Finite coordinates, unit source/GLB normals, consistent winding, independent literal
bounds and ground datum pass. Actual GLB binary positions/indices/normals are
checked, not merely accessor metadata. Fresh-process re-export is **byte-identical**,
161,224 bytes, SHA-256
`45dcd053988e0cbf56381808d0afa7d04bc3fd8f2189eb5b3cdae3b81795e2ce`.

From repository root in Bash; logs/scratch outputs remain outside the checkout:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
TMP='C:/tmp/ft/assets/city_waste_03'
mkdir -p "$TMP"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_waste_03/author.py
timeout 600 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_waste_03/render.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 art/source/models/environment/city_waste_03/city_waste_03.blend --python tools/asset_production/city_waste_03/export.py -- "$TMP/reexport"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_waste_03/validate.py -- "$TMP/reexport/city_waste_03.glb"
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script tools/asset_production/city_waste_03/check.gd -- --normalize
timeout 180 "$GODOT" --headless --path . --script tools/asset_production/city_waste_03/check.gd
# Use a fresh empty checks directory on each run.
timeout 1800 mise exec -- python tools/production_checks.py --output "$TMP/checks"
python tools/asset_production/city_waste_03/manifest.py "$TMP/checks"
```

`manifest.py` requires Pillow, as do other asset evidence tools.
[validation.json](city_waste_03-evidence/validation.json) records geometry, material
values, engine observations and production-check outcomes.
[manifest.json](city_waste_03-evidence/manifest.json) hashes every delivery payload
except itself; [final.log](city_waste_03-evidence/final.log) is the concise receipt.
The complete production suite passes: owned-script formatting/lint/compilation,
**14 Python tests**, **86 GUT tests / 2,178 assertions**, and expected-failure
detection. No failure exemptions were needed.

Diagnostics remain explicit: Blender reports `use_nodes` deprecation for future
6.0; editor import warns the existing MCP plugin was last tested against 4.7.
Normalization assertions and exit status pass, but editor shutdown reports
renderer/text RID and ObjectDB leaks. The runtime resource/physics check exits 0
without ERROR/WARNING/SCRIPT ERROR diagnostics, and the complete isolated production
suite passes. No broad diagnostic suppression or vendor changes were made.

## Remaining acceptance

Independent technical/art review is pending. World integration must confirm final
dimensions, supporting district uses and placements; preserve walking/car routes
and check actual actor contrast/occlusion in the engine camera. Car contact,
real-process multiplayer transport/admission/prediction, packaged builds, Deck
readability and sustained repeat-placement performance remain untested. No world
scene, gameplay system, shared tracker, TODO or READY status was changed.
