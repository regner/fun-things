# city_service_furniture.03 — Closed service door and surround

10 October 2026. **Source/export and linked prefab delivered; independent review and
world/gameplay/device acceptance pending.** Production is commissioned by the
[register commission](commission.md) and current asset-common handoff, superseding
the historical concept-only restrictions in the [family brief](../city_service_furniture.md).
Producer: commissioned implementation specialist, branch `lane/a-service`.
The production lead owns independent review, register reconciliation and integration.
No shared brief, queue, progress, sibling asset, world scene or gameplay script changed.

## Design and dimensions

Original Blender construction: one static closed steel service-entry assembly with
soft-edged jambs/head, a broad pressed inset panel, low kick plate, three quiet hinges,
a short return lever and one small blank amber identification plate. It is an ordinary
rear door, not a glazed shop entrance or industrial roller shutter. No interior,
opening animation, interaction, electrical system or destruction is introduced.

The [district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) inform quiet
rear-route dressing, especially Ironreach's practical service corners. District use
and placement remain unconfirmed. The geometry and exact material values follow
[the delivered utility cabinet](city_service_furniture_01.md): blue-slate enamel,
petrol frame, dark broad seams and restrained amber. Its source and evidence were
inspected but not modified. No downloaded geometry, brand, font or external artwork.

All dimensions below are **provisional authored values**, not measurements inferred
from concept images. Envelope/ground acceptance tolerance is ±0.001 m.

| Contract | Metres |
| --- | --- |
| Godot width X / height Y / depth Z, including lever | **1.36 / 2.44 / 0.30** |
| Godot visual AABB minimum | (-0.680, 0, -0.180) |
| Godot visual AABB maximum | (0.680, 2.440, 0.120) |
| Surround structural width / height / depth | 1.36 / 2.44 / 0.24 |
| Jamb width / head height | 0.12 / 0.12 |
| Frame inner opening width / head underside height | 1.12 / 2.32 |
| Closed leaf width / height / thickness | 1.10 / 2.26 / 0.072 |
| Leaf bottom / top | 0.04 / 2.30 |
| Broad inset face width / height | 0.92 / 1.52 |
| Sill height | 0.04 |
| Lever centre height / maximum forward extent | 1.12 / 0.18 |
| Root and mesh pivot, ground-centred surround | (0, 0, 0) |

Metre units, applied transforms and identity roots; Blender +Y front maps to Godot
-Z and Blender +Z up maps to Godot +Y. The pivot centres the **structural surround**,
not the asymmetrical lever overhang. No mounting socket or new attachment API is needed.

Provisional mounting interface: align the root with the facade ground and the wall
finish plane at local Z=0. The surround extends 0.12 m both into and out of that plane;
the handle reaches 0.18 m toward the route. A **1.14 m wide × 2.33 m high** rough
opening from ground is the proposed receiving void, leaving jamb/head cover overlap.
This is a proposal for a future compatible building opening, **not a tested fit to an
existing shell**. Do not paste the assembly across a glazed/integral entrance or
commission a duplicate door for the same opening. Keep rear routes and passage mouths
clear; this is closed dressing and never a promised escape route or usable interior.

## Source, exports and materials

- Source: `art/source/models/environment/city_service_furniture_03/city_service_furniture_03.blend`.
- Export collection: `export_city_service_furniture_03`.
- Root/mesh: `CityServiceFurniture03` / `CityServiceFurniture03_Mesh`.
- Explicit GLB: `art/models/environment/city_service_furniture_03/city_service_furniture_03.glb`.
- Linked wrapper: `scenes/prefabs/environment/city_service_furniture_03.tscn`.
- Parametric author/export/validation/render scripts and bounded physics fixture:
  `tools/asset_production/city_service_furniture_03/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export uses
`tools/assets/blender/export_settings.json` with the named collection, animations
and skins disabled. No runtime mesh construction, textures, embedded images,
external dependencies, sockets, rig or clips. Manufactured parts are closed
manifold shells joined into one mesh; intentional intersections hide their backing
faces rather than leaving open geometry. Bevels and weighted normals are baked.
Studio floor/lights/camera are added only by render.py and never saved/exported.
The scripts follow the sibling's existing audit/camera/physics conventions and use
the shared export settings and canonical production checks, without a new framework.

Four opaque back-culled Principled surfaces, in exported slot order:

| Slot / material | Linear RGB | Metallic / roughness |
| --- | --- | --- |
| 0 `service_frame` | (.035, .070, .085) | .45 / .50 |
| 1 `service_recess` | (.012, .023, .027) | .20 / .58 |
| 2 `service_enamel` | (.095, .160, .175) | .35 / .48 |
| 3 `service_warning_amber` | (.750, .390, .095) | .05 / .52 |

No emission or material override. The amber plate is blank decorative identification,
not essential wayfinding or an unfulfilled artwork dependency. Default Godot import
LOD/shadow-mesh generation is retained; no hand-authored LOD or platform budget is
claimed. Repeated-instance cost needs later profiling.

## Prefab and collision

The saved wrapper retains the imported GLB at `Visuals/Model` with identity
transform. `Collision/Body` is one `StaticBody3D`, static-world layer 1 / mask 0.
Its direct child `Shape` is one **1.36 × 2.44 × 0.24 m** box at (0, 1.22, 0).
It fills the closed entry through the surround depth; decorative lever overhang
does not inflate the blocking envelope. This conservative single solid avoids
panel/handle snag geometry. Visual geometry does not own collision. No runtime
scripts or new gameplay state are attached to the prefab.

Headless Godot load/pack/save/reload normalized resource UIDs and node identities;
a second save was byte-identical for wrapper and physics fixture. Recursive
resource/UID resolution, imported bounds, mesh/surface count and opaque back-culling
passed. No open/live editor was used or synchronized; isolated headless calls are
the required fallback because the brief prohibits the owner's live sessions and
reports that windowed editing crashes.

The saved collision-only fixture uses production `ActorMotion.step` and
`FootCommand` with the actual 0.35 m radius / 1.8 m capsule. Three ray cases establish
solid front planes at heights 0.2/1.2 m and clear passage above the 2.44 m head at
2.6 m. Six 60-tick movement cases cover front, rear and isolated side bypass in
AUTHORITY and REPLAY. Front/rear stops are Z = **-0.470051765 / +0.470051765 m**;
bypass at X = 1.1 m reaches Z = **2.999999762 m**. Both modes produce equal positions.
A fresh physics body per case follows the cabinet's proven contact-cache isolation.
This is a local rule check, not network transport/admission/prediction, actual car
contacts or proof that a mounted door has a walkable side bypass.

## Evidence and reproduction

[Hero](city_service_furniture_03-evidence/hero.png) ·
[Side](city_service_furniture_03-evidence/side.png) ·
[Detail](city_service_furniture_03-evidence/detail.png) ·
[Gameplay-camera overhead](city_service_furniture_03-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU renders, 1280×720, AgX, 32 samples.
The overhead is unscaled vertical-down perspective at **47 m / 42° vertical FOV**,
Blender +Y at image top. The current handoff's 720-pixel maximum supersedes the
older 800-pixel evidence size. All four were visually inspected against the cabinet:
hero/detail show the broad closed-panel language and small practical hardware;
side shows the shallow structural depth; overhead reads as a quiet narrow lintel,
not a readable door face. No essential information relies on overhead plate/lever
visibility. These are not Godot captures or populated-street evidence.
PNG compression 95 is followed by seven-significant-bit RGB compression for lean
review storage; no camera crop, upscaling or silhouette alteration is performed.

Commands from repository root (all scratch outside the checkout):

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
A=city_service_furniture_03
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
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks"
python tools/asset_production/$A/manifest.py "$T/checks"
```

Final [validation.json](city_service_furniture_03-evidence/validation.json):
**3,068 triangles, 1,568 Blender vertices, 1,900 exported vertices, one mesh,
four surfaces; zero degenerate faces and zero non-manifold edges**. Unit source
corner/export normals, consistent winding, applied transforms and literal source/
GLB/Godot bounds pass. Fresh separate-process re-export is byte-identical to the
83,356-byte committed GLB. [manifest.json](city_service_furniture_03-evidence/manifest.json)
hashes every delivered payload except itself. A concise [final log](city_service_furniture_03-evidence/final.log)
records command outcomes; raw logs remain under the scratch path above.

Canonical production checks **all pass with no exemptions**: owned-script formatting,
lint and explicit compilation, Python tests, GUT import/tests and the intentional
negative diagnostic test. The owned GDScript passes pinned gdstyle 0.3.0.
Blender author/render emitted pinned use_nodes deprecation notices. Headless import
emitted the existing MCP 4.8 compatibility warning; editor normalization passed all
assertions but reported shutdown RID/ObjectDB leaks. The standalone asset check is
clean of error/warning diagnostics. Those editor diagnostics are not called clean
engine exits. No unchanged failed command was repeated.

## Remaining acceptance

Independent art/technical review remains required. Final district assignment,
compatible facade/opening fit, saved world placement, rear-route/corner clearance,
actual car contacts, populated camera readability, combat occlusion, separate-process
multiplayer collision/prediction, packaged builds and sustained Deck/renderer/repetition
performance remain pending. No new system or whole-register READY status is claimed.
The drain-cover sibling remains separately owned; this entry adds no interaction or
new shared material/geometry dependency to it.
