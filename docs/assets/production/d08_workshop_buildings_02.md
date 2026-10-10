# d08_workshop_buildings.02 — Sawtooth workshop

10 October 2026. **Source/export and bounded prefab checks delivered; independent review and
world/gameplay/device acceptance pending.** Commissioned by Regner under the
[commission](commission.md) and per-record production instructions. These supersede the
concept-only status of the [workshop family brief](../d08_workshop_buildings.md), not its
Ironreach revision-02 finish and silhouette requirements.

Producing owner: commissioned asset-production worker, original Blender construction,
technical integration and visual self-review. Accepting owners: independent asset reviewer
and supervising production lead (pending); downstream layout/gameplay/device owners retain
their gates. No world placement, shared register, catalogue or progress changes. The sole
approved sibling edit updates the .01 handoff's stale pending item and its manifest entry;
its source, prefab, validation and historical receipts are unchanged.

## Design and dimensions

A compact, nearly square two-bay workshop with **three asymmetric sawtooth roof folds**,
not a stretched dock warehouse. Broad opaque clerestory strips face local +X beneath pale
peak caps. Faded petrol walls, oversized worn-brick courses, localized rust, dented closed
roller shutters and three mismatched corrugated repair sheets retain the first shed's
Ironreach vocabulary. One short amber roof band and occupied service-door glazing provide
restrained work accents; no cyan is needed here. Original construction, no brands,
downloaded assets, generated-image geometry or external textures. The selected Ironreach
v02 district concept was inspected as style reference, not measured for dimensions.

These are **provisional authored dimensions**, consistent with the first sibling and the
production brief's permission to proceed. They are not a district parcel or traffic allocation.

| Contract | Metres, Godot local axes unless stated |
| --- | --- |
| Closed structural footprint | X 14.00 × Z 12.00, ground-centred |
| Wall/collision datum | Y 4.00 |
| Visual AABB minimum | (-7.35, 0, -6.35) |
| Visual AABB maximum | (7.35, 6.50, 6.35) |
| Overall visual dimensions X/Y/Z | 14.70 × 6.50 × 12.70 |
| Three tooth stations, X | -7.35, -2.45, 2.45, 7.35; 4.90m pitch |
| Tooth roof plane | nominal valley Y 4.10 → peak Y 6.40; 0.16m vertical thickness |
| Peak caps | top Y 6.50; 0.12m wide; cover recessed sheet/rib ends |
| Clerestory glazing | Y 4.48–6.05; nominal 11.60m length, four broad panes per strip |
| Overhang | maximum 0.35 beyond structural walls; overhead, not walkable |
| Brick base / straight side bays | 0.72 high / four 3.00m bays per side |
| Pale wall bands | Y 3.65–3.90 |
| Two closed shutter leaves | 4.20 wide × 3.00 nominal high; centres X -3.50 and +1.50 |
| Shutter surrounds | 0.24 jambs, 0.32 header; outer width 4.68; top Y 3.43 |
| Closed service door | 1.20 wide; centre X +5.60; top Y 2.39 |
| Applied detail projections | mortar 0.006; pilasters 0.045; window 0.15; door pull 0.23 |
| Integral task-lamp projection | 0.26, entirely above Y 3.415 |
| Numeric tolerance | envelope/ground ±0.001; source → GLB axis mapping ±0.00001 |

The root and joined mesh pivots are both (0,0,0), centred on the structural ground
footprint. Metres, applied transforms, unit scale, no corrective wrapper transform.
Blender +Y front maps to Godot -Z; Blender +Z maps to Godot +Y. The sawtooth high faces
point +X. No interior, rooftop access, usable doors, destruction, animation or interaction.
Amber material emission 0.3 is appearance-only: no actual lights or illumination budget.

### Family continuity and office interface

The delivered [small pitched repair shed](d08_workshop_buildings_01.md) is 10 × 12m with
one gable and one shutter; this workshop is 14 × 12m with three sawteeth and two shutters.
The unequal silhouettes, rather than recolouring or stretching a whole prefab, establish
separate practical repair plots. Both use the same eight material names/PBR values,
3m side bays, 4m wall datum, 0.72m base, 4.2m shutter leaf and 0.16m roof-sheet construction.
Shutter folds retain the sibling's 0.055m broad dent and replace only selected courses.
Corrugations are deliberately broad, at 0.65m centres, rather than fine grunge.

This workshop's available office connection is its plain **right-rear wall X +7**,
**Z 3…6**, centred at **(7,0,4.5)**. The forward high window is outside that interface.
The joining office should remain below the shared pale eave band/4m wall datum, cover the
at-most-0.05m trim seam and never imply passage through this closed wall. The clerestory
and roof begin above this interface. This is a documented plane, not a runtime socket.
The office owner retains attachment dimensions and the saved composition; no substitute
office or extra landmark is invented here. The [.04 office delivery](d08_workshop_buildings_04.md)
now supplies a saved family comparison with an attached office, using the existing shed
prefabs; the [.03 larger depot](d08_workshop_buildings_03.md) is also delivered separately.

## Source, exports and materials

| Deliverable | Path / identity |
| --- | --- |
| Editable source | `art/source/models/environment/d08_workshop_buildings_02/d08_workshop_buildings_02.blend` |
| Export collection | `export_d08_workshop_buildings_02` |
| Root → mesh | `D08WorkshopBuildings02` → `D08WorkshopBuildings02_Mesh` |
| Linked explicit export | `art/models/environment/d08_workshop_buildings_02/d08_workshop_buildings_02.glb` |
| Import metadata | adjacent `.glb.import`, UID `uid://dg2uc1pxhyqph` |
| Saved wrapper | `scenes/prefabs/environment/d08_workshop_buildings_02.tscn`, UID `uid://1fmk413q355u` |
| Tools | `tools/asset_production/d08_workshop_buildings_02/{author.py,export.py,validate.py,check_prefab.gd,record.py}` |

Eight opaque, back-culling Principled material surfaces, in exported order:

1. `ironreach_worn_brick` — muted brick base.
2. `ironreach_faded_petrol` — wall paint, quiet mortar, one replacement sheet.
3. `ironreach_pale_band` — structural bands, surrounds, mullions and peak caps.
4. `ironreach_local_rust` — sparse base repairs, shutter wear and one roof patch.
5. `ironreach_dark_recess` — opaque clerestories, window/door and lamp casing.
6. `ironreach_roof_petrol` — main sawtooth sheets and shutters.
7. `ironreach_replacement_sheet` — galvanized repair sheet and shutter courses.
8. `ironreach_working_amber` — occupied door, task lenses and one roof band.

Exact PBR values are in [validation.json](d08_workshop_buildings_02-evidence/validation.json).
No textures, embedded images, material overrides, external material resources, authored UV
artwork, rigs, clips or sockets. No extra variant or custom LOD is required. Default Godot
LOD generation remains enabled; transitions and repeated-building cost need native review.

Blender **5.2.2 LTS**, build **d13f752e3b9c**; glTF exporter **5.2.40**. The export script
loads the shared `tools/assets/blender/export_settings.json`, explicitly filters the named
collection and disables animation/skins for this static model. Applied bevel/normal
modifiers are baked into the editable source. Closed manufactured components are joined
into one mesh, not boolean-unioned into a single solid. Studio geometry, cameras and lights
are outside the export collection. Gameplay collision is independent of render topology.

## Evidence and reproduction

[Hero](d08_workshop_buildings_02-evidence/hero.png) ·
[Side](d08_workshop_buildings_02-evidence/side.png) ·
[Clerestory detail](d08_workshop_buildings_02-evidence/clerestory_detail.png) ·
[47m / 42° overhead](d08_workshop_buildings_02-evidence/overhead_47m_42deg.png).

All four are **isolated Blender renders**, Cycles CPU, 32 samples, AgX, soft studio lighting.
The vertical-down perspective camera is at (0,0,47), north/+Y at image top, **42° vertical
FOV**, **1280×720**. The three oblique views are rendered at 1280×720 and reduced to
1152×648 by `record.py` to meet lean evidence size targets. All remain within the current
1280×720 maximum, which supersedes the older 800px example. Blender PNG compression 95;
evidence-only 6-bit RGB quantization (overhead 7-bit), lossless PNG compression level 9.
Final PNGs are 228–407KB. Quantization can band the studio gradients; it does not alter
model materials or exported shading.

Self-review inspected all four final images. Three pale peak lines, asymmetric slope
shading, mismatched patches and the single amber strip remain distinct overhead. The
obliques show broad clerestories, two closed work bays and a quieter office-compatible
flank. Initial coplanar sheet/rib end faces produced cap speckling; recessing them beneath
the caps removed it. The final side view is a true flank view. No native Godot visual or
populated-gameplay screenshot is claimed.

Exact reproduction from repository root, isolated processes only:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=tools/asset_production/d08_workshop_buildings_02
X=C:/tmp/ft/assets/d08_workshop_buildings_02
mkdir -p "$X"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py" > "$X/author-final.log" 2>&1
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" > "$X/validate-final.log" 2>&1
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

`validate.py` opens the saved source, decodes actual GLB position/normal/index buffers,
checks literal independent bounds and material rays (including all three clerestories),
then runs `export.py` into scratch and compares the entire GLB bytes. `export.py` also
accepts `-- <output-directory>` when run against the saved source. The producer
[manifest](d08_workshop_buildings_02-evidence/manifest.json) hashes every delivered payload
except itself. Scratch/retry renders and raw logs remain outside the repository; the
[concise final log](d08_workshop_buildings_02-evidence/final.log) retains final results and
unsuppressed editor diagnostics.

## Validation and prefab collision

**23,616 triangles; 12,432 source vertices; 14,480 exported vertices (normal splits);
one mesh; eight surfaces.** Zero non-manifold source edges, zero degenerate source faces,
zero degenerate exported triangles. Source/export normals are unit length; triangle
winding agrees with exported normals. Bounds, axis mapping and ground meet the stated
tolerances. The **495,968-byte GLB** re-exports byte-identically. Exactly two exported nodes;
no cameras, lights, images, skins or animation.

The wrapper was text-authored then loaded/packed/resaved in the pinned headless editor;
a second load/save was byte-stable, preserving scene/node UIDs. `Visuals/Model` is an
identity-transform imported instance, without copied render geometry. One direct-child
`BoxShape3D` under `Collision/Body`, named `WorkshopSolid`, is **14 × 4 × 12m**, centred
at **(0,2,0)**, static-world layer 1 / mask 0. It blocks the full closed workshop and all
three decorative entrances. Small applied trim is deliberately excluded; roof/infill
above the 4m solid envelope is overhead visual-only, not walkable. No deck, step or ramp.

Pinned Godot **4.8.dev7.official.c971f93e7** checks passed:

- Dependencies, UIDs, linked ancestry, identity transforms, measured AABB, all eight opaque
  back-culling materials, exact collider size/layers and save/reload stability.
- Ten radius-0.35m / height-1.8m capsule queries: both shutters, service door, closed volume
  and opposite corners solid; four outside routes clear. Front ray hits exactly Z -6.
- Production `ActorMotion.step`, 60 ticks per case in **AUTHORITY and REPLAY**: both shutters
  and service door stop at Z **-6.350261m**; east wall at X **7.350267m**; east bypass reaches
  Z **-3.999996m**. All paired endpoints are exactly equal. Static physics equivalence is
  not real network transport proof.
- A **1.9 × 1.5 × 4.3m car-sized box** sweep stops at the facade and clears the east bypass.
  This is not production driving, turning-radius or car physics acceptance.
- Pinned gdstyle 0.3.0 formatting/lint passed after splitting movement-case literals from
  the test loop to resolve one function-length warning. Canonical production checks passed
  every layer: explicit owned-script compilation, **17 Python tests**, **165 GUT tests /
  6,918 assertions**, and expected-negative-test detection. **No failures ignored.**

Final import exited 0 without ERROR lines. Isolated editor normalization exited 0 with
byte-stable saves but emitted the existing toolkit 4.8 compatibility warning, aborted scan
and editor-shutdown RID/ObjectDB leak diagnostics; these remain visible in the final log,
not described as a clean editor exit. Fresh non-editor prefab/motion runtime exited 0
without ERROR/WARNING. No live Blender/Godot MCP or windowed session was used. Headless
import does not prove synchronization of a separate open editor, and none is claimed.

## Remaining acceptance

- Independent technical/art review of this exact source/export/prefab candidate.
- The [d08_workshop_buildings.03 larger depot](d08_workshop_buildings_03.md) is now delivered
  with the shared datums/finishes. The [.04 attached office](d08_workshop_buildings_04.md)
  now supplies a saved comparison instancing .01 and .02 with the office, without a duplicate
  landmark. Its bounded checks cover the join and open two-ended yard; actual world routes
  and the foot bypass remain placement responsibilities.
- World integration: district placement, building-to-route clearances, two yard exits,
  foot bypass, production car turning and chain spacing. Nothing is placed here.
- Native 47m/42° camera with actors/combat, populated-city visibility and occlusion;
  authoritative/predicted behavior over real separate network processes.
- Packaged platform and Deck LCD/OLED review, sustained frame pacing, repeated-building
  draw/LOD/shadow costs and any future actual task lighting. No full game-ready production
  acceptance is claimed by isolated source/import evidence.
