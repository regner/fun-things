# d01_sports_pavilion.01 — Crescent sports pavilion

**Source/export and linked prefab delivered; independent review and placement acceptance pending.**
Produced by the commissioned isolated asset-production worker on `lane/a-d01`, 10 October 2026.
Regner owns design selection; the production supervisor owns independent review and integration.
The [commission](commission.md) and current production brief supersede the concept-only status in
[the pavilion family brief](../d01_sports_pavilion.md). No earlier sports-family asset existed in
this lane. No district, road, registry, shared brief or gameplay code was changed.

## Design and provisional dimensions

An original low crescent pavilion, not an enclosed arena or tower: a broad, shallow-crowned slate
canopy, field-green curved fascias, pale soffit, two closed rear service wedges, and an **open,
column-free field-facing sheltered apron**. Two closed double service doors carry restrained mint
surrounds and amber vision panels. Broad clerestory windows and four quiet roof seams provide scale
without stadium seating, fine roof noise, signage copy or new sports equipment.

References inspected: [Northpoint revision 02](../../concepts/districts-v1/01-northpoint-v02.png),
[current district record](../../concepts/districts-v1/northpoint.md),
[approved identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and
[selected map fit](../../concepts/districts-v1/map-context.md#district-01).
The curved field-side landmark is retained. Dimensions below are **provisional authored choices**
under the standing dimension rule, not measurements inferred from generated imagery or accepted
plot allocations. Northpoint's roughly 80 × 45 m concept track is context, not a required mating
surface or regulation facility. This asset does not include the track, field, court or perimeter path.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Whole visual size X / Y / Z | 45.921665 × 6.555000 × 17.149256 |
| Visual AABB minimum | (-22.960833, 0, -8.568232) |
| Visual AABB maximum | (22.960833, 6.555000, 8.581024) |
| Main roof annulus | Radii 19 / 28; sweep -55° to +55°; 64 angular segments |
| Fascia extension | 0.03 beyond inner/outer soffit edges, avoiding coincident material faces |
| Main roof top / highest seam | Y=6.50 / 6.555 |
| Soffit underside | Y=5.50; no columns or lower overhead obstructions |
| Closed service masses | Two convex quadrilateral wedges, Y=0 to 5.65 |
| Service plan | Chords between radii 24 / 26, angles -50° / 0° / +50° |
| Sheltered depth | At least 2.75 between inner soffit edge and service wall chord before small relief |
| Ground / pivot | (0,0,0), roof-plan centre projected to ground, in the empty apron |
| Orientation | Open side faces -Z; Blender +Y → Godot -Z, Blender +Z → Godot +Y |
| Numerical envelope tolerance | ±0.001; collision/source corner comparison within 0.00001 |

The annulus centre is Blender (0, 19.448976145, 0), equivalent to Godot (0, 0, -19.448976145).
The pivot is not that construction centre. All roots/mesh objects use identity transforms and
metre units. The open apron continues onto world-supplied flat ground: **no floor/deck mesh,
raised threshold, step, ramp or paving collider** is exported. Roofs are inaccessible overhead
visuals, not a walkable deck. There are no interiors, working doors, rigs, animations, sockets,
destruction states, lights or gameplay interactions.

The slate, field-green, pale stone, mint and amber values intentionally match the neighbouring
[main academic hall](d01_academic_buildings_01.md) palette, with asset-specific material names.
The pavilion stays substantially lower and uses its curved roof rather than the hall's tower.
Sports artwork should retain the family brief's quiet green field, warm track and broad markings;
there is no new common surface API or fixed placement socket in this delivery.

## Source, export and materials

- Source: `art/source/models/environment/d01_sports_pavilion_01/d01_sports_pavilion_01.blend`.
- Collection: `export_d01_sports_pavilion_01`; root `D01SportsPavilion01`;
  child `D01SportsPavilion01_Mesh`, mesh data `D01SportsPavilion01_Geometry`.
- Export: `art/models/environment/d01_sports_pavilion_01/d01_sports_pavilion_01.glb`
  with the pinned engine's `.import` sidecar.
- Prefab: `scenes/prefabs/environment/d01_sports_pavilion_01.tscn`.
- Recipe and checks: `tools/asset_production/d01_sports_pavilion_01/`.

Original editable Blender construction only: no downloads, purchased/generated-source models,
image-to-mesh, real brands, external fonts or textures. One material-batched mesh contains closed
architectural components; touching/intersecting components are intentional, not a Boolean-unioned
watertight building. The topology receipt checks each closed component. Studio ground, lights and
camera remain outside the named export collection. No runtime-authored visible geometry.

Actual surface order: `pavilion_pale_stone`, `pavilion_base_stone`, `pavilion_field_green`,
`pavilion_opaque_glass`, `pavilion_wayfinding_mint`, `pavilion_occupied_amber`,
`pavilion_slate_roof`. All are opaque, back-culled Principled materials. Exact linear colors,
roughness and metallic values are in the author recipe and final validation receipt. No embedded
images, external material remaps, emission, separate textures or appearance overrides are needed.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. Export uses the shared
`tools/assets/blender/export_settings.json`, restricted to the named collection, static animations
and skins disabled. Godot **4.8.dev7.official.c971f93e7** imports at unit scale with its default
LOD/shadow-mesh generation. Imported LOD transitions and repeated-placement cost remain unprofiled;
no platform triangle/performance budget is claimed accepted.

## Prefab and collision

`Visuals/Model` is the identity-transform linked GLB instance, with no copied geometry or imported
child overrides. Saved scene/dependency UIDs and node identities are engine-generated.
`Collision/Body` is one StaticBody3D, world layer 1 / mask 0, with exactly **two** direct
ConvexPolygonShape3D children. Each is a documented four-point footprint extruded from Y=0 to 5.65:

| Child | Ordered ground vertices (X, Z), metres |
| --- | --- |
| WestServiceSolid | (-19.917156, -2.736498), (0, 6.551024), (0, 4.551024), (-18.385067, -4.022074) |
| EastServiceSolid | (0, 6.551024), (19.917156, -2.736498), (18.385067, -4.022074), (0, 4.551024) |

Each shape has eight points, below the twelve-point limit, authored from the dimensions rather
than from a visual mesh hull. The two pieces meet at X=0 over Z=4.551024 to 6.551024. Their corners
match the source service masses within 0.00001 m. **No convex hull spans the open crescent.**
Small window/door/pilaster relief remains decorative, extending at most 0.079 m past the wall;
it does not create snagging shapes. No rail or barrier is visible without collision. Overhead
roof/soffit/fascia are visual-only and do not expand the ground-level collision envelope.

Fifteen independently specified solid/clear overlap cases cover both pods, four outer corners,
the shared seam, both ends, the apron and overhead exclusion. Thirty-two face rays at two heights
check literal front/rear datums along both wedges. These plus source-to-collider corner matching
prove the intended footprint without corner gaps or invisible blockers across the open apron.
Production `ActorMotion.step` with capsule radius .35 / height 1.8 exercises the central seam,
slanted wall and clear front passage in AUTHORITY and REPLAY modes. These are bounded API/physics
checks, not whole-city car handling, transport or gameplay acceptance.

The authorized headless-only workflow used direct scene text followed by load/pack/save/reload.
No owner's live editor or MCP session was accessed. Two pack/save passes preserve exact bytes and
UIDs. Headless editor shutdown reports RID/ObjectDB leaks and a scan-abort warning despite exit 0
and passing assertions; these remain in the final log, **not a clean editor-log claim**. The final
headless import and both fresh runtime resource/physics checks have no ERROR/SCRIPT ERROR lines.

## Evidence and validation

[Hero](d01_sports_pavilion_01-evidence/hero.png) ·
[Side](d01_sports_pavilion_01-evidence/side.png) ·
[Entry detail](d01_sports_pavilion_01-evidence/entry_detail.png) ·
[47 m / 42° overhead](d01_sports_pavilion_01-evidence/overhead_47m_42deg.png).
All four final images were inspected. Each is 1280×720 RGB8 PNG, compression 95, below 400 KiB;
Cycles CPU 32 samples, AgX, no post-processing. The overhead uses true vertical-down perspective,
position Blender (0,0,47), 42° vertical FOV, +Y at image top. The **entire crescent fits** and reads
as a low quiet silhouette with an open field-side centre. Detail demonstrates closed service
leaves, not a traversable portal. Initial coplanar fascia/wall-band flicker was corrected before
these final renders. These are isolated Blender renders, not Godot lighting or actor visibility
acceptance; under-canopy visual occlusion remains a placement concern.

[validation.json](d01_sports_pavilion_01-evidence/validation.json) contains the final source/GLB,
engine, collision, render and style receipts. [manifest.json](d01_sports_pavilion_01-evidence/manifest.json)
hashes every produced payload except itself. [final.log](d01_sports_pavilion_01-evidence/final.log)
retains concise command outcomes, initial corrections and exact normalization diagnostics.

- **8,718 triangles; 4,499 Blender vertices; 5,395 GLB vertices including surface splits.**
- **One mesh, seven surfaces; zero source degenerate faces/non-manifold edges;
  zero GLB degenerate triangles.** Source/export unit normals pass within .0001.
- Final GLB **229,164 bytes**, SHA-256
  `df954b2962ef909ed392b1cde02d982854cc8114d63f21849a091314fa833c9e`.
  Fresh saved-source re-export is byte-identical.
- Pinned import exit 0, no ERROR/SCRIPT ERROR; fresh linked prefab loads without missing dependencies.
- Fifteen shape cases and thirty-two footprint face rays pass.
- Central seam stop Z=4.164165; 12 m clear-front traverse ends X=6.000005;
  slanted-wall motion ends (11.449283, .001000, -1.180985), preserving capsule clearance outside
  the wall while sliding toward the field. AUTHORITY and REPLAY match exactly.
- Two fresh runtime processes produce identical receipts. This is **not network transport proof**.
- Owned GDScript format and zero-warning lint pass. No `production_checks.py` invocation.

## Reproduction

From repository root in Bash. All calls are bounded; scratch files stay outside the checkout.
`validate.py` opens the saved source and re-exports to external scratch before byte comparison.
`export.py` also accepts an output directory after `--` when run against the saved `.blend`.
`record.py` must run after final checks and handoff edits so receipts and hashes remain current.

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/d01_sports_pavilion_01
S=C:/tmp/ft/assets/d01_sports_pavilion_01
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

## Remaining acceptance

Independent technical/art review; owner acceptance of provisional dimensions and sports plot fit;
saved world placement protecting the field and walking perimeter; populated Godot camera/lighting
and under-canopy occlusion review; car approaches and turning; actual multiplayer transport,
admission and prediction; imported LOD/package review and sustained Deck/performance checks.
No world placement, registry readiness, completed TODO or final gameplay/device acceptance is claimed.
