# city_waste.01 — Public bin

**Source, export, linked prefab and bounded headless checks delivered; independent
review and world/gameplay acceptance pending.** Produced by the commissioned
implementation specialist on `lane/a-waste`. This task resumes the
[production commission](commission.md) and supersedes the concept-only status in
[city_waste](../city_waste.md). The supervisor owns acceptance and shared-register
updates; neither the queue nor shared progress was edited.

## Design and dimensions

An original closed municipal bin: softly rounded petrol body, recessed stationary
plinth, broad sage barrel crown, shut slate disposal flap and flush service door
with a small latch. No wheels, projecting handles, branding, text, grime or bright
pickup-like accent. The crown and squat stationary footprint distinguish it from
the future domestic wheelie bin and broad service dumpster. This is the first waste
family delivery; no earlier sibling outputs existed to change.

The muted palette and broad forms follow [Petrol & Coral](../../art-direction.md)
and the [district identities](../../concepts/world-v1/stage-03-district-identities/README.md).
Public-bin supporting uses across the nine districts remain unconfirmed. Placement
must keep passage mouths, intersection corners and service/yard exits clear under
[the street hierarchy](../../concepts/world-v1/stage-04-streets/README.md).

Dimensions are **provisional authoring choices**, allowed by the production task,
not measurements inferred from a concept or approved clearance specifications:

| Element | Metres |
| --- | --- |
| Overall Godot X / Y / Z size | 0.660 / 1.050 / 0.593 |
| Main body width / depth | 0.600 / 0.500 |
| Barrel crown width / depth | 0.660 / 0.580 |
| Crown shoulder / crest height | 0.940 / 1.050 |
| Plinth width / depth / height | 0.540 / 0.440 / 0.090 |
| Shut flap width / height | 0.398 / 0.074 |
| Visual AABB minimum | (-0.330, 0, -0.303) |
| Visual AABB maximum | (0.330, 1.050, 0.290) |
| Acceptance tolerance | 0.001 |

Root and mesh pivots are identity at the ground-centered body/plinth footprint.
The front flap adds a 13 mm visual asymmetry beyond the crown. Blender +Y is front
and maps once to Godot -Z; Blender +Z maps to Godot +Y. Metre units, unit scale,
applied object transforms and no corrective prefab rotation/scale.

## Source, export and materials

- Source: `art/source/models/environment/city_waste_01/city_waste_01.blend`.
- Collection: `export_city_waste_01`; root `CityWaste01`; mesh `CityWaste01_Mesh`.
- Export: `art/models/environment/city_waste_01/city_waste_01.glb`, with retained
  Godot `.import` metadata. No prototypes or external model references.
- Recipe, export, render, geometry validator, engine check and manifest scripts:
  `tools/asset_production/city_waste_01/`.
- Prefab: `scenes/prefabs/environment/city_waste_01.tscn`.

Entirely original Blender construction; no downloads, purchased meshes, generated
image-to-mesh assets, external textures or fonts. Closed joined solid subparts form
manufactured seams; their deliberate internal overlaps are not a boolean union.
Each subpart is watertight and consistently wound. Applied three-segment edge
bevels and weighted normals keep broad highlights. The crown uses a 16-step arc.
The render-only studio plane/lights/camera are created by `render.py`, never saved
into the source or exported collection.

Four opaque, non-emissive, back-culled Principled surfaces, in exported slot order:

| Slot | Material | Linear RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `waste_recess_charcoal` | .016 / .025 / .029 | .15 / .60 |
| 1 | `waste_body_petrol` | .035 / .085 / .090 | .25 / .49 |
| 2 | `waste_lid_sage` | .100 / .165 / .155 | .25 / .47 |
| 3 | `waste_hardware_slate` | .170 / .215 / .225 | .50 / .42 |

These provide a quiet material reference for later waste siblings without imposing
identical geometry or color variants. No textures, embedded images, rig, animation,
sockets, opening, collection, loot, debris or destruction systems are included.
No explicit LOD mesh is authored; Godot's asset-local default automatic LOD import
is retained. Repeat-placement profiling is still required; no polygon/device budget
is asserted.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. Export loads
`tools/assets/blender/export_settings.json`, selects only the named collection,
and disables skins/animations. Material normals/UV export follows that shared
contract. Godot **4.8.dev7.official.c971f93e7** is the only engine used.

## Prefab and bounded collision checks

`Visuals/Model` is an identity-transform linked GLB instance, with no embedded
replacement geometry or material overrides. `Collision/Body` is a separate static
body, layer 1 / mask 0, containing **one box**: 0.660 × 1.050 × 0.600 m, centered
at (0, .525, 0). It blocks the complete closed prop with no small snag-producing
colliders. The shut flap's 3 mm front projection is cosmetic; the box pads the rear
by 10 mm. No interaction code or dynamic body was added.

The prefab and saved `collision_check.tscn` fixture were loaded, packed/resaved,
reloaded and resaved headlessly. Both second saves are byte-stable; resource UIDs,
imported ancestry, materials, bounds and dependency resolution pass. Scene UIDs and
node IDs are embedded in the saved scenes; the check script's `.gd.uid` is retained.
No live Blender/Godot editor session was used. The task excludes windowed editors,
so direct text authoring plus headless normalization was the required fallback;
this does not prove synchronization with any separately open editor.

The fixture exercises actual `ActorMotion.step` and `FootCommand` with the production
0.35 m radius / 1.8 m capsule, 60 fixed ticks per case, in authority and replay modes:

- Front contact: stops at Z **0.650064945 m** (independent expectation .650 ± .002 m).
- Side contact: stops at X **0.680065036 m** (expectation .680 ± .002 m).
- Clear bypass at X .75 m: ends at Z **-2.999999762 m** (expectation -3 ± .002 m).
- Both modes produce equal results; body ray hits the actual bin static body, and
  an above-lid ray at Y 1.1 m stays clear.

These are bounded local simulation/query checks, not car handling, network
transport/prediction admission, placed-world movement or multiplayer acceptance.

## Evidence and reproduction

[Hero](city_waste_01-evidence/hero.png) · [side](city_waste_01-evidence/side.png) ·
[closed-flap detail](city_waste_01-evidence/detail.png) ·
[47 m / 42° overhead](city_waste_01-evidence/overhead_47m_42deg.png).
All four are isolated Blender CPU Cycles renders, 32 samples, AgX, 1280×720, compressed
PNG. Overhead is vertical-down perspective with **42° vertical FOV** at 47 m,
Blender +Y at image top. The task's latest 720-pixel height cap supersedes the older
1280×800 evidence size. Seven significant color bits trim background entropy.

All four final views were inspected. Initial close views cropped the bin, so framing
was widened; crown segmentation was increased before the final export. The complete
hero/side now show ground contact and the crown. From gameplay distance the lid is a
small, quiet silhouette; fine flap/latch details intentionally disappear. This is not
an in-engine actor-contrast or street-composition proof. No oversized marking was
added to force a tiny street prop to compete with characters.

Final source/export: **1,676 triangles; 856 Blender vertices; 1,002 GLB vertices;
one mesh; four surfaces; zero degenerate faces and zero non-manifold edges**.
Finite coordinates, unit source/GLB normals, winding, literal dimensions and ground
datum pass. Actual GLB binary positions/indices/normals are checked, not just metadata.
Fresh-process re-export is **byte-identical**, 46,212 bytes, SHA-256
`45af020b665fa992f3722867cc9ea825ee92b32cc3cb6db47ee8f42ab3984017`.

From repository root in Bash (scratch logs/output remain outside the checkout):

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
TMP='C:/tmp/ft/assets/city_waste_01'
mkdir -p "$TMP"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_waste_01/author.py
timeout 600 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_waste_01/render.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 art/source/models/environment/city_waste_01/city_waste_01.blend --python tools/asset_production/city_waste_01/export.py -- "$TMP/reexport"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/city_waste_01/validate.py -- "$TMP/reexport/city_waste_01.glb"
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script tools/asset_production/city_waste_01/check.gd -- --normalize
timeout 180 "$GODOT" --headless --path . --script tools/asset_production/city_waste_01/check.gd
# Use a fresh empty checks directory on each run.
timeout 1800 mise exec -- python tools/production_checks.py --output "$TMP/checks"
python tools/asset_production/city_waste_01/manifest.py "$TMP/checks"
```

`manifest.py` needs Pillow, also used by other production asset evidence tools.
[validation.json](city_waste_01-evidence/validation.json) records numbers, material
values, engine observations and all production-check layer outcomes.
[manifest.json](city_waste_01-evidence/manifest.json) hashes every delivery payload
except itself; [final.log](city_waste_01-evidence/final.log) retains the concise receipt.
The full production suite passed: owned-script formatting/lint/compilation, **14
Python tests**, **86 GUT tests / 2,178 assertions**, and expected-failure detection.
No pre-existing failure exemptions were needed.

Diagnostics remain explicit: Blender warns that `use_nodes` will be deprecated in
6.0. Headless editor import warns that the existing MCP plugin's latest tested
engine is 4.7. Normalization assertions and exit status pass, but editor shutdown
reports renderer/text RID and ObjectDB leaks. The subsequent runtime load/physics
check exits 0 without ERROR/WARNING/SCRIPT ERROR diagnostics; the isolated complete
production suite also passes. Initial local style findings were fixed before it ran.

## Remaining acceptance

Independent technical/art review is pending. World integration must confirm district
use, final dimensions and placement; preserve walking/vehicle routes and test actual
actor contrast/occlusion in the engine camera. Car contact, real-process multiplayer
transport/admission/prediction, packaged builds, Deck readability and sustained
repeat-placement performance remain untested. No world scene, gameplay system,
shared tracker, TODO or READY status was changed.
