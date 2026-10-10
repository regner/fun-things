# d01_academic_buildings.01 — Main university hall with connected wings

**Source/export and linked prefab delivered; independent review and placement acceptance pending.**
Produced by the commissioned isolated asset-production worker on `lane/a-acad`.
Regner owns design selection; the production supervisor owns independent review and integration.
The [production commission](commission.md) supersedes the concept-only restriction in the
[academic family brief](../d01_academic_buildings.md). No district, road or registry files changed.
No earlier academic-family delivery existed in this lane.

## Design and provisional dimensions

An original two-storey brick-and-pale-stone collegiate hall: connected U-shaped wings,
ordered tall paired-light windows, pitched slate roofs, green gable fields and ridge caps,
a formal **closed** amber arched entrance, mint entry accents, and an integrated modest
clock tower with four static 10:10 faces. No text, downloaded geometry, fonts or textures.
The tower and both attached wings belong to this asset, not separate props.

References inspected: [Northpoint revision 03](../../concepts/districts-v1/01-northpoint-v03.png),
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and
[selected map measurements](../../concepts/districts-v1/map-context.md#district-01).
The roughly 45 × 50 m concept envelope is a visual proposal, not a measured allocation.
The authored dimensions below are **provisional**, chosen under the production brief's
standing dimension rule. They are not measurements inferred from generated imagery.

| Contract | Metres, Godot local axes |
| --- | --- |
| Whole visual size X / Y / Z | 45.200 × 21.000 × 41.365 |
| Visual AABB minimum | (-22.600, 0, -20.765) |
| Visual AABB maximum | (22.600, 21.000, 20.600) |
| Main wall bar | 44 × 10.5 × 12; centre X=0, Z=14; wall base Y=.25 |
| Each attached wing wall | 10 × 10.5 × 28; centre X=±17, Z=-6; wall base Y=.25 |
| Slate roof eave / ridge | Y=10.8 / 14.1; ridge cap top Y=14.18 |
| Tower cap apex | Y=21; tower centre X=0, Z=11.2 |
| Clear court between collision faces | 23.6 wide; open mouth Z=-20.2 to rear face Z=7.7 |
| Ground / pivot | (0,0,0), centre of U footprint, in the empty court |
| Orientation | Entrance and court mouth face -Z; Blender +Y → Godot -Z |
| Numerical envelope tolerance | ±.001; source/GLB coordinates checked independently |

No court paving or surrounding landscape is exported. The floor visible in the evidence is
studio-only. World placement supplies flat ground. No steps, ramps, rails, interior passage,
working door, animation, destruction state, rooftop access or elevated route is implied.
The arch is visibly filled with closed door leaves, not a traversable tunnel.

## Source, export and materials

- Source: `art/source/models/environment/d01_academic_buildings_01/d01_academic_buildings_01.blend`.
- Collection: `export_d01_academic_buildings_01`; root `D01AcademicBuildings01`;
  child `D01AcademicBuildings01_Mesh`, mesh data `D01AcademicBuildings01_Geometry`.
- Export: `art/models/environment/d01_academic_buildings_01/d01_academic_buildings_01.glb`
  and its engine-generated `.import` sidecar.
- Prefab: `scenes/prefabs/environment/d01_academic_buildings_01.tscn`.
- Recipe/checks: `tools/asset_production/d01_academic_buildings_01/`.

Original Blender construction only. Metric units, applied transforms, identity root and mesh,
no sockets, rigs or animation. One joined mesh batches closed architectural parts into nine
material surfaces; internal intersections are intentional, not a Boolean-unioned building.
Topology checks apply to the closed components. Cameras, studio ground and lights stay outside
its export collection. Sparse relief and single-segment micro-bevels preserve silhouette without
tile/brick texture noise. The tower cap has flat planar normals, avoiding a melted highlight.

Material order: `academic_base_stone`, `academic_brick`, `academic_pale_stone`,
`academic_field_green`, `academic_slate_roof`, `academic_opaque_glass`,
`academic_occupied_amber`, `academic_wayfinding_mint`, `academic_clock_ivory`.
All are opaque, back-culled Principled PBR materials. Exact linear colors, metallic and
roughness values are in the validation receipt and author recipe. No external/embedded images,
material overrides, emission or real lights. This establishes the academic-family material
spelling and low collegiate roof/window language; it does not create a new shared material API.

Pinned Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; export options
come from `tools/assets/blender/export_settings.json` with collection selection and static
animation/skin exclusions. Godot **4.8.dev7.official.c971f93e7** imports at unit scale with its
normal generated-LOD/shadow-mesh defaults. Imported LOD quality and repeated-instance cost
remain unprofiled; no triangle or target-device budget is claimed accepted.

## Prefab and collision

`Visuals/Model` is the identity-transform linked GLB instance, not copied render geometry.
The prefab has an engine-generated scene UID and saved node identities. `Collision/Body` is
one StaticBody3D on world layer 1, mask 0, with exactly three direct BoxShape3D children:

| Child | Size X / Y / Z | Centre |
| --- | --- | --- |
| MainHallSolid | (44.4, 10.8, 12.5) | (0, 5.4, 13.95) |
| WestWingSolid | (10.4, 10.8, 28.4) | (-17, 5.4, -6) |
| EastWingSolid | (10.4, 10.8, 28.4) | (17, 5.4, -6) |

The boxes follow ground plinths and the closed entrance, with overlapping hall/wing joints;
there is no collider spanning the court. Window framing and small plinth bevels do not add
snagging shapes. Roof eaves, pediments and tower are above-head decoration and do not expand
walking collision. The solid ground-level rectangles have no angled footprint corners.

The authorized headless-only workflow used direct scene text followed by pack/save/reload.
No live editor or owner's MCP session was accessed. Two headless-editor save/reload passes preserved
bytes and UIDs; fresh runtime loading verifies linked ancestry, bounds, materials and dependencies.
The pin's custom editor SceneTree reports RID/ObjectDB leaks on shutdown despite successful
resource assertions and exit 0; those diagnostics are retained, not called a clean-log pass.
Runtime-only ResourceSaver stripped UIDs after a cache refresh during an exploratory check.
The original generated UIDs were restored, editor-normalized and reimported. The checker now
rejects runtime normalization; final runtime checks are read-only and error-free.

## Evidence and validation

[Hero](d01_academic_buildings_01-evidence/hero.png) ·
[Side](d01_academic_buildings_01-evidence/side.png) ·
[Entrance and clock](d01_academic_buildings_01-evidence/entrance_clock_detail.png) ·
[47 m / 42° overhead](d01_academic_buildings_01-evidence/overhead_47m_42deg.png).
All four final images were inspected. Hero/side/detail are 1120×630, overhead 1280×720;
RGB8 PNG compression 95, no post-processing, Cycles CPU 32 samples, AgX.
The overhead is true vertical-down perspective, Blender +Y at image top, position (0,-3,47),
42° vertical FOV. It is an honest **local court crop**: the whole campus hall does not fit
inside that camera's vertical coverage. Hero establishes the complete U silhouette; overhead
shows the quiet roof margins and empty court. Clock-face detail is not essential overhead
information. These are isolated Blender renders, not Godot lighting/actor visibility acceptance.

[validation.json](d01_academic_buildings_01-evidence/validation.json) contains measured source,
GLB and engine receipts. [manifest.json](d01_academic_buildings_01-evidence/manifest.json) hashes
every produced payload except itself. [final.log](d01_academic_buildings_01-evidence/final.log)
summarizes final checks and explicitly retains initial diagnostic limitations.

- **28,758 triangles; 15,547 source vertices; 21,604 GLB vertices including surface splits.**
- **One mesh, nine surfaces; zero source degenerate faces/non-manifold edges;
  zero GLB degenerate triangles.** Unit source/export normals pass within .0001.
- Final GLB **872,500 bytes**, SHA-256
  `b6d851edea5418ff0938b84a5bfb664906701881be554fb0d05cfe34a6786522`.
  Fresh saved-source re-export is byte-identical.
- Final pinned import: exit 0, no ERROR or SCRIPT ERROR lines; asset load has no missing dependency.
- Thirteen independent shape expectations cover solids, both connection joints, corners,
  empty court/mouth, exterior clearance and above-head decoration. Court-to-door ray hits Z=7.7000.
- Production `ActorMotion.step`, capsule radius .35 m / height 1.8 m: closed entrance stop
  Z=7.33334, open-court traversal ends Z=-7.00001 after 12 m, wing stop X=11.44921.
  AUTHORITY and REPLAY results match exactly. Two fresh processes agree; this is bounded
  physics/API evidence, **not multiplayer transport or car handling acceptance**.
- Owned GDScript format and zero-warning lint pass. No `production_checks.py` invocation.

## Reproduction

Run from repository root in Bash; scratch stays outside the checkout. Every engine call is bounded.
The final `record.py` command runs after the final receipt-producing checks and handoff edits.

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/d01_academic_buildings_01
S=C:/tmp/ft/assets/d01_academic_buildings_01
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

`export.py` also accepts an external output-directory argument after `--` when run against the
saved `.blend`; `validate.py` already opens that source and performs this scratch export/compare.

## Remaining acceptance

Independent technical/art review; owner selection of provisional dimensions and map fit;
saved district placement that preserves roads, sports grounds and coastal boardwalk;
populated Godot gameplay-camera views and tower/roof occlusion; car approaches/turning;
real-process networking/admission/prediction; imported LOD/package review and sustained
Deck/performance profiling. No world placements, registry readiness, global settings,
shared briefs or TODO completion are claimed.
