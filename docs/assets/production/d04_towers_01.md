# d04_towers.01 — Rectangular-crown tower

**Source/export, linked prefab and bounded headless checks delivered; independent review,
world placement and gameplay/device acceptance pending.** Commissioned production supersedes
this family's earlier concept-only status. Producer: isolated asset-production worker;
acceptance owner: supervising production/art/technical reviewers, not the producer.

References: [commission](commission.md), [tower family](../d04_towers.md),
[Glassward breakdown](../../concepts/districts-v1/glassward-assets.md),
[liked district concept](../../concepts/districts-v1/glassward.md),
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[gridded downtown streets](../../concepts/world-v1/stage-04-streets/README.md).

## Design and dimensions

An original conventional office tower with a **rectangular cyan crown**, indigo mass,
restrained grey-blue vertical framing, broad three-floor glazing groups and a six-metre
closed lobby. A single small magenta entry lintel accents the front; it is architectural
color, not corporate artwork or an invented brand. The roof is a quiet recessed rectangle,
without duplicated vents, plant enclosures or other shared-family hardware. Smooth bevels
and weighted normals keep the ordinary architecture legible without dense fine detail.

All dimensions below are **provisional authored proposals**, permitted by the standing
production brief, not measurements inferred from concept imagery or approved parcel sizes.
Metre-space acceptance tolerance is ±0.001 m. Godot dimensions are X width / Y height / Z depth.

| Contract | Provisional value |
| --- | --- |
| Ground/lobby footprint | 24 × 18 m; 432 m², ground at Y=0 |
| Lobby height | 6 m, closed exterior, no enterable doorway |
| Tower shaft | 22 × 16 m plan, Y=6 to 49.2 m |
| Floor rhythm | 12 floors at 3.6 m pitch; four broad 10.8 m three-floor groups |
| Crown interface | Horizontal seat at Y=49.2 m, centred 22 × 16 m shaft envelope |
| Crown envelope | 22.8 × 16.8 m plan, Y=49.2 to 54 m |
| Overall height | **54 m**, 7 m above the provisional gameplay camera |
| Crown cyan rim | 0.8 m broad, Y=53.1 to 54 m; rectangular, not chamfered/rounded |
| Entry canopy | 6 × 1.7 m plan; front reaches Z=-10.2 m; lowest soffit Y=3.56 m |
| Whole visual AABB | min (-12, 0, -10.2), max (12, 54, 9) m |
| Whole visual size | 24 × 54 × 19.2 m, including front canopy |
| Pivot/front | Ground-centred footprint (0,0,0); front Godot -Z / Blender +Y |

Blender metric units, scale length 1. Root and all three mesh sections have zero translation
and rotation, unit scale and no remaining modifiers. Axis conversion occurs once in glTF:
Blender +Z → Godot +Y, Blender +Y → Godot -Z. No compensating prefab scale/rotation.

### Family handoff

This is the first delivered sibling. `author.py` has explicit `lobby()`, `facade()` and
`crown()` sections; the saved source retains them as separately named editable meshes.
The 6 m lobby, 3.6 m floor pitch, three-floor grouping, opaque indigo/glazing palette and
horizontal crown-seat convention are the baseline vocabulary for `.02–.04`. The 22 × 16 m
seat applies to this rectangular member; different silhouette footprints must document their
own seats rather than silently rescaling this model. Datums describe design compatibility,
not an API promising arbitrary mix-and-match crowns. Each later member remains a separate
saved original model and export. No runtime generator, new kit dependency or extra variant.

No podium, paving, raised forecourt, plants, road surfaces or placement is included. The
432 m² footprint is not a whole-block allocation. Layout must keep the three unequal crowns
around **important open ground**; this single asset does not establish that composition.

## Source, export and materials

- Source: `art/source/models/environment/d04_towers_01/d04_towers_01.blend`.
- Export collection: `export_d04_towers_01`; root: `D04Towers01`.
- Editable children: `D04Towers01_Lobby`, `D04Towers01_Facade`, `D04Towers01_Crown`.
  All are ground-origin meshes; their actual vertex extents define the section datums.
- Explicit output: `art/models/environment/d04_towers_01/d04_towers_01.glb`, plus its
  pinned-engine `.import` sidecar. No source asset references `prototypes/`.
- Tools: `tools/asset_production/d04_towers_01/{author,export,validate,record}.py` and
  `check_prefab.gd` with its generated `.uid`.
- Prefab: `scenes/prefabs/environment/d04_towers_01.tscn`.

Original Blender construction; no downloads, purchased models, image-to-mesh, textures,
fonts, real brands or runtime render geometry. Studio plane/lights/camera are outside the
export collection. Closed overlapping decorative components are intentional, not Boolean
union topology; each component is manifold. No rig, animation, sockets, destruction state,
interior, elevator, rooftop route, external material remap or texture dependency is requested.

Seven opaque, back-culled Principled materials (no embedded images):

| Material | Role |
| --- | --- |
| `glassward_indigo` | Main mass, sparse spandrels, quiet roof |
| `glassward_frame` | Vertical framing, collar, lobby fascia/canopy |
| `glassward_glazing_opaque` | Broad nontransparent window groups and closed doors |
| `glassward_glazing_highlight` | Only two restrained broad facade variations |
| `glassward_crown_cyan` | Rectangular rim, emission strength 0.35 |
| `glassward_accent_magenta` | One small front lintel, emission strength 0.12 |
| `glassward_lobby_stone` | Ground shoe, lobby piers and canopy soffit |

Actual per-section slot order and PBR values are in `validation.json`. Crown: 3 surfaces;
facade: 4; lobby: 5. Shared names/colors are a sibling vocabulary, not global material assets.
Emission is appearance-only, with no real lights or bloom-dependent detail. Import retains
default automatic LOD and shadow-mesh generation; visual LOD transitions and repeat cost are
not accepted by headless import. No manual LOD is added without a measured need.

## Prefab and collision

`Visuals/Model` is the identity-transform linked GLB instance, not editable copied geometry.
`Collision/Body` is one `StaticBody3D`, layer 1 / mask 0, with the minimal two-box compound:

- `Lobby`: size (24,6,18), centre (0,3,0), spanning Y=0–6.
- `Shaft`: size (22,48,16), centre (0,30,0), spanning Y=6–54.

The boxes intentionally fill the inaccessible building interior and touch without a gap.
They preserve the lobby-to-shaft setback and block the closed doors, full-height tower,
actor and car paths. Small bevels/flush trim do not add snag shapes. The crown collar/rim's
0.4 m plan overhang and canopy are overhead visual decoration. The canopy has **3.56 m**
minimum ground clearance and does not block a ground-level actor. There is no authored
walkable rooftop or gameplay claim for the solid roof envelope.

Pinned Godot normalization followed by two complete save/reload roundtrips was byte-stable,
including node IDs and scene UID. A subsequent import/fresh process resolved both registered
prefab and GLB UIDs. `.tscn` stores its UID internally; the GDScript's required `.uid` is retained.
No external live editor was used or claimed synchronized; direct text authoring followed by
headless load/pack/save is the authorized fallback for this commission.

## Evidence and measured validation

[Hero](d04_towers_01-evidence/hero.png) · [side](d04_towers_01-evidence/side.png) ·
[crown detail](d04_towers_01-evidence/crown_detail.png) ·
[47 m / 42° gameplay camera](d04_towers_01-evidence/overhead_47m_42deg.png).

All four final images were inspected by the producer. Supporting images are 1152×648;
overhead is 1280×720 per the lean-evidence rule. Blender Cycles CPU, 32 samples, AgX,
broad studio fill; RGB evidence is reduced to 7 bits/channel and PNG compression level 9.
The hero was reframed after the first attempt clipped the top and foot. The final hero and
side show the full silhouette, and the detail shows the rectangular cyan rim and quiet roof.

The gameplay camera is vertical-down, north-up, 42° **vertical** FOV, at Godot (18,47,-16)
relative to this ground pivot: a labelled off-footprint forecourt vantage. The 54 m crown
is **above the camera and absent from this view**. The lower facade expands/crops at the
frame edge while the forecourt side stays open. This honestly records the above-camera
constraint: it is not a full-building overview, a cutaway, an engine capture or evidence
that targets remain visible. Nothing was hidden, scaled down or clipped by an added system.

Final measured receipt: [validation.json](d04_towers_01-evidence/validation.json).
Producer SHA-256 inventory: [manifest.json](d04_towers_01-evidence/manifest.json).
Concise command outcomes/diagnostics: [final.log](d04_towers_01-evidence/final.log).

- **8,680 source vertices, 16,728 triangles; 11,216 GLB vertices including splits.**
- **3 meshes, 12 material surfaces, 7 unique materials.**
- Zero degenerate source faces, zero non-manifold source edges, zero degenerate GLB triangles.
- Unit-length source/GLB normals; maximum GLB length error <0.000001.
- Source section bounds and actual GLB/Godot bounds meet the ±0.001 m literal contract.
- Fresh reexport from the saved `.blend` is byte-identical: **467,724 bytes**,
  SHA-256 `59a61f41b835e00976e495149ebff1e4200ecaf527d1422aa578bb80b6c49885`.
- Headless resource checks: linked ancestry, identity transform, three mesh sections,
  opaque/back-culled materials, bounds, collision and registered UIDs pass.
- Fourteen shape queries pass (closed lobby, corner coverage, setback, collision join,
  above-camera solid, clear walking edges and nonblocking overhead trim).
- Seven actor/car envelope casts pass: actor front/rear/end and car front blocked;
  actor side bypass, under-canopy bypass and car bypass clear. Actor capsule r=0.35 m,
  h=1.8 m; test car box 1.8×1.5×4.4 m. Front ray hits Z=-9 m.
  These use Godot physics APIs, **not** production-controller driving or network proof.
- Historical check completed before owner decision 52: **230 scripts compiled; 17/17 Python tests;
  165/165 GUT tests, 6,918 assertions; diagnostic negative control detected**.
  No known-failure exemptions were needed. This global suite is no longer required and must
  not be rerun for asset work. Current checks are pinned import, asset validation/byte-compare,
  prefab roundtrips, and owned gdstyle formatting/lint, all already passed.

Toolchain: Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**;
Godot **4.8.dev7.official.c971f93e7**; gdstyle **0.3.0**. Import's existing MCP 4.8
compatibility warning and Blender's `use_nodes` future-6.0 deprecation warnings are retained
in the concise log classification, not suppressed. Scratch logs are outside the repository.

## Exact reproduction

From the repository root in Git Bash. Owner decision 52 limits reproduction to these
asset-scoped checks; the earlier global suite result above is historical only:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_towers_01/author.py
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_towers_01/validate.py
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_towers_01/check_prefab.gd -- --normalize
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_towers_01/check_prefab.gd -- --output C:/tmp/ft/assets/d04_towers_01/prefab-fresh-final.json
timeout 60 "$(mise which gdstyle)" fmt --check tools/asset_production/d04_towers_01/check_prefab.gd
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 tools/asset_production/d04_towers_01/check_prefab.gd
python tools/asset_production/d04_towers_01/record.py --compress-renders
```

The validator loads the saved source and invokes `export.py` using the shared
`tools/assets/blender/export_settings.json`, with this collection and animation/skin export
explicitly disabled. Fresh comparison output goes to `C:/tmp/ft/assets/d04_towers_01/reexport/`.
`record.py` verifies asset-scoped receipts and GLB bytes, packages evidence and regenerates the
manifest last. It does not require or invoke the global suite. Reinspect rendered evidence after
reproduction; this tool does not replace visual review.

## Remaining acceptance

- Supervising art/technical reviewers: independent exact-commit review remains pending.
- Layout/gameplay owners: confirm provisional dimensions, compose the unequal skyline and
  important open forecourt without occupying routes; check walking/car clearance and
  populated-city sightlines from the **actual** fixed camera. No placement was authored.
- Integration/render owners: engine material/normal/LOD visual review, shadow fill,
  near/above-camera clipping and actor/target visibility. No cutaway/occlusion system added.
- Gameplay/network owners: production actor/car handling, authoritative/predicted collision,
  real separate-process multiplayer and platform transport checks.
- Performance/build owners: repeated placements, draw-call/LOD cost, sustained Deck LCD/OLED
  frame pacing and packaged dependency validation. Import success is not device acceptance.

No register, shared brief, TODO, progress, gameplay rule or world scene was changed, and no
full production-ready/placement acceptance is implied by these bounded checks.
