# d08_workshop_buildings.03 — Larger depot

10 October 2026. **Source/export and bounded prefab checks delivered; independent review and
world/gameplay/device acceptance pending.** Regner's [production commission](commission.md)
and per-record production brief supersede the concept-only status of the
[workshop family brief](../d08_workshop_buildings.md), not its Ironreach revision-02 requirements.

Producing owner: commissioned asset-production worker, original Blender construction,
technical integration and visual self-review. Accepting owners: independent asset reviewer
and supervising production lead (pending); downstream layout/gameplay/device owners retain
their gates. No register, progress, catalogue or world-placement changes. The only sibling
edits update the .01/.02 handoffs' stale depot-pending items and those documents' manifest
entries; their assets, validation and historical receipts are unchanged.

## Design and dimensions

A larger low working depot with **two unequal adjacent pitched roofs**, three closed roller
shutters and a small occupied service door. The footprint is longer and wider than either
repair shed, but remains a compact 18 × 15m block rather than a long East Docks warehouse.
The broad main roof, narrower lower roof and dark valley give it an independent silhouette:
it is not a scaled copy of the single-gable shed or a recoloured sawtooth workshop.

Faded petrol walls, pale bands, oversized worn-brick courses, localized rust, dented shutter
folds and four broad mismatched corrugated roof repairs implement revision 02. One restrained
amber band crosses only the main pitch; amber panes/task lenses imply an occupied frontage.
No cyan, fine grunge, real brands, downloaded art, image-derived geometry or external textures.
The selected Ironreach v02 concept was inspected for style, never measured for dimensions.

All dimensions below are **provisional authored values**, permitted by the production brief
and consistent with the delivered siblings; they are not approved parcel/traffic allocations.

| Contract | Metres, Godot local axes unless stated |
| --- | --- |
| Closed structural footprint | X 18.00 × Z 15.00, ground-centred |
| Shared wall/collision datum | Y 4.00 |
| Visual AABB minimum | (-9.35, 0, -7.85) |
| Visual AABB maximum | (9.35, 6.80, 7.85) |
| Overall visual dimensions X/Y/Z | 18.70 × 6.80 × 15.70 |
| Main roof | X -9.35…2.00; ridge X -3.675; sheet ridge Y 6.70 |
| Lower roof | X 2.00…9.35; ridge X 5.675; sheet ridge Y 5.65 |
| Ridge caps | 0.19 wide; tops Y 6.80 and 5.75 |
| Roof sheets | 0.16 vertical thickness; valley/eave upper faces Y 4.10 |
| Overhang | 0.35 beyond exterior walls; overhead, non-walkable |
| Valley flashing | X 1.87…2.13; top Y 4.19; covers the sheet junction |
| Brick base / side wall bays | 0.72 high / five 3.00m bays per side |
| Pale upper bands | Y 3.65–3.90 |
| Three closed shutter leaves | 4.20 wide × 3.00 nominal high; centres X -6, -1, +4 |
| Shutter surrounds | 0.24 jambs, 0.32 header; outer width 4.68; top Y 3.43 |
| Closed service door | 1.20 wide; centre X +7.60; top Y 2.39 |
| Applied detail projection | mortar 0.006; pilasters 0.045; window 0.15; door pull 0.23 |
| Integral task-lamp projection | 0.26, entirely above Y 3.415 |
| Numeric tolerance | envelope/ground ±0.001; source → GLB axis mapping ±0.00001 |

Root and joined mesh pivots are both (0,0,0). Metre units, applied rotation/scale and unit
root scale; no corrective wrapper transforms. Blender +Y front maps to Godot -Z, and
Blender +Z maps to Godot +Y. No interiors, usable doors, roof traversal, loading platform,
steps, destruction, rig, animation, real lights or interaction state. Amber emission 0.3
is appearance-only, not a yard-illumination or lighting-budget claim.

### Family continuity and office connection

The [10 × 12m pitched shed](d08_workshop_buildings_01.md) and
[14 × 12m sawtooth workshop](d08_workshop_buildings_02.md) establish the shared 3m bays,
4m wall datum, 0.72m brick base, 4.2m shutter leaf, 0.16m roof sheets and eight material
names/PBR values. This depot retains those component dimensions and finishes, with an
extra side bay and third shutter. The original sibling shutter recipe retains twelve
folds, a maximum 0.055m broad dent and selected replacement courses. Corrugations remain
0.65m apart, deliberately broad for the gameplay camera. The validator compares actual
exported material definitions against **both delivered sibling GLBs**.

Available office plane: plain **right-rear wall X +9**, **Z 4.5…7.5**, centre
**(9,0,6)**. This is one shared 3m bay; the forward window is outside it. The joining
office roof should stay below the common pale band/4m wall datum (outer eave underside
approximately 3.94m), cover the at-most-0.05m trim seam and not imply passage through the
closed wall. The attached-office record owns its dimensions and saved composition. This
is a documented plane, not a runtime socket or new opening API. No duplicate landmark,
substitute office, yard surface or family assembly is invented here.

## Source, exports and materials

| Deliverable | Path / identity |
| --- | --- |
| Editable source | `art/source/models/environment/d08_workshop_buildings_03/d08_workshop_buildings_03.blend` |
| Export collection | `export_d08_workshop_buildings_03` |
| Root → mesh | `D08WorkshopBuildings03` → `D08WorkshopBuildings03_Mesh` |
| Linked export | `art/models/environment/d08_workshop_buildings_03/d08_workshop_buildings_03.glb` |
| Import metadata | adjacent `.glb.import`, UID `uid://4mbapcfcv743` |
| Saved wrapper | `scenes/prefabs/environment/d08_workshop_buildings_03.tscn`, UID `uid://b733foxnh7usw` |
| Tools | `tools/asset_production/d08_workshop_buildings_03/{author.py,export.py,validate.py,check_prefab.gd,record.py}` plus generated GDScript `.uid` |

Eight opaque, back-culling Principled surfaces, in exported order:

1. `ironreach_worn_brick` — muted masonry base.
2. `ironreach_faded_petrol` — wall paint, quiet mortar and one repair sheet.
3. `ironreach_pale_band` — bands, surrounds, mullions and ridge caps.
4. `ironreach_local_rust` — sparse base repairs, shutter wear and one roof patch.
5. `ironreach_dark_recess` — glazing, door/reveal, lamp casings and valley flashing.
6. `ironreach_roof_petrol` — paired roof planes and shutter folds.
7. `ironreach_replacement_sheet` — galvanized roof repairs and shutter courses.
8. `ironreach_working_amber` — occupied door, integral task lenses and main-roof band.

Exact PBR values are in [validation.json](d08_workshop_buildings_03-evidence/validation.json).
No textures, embedded images, external materials, material overrides or UV artwork are
needed. No rig, clips, sockets, extra variants or custom LODs. Godot's default automatic
LOD generation is enabled; repeated-building cost and transitions need native profiling.

Blender **5.2.2 LTS**, build **d13f752e3b9c**; glTF exporter **5.2.40**. `export.py` reads
`tools/assets/blender/export_settings.json`, filters the named collection and disables
animation/skins for this static asset. Applied bevel/normal modifiers are baked into the
editable source. Closed manufactured components are joined into one mesh, not boolean-unioned
into one solid. The studio ground, camera and lights remain outside the export collection.
Geometry is original Blender construction; no procedural runtime render hierarchy is used.

## Evidence and reproduction

[Hero](d08_workshop_buildings_03-evidence/hero.png) ·
[Side](d08_workshop_buildings_03-evidence/side.png) ·
[Frontage detail](d08_workshop_buildings_03-evidence/frontage_detail.png) ·
[47m / 42° overhead](d08_workshop_buildings_03-evidence/overhead_47m_42deg.png).

All are **isolated Blender renders**, Cycles CPU, 32 samples, AgX and soft studio lighting.
The overhead is vertical-down perspective at (0,0,47), north/+Y at image top, **42° vertical
FOV, 1280×720**. The current maximum 720px evidence height supersedes the older example's
800px height. Obliques are rendered at 1280×720 then reduced to 1152×648 by `record.py`.
PNG compression 95 in Blender; evidence-only 6-bit RGB quantization (overhead 7-bit) and
lossless PNG compression level 9. Final images are approximately 219–411KB. Gradient
banding can result from evidence compression; it does not alter the model or materials.

Self-review inspected all four final renders. Two unequal roof ridges, dark valley, four
repair sheets and one amber frontage band remain clear overhead. The true flank view shows
five quiet wall bays, the lower roof and office-compatible rear wall. The detail view shows
three dented closed work bays, pale surrounds and an occupied service door. Roof details
remain broad and sparse. Facade details are not claimed readable directly overhead. These
are not native Godot, populated-city or movement captures.

Exact reproduction from repository root, isolated processes only:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=tools/asset_production/d08_workshop_buildings_03
X=C:/tmp/ft/assets/d08_workshop_buildings_03
mkdir -p "$X"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py" > "$X/author-final.log" 2>&1
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" > "$X/validate-final.log" 2>&1
G="$(mise which godot)"
timeout 300 "$G" --headless --path . --import > "$X/import-final.log" 2>&1
timeout 180 "$G" --headless --editor --path . --script "res://$T/check_prefab.gd" -- --normalize > "$X/normalize.log" 2>&1
timeout 180 "$G" --headless --path . --script "res://$T/check_prefab.gd" > "$X/prefab-final.log" 2>&1
{ "$(mise which gdstyle)" fmt --check "$T/check_prefab.gd" && "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd"; } > "$X/style-final.log" 2>&1
python "$T/record.py" --compress-renders
python "$T/record.py"
python "$T/record.py" --verify
```

`validate.py` opens the saved source, decodes actual GLB position/normal/index buffers,
checks literal independent bounds and exterior material rays (brick, rear wall, three
shutters, two gables and office plane), compares sibling material definitions, then freshly
re-exports to scratch and compares the entire GLB bytes. `export.py` can also run against
the saved source with `-- <output-directory>`. [manifest.json](d08_workshop_buildings_03-evidence/manifest.json)
hashes every delivered payload except itself. Scratch logs/intermediate exports stay under
`C:/tmp/ft/assets/d08_workshop_buildings_03/`, outside the repository. One
[final log](d08_workshop_buildings_03-evidence/final.log) retains concise results and
unsuppressed editor diagnostics. `tools/production_checks.py` was **not run**, per owner
decision 52 for unplaced assets; no project-wide test result is inferred from import.

## Validation and prefab collision

**29,828 triangles; 15,684 source vertices; 18,212 exported vertices (normal splits);
one mesh; eight surfaces.** Zero non-manifold source edges, zero degenerate source faces
and zero degenerate exported triangles. Source/export normals are unit length; winding
agrees with exported normals. Literal bounds, ground datum and axis mapping pass. Exactly
two exported nodes, with no images, textures, cameras, lights, skins or animation.

Final GLB: **622,820 bytes**; SHA-256
`28f491977560abe5c4bf065351056ce22a3328db9d8182f7ea8b6f2b56992958`.
The fresh export is byte-identical; the hash/byte count above is copied from the final
validation receipt and verified against the producer manifest.

The text-authored wrapper was loaded/packed/resaved in the pinned headless editor; the
subsequent reload/save was byte-stable with unchanged scene/node IDs. `Visuals/Model` is
an identity-transform imported instance. One direct-child `BoxShape3D`, `DepotSolid`, under
`Collision/Body` is **18 × 4 × 15m**, centred at **(0,2,0)**, static-world layer 1 / mask 0.
It blocks the entire closed rectangular building, including its shutters and service door.
Small applied trim does not enlarge the collider. Roof/gables above the 4m solid envelope
are visual-only overhead decoration, not walkable. No copied render geometry, deck or ramp.

Pinned Godot **4.8.dev7.official.c971f93e7** checks passed:

- Dependencies/UIDs, linked mesh ancestry, identity transform, actual imported bounds,
  eight opaque/back-culling materials, one collider and exact collider size/layers/datum.
- **Eleven** r=0.35m / h=1.8m capsule queries: closed volume, all four entrances and opposite
  corners solid; four perimeter routes clear. Front aim ray hits exactly **Z -7.5**.
- Production `ActorMotion.step`, **60 ticks per case**, **AUTHORITY and REPLAY**: all three
  shutters and the service door stop at Z **-7.850272m**; east wall at X **9.350270m**;
  east bypass reaches Z **-6.000008m**. All six paired endpoints are exactly equal.
  This is bounded static collision equivalence, not network transport proof.
- A **1.9 × 1.5 × 4.3m car-sized test box** sweep is stopped at the front and clears the
  east bypass. This is not production driving, turning radius or car-physics acceptance.
- Pinned **gdstyle 0.3.0** formatting and zero-warning lint pass on the added GDScript.
  Python syntax checks pass on all four added Python scripts.

Final import exited 0 without ERROR/SCRIPT ERROR lines; the existing toolkit 4.8 compatibility
warning remains. Headless editor normalization exited 0 and proved stable saves but emitted
existing aborted-scan and shutdown RID/ObjectDB leak diagnostics, retained in the final log.
Fresh non-editor prefab/motion runtime exited 0 without ERROR/WARNING. An initial extra
GDScript blank line and evidence-recorder syntax error were corrected; no failed check is
counted as passing. Non-editor normalization was insufficient to supply resource UIDs, so
headless editor normalization was used. No windowed editor or owner's live Blender/Godot
MCP session was accessed; headless import does not synchronize a separate open editor.

## Remaining acceptance

- Independent technical/art review of this exact source/export/prefab candidate.
- The [.04 attached office](d08_workshop_buildings_04.md) now delivers the saved unequal-shed
  comparison and documented joins, including a source roof-clearance check for this depot.
  World integration still owns selected district fit, actual placement/office joins,
  two-exit yard and foot bypass, building-to-route clearance, car turning and chain spacing.
  Nothing is placed in a world scene here, and no duplicate landmark is delivered.
- Native 47m/42° camera with actors/combat, populated-city occlusion and visibility;
  authoritative/predicted behavior over real separate network processes.
- Packaged-platform and Deck LCD/OLED review, sustained frame pacing, repeated-building
  draw/LOD/shadow costs and any future real task lights. Source/import and isolated evidence
  alone do not establish full game-ready production acceptance.
