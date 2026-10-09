# city_moored_yachts.02 — small sailing yacht

**Source, explicit export and blocking prefab delivered; independent review and world placement
pending.** Production follows the [commission](commission.md) and current per-asset lane assignment,
which authorizes this asset's prefab/import/commit. The historical concept-only language in the
[family brief](../city_moored_yachts.md) does not prohibit this commissioned delivery.

Producer: commissioned implementation specialist `worker`, branch `lane/a-yachts`.
Accepting owners: production supervisor / independent asset reviewer. World integration is separate.
The earlier [motor yacht](city_moored_yachts_01.md), shared briefs, register, progress and world scenes
were read but not modified.

## Design and dimensions

Original Blender construction: a slender sailing hull with rising pointed bow, raked transom, fin
keel, rudder, low coachroof, broad petrol side glazing and an open cockpit with a simple tiller.
One tapered mast, one spreader and four stays support a compact furled mainsail above the boom.
Three broad navy sail ties, short bow/stern rails, four fenders, four cleats and two winches are
integrated boat fittings, not a separate prop catalogue. No unfurled sail, interior, logo, downloaded
geometry, external artwork, image-to-mesh content, rig or animation is included.

References inspected: [Old Quay identity](../../concepts/world-v1/stage-03-district-identities/README.md#old-quay--the-warm-edge-of-the-water),
[streets and basin constraints](../../concepts/world-v1/stage-04-streets/README.md),
[Old Quay concept](../../concepts/districts-v1/old-quay.md), [marina docks](../city_marina_docks.md),
`city_lights_01` end-to-end evidence/tooling and the batch integration conventions.
The quiet ivory/sand/petrol/coral vocabulary matches .01, while the narrower hull, low coachroof,
central furled sail and tall sparse mast distinguish .02 through shape rather than paint.

Before construction the supervisor approved **provisional production bounds and interfaces**:
11.6 m nominal length, 3.4 m beam including fenders, 1.6 m draft, 10.0 m mast top above water,
waterline-centred root, bow Godot -Z, low coachroof/open cockpit, single mast/boom/furled ivory sail,
sparse stays, no dock-dependent ropes or sockets, and layer-1/mask-0 hull/coachroof blocking.
Mast and rigging are visual-only, including everything above approximately 2.5 m. These bounded
choices do not approve basin density, berth clearance, boarding or any boat simulation.

| Measurement | Delivered value |
| --- | --- |
| Godot X/Y/Z dimensions | **3.400000 × 11.600000 × 11.623590 m** |
| Godot AABB minimum | **(-1.700000, -1.600000, -5.809889) m** |
| Godot AABB maximum | **(1.700000, 10.000000, 5.813701) m** |
| Root and mesh origin | (0, 0, 0), nominal waterline footprint centre; **not keel/ground contact** |
| Draft / above-water height | 1.600 / 10.000 m |
| Main hull beam / maximum fender beam | 3.100 / 3.400 m |
| Main sheer height | 0.730 m aft to 1.130 m at bow; rim adds 0.055 m |
| Coachroof / hatch top | 1.550 / 1.635 m above water |
| Mast centre / boom centre | Godot Z=-0.630 m / Y=2.150 m |
| Furled sail | approximately 3.85 m long, 0.58 m maximum width, top Y=2.59 m |
| Coordinate contract | Blender +Y bow, +Z up → Godot -Z bow, +Y up; applied transforms |

Envelope tolerance is 0.015 m **per AABB endpoint** (0.030 m total length tolerance), accounting for
rub-strake endcaps extending 9.89 mm at the bow and 13.70 mm aft. Draft/top-height and engine bounds
checks use 0.001 m; source/export equivalence uses 0.00001 m. Place root Y at the authored water
surface, not 1.6 m above it. Waterline is a static placement datum, not buoyancy. No mooring endpoints,
entry markers or dock-dependent ropes promise a particular attachment. Berth spacing remains pending.

## Source, export and materials

- Source: `art/source/models/environment/city_moored_yachts_02/city_moored_yachts_02.blend`.
- Named export collection: `export_city_moored_yachts_02`.
- Export root/mesh: `CityMooredYachts02` / `CityMooredYachts02_Mesh`.
- Explicit linked export: `art/models/environment/city_moored_yachts_02/city_moored_yachts_02.glb`,
  with retained `.glb.import`. The existing source `.gdignore` excludes the Blender source from Godot.
- Parametric authoring, export, validator and prefab check:
  `tools/asset_production/city_moored_yachts_02/`.
- Prefab: `scenes/prefabs/environment/city_moored_yachts_02.tscn`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. The export reads shared
`tools/assets/blender/export_settings.json`, filters the declared collection and disables animation
and skins for this static prop. No project setting or shared export contract changed.

One consolidated mesh contains separately closed, intentionally overlapping manufactured component
islands; zero non-manifold edges does not mean one Boolean-welded solid. All modifiers are applied.
Root/mesh location and rotation are zero, scale is one. Cameras, lights and studio floor remain
outside the export collection. There are no external images, textures, hidden geometry dependencies,
light nodes, shaders, morphs, animations or skins in the GLB.

Seven opaque, backface-culled Principled material surfaces, in export order:

| Slot | Material | Linear RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `hull_ivory` | (0.88, 0.87, 0.77) | 0.08 / 0.31 |
| 1 | `waterline_navy` | (0.025, 0.045, 0.063) | 0.05 / 0.45 |
| 2 | `deck_sand` | (0.38, 0.28, 0.17) | 0 / 0.65 |
| 3 | `sail_canvas` | (0.70, 0.67, 0.54) | 0 / 0.72 |
| 4 | `accent_coral` | (0.90, 0.19, 0.12) | 0 / 0.60 |
| 5 | `glazing_petrol` | (0.018, 0.066, 0.081) | 0.30 / 0.23 |
| 6 | `hardware_slate` | (0.39, 0.47, 0.49) | 0.65 / 0.30 |

`sail_canvas` also covers quiet cushions/fenders using the same cream value as .01 upholstery.
Glazing is deliberately opaque; it does not expose an interior. No external material remap or
texture/UV-density contract is needed. Default automatic import LOD/shadow-mesh settings remain;
thin-stay LOD transitions, temporal aliasing and repeated-placement performance are not measured.

## Prefab and collision

`Visuals/Model` is an **identity-transform imported GLB instance**, with no editable imported children
or copied mesh arrays. Pinned headless Godot normalized the text-authored wrapper and generated its
scene UID/node identities. Save/reopen/resave preserves exact normalized bytes. The scene UID is
embedded in `.tscn`; the validator script has its required `.gd.uid` sidecar.

`Collision/Body` is a `StaticBody3D`, layer **1**, mask **0**, with three direct box-shape children:

| Shape | Godot centre (m) | Size X/Y/Z (m) |
| --- | --- | --- |
| Hull | (0, 0.500, 1.050) | (3.200, 1.000, 9.500) |
| Bow | (0, 0.600, -4.755) | (1.950, 1.200, 2.130) |
| Cabin | (0, 1.210, 0.050) | (2.120, 0.720, 4.320) |

These are conservative blocking envelopes, not precise hull/deck contact surfaces. Hull and bow
start at waterline; cabin runs Y=0.85–1.57 m. The tapered bow and transom corners are overblocked.
There is no underwater collider and no boarding floor or interior passage. Mast, stays, boom,
furled sail, rails, fenders, cushions, winches and cleats are visual-only; the mast has no separate
collision even below 2.5 m. Tiny nautical fittings cannot snag actors/projectiles. Placement must not
put pontoons inside the conservative boxes. No health, damage, vehicle, navigation, interaction or
network component is attached.

## Validation and evidence

[Hero](city_moored_yachts_02-evidence/hero.png) · [side](city_moored_yachts_02-evidence/side.png) ·
[furled sail/cockpit detail](city_moored_yachts_02-evidence/detail.png) ·
[47 m / 42° overhead](city_moored_yachts_02-evidence/overhead_47m_42deg.png).
All four final isolated Blender renders were inspected. The central narrow furled-sail strip,
three broad ties, spreader and sparse stays remain visible without a web of lines at overhead scale;
the narrow low-roof silhouette differs from .01's broad motor-cabin roof. Fine hardware intentionally
recedes. Static renders do not establish temporal anti-aliasing, motion readability or harbour density.

All renders are **1280×720**, PNG compression 95, no output dithering. Hero/side/overhead are
308,132 / 225,058 / 203,086 bytes; detail is 437,969 bytes (428 KiB, near the approximate 400 KB target).
The current production evidence cap and supervisor instruction supersede the historical 1280×800
example. Overhead is vertical-down, fixed north-up, 47 m high with 42° vertical FOV. The overhead
studio floor is at waterline; other views show the full dry hull over a slate studio floor. An initial
side-view floor horizon was removed by enlarging only the non-export studio plane. Detail framing
was widened to reduce evidence size. These are not Godot or accepted gameplay captures.

[validation.json](city_moored_yachts_02-evidence/validation.json) records:

- **7,004 triangles**, **3,644 Blender vertices**, **4,040 exported vertices**, one mesh,
  seven material surfaces, GLB **178,228 bytes**.
- **Zero non-manifold edges and zero degenerate source faces/triangles**; zero exported degenerate
  triangles. Maximum unit-normal error is **1.76e-7 source / 1.21e-7 GLB**.
- Exact export membership, metres, applied transforms, pivot, independent envelope expectations,
  source/GLB coordinate mapping, exported materials/normals and absence of external images.
- A fresh export from the saved `.blend` is **byte-identical** to the delivered GLB.
- Godot resolves model/prefab UIDs, loads linked dependencies, checks measured bounds/materials,
  and passes normalized save/reload byte stability.
- Actual world rays hit hull and coachroof; a swept 0.10 m projectile sphere stops on the hull.
  Rays through the mast at Y=5 m, below waterline, above the bow rail region and outside the hull
  stay clear. These are physics API tests, not complete weapon/rocket integration.
- The production saved player and `ActorMotion.step` pass six bounded motion cases, 120 commands
  each, with the existing 0.35 m radius / 1.8 m actor at foot Y=0.55 m. Authority and replay endpoints
  match exactly: hull stop **X=1.950523 m**, bow stop **Z=-6.170899 m**, clear stern bypass
  **X=-6.000001 m**. No dock floor, boarding, water behavior, network admission or transport ran.

Canonical production checks pass: **107/107 GDScript compilations**, pinned gdstyle format/lint,
**14 Python tests**, **75/75 GUT tests / 2,041 assertions**, and expected nonzero negative GUT probe.
No known-failure exemption was needed. See [final.log](city_moored_yachts_02-evidence/final.log).

Tool diagnostics are not suppressed: Blender emits pinned `use_nodes` deprecation advice. The
headless editor emits plugin version advice plus the same exit-leak signature documented by the
.01 no-yacht control: 5 viewports, 8 textures, 1 scenario, 52 shaped-text objects, 1 font, 5 canvases,
31 canvas items and 168 ObjectDB instances. Asset assertions pass; runtime has no errors/warnings.
Initial gdstyle format check requested reformatting; applying the pinned formatter resolved it.
No live Blender/Godot editor was used or synchronized. Import is not claimed as all-script validation.

## Exact reproduction

Run from repository root in Git Bash; scratch outputs stay outside the repository:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="$(mise which gdstyle)"
N='city_moored_yachts_02'
T="C:/tmp/ft/assets/$N"
mkdir -p "$T/godot-user/appdata" "$T/godot-user/localappdata"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONUTF8=1
export APPDATA="$T/godot-user/appdata" LOCALAPPDATA="$T/godot-user/localappdata"
python "tools/asset_production/$N/validate.py" --verify-manifest

timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "tools/asset_production/$N/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "tools/asset_production/$N/validate.py"
# Validator already performs a fresh saved-source export and strict byte comparison.
# Optional independent export goes to scratch, never over the production output:
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
# Use a fresh output directory; the retained final run used checks.
timeout 1800 python tools/production_checks.py --godot "$G" --gdstyle "$S" \
  --output "$T/checks-reproduction"
```

`author.py` regenerates source/export/renders. `validate.py` rewrites source/export evidence; run
editor then runtime checks afterward to restore engine results. A newly saved Blender container may
have different bytes despite identical exported geometry. After an intentional production revision,
update this record/final log then run `python tools/asset_production/city_moored_yachts_02/validate.py
--manifest-only`. The [producer manifest](city_moored_yachts_02-evidence/manifest.json) hashes every
owned delivered file except its self-referential hash. No scratch renders or raw multi-file logs are
committed.

## Remaining acceptance

Independent technical/art review remains required. World integration owns basin/bridge clearance,
open-water density, berth spacing and fender/pontoon fit. Conservative blocking margins, actual dock
movement/combat interaction, real multiplayer transport, in-engine lighting/camera readability,
thin-stay LOD/temporal behavior and target-device performance remain pending. No piloting, boarding,
sail operation, wakes, buoyancy or damage feature is commissioned. No register READY status, TODO
closure or accepted sector placement is asserted.
