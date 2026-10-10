# d07_trolley_shelter.01 — Short shelter

**Source/export and bounded headless prefab checks delivered; independent review and
world/gameplay acceptance pending.** Production commissioned under the register task
and [commission](commission.md), superseding the historical concept-only restriction
in the [family brief](../d07_trolley_shelter.md). Producer: commissioned implementation
specialist. No preceding trolley-family outputs existed in this lane at authoring time.

## Design and dimensions

An original open-front retail trolley corral: four dark petrol uprights, continuous low
skids, two broad guard rails, a rear trolley stop and a shallow pale barrel canopy.
Two small coral collars mark the entry without competing with parking-row wayfinding.
No glazing, seats, fine basket-like wire, signs, brands or simulated shopping behavior.
The roof and empty corral are this record's design; the single trolley and nested group
belong to `.02` and `.03`, respectively, and are not duplicated here.

Provenance is original Blender construction, authored by the committed parametric script.
No downloads, purchased meshes, image-to-mesh, external fonts, textures or generated
runtime meshes. Reference direction: Petrol & Coral, the approved Broadlot district
identity and the Stage 4 street hierarchy. Sparse parking-row placement is downstream;
no district, road, parking-bay or pedestrian-route scene was changed.

All dimensions below are **provisional authored choices**, not measurements taken from
concept art. Envelope tolerance is ±0.001 m; source-to-GLB comparison is 0.00001 m.

| Contract | Metres, Godot local axes |
| --- | --- |
| Width X × height Y × depth Z | 2.900 × 3.110 × 3.600 |
| Visual AABB minimum / maximum | (-1.450, 0, -1.800) / (1.450, 3.110, 1.800) |
| Root and mesh origin | (0, 0, 0), centred ground-contact footprint |
| Entry | Local -Z; Blender +Y maps to Godot -Z |
| Roof | 0.090 thick; underside 2.700 at outer eaves, 3.020 at crown |
| Uprights | 0.140 square, centres X ±1.240 / Z ±1.470; top 2.730 |
| Side skids | 0.220 wide × 0.150 high × 3.160 long |
| Guard rails | 0.120 section; centres Y 0.570 and 1.100 |
| Clear entry / inner skids | 2.260 wide; no front crossbar or sill |
| Rear stop | Z +1.470, extends forward to +1.400; top Y 1.160 |

**Sibling fit handoff:** use the same metre scale, ground datum and petrol/coral palette.
A conservative trolley arrangement region is X [-1.0, +1.0], Z [-1.30, +1.20], below
Y 1.50; that is a proposed fitting region, not geometry or placement owned by this asset.
Keep the shelter entrance at -Z. Trolleys may face toward the rear for nesting; their
own model-front convention remains -Z. `.03` must reuse `.02`, not create another trolley
mesh. Neither group size nor shopping interactions are defined by this shelter.

## Source, exports and materials

- Source: `art/source/models/environment/d07_trolley_shelter_01/d07_trolley_shelter_01.blend`.
- Collection: `export_d07_trolley_shelter_01`.
- Root / mesh: `D07TrolleyShelter01` / `D07TrolleyShelter01_Mesh`.
- Export: `art/models/environment/d07_trolley_shelter_01/d07_trolley_shelter_01.glb`
  and its pinned Godot `.import` sidecar.
- Prefab: `scenes/prefabs/environment/d07_trolley_shelter_01.tscn`.
- Tools: `tools/asset_production/d07_trolley_shelter_01/` contains the author,
  export, source/binary validator, headless prefab check and evidence recorder.

Blender 5.2.2 LTS (`d13f752e3b9c`), glTF exporter 5.2.40, metre units with applied
rotation/scale and ground-centred origins. The editable source keeps closed manufactured
mesh islands in one export mesh. Shared `tools/assets/blender/export_settings.json`
is loaded directly; collection filtering, Y-up conversion, normals/UVs, no cameras,
lights, animation or skins. Studio ground/lights/camera are outside the export collection.

Three opaque, backface-culled Principled surfaces, ordered as follows. Values are linear
RGB; complete actual exported PBR values are in validation.json.

| Slot | RGB | Metallic | Roughness |
| --- | --- | --- | --- |
| `shelter_frame_petrol` | (0.025, 0.075, 0.090) | 0.45 | 0.46 |
| `shelter_entry_coral` | (1.000, 0.168, 0.110) | 0.10 | 0.48 |
| `shelter_roof_ivory` | (0.760, 0.820, 0.780) | 0.12 | 0.52 |

No runtime textures, external materials, embedded images, sockets, rigs, animations,
interactions, destruction states or manual LODs are needed. Godot default generated
LODs and shadow mesh remain enabled; repeated-placement performance is not measured.

## Prefab and collision

`Visuals/Model` is the identity-transform imported instance; no copied mesh data or
editable imported-child overrides. `Collision/ShelterBody` is one static-world body,
layer 1 / mask 0, with three direct-child boxes:

- `LeftSide` / `RightSide`: size (0.220, 2.730, 3.180), centres
  (±1.240, 1.365, 0). These conservative side envelopes intentionally fill rail gaps
  and cover the uprights, rather than using separate snag-prone bar/post colliders.
- `RearStop`: size (2.480, 1.160, 0.140), centre (0, 0.580, 1.470).

The front and floor remain open. Existing terrain owns the walkable ground; no duplicate
floor collider. The overhead canopy is visual-only. Side envelopes can block queries
through visibly open spaces above/between rails: deliberate simple obstacle collision,
not precision projectile/cover geometry. Placement must not treat this corral as a
through-route, aim-permeable fence or safe space beneath an opaque roof.

Only isolated headless Godot was used; the brief prohibits live editor/MCP session use
and reports the windowed editor unavailable. The prefab was authored as text then
loaded, packed and resaved twice headlessly, retaining UIDs and stable node identities.
This proves saved-resource roundtrip, not synchronization of any separate open editor.

## Evidence and reproduction

[Hero](d07_trolley_shelter_01-evidence/hero.png),
[side](d07_trolley_shelter_01-evidence/side.png),
[roof/frame detail](d07_trolley_shelter_01-evidence/detail.png),
[47 m / 42° overhead](d07_trolley_shelter_01-evidence/overhead_47m_42deg.png).
All four were visually inspected: clean bevels, broad quiet roof and open front; the
pale roof reads clearly overhead but hides the corral contents from directly above.
The coral collars are close-view detail, not required gameplay-distance identifiers.
Retail reading still needs the separately produced trolley and actual parking context.

These are isolated Blender Cycles/AgX renders, not engine captures. 1280×720 maximum
per the production-cleanliness override, 32 samples, neutral studio fill. Overhead:
vertical-down perspective at 47 m, vertical FOV 42°, Blender +Y at image top (north-up).
Evidence-only PNGs retain six significant bits per RGB channel without changing
resolution; no runtime texture is affected. A 256-colour trial visibly dulled the small
coral collars, so that trial was discarded and rerendered before final compaction. Studio cameras and light values live in author.py.

From repository root in Git Bash; every engine invocation is bounded:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/d07_trolley_shelter_01
S=C:/tmp/ft/assets/d07_trolley_shelter_01
mkdir -p "$S"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" -- --normalize
timeout 30 "$(mise which gdstyle)" check "$T/check.gd"
PYTHONUTF8=1 timeout 1800 python tools/production_checks.py --godot "$G" --gdstyle "$(mise which gdstyle)" --output "$S/checks-utf8"
python "$T/record.py" --checks "$S/checks-utf8"
timeout 300 "$G" --headless --path . --import
python "$T/record.py" --checks "$S/checks-utf8"
```

Use a fresh empty output directory for a new production suite run. `validate.py` opens
the saved source, freshly exports to scratch and compares the actual GLB bytes; it does
not reauthor the source. To export independently, open the saved `.blend` using the same
Blender CLI prefix and run `export.py -- C:/tmp/ft/assets/d07_trolley_shelter_01/reexport`.
The recorder uses Pillow solely for review PNG compaction and writes the final manifest.

## Validation results

[validation.json](d07_trolley_shelter_01-evidence/validation.json) contains measured
source and binary-accessor geometry, Godot observations and complete suite statuses.
[manifest.json](d07_trolley_shelter_01-evidence/manifest.json) hashes all final payloads
except itself. [final.log](d07_trolley_shelter_01-evidence/final.log) is the concise
command/diagnostic receipt; raw logs stay outside the repository in the scratch path.

- **3,592 triangles; 1,836 source vertices; 2,159 exported vertices; one mesh, three surfaces.**
- Zero degenerate source faces/triangles, zero degenerate binary GLB triangles,
  zero non-manifold source edges. Closed signed volume 1.810871 m³ (sum of islands,
  not union volume). Source and exported normals unit length within 0.000001.
- Actual imported dimensions 2.900000 × 3.110000 × 3.600000 m; ground datum zero.
- Fresh GLB export is byte-identical: 93,848 bytes, SHA-256
  `6f4951bc04b0aa457f6bb21b29216f40a9acff1c0712e3186577ed5d1413a459`.
- Pinned Godot 4.8.dev7.official.c971f93e7: dependency/UID resolution, identity linked
  model, imported materials/bounds, three-box separation and double save/reload pass.
- Rays block on both outer sides at X ±1.350 and rear at Z +1.400. Front and roof-only
  queries are clear. Capsule r=0.35 m / h=1.8 m fits the entry/interior and overlaps
  each of the three barriers as expected. These are bounded physics queries only.
- Final gdstyle lint and formatting pass. Full production suite passes: owned-script
  formatting/lint/compilation, **17 Python tests**, **149 GUT tests / 6,768 assertions**,
  and negative-test detection. No existing test failures needed exceptions.
- Initial unqualified production command failed on Windows cp1252 decoding during
  engine discovery. UTF-8 mode and explicit mise-resolved binary paths fixed the
  environment; the successful retry is separate evidence, not an ignored failure.
  Initial local lint reported 11 local variables; removing an unnecessary temporary
  fixed it. Import emits the existing MCP plugin's 4.8-versus-4.7 support warning;
  no asset errors were reported and no live sessions were touched.

## Remaining acceptance

Independent technical/art review remains pending. World integrator owns sparse
parking-row placement, full aisle/actor bypass clearances, alignment with `.02`/`.03`
and under-roof occlusion/retail recognition in the actual fixed gameplay camera.
ActorMotion movement, car turning/contact, weapon queries, authoritative/predicted
multiplayer behavior, repeated-placement LOD/shadows, packaged builds and sustained
Deck performance are **not tested** by this handoff. No district placement, content
budget, register-ready status or broader gameplay acceptance is claimed.
