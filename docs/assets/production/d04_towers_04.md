# d04_towers.04 — Mid-height tower

**Source/export, linked prefab and bounded headless checks delivered; independent review,
world placement and gameplay/device acceptance pending.** Production is commissioned under
the [commission](commission.md) and standing asset-production brief. Producer: isolated
asset-production worker. Accepting owners: supervising art/technical/gameplay reviewers;
the producer does not self-approve downstream acceptance.

References: [tower family](../d04_towers.md),
[Glassward breakdown](../../concepts/districts-v1/glassward-assets.md),
[liked district concept](../../concepts/districts-v1/glassward.md),
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[gridded downtown streets](../../concepts/world-v1/stage-04-streets/README.md),
[rectangular](d04_towers_01.md), [chamfered](d04_towers_02.md) and
[rounded](d04_towers_03.md) siblings.

## Design and dimensions

A conventional indigo office tower with a **two-tier stepped rectangular cyan crown**.
Six floors make it the shorter supporting tower, not a low-office/podium substitute. The
upper crown steps inward on all four sides, creating two broad horizontal silhouettes and
quiet roof shoulders. This is architectural crown geometry, not a duplicate roof plant
unit. Broad three-floor glazing groups, restrained grey-blue piers, the closed six-metre
lobby and one small magenta entry lintel retain the family vocabulary. No lettering or real
brand is introduced. At 32.4 m it sits below the 43.2, 54 and 64.8 m delivered members; the
family's near/above-camera ambition is preserved rather than replacing the taller designs.

All dimensions are **provisional authored proposals**, permitted by the standing production
brief, not measurements inferred from concept imagery or approved parcel sizes. Metre-space
acceptance tolerance: ±0.001 m. Godot dimensions are X width / Y height / Z depth.

| Contract | Provisional value |
| --- | --- |
| Ground/lobby footprint | 24 × 18 m, 432 m²; Y=0 ground |
| Lobby | Y=0–6 m, closed exterior; no enterable door or interior |
| Shaft | 22 × 16 m plan, Y=6–27.6 m |
| Floor rhythm | 6 floors at 3.6 m pitch; two broad 10.8 m three-floor groups |
| Crown interface | Centred horizontal 22 × 16 m seat at Y=27.6 m |
| Seat collar | 22 × 16 m, Y=27.6–27.9 m |
| Lower crown drum | 21.6 × 15.6 m, Y=27.9–29.5 m |
| Lower cyan shoulder rim | 22.8 × 16.8 m, Y=29.1–29.7 m |
| Upper crown drum | 15.2 × 9.2 m, Y=29.5–31.6 m |
| Upper cyan rim | 16 × 10 m, Y=31.5–32.4 m |
| Tier setback | Upper rim is 3.4 m inward from the lower rim on every side |
| Both cyan rims | 0.8 m broad with 0.04 m soft edge bevels; closed annular meshes |
| Overall height | **32.4 m**, 14.6 m below the provisional gameplay camera |
| Entry canopy | 6 × 1.7 m; front reaches Z=-10.2 m; minimum soffit Y=3.56 m |
| Whole visual AABB | min (-12,0,-10.2), max (12,32.4,9) m |
| Whole visual size | 24 × 32.4 × 19.2 m, including the front canopy |
| Pivot/front | Ground-centred (0,0,0); front Godot -Z / Blender +Y |

The cyan rings are each one continuous closed annular prism, not four overlapping mitre
pieces. Independent per-tier bounds and open-recess checks verify the actual setback rather
than accepting a single bounding box that could hide a full-width upper crown. The inner
corners allow the documented 0.04 m bevel in addition to the numerical tolerance.

### Family compatibility and scope

The 6 m lobby, 3.6 m floor pitch, three-floor grouping, seven-material opaque palette and
horizontal crown-seat convention follow all three earlier siblings. The owned Blender recipe
adapts their lobby/facade construction while retaining separately editable `lobby()`, `facade()`
and `crown()` sections. The 22 × 16 m seat expresses design compatibility, **not** a runtime
interchangeable-crown API. This member has its own source, export and seat height. Its shorter
shaft and stepped crown are geometry changes, not a recolor. No runtime generator or extra
variant is included.

No podium, paving, forecourt platform, fixtures, roof machinery, road surfaces or placement
is included. The 432 m² footprint is not a whole-block allocation. Layout must preserve the
unequal skyline and **important open ground**, not pack every gap with another building.
All three earlier current handoffs were checked: none contains a stale pending item for
`.04`, so no sibling document or manifest was changed. Registry/family progress is not owned
by this handoff.

## Source, export and materials

- Source: `art/source/models/environment/d04_towers_04/d04_towers_04.blend`.
- Collection: `export_d04_towers_04`; root: `D04Towers04`.
- Editable meshes: `D04Towers04_Lobby`, `D04Towers04_Facade`, `D04Towers04_Crown`.
- Explicit export: `art/models/environment/d04_towers_04/d04_towers_04.glb` and its
  pinned-engine `.import` sidecar. The existing source `.gdignore` excludes the `.blend`.
- Prefab: `scenes/prefabs/environment/d04_towers_04.tscn`.
- Tools: `tools/asset_production/d04_towers_04/{author,export,validate,record}.py`,
  `check_prefab.gd` and its engine-generated `.uid`.

Original Blender construction only: no downloads, purchased assets, image-to-mesh, fonts,
textures, external material dependencies or runtime render geometry. Studio plane, lights
and camera stay outside the export collection. Metric units, scale length 1; root and all
three meshes have zero translation/rotation, unit scale, ground-origin pivots and no remaining
modifiers. Blender +Z → Godot +Y and Blender +Y → Godot -Z occur once through glTF export;
there is no compensating prefab transform or reference to archived prototypes.

Seven opaque, back-culled Principled materials retain the siblings' names and PBR values:

| Material | Role |
| --- | --- |
| `glassward_indigo` | Main mass, both crown drums, quiet roof and spandrels |
| `glassward_frame` | Vertical piers, seat collar, lobby fascia/canopy |
| `glassward_glazing_opaque` | Broad opaque glazing groups and closed door faces |
| `glassward_glazing_highlight` | Two restrained broad facade variations |
| `glassward_crown_cyan` | Both stepped rims; emission strength 0.35 |
| `glassward_accent_magenta` | One small entrance lintel; emission strength 0.12 |
| `glassward_lobby_stone` | Base shoe, lobby piers and canopy soffit |

Actual per-section slot order and PBR values are in `validation.json`: crown 3 surfaces,
facade 4, lobby 5. Emission is appearance-only, with no real lights or bloom dependency.
There are no embedded images. Closed overlapping architectural pieces are intentional, each
manifold; they are not a Boolean-unioned building. No rig, animation, socket, destruction
state, interior, elevator, rooftop route or material-remap API is required. Default automatic
Godot LOD/shadow-mesh generation remains enabled; transitions and repeat cost await review.

## Prefab and collision

`Visuals/Model` is an identity-transform linked GLB instance with no editable-child override
or embedded replacement render mesh. `Collision/Body` is one `StaticBody3D`, layer 1 / mask 0,
with a minimal two-box compound:

- `Lobby`: size (24,6,18), centre (0,3,0), spanning Y=0–6 m.
- `Shaft`: size (22,21.6,16), centre (0,16.8,0), spanning Y=6–27.6 m.

The boxes fill the inaccessible lobby and shaft, touching without a gap and preserving the
setback. Closed doors block entry; small bevels and flush trim do not add snag shapes.
The **crown above Y=27.6 m is overhead visual-only**, per the standing collision rule. The
canopy is also overhead decoration with 3.56 m ground clearance. No rooftop traversal or
collision promise above the shaft cap is implied; the raised crown is not a walkable deck.

Initial headless normalization followed by two complete save/reload roundtrips preserved
prefab bytes, node identities and scene UID. Fresh-process checks resolve model/prefab UIDs.
The scene UID is stored internally in `.tscn`; GDScript retains its required `.uid` sidecar.
The commission forbids live editor access and the windowed editor is unavailable, so direct
text authoring followed by pinned headless load/pack/save was used. No live editor was touched
or claimed synchronized.

## Evidence and measured validation

[Hero](d04_towers_04-evidence/hero.png) · [side](d04_towers_04-evidence/side.png) ·
[crown detail](d04_towers_04-evidence/crown_detail.png) ·
[47 m / 42° gameplay camera](d04_towers_04-evidence/overhead_47m_42deg.png).

All four final images were inspected by the producer and supporting views compared with the
earlier siblings. Hero/side show the full silhouette and the detail clearly separates the two
crown tiers. The broad glazing, dark lobby setback and small entry accent retain the family
appearance without extra rooftop props. Supporting images are 1152×648; overhead is 1280×720
under the lean-evidence rule. Blender Cycles CPU, 32 samples, AgX and broad studio fill;
evidence is reduced to 7 bits/channel RGB with PNG compression level 9.

The gameplay camera is vertical-down, north-up, **42° vertical FOV**, at Godot (14,47,-12)
relative to the pivot. This closer off-footprint forecourt vantage differs from the earlier
siblings' (18,47,-16), allowing part of the shorter member's lower crown into frame. The
lower cyan rim and facade occupy/crop at the bottom-left edge while most of the view is open
ground. The upper tier remains outside this off-centre frustum despite being below camera
height. This is not a full-building overview, engine capture, cutaway or actor/target visibility
proof. No model was hidden, rescaled or given an occlusion treatment to conceal the constraint.

Final measurements: [validation.json](d04_towers_04-evidence/validation.json).
Producer payload inventory: [manifest.json](d04_towers_04-evidence/manifest.json).
Concise command/diagnostic outcomes: [final.log](d04_towers_04-evidence/final.log).

- **5,768 source vertices; 11,128 triangles; 7,408 exported vertices including splits.**
- **3 meshes, 12 material surfaces, 7 unique materials.**
- Zero degenerate source faces, zero non-manifold source edges, zero degenerate GLB triangles.
- Unit-length source/GLB normals; maximum exported normal-length error <0.000001.
- Source section bounds and actual GLB/Godot bounds meet the ±0.001 m literal contract.
- Independent stepped-tier envelope and open-recess checks pass, including the inner bevel.
- Fresh saved-source export is byte-identical: **314,476 bytes**, SHA-256
  `fd716f77780c47b9a692f58b811a14e064360544d12924de20f20625a1371e61`.
- Pinned imports pass without ERROR/SCRIPT ERROR lines. Fresh linked-prefab checks pass for
  dependencies, ancestry, transforms, bounds, materials, collision and registered UIDs.
- **16 shape queries** cover closed lobby, corner coverage, clear edges, setback, section
  join, shaft cap, overhead visual-only crown/canopy and clear space above camera height.
- **7 actor/car envelope casts**: front/rear/end actor and front car blocked; side actor,
  under-canopy actor and side car bypass clear. Front ray hits Z=-9 m. Actor capsule r=0.35 m,
  h=1.8 m; test car box 1.8×1.5×4.4 m. These exercise Godot physics APIs, not production
  controller handling, prediction or network transport.
- Owned Python syntax and GDScript formatting/lint pass. No global production suite was run
  (owner decision 52).

Toolchain: Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**;
Godot **4.8.dev7.official.c971f93e7**; gdstyle **0.3.0**. Blender's future-6.0 `use_nodes`
deprecation and the existing MCP Godot-4.8 compatibility warning are classified, not broadly
suppressed. The initial recess assertion omitted the 0.04 m bevel allowance; the literal
expectation was corrected and validation rerun successfully without changing geometry.
Scratch exports, renders and raw logs remain outside the repository.

## Exact reproduction

From repository root in Git Bash, without accessing live editor sessions:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_towers_04/author.py
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/d04_towers_04/validate.py
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_towers_04/check_prefab.gd -- --normalize
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script res://tools/asset_production/d04_towers_04/check_prefab.gd -- --output C:/tmp/ft/assets/d04_towers_04/prefab-fresh-final.json
timeout 60 "$(mise which gdstyle)" fmt --check tools/asset_production/d04_towers_04/check_prefab.gd
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 tools/asset_production/d04_towers_04/check_prefab.gd
python tools/asset_production/d04_towers_04/record.py --compress-renders
```

The validator invokes `export.py` with the shared `tools/assets/blender/export_settings.json`,
the named collection and animation/skin export disabled. Fresh output goes to
`C:/tmp/ft/assets/d04_towers_04/reexport/`. `record.py` verifies final receipts and GLB bytes,
packages lean evidence and regenerates the manifest last. Reinspect all rendered images after
reproduction; packaging does not replace visual review.

## Remaining acceptance

- Supervising art/technical reviewers: independent exact-commit review and final dimensions.
- Layout/gameplay owners: compose the unequal skyline around important open forecourt space;
  check actual walking/car clearance and populated-city sightlines. No placement was authored.
- Render/integration owners: engine material/normal/LOD views, shadow fill, perspective
  magnification, tower clipping and actor/target visibility. No cutaway/occlusion system added.
- Gameplay/network owners: production controller handling, authoritative/predicted collision,
  real separate-process multiplayer and each platform transport.
- Performance/build owners: repeated-placement draw calls, LOD transitions, sustained Deck
  LCD/OLED frame pacing and packaged dependencies. Headless import is not device acceptance.

No register, shared brief, TODO, progress, gameplay rule or world scene was changed. This
bounded asset delivery does not claim downstream full game-ready/placement acceptance.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
