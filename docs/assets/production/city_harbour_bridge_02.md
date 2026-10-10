# city_harbour_bridge.02 — Matching low parapet pair

**Source/export and linked-prefab candidate; independent review and world acceptance pending.**
Produced by the commissioned implementation specialist on `lane/a-hbridge`.
The [commission](commission.md) and current asset-common production brief supersede
concept-only wording in the [family brief](../city_harbour_bridge.md). Original Blender
construction; no downloaded/purchased/image-to-mesh geometry, brands or textures.
No sibling asset, world placement, register, shared brief or project setting was changed.

## Design and dimensions

Two continuous low civic concrete parapets, dark petrol metal coping, a quiet seven-metre
casting rhythm and three small warm inset markers on the inward face of each side.
Broad smooth bevels and restrained materials match [the completed structural deck](city_harbour_bridge_01.md).
The design follows Old Quay's municipal waterfront character and preserves visible water
under the one existing crossing. No new road surface, ramp, pier, second crossing, interior,
animated hardware or illumination system is introduced.

The pair is one registered component-set export: both guards share the deck-centred pivot
and are installed together at identity relative to `.01`, not scaled as independent rails.
The inherited deck footprint is **91 × 17 m**, local +X along the crossing. Its 0.35 m
flush shoulders own the placement reservation. Height and detailed proportions below are
**provisional production values**, not structural/safety certification or a layout change.

| Contract | Metres, Godot local axes |
| --- | --- |
| Pair AABB minimum / maximum | `(-45.5,0,-8.5)` / `(45.5,1.1,8.5)` |
| Pair X width / Y height / Z length | **91 / 1.10 / 17** |
| Each guard envelope | **91 × 1.10 × 0.35** |
| North / south centre lines | Z=`-8.325` / `8.325` |
| Shoulder occupation | Z=`[-8.5,-8.15]` and `[8.15,8.5]` |
| Full clear width between guards | **16.30** |
| Roadway reference / clear walk corridor each side | **9.00 / 3.65** |
| Pivot / contact datum | `(0,0,0)`, centre of pair at deck top; both feet at Y=0 |
| Continuous base / main wall / coping | base 0–0.16; main wall 0.10–0.98; coping 0.96–1.10 |
| Main wall / coping width | 0.30 / 0.35 |
| Casting rhythm | 13 bays at 7 m; 14 narrow joint collars per side |
| Marker centres | X=`-35,0,35`, Y=0.78; inward faces only |
| Marker face / emission | 0.40 × 0.075; 0.25 appearance-only emission strength |
| Numeric envelope tolerance | ±0.001 |

All markers, collars and coping remain inside the shoulder envelope. Blender +Y maps to
Godot -Z, and Blender +Z to Godot +Y. Both root and mesh have applied identity transforms.
The pair's pivot is deliberately centred between the two ground-contact strips, not on one rail.

### Family interface

Place at identity with `.01` and retain the bank end planes X=±45.5, Y=0. `.03` owns final
bank-end trim: it must meet the existing square guard ends without blocking the roadway or
creating a raised full-width threshold. No side-return or invisible across-road blocker is
included here. The road tool still owns road/sidewalk surface dressing and final surface
datums. The inherited water reference is Y=-2.1; this pair adds nothing below Y=0 and does
not narrow the deck's 0.85 m under-girder water gap. No world replacement was performed.

## Source, export, materials and prefab

- Source: `art/source/models/environment/city_harbour_bridge_02/city_harbour_bridge_02.blend`.
- Collection: `export_city_harbour_bridge_02`; root `CityHarbourBridge02`, child mesh
  `CityHarbourBridge02_Mesh`. One joined mesh contains the two matched guards.
- Explicit export: `art/models/environment/city_harbour_bridge_02/city_harbour_bridge_02.glb`
  with Godot-generated `.glb.import` metadata.
- Saved wrapper: `scenes/prefabs/environment/city_harbour_bridge_02.tscn`.
  `Visuals/Model` remains an identity-transform imported instance, not copied mesh data.
- Five opaque, back-culling Principled surfaces: `bridge_civic_concrete`,
  `bridge_pale_fascia`, `bridge_petrol_steel`, `bridge_recess`, `bridge_warm_marker`.
  The first four use the sibling's exact PBR values. Full exported values are in validation.json.
- No textures, embedded images, external material overrides, sockets, rigs, clips,
  destruction states or real light nodes. Godot default automatic import LOD is retained;
  no explicit LOD budget or device-performance acceptance is claimed.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. The exporter loads
`tools/assets/blender/export_settings.json` with the named collection filter and static
animation/skin exclusions. Authoring reuses the existing `.01/author.py` material/box/finish
helpers read-only, keeping the family bevel and normal treatment consistent rather than
introducing another helper library. Validation and rendering entrypoints follow the sibling's
established conventions. Rebuilding requires that earlier sibling's tools and source to remain
available. Render-only deck context is appended from its unchanged `.blend`, never re-exported.

Collision is separate at `Collision/Body`: one static body, layer 1 / mask 0, with **two**
BoxShape3D instances, size `(91,1.1,0.35)`, centred at `(0,0.55,±8.325)`.
These continuous thin barriers deliberately fill small bevel recesses and prevent decorative
collars/markers from snagging actors. This wrapper has no walk-plane collider: `.01` owns
continuous deck support. Avoid duplicate support collision when integrating generated surfaces.

The required isolated fallback used text-authored scenes, then pinned headless load/pack/resave.
Scene UIDs and generated node identities are retained in the saved `.tscn`; the check script's
`.gd.uid` is retained. Godot does not generate a separate `.tscn.uid` for these scenes.
No owner live Blender/Godot session was used or touched. Headless import does not establish
synchronization of any separate open editor scene.

## Evidence and validation

[Hero](city_harbour_bridge_02-evidence/hero.png) ·
[side](city_harbour_bridge_02-evidence/side.png) ·
[inner marker detail](city_harbour_bridge_02-evidence/detail.png) ·
[47 m / 42° overhead](city_harbour_bridge_02-evidence/overhead_47m_42deg.png).
All four are isolated Blender renders, **1280×720**, inspected by the producer. The `.01` deck
is unchanged read-only context; the teal studio plane at Y=-2.1 is not an exported asset.
Hero and side show both bank ends/full span; detail shows the marker, broad coping and casting
joints. The true north-up vertical perspective camera at 47 m / 42° vertical FOV intentionally
crops the long span. Both edge lines remain continuous and quiet; markers are subtle, not
large navigation cues. Road-tool dressing is absent. These are not final in-engine captures.
PNG compression 9 and seven significant RGB bits keep evidence below the approximate 400 KB target.

`city_harbour_bridge_02-evidence/validation.json` records:

- **8,648 triangles; 4,416 source vertices; 5,330 GLB vertices; one mesh; five surfaces.**
- **Zero degenerate faces, zero non-manifold edges**, finite coordinates, consistent outward
  winding, unit source/exported normals, applied transforms, and the measured AABB above.
  Manufactured pieces are individually closed overlapping shells, not one boolean solid.
- Binary GLB positions, normals and triangle indices inspected, not just accessor metadata.
  No exported studio nodes, textures, cameras, skins or animation. Each side fills the complete
  91 m span, stays inside its shoulder and touches the deck datum.
- A fresh independent Blender process re-exported a **byte-identical** GLB.
- Pinned Godot **4.8.dev7.official.c971f93e7** dependency/UID resolution, imported bounds,
  identity-linked mesh, five opaque surfaces, exact guard collider envelopes/layers and stable
  load/pack/resave bytes for both the prefab and saved `guard_check.tscn` fixture.
- **14 guard-hit rays** at both ends, collars and intermediate points; **three clear rays**
  for the water mouth, space above the low guard and longitudinal roadway.
- Production `ActorMotion.step` and `FootCommand` with radius **0.35**, height **1.8** capsule:
  **120 blocking ticks plus 240 sidewalk-walking ticks per side per mode**, both AUTHORITY
  and REPLAY, **1,440 ticks total**. Contact Z=`±7.7994804`; 20 m sidewalk traversal ends
  X=`9.9999971`; no snagging or lateral drift. Authority/replay outcomes match.
  This is local production movement equivalence, **not separate-process multiplayer or car driving**.
- Canonical production checks passed: formatting, style and all-script compilation;
  **16 Python tests; 142/142 GUT tests, 6,705 assertions**; intentional negative diagnostic test
  correctly exits 1. No known-failure exclusions were needed.

Headless import emitted the existing third-party MCP 4.8 compatibility warning. Editor-mode
normalization completed all assertions but reported editor/plugin RID/ObjectDB shutdown leaks,
matching the earlier sibling's diagnostics. The subsequent runtime check passed without
errors/warnings, as did the clean compiler mirror. The Blender render log contains the pin's
`Material.use_nodes` deprecation notice; it is not an export failure. These diagnostics were
reviewed, not suppressed. A concise receipt is `final.log`; scratch/raw logs live outside the
checkout at `C:/tmp/ft/assets/city_harbour_bridge_02/`. The producer `manifest.json` hashes every
delivery payload (self excluded).

## Exact reproduction (Git Bash, repository root)

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=tools/asset_production/city_harbour_bridge_02
S=art/source/models/environment/city_harbour_bridge_02/city_harbour_bridge_02.blend
O=C:/tmp/ft/assets/city_harbour_bridge_02
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
# Source rebuild also exports. Do not run while editing the source.
timeout 300 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 "$S" --python "$T/export.py" -- "$O/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$O/reexport/city_harbour_bridge_02.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
timeout 300 "$(mise which godot)" --headless --editor --path . --import --quit
timeout 180 "$(mise which godot)" --headless --editor --path . --script "res://$T/check.gd" -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script "res://$T/check.gd"
timeout 30 "$(mise which gdstyle)" "$T/check.gd"
# Put actual pinned binaries before Windows mise shims; UTF-8 avoids cp1252 decoding faults.
GODOT_DIR=$(dirname "$(cygpath -u "$(mise which godot)")")
STYLE_DIR=$(dirname "$(cygpath -u "$(mise which gdstyle)")")
# The checker requires a fresh external output directory for each reproduction.
PATH="$GODOT_DIR:$STYLE_DIR:$PATH" PYTHONUTF8=1 timeout 1800 python tools/production_checks.py --output "$O/checks-repro"
python "$T/manifest.py" "$O/checks-repro"
```

## Remaining acceptance and integration gates

Independent technical/art review remains pending. World integration must combine the deck,
parapets and `.03` bank trims without duplicate road/support geometry; preserve existing route,
water and final generated surface datums. Final bank-edge transitions, actual vehicle turning
and impact/sliding, movement through complete approaches, final gameplay-camera visibility,
separate-process multiplayer, packaged builds and sustained Deck/performance checks remain
pending. This delivery does not place a bridge, certify structural safety, close a register
record or change authoritative gameplay rules.
