# city_moored_yachts.01 — compact motor yacht

**Source, explicit export and blocking prefab delivered; independent review and world
placement pending.** Production is commissioned under the [common production commission](commission.md)
and the current per-asset lane assignment, which authorizes this asset's import, prefab and commit.
The historical concept-only restrictions in the [family brief](../city_moored_yachts.md)
do not prohibit this commissioned delivery.

Producer: commissioned implementation specialist `worker`, branch `lane/a-yachts`.
Accepting owners: production supervisor / independent asset reviewer; world integration remains
separate. No existing assets, register, progress record, shared brief or world placement changed.

## Design and dimensions

Original Blender construction: a compact V-bottom motor hull, rising pointed bow, low enclosed cabin
with broad petrol glazing, ivory roof, sparse bow rails, two foredeck sun pads and an open aft lounge.
A short stern platform, four fenders, four cleats and a low radar/aerial assembly give it a modest
moored-yacht reading without tall flybridge equipment. There are no logos, external meshes, downloaded
art, generated image-to-mesh content, interiors, rig, animation or nautical-prop subcatalogue.

References inspected: [Old Quay district identity](../../concepts/world-v1/stage-03-district-identities/README.md#old-quay--the-warm-edge-of-the-water),
[street/basin constraints](../../concepts/world-v1/stage-04-streets/README.md),
[Old Quay concept](../../concepts/districts-v1/old-quay.md),
[marina docks](../city_marina_docks.md), and the accepted `city_lights_01` end-to-end example.
Broad quiet ivory/sand forms, dark petrol glazing and one small coral cushion follow Petrol & Coral.
The basin and bridge remain placement constraints, not content authored by this asset.

The supervisor explicitly approved these **provisional production dimensions/interfaces** before
construction: 12.4 m nominal length, 3.8 m maximum beam including fenders, 1.0 m draft, 3.1 m above
water, waterline-centred pivot, bow toward Godot -Z, integrated fenders/cleats and no dock-dependent
mooring ropes. The supervisor additionally required simple above-water hull/cabin blocking because
boats will sit beside walkable pontoons and receive weapon/projectile queries. This bounded approval
supersedes the historical decorative-only/no-dock-gameplay assumption for this prefab's collision;
it does not commission boarding, piloting, buoyancy, damage or interior systems.

| Measurement | Delivered value |
| --- | --- |
| Godot X/Y/Z dimensions | **3.800000 × 4.100000 × 12.412151 m** |
| Godot AABB minimum | **(-1.900000, -1.000000, -6.212152) m** |
| Godot AABB maximum | **(1.900000, 3.100000, 6.200000) m** |
| Nominal length difference | 12.15 mm bow rub-strake endcap; within the documented 15 mm envelope tolerance |
| Root and mesh origin | (0, 0, 0), centred on the nominal waterline footprint; **not keel/ground contact** |
| Draft / above-water height | 1.000 / 3.100 m |
| Main hull beam excluding fittings | 3.500 m; sheer cap extends to 3.5525 m |
| Main sheer/deck height | approximately 0.84 m aft to 1.43 m at the bow cap |
| Cabin roof / highest aerial | 2.620 / 3.100 m above water |
| Coordinate contract | Blender +Y bow, +Z up → Godot -Z bow, +Y up; unit scale, no corrective wrapper transforms |

Dimensional tolerance is 0.015 m for nominal whole-asset bounds, 0.001 m for draft/top height and
engine-bound checks, and 0.00001 m for source/GLB coordinate equivalence. The waterline is a placement
datum, not a live water simulation. Put root Y at the future authored water surface; do not raise the
root by the draft. There are no attachment sockets, entry markers or mooring endpoints to promise a
particular dock connection. Berth spacing and fender-to-pontoon fit remain unselected.

### Family handoff to city_moored_yachts.02

Reuse the waterline-centred, bow -Z interface and quiet material vocabulary where useful; retain the
sailing boat's distinct mast/furled-sail silhouette. The supervisor requests the same static blocking
interface for .02, with its mast visual-only above about 2.5 m. This record does not authorize changes
to .02 or fix its dimensions. No earlier family asset existed when .01 began.

## Source, exports and materials

- Source: `art/source/models/environment/city_moored_yachts_01/city_moored_yachts_01.blend`.
- Named export collection: `export_city_moored_yachts_01`.
- Export root: `CityMooredYachts01`; mesh: `CityMooredYachts01_Mesh`.
- Explicit export: `art/models/environment/city_moored_yachts_01/city_moored_yachts_01.glb` and its
  retained `.glb.import` sidecar. Source is excluded from Godot by the existing `art/source/.gdignore`.
- Parametric construction, export, source validator and prefab check:
  `tools/asset_production/city_moored_yachts_01/`.
- Prefab: `scenes/prefabs/environment/city_moored_yachts_01.tscn`.

The source contains one consolidated static mesh with separately closed component islands; intended
manufactured joins overlap. Topology validation is per mesh edge, not a claim of one Boolean-welded
watertight solid. There are no unapplied modifiers, negative scales, animation dependencies or hidden
export cameras/lights. Studio camera/plane/area lights remain outside the export collection.

Seven opaque, backface-culled Principled material surfaces, in exported order:

| Slot | Material | Linear base RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `hull_ivory` | (0.88, 0.87, 0.77) | 0.08 / 0.31 |
| 1 | `waterline_navy` | (0.025, 0.045, 0.063) | 0.05 / 0.45 |
| 2 | `deck_sand` | (0.38, 0.28, 0.17) | 0 / 0.65 |
| 3 | `glazing_petrol` | (0.018, 0.066, 0.081) | 0.30 / 0.23 |
| 4 | `hardware_slate` | (0.39, 0.47, 0.49) | 0.65 / 0.30 |
| 5 | `upholstery_cream` | (0.70, 0.67, 0.54) | 0 / 0.72 |
| 6 | `accent_coral` | (0.90, 0.19, 0.12) | 0 / 0.60 |

Materials are carried by the GLB; no external textures, embedded images, remap resources, shaders,
light nodes or emission are needed. Glazing is deliberately opaque, not a transparent cabin interior.
No texture/UV-density claim is relevant. Import preserves default automatic LOD/shadow-mesh settings;
LOD transitions and repeated-placement GPU performance have not been visually profiled.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. `export.py` reads the existing
shared `tools/assets/blender/export_settings.json`, selects only the declared collection and disables
animation/skins for this static asset. No project settings or shared export rules were modified.

## Prefab and collision

`Visuals/Model` is an **identity-transform linked GLB instance**. No imported children are editable and
no mesh arrays are copied into the wrapper. Godot normalized the newly authored text scene, retained
its new scene UID/node identities, and passed a save/reopen/resave byte-stability check. The GLB UID and
scene UID resolve in the pinned engine. The scene UID is embedded in the `.tscn`; the check script has
its engine-generated `.gd.uid` sidecar.

`Collision/Body` is one `StaticBody3D`, static-world layer **1**, mask **0**, with three direct box-shape
children. Boxes are conservative blocking envelopes, not accurate hull contact surfaces:

| Shape | Godot centre (m) | Size X/Y/Z (m) |
| --- | --- | --- |
| Hull | (0, 0.625, 1.45) | (3.6, 1.25, 9.5) |
| Bow | (0, 0.725, -4.76) | (2.5, 1.45, 2.92) |
| Cabin | (0, 1.975, 0.2) | (2.7, 1.45, 4.75) |

The first two boxes begin at waterline Y=0; cabin blocking runs Y=1.25–2.70 m. The narrow bow box
intentionally overblocks the pointed nose and the main box overblocks the stern-platform corners.
There is no collider below the waterline. Fenders, cleats, rails, seat backs, radar and antenna are
visual-only; no tiny snag colliders or interior openings. Placing a pontoon inside these conservative
boxes is invalid even if a visible tapered hull corner appears clear. Whole-berth clearance is pending.
The wrapper has no health, destruction, ownership, vehicle controller, interaction or navigation code.

## Validation and evidence

[Hero](city_moored_yachts_01-evidence/hero.png) ·
[side](city_moored_yachts_01-evidence/side.png) ·
[aft/cabin detail](city_moored_yachts_01-evidence/detail.png) ·
[47 m / 42° overhead](city_moored_yachts_01-evidence/overhead_47m_42deg.png).
All four final isolated Blender renders were inspected by the producer. The broad pointed hull,
contrasting roof hatch/windscreen, paired sun pads and open stern remain readable overhead; small rail
and cleat hardware intentionally recedes. No harbour density or motor/sailing comparison is claimed.
An initial sheer-cap/inlay intersection was corrected before final validation and renders.

Hero, side and overhead are **1280×720**; detail is **1024×576**. PNG compression is 95, output dithering
is disabled, and all four files are under 400 KB. The lean-evidence size cap takes precedence over the
historical 1280×800 example; overhead still uses a vertical-down 47 m height, 42° vertical FOV and fixed
north-up yaw. The overhead studio plane is at waterline; hero/side/detail show the full dry hull above
a slate studio floor. These are not in-engine captures or accepted gameplay-camera evidence.

[validation.json](city_moored_yachts_01-evidence/validation.json) records:

- **7,626 triangles**, **3,941 Blender vertices**, **4,525 exported vertices** (normal/material splits),
  **one mesh**, **seven surfaces**, GLB **197,480 bytes**.
- **Zero non-manifold edges, zero degenerate faces/triangles** in source and zero exported degenerate
  triangles. Maximum unit-normal error: source 1.77e-7, GLB 1.42e-7.
- Declared membership, applied transforms, metre units, exact pivot, independent envelope expectations,
  source/GLB axis and bounds equivalence, actual exported normals/materials and no external images.
- A fresh export from the saved `.blend` is **byte-identical** to the committed GLB.
- Pinned Godot loaded linked dependencies, measured bounds/material surfaces, resolved UIDs and passed
  normalized scene byte stability. No scene import fallback or missing dependency error occurred.
- Actual physics rays stop on hull and cabin; a swept 0.10 m projectile sphere stops on the hull.
  Separate rays above the asset, below water, through the visual-only bow rail height and outside the
  hull remain clear. These test world collision APIs, not a nonexistent boat damage/weapon system.
- The production saved `scenes/entities/player.tscn` and `ActorMotion.step` pass **six bounded motion
  cases**, 120 commands per case, with the existing radius 0.35 m / height 1.8 m actor at foot Y=0.55 m.
  Authority and replay endpoints are exactly identical: hull stop **X=2.150393 m**, bow stop
  **Z=-6.570313 m**, clear stern bypass **X=-6.000001 m**. No network transport, admission, actual dock
  floor, stepping aboard or water behavior was exercised.

The final canonical production check passes: **106/106 GDScript compilations**, pinned gdstyle
lint/format checks, **14 Python tests**, **75/75 GUT tests / 2,041 assertions**, and the expected negative
GUT failure probe. No known-failure exemptions were needed. See the concise
[final.log](city_moored_yachts_01-evidence/final.log).

Tool limitations are retained rather than suppressed:

- The first bare `production_checks.py` invocation resolved the machine's `gdvm` wrapper and failed
  engine-version decoding before tests ran. The corrected/final command explicitly selects both
  mise-pinned executable paths and UTF-8; all checks pass.
- A first attempt to execute `ActorMotion` in `--editor` mode exposed Godot's non-tool script stubs.
  The check now separates editor normalization from runtime motion and fails closed on incomplete
  asynchronous cases. Final runtime output has no errors or warnings.
- The CLI editor's shutdown reports plugin version advice and RID/ObjectDB leaks. A four-second
  `SceneTree` control that never loads/instantiates the yacht produced **the identical leak signature**:
  5 viewports, 8 textures, 1 scenario, 52 shaped-text objects, 1 font, 5 canvases, 31 canvas items and
  168 ObjectDB instances. These are editor-harness/environment diagnostics, not silently counted as a
  clean editor exit. Asset checks and runtime are successful. No live editor was used or synchronized.
- Blender emits its pinned API deprecation advice for `use_nodes`; final author/validator calls exit 0.

## Exact reproduction

Run from the repository root in Git Bash. Every engine call is bounded; raw logs, intermediate files
and retries belong under `C:/tmp/ft/assets/city_moored_yachts_01/`, never the repository.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="$(mise which gdstyle)"
T='C:/tmp/ft/assets/city_moored_yachts_01'
N='city_moored_yachts_01'
mkdir -p "$T/godot-user/appdata" "$T/godot-user/localappdata"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONUTF8=1
export APPDATA="$T/godot-user/appdata" LOCALAPPDATA="$T/godot-user/localappdata"
# Check the retained producer payload before rebuilding any source container.
python "tools/asset_production/$N/validate.py" --verify-manifest

timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "tools/asset_production/$N/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "tools/asset_production/$N/validate.py"
# validate.py already performs and compares a fresh saved-source export.
# Optional independent export invocation, to a scratch directory only:
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 "art/source/models/environment/$N/$N.blend" \
  --python "tools/asset_production/$N/export.py" -- "$T/independent-export"

timeout 300 "$G" --headless --editor --path . --import --quit
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$N/check_prefab.gd"
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$N/check_prefab.gd"
"$S" "tools/asset_production/$N/check_prefab.gd"
"$S" fmt --check "tools/asset_production/$N/check_prefab.gd"
# Output directory must be fresh; retained final run used checks-final.
timeout 1800 python tools/production_checks.py --godot "$G" --gdstyle "$S" \
  --output "$T/checks-reproduction"
```

`author.py` regenerates source/export/renders; `validate.py` regenerates geometry evidence; run editor
then runtime checks to restore engine evidence. A newly saved `.blend` may have different container
bytes even when its fresh GLB is identical. After an intentional production change, update this record
and final log, then reseal with `python tools/asset_production/city_moored_yachts_01/validate.py
--manifest-only`. The producer [manifest](city_moored_yachts_01-evidence/manifest.json) hashes every
owned delivered file except its own self-referential hash; scratch files are not deliverables.

## Remaining acceptance

Independent technical/art review is required. Whole-city basin/dock placement, fender/berth clearance,
conservative-collider margins, actual pontoon-to-yacht interaction, combat/rocket integration, real
multiplayer transport, in-engine lighting/camera readability, repeat-placement LOD cost and target-device
performance remain pending. No boarding, piloting, sail, wake, damage or buoyancy feature is implied.
No catalogue/register READY claim, TODO closure or accepted sector placement is made by this handoff.
