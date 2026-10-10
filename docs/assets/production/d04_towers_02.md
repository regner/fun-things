# d04_towers.02 — Chamfered-crown tower

**Source/export, linked prefab and bounded headless checks delivered; independent review,
world placement and gameplay/device acceptance pending.** Production is commissioned under
the [commission](commission.md) and standing asset-production brief. Producer: isolated
asset-production worker; accepting owners: supervising art/technical/gameplay reviewers.
The producer does not self-approve downstream acceptance.

References: [tower family](../d04_towers.md),
[Glassward breakdown](../../concepts/districts-v1/glassward-assets.md),
[liked district concept](../../concepts/districts-v1/glassward.md),
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[gridded downtown streets](../../concepts/world-v1/stage-04-streets/README.md),
[first sibling](d04_towers_01.md).

## Design and dimensions

A conventional indigo office tower with a **four-corner-chamfered cyan crown**. A continuous
closed eight-sided rim surrounds a quiet recessed roof, with broad diagonal cuts rather than
small decorative bevels doing the silhouette work. The rectangular shaft keeps the first
sibling's broad three-floor window groups, restrained grey-blue piers, closed six-metre lobby
and one small magenta entrance lintel. No lettering or real brand is introduced. Fifteen
floors make this member 10.8 m taller than the rectangular-crown sibling.

These are **provisional authored proposals**, permitted by the standing production brief,
not measurements inferred from imagery or accepted parcel/clearance dimensions. Godot axes:
X width / Y height / Z depth. Metre-space acceptance tolerance: ±0.001 m.

| Contract | Provisional value |
| --- | --- |
| Ground/lobby footprint | 24 × 18 m, 432 m²; ground at Y=0 |
| Lobby | Y=0–6 m, closed exterior; no enterable door or interior |
| Shaft | 22 × 16 m plan; Y=6–60 m |
| Floor rhythm | 15 floors at 3.6 m; five broad 10.8 m three-floor groups |
| Crown interface | Centred horizontal 22 × 16 m rectangular seat at Y=60 m |
| Seat collar | 22 × 16 m, Y=60–60.3 m |
| Chamfered drum | 23.2 × 17.2 m plan, 3.4 m corner cuts; Y=60.3–63.95 m |
| Cyan rim | 24 × 18 m plan, 3.8 m cuts at all four corners; Y=63.9–64.8 m |
| Rim width | 1 m perpendicular inset on straight and diagonal edges; 0.04 m soft bevel |
| Overall height | **64.8 m**, 17.8 m above the provisional gameplay camera |
| Entry canopy | 6 × 1.7 m; front Z=-10.2 m; minimum soffit Y=3.56 m |
| Whole visual AABB | min (-12,0,-10.2), max (12,64.8,9) m |
| Whole visual size | 24 × 64.8 × 19.2 m, including the front canopy |
| Pivot/front | Ground-centred (0,0,0); front Godot -Z / Blender +Y |

The rim's plan boundary is |X|≤12, |Z|≤9 and |X|+|Z|≤17.2 m. Its four diagonal
segments are about 5.37 m long before edge bevels. These cuts are independently checked in
the validator, not merely inferred from the overall bounding box. The drum is one closed
prism; the rim is one closed annular prism, avoiding overlapping mitre-piece seams. Small
rectangular shaft shoulders remain visible below the clipped crown corners by design.

### Family compatibility and scope

The first sibling's 6 m lobby, 3.6 m floor pitch, opaque palette, three-floor grouping and
horizontal crown-seat convention are retained. Its lobby recipe is reused in this original
Blender construction; no imported mesh bytes are copied into a scene. Source sections remain
separately editable as `lobby()`, `facade()` and `crown()`. Both members have a 22 × 16 m seat,
but at different heights; these are design datums, **not** a runtime interchangeable-crown API
or procedural building generator. The distinct crown and height are geometry, not a recolor.

No podium, paving, forecourt platform, fixtures, roof machinery or placement is included.
The 432 m² footprint is not a whole-block allocation. Layout must retain important open
forecourt space and an unequal skyline. The first sibling's current Remaining acceptance
section contained no stale item specifically awaiting `.02`; no sibling file was changed.

## Source, export and materials

- Source: `art/source/models/environment/d04_towers_02/d04_towers_02.blend`.
- Collection: `export_d04_towers_02`; root: `D04Towers02`.
- Editable meshes: `D04Towers02_Lobby`, `D04Towers02_Facade`, `D04Towers02_Crown`.
- Export: `art/models/environment/d04_towers_02/d04_towers_02.glb` and its pinned-engine
  `.import` sidecar. The source remains excluded from Godot by the existing source `.gdignore`.
- Prefab: `scenes/prefabs/environment/d04_towers_02.tscn`.
- Tools: `tools/asset_production/d04_towers_02/{author,export,validate,record}.py`,
  `check_prefab.gd` and its engine-generated `.uid`.

Original Blender construction only: no downloads, purchased assets, image-to-mesh, fonts,
textures, external material dependencies or runtime render geometry. Studio plane, camera
and lighting stay outside the export collection. Metric units, scale length 1; root and
all meshes have zero location/rotation, unit scale, ground-origin pivots and no remaining
modifiers. Blender +Z → Godot +Y and Blender +Y → Godot -Z exactly once through glTF export.

Seven opaque, back-culled Principled materials, with the same names and values as `.01`:

| Material | Role |
| --- | --- |
| `glassward_indigo` | Main mass, quiet roof and spandrels |
| `glassward_frame` | Vertical piers, seat collar, lobby fascia/canopy |
| `glassward_glazing_opaque` | Broad opaque window groups and closed door faces |
| `glassward_glazing_highlight` | Two restrained broad window variations |
| `glassward_crown_cyan` | Chamfered rim; emission strength 0.35 |
| `glassward_accent_magenta` | One small entrance lintel; emission strength 0.12 |
| `glassward_lobby_stone` | Base shoe, lobby piers and canopy soffit |

Actual per-section slot order and PBR values are in `validation.json`: crown 3 surfaces,
facade 4, lobby 5. Emission is appearance-only, with no real lights or reliance on bloom.
No rig, animation, sockets, destruction state, interior, rooftop route or external material
remap is required. Default automatic Godot LOD/shadow-mesh generation is retained; no manual
LOD or unmeasured performance optimization is added.

## Prefab and collision

`Visuals/Model` is an identity-transform linked GLB instance with no editable-child overrides
or embedded render mesh data. `Collision/Body` is one static world body, layer 1 / mask 0,
with a minimal two-box compound:

- `Lobby`: size (24,6,18), centre (0,3,0); Y=0–6 m.
- `Shaft`: size (22,54,16), centre (0,33,0); Y=6–60 m.

These boxes fill only the inaccessible rectangular lobby/shaft, touching without a gap and
preserving the setback. Closed door faces block entry. The small visual bevels do not create
snag colliders. **The crown above Y=60 m is overhead visual-only**, as permitted by the standing
collision rule. Its clipped corners are not filled by an oversized box. The canopy is also
overhead decoration, with 3.56 m minimum clearance above ground. There is no rooftop gameplay
or collision promise for projectiles/actors above the shaft cap.

Two complete load/pack/save roundtrips after initial normalization preserved exact prefab
bytes, including node identities and scene UID. The scene UID is stored internally in the
`.tscn`; GDScript retains its required `.uid`. Fresh-process checks resolve prefab/model UIDs,
linked ancestry, bounds, material surfaces and the intentional compound. Authorized direct
text authoring followed by headless normalization was used because the commission prohibits
live editor access and the windowed editor is unavailable. No live scene is claimed synchronized.

## Evidence and validation

[Hero](d04_towers_02-evidence/hero.png) · [side](d04_towers_02-evidence/side.png) ·
[crown detail](d04_towers_02-evidence/crown_detail.png) ·
[47 m / 42° gameplay camera](d04_towers_02-evidence/overhead_47m_42deg.png).

All four final images were inspected by the producer. Supporting views are 1152×648;
overhead is 1280×720 under the lean-evidence rule. Blender Cycles CPU, 32 samples, AgX,
broad studio fill; RGB evidence is reduced to 7 bits/channel and PNG compression level 9.
Hero and side show the full-height silhouette. The detail makes the four broad corner cuts,
continuous rim and quiet roof legible. No extra rooftop props were needed.

The gameplay camera is vertical-down, north-up, **42° vertical FOV**, at Godot (18,47,-16)
relative to the pivot: the same off-footprint forecourt vantage as `.01`. The crown is above
this camera and **does not appear**. The lower facade projects/crops at the frame edge while
open ground stays visible. This is an honest camera constraint, not a full-building overview,
cutaway, engine capture, placement acceptance or proof of actor/target readability. No object
was hidden, rescaled or camera treatment added to conceal the above-camera issue.

Final measurements: [validation.json](d04_towers_02-evidence/validation.json).
Full producer payload inventory: [manifest.json](d04_towers_02-evidence/manifest.json).
Concise command/diagnostic summary: [final.log](d04_towers_02-evidence/final.log).

- **10,136 source vertices; 19,556 triangles; 12,992 exported vertices including splits.**
- **3 meshes, 12 material surfaces, 7 unique materials.**
- Zero degenerate source faces, zero non-manifold source edges, zero degenerate GLB triangles.
  Closed overlapping architectural components are intentional; each component is manifold.
- Unit-length source and GLB normals; source/GLB/engine bounds meet the ±0.001 m contract.
- Fresh reexport from the saved source is byte-identical: **543,640 bytes**, SHA-256
  `1da77ccfd89f40d84d513ba841c52d31249be72ac02ed4fe1c100147b4303704`.
- Pinned headless imports pass without ERROR/SCRIPT ERROR lines; linked prefab dependency,
  material, transform, bound, collision and UID checks pass in a fresh process.
- **16 shape queries** verify closed lobby, corner coverage, setback, section join, solid
  shaft above the camera, clear walking edges and intentionally nonblocking crown/canopy.
- **7 actor/car envelope casts**: front/rear/end actor and front car blocked; actor side,
  under-canopy and car side bypass clear. Front ray hits Z=-9 m. Capsule r=0.35 m, h=1.8 m;
  test car box 1.8×1.5×4.4 m. These use Godot physics APIs, not production controllers or networking.
- Owned GDScript formatting/lint passes. The global production suite was not run (decision 52).

Toolchain: Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**;
Godot **4.8.dev7.official.c971f93e7**; gdstyle **0.3.0**. Blender's `use_nodes` future-6.0
deprecation and the existing MCP Godot-4.8 compatibility warning are classified in the concise
log, not broadly suppressed. Raw scratch logs/byte-comparison output remain outside the repo.

## Exact reproduction

From repository root in Git Bash, without accessing live editor sessions:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_towers_02/author.py
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_towers_02/validate.py
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_towers_02/check_prefab.gd -- --normalize
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_towers_02/check_prefab.gd -- --output C:/tmp/ft/assets/d04_towers_02/prefab-fresh-final.json
timeout 60 "$(mise which gdstyle)" fmt --check tools/asset_production/d04_towers_02/check_prefab.gd
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 tools/asset_production/d04_towers_02/check_prefab.gd
python tools/asset_production/d04_towers_02/record.py --compress-renders
```

The validator invokes `export.py` using the shared `tools/assets/blender/export_settings.json`
with the named collection and animation/skin export disabled. Scratch reexport goes to
`C:/tmp/ft/assets/d04_towers_02/reexport/`. `record.py` verifies final receipts/GLB bytes,
packages lean evidence and regenerates the manifest last. Reinspect rendered outputs after
reproduction; packaging does not replace visual review.

## Remaining acceptance

- Supervising art/technical reviewers: independent exact-commit review and final dimensions.
- Layout/gameplay owners: compose the unequal skyline around important open forecourt space;
  check actual actor/car clearance and populated-city sightlines. No world placement was authored.
- Render/integration owners: actual engine material/normal/LOD views, shadow fill, tower clipping
  and actor/target visibility under the fixed camera. No cutaway/occlusion system was added.
- Gameplay/network owners: production controller handling, authoritative/predicted collision,
  real separate-process multiplayer and each platform transport.
- Performance/build owners: repeated-placement draw calls, LOD transitions, sustained Deck
  LCD/OLED frame pacing and packaged dependencies. Headless success is not device acceptance.

No register, shared brief, TODO, progress, gameplay rule or world scene was changed. This
bounded asset delivery is not a claim that downstream full game-ready acceptance is complete.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
