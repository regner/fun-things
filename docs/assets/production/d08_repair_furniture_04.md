# d08_repair_furniture.04 — Compact workbench

10 October 2026. **Source/export and bounded prefab checks delivered; independent review,
world/gameplay and target-device acceptance pending.** Commissioned by Regner under
[the commission](commission.md) and the current per-record production brief. This supersedes
the concept-only restriction in [the family brief](../d08_repair_furniture.md), preserving
Ironreach revision-02 appearance and static closed-dressing requirements.

Producing owner: commissioned asset-production worker (original Blender construction,
technical integration, visual self-review). Accepting owners: independent asset reviewer
and supervising production lead; placement/gameplay/device owners retain downstream gates.
The preceding [tool cabinet](d08_repair_furniture_01.md), [tyre rack](d08_repair_furniture_02.md)
and [parts trolley](d08_repair_furniture_03.md) were read and visually inspected. None of their
current handoffs lists this workbench as pending. No sibling, registry, shared brief,
progress, catalogue, gameplay code or world scene changed.

## Design and dimensions

A compact stationary steel workbench with a broad clear worktop, low rear stop, four fixed
feet, two closed drawers on the left and a lower shelf with one integral covered parts bin.
The open right knee bay distinguishes it from the cabinet; fixed legs and the clear work
surface distinguish it from the trolley. One amber replacement drawer, sparse edge abrasion,
two small rust patches and one faint old-paint remnant on the worktop continue the family
finish. No loose tools, rubble, dense grunge, brand, signage or invented repair mechanic.

The selected [Ironreach v02 concept](../../concepts/districts-v1/08-ironreach-v02.png),
[approved district identity](../../concepts/world-v1/stage-03-district-identities/README.md)
and [working-street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) informed
the design. Dimensions are **provisional authored choices**, allowed by the standing
production rules, not measurements from generated concepts or approved world placements.
Group against workshop/fence edges; preserve the open yard centre, two exits and foot bypass.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Overall visual dimensions X/Y/Z | **1.80 × 1.06 × 0.80** |
| Visual AABB minimum / maximum | **(-0.90, 0, -0.40) / (0.90, 1.06, 0.40)** |
| Thick steel worktop | 1.80 wide × 0.08 high × 0.80 deep; working surface Y 0.94 |
| Rear stop | 1.80 wide × 0.14 high × 0.03 deep; centre (0,0.99,+0.385) |
| Four fixed feet | Each 0.16 × 0.04 × 0.16; centres X ±0.76, Y 0.02, Z ±0.27 |
| Four legs | 0.08 square; Y 0.04–0.88, same X/Z centres as feet |
| Lower shelf | 1.50 wide × 0.04 high × 0.52 deep; top Y 0.23 |
| Closed drawer housing | 0.74 × 0.35 × 0.61; centre (-0.34,0.685,+0.015) |
| Drawer faces | Two 0.676 wide × 0.128 high; centres Y 0.5975 / 0.7575 |
| Drawer grips | 0.51 long; maximum front projection Z -0.375 |
| Lower covered bin body | 0.48 × 0.20 × 0.40; centre (+0.37,0.33,+0.025) |
| Wear geometry | Four sparse closed 0.0008m-thick prisms; no noisy texture field |
| Pivot | (0,0,0), centred ground footprint; root and joined mesh at identity |
| Tolerances | Envelope and ground ±0.001m; normal length ±0.0001 |
| Collision | One **1.80 × 1.06 × 0.80** box at **(0,0.53,0)** |

Metre units and applied transforms. Blender +Y faces the drawers and maps to Godot -Z;
Blender +Z maps to Godot +Y. No corrective prefab rotation or scale. Shelf/apron joints
intersect inside legs without coincident external faces; the first studio pass exposed
coplanar dark bands which were removed before final export and evidence. No moving drawers,
opening bin, casters, vice interaction, rig, clips, sockets, interior, destruction or physics
clutter. The worktop is static dressing, not a newly authored walkable gameplay surface.

## Source, exports and materials

| Deliverable | Path / identity |
| --- | --- |
| Editable original source | `art/source/models/environment/d08_repair_furniture_04/d08_repair_furniture_04.blend` |
| Export collection | `export_d08_repair_furniture_04` |
| Root → mesh | `D08RepairFurniture04` → `D08RepairFurniture04_Mesh` |
| Explicit export | `art/models/environment/d08_repair_furniture_04/d08_repair_furniture_04.glb` |
| Model import UID | `uid://doa0hqy43l67v`; adjacent `.glb.import` retained |
| Linked wrapper | `scenes/prefabs/environment/d08_repair_furniture_04.tscn` |
| Wrapper UID | `uid://3gdhmk6n6rt`; engine-generated node identities retained |
| Reproduction/check tools | `tools/asset_production/d08_repair_furniture_04/` |

Original Blender construction only: no downloads, purchased geometry, external fonts or
textures, image-to-mesh or runtime-authored render geometry. `author.py` retains the
parametric recipe. `export.py` uses shared `tools/assets/blender/export_settings.json`,
filtering the named collection and disabling skins/animations. **Blender 5.2.2 LTS**, build
**d13f752e3b9c**, glTF exporter **5.2.40**. Bevel/normal modifiers are baked before saving;
glTF triangulates editable faces. Independent closed manufactured components intersect at
joints and share one joined mesh, not a boolean-unioned solid. Collision is separate.

Six opaque back-culled Principled surfaces, in exported order. Swatches and PBR settings
match the cabinet's common worn-metal palette; there is no sibling runtime dependency.

| Surface | sRGB swatch | Metallic / roughness | Use |
| --- | --- | --- | --- |
| `ironreach_roof_petrol` | `#294E58` | 0.30 / 0.60 | Feet, legs, stiffeners, drawer housing, bin |
| `ironreach_faded_petrol` | `#627D7B` | 0.25 / 0.64 | Aprons, shelf, rear stop, lower drawer, bin lid, paint remnant |
| `ironreach_replacement_sheet` | `#7D9190` | 0.55 / 0.52 | Worktop, grips and rubbed drawer edge |
| `ironreach_dark_recess` | `#20363F` | 0.05 / 0.78 | Drawer seams |
| `ironreach_working_amber` | `#F5BA55` | 0.10 / 0.65 | Upper replacement drawer |
| `ironreach_local_rust` | `#A7653E` | 0 / 0.90 | Localized leg and shelf-edge wear |

sRGB is converted to linear PBR values by the author, recorded in validation.json. No
textures, embedded images, external `.tres` resources, emission or lights. No private
shared-material abstraction. Repeated placements instance the same prefab. Default Godot
automatic LOD generation is retained; no explicit LOD variants or accepted repeat-placement
performance budget are claimed.

## Evidence and reproduction

[Hero](d08_repair_furniture_04-evidence/hero.png) ·
[Side](d08_repair_furniture_04-evidence/side.png) ·
[Drawer/worktop detail](d08_repair_furniture_04-evidence/detail.png) ·
[47m / 42° overhead](d08_repair_furniture_04-evidence/overhead_47m_42deg.png).

Four **isolated Blender renders**, 1280×720, Cycles CPU 32 samples, AgX, soft studio fill.
The temporary studio is never saved into the source or export collection. The overhead
is vertical-down perspective at (0,0,47)m, +Y/north up, **42° vertical FOV**. Standing
720px lean-evidence rules supersede the older example's 800px height. Blender PNG compression
95, then evidence-only RGB quantization (6 significant bits; overhead 7), PNG compression 9:
213–379KB per image. Runtime art is not quantized.

All four final compressed views were inspected. The broad clear worktop, low rear stop,
two drawers, shelf/bin, fixed feet and restrained wear read in close views. The side camera
was widened after the initial framing cropped the feet/stop. At 47m the pale worktop is a
small quiet rectangle with a thin rear edge; drawers, feet, bin and abrasion are not claimed
readable. No scale inflation or billboard was added. Native engine/world lighting, actors
and populated-camera occlusion remain placement review, not isolated studio acceptance.

Exact commands from repository root, isolated processes only, never live owner MCP sessions:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=tools/asset_production/d08_repair_furniture_04
S=art/source/models/environment/d08_repair_furniture_04/d08_repair_furniture_04.blend
X=C:/tmp/ft/assets/d08_repair_furniture_04
mkdir -p "$X"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup "$S" --threads 4 --python-exit-code 1 --python "$T/export.py" -- "$X/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$X/reexport/d08_repair_furniture_04.glb"
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

Python/Pillow serves only evidence encoding/manifests. The validator opens the saved source,
audits binary GLB positions/normals/indices, asserts independent literal bounds, checks four
fixed-foot solid dimensions/centres and the broad worktop solid, and requires a fresh-process
export argument for byte comparison. Per-asset scripts follow sibling conventions and reuse
the shared export settings. `record.py` incorporates bounded engine results and hashes every
produced payload except its own manifest, after final import and handoff edits. Scratch,
intermediate exports and raw logs stay under the displayed `C:/tmp` path; only one concise
[final log](d08_repair_furniture_04-evidence/final.log) is retained. No
`tools/production_checks.py` run, per owner decision 52.

## Validation and prefab collision

**5,900 triangles; 3,020 source vertices; 3,728 exported vertices (normal/UV splits);
one mesh; six surfaces.** Zero degenerate source faces, zero non-manifold edges and zero
degenerate exported triangles. Unit source corner/exported normals and consistent winding
pass. Four independent foot solids match the expected 0.16 × 0.04 × 0.16m Godot dimensions
and centres; the worktop solid matches 1.80 × 0.08 × 0.80m. Source/GLB bounds and ground
datum pass. Exactly two exported nodes at identity; no cameras, skins, clips or images.

Final **160,784-byte** GLB re-exports **byte-identically**. SHA-256 copied from the final
validation receipt:
`5879be2c84e8c459889ded260188d3369fc3fcabbf2c6d379bfc672cbe7bbf38`.
The producer manifest independently verifies the same byte count and hash.

`Visuals/Model` is an identity-transform linked imported scene, no embedded replacement
mesh or runtime-generated visual hierarchy. `Collision/Body/WorkbenchSolid` is a direct
`CollisionShape3D` child of one `StaticBody3D`, box **1.80 × 1.06 × 0.80m**, centre
**(0,0.53,0)**, static-world layer **1**, mask **0**. The whole-prop envelope deliberately
fills shelf/knee gaps and underclearance rather than adding decorative snag colliders.
The shelf is only 0.19m above ground; the 0.63m gap between shelf and tabletop underside
cannot admit the 1.8m actor. The collider covers the top's 0.12m rear-stop rise across
its footprint, and extends up to 0.10m beyond the front/rear leg faces under the worktop.
This is nontraversable furniture, not a yard boundary or walkable deck. No navigation,
world placement or gameplay interaction was added.

Pinned **Godot 4.8.dev7.official.c971f93e7** bounded checks passed:

- Linked imported ancestry, identity transform, resource-backed mesh, measured AABB,
  six opaque back-culled materials, exact one-box collider and registered model/wrapper UIDs.
- Headless editor load/pack/save/reload/save assigns scene/node identities. The second
  save is byte-identical, preserving normalized UIDs and node identities.
- Eight production-size capsule queries (radius 0.35m, height 1.8m): body and opposite
  corners blocked; four perimeter routes and above-workbench region clear.
- Front ray at worktop height hits Z **-0.399999976m**; shape query, not combat acceptance.
- Production `ActorMotion.step`, 60 ticks per case, front/rear/east contact and east bypass
  in both **AUTHORITY and REPLAY**. Paired endpoints are exactly equal. Front/rear stop at
  Z **±0.750081122m**, east at X **1.250000358m**; bypass X **1.35m** reaches
  Z **2.999999762m**. Solver tolerance 0.025m against independent literal expectations.
- A 1.9 × 1.5 × 4.3m car-sized box sweep is blocked from the front and clear at east bypass
  X **1.95m**. This is not production car handling, turning or network transport evidence.
- Owned GDScript passes pinned gdstyle format/lint with zero issues; owned Python parses.

Final Blender author/export/validator/render calls exit 0; material API deprecation notices
only. The separate initial version query printed a tiny shutdown memory warning; it is not
source validation. Final pinned import exits 0 with no ERROR/SCRIPT ERROR lines (existing
toolkit compatibility warning remains). Headless editor normalization exits 0 with stable-save
assertions but known aborted-scan and shutdown RID/ObjectDB leak diagnostics; retained in
final.log, not called a clean editor shutdown. The fresh runtime exits 0 with no ERROR/WARNING
lines. A temporary Python evidence-script rewrite hit Windows codepage encoding; restored
with explicit UTF-8 before final checks. No source/export data was affected by that tooling
failure. Text authoring plus headless normalization is the authorized fallback: windowed
editor use is prohibited, and live owner sessions were neither accessed nor synchronized.

## Remaining acceptance

- Independent technical/art review of this exact committed delivery.
- World placement at workshop/fence edges: preserve both exits, foot bypass, turning/chain
  spacing and open yard centre. Ensure the freestanding collider does not become a route barrier.
- Native 47m/42° camera/readability with actors, final lighting, combat/aim and repeated props;
  actual authoritative/predicted behavior across separate network processes.
- Production vehicle movement, packaged-platform/Deck LCD and OLED review, sustained frame
  pacing, LOD transitions and repeated-prop draw/shadow cost. Isolated renders, bounded API
  probes and successful imports do not establish full production acceptance.
