# d08_repair_furniture.03 — Low parts trolley

10 October 2026. **Source/export and bounded prefab checks delivered; independent review,
world/gameplay and target-device acceptance pending.** Commissioned by Regner under
[the commission](commission.md) and the current per-record production brief. This supersedes
the concept-only restriction in [the family brief](../d08_repair_furniture.md), preserving
Ironreach revision-02 appearance and static closed-dressing requirements.

Producing owner: commissioned asset-production worker (original Blender construction,
technical integration, visual self-review). Accepting owners: independent asset reviewer
and supervising production lead; placement/gameplay/device owners retain downstream gates.
The preceding [tool cabinet](d08_repair_furniture_01.md) and
[tyre rack](d08_repair_furniture_02.md) were read and visually inspected. Neither current
handoff lists this trolley as a pending item. No sibling, registry, shared brief, progress,
catalogue, gameplay code or world scene changed.

## Design and dimensions

A low stationary two-tray service trolley with four integral casters and a bent end push
handle. Two small covered sorting tins on the upper tray and one closed parts case below
supply restrained integral storage. A single amber front rim and four sparse irregular
rubbed-metal/rust patches continue the family finish. Broad painted surfaces and rounded
manufactured edges dominate; no loose tool inventory, rubble or noisy grunge.

The selected [Ironreach v02 concept](../../concepts/districts-v1/08-ironreach-v02.png),
[approved district identity](../../concepts/world-v1/stage-03-district-identities/README.md)
and [working-street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) informed
the design. Dimensions are **provisional authored choices**, allowed by the standing
production rules, not measurements from generated concepts or approved placements.
Group at workshop/fence edges; keep the yard centre, two exits and foot bypass clear.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Nominal overall X/Y/Z | **1.36 × 0.86 × 0.70** |
| Actual visual AABB min / max (rounded) | **(-0.6805, 0, -0.3505) / (0.6800, 0.8600, 0.3500)** |
| Actual visual dimensions (rounded) | **1.3605 × 0.8600 × 0.7005**; 0.5mm wear projection beyond nominal bounds |
| Tray floors | 1.24 wide × 0.03 high × 0.70 deep; X centre -0.06, Y centres 0.235 / 0.545 |
| Retaining lips | 0.03 thick × 0.085 high, top Y 0.335 / 0.645 |
| Four corner posts | 0.045 square; Y 0.190–0.620 |
| Four caster tyres | Diameter 0.18, width 0.06 along X; ground contact Y 0 |
| Caster centres | X -0.51 / +0.39, Y 0.09, Z ±0.255 |
| Push handle | 0.05 diameter bent bar; X centre +0.655; top Y 0.86, ends Z ±0.27 |
| Closed lower case body | 0.49 × 0.16 × 0.40; centre (-0.22, 0.33, +0.02) |
| Upper tin bodies | 0.38 × 0.10 × 0.43 and 0.29 × 0.078 × 0.35; highest lid grip Y 0.692 |
| Wear geometry | Four closed 0.0008m-thick prisms on retaining-rim faces |
| Pivot | (0,0,0), centred nominal ground footprint, root and mesh identity |
| Tolerances | Nominal envelope/ground ±0.001m; unit normals ±0.0001 |
| Collision | One **1.36 × 0.86 × 0.70** box at **(0,0.43,0)** |

Metre units and applied transforms. Blender +Y faces the amber long rim and maps to Godot
-Z; Blender +Z maps to Godot +Y. The push handle is at +X. The tray/axle assembly sits
slightly left of the centred overall envelope to accommodate the handle, not a corrective
prefab translation. No movement, repair interaction, opening lids, rig, clips, sockets,
interior, destruction or physics clutter. Casters suggest the manufactured object, but are
joined static geometry with no wheel nodes, simulation or moving-equipment system.

## Source, exports and materials

| Deliverable | Path / identity |
| --- | --- |
| Editable original source | `art/source/models/environment/d08_repair_furniture_03/d08_repair_furniture_03.blend` |
| Export collection | `export_d08_repair_furniture_03` |
| Root → mesh | `D08RepairFurniture03` → `D08RepairFurniture03_Mesh` |
| Explicit export | `art/models/environment/d08_repair_furniture_03/d08_repair_furniture_03.glb` |
| Model import UID | `uid://t1m2en3luf61`; adjacent `.glb.import` retained |
| Linked wrapper | `scenes/prefabs/environment/d08_repair_furniture_03.tscn` |
| Wrapper UID | `uid://c3bpjgrs6ccol`; engine-generated node identities retained |
| Reproduction/check tools | `tools/asset_production/d08_repair_furniture_03/` |

Original Blender construction only; no downloaded/purchased geometry, real brands, fonts,
external textures, generated-image geometry or runtime-authored render meshes. `author.py`
retains the parametric recipe, including the closed swept handle and caster assemblies.
`export.py` uses shared `tools/assets/blender/export_settings.json`, filtering the named
collection and disabling skins/animations. **Blender 5.2.2 LTS**, build **d13f752e3b9c**,
glTF exporter **5.2.40**. Bevel/normal modifiers are baked before saving; glTF triangulates
editable faces. Independent closed manufactured components intersect at their joints and
share one joined mesh, not a boolean-unioned solid. Collision is authored separately.

Six opaque back-culled Principled surfaces, in exported order. Swatches and PBR values
match the preceding tyre rack; painted metal also matches the cabinet.

| Surface | sRGB swatch | Metallic / roughness | Use |
| --- | --- | --- | --- |
| `ironreach_tyre_rubber` | `#293437` | 0 / 0.86 | Four integral caster tyres |
| `ironreach_replacement_sheet` | `#7D9190` | 0.55 / 0.52 | Axles, mounting plates, lids and rubbed rim edges |
| `ironreach_roof_petrol` | `#294E58` | 0.30 / 0.60 | Frame, handle and closed case bodies |
| `ironreach_faded_petrol` | `#627D7B` | 0.25 / 0.64 | Tray floors and retaining lips |
| `ironreach_working_amber` | `#F5BA55` | 0.10 / 0.65 | Upper front replacement rim |
| `ironreach_local_rust` | `#A7653E` | 0 / 0.90 | Localized lower/front and end-rim wear |

The author converts sRGB swatches to linear PBR values, recorded in validation.json.
No textures, embedded images, external `.tres` resources, emission or lights. No new
shared-material abstraction or sibling runtime dependency. Repeated placements reuse this
prefab. Godot default automatic LOD generation remains enabled; no explicit LOD variants
or accepted repeat-placement draw/shadow budget are claimed.

## Evidence and reproduction

[Hero](d08_repair_furniture_03-evidence/hero.png) ·
[Handle-side view](d08_repair_furniture_03-evidence/side.png) ·
[Storage/rim detail](d08_repair_furniture_03-evidence/detail.png) ·
[47m / 42° overhead](d08_repair_furniture_03-evidence/overhead_47m_42deg.png).

Four **isolated Blender renders**, 1280×720, Cycles CPU 32 samples, AgX, soft studio fill.
The render-only studio is never saved into the source/export collection. The overhead is
vertical-down perspective at (0,0,47)m, +Y/north up, **42° vertical FOV**. Standing lean
720px evidence rules supersede the older example's 800px height. Blender PNG compression
95, then evidence-only RGB quantization (6 significant bits; overhead 7), compression 9:
211–378KB per image. Runtime art is not quantized.

All four final views were visually inspected. Two low trays, small caster assemblies,
bent handle, closed tins and restrained wear read in close views. The 47m view remains a
small quiet rectangle with two pale lids and a narrow warm edge; lower storage, casters and
abrasion are not claimed readable overhead. No artificial scale increase or billboard was
added. This is self-review, not native engine/world-lighting or populated-camera acceptance.

Exact commands from repository root; isolated processes only, never live owner MCP sessions:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=tools/asset_production/d08_repair_furniture_03
S=art/source/models/environment/d08_repair_furniture_03/d08_repair_furniture_03.blend
X=C:/tmp/ft/assets/d08_repair_furniture_03
mkdir -p "$X"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup "$S" --threads 4 --python-exit-code 1 --python "$T/export.py" -- "$X/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$X/reexport/d08_repair_furniture_03.glb"
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
audits actual binary GLB positions/normals/indices, asserts independent literal bounds and
four caster-island dimensions/locations, and requires a fresh-process export argument for
whole-file comparison. Per-asset scripts follow sibling conventions and reuse the shared
export contract. `record.py` incorporates bounded engine results and hashes every produced
payload except its own manifest, after final import and handoff edits. Scratch/retry files
and full raw logs stay under the displayed `C:/tmp` path. One concise
[final log](d08_repair_furniture_03-evidence/final.log) is committed. No
`tools/production_checks.py` run, per owner decision 52.

## Validation and prefab collision

**10,352 triangles; 5,276 source vertices; 6,560 exported vertices (normal/UV splits);
one mesh; six surfaces.** Zero degenerate source faces, zero non-manifold edges and zero
degenerate exported triangles. Unit-length source corner/exported normals and consistent
winding pass. Four rubber islands independently match caster centres and 0.06 × 0.18 ×
0.18m source dimensions. Source/GLB bounds and ground datum pass. Exactly two exported
nodes, identity transforms, no cameras, skins, animations, images or textures.

Final **278,112-byte** GLB re-exports **byte-identically**. SHA-256 copied from final
validation.json:
`6b3a435902857ba0f74987ae3de3a8b6c39725a89b640351b8c0407cda5bf44b`.
The producer manifest independently verifies the same byte count and hash.

`Visuals/Model` is an identity-transform linked imported scene; no embedded replacement
mesh or runtime-generated visual hierarchy. `Collision/Body/TrolleySolid` is a direct
`CollisionShape3D` child of one `StaticBody3D`, box **1.36 × 0.86 × 0.70m**, centre
**(0,0.43,0)**, static-world layer **1**, mask **0**. The whole-prop envelope deliberately
fills shelf gaps, caster underclearance and the space beside the handle, avoiding small
snag colliders. The widest empty top margin is 0.215m above the tray lip; it is included
to cover the 0.86m handle. At ground level the box abstracts 0.22m of under-tray space.
Wear protrudes at most 0.5mm outside collision, within the recorded tolerance. This is
nontraversable static furniture, not a walkable deck or a movable obstacle system.

Pinned **Godot 4.8.dev7.official.c971f93e7** bounded checks passed:

- Linked imported ancestry, identity transform, resource-backed mesh, measured AABB,
  six opaque back-culled materials, exact one-box collider and registered model/wrapper UIDs.
- Headless editor load/pack/save/reload/save assigned scene/node identities. The second
  save is byte-identical, preserving normalized UIDs and node identities.
- Eight production-size capsule queries (radius 0.35m, height 1.8m): solid body and opposite
  corners blocked; four perimeter routes and above-trolley region clear.
- A front ray at tray height hits Z **-0.350000024m**. This is a shape query, not combat acceptance.
- Production `ActorMotion.step`, 60 ticks per case, front/rear/east contact and east bypass
  in both **AUTHORITY and REPLAY**. Paired endpoints are exactly equal. Front/rear stop at
  Z **±0.700520575m**; east at X **1.031250238m**. East bypass X **1.13m** reaches
  Z **2.999999762m**. Solver tolerance 0.025m against independent literal expectations.
- A 1.9 × 1.5 × 4.3m car-sized box sweep is blocked from the front and clear at east bypass
  X **1.75m**. This is not production car handling, turning or network transport evidence.
- Owned GDScript passes pinned gdstyle format/lint with zero issues; owned Python parses.

All Blender checks exit 0; material-API deprecation notices only. Final pinned import exits
0 with no ERROR/SCRIPT ERROR lines (existing toolkit compatibility warning remains).
Headless editor normalization exits 0 with stable-save assertions but known aborted-scan
and shutdown RID/ObjectDB leak diagnostics; these are retained in final.log, not called a
clean editor shutdown. The separate fresh runtime exits 0 with no ERROR/WARNING lines.
Text authoring plus headless normalization is the authorized fallback: windowed editor use
is prohibited by the brief, and live owner sessions were neither accessed nor synchronized.

## Remaining acceptance

- Independent technical/art review of this exact committed delivery.
- World placement at workshop/fence edges: preserve both exits, foot bypass, turning/chain
  spacing and open yard centre. Ensure the freestanding collider is not a route barrier.
- Native 47m/42° camera/readability with actors, final lighting, combat/aim and repeated
  props; actual authoritative/predicted behavior across separate network processes.
- Production vehicle movement, packaged-platform/Deck LCD and OLED review, sustained frame
  pacing, LOD transitions and repeated-prop draw/shadow cost. Isolated renders, bounded
  API probes and successful imports do not establish full production acceptance.
