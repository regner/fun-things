# d02_domestic_details.03 — Mailbox

**Source/export, linked prefab and bounded headless checks delivered; independent
review and placement acceptance pending.** Production commissioned by Regner under
[the commission](commission.md) and the current per-asset production brief. Original
Blender construction by the commissioned worker on `lane/a-d02`; supervisor/reviewer
owns acceptance and world integration. No live Blender/Godot session was touched.

Family: [Domestic boundary and porch details](../d02_domestic_details.md).
Direction: [The Crescents](../../concepts/world-v1/stage-03-district-identities/README.md),
[selected revision 02](../../concepts/districts-v1/02-the-crescents-v02.png), and
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md).
The production commission supersedes historical concept-only restrictions.

## Design and dimensions

A compact freestanding domestic mailbox: rolled arched sage-metal housing on a
square slate post and small ground shoe. A dark perimeter reveal separates the
closed front leaf; an ivory rain lip over the letter slot and a small pull tab
provide restrained close-view detail. No loud flag, real brand, copy, dense texture,
interior, working door, interaction, animation or destruction state is added.
Original Blender geometry only; no downloads, purchased mesh or image-to-mesh.

The [straight wall](d02_domestic_details_01.md) and
[return](d02_domestic_details_02.md) establish the family palette. Their exact ivory
`#D4CEBB` and slate `#58636B` materials are retained in the mailbox accents/support;
quiet sage enamel `#526B65` and dark slot/seam `#293B40` extend the painted-metal
language without repeating the rendered wall material on metal hardware.

Dimensions are **provisional authoring proposals**, not measurements from concepts
or approved plot placement. Tolerance is 0.001 m; normals within 0.0001 of unit length.

| Contract | Metres, Godot local axes |
| --- | --- |
| Whole visual X / Y / Z | 0.480 / 1.350 / 0.420 |
| Whole AABB | (-0.240, 0, -0.210) to (0.240, 1.350, 0.210) |
| Pivot | Ground centre of foot and whole AABB at (0,0,0) |
| Front | Local -Z; Blender +Y before export |
| Ground shoe | 0.240 × 0.060 × 0.240; Y=0 to 0.060 |
| Visible post | 0.120 square; Y=0.060 to 0.870, embedded into housing |
| Housing | X=±0.240; Y=0.850 base, 1.110 shoulder, 1.350 crown |
| Housing depth | Rear Z=0.210 to front shell Z=-0.170 |
| Front hardware limit | Z=-0.210; contained within whole envelope |
| Letter slot | 0.292 wide × 0.027 high, centred at Y=1.120 |

The curved roof uses a 16-segment semicircular profile with softened manufactured
edges. Nine closed components are joined into one editable mesh. Blender +Z maps
to Godot +Y and Blender +Y to Godot -Z. All export members have identity transforms,
metre units and ground-centred origins. A hidden-render, non-export 1 m reference
cube is retained. No sockets, rigs, clips or state variants are required.

Place beside a plot entrance, **not across a pedestrian shortcut**. The mailbox is
freestanding rather than wall-mounted, so its ground pivot and collider do not
depend on a selected home or wall height. Do not perch the full prefab on the wall
cap or stretch it to fit a site. Final setback and clear passage width are placement
review, not supplied by this isolated asset.

## Source, export and materials

- Source: `art/source/models/environment/d02_domestic_details_03/d02_domestic_details_03.blend`.
- Collection: `export_d02_domestic_details_03`.
- Root / mesh: `D02DomesticDetails03` / `D02DomesticDetails03_Mesh`.
- GLB: `art/models/environment/d02_domestic_details_03/d02_domestic_details_03.glb`
  with its engine-normalized `.import`.
- Prefab: `scenes/prefabs/environment/d02_domestic_details_03.tscn`.
- Author/export/validator/render/receipt tools and engine check:
  `tools/asset_production/d02_domestic_details_03/`.

One mesh, four opaque Principled surfaces in actual exported order:

| Slot | Material | Roughness | Metallic |
| --- | --- | --- | --- |
| 0 | `crescents_sage_enamel` | 0.42 | 0.25 |
| 1 | `crescents_slate_plinth` | 0.75 | 0 |
| 2 | `mailbox_recess` | 0.70 | 0 |
| 3 | `crescents_ivory_trim` | 0.55 | 0 |

Original flat colors converted from sRGB to linear; backface culling enabled.
No textures, embedded images, external material remaps, custom shaders or morphs.
Applied bevel/weighted-normal modifiers retain editable source geometry; glTF
triangulates at export. Blender **5.2.2 LTS**, build `d13f752e3b9c`, exporter
**5.2.40**; export uses the shared `tools/assets/blender/export_settings.json`
with explicit collection and animation/skins disabled. Studio content is never
saved/exported. Godot **4.8.dev7.official.c971f93e7** imports scale 1 with default
automatic LODs and shadow meshes. No repeat-placement/device budget is claimed.

## Prefab and collision

`Visuals/Model` is an identity-transform linked imported instance. Separate
`Collision/Body` is one static body, world layer 1 / mask 0, with three simple boxes:

| Shape | Size X / Y / Z | Centre |
| --- | --- | --- |
| Foot | 0.240 / 0.060 / 0.240 | (0, 0.030, 0) |
| Post | 0.120 / 0.810 / 0.120 | (0, 0.455, 0) |
| Mailbox | 0.480 / 0.500 / 0.420 | (0, 1.100, 0) |

The post collider overlaps the foot/head by **0.010 m** to prevent numerical seam
misses; it does not widen the visible post. The head box deliberately fills the
rounded roof corners (up to 0.240 m above the outer shoulder) and thin front reveals.
This conventional conservative box avoids a detailed render-mesh collider. The open
space beneath the head and beside the narrow post remains empty; no full-height
bounding box or whole-plot blocker is added. The shape is not a walk surface and
adds no climbing, navigation, destruction, world IDs or gameplay code.

Live editor tools were prohibited and the windowed editor is unavailable. The
commissioned text fallback was loaded/packed/resaved with pinned headless Godot;
the second save was byte-stable. Prefab UID `uid://cdpvwkjmgorc4`, model UID
`uid://bx8xg8mpvasud`, imported ancestry and saved node identities resolve. No separate
open editor synchronization is claimed.

## Evidence and reproduction

[Hero](d02_domestic_details_03-evidence/hero.png),
[side](d02_domestic_details_03-evidence/side.png),
[front detail](d02_domestic_details_03-evidence/detail.png),
[gameplay overhead](d02_domestic_details_03-evidence/overhead_47m_42deg.png).
All four final compressed images were inspected. Close views show the arched box,
closed leaf/reveal, understated slot/pull and clean grounded post. The roof is only
approximately **10 pixels wide** at the reference overhead camera: it is quiet
plot dressing, not a readable interaction or wayfinding cue. Front details are not
visible in that view and are not used to communicate gameplay. Populated-city
contrast and obstacle recognition remain native camera/placement review.

These are isolated Blender Cycles CPU renders, 32 samples, AgX, 1280×720, PNG
compression 95 plus six-bit RGB compression; each is below 400 KB. Overhead uses
vertical-down perspective at 47 m / 42-degree vertical FOV, north at image top.
The standing 1280×720 evidence-size rule supersedes the older 1280×800 reference.
No image is an engine capture. An initial studio floor offset made the foot appear
to float; it was raised to 0.001 m below the model datum before final renders.

Run from repository root in Bash; scratch stays outside Git:

```sh
N=d02_domestic_details_03
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="C:/tmp/ft/assets/$N"
mkdir -p "$S" "docs/assets/production/$N-evidence"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8

timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/author.py"
timeout 600 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/render.py"
python "tools/asset_production/$N/record.py" --compress-renders
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  "art/source/models/environment/$N/$N.blend" \
  --python "tools/asset_production/$N/export.py" -- "$S/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/validate.py" -- "$S/reexport/$N.glb"

timeout 300 "$G" --headless --path . --import > "$S/import-initial.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "tools/asset_production/$N/check_prefab.gd" -- --normalize \
  > "$S/normalize-editor.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script "tools/asset_production/$N/check_prefab.gd" \
  > "$S/prefab-final.log" 2>&1
"$(mise which gdstyle)" fmt --check "tools/asset_production/$N/check_prefab.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$N/check_prefab.gd"
python "tools/asset_production/$N/record.py"
python "tools/asset_production/$N/record.py" --verify
```

Tools follow the accepted sibling patterns and reuse the shared export contract.
`production_checks.py` was not run, per owner decision 52.

## Validation results

[Final receipt](d02_domestic_details_03-evidence/validation.json),
[concise diagnostic log](d02_domestic_details_03-evidence/final.log),
[producer manifest](d02_domestic_details_03-evidence/manifest.json).

- **2,220 triangles, 1,128 Blender vertices, 1,248 GLB vertices; one mesh, four surfaces.**
- **Zero degenerate faces/triangles and zero non-manifold edges**; contiguous source
  winding, positive signed volume, outward binary triangle winding and unit normals.
- Source, binary GLB and imported Godot AABBs match the independent dimensions above
  within 0.001 m; ground is zero and export transforms are identity.
- Separate-process fresh reexport is byte-identical: **57,364 bytes**, SHA-256
  `3534f1614150700cb0744b51c9510bbee2cdf1ba97a683a4ad73ff000821733b`.
- Final pinned import exits 0 without ERROR/SCRIPT ERROR lines. Fresh runtime resolves
  all dependencies, opaque/back-culling surfaces, linked mesh ancestry and UIDs.
- Seven capsule overlap/clearance cases and six component rays pass, including both
  collider joins and clear under-head space. Front foot/post/head ray expectations
  are Z=-0.120 / -0.060 / -0.210 m respectively.
- Production `ActorMotion.step`, r=0.35 m / h=1.8 m capsule: front/rear/side stops and
  bypass at X=0.650 pass over 60 fixed ticks each in AUTHORITY and REPLAY modes with
  identical endpoints. Front/rear stop at Z=±0.561198; side at X=0.590495; bypass
  reaches Z=3.000000. Literal contact expectations allow 0.025 m solver separation.
- A 1.9×1.5×4.3 m car-sized test box blocks frontally and clears at X=3 m; this is
  an envelope sweep, **not** production car handling/turning evidence.
- Pinned format check and strict lint pass. Function-purpose comments and spacing
  were checked. Test bodies/floor are invisible validation-only probes.

The initial exact foot/post seam ray failed due to a floating-point butt join.
The post collider's 0.010 m overlap resolves it; the identical seam probe now passes.
Raw initial failure/retries remain scratch-only; the final log records the correction.
Blender reports its known future-6.0 `use_nodes` deprecation. Import reports the
existing MCP 4.8 compatibility warning. Editor normalization exits 0 and proves
byte stability but emits scan-aborted/RID/ObjectDB shutdown diagnostics, retained
verbatim in `final.log`. Fresh runtime has no ERROR/WARNING lines. No diagnostics
are suppressed and no owner's live process was accessed.

## Remaining acceptance

- Independent source/technical and art review at the committed candidate.
- World integrator: fit beside selected homes/walls, setbacks, clear foot-link
  mouths, short domestic plots and repeated placement; preserve shortcuts.
- Gameplay/camera owner: native 47 m/42-degree actor/combat visibility and obstacle
  recognition, actual car movement around placed mailboxes and walking alternatives.
- Network owner: separate-process transport/admission/prediction/lifecycle evidence
  if placed in a replicated world; local authority/replay is not network acceptance.
- Device/performance owner: native materials/LODs, repeat-placement profiling,
  packaged dependencies and sustained Deck LCD/OLED evidence.

Earlier sibling handoffs were checked; neither has a stale pending mailbox item,
so no sibling document or manifest edit is required. Shared queue/progress, world
scenes, project settings and historical receipts remain unchanged.
