# d02_house_family.01 — Detached house

10 October 2026. **Source, export, linked prefab and bounded headless checks delivered;
independent review and world/gameplay/device acceptance pending.** Production commissioned
by Regner; [commission](commission.md), [family brief](../d02_house_family.md),
[Crescents v02](../../concepts/districts-v1/the-crescents.md). The later explicit
production commission supersedes the historical concept-only restriction.

Producer: commissioned asset-production worker on `lane/a-house`. This is the first
house-family delivery; no earlier sibling output existed in this lane. Shared queue,
progress, briefs, world placements and other asset files are unchanged.

## Design and provisional dimensions

A compact two-storey detached home with a deep blue/slate hipped roof, short integral
ridge, and a lower rear-aligned plum side wing. The L-shaped ground footprint and
unequal roof heights distinguish it from a long terrace or paired-house frontage
without relying on colour. Quiet warm-grey render, ivory eaves/courses, broad paired
windows and one warm grade-level door keep it domestic rather than commercial.
Two warm blind panels are opaque colour accents, not lights or emissive gameplay cues.

Original Blender construction only; no downloaded geometry, brands, generated
image-to-mesh, external textures or runtime render meshes. The concept was inspected
for visual direction, not measured for dimensions. This asset includes the normal
closed door, windows and trim requested inside the shell. No porch canopy, chimney,
dormer, garden wall, ground surface or planting was selected: those remain separately
owned shared/district fixtures and are not duplicated here. No interior, interaction,
destruction, animation, rooftop traversal or new gameplay state is introduced.

**All dimensions are provisional authored choices**, consistent with the district's
10 × 12 m neutral house reference, not approved parcel allocations. Godot local X/Y/Z:

| Region | Bounds / dimensions in metres |
| --- | --- |
| Whole visual | min **(-5.4, 0, -5.7)**; max **(5.4, 8.2, 5.7)**; size **10.8 × 8.2 × 11.4** |
| Main structural volume | min (-5, 0, -5.3); max (3, 5.6, 5.3); 8 × 5.6 × 10.6 |
| Lower side wing | min (3, 0, -0.7); max (5, 3.15, 5.3); 2 × 3.15 × 6 |
| Overall structural footprint | 10 × 10.6 bounding rectangle; occupied L-footprint 96.8 m² |
| Main roof | fascia underside 5.48; hip eave 5.88; ridge cap 8.20; 0.40 overhang |
| Wing roof | high attachment 3.93; low edge 3.28; 0.40 outer/end overhang |
| Entry | centre X=1.12; facade Z=-5.3; closed leaf 1.30 wide × 2.38 high; no step |
| Principal window pair | 2.35 wide × 1.40/1.42 high; 0.09 centre mullion |
| Decorative projections | plinth 0.04; window sills 0.20; door pull 0.225 from wall |

The ground pivot is the centre of the **overall structural bounding footprint**, not
the main roof or L-area centroid. Root and mesh origin (0,0,0), unit scale and applied
rotation/translation. Blender +Y facade/front maps to Godot -Z; Blender +Z maps to +Y.
Source/export bounds tolerance ±0.001 m; axis mapping tolerance 0.00001 m. Flat ground
datum is zero. No authored sockets were requested or added.

For subsequent family members, this delivery supplies a concrete material/naming and
closed-shell reference, not a requirement to clone its footprint. Keep blue/slate or
muted plum roof planes, warm doors, ivory trim, quiet closed glazing and sparse roof
fittings. Paired/terrace/corner members still need genuinely different roof depth and
footprint, not recolours. Whole-row spacing/setback diversity remains a placement gate.

## Source, export and materials

- Source: `art/source/models/environment/d02_house_family_01/d02_house_family_01.blend`.
- Collection: `export_d02_house_family_01`; root `D02HouseFamily01`, one joined editable
  mesh `D02HouseFamily01_Mesh`. Closed constituent solids deliberately overlap at
  building/fitting junctions; there are no open mesh boundaries. This is not a boolean
  interior shell or watertight single connected volume.
- Export: `art/models/environment/d02_house_family_01/d02_house_family_01.glb` plus
  engine-generated `.glb.import`.
- Prefab: `scenes/prefabs/environment/d02_house_family_01.tscn`.
- Recipe/checks: `tools/asset_production/d02_house_family_01/` (`author.py`, `export.py`,
  `validate.py`, `check_prefab.gd` + UID, `record.py`).

Seven opaque Principled material surfaces, no images, UV-dependent artwork or material
remaps. Original sRGB authoring swatches are converted to linear shader colours:

| Imported slot | Material | sRGB swatch |
| --- | --- | --- |
| 0 | `crescents_warm_render` | `#ACA69E` |
| 1 | `crescents_slate_plinth` | `#58636B` |
| 2 | `crescents_ivory_trim` | `#D4CEBB` |
| 3 | `crescents_blue_slate_roof` | `#3E526C` |
| 4 | `crescents_muted_plum_roof` | `#68566B` |
| 5 | `crescents_petrol_closed_glass` | `#263F4D` |
| 6 | `crescents_warm_entrance` | `#D4A16B` |

All backface-culled, no transparency or emission. PBR values are retained in
[validation.json](d02_house_family_01-evidence/validation.json). Opaque glass avoids
implying interiors and bounds transparency cost. No external `.tres` is needed.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. The export script
loads `tools/assets/blender/export_settings.json`, selects the named collection and
disables animations/skins for this static asset. Studio cameras, lights, ground and
hidden one-metre reference remain outside the export. Applied bevels/weighted normals
are retained as editable mesh geometry; no unresolved modifiers. Default Godot import
keeps generated LODs/shadow meshes enabled. No explicit LOD family or ratified polygon,
draw-call, shadow or device budget is claimed.

## Prefab and collision

Saved linked imported instance at **`Visuals/Model`**, identity transform, no overrides,
embedded replacement render geometry or runtime hierarchy construction. Engine-generated
scene UID `uid://b2ibgbmqgrngb`, imported model UID `uid://48f4xwopelbr`; node identities
and script `.uid` retained. Scenes embed their UID rather than requiring a separate
`.tscn.uid` file.

`Collision/Body` is one static-world body, layer 1 / mask 0, with **two boxes** exactly
matching the main and side-wing structural volumes above. The front-side setback remains
open. Decoration, 0.40 m overhead roofs and shallow trim do not inflate gameplay solids.
The 0.04 m plinth/sill/pull projections are intentionally not snag colliders. Closed
entry/windows are blocked by the volume; no invisible traversable interior is implied.
Roofs are visual-only overhead regions, not walkable surfaces or an invitation to climb.

Text authoring plus pinned **headless editor** load/pack/save/reload established UIDs
and stable saved bytes. The explicit brief forbids live editor sessions; no owner's
Blender/Godot session was touched. This is not evidence of synchronizing an open editor.

## Validation and visual evidence

- **8,312 triangles; 4,318 source and exported vertices; one mesh, seven surfaces.**
- **Zero non-manifold edges, zero degenerate source faces/export triangles**; finite
  coordinates, unit source/export normals and positive triangle/normal alignment.
- Actual raw GLB buffer bounds match source conversion and literal design expectations.
- Fresh source-open export is **byte-identical**, GLB **157,956 bytes**, SHA-256
  `77ece7b85ff5d9dce824506aa8b8ef3d9ba68421c0acf349574baf2a18e6c993`.
- Fresh pinned Godot load proves linked dependencies, opaque materials, imported bounds,
  identity transform, two authored collision envelopes and registered UIDs.
- Seven production physics capsule overlap/clearance queries pass for radius **0.35 m**,
  height **1.8 m**. Front aim ray hits wall Z=-5.30000019 m.
- Production **`ActorMotion.step`**, 60 fixed ticks per case in both `AUTHORITY` and
  `REPLAY`: closed front stops Z=-5.66666222; setback approach stops at wing Z=-1.05078244;
  side approach stops X=5.35025549; clear east bypass reaches Z=-2.99999356 m. Both modes
  produce exactly equal final coordinates. Tests compare independent literal contact
  positions with 0.025 m solver-separation tolerance, not copied movement formulas.
- A documented **1.9 × 1.5 × 4.3 m test box** sweep blocks at the facade and clears the
  east bypass. This is a physics-envelope test, not production vehicle turning/handling.
- Full production checks **PASS**, no ignored failures: pinned compilation/style,
  **17 Python tests**, **149 GUT tests / 6,768 assertions**, expected failing negative
  control detected. Fresh runtime emitted no ERROR/WARNING diagnostics.

[Hero](d02_house_family_01-evidence/hero.png) ·
[side](d02_house_family_01-evidence/side.png) ·
[entrance detail](d02_house_family_01-evidence/entrance_detail.png) ·
[47 m / 42° overhead](d02_house_family_01-evidence/overhead_47m_42deg.png).
All are isolated Blender Cycles CPU / 32 samples / AgX **1280 × 720** renders. The
vertical-down overhead is perspective at (0,0,47), north/+Y up, **42° vertical FOV**;
not an oblique view, crop, orthographic substitution or engine capture. PNGs retain
6-bit RGB channel precision (overhead 7-bit), compression 9, each below 400 KB. This
bounded evidence-only colour reduction changes neither framing nor model materials.

Self-inspection of all four views confirms the compact hip plus unequal-height side
wing reads overhead; domestic facade details are intentionally not readable from directly
above. Raised rear-east upper sill now clears the wing roof; floor course ends no longer
intersect the front corner trims. Initial adaptive-palette compression visibly banded
shadows and was replaced with higher-colour RGB compression. Uncompressed renders and
retries remain outside Git. These are self-review observations, not independent acceptance.

Known diagnostics: Blender future-6.0 API deprecation notices; headless editor toolkit
4.8 compatibility warning and scan-aborted/RID/ObjectDB shutdown diagnostics during
normalization. Normalization returned 0 and stable bytes; a fresh runtime subsequently
passed without diagnostics. The first motion check's 3 mm endpoint tolerance rejected
normal front-contact separation (~17 mm); final tolerance is explicitly documented above.
Raw scratch logs are in `C:/tmp/ft/assets/d02_house_family_01/`; the concise committed
[final log](d02_house_family_01-evidence/final.log) retains final diagnostic classifications.

## Exact reproduction

From this worktree in Git Bash; scratch output directories must be fresh for the full
production suite. No windowed or MCP commands are required:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
STYLE="$(mise which gdstyle)"
TOOL=tools/asset_production/d02_house_family_01
TMP=C:/tmp/ft/assets/d02_house_family_01
mkdir -p "$TMP"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOL/author.py"
python "$TOOL/record.py" --compress-renders
timeout 300 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOL/validate.py"
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --editor --path . --script "$TOOL/check_prefab.gd" -- --normalize > "$TMP/normalize.log" 2>&1
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . --script "$TOOL/check_prefab.gd" > "$TMP/prefab-final.log" 2>&1
timeout 180 "$STYLE" "$TOOL/check_prefab.gd"
timeout 180 "$STYLE" fmt --check "$TOOL/check_prefab.gd"
timeout 1800 python tools/production_checks.py --godot "$GODOT" --gdstyle "$STYLE" --output "$TMP/checks"
python "$TOOL/record.py"
python "$TOOL/record.py" --verify
```

`author.py` rebuilds source/export/renders. `validate.py` separately opens the saved
source and reexports to scratch. `record.py` collects final receipts and hashes every
produced payload (including tools, source, import/UID metadata, prefab, doc and evidence)
except the self-referential manifest. Do not regenerate the source just to verify hashes;
`record.py --verify` is non-mutating. The shared pinned export contract is reused; no
new private general-purpose framework or shared-tool modification was introduced.

## Remaining acceptance

Independent art/technical review is pending. No saved district placement changed.
Parcel fit, sibling/whole-row silhouette comparison, diverse setbacks and unobstructed
cut-throughs, native fixed-light gameplay-camera/actor/combat visibility, real vehicle
handling, populated-city movement, separate-process multiplayer/transport/prediction,
packaged dependencies and sustained target-device performance remain downstream gates.
In particular, the actor mode-equivalence check is **not** a multiplayer test. No
whole-register readiness, TODO completion or placement authorization is implied.
