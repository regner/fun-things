# city_service_furniture.02 — Drain cover

10 October 2026. **Source/export and linked prefab delivered; independent review and
world/gameplay/device acceptance pending.** Production is commissioned by the
[register commission](commission.md) and current asset-common handoff, superseding
the historical concept-only restrictions in the [family brief](../city_service_furniture.md).
Producer: commissioned implementation specialist, branch `lane/a-service`.
The production lead owns independent review, register reconciliation and integration.
No shared brief, queue, progress, sibling asset, world scene or gameplay script changed.

## Design and dimensions

Original Blender construction: a rounded rectangular cast rim, six broad grate ribs,
a transverse tie and two banks of dark sealed slot impressions. Quiet petrol metal
and blue-slate ribs match the exact opaque material values of the delivered
[utility cabinet](city_service_furniture_01.md) and [service door](city_service_furniture_03.md).
Both sibling documents, construction conventions and hero evidence were inspected;
neither sibling was modified. No warning accent is needed on this ground detail.
No downloaded geometry, generated/image-to-mesh asset, brand, font or external artwork.

The [district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) inform quiet
rear-route dressing, especially Ironreach and East Docks service/yard surfaces.
District uses remain unconfirmed. This is a **sealed visual overlay**, not an open
drain, separate road-surface kit, removable cover, interior or drainage system.
It adds no obstacle maze, interaction, destruction or authoritative state.

All dimensions below are **provisional authored values**, not measurements inferred
from concept images. Envelope/ground acceptance tolerance is ±0.001 m.

| Contract | Metres |
| --- | --- |
| Godot width X / height Y / depth Z | **0.80 / 0.008 / 0.60** |
| Godot visual AABB minimum | (-0.400, 0, -0.300) |
| Godot visual AABB maximum | (0.400, 0.008, 0.300) |
| Outer rim corner radius / nominal border width | 0.035 / 0.065 |
| Inner rim width / depth / corner radius | 0.67 / 0.47 / 0.024 |
| Six ribs, width / length / pitch | 0.052 / 0.462 / 0.110 |
| Transverse tie width / depth / top height | 0.662 / 0.048 / 0.0075 |
| Dark backing top height | 0.003 |
| Root and mesh pivot, ground-contact footprint centre | (0, 0, 0) |

Metre units, applied transforms and identity roots; Blender +Y maps to Godot -Z,
Blender +Z to Godot +Y. This ground fixture is bilaterally symmetric, not a directional
sign. Its long dimension is X. Place the root **on an existing continuous flat ground
surface**, at unit scale, with the rim and slot backing above that surface. The 8 mm
relief is deliberate render separation, not a gameplay step. Do not sink it until the
road hides its backing, cut a road opening, or use this shallow mesh over a real void.
The top backing stays 3 mm above the receiving plane to avoid coplanar ground faces.

## Source, exports and materials

- Source: `art/source/models/environment/city_service_furniture_02/city_service_furniture_02.blend`.
- Export collection: `export_city_service_furniture_02`.
- Root/mesh: `CityServiceFurniture02` / `CityServiceFurniture02_Mesh`.
- Explicit GLB: `art/models/environment/city_service_furniture_02/city_service_furniture_02.glb`.
- Linked wrapper: `scenes/prefabs/environment/city_service_furniture_02.tscn`.
- Parametric author/export/validation/render scripts and headless resource check:
  `tools/asset_production/city_service_furniture_02/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export uses
`tools/assets/blender/export_settings.json` with the named collection, animations
and skins disabled. No runtime mesh construction, textures, embedded images,
external dependencies, sockets, rig or clips. Closed manifold manufactured shells
are joined into one mesh; intentional intersections hide their backing faces.
The transverse tie is 0.5 mm below rib tops to avoid coplanar overlapping top faces.
Ribs stop inside the rim rather than overlapping its differently coloured top.
Bevels and weighted normals are baked. Studio floor/lights/camera are added only by
render.py and never saved/exported. Scripts follow the sibling audit/camera patterns
and shared export settings; no new shared framework or asset dependency was added.

Three opaque back-culled Principled surfaces, in exported slot order:

| Slot / material | Linear RGB | Metallic / roughness |
| --- | --- | --- |
| 0 `service_frame` | (.035, .070, .085) | .45 / .50 |
| 1 `service_recess` | (.012, .023, .027) | .20 / .58 |
| 2 `service_enamel` | (.095, .160, .175) | .35 / .48 |

No emission or material override. Broad slots are decorative rhythm, not gameplay
information. Default Godot import LOD/shadow-mesh generation is retained; no custom
LOD or platform budget is claimed. Repetition and distant shimmer need engine review.

## Prefab and collision

The saved wrapper retains the imported GLB at `Visuals/Model` with identity
transform. **No physics body or collision shape** is authored: this is flush surface
dressing, covered by the standing flush-face exception. Existing road/yard collision
remains the sole continuous walk/drive surface. Duplicating it with a tiny box would
introduce a needless seam. This asset must not cover a real collision hole or promise
a walkable deck. No runtime script or new gameplay state is attached to the prefab.

Headless Godot load/pack/save/reload normalized resource UIDs and node identities;
a second save was byte-identical. Recursive resource/UID resolution, imported bounds,
one mesh/three surfaces, opaque back-culling and zero collision objects/shapes passed.
A fresh standalone process loaded and checked the same saved wrapper without missing
dependencies or corrective transforms. There is no inherited variant to roundtrip.
No live editor was used or synchronized: isolated headless calls are the prescribed
fallback because the brief prohibits live sessions and reports windowed-editor crashes.
No collision was changed, so this delivery does not add a movement/network fixture
or claim actual actor/car contact validation.

## Evidence and reproduction

[Hero](city_service_furniture_02-evidence/hero.png) ·
[Side](city_service_furniture_02-evidence/side.png) ·
[Detail](city_service_furniture_02-evidence/detail.png) ·
[Gameplay-camera overhead](city_service_furniture_02-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU renders, 1280×720, AgX, 32 samples.
The overhead is unscaled vertical-down perspective at **47 m / 42° vertical FOV**,
Blender +Y at image top. The current handoff's 720-pixel maximum supersedes the
older 800-pixel evidence size. All four were visually inspected: the rounded rim and
two-bank grate read clearly close up; overhead reads as a small, quiet gridded patch
rather than a landmark. The first side render exposed a studio floor clipping band;
raising that camera removed it without changing source or GLB. Final side evidence
is an oblique side view showing the shallow relief. These are not Godot captures
or populated-street evidence. PNG compression 95 is followed by RGB compression to
six significant bits for hero/detail and seven for side/overhead, without scaling or
cropping the gameplay image. The initial seven-bit hero exceeded the evidence-size
check; six-bit close views meet the limit and were re-inspected for retained detail.
This affects evidence encoding only, never source materials or the exported asset.

Commands from repository root (all scratch outside the checkout):

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
A=city_service_furniture_02
T=C:/tmp/ft/assets/$A
mkdir -p "$T/user/appdata" "$T/user/localappdata"
(
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
# Private user paths are scoped to these Blender invocations.
export APPDATA="$T/user/appdata" LOCALAPPDATA="$T/user/localappdata"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$A/author.py
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$A/render.py
timeout 180 "$B" -noaudio --background --factory-startup art/source/models/environment/$A/$A.blend --threads 4 --python-exit-code 1 --python tools/asset_production/$A/export.py -- "$T/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$A/validate.py -- "$T/reexport/$A.glb"
)
# Godot/mise use the restored normal user environment.
timeout 300 "$(mise which godot)" --headless --editor --path . --import --quit
timeout 180 "$(mise which godot)" --headless --editor --path . --script res://tools/asset_production/$A/check.gd -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script res://tools/asset_production/$A/check.gd
timeout 40 "$(mise which gdstyle)" fmt --check tools/asset_production/$A/check.gd
timeout 40 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 tools/asset_production/$A/check.gd
# Output directory must be fresh; this is the retained run's path.
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks-final"
python tools/asset_production/$A/manifest.py "$T/checks-final"
```

Final [validation.json](city_service_furniture_02-evidence/validation.json):
**1,536 triangles, 784 Blender vertices, 912 exported vertices, one mesh,
three surfaces; zero degenerate faces and zero non-manifold edges**. Unit source
corner/export normals, consistent winding, applied transforms and literal source/
GLB/Godot bounds pass. Fresh separate-process re-export is byte-identical to the
41,560-byte committed GLB. [manifest.json](city_service_furniture_02-evidence/manifest.json)
hashes every delivered payload except itself. A concise [final log](city_service_furniture_02-evidence/final.log)
records command outcomes; raw/intermediate logs remain under the scratch path above.

Canonical production checks **all pass with no exemptions**: owned-script formatting,
lint and explicit compilation, **14 Python tests**, **119 GUT tests / 6,362 assertions**,
GUT import and the intentional negative diagnostic test. The owned GDScript passes
pinned gdstyle 0.3.0. Blender author/render emitted pinned use_nodes deprecation
notices. Headless import emitted the existing MCP 4.8 compatibility warning; editor
normalization passed all assertions but reported shutdown RID/ObjectDB leaks.
The standalone asset check is clean of error/warning diagnostics. Those editor
diagnostics are not called clean engine exits. No unchanged failing step was repeated.

## Remaining acceptance

Independent art/technical review remains required. Final district assignment, saved
world placement and road-surface fit, populated gameplay-camera readability, distant
LOD/shimmer, actual actor/car traversal, separate-process multiplayer, packaged builds
and sustained Deck/renderer/repetition performance remain pending. The 8 mm visual
relief and backing separation must be checked against the actual generated ground
material and camera; no road tooling change or new drainage mechanic is authorized.
No whole-register READY status, TODO completion or placement acceptance is claimed.
