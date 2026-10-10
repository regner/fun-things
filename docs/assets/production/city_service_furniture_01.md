# city_service_furniture.01 — Utility cabinet

10 October 2026. **Source/export and linked prefab delivered; independent review and
world/gameplay/device acceptance pending.** Production is commissioned by the
[register commission](commission.md) and current asset-common handoff, superseding
the historical concept-only restrictions in the [family brief](../city_service_furniture.md).
Producer: commissioned implementation specialist, branch `lane/a-service`.
The production lead owns independent review, register reconciliation and integration.
No shared brief, queue, progress, world scene or gameplay script was changed.

## Design and dimensions

Original Blender construction: a compact closed steel cabinet on a raised plinth,
soft-edged weather cap, broad inset door and side panels, two quiet hinges, flush
latch, three broad vent impressions and one small amber warning plate. The original
geometric exclamation mark uses no font, artwork download or brand. There is no
interior, working door, electrical/drainage system, destruction or interaction.

The [district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) inform quiet
rear-route dressing, especially Ironreach's practical service corners. District use
and placement remain unconfirmed. This is the first delivered member of the service
family; subsequent door/drain work can reuse the quiet blue-slate enamel, petrol
frame, dark recesses and restrained amber language without changing this asset.

All dimensions below are **provisional authored values**, not measurements inferred
from concept images. Envelope/ground acceptance tolerance is ±0.001 m.

| Contract | Metres |
| --- | --- |
| Godot width X / height Y / depth Z | **1.20 / 1.50 / 0.55** |
| Godot AABB minimum | (-0.600, 0, -0.275) |
| Godot AABB maximum | (0.600, 1.500, 0.275) |
| Plinth width / height / depth | 1.12 / 0.12 / 0.50 |
| Main steel housing width / height / depth | 1.14 / 1.31 / 0.49 |
| Weather cap thickness | 0.075 |
| Inset front door width / height | 1.03 / 1.16 |
| Ground-centred root and mesh pivot | (0, 0, 0) |

Metre units, applied transforms and identity roots; Blender +Y front maps to Godot
-Z and Blender +Z up maps to Godot +Y. The cap owns the symmetrical plan bounds.
This freestanding obstruction must be placed in a furniture zone or wall recess,
not in the 1.5 m foot strips or at passage mouths. The cabinet leaves no usable
interior or undercut route. Final actor/car clearance is a world-placement gate.

## Source, exports and materials

- Source: `art/source/models/environment/city_service_furniture_01/city_service_furniture_01.blend`.
- Export collection: `export_city_service_furniture_01`.
- Root/mesh: `CityServiceFurniture01` / `CityServiceFurniture01_Mesh`.
- Explicit GLB: `art/models/environment/city_service_furniture_01/city_service_furniture_01.glb`.
- Linked wrapper: `scenes/prefabs/environment/city_service_furniture_01.tscn`.
- Parametric author/export/validation/render scripts and the bounded physics fixture:
  `tools/asset_production/city_service_furniture_01/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export uses
`tools/assets/blender/export_settings.json` with the named collection, animations
and skins disabled. No runtime mesh construction, textures, embedded images,
external dependencies, sockets, rig or clips. Manufactured parts are closed
manifold shells joined into one mesh; intentional intersections conceal their
backing faces, not missing/open geometry. Bevels and weighted normals are baked.
Studio floor/lights/camera are added only by render.py and never saved/exported.

Four opaque back-culled Principled surfaces, in exported slot order:

| Slot / material | Linear RGB | Metallic / roughness |
| --- | --- | --- |
| 0 `service_frame` | (.035, .070, .085) | .45 / .50 |
| 1 `service_recess` | (.012, .023, .027) | .20 / .58 |
| 2 `service_enamel` | (.095, .160, .175) | .35 / .48 |
| 3 `service_warning_amber` | (.750, .390, .095) | .05 / .52 |

No emission or material override. The cap provides the quiet overhead silhouette;
the warning plate and hardware are close-view dressing, not gameplay information.
Default Godot import LOD/shadow-mesh generation is retained; no hand-authored LOD
or platform budget is claimed. Repeat-instance cost needs later profiling.

## Prefab and collision

The saved wrapper retains the imported GLB at `Visuals/Model` with identity
transform. `Collision/Body` is one `StaticBody3D`, static-world layer 1 / mask 0.
Its direct child `Shape` is one **1.20 × 1.50 × 0.55 m** box at (0, .75, 0).
The deliberate conservative envelope includes the cap/trim and fills tiny panel
insets, avoiding detailed snag geometry. Visual geometry does not own collision.
No runtime scripts or new gameplay state are attached to the prefab.

Headless Godot load/pack/save/reload normalized resource UIDs and node identities;
a second save was byte-identical for wrapper and physics fixture. Recursive
resource/UID resolution, imported bounds, mesh/surface count and opaque back-culling
passed. No open/live editor was used or synchronized; isolated headless calls are
the required fallback because the brief prohibits the owner's live sessions and
reports that windowed editing crashes.

The saved collision-only fixture uses production `ActorMotion.step` and
`FootCommand` with the actual 0.35 m radius / 1.8 m capsule. Three ray cases establish
solid front planes at heights .2/.9 m and clear passage above the 1.5 m cap at 1.7 m.
Six 60-tick movement cases cover front, rear and side bypass in AUTHORITY and REPLAY.
Front/rear stops are Z = **-0.626301765 / +0.626301765 m**; bypass at X = 1.1 m reaches
Z = **2.999999762 m**. Both modes produce equal positions. This is a local rule check,
not network transport/admission/prediction or actual car-driving acceptance.

The first movement comparison exposed cached floor-contact state in a reused test
body (0.000129 m vertical difference only). The fixture now duplicates the authored
actor into a fresh physics body per case; strict equality passes without relaxing
the expectation. No production actor change was made.

## Evidence and reproduction

[Hero](city_service_furniture_01-evidence/hero.png) ·
[Side](city_service_furniture_01-evidence/side.png) ·
[Detail](city_service_furniture_01-evidence/detail.png) ·
[Gameplay-camera overhead](city_service_furniture_01-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU renders, 1280×720, AgX, 32 samples.
The overhead is unscaled vertical-down perspective at **47 m / 42° vertical FOV**,
Blender +Y at image top. The current handoff's 720-pixel maximum supersedes the
older 800-pixel evidence size. All four were visually inspected: the hero/side show
closed construction and restrained details; overhead intentionally reads as a small
quiet capped rectangle. These are not Godot captures or populated-street evidence.
PNG compression 95 is followed by seven-significant-bit RGB compression for lean
review storage; no camera crop, upscaling or silhouette alteration is performed.

Commands from repository root (all scratch outside the checkout):

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
A=city_service_furniture_01
T=C:/tmp/ft/assets/$A
mkdir -p "$T/user/appdata" "$T/user/localappdata"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
export APPDATA="$T/user/appdata" LOCALAPPDATA="$T/user/localappdata"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$A/author.py
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$A/render.py
timeout 180 "$B" -noaudio --background --factory-startup art/source/models/environment/$A/$A.blend --threads 4 --python-exit-code 1 --python tools/asset_production/$A/export.py -- "$T/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$A/validate.py -- "$T/reexport/$A.glb"
timeout 300 "$(mise which godot)" --headless --editor --path . --import --quit
timeout 180 "$(mise which godot)" --headless --editor --path . --script res://tools/asset_production/$A/check.gd -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script res://tools/asset_production/$A/check.gd
timeout 40 "$(mise which gdstyle)" fmt --check tools/asset_production/$A/check.gd
timeout 40 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 tools/asset_production/$A/check.gd
# Output directory must be fresh; this is the retained final run's path.
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks-final"
python tools/asset_production/$A/manifest.py "$T/checks-final"
```

Final [validation.json](city_service_furniture_01-evidence/validation.json):
**3,352 triangles, 1,712 Blender vertices, 2,067 exported vertices, one mesh,
four surfaces; zero degenerate faces and zero non-manifold edges**. Unit source
corner/export normals, consistent winding, applied transforms and literal source/
GLB/Godot bounds pass. Fresh separate-process re-export is byte-identical to the
90,344-byte committed GLB. [manifest.json](city_service_furniture_01-evidence/manifest.json)
hashes every delivered payload except itself. A concise [final log](city_service_furniture_01-evidence/final.log)
records command outcomes; raw/intermediate logs remain under the scratch path above.

Canonical production checks **all pass with no exemptions**: owned-script formatting,
lint and explicit compilation, Python tests, GUT import/tests and the intentional
negative diagnostic test. The owned GDScript passes pinned gdstyle 0.3.0.
Blender author/render emitted pinned use_nodes deprecation notices. Headless import
emitted the existing MCP 4.8 compatibility warning; editor normalization passed all
assertions but reported shutdown RID/ObjectDB leaks. The standalone asset test is
clean of error/warning diagnostics. Those editor diagnostics are not called clean
engine exits. Plain `gdstyle` was unavailable on PATH; using `mise which gdstyle`
resolved the pinned executable without environment/project changes.

## Remaining acceptance

Independent art/technical review remains required. Final district assignment, saved
world placement, rear-route/corner clearance, actual car contacts, populated camera
readability, combat occlusion, separate-process multiplayer collision/prediction,
packaged builds and sustained Deck/renderer/repetition performance remain pending.
No new system or whole-register READY status is claimed. The next family members
must remain separate static door/drain designs; this cabinet adds no interaction
or contract requirement to them.
