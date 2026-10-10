# d01_academic_buildings.02 — Long teaching wing

**Source/export and linked prefab delivered; independent review and placement acceptance pending.**
Produced by the commissioned isolated asset-production worker on `lane/a-acad`.
Regner owns design selection; the production supervisor owns technical/art review and integration.
The [production commission](commission.md) supersedes the concept-only restriction in the
[academic family brief](../d01_academic_buildings.md). No district, road or registry files changed.

## Design and provisional dimensions

An original separate two-storey teaching building: a long brick bar, pale-stone paired-light
windows, slate pitched roof, green end pediments and one central entrance cross-gable. A closed
amber paired door and two restrained mint strips mark the occupied entrance. No clock tower,
courtyard, text or scattered roof fittings: the roof silhouette differentiates this building from
[the main university hall](d01_academic_buildings_01.md) without competing with its landmark.
The connected wings in that hall remain part of `.01`; this is a standalone campus building.

References inspected: [Northpoint revision 03](../../concepts/districts-v1/01-northpoint-v03.png),
[approved identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[selected map measurements](../../concepts/districts-v1/map-context.md#district-01), and the
main hall's source, materials, prefab and renders. The straight narrow footprint keeps open
courts available to the district integrator; it does not claim an approved location or quota.

Dimensions below are **provisional authored choices**, permitted by the standing production
brief, not measurements inferred from generated imagery. The 20 × 14 m classroom greybox
reference is not an approved replacement envelope. This longer, narrower teaching-wing design
requires its own later map-fit review rather than rescaling an existing placed instance.

| Contract | Metres, Godot local axes |
| --- | --- |
| Whole visual size X / Y / Z | 37.440 × 12.330 × 11.345 |
| Visual AABB minimum | (-18.720, 0, -5.745) |
| Visual AABB maximum | (18.720, 12.330, 5.600) |
| Brick wall bar | 36 × 9 × 10; centre (0, 4.75, 0), base Y=.25 |
| Ground plinth | 36.4 × .5 × 10.4; centre (0, .25, 0) |
| Main roof plan / eave / ridge | 37.2 × 11.2; Y=9.5 / 12.25; cap top Y=12.33 |
| Central cross-gable roof | 6.4 wide; from Z=0 to -5.6; same ridge height |
| Closed doorway face | 3.1 wide × 4 high, from ground; outer pull face Z=-5.2625 |
| Ground / pivot | (0,0,0), centre of rectangular ground footprint |
| Orientation | Entrance faces -Z; long axis X; Blender +Y → Godot -Z |
| Numerical envelope tolerance | ±.001; independent source/GLB/import bounds checks |

No interior, working door, passage, porch, stairs, ramp, rooftop access, destruction state or
animation is implied. The raised plinth is part of a solid closed building, not a walkable step.
No ground or paving is exported; the evidence floor is studio-only. Placement supplies flat
terrain and keeps campus roads, sports grounds, boardwalk and walking courts unobstructed.

## Source, exports and materials

- Source: `art/source/models/environment/d01_academic_buildings_02/d01_academic_buildings_02.blend`.
- Collection: `export_d01_academic_buildings_02`; root `D01AcademicBuildings02`;
  child `D01AcademicBuildings02_Mesh`, mesh data `D01AcademicBuildings02_Geometry`.
- Export: `art/models/environment/d01_academic_buildings_02/d01_academic_buildings_02.glb`
  and its engine-generated `.import` sidecar.
- Prefab: `scenes/prefabs/environment/d01_academic_buildings_02.tscn`.
- Reproducible recipe and checks: `tools/asset_production/d01_academic_buildings_02/`.

Original Blender construction only; no downloads, generated image-to-mesh, brands, fonts or
external textures. Metre units, applied transforms, identity root/mesh and ground-centred pivot.
One joined mesh batches closed architectural components into eight material surfaces. Internal
intersections are intentional, not a Boolean-unioned shell; non-manifold checks apply to each
closed component. Small single-segment bevels and weighted normals preserve the smooth family
edge treatment. Studio cameras, ground and lights are outside the named export collection.

Material order and exact PBR values match the main hall's corresponding slots:
`academic_base_stone`, `academic_brick`, `academic_pale_stone`, `academic_field_green`,
`academic_slate_roof`, `academic_opaque_glass`, `academic_occupied_amber`,
`academic_wayfinding_mint`. The hall-only clock material is absent. All are opaque, back-culled
Principled PBR surfaces; no emission, real lights, embedded images or material overrides.
The validation receipt records exact linear colors, metallic and roughness. These local embedded
GLB materials preserve family spelling/treatment without adding a new shared material API.
Sockets, rigs, clips and textures: not applicable to this static intact exterior.

Pinned Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. The local export
entrypoint uses `tools/assets/blender/export_settings.json`, named-collection filtering and static
animation/skin exclusions. Godot **4.8.dev7.official.c971f93e7** imports at scale 1 with the normal
generated-LOD/shadow-mesh defaults. No explicit LODs or performance budget are claimed accepted.

## Prefab and collision

`Visuals/Model` is an identity-transform linked GLB instance, not copied render geometry.
The wrapper has an engine-generated UID and stable saved node identities. `Collision/Body` is
one StaticBody3D on world layer 1, mask 0, with exactly one direct BoxShape3D child:

| Child | Size X / Y / Z | Centre |
| --- | --- | --- |
| TeachingWingSolid | (36.4, 9.5, 10.5) | (0, 4.75, -.05) |

The box covers the rectangular plinth and closed doorway without window/trim snag shapes.
Its X faces are ±18.2, rear Z=5.2 and front Z=-5.3. The front is deliberately .10 m beyond the
plinth to cover the protruding door/pulls; it is only .0375 m beyond the foremost pull. There is
no entrance void and no angled footprint requiring a convex approximation. Roof/pediment
projection is above-head decoration and does not expand collision. No walkable roof is promised.

Per the headless-only commission, direct scene text was followed by pinned headless-editor
load/pack/save/reload. No live Blender/Godot editor or owner's MCP session was accessed. The
second save preserved bytes and therefore saved node identities; final runtime loading resolves
the same prefab/model UIDs and linked ancestry. The custom editor SceneTree exits 0 with valid
resource assertions but reports scan-thread/RID/ObjectDB shutdown diagnostics, retained in
`validation.json` and `final.log`; it is **not** claimed as a clean-log editor pass. Both runtime
checks and the final import are free of ERROR/SCRIPT ERROR lines. Runtime checks are read-only;
normalization explicitly requires `--editor` to preserve UIDs on this pin.

## Evidence and validation

[Hero](d01_academic_buildings_02-evidence/hero.png) ·
[Rear and end](d01_academic_buildings_02-evidence/side.png) ·
[Closed entrance detail](d01_academic_buildings_02-evidence/entrance_detail.png) ·
[47 m / 42° overhead](d01_academic_buildings_02-evidence/overhead_47m_42deg.png).
All four final images were inspected. Hero/rear/detail are 1120×630, overhead 1280×720;
RGB8 PNG compression 95, no post-processing, Cycles CPU 32 samples, AgX. Each is under 400 KiB.
The overhead is true vertical-down perspective, Blender +Y at image top, position (0,0,47),
42° vertical FOV. The whole roof fits the landscape frame; its long ridge and one entrance
cross-gable read without lettering. Hero and detail show ordered windows and the closed portal.
These are isolated Blender renders, not populated Godot lighting or actor-visibility acceptance.

[validation.json](d01_academic_buildings_02-evidence/validation.json) combines source, export and
engine observations. [manifest.json](d01_academic_buildings_02-evidence/manifest.json) hashes all
produced payloads except itself. [final.log](d01_academic_buildings_02-evidence/final.log) retains
the concise final check summary and exact editor shutdown diagnostic lines.

- **10,048 triangles; 5,488 source vertices; 7,561 GLB vertices including surface splits.**
- **One mesh, eight surfaces; zero source degenerate faces/non-manifold edges;
  zero GLB degenerate triangles.** Source/export unit normals pass within .0001.
- Final GLB **309,940 bytes**, SHA-256
  `2901a76608077accf0893734b87616da72c69bdef746aa7b728a663bd0b94f61`.
  Fresh export from the saved source is byte-identical.
- Final pinned import: exit 0, no ERROR/SCRIPT ERROR lines; prefab dependencies resolve.
- Thirteen independent shape expectations cover the solid centre/door, all four corners,
  clear perimeter approaches and above-head decoration. Front ray hits Z=-5.30000.
- Production `ActorMotion.step`, capsule radius .35 m / height 1.8 m: closed entrance stop
  Z=-5.66667, east wall stop X=18.55075, clear rear bypass moves from X=-6 to X=6.00000.
  AUTHORITY and REPLAY results agree exactly. Two fresh processes produce identical receipts.
  This is bounded production-API physics evidence, **not transport or car-handling acceptance**.
- Owned GDScript format and zero-warning lint pass after extracting collision inspection to
  resolve one local-variable-count warning. No `production_checks.py` invocation.

## Reproduction

Run from the repository root in Bash. Scratch outputs and raw logs stay outside the checkout.
The final `record.py` command runs after the last receipt-producing checks and handoff edits.

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/d01_academic_buildings_02
S=C:/tmp/ft/assets/d01_academic_buildings_02
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

`export.py` also accepts an external output-directory argument after `--` when invoked against
the saved `.blend`; `validate.py` already opens the source and performs this scratch byte-compare.
No shared generic building-authoring library exists; the local recipe/checks follow the earlier
hall's construction and validation conventions and use the shared export-settings contract.

## Remaining acceptance

Independent technical/art review; owner selection of provisional dimensions and map fit;
saved district placement preserving roads, sports grounds, boardwalk and open courts;
populated Godot gameplay-camera/roof-occlusion views; car approaches and handling;
real-process network/admission/prediction checks; imported LOD/package review and sustained
Deck/performance profiling. No world placements, registry readiness, global settings,
shared briefs or TODO completion are claimed.
