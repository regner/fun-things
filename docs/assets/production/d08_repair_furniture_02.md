# d08_repair_furniture.02 — Tyre rack

10 October 2026. **Source/export and bounded prefab checks delivered; independent review,
world/gameplay and target-device acceptance pending.** Commissioned by Regner under
[the commission](commission.md) and the current per-record production brief. This supersedes
concept-only restrictions in [the family brief](../d08_repair_furniture.md), retaining its
Ironreach revision-02 appearance and static dressing constraints.

Producing owner: commissioned asset-production worker (original Blender construction,
technical integration, visual self-review). Accepting owners: independent asset reviewer
and supervising production lead; placement/gameplay/device owners retain downstream gates.
The preceding [tool cabinet](d08_repair_furniture_01.md) establishes the family finish.
Its current handoff has no pending tyre-rack item to reconcile; no sibling, registry,
shared brief, progress, catalogue or world file changed.

## Design and dimensions

A grounded two-tier steel rack with **ten integral tyres**, five per row. Open end frames,
paired cradle rails and a diagonal rear brace keep the silhouette functional rather than
cabinet-like. Rounded tyre shoulders, hollow centres and two broad circumferential tread
channels read at close range without dense tread noise. The upper front rail is a restrained
amber replacement; five small edge-wear patches expose muted metal or localized rust.
The rack remains usable-looking. No loose tools, scattered tyres, rubble or neon labels.

The selected [Ironreach v02 concept](../../concepts/districts-v1/08-ironreach-v02.png),
[approved district identity](../../concepts/world-v1/stage-03-district-identities/README.md)
and [working-street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) were
inspected as context. Dimensions are **provisional authored choices**, allowed by the
standing production rules, not measurements inferred from generated concepts or approved
placements. Group against workshop/fence edges, never across exits or the foot bypass.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Overall visual dimensions X/Y/Z | **2.20 × 1.84 × 0.82** |
| Visual AABB minimum / maximum | **(-1.10, 0, -0.41) / (1.10, 1.84, 0.41)** |
| Two ground runners | Each 0.20 wide × 0.04 high × 0.82 deep; centres X ±1.00 |
| Four uprights | 0.07 square, Y 0.04–1.84; centres X ±1.00, Z ±0.32 |
| Cradle rails | 2.00 wide × 0.12 high × 0.07 deep; centres Y 0.19 / 1.03, Z ±0.255 |
| Tyres | Diameter 0.72, width along X 0.30, inner bore diameter 0.40 |
| Tyre centres | X -0.72 / -0.36 / 0 / 0.36 / 0.72; Y 0.50 / 1.34; Z 0 |
| Tyre clearances | 0.06 between adjacent sidewalls; lowest tyre point Y 0.14 |
| Abrasion geometry | Five sparse closed 0.0008m-thick paint-loss prisms |
| Pivot | (0,0,0), centred ground footprint; root and joined mesh at identity |
| Tolerances | Envelope and ground ±0.001m; normal length ±0.0001 |
| Collision | One 2.20 × 1.84 × 0.82m box, centre (0,0.92,0) |

Metre units and applied transforms. Blender +Y faces the amber front rail and maps to
Godot -Z; Blender +Z maps to Godot +Y. There is no corrective prefab rotation or scale.
Tyres are integral static dressing, not pickup or physics objects. No animation, wheels
on the rack, repair interaction, interiors, moving equipment, destruction states or sockets.

## Source, exports and materials

| Deliverable | Path / identity |
| --- | --- |
| Editable original source | `art/source/models/environment/d08_repair_furniture_02/d08_repair_furniture_02.blend` |
| Export collection | `export_d08_repair_furniture_02` |
| Root → mesh | `D08RepairFurniture02` → `D08RepairFurniture02_Mesh` |
| Explicit export | `art/models/environment/d08_repair_furniture_02/d08_repair_furniture_02.glb` |
| Model import UID | `uid://yxupe8mmhn12`; adjacent `.glb.import` retained |
| Linked wrapper | `scenes/prefabs/environment/d08_repair_furniture_02.tscn` |
| Wrapper UID | `uid://b1xkmimjh2ynm`; engine-generated node identities retained |
| Reproduction/check tools | `tools/asset_production/d08_repair_furniture_02/` |

Original Blender construction only: no downloaded meshes, purchased assets, external
fonts/textures, real brands, generated-image geometry or runtime-generated render meshes.
`author.py` retains the parametric original recipe, including the revolved tyre section.
`export.py` uses shared `tools/assets/blender/export_settings.json`, filtering the named
collection and disabling skins/animations. Pinned **Blender 5.2.2 LTS**, build
**d13f752e3b9c**, glTF exporter **5.2.40**. Bevel/weighted-normal modifiers are baked before
saving; glTF triangulates the editable faces. Independent closed manufactured parts share
one mesh, intentionally intersecting at joints/cradles; they are not a boolean-unioned
solid. The collider does not derive from render topology.

The tool-cabinet's five applicable painted-metal swatches and PBR settings are retained;
a sixth tyre-rubber material is specific to these contents. Six opaque back-culled
Principled surfaces in exported order:

| Surface | sRGB swatch | Metallic / roughness | Use |
| --- | --- | --- | --- |
| `ironreach_roof_petrol` | `#294E58` | 0.30 / 0.60 | Runners, collars, rails, rear brace |
| `ironreach_faded_petrol` | `#627D7B` | 0.25 / 0.64 | Uprights and connection plates |
| `ironreach_replacement_sheet` | `#7D9190` | 0.55 / 0.52 | Broad fasteners and rubbed edges |
| `ironreach_working_amber` | `#F5BA55` | 0.10 / 0.65 | Upper front rail |
| `ironreach_tyre_rubber` | `#293437` | 0 / 0.86 | Ten integral tyres |
| `ironreach_local_rust` | `#A7653E` | 0 / 0.90 | Lower rail/post abrasion |

sRGB swatches are converted to linear values by the author; actual exported PBR values
are recorded in validation.json. No embedded images, textures, external `.tres` resources,
emission or lights. No private shared-material abstraction or sibling dependency. Repeated
placements instance the same prefab. Godot's default automatic LOD generation is retained;
no explicit LOD variants or accepted repeated-placement performance budget are claimed.

## Evidence and reproduction

[Hero](d08_repair_furniture_02-evidence/hero.png) ·
[Side](d08_repair_furniture_02-evidence/side.png) ·
[Tyre/cradle detail](d08_repair_furniture_02-evidence/detail.png) ·
[47m / 42° overhead](d08_repair_furniture_02-evidence/overhead_47m_42deg.png).

Four **isolated Blender renders**, 1280×720, Cycles CPU 32 samples, AgX, soft studio fill.
The temporary studio is neither saved into the source nor exported. The overhead is
vertical-down perspective at (0,0,47)m, +Y/north up, **42° vertical FOV**. The standing
720px lean-evidence rule supersedes the older example's 800px height. PNG compression 95,
then evidence-only RGB quantization to 6 significant bits (overhead 7) and PNG compression
9: each final image is below 400KB. Runtime art is not quantized.

All four views were inspected. Close views show both rows, hollow sidewalls, broad tread
channels, worn rails and the open frame. At 47m the five dark upper arcs, narrow gaps,
end frames and amber rail make a small quiet storage silhouette. Lower tyres and rust
are not claimed visible overhead. No enlargement or billboard was introduced for camera
readability. Native engine/world lighting, actors and populated-camera occlusion remain
placement review, not results of isolated studio renders.

Exact commands from repository root (isolated processes; no live owner MCP sessions):

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=tools/asset_production/d08_repair_furniture_02
S=art/source/models/environment/d08_repair_furniture_02/d08_repair_furniture_02.blend
X=C:/tmp/ft/assets/d08_repair_furniture_02
mkdir -p "$X"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup "$S" --threads 4 --python-exit-code 1 --python "$T/export.py" -- "$X/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$X/reexport/d08_repair_furniture_02.glb"
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

Python/Pillow is only for evidence encoding/manifests. The validator opens the saved
source, audits actual GLB binary positions/normals/indices, checks independent literal
bounds, confirms ten rubber islands with specified dimensions/row positions, and requires
a fresh-process GLB argument for whole-file byte comparison. Asset-specific tools follow
the sibling conventions and shared export settings, without adding shared infrastructure.
`record.py` incorporates bounded engine results and hashes all produced payloads except
its own manifest. Scratch/retry exports and raw logs remain under the displayed `C:/tmp`
path; only a concise [final log](d08_repair_furniture_02-evidence/final.log) is committed.
No `tools/production_checks.py` run, per owner decision 52.

## Validation and prefab collision

**19,944 triangles; 10,040 source vertices; 10,731 exported vertices (normal/UV splits);
one mesh; six surfaces.** Ten connected tyre solids have their own expected 0.30 × 0.72 ×
0.72m source dimensions and two-row locations. Zero degenerate source faces, zero
non-manifold source edges, zero degenerate exported triangles. Source corner and exported
normals have unit length; consistent winding and exported triangle/normal agreement pass.
Source and GLB bounds/ground datum pass. Exactly two export nodes with identity transforms;
no cameras, skins, animations, textures or images.

Final **469,100-byte** GLB re-exports **byte-identically**. SHA-256 copied from the final
validation receipt:
`0734a510f949a3ad7e6d050e6596629c75b5f283c9e157d0b1f6bbe9af4eb622`.
The same byte count and hash are verified by the final producer manifest.

`Visuals/Model` is an identity-transform linked imported scene, with no embedded replacement
mesh. `Collision/Body/RackSolid` is one direct `CollisionShape3D` child of a `StaticBody3D`:
box **2.20 × 1.84 × 0.82**, centre **(0,0.92,0)**, static-world layer **1**, mask **0**.
This deliberate furniture envelope fills small gaps rather than creating decorative snag
points. The 0.40m tyre bores and 0.06m inter-tyre gaps cannot admit a 0.70m-wide actor.
The box extends at most 0.065m beyond end posts, 0.05m beyond the tyres' front/rear arcs
and 0.14m above the upper tyres to include the end-frame height; runners establish the
full plan footprint. The rack is a solid static prop, not a traversable shelf or yard
boundary. No navigation, world placement or gameplay interaction was added.

Pinned **Godot 4.8.dev7.official.c971f93e7** bounded checks passed:

- Linked imported ancestry, identity transform, resource-backed mesh, measured AABB,
  six opaque back-culled materials, exact one-box collider and registered model/wrapper UIDs.
- Headless editor load/pack/save/reload/save assigns scene/node identities. The second
  save is byte-identical; scene/dependency UIDs and node identities remain stable.
- Eight production-size capsule queries (radius 0.35m, height 1.8m): body and opposite
  corners blocked; four perimeter routes and the above-rack region clear.
- Front aim ray strikes Z **-0.409999967m**.
- Production `ActorMotion.step`, 60 ticks per case, front/rear/east contact and east bypass
  in both **AUTHORITY and REPLAY**. Paired endpoints exactly equal. Front/rear stop at
  Z **±0.761067450m**, east at X **1.450521350m**; bypass reaches Z **2.999999762m**.
  Solver tolerance 0.025m against independent literal contact expectations.
- A 1.9 × 1.5 × 4.3m car-sized box sweep is blocked from the front and clears the east
  bypass at X 2.15m. This is not production car handling or network transport evidence.
- Owned GDScript passes pinned gdstyle format and lint with zero issues; Python scripts parse.

All Blender checks exit 0; only material-API deprecation notices. Final pinned import
exits 0 with no ERROR/SCRIPT ERROR lines (existing toolkit compatibility warning remains).
Headless editor normalization exits 0 with stable-save assertions but emits known aborted
scan and shutdown RID/ObjectDB leak diagnostics; these are retained in final.log, not
called a clean editor shutdown. The separate fresh runtime exits 0 with no ERROR/WARNING
lines. Text authoring plus pinned headless normalization is the explicitly authorized
fallback; live editors were neither accessed nor synchronized.

## Remaining acceptance

- Independent technical/art review of the exact committed delivery.
- World placement against the selected district: group along workshop/fence edges,
  preserve both yard exits, the foot bypass, turning/chain spacing and open yard centre.
- Native 47m/42° camera/readability with actors, final lighting, combat/aim and repeated
  props; actual authoritative/predicted behavior across separate network processes.
- Production vehicle movement, packaged-platform/Deck LCD and OLED review, sustained
  frame pacing, LOD transitions and repeated-prop draw/shadow costs. Isolated renders,
  bounded motion probes and clean imports do not establish full production acceptance.
