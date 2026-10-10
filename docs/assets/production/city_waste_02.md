# city_waste.02 — Domestic wheelie bin

**Source, export, linked prefab and bounded headless checks delivered; independent
review and world/gameplay acceptance pending.** Produced by the commissioned
implementation specialist on `lane/a-waste`. This task resumes the
[production commission](commission.md) and supersedes the concept-only status in
[city_waste](../city_waste.md). The supervisor owns acceptance and shared-register
updates; neither the queue nor shared progress was edited.

## Design and dimensions

An original closed domestic wheelie bin: tapered petrol plastic body, broad flat
sage lid with two shallow molded ribs, front lifting lip, rear carry handle and two
charcoal wheels with slate hubs. No service-door panel, barrel crown or stationary
plinth: those distinguish the [public-bin sibling](city_waste_01.md). The sibling's
muted four-color palette, soft bevels and restrained detail are preserved, with
nonmetallic, rougher plastic surfaces for this domestic member. No branding, bright
pickup-like markings, text, grime or additional appearance variants.

Direction follows [Petrol & Coral](../../art-direction.md) and the
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md).
Domestic dressing supports The Crescents' small house plots and possible Terrace
Ward use; actual supporting district uses remain unconfirmed. Placement must keep
foot shortcuts, court entrances and service/yard exits clear under the
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md).

Dimensions are **provisional authoring choices**, allowed by the production task,
not concept-image measurements or approved clearance specifications:

| Element | Metres |
| --- | --- |
| Overall Godot X / Y / Z size | 0.630 / 1.100 / 0.740 |
| Body bottom width / depth | 0.440 / 0.430 |
| Body rim width / depth / height | 0.560 / 0.560 / 1.005 |
| Lid width / depth / top height | 0.600 / 0.640 / 1.080 |
| Rib top height | 1.100 |
| Rear wheel diameter / thickness | 0.220 / 0.070 |
| Wheel centers in Godot axes | (±0.275, 0.110, 0.220) |
| Rear handle width / bar thickness | 0.490 / 0.060 |
| Handle-to-lid central plan gap | 0.040 |
| Visual AABB minimum | (-0.315, 0, -0.330) |
| Visual AABB maximum | (0.315, 1.100, 0.410) |
| Acceptance tolerance | 0.001 |

Root and mesh pivots are identity at the ground-centered **body footprint**, not
the rear-overhanging handle. The toe and wheels contact ground at zero; hubs add
5 mm beyond each wheel outer face. Blender +Y is front (lifting lip) and maps once
to Godot -Z; +Z maps to Godot +Y. The rear handle produces the asymmetric Z bounds.
Metre units, unit scale, applied object transforms, no corrective prefab transforms.

## Source, export and materials

- Source: `art/source/models/environment/city_waste_02/city_waste_02.blend`.
- Collection: `export_city_waste_02`; root `CityWaste02`; mesh `CityWaste02_Mesh`.
- Export: `art/models/environment/city_waste_02/city_waste_02.glb`, with retained
  Godot `.import` metadata. No prototype or external model dependencies.
- Recipe, export, render, geometry validator, engine check and manifest scripts:
  `tools/asset_production/city_waste_02/`.
- Prefab: `scenes/prefabs/environment/city_waste_02.tscn`.

Entirely original Blender construction; no downloads, purchased meshes, generated
image-to-mesh assets, external textures or fonts. Closed solid subparts are joined
into one mesh; deliberate internal manufacturing overlaps are not a boolean union.
Every subpart is watertight and consistently wound. Applied three-segment bevels
and weighted normals retain broad highlights; wheel silhouettes use 24 segments,
hubs 20. The studio plane, lights and cameras exist only in `render.py`'s temporary
scene, never in the saved source or export.

The per-asset tooling follows the sibling's established recipe/check conventions;
the export consumes the shared `tools/assets/blender/export_settings.json` rather
than introducing a competing export contract. No shared tooling or sibling file
was modified. Four opaque, non-emissive, back-culled Principled surfaces, in actual
exported slot order:

| Slot | Material | Linear RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `waste_body_petrol` | .035 / .085 / .090 | 0 / .58 |
| 1 | `waste_recess_charcoal` | .016 / .025 / .029 | 0 / .72 |
| 2 | `waste_lid_sage` | .100 / .165 / .155 | 0 / .54 |
| 3 | `waste_hardware_slate` | .170 / .215 / .225 | .50 / .42 |

Material names/colors match the sibling family reference; these are asset-local
materials, not overrides of the public bin's materials. No textures, embedded
images, rig, animation, sockets, opening, loot, collection, rolling physics, debris
or destruction systems. The wheels, lid and handle are static geometry only.
No explicit LOD is authored; Godot's default asset-local automatic LOD import is
retained. Repeated-prop profiling remains pending; no polygon/device budget is claimed.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. Export selects
only the named collection and disables skins/animations. Godot
**4.8.dev7.official.c971f93e7** is the only engine used.

## Prefab and bounded collision checks

`Visuals/Model` is an identity-transform linked GLB instance, with no embedded mesh
replacement or material overrides. `Collision/Body` is a separate static body,
layer 1 / mask 0, with **one box**: 0.640 × 1.100 × 0.740 m centered at
(0, .550, .040). Its Z bounds match the full front-lip/rear-handle envelope; X pads
the hubs by 5 mm each side. The single conservative box intentionally fills the
tapered silhouette and wheel/handle gaps without snag-producing small colliders.
No interaction code or dynamic body was added.

The prefab and saved `collision_check.tscn` fixture were loaded, packed/resaved,
reloaded and resaved headlessly. Both second saves are byte-stable; resource UIDs,
imported ancestry, four materials, bounds and dependencies pass. Scene UIDs and node
IDs are embedded; the check script's `.gd.uid` is retained. The task excludes live
editor sessions and windowed editors, so direct text authoring plus pinned headless
normalization was the required fallback. No live Blender/Godot session was used or
claimed synchronized by these checks.

The fixture exercises production `ActorMotion.step` and `FootCommand` with the
0.35 m radius / 1.8 m capsule, 60 fixed ticks per case in authority and replay modes:

| Case | Observed | Independent expectation |
| --- | --- | --- |
| Rear (+Z) contact | Z 0.760065019 m | 0.760 ± .002 m |
| Side (+X) contact | X 0.670064986 m | 0.670 ± .002 m |
| Front (-Z) contact | Z -0.680064976 m | -0.680 ± .002 m |
| Clear bypass at X .75 m | Z -2.999999762 m | -3 ± .002 m |

Both modes give equal results. The body ray hits the actual bin static body at
rear Z .410 m; an above-lid ray at Y 1.2 m remains clear. These are bounded local
simulation/query checks, not car handling, placed-world movement or multiplayer
transport/admission/prediction acceptance.

## Evidence and reproduction

[Hero](city_waste_02-evidence/hero.png) · [side](city_waste_02-evidence/side.png) ·
[handle/lid detail](city_waste_02-evidence/detail.png) ·
[47 m / 42° overhead](city_waste_02-evidence/overhead_47m_42deg.png).
All four are isolated Blender CPU Cycles renders, 32 samples, AgX, 1280×720,
compressed PNG. Overhead is vertical-down perspective at 47 m with **42° vertical
FOV**, Blender +Y at image top. The latest 720-pixel evidence cap supersedes the
older 1280×800 requirement. Seven significant color bits reduce background entropy.

All final views were inspected against the public bin and accepted lamp evidence.
The initial handle's narrow slot was widened to a 40 mm central plan gap, then the
source, export and all renders were regenerated. Hero and side show complete toe/
wheel contact and the domestic taper. The lid is a small quiet rectangular cue
from gameplay distance; ribs and hubs intentionally disappear. This does not prove
in-engine actor contrast or populated-street readability, and no bright marking was
added to force this small background prop to compete with characters.

Final source/export: **3,052 triangles; 1,552 Blender vertices; 1,908 GLB vertices;
one mesh; four surfaces; zero degenerate faces and zero non-manifold edges**.
Finite coordinates, unit source/GLB normals, consistent winding, independent literal
bounds and ground datum pass. Actual GLB binary positions/indices/normals are checked,
not merely accessor metadata. Fresh-process re-export is **byte-identical**,
83,440 bytes, SHA-256
`642848a43fbea37a1d5cefda46886e255c25185a1097b7c8d4ca4dd4b904d1c7`.

From repository root in Bash; logs/scratch outputs remain outside the checkout:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
TMP='C:/tmp/ft/assets/city_waste_02'
mkdir -p "$TMP"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_waste_02/author.py
timeout 600 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_waste_02/render.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 art/source/models/environment/city_waste_02/city_waste_02.blend --python tools/asset_production/city_waste_02/export.py -- "$TMP/reexport"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_waste_02/validate.py -- "$TMP/reexport/city_waste_02.glb"
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script tools/asset_production/city_waste_02/check.gd -- --normalize
timeout 180 "$GODOT" --headless --path . --script tools/asset_production/city_waste_02/check.gd
# Use a fresh empty checks directory on each run.
timeout 1800 mise exec -- python tools/production_checks.py --output "$TMP/checks"
python tools/asset_production/city_waste_02/manifest.py "$TMP/checks"
```

`manifest.py` requires Pillow, as do other asset evidence tools.
[validation.json](city_waste_02-evidence/validation.json) records geometry, material
values, engine observations and production-check outcomes.
[manifest.json](city_waste_02-evidence/manifest.json) hashes every delivery payload
except itself; [final.log](city_waste_02-evidence/final.log) is the concise final receipt.
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

Independent technical/art review is pending. World integration must confirm district
use, provisional dimensions and final placements; preserve walking/car routes and
check actual actor contrast/occlusion in the engine camera. Car contact, real-process
multiplayer transport/admission/prediction, packaged builds, Deck readability and
sustained repeat-placement performance remain untested. No world scene, gameplay
system, shared tracker, TODO or READY status was changed.
