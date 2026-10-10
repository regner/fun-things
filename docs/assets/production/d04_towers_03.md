# d04_towers.03 — Rounded-crown tower

**Source/export, linked prefab and bounded headless checks delivered; independent review,
world placement and gameplay/device acceptance pending.** Production is commissioned by
Regner under the [commission](commission.md) and standing asset-production brief. Producer:
isolated asset-production worker. Accepting owners: supervising art/technical/gameplay
reviewers; the producer does not self-approve downstream acceptance.

References: [tower family](../d04_towers.md),
[Glassward breakdown](../../concepts/districts-v1/glassward-assets.md),
[liked district concept](../../concepts/districts-v1/glassward.md),
[approved district identity](../../concepts/world-v1/stage-03-district-identities/README.md),
[gridded downtown streets](../../concepts/world-v1/stage-04-streets/README.md),
[rectangular sibling](d04_towers_01.md), [chamfered sibling](d04_towers_02.md).

## Design and dimensions

A conventional indigo office tower with a **rounded-rectangle cyan crown**. Four broad
circular corners, not small edge bevels or diagonal cuts, establish its silhouette. A closed
rounded drum supports a continuous cyan rim around a quiet recessed roof. The nine-floor
shaft retains the siblings' broad three-floor glazing groups, grey-blue framing, six-metre
closed lobby and single small magenta entry lintel. No lettering or real brand is introduced.
At 43.2 m it is the near-camera member of the three unequal delivered crowns, below the
54 m rectangular and 64.8 m chamfered members. No separate low-office or podium asset is added.

All dimensions are **provisional authored proposals**, permitted by the standing production
brief, not measurements inferred from imagery or approved parcel sizes. Numerical tolerance:
±0.001 m. Godot axes below are X width / Y height / Z depth.

| Contract | Provisional value |
| --- | --- |
| Ground/lobby footprint | 24 × 18 m, 432 m²; Y=0 ground |
| Lobby | Y=0–6 m, closed exterior; no enterable door or interior |
| Shaft | 22 × 16 m plan, Y=6–38.4 m |
| Floor rhythm | 9 floors at 3.6 m; three broad 10.8 m three-floor groups |
| Crown interface | Centred horizontal 22 × 16 m rectangular seat at Y=38.4 m |
| Seat collar | 22 × 16 m, Y=38.4–38.7 m |
| Rounded drum | 23.2 × 17.2 m plan, 5.6 m corner radius; Y=38.7–42.35 m |
| Cyan rim | 24 × 18 m plan, 6 m outer / 5 m inner corner radii; Y=42.3–43.2 m |
| Rim width | 1 m on straight runs and radial corners; 0.04 m soft edge bevel |
| Overall height | **43.2 m**, 3.8 m below the provisional gameplay camera |
| Entry canopy | 6 × 1.7 m; front reaches Z=-10.2 m; minimum soffit Y=3.56 m |
| Whole visual AABB | min (-12,0,-10.2), max (12,43.2,9) m |
| Whole visual size | 24 × 43.2 × 19.2 m, including the front canopy |
| Pivot/front | Ground-centred (0,0,0); front Godot -Z / Blender +Y |

Outer rim corner centres are (X,Z)=(±6,±3) m. Each quarter circle has twelve segments;
the four straight runs join tangentially. Inner radii share those centres for a constant-width
band. The rim is one closed annular prism; the drum is one capped prism, without mitred-piece
seams. Small rectangular shaft/collar shoulders remain visible beneath the rounded corners
by design. Twenty independent support-plane checks distinguish the curves from a chamfer
that could otherwise pass the same AABB test.

### Family compatibility and scope

The 6 m lobby, 3.6 m floor pitch, three-floor grouping, seven-material opaque palette and
horizontal crown-seat convention retain the delivered family vocabulary. The owned Blender
recipe adapts the existing siblings' lobby/facade construction, retaining separately editable
`lobby()`, `facade()` and `crown()` sections. The 22 × 16 m seat is compatible in design scale,
not a runtime interchangeable-crown API: this member has its own documented seat height and
original source/export. No runtime generator, extra variant or shared-tool change is included.

No podium, paving, raised forecourt, fixtures, roof machinery, road surfaces or placement is
included. The 432 m² footprint is not a whole-block allocation. Layout must compose the
unequal skyline around **important open ground**. Neither earlier sibling's current Remaining
acceptance section contained a stale item awaiting `.03`; no sibling document or manifest
needed changing. Unproduced family members remain tracked by the registry, not this handoff.

## Source, export and materials

- Source: `art/source/models/environment/d04_towers_03/d04_towers_03.blend`.
- Export collection: `export_d04_towers_03`; root: `D04Towers03`.
- Editable meshes: `D04Towers03_Lobby`, `D04Towers03_Facade`, `D04Towers03_Crown`.
- Explicit export: `art/models/environment/d04_towers_03/d04_towers_03.glb`, with its
  pinned-engine `.import` sidecar. The existing source `.gdignore` excludes the `.blend`.
- Prefab: `scenes/prefabs/environment/d04_towers_03.tscn`.
- Tools: `tools/asset_production/d04_towers_03/{author,export,validate,record}.py`,
  `check_prefab.gd` and its engine-generated `.uid`.

Original Blender construction only: no downloads, purchased assets, image-to-mesh, fonts,
textures, external material dependencies or runtime render geometry. Studio plane, camera
and lights stay outside the export collection. Metric units, scale length 1; root and all
meshes have zero translation/rotation, unit scale, ground-origin pivots and no remaining
modifiers. Blender +Z → Godot +Y and Blender +Y → Godot -Z occur once through glTF.
No compensating prefab transform is used.

Seven opaque, back-culled Principled materials retain the siblings' names and PBR values:

| Material | Role |
| --- | --- |
| `glassward_indigo` | Main mass, quiet roof and spandrels |
| `glassward_frame` | Vertical piers, seat collar, lobby fascia/canopy |
| `glassward_glazing_opaque` | Broad opaque glazing groups and closed doors |
| `glassward_glazing_highlight` | Two restrained broad window variations |
| `glassward_crown_cyan` | Rounded rim; emission strength 0.35 |
| `glassward_accent_magenta` | One small entrance lintel; emission strength 0.12 |
| `glassward_lobby_stone` | Base shoe, lobby piers and canopy soffit |

Actual per-section slot order and PBR values are in `validation.json`: crown 3 surfaces,
facade 4, lobby 5. Emission is appearance-only; no real light or bloom dependency. There are
no embedded images. Closed overlapping architectural pieces are intentional, each manifold;
they are not a Boolean-unioned building. No rig, animation, sockets, destruction state,
interior, elevator, rooftop route or material-remap API is required. Default automatic Godot
LOD/shadow-mesh generation remains enabled; transitions and repeat cost await engine review.

## Prefab and collision

`Visuals/Model` is an identity-transform linked GLB instance, with no copied render mesh data
or editable-child overrides. `Collision/Body` is one `StaticBody3D`, layer 1 / mask 0, with a
minimal two-box compound:

- `Lobby`: size (24,6,18), centre (0,3,0), Y=0–6 m.
- `Shaft`: size (22,32.4,16), centre (0,22.2,0), Y=6–38.4 m.

These boxes fill the inaccessible rectangular lobby and shaft, meeting without a gap and
preserving the setback. Closed doors block entry; small bevels/flush trim add no snag shapes.
The **crown above Y=38.4 m is overhead visual-only**, per the standing collision rule; no box
fills its rounded corner cutouts. The canopy is also overhead decoration, with 3.56 m ground
clearance. No rooftop traversal or collision promise above the shaft cap is implied.

Initial headless normalization followed by two complete save/reload roundtrips preserved
prefab bytes, node identities and scene UID. Fresh-process checks resolve both model/prefab
UIDs. The scene UID lives internally in `.tscn`; GDScript retains its required `.uid` sidecar.
The commission forbids live editor access and the windowed editor is unavailable, so direct
text authoring followed by pinned headless load/pack/save was used. No live scene is claimed
synchronized and no owner's editor process was touched.

## Evidence and measured validation

[Hero](d04_towers_03-evidence/hero.png) · [side](d04_towers_03-evidence/side.png) ·
[crown detail](d04_towers_03-evidence/crown_detail.png) ·
[47 m / 42° gameplay camera](d04_towers_03-evidence/overhead_47m_42deg.png).

All four final images were inspected by the producer and compared with the earlier siblings.
Supporting images are 1152×648; overhead is 1280×720 under the lean-evidence rule. Blender
Cycles CPU, 32 samples, AgX, broad studio fill; evidence is reduced to 7 bits/channel RGB with
PNG compression level 9. Hero/side retain the full silhouette, while the detail shows the
continuous circular corners, restrained roof and intentional square seat shoulders.

The gameplay camera is vertical-down, north-up, **42° vertical FOV**, at Godot (18,47,-16)
relative to the pivot, the same off-footprint forecourt vantage as `.01/.02`. The crown is
3.8 m below the camera but **outside its off-footprint frustum**. Lower facade/lobby geometry
projects into the frame edge while open ground remains visible. Near-camera perspective
magnification is still a placement/occlusion risk. This is not a full-building overview,
engine capture, cutaway or actor/target visibility proof; nothing was hidden, rescaled or
provided with a camera treatment to conceal that constraint.

Final measurements: [validation.json](d04_towers_03-evidence/validation.json).
Producer payload inventory: [manifest.json](d04_towers_03-evidence/manifest.json).
Concise command/diagnostic outcomes: [final.log](d04_towers_03-evidence/final.log).

- **7,824 source vertices; 15,140 triangles; 9,848 exported vertices including splits.**
- **3 meshes, 12 material surfaces, 7 unique materials.**
- Zero degenerate source faces, zero non-manifold source edges, zero degenerate GLB triangles.
- Unit-length source and GLB normals; maximum exported normal-length error <0.000001.
- Source section bounds and actual GLB/Godot bounds meet the ±0.001 m literal contract.
- Twenty circular-corner support checks pass, maximum error <0.000001 m.
- Fresh saved-source export is byte-identical: **416,584 bytes**, SHA-256
  `332a177005e1c7ff67916845e786c2ab050cfff62536298390644ead82e05d1a`.
- Pinned imports pass without ERROR/SCRIPT ERROR lines. Fresh linked-prefab checks pass for
  dependencies, ancestry, transforms, bounds, materials, collision and registered UIDs.
- **16 shape queries** cover closed lobby, rectangular corners, clear edges, setback, section
  join, shaft cap, overhead visual-only crown/canopy and clear space above camera height.
- **7 actor/car envelope casts**: front/rear/end actor and front car blocked; side actor,
  under-canopy actor and side car bypass clear. Front ray hits Z=-9 m. Capsule r=0.35 m,
  h=1.8 m; test car box 1.8×1.5×4.4 m. These exercise Godot physics APIs, not production
  controller handling, authoritative prediction or network transport.
- Owned GDScript formatting/lint passes. No global production suite was run (decision 52).

Toolchain: Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**;
Godot **4.8.dev7.official.c971f93e7**; gdstyle **0.3.0**. Blender's future-6.0 `use_nodes`
deprecation and the existing MCP Godot-4.8 compatibility warning are classified, not broadly
suppressed. Scratch renders, raw logs and comparison exports stay outside the repository.

## Exact reproduction

From repository root in Git Bash, without accessing live editor sessions:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_towers_03/author.py
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_towers_03/validate.py
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_towers_03/check_prefab.gd -- --normalize
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_towers_03/check_prefab.gd -- --output C:/tmp/ft/assets/d04_towers_03/prefab-fresh-final.json
timeout 60 "$(mise which gdstyle)" fmt --check tools/asset_production/d04_towers_03/check_prefab.gd
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 tools/asset_production/d04_towers_03/check_prefab.gd
python tools/asset_production/d04_towers_03/record.py --compress-renders
```

The validator invokes `export.py` with the shared `tools/assets/blender/export_settings.json`,
the named collection and animation/skin export disabled. Fresh output goes to
`C:/tmp/ft/assets/d04_towers_03/reexport/`. `record.py` verifies final receipts/GLB bytes,
packages lean evidence and regenerates the manifest last. Reinspect all rendered images after
reproduction; packaging does not replace visual review.

## Remaining acceptance

- Supervising art/technical reviewers: independent exact-commit review and final dimensions.
- Layout/gameplay owners: compose the unequal skyline around important open forecourt space;
  check actual walking/car clearance and populated-city sightlines. No placement was authored.
- Render/integration owners: engine material/normal/LOD views, shadow fill, near-camera
  magnification, tower clipping and actor/target visibility. No cutaway/occlusion system added.
- Gameplay/network owners: production controller handling, authoritative/predicted collision,
  real separate-process multiplayer and each platform transport.
- Performance/build owners: repeated-placement draw calls, LOD transitions, sustained Deck
  LCD/OLED frame pacing and packaged dependencies. Headless import is not device acceptance.

No register, shared brief, TODO, progress, gameplay rule or world scene was changed. This
bounded asset delivery does not claim downstream full game-ready/placement acceptance.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
