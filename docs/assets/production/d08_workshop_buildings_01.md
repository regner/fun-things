# d08_workshop_buildings.01 — Small pitched repair shed

10 October 2026. **Source/export and bounded prefab checks delivered; independent review and
world/gameplay/device acceptance pending.** Production commissioned by Regner under the
[commission](commission.md) and per-record production brief. The commission supersedes the
concept-only status of [the workshop family brief](../d08_workshop_buildings.md), not its
Ironreach revision-02 visual requirements.

Producing owner: commissioned asset-production worker, original Blender construction,
technical integration and visual self-review. Accepting owners: independent asset reviewer
and supervising production lead (pending); downstream layout/gameplay/performance owners
retain their gates. No shared register, catalogue, progress, world scene or sibling changed.

## Design and dimensions

A compact single-gable repair shed, not a long dock warehouse: four short side bays, one
closed roller shutter, a small occupied service door and one high side window. Faded petrol
walls, pale structural bands, worn brick base, localized rust, subtly dented shutter folds
and broad mismatched corrugated roof patches implement revision 02. One restrained amber
cross-roof band identifies the working frontage from above. Cyan is omitted rather than
making every shed bright. No brands, downloaded art, generated-image geometry or external
textures were used. The selected Ironreach v02 concept was inspected as style reference;
no dimensions were measured from it.

These are **provisional authored dimensions**, permitted by the production brief; they are
not an approved district arrangement or final traffic-clearance allocation.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Closed structural footprint | X 10.00 × Z 12.00, centred on ground |
| Structural wall/collision datum | Y 4.00; gable infill meets roof above it |
| Basic pitched sheets | Eave upper face Y 4.10; central sheet ridge Y 5.80 |
| Ridge-cap / overall height | Y 5.88 |
| Roof overhang | 0.35 beyond each structural wall; non-walkable overhead decoration |
| Visual AABB minimum | (-5.35, 0, -6.35) |
| Visual AABB maximum | (5.35, 5.88, 6.35) |
| Visual dimensions X/Y/Z | 10.70 × 5.88 × 12.70 |
| Brick base | 0.72 high; three deliberately oversized 0.24m courses |
| Shutter face | 4.20 wide × approximately 3.00 high; centre X -1.50, facade Z -6 |
| Shutter surround | X -3.84…0.84; Y 0.02…3.43; projection up to 0.19 |
| Closed service door | 1.20 wide; centre X 3.30; top Y 2.39 |
| Applied detail | Grout 0.006; side pilasters 0.045; window 0.15; door pull 0.23 outward |
| Numeric tolerance | Envelope/ground ±0.001; source → GLB axis mapping ±0.00001 |

Root and joined mesh pivots are both (0,0,0), centred on the structural ground footprint.
Metres, applied transforms, unit scale, no corrective prefab transforms. Blender +Y is the
front and maps to Godot -Z; Blender +Z maps to Godot +Y. No interiors, usable roof,
opening doors, destruction, animation, dynamic bodies, real lights or interaction state.
The opaque amber panes/lens/band use a restrained material emission of 0.3; this does not
illuminate a yard or establish a lighting budget.

### Provisional family reuse / office interface

This is the first delivered member; there were no completed sibling outputs to reconcile.
The next shed/depot should reuse the visual vocabulary and these local component dimensions,
not stretch this entire prefab or produce weathering-only building variants:

- Straight side-wall bay: **3.00m long**, wall datum **4.00m**; pale upper band Y 3.65–3.90,
  brick base Y 0–0.72. Four bays compose this 12m depth.
- Roller door: **4.20m clear visual leaf width / 3.00m nominal height**, 0.24m jambs,
  0.32m header; closed decorative leaf, not a drive-through opening. Its twelve horizontal
  folds include two replacement courses and a shallow broad dent (maximum 0.055m).
- Roof construction: paired closed sheets with **0.16m vertical thickness**, 0.35m
  overhang; broad corrugations at 0.65m centres. The sawtooth/depot change silhouette rather
  than merely recolouring this pitch. Repair-sheet geometry stays attached to its roof.
- Available office connection: plain right rear wall, **X +5**, rear half **Z 0…6**.
  A single 3m bay can connect at **(5,0,4.5)**, covering **Z 3…6**. Side pilasters are at
  bay boundaries; trim protrudes at most 0.05m. The forward high window is outside this
  interface. The later office owns its dimensions and attachment wrapper; its joining roof
  should stay below the shed eave underside (~3.94m at outer edge), cover the trim seam,
  and not imply a passage through the closed wall. This is a documented plane, not a
  runtime socket or public opening API.

The two unequal shed assemblies plus office attachment requested by the family brief require
the later members. No substitute office, depot, sawtooth or duplicate landmark was invented
in this record. Family comparison/assembly remains pending those deliveries, not a missing
second variant of this small-shed record.

## Source, exports and materials

| Deliverable | Path / identity |
| --- | --- |
| Editable Blender source | `art/source/models/environment/d08_workshop_buildings_01/d08_workshop_buildings_01.blend` |
| Named export collection | `export_d08_workshop_buildings_01` |
| Root → mesh | `D08WorkshopBuildings01` → `D08WorkshopBuildings01_Mesh` |
| Explicit export | `art/models/environment/d08_workshop_buildings_01/d08_workshop_buildings_01.glb` |
| Import metadata | Adjacent `.glb.import`, model UID `uid://dldr2v0kyb1j8` |
| Saved linked wrapper | `scenes/prefabs/environment/d08_workshop_buildings_01.tscn`, UID `uid://b4a0j385hgex5` |
| Reproduction / checks | `tools/asset_production/d08_workshop_buildings_01/{author.py,export.py,validate.py,check_prefab.gd,record.py}` |

Eight opaque, back-culling Principled material surfaces, in exported order:

1. `ironreach_worn_brick` — muted brown base.
2. `ironreach_faded_petrol` — weathered wall paint, quiet mortar and one replacement panel.
3. `ironreach_pale_band` — structural bands, jambs, mullions and ridge cap.
4. `ironreach_local_rust` — sparse broad repairs, shutter wear and a roof patch.
5. `ironreach_dark_recess` — closed glazing, door/reveal and lamp casing.
6. `ironreach_roof_petrol` — main pitched sheets and shutter.
7. `ironreach_replacement_sheet` — galvanized repair panel and shutter replacement courses.
8. `ironreach_working_amber` — occupied door, integral task lens and front roof band.

Actual PBR values are retained in [validation.json](d08_workshop_buildings_01-evidence/validation.json).
No textures, embedded images, material overrides, external material resources or authored
UV artwork are needed. No rig, clips, sockets, extra variants or custom LODs. Default Godot
mesh LOD generation remains enabled; visual transitions and repeat-placement cost are not
accepted without profiling.

Blender **5.2.2 LTS**, build **d13f752e3b9c**; glTF exporter **5.2.40**. The export script
loads `tools/assets/blender/export_settings.json`, selects only the named collection and
explicitly disables animation/skins for this static model. Modifiers are applied in the
saved editable source. Studio plane, camera and lights are outside the collection. Static
manufactured parts are joined into one mesh with closed disconnected components, not a
boolean-unioned solid. Gameplay collision is independent.

## Evidence and reproduction

[Hero](d08_workshop_buildings_01-evidence/hero.png) ·
[Side](d08_workshop_buildings_01-evidence/side.png) ·
[Shutter detail](d08_workshop_buildings_01-evidence/shutter_detail.png) ·
[47m / 42° overhead](d08_workshop_buildings_01-evidence/overhead_47m_42deg.png).

All four are **isolated Blender renders**, 1280×720, Cycles CPU 32 samples, AgX,
soft studio lighting. The vertical-down perspective camera is at (0,0,47), north/+Y
at the top, **42° vertical FOV**. The 720px height follows the current lean-evidence
rule, superseding the older example's 800px output. PNG compression 95 in Blender;
`record.py` applies evidence-only 6-bit RGB quantization (overhead 7-bit) and lossless
PNG compression level 9. Final PNGs are 262–396KB each. No mesh or material is changed
by that compression.

Self-review inspected all four views. Compact roof, pale ridge, amber front strip and
unequal repair panels remain distinguishable overhead. The shut workshop bay and occupied
service door read from the oblique/detail views; facade detail is not claimed readable
from directly above. An initial overlapping base/wall face was removed, gable/eave contact
was sealed, and the ridge cap raised over the amber strip. A source ray protects the
visible brick material. There is no native Godot visual/playtest capture in this delivery.

Exact reproduction from repository root, using only isolated processes:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=tools/asset_production/d08_workshop_buildings_01
S=art/source/models/environment/d08_workshop_buildings_01/d08_workshop_buildings_01.blend
X=C:/tmp/ft/assets/d08_workshop_buildings_01
mkdir -p "$X"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background "$S" --threads 4 --python-exit-code 1 --python "$T/export.py" -- "$X/manual-reexport"
G="$(mise which godot)"
timeout 300 "$G" --headless --path . --import > "$X/import-final.log" 2>&1
timeout 180 "$G" --headless --editor --path . --script "res://$T/check_prefab.gd" -- --normalize > "$X/normalize.log" 2>&1
timeout 180 "$G" --headless --path . --script "res://$T/check_prefab.gd" > "$X/prefab-final.log" 2>&1
"$(mise which gdstyle)" fmt --check "$T/check_prefab.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd"
# The canonical runner requires a fresh, empty output directory.
timeout 1800 mise exec -- python tools/production_checks.py --output "$X/checks"
python "$T/record.py" --compress-renders
python "$T/record.py"
python "$T/record.py" --verify
```

`validate.py` itself opens the saved source, decodes raw GLB positions/normals/indices,
checks literal independent bounds and face-material rays, and makes a fresh scratch export
whose entire bytes must match production. The explicit manual-reexport command is an
optional equivalent entrypoint, not a separate claimed test run. Producer
[manifest.json](d08_workshop_buildings_01-evidence/manifest.json) hashes every delivered
payload except itself. Scratch/retry renders and raw logs remain outside the repository.
The [concise final log](d08_workshop_buildings_01-evidence/final.log) retains final runtime
results, check summary and unsuppressed editor diagnostics.

## Validation and prefab collision

**14,932 triangles; 7,918 source vertices; 9,678 exported vertices (normal splits);
one mesh; eight surfaces.** Zero non-manifold source edges, zero degenerate source faces
and zero degenerate exported triangles. Source and export normals are unit length;
triangle winding agrees with exported normals. Source/GLB bounds and ground datum meet
the stated tolerances. The 328,616-byte GLB re-exports byte-identically. Export contains
exactly two nodes, no images, cameras, lights, skins or animations.

The text-authored wrapper was loaded/packed/resaved by the pinned headless editor; the
subsequent reload/save was byte-identical, preserving scene/node UIDs. `Visuals/Model`
is an identity-transform imported instance. One direct-child `BoxShape3D` under
`Collision/Body` is **10 × 4 × 12m**, centred at **(0,2,0)**, static-world layer 1 /
mask 0. No copied render mesh or runtime composition. It blocks the full closed shed,
including its non-enterable shutter/door. Small applied trim is deliberately excluded
from collision; roof and gables above the 4m solid envelope are visual-only and not
walkable. No step, ramp or accessible deck is authored.

Pinned Godot **4.8.dev7.official.c971f93e7** checks passed:

- Load and dependency identities, linked mesh ancestry, identity transforms, measured
  AABB, all eight opaque/back-culling materials and exact collider dimensions/layers.
- Nine radius-0.35m / height-1.8m capsule queries: closed volume and both entrances solid,
  opposite corners solid, four outside routes clear. Front ray hits exactly Z -6.
- Production `ActorMotion.step`, 60 ticks per case in **AUTHORITY and REPLAY** modes:
  shutter and service-door approaches both stop at Z **-6.350261m**; east wall at X
  **5.350255m**; east bypass reaches Z **-3.999996m**. All paired mode endpoints are
  exactly equal. These are bounded static-physics tests, not network transport proof.
- A **1.9 × 1.5 × 4.3m car-sized test box** is stopped by the front and clears the east
  bypass. This is a sweep query, not production driving, turn-radius or car physics proof.
- Pinned gdstyle 0.3.0 formatting/lint passed. Canonical production checks passed every
  layer: explicit owned-script compilation, **17 Python tests**, **165 GUT tests /
  6,918 assertions**, plus expected-negative-test detection. **No failures ignored.**

The first import and final post-export import exited 0. Isolated headless-editor
normalization also exited 0 with a stable save/reload, but emitted existing toolkit
4.8 compatibility, aborted scan and editor-shutdown RID/ObjectDB leak diagnostics;
these are retained, not called a clean editor exit. Fresh non-editor prefab/motion
runtime exited 0 **without ERROR/WARNING**. No windowed editor or owner's live
Blender/Godot MCP session was used. Headless import does not synchronize any separate
open scene, and no such synchronization is claimed.

## Remaining acceptance

- Independent technical/art review of this exact source/export/prefab candidate.
- Later family members **d08_workshop_buildings.02 (sawtooth), .03 (depot), .04 (office)**:
  compare two unequal shed assemblies and one attached office using their delivered
  prefabs. Retain this datum/finish contract or document coordinated refinement; do not
  duplicate a landmark model. These assets were unproduced at this handoff.
- World integration: selected district fit, placement, two yard exits, foot bypass,
  car turning/chain spacing and building-to-route clearances. Nothing is placed here.
- Actual native 47m/42° camera with actors, combat/aim and populated-city occlusion;
  authoritative/predicted behavior over real separate network processes.
- Packaged-platform and Deck LCD/OLED review, sustained frame pacing, repeated-building
  draw/LOD/shadow cost, and any future real lighting. No device budget or full game-ready
  production acceptance is claimed by successful import or isolated evidence.
