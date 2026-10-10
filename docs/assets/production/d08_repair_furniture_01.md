# d08_repair_furniture.01 — Tool cabinet

10 October 2026. **Source/export and bounded prefab checks delivered; independent review,
world/gameplay and target-device acceptance pending.** Production commissioned by Regner under
[the commission](commission.md) and the current per-record production brief. This supersedes
concept-only restrictions in [the family brief](../d08_repair_furniture.md), while retaining
its Ironreach revision-02 appearance and static closed-dressing constraints.

Producing owner: commissioned asset-production worker (original Blender construction,
technical integration, visual self-review). Accepting owners: independent asset reviewer
and supervising production lead; placement/gameplay/device owners retain downstream gates.
This is the first repair-furniture delivery in this lane. No prior sibling handoff required
reconciliation. No shared registry, brief, progress, catalogue or world scene changed.

## Design and dimensions

A stationary workshop cabinet: five broad closed tool drawers above a two-door lower
cupboard, long metal drawer grips, short vertical cupboard pulls, recessed ground plinth
and a dark rubber top pad. One amber replacement drawer and narrow warm top-front rim
provide restrained accents. Sparse irregular rust and rubbed-metal patches sit at lower
door/side edges, a drawer edge and a top corner. Broad clean surfaces remain dominant:
usable-looking worn painted metal, not rubble, grime noise or scattered tools.

The selected [Ironreach v02 concept](../../concepts/districts-v1/08-ironreach-v02.png),
[approved district identity](../../concepts/world-v1/stage-03-district-identities/README.md)
and [working-street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) were
inspected for context. Dimensions are **provisional authored choices**, permitted by the
standing production rules, not measured from concept images or approved yard placements.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Overall visual dimensions X/Y/Z | **1.44 × 1.50 × 0.80** |
| Visual AABB minimum / maximum | **(-0.72, 0, -0.40) / (0.72, 1.50, 0.40)** |
| Main closed body | 1.40 wide × 1.32 high × 0.65 deep; Y 0.12–1.44 |
| Ground-contact plinth | 1.32 × 0.13 × 0.60; depth centre Z +0.015 |
| Cap | 1.44 × 0.06 × 0.80; top Y 1.48 |
| Rubber pad | 1.27 × 0.024 × 0.62; top Y 1.50 |
| Drawer fronts | 1.254 wide; four 0.112 high and one 0.13 high |
| Lower cupboard leaves | Two 0.616 wide × 0.55 high; closed centre seam |
| Long grips | 1.012 long; maximum front projection Z -0.378 |
| Abrasion geometry | Seven sparse closed 0.0008m-thick paint-loss prisms |
| Pivot | (0,0,0), centred on overall ground footprint; source root and mesh at identity |
| Tolerance | Visual/ground bounds ±0.001m; unit-normal length ±0.0001 |
| Collision | One 1.44 × 1.50 × 0.80m box, centre (0,0.75,0) |

Metre units, applied rotation/scale, no corrective prefab scale or rotation. Blender +Y
faces the drawers and maps to Godot -Z; Blender +Z maps to Godot +Y. The plinth is slightly
rearward under the centred cap; minimum height is zero. No wheels, loose tools, moving
parts, interior, opening doors, repair interaction, animation, destruction or physics clutter.
No invented sign/copy, real brand, emission or real light.

### Family finish language

This establishes the repair-furniture finish using the existing
[d08 workshop building](d08_workshop_buildings_01.md) swatches: faded petrol body, darker
petrol frame, quiet recess, muted bare metal, localized warm rust and selective amber.
The six stable names and sRGB swatches below are available to the other family designs;
metallic/roughness values are adapted here for painted furniture rather than masonry.
Repeated cabinets should instance this same prefab. Distinct family silhouettes are not
produced by stretching it. No shared material owner or external dependency is introduced.

## Source, exports and materials

| Deliverable | Path / identity |
| --- | --- |
| Editable original source | `art/source/models/environment/d08_repair_furniture_01/d08_repair_furniture_01.blend` |
| Export collection | `export_d08_repair_furniture_01` |
| Root → mesh | `D08RepairFurniture01` → `D08RepairFurniture01_Mesh` |
| Explicit export | `art/models/environment/d08_repair_furniture_01/d08_repair_furniture_01.glb` |
| Model import UID | `uid://ctbf6l0cd3k1e`; adjacent `.glb.import` retained |
| Linked wrapper | `scenes/prefabs/environment/d08_repair_furniture_01.tscn` |
| Wrapper UID | `uid://cmwhakquxvu81`; engine-generated node identities retained |
| Reproduction and checks | `tools/asset_production/d08_repair_furniture_01/` |

Original Blender construction only; no downloads, purchased art, generated-image geometry,
external fonts/textures or embedded images. `author.py` is the parametric source recipe;
`export.py` reads the shared `tools/assets/blender/export_settings.json` contract and
exports only the named collection, with skins and animations disabled. Pinned **Blender
5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. The static bevel/normal
modifiers are baked before saving, and glTF triangulates the editable faces. Independent
closed components share a joined mesh; they are intentionally intersecting manufactured
parts, not a boolean-unioned volume. Gameplay collision never derives from those parts.

Six opaque back-culling Principled surfaces in exported order:

| Surface | sRGB swatch | Metallic / roughness | Use |
| --- | --- | --- | --- |
| `ironreach_roof_petrol` | `#294E58` | 0.30 / 0.60 | Frame, plinth, hinge plates |
| `ironreach_faded_petrol` | `#627D7B` | 0.25 / 0.64 | Painted panels, cap, drawers |
| `ironreach_dark_recess` | `#20363F` | 0.05 / 0.78 | Top pad, cap seam, pull backings |
| `ironreach_working_amber` | `#F5BA55` | 0.10 / 0.65 | Replacement drawer and thin front rim |
| `ironreach_replacement_sheet` | `#7D9190` | 0.55 / 0.52 | Grips and rubbed-metal patches |
| `ironreach_local_rust` | `#A7653E` | 0 / 0.90 | Localized lower-edge wear |

The author converts sRGB to linear PBR values; actual exported values are in
[validation.json](d08_repair_furniture_01-evidence/validation.json). No separate textures,
`.tres` materials, overrides, UV artwork, rig, clips, sockets or explicit LOD variants are
needed. Default Godot automatic LOD generation is retained; transitions and repeated-prop
cost remain unmeasured, not accepted by the small standalone test.

## Evidence and reproduction

[Hero](d08_repair_furniture_01-evidence/hero.png) ·
[Side](d08_repair_furniture_01-evidence/side.png) ·
[Drawer/top detail](d08_repair_furniture_01-evidence/detail.png) ·
[47m / 42° overhead](d08_repair_furniture_01-evidence/overhead_47m_42deg.png).

All four are **isolated Blender renders**, 1280×720, Cycles CPU 32 samples, AgX with
soft studio fill. `render.py` loads the saved source and creates a temporary studio outside
the export collection; it does not save studio geometry into the asset. The overhead is
vertical-down perspective at (0,0,47)m, north/+Y up, **42° vertical FOV**. The current
720px lean-evidence rule supersedes the older example's 800px output. PNG compression 95
in Blender, then evidence-only RGB channel quantization (6-bit close views, 7-bit overhead)
and PNG compression 9 in `record.py`: 235–378KB per image. No runtime art is quantized.

All views were inspected before and after compression. The long grip rhythm, replacement
drawer, closed lower doors and limited abrasion are legible in close views. Overhead the
cabinet occupies a deliberately small footprint: a dark rectangle with a warm front edge,
not a bright landmark. Individual drawers and rust are not claimed readable from 47m.
No readability-driven enlargement or invented billboard was added. Native engine visuals,
actors, blue-hour world lighting and populated-camera occlusion still require placement review.

Exact commands from the repository root (isolated processes, never live MCP sessions):

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=tools/asset_production/d08_repair_furniture_01
S=art/source/models/environment/d08_repair_furniture_01/d08_repair_furniture_01.blend
X=C:/tmp/ft/assets/d08_repair_furniture_01
mkdir -p "$X"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
# Rebuild source and production GLB; render studio is not part of the saved source.
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup "$S" --threads 4 --python-exit-code 1 --python "$T/export.py" -- "$X/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$X/reexport/d08_repair_furniture_01.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
python "$T/record.py" --compress-renders
G="$(mise which godot)"
timeout 300 "$G" --headless --path . --import > "$X/import-final.log" 2>&1
timeout 180 "$G" --headless --editor --path . --script "res://$T/check_prefab.gd" -- --normalize > "$X/normalize-editor.log" 2>&1
timeout 180 "$G" --headless --path . --script "res://$T/check_prefab.gd" > "$X/prefab-final.log" 2>&1
{ "$(mise which gdstyle)" fmt --check "$T/check_prefab.gd" && "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd"; } > "$X/style-final.log" 2>&1
python "$T/record.py"
python "$T/record.py" --verify
```

Python/Pillow is used only for evidence encoding and manifest generation. `validate.py`
opens the committed source, reads actual GLB binary positions/normals/triangle indices,
asserts independent literal bounds/materials, and compares the entire fresh-process export
against production. Re-export comparison is required: pass the fresh GLB path after `--`.
`record.py` writes a manifest of every produced payload except itself, after final import,
checks and handoff updates. Scratch/retry logs remain under the displayed `C:/tmp` path.
The concise [final log](d08_repair_furniture_01-evidence/final.log) retains final test
results and known diagnostics. No `tools/production_checks.py` run, per owner decision 52.

## Validation and prefab collision

**6,868 triangles; 3,520 source vertices; 4,397 exported vertices (normal/UV splits);
one mesh; six surfaces.** Zero degenerate source faces, zero non-manifold source edges,
zero degenerate exported triangles. Source and exported normals have unit length;
consistent source winding and exported triangle/normal agreement pass. Source and GLB
literal bounds and zero ground datum pass. Exactly two export nodes, identity transforms,
no images, textures, cameras, skins or animations.

The final **187,944-byte** GLB re-exports **byte-identically**. SHA-256 from the final
validation receipt:
`65526b803f39c01646f673f869eaafefa92c2381925dfb2cf3871d72842779a1`.
The same byte count and hash are verified by the producer manifest.

`Visuals/Model` is an identity-transform linked imported scene. No embedded replacement
mesh or runtime-authored visual hierarchy. `Collision/Body/CabinetSolid` is one direct
`CollisionShape3D` child of a `StaticBody3D`: box **1.44 × 1.50 × 0.80**, centre
**(0,0.75,0)**, static-world layer **1**, mask **0**. The envelope includes the cap/grips
and abstracts recessed sides/plinth (up to approximately 0.115m of recess at the front
plinth); it prevents decorative snag points rather than reproducing tiny furniture gaps.
No route, gate, navigation, world placement or gameplay interaction was added.

Pinned **Godot 4.8.dev7.official.c971f93e7** bounded checks passed:

- Imported ancestry, identity transforms, resource-backed mesh, measured AABB, six opaque
  back-culling materials, exact one-box collision, wrapper/model UID registration and paths.
- Headless editor load/pack/save/reload/save normalizes the new scene. Second save is
  byte-identical, retaining scene/dependency UIDs and node identities.
- Eight production-size capsule queries (radius 0.35m, height 1.8m): closed body and
  opposite corners blocked, four perimeter routes clear, above-cabinet region clear.
- Aim ray strikes the front at Z **-0.399999976m**.
- Production `ActorMotion.step`: 60 ticks each, front/rear/east contact and east bypass,
  in both **AUTHORITY and REPLAY**. Paired endpoints are exactly equal. Front/rear stop
  at Z **±0.750081m**; east stop X **1.083334m**; bypass reaches Z **2.999999762m**.
  Contact tolerance is 0.025m around independent box/capsule expectations.
- A 1.9 × 1.5 × 4.3m car-sized box sweep hits the front and clears an east bypass at
  X 1.9m. This is not production car handling, turning or network transport evidence.
- Pinned gdstyle formatting and lint pass with zero issues. Owned Python scripts parse.

The initial runtime-only scene normalization did not assign a prefab UID; the check
correctly rejected it. Headless **editor** normalization fixed this (now enforced by the
check). Final imports exited 0 with no ERROR/SCRIPT ERROR lines; the existing toolkit
compatibility warning remains. Editor normalization exited 0 and passed stable-save
assertions, but emitted known aborted-scan and shutdown RID/ObjectDB leak diagnostics;
these are retained, not called a clean editor shutdown. The final fresh non-editor runtime
exited 0 with no ERROR/WARNING lines. Live owner editors were not used or synchronized.

## Remaining acceptance

- Independent technical/art review of this exact source/export/prefab commit.
- World placement against the selected district: group at workshop/fence edges, preserve
  the two yard exits, pedestrian bypass, turning/chain spacing and open centre. The
  freestanding collider must not become an unintended route barrier.
- Native 47m/42° camera/readability with actors, final lighting, combat/aim and repeated
  props; actual authoritative/predicted behavior across separate network processes.
- Production vehicle movement, packaged-platform/Deck LCD and OLED review, sustained
  frame pacing, LOD transitions and repeated-prop draw/shadow cost. These remain pending;
  isolated renders and successful imports do not claim full production acceptance.
