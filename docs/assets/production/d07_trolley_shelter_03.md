# d07_trolley_shelter.03 — Compact nested trolley group

**Saved assembly and bounded technical checks delivered; independent review and full
world/gameplay acceptance pending.** Producer: commissioned implementation specialist.
The register task and [commission](commission.md) supersede the historical concept-only
restriction in the [family brief](../d07_trolley_shelter.md).

## Design and dimensions

Three existing [single trolleys](d07_trolley_shelter_02.md) in a shallow nested line, with
one intentional static group envelope. Broadlot's sparse retail dressing retains the
pale basket mass, dark petrol chassis and coral handle rhythm. No shopping, pushing,
loose physics, goods, signage or new trolley design. This is an **Assembly reference**:
the saved Godot scene is its editable source; no new `.blend`, GLB or carrier geometry
is appropriate. Every visible mesh remains linked to the original Blender-authored `.02`.

References inspected: Petrol & Coral; approved Stage 3 Broadlot identity; Stage 4 streets;
existing [shelter](d07_trolley_shelter_01.md), trolley and accepted city_lights.01/batch
handoff conventions. No concept image supplies inferred measurements. All arrangement
values below are **provisional authored choices**, not world-placement acceptance.

| Contract | Metres, Godot local axes |
| --- | --- |
| Width X × height Y × depth Z | 0.680 × 1.080 × 2.490 |
| Visual and group collider AABB | (-0.340, 0, -1.245) → (0.340, 1.080, 1.245) |
| Root pivot | (0, 0, 0), ground-centred footprint |
| Front | All three basket noses point -Z; Blender +Y maps to Godot -Z |
| `Trolleys/Front` position | (0, 0, -0.720) |
| `Trolleys/Middle` position | (0, 0, 0) |
| `Trolleys/Rear` position | (0, 0, +0.720) |
| Instance bases | Identity rotation/scale; no lifting, tilting or corrective transforms |
| Box size / centre | (0.680, 1.080, 2.490) / (0, 0.540, 0) |
| Bound tolerance / contact tolerance | ±0.001 / 0.000001 |

The sibling's untested 0.45 m pitch was rejected: source triangle checks exposed chassis
and basket/frame crossings. A 0.70 m trial still crossed upper rails/handle uprights;
**0.72 m is the delivered pitch**. Basket upper-rail centre spans overlap longitudinally
by approximately 0.06 m; this is deliberately shallow nesting, not the tightly compressed
arrangement a different trolley design might permit. Three 1.05 m standalone footprints
would occupy 3.15 m nose-to-tail; this group occupies 2.49 m. Geometry is unchanged.

Adjacent front/rear rubber wheel sidewalls touch at X ±0.25 m. Blender BVH reports 36
triangle contact pairs per adjacent pair, all restricted to rubber sidewall triangles
in opposite X halfspaces within 1 micrometre; no unintended crossing pairs remain.
The nonadjacent trolleys have no contacts. This tolerance handles float-level coplanar
wheel contact, not arbitrary mesh penetration. Source mesh islands retain their original
manufactured joints; no Boolean union or new mesh export was introduced.

## Source, dependencies and materials

- Editable assembly: `scenes/prefabs/environment/d07_trolley_shelter_03.tscn`.
- Three instances of `scenes/prefabs/environment/d07_trolley_shelter_02.tscn`.
- Each retains identity-transform `Visuals/Model` linked to
  `art/models/environment/d07_trolley_shelter_02/d07_trolley_shelter_02.glb`.
- Original source: `art/source/models/environment/d07_trolley_shelter_02/d07_trolley_shelter_02.blend`,
  collection `export_d07_trolley_shelter_02`, root `D07TrolleyShelter02`, mesh
  `D07TrolleyShelter02_Mesh`. No sibling source/export/import/prefab was modified.
- Four unchanged opaque Principled slots: `trolley_frame_petrol`, `trolley_basket_metal`,
  `trolley_wheel_rubber`, `trolley_handle_coral`; full measured PBR values are retained in
  validation.json. No material overrides, textures, embedded images or new materials.
- No rigs, sockets, clips, interactive states, destruction or manual LODs are required.
  Existing generated Godot LOD/shadow settings are unchanged; cost is not a budget.

Tools under `tools/asset_production/d07_trolley_shelter_03/`:
`assembly.py` reads literal transforms from the saved scene; `render.py` renders unchanged
source mesh instances; `validate.py` measures composition and reuses `.02/validate.py`
with its output redirected to scratch; `check.gd` extends `.02/check.gd` to reuse safe
save/dependency helpers; `record.py` compacts evidence and hashes final payloads.
No runtime hierarchy builder, duplicate exporter or private copy of the component model.
The existing sibling validator loads `tools/assets/blender/export_settings.json` through
`.02/export.py` and uses `.01/validate.py`'s binary accessor reader. Render camera aiming
reuses `.01/author.py`; the studio is already in the unchanged `.02` Blender source.

## Prefab, collision and shelter interface

`Trolleys/{Front,Middle,Rear}` remain linked prefab instances. Only the existing component
`Collision/TrolleyBody/Envelope.disabled` property is overridden. Saved editable paths
refer to the **project-owned component wrapper**, not imported GLB children. There are
no imported-child material/identity overrides or copied vertices. The three inherited
static bodies remain empty of active shapes. `Collision/GroupBody/Envelope` is the one
active simple box, direct child of a static-world body on layer 1 / mask 0.

This envelope fills basket, chassis and inter-trolley gaps deliberately: they are not
walkable interiors or precision bullet-cover holes. It prevents snagging and makes the
freestanding assembly block actors/cars. Actual movement and vehicle behavior remain
unaccepted; the bounded public-physics queries below are not those gameplay tests.

Optional interface to the existing `.01` shelter: place this group at **(0, 0, -0.05)**
relative to the shelter, rotated **180° about Y** so noses face the rear stop. This is
a documented fitting transform tested headlessly, not a second saved world placement.
It occupies X ±0.34, Y [0,1.08], Z [-1.295,+1.195] within the sibling's proposed
X [-1,+1], Y <1.50, Z [-1.30,+1.20] region. Front/rear region margins are only 0.005 m;
do not increase pitch or count without rechecking. Actual rear-stop collision starts at
Z +1.400, leaving 0.205 m. Each side gap between group and shelter collision is 0.790 m:
bounded 0.35 m-radius capsule queries fit, but this is **not an approved through-route**.
The pale shelter roof hides the trolleys from directly above. Placement must not promise
under-canopy visibility or solve recognition by adding arbitrary extra geometry.

The task prohibits live MCP/editor sessions and reports the windowed editor unavailable.
Direct-text scene authoring was therefore followed by isolated pinned headless
load/pack/resave normalization and **two further byte-stable save/reload roundtrips**.
This proves saved scene/UID/node-identity stability, not synchronization of an open editor.

## Evidence and reproduction

[Hero](d07_trolley_shelter_03-evidence/hero.png),
[side](d07_trolley_shelter_03-evidence/side.png),
[basket/handle nesting detail](d07_trolley_shelter_03-evidence/detail.png),
[47 m / 42° overhead](d07_trolley_shelter_03-evidence/overhead_47m_42deg.png).
All four were visually inspected. Close views show clean repeated basket/handle forms,
shallow entry and touching wheel sidewalls without frame intersections. At gameplay
height the assembly is a small pale strip with three coral divisions; fine ribs disappear.
Retail reading still depends on sparse parking/shelter context and actual engine lighting.
No essential lettering, enlarged model or cropped close-up substitutes for the overhead.

Isolated Blender 5.2.2 LTS (`d13f752e3b9c`), glTF exporter 5.2.40; Cycles CPU, AgX,
32 samples, 1280×720. Overhead is **vertical-down perspective**, 47 m height and 42°
vertical FOV, not a 42° camera tilt. Camera/framing changes affect evidence only. PNGs
use render compression 100 and idempotent six-significant-bit RGB compaction with lossless
PNG compression level 9. There are no new runtime textures. No duplicate `.blend` is saved.

From repository root in Git Bash, with fresh/empty suite output:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/d07_trolley_shelter_03
S=C:/tmp/ft/assets/d07_trolley_shelter_03
mkdir -p "$S"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" -- --normalize
timeout 30 "$(mise which gdstyle)" check "$T/check.gd"
PYTHONUTF8=1 timeout 1800 python tools/production_checks.py --godot "$G" --gdstyle "$(mise which gdstyle)" --output "$S/checks"
python "$T/record.py" --checks "$S/checks"
timeout 300 "$G" --headless --path . --import
python "$T/record.py" --checks "$S/checks"
```

`validate.py` freshly exports the committed `.02` source to this asset's scratch folder
and compares bytes; no sibling evidence/source/export is overwritten. The only sibling
change is the supervisor-approved stale Remaining acceptance link in `.02.md` and that
doc's size/hash entry in its manifest. Historical receipts remain unchanged. The current
`.03` manifest includes those two amended handoff files as well as all `.03` payloads.

## Validation results

[validation.json](d07_trolley_shelter_03-evidence/validation.json) records measured
source/export, composition, engine checks and suite results.
[manifest.json](d07_trolley_shelter_03-evidence/manifest.json) hashes every produced payload
except itself and records read-only dependencies.
[final.log](d07_trolley_shelter_03-evidence/final.log) is the concise final receipt;
raw logs, rejected trial data and fresh reexports stay under the scratch path above.

- **Zero new meshes/exports; three mesh instances sharing one imported mesh resource.**
- Component: **4,296 triangles, 2,240 source vertices, 3,550 exported vertices, four surfaces**.
  Group: **12,888 triangles, 6,720 source-vertex instances, 10,650 exported-vertex instances,
  12 surface instances**. These are unsimplified totals, not measured draw calls or a budget.
- Freshly checked component: zero degenerate faces/triangles and non-manifold source edges;
  unit source/export normals, maximum length errors 1.893e-7 / 1.243e-7.
- Fresh `.02` GLB byte-identical: 143,548 bytes; SHA-256
  `ce51d11d469a69b0ab9f04ebcda2e10332f8bc4ce24e6872933d796a12434b25`.
- Group source/imported dimensions match 0.680 × 1.080 × 2.490 m; ground datum zero.
  Adjacent source BVH pairs: 36 + 36 tolerated rubber sidewall contacts; **zero unintended
  crossing pairs**. Nonadjacent pair: zero contacts.
- Godot **4.8.dev7.official.c971f93e7** resolves all group/component/GLB resource UIDs,
  preserves imported identity transforms, shares one mesh, and retains exact scene bytes
  across two normalized roundtrips. One active group shape / three disabled component shapes.
- Four side/end rays hit the group's exact planes and **only its body**. Ray at Y 1.2 is
  clear. Four capsule bypasses pass and four overlaps block, r=0.35 / h=1.8. Six additional
  side-gap capsule queries pass with the documented shelter transform.
- Pinned gdstyle formatting/lint and owned-script compilation pass. Full production suite:
  **17 Python tests; 165 GUT tests / 6,918 assertions; negative-test detection passed**.
  No known-failure exclusions were needed. Explicit mise paths and Python UTF-8 mode avoid
  the earlier sibling's Windows discovery/encoding issue.
- Import retains the existing MCP plugin's 4.8-versus-4.7 support warning. No asset errors,
  live-session access or plugin/project configuration changes. Initial four line-length
  warnings were corrected; rejected pitches remain classified as failed trials, not passes.

## Remaining acceptance

Independent technical/art review is pending. World integration owns sparse parking-row
placement, full actor/car bypass widths and actual fixed-camera retail recognition,
including under-roof occlusion. ActorMotion movement, real vehicle contact/turning,
weapon queries, authoritative/predicted multiplayer, packaged builds, repeated-placement
LOD/shadow cost and sustained Deck performance are **not tested** by this delivery.
No district placement, register-ready status or broader gameplay acceptance is claimed.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
