# d01_academic_buildings.03 — Compact annex

**Source/export and linked prefab delivered; independent review and placement acceptance pending.**
Produced by the commissioned isolated asset-production worker on `lane/a-acad`.
Regner owns design selection; the production supervisor owns technical/art review and integration.
The [production commission](commission.md) supersedes the concept-only restriction in the
[academic family brief](../d01_academic_buildings.md). No district, road or registry files changed.

## Design and provisional dimensions

An original compact single-storey campus annex: brick walls, pale-stone paired-light windows,
a four-slope hipped slate roof with a short field-green ridge, and a shallow green/pale pediment
over a **closed** amber paired door. Two restrained mint strips identify the occupied entrance.
The nearly square hipped roof is deliberately lower and quieter than the
[main hall's U-shaped court and clock tower](d01_academic_buildings_01.md) and the
[long teaching wing's ridge and cross-gable](d01_academic_buildings_02.md). This is a distinct
building silhouette, not a scaled/recoloured wing. No text or scattered roof fittings.

References inspected: [Northpoint revision 03](../../concepts/districts-v1/01-northpoint-v03.png),
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[selected map measurements](../../concepts/districts-v1/map-context.md#district-01), and both
academic sibling handoffs and the teaching wing's source recipe, materials, prefab and renders.
The 14 × 12 m neutral annex footprint reference informs this compact scale but is not an
approved parcel or replacement quota. No saved greybox or world instance was replaced.

Dimensions below are **provisional authored choices**, permitted by the production brief's
standing dimension rule, not measurements inferred from generated imagery.

| Contract | Metres, Godot local axes |
| --- | --- |
| Whole visual size X / Y / Z | 15.200 × 8.230 × 13.200 |
| Visual AABB minimum | (-7.600, 0, -6.600) |
| Visual AABB maximum | (7.600, 8.230, 6.600) |
| Brick wall volume | 14 × 4.8 × 12; centre (0, 2.65, 0), base Y=.25 |
| Ground plinth | 14.4 × .5 × 12.4; centre (0, .25, 0) |
| Hipped roof plan / eave / ridge | 15.2 × 13.2; Y=5.3 / 8.15; cap top Y=8.23 |
| Short ridge | Along Z, from -2.6 to +2.6; .24 wide |
| Blind entry pediment | 3.7 wide; base Y=4.1, apex Y=5.05, below eaves |
| Closed door / pull face | Door 2.9 wide × 3.8 high; foremost pull Z=-6.2625 |
| Ground / pivot | (0,0,0), centre of rectangular ground footprint |
| Orientation | Entrance faces -Z; Blender +Y → Godot -Z |
| Numerical envelope tolerance | ±.001; independent source/GLB/import bounds checks |

No interior, working door, passage, porch, stairs, ramp, rooftop access, destruction state or
animation is implied. The .5 m plinth remains the solid building base, visible across the bottom
of the closed doorway; it is not a walkable entry step. No ground/paving is exported; the evidence
floor is studio-only. Placement supplies flat terrain and preserves campus roads, open courts,
sports grounds and coastal boardwalk. The annex does not allocate a site inside the district.

## Source, exports and materials

- Source: `art/source/models/environment/d01_academic_buildings_03/d01_academic_buildings_03.blend`.
- Collection: `export_d01_academic_buildings_03`; root `D01AcademicBuildings03`;
  child `D01AcademicBuildings03_Mesh`, mesh data `D01AcademicBuildings03_Geometry`.
- Export: `art/models/environment/d01_academic_buildings_03/d01_academic_buildings_03.glb`
  and its engine-generated `.import` sidecar.
- Prefab: `scenes/prefabs/environment/d01_academic_buildings_03.tscn`.
- Reproducible authoring/export/validation: `tools/asset_production/d01_academic_buildings_03/`.

Original Blender construction only; no downloads, brands, fonts, image-to-mesh or external
textures. Metric units, applied transforms, identity root/mesh, ground-centred pivot. One joined
mesh batches closed architectural components into eight material surfaces. Internal intersections
are intentional, not a Boolean-unioned shell; non-manifold checks apply to the closed components.
Small single-segment bevels and weighted normals preserve the family's smooth edges and broad
planar roof highlights. Studio cameras, ground and lights remain outside the export collection.

Material order and exact PBR values match the corresponding hall and teaching-wing slots:
`academic_base_stone`, `academic_brick`, `academic_pale_stone`, `academic_field_green`,
`academic_slate_roof`, `academic_opaque_glass`, `academic_occupied_amber`,
`academic_wayfinding_mint`. The hall-only clock material is absent. All are opaque, back-culled
Principled surfaces. No emission, real lights, embedded images or overrides. The validation
receipt records exact linear colors, metallic and roughness; the recorder independently compares
the complete material records with the teaching wing's retained receipt. These local embedded
GLB materials preserve family treatment without creating a new shared material API.
Sockets, rigs, clips and textures: not applicable to this static intact exterior.

Pinned Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. The export script
uses `tools/assets/blender/export_settings.json`, named-collection filtering and static
animation/skin exclusions. Godot **4.8.dev7.official.c971f93e7** imports at scale 1 with normal
generated-LOD/shadow-mesh defaults. No explicit LODs or target-device budget are claimed accepted.

## Prefab and collision

`Visuals/Model` is an identity-transform linked GLB instance, not copied render geometry.
The wrapper has an engine-generated UID and saved node identities. `Collision/Body` is one
StaticBody3D on world layer 1, mask 0, with exactly one direct BoxShape3D child:

| Child | Size X / Y / Z | Centre |
| --- | --- | --- |
| AnnexSolid | (14.4, 5.3, 12.5) | (0, 2.65, -.05) |

The box covers the rectangular plinth and closed door without window/trim snag shapes.
Its X faces are ±7.2, rear Z=6.2, front Z=-6.3. The front is deliberately .10 m beyond the
plinth to cover the door/pulls, only .0375 m beyond the foremost pull. There is no entrance
void or angled footprint requiring a convex approximation. Roof/eaves are above-head decoration
and do not expand walking collision. No walkable roof is promised.

Per the mandated headless-only workflow, direct scene text was followed by isolated pinned
headless-editor load/pack/save/reload. No live Blender/Godot editor or owner's MCP session was
accessed. The second save preserved exact bytes and saved identities; fresh runtime checks
resolve the same prefab/model UIDs and linked ancestry. The custom editor SceneTree exits 0
with valid resource assertions but reports scan-thread/RID/ObjectDB shutdown diagnostics,
retained in `validation.json` and `final.log`; it is **not** claimed as a clean-log editor pass.
Both runtime checks and the final import are free of ERROR/SCRIPT ERROR lines. Runtime checks
are read-only; normalization requires `--editor` to preserve UIDs on this pin.

## Evidence and validation

[Hero](d01_academic_buildings_03-evidence/hero.png) ·
[Rear and side](d01_academic_buildings_03-evidence/side.png) ·
[Closed entrance detail](d01_academic_buildings_03-evidence/entrance_detail.png) ·
[47 m / 42° overhead](d01_academic_buildings_03-evidence/overhead_47m_42deg.png).
All four final images were inspected. Hero/rear/detail are 1120×630, overhead 1280×720;
RGB8 PNG compression 95, no post-processing, Cycles CPU 32 samples, AgX. Each is under 400 KiB.
The overhead is true vertical-down perspective, Blender +Y at image top, position (0,0,47),
42° vertical FOV. The whole compact hipped roof fits the frame: four broad planes and a short
green ridge distinguish the silhouette without signs. Hero and detail show the ordered paired
windows and closed portal. Initial detail review found dark specks where transom/mullion faces
were coplanar; a .025 m transom depth separation resolved them. Source, export and all four
renders were regenerated and checked. These are isolated Blender renders, not populated Godot
lighting or actor-visibility acceptance.

[validation.json](d01_academic_buildings_03-evidence/validation.json) combines source, export and
engine observations. [manifest.json](d01_academic_buildings_03-evidence/manifest.json) hashes all
produced payloads except itself. [final.log](d01_academic_buildings_03-evidence/final.log) retains
the concise final check summary and exact editor shutdown diagnostic lines.

- **3,596 triangles; 1,966 source vertices; 2,716 GLB vertices including surface splits.**
- **One mesh, eight surfaces; zero source degenerate faces/non-manifold edges;
  zero GLB degenerate triangles.** Source/export unit normals pass within .0001.
- Final GLB **116,200 bytes**, SHA-256
  `960ea64e0993901cc64ec7dc7798e3a3d2b397da8a5311290c275e6bf417e2a3`.
  Fresh export from the saved source is byte-identical.
- Final pinned import: exit 0, no ERROR/SCRIPT ERROR lines; prefab dependencies resolve.
- Thirteen independent shape expectations cover the solid centre/door, four corners,
  clear perimeter approaches and above-head decoration. Front ray hits Z=-6.30000.
- Production `ActorMotion.step`, capsule radius .35 m / height 1.8 m: closed entrance stop
  Z=-6.66667, east wall stop X=7.55079, clear rear bypass moves from X=-6 to X=6.00000.
  AUTHORITY and REPLAY agree exactly; two fresh processes produce identical receipts.
  This is bounded production-API physics evidence, **not transport or car-handling acceptance**.
- Owned GDScript format and zero-warning lint pass. No `production_checks.py` invocation.

## Reproduction

Run from the repository root in Bash. Scratch outputs/raw logs stay outside the checkout.
The final `record.py` command runs after the last receipt-producing checks and handoff edits.

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/d01_academic_buildings_03
S=C:/tmp/ft/assets/d01_academic_buildings_03
mkdir -p "$S"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py" > "$S/author.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" > "$S/validate.log" 2>&1
mise exec -- gdstyle fmt --check "$T/check_prefab.gd" > "$S/format.log" 2>&1
mise exec -- gdstyle --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd" > "$S/style.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-initial.log" 2>&1
timeout 180 "$G" --headless --editor --path . --script "$T/check_prefab.gd" -- \
  --normalize --output "$S/roundtrip.json" > "$S/roundtrip.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" -- \
  --output "$S/prefab-check.json" > "$S/prefab-check.log" 2>&1
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" -- \
  --output "$S/prefab-second-process.json" > "$S/prefab-second-process.log" 2>&1
python "$T/record.py"
```

`export.py` also accepts an external output directory after `--` when invoked against the saved
`.blend`; `validate.py` already opens that source and performs the scratch export/byte comparison.
No shared generic building-authoring library exists; local recipes/checks follow the academic
siblings' construction and validation conventions and reuse the shared export-settings contract.
Neither sibling handoff lists the annex as pending, so no sibling doc/manifest edit was necessary.

## Remaining acceptance

Independent technical/art review; owner selection of provisional dimensions and map fit;
saved district placement preserving roads, sports grounds, boardwalk and open courts;
populated Godot gameplay-camera/roof-occlusion views; car approaches and handling;
real-process network/admission/prediction checks; imported LOD/package review and sustained
Deck/performance profiling. No world placements, registry readiness, global settings,
shared briefs or TODO completion are claimed.
