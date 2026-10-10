# city_harbour_bridge.01 — Single level-deck bridge

**Source/export and linked-prefab candidate; independent review and world acceptance pending.**
Produced by the commissioned implementation specialist on `lane/a-hbridge`.
The current [commission](commission.md) and asset-common production brief supersede the
concept-only wording of the [family brief](../city_harbour_bridge.md). Original Blender
construction, no downloaded/purchased/image-generated meshes, brands or textures.
No sibling, register, project setting, shared brief or world scene was changed.

## Design and measured layout fit

A single quiet civic concrete slab, pale integral edge shoulders, a narrow recessed
metal fascia line, five shallow petrol steel box girders and seven cross diaphragms.
The level top is **structural concrete, not a substitute road/sidewalk/marking kit**.
Those surfaces remain road-tool-owned. Low parapets and warm fixtures belong to
`city_harbour_bridge.02`; bank-end finish belongs to `.03`. No towers, new ramps,
water piers, interiors or additional crossing are introduced.

The existing route is materially larger than the word “short” in the concept:
`Harbour bridge` is map `(309,590)` → `(400,590)`, exactly **91 m**. The greybox
preparation buffers it by **8.5 m** on each side with flat ends. This asset preserves
that **91 × 17 m** footprint, rather than inventing a small generic bridge. Sources:
[road plan](../../concepts/world-v1/stage-04-streets/README.md),
`docs/concepts/world-v1/stage-04-streets/draw_plan.py`,
`tools/assets/world/brackett_greybox/prepare.py`, and
[greybox datums](../brackett_greybox.md). Old Quay's approved district identity calls
for a quiet municipal crossing and continuous harbour-mouth water.

| Contract | Value in metres, Godot local axes |
| --- | --- |
| Visual AABB | min `(-45.5,-1.25,-8.5)`, max `(45.5,0,8.5)` |
| X width / Y height / Z length | **91 / 1.25 / 17** |
| Pivot / surface datum | `(0,0,0)`, centre of structural deck top; deliberately not seabed/ground-contact |
| Level top area | **1547 m²**, all top vertices at Y=0 |
| Slab | 0.55 deep; bottom side shoulders chamfer inward 0.15 |
| Integral pale top shoulder | 0.35 wide along each long edge; flush, not a raised guard |
| Girders | five, 90.2 long; maximum depth below top 1.25 |
| Bank joins | `(-45.5,0,0)` and `(45.5,0,0)`, square, full 17 m width |
| Water reference | existing Y=-2.1; **0.85 m** minimum clear gap below the visual girders |
| Tolerances | envelope ±0.001; source top plane ±0.000001 |

Footprint and ground/water references are inherited measurements. **Structural
thickness, girder proportions and 0.85 m gap are provisional production choices**,
not engineered span certification or navigable-boat clearance. There is no boat
play requirement. The gap remains open across the entire water mouth with no piers.

### Family interface for subsequent siblings

Use the same axis convention: local +X is east along the span, Godot +Z south across
it; Blender +Y maps to Godot -Z. No corrective root rotation/scale. For eventual
layout replacement only, the existing route centre maps to world `(-275.5,0,235)`;
**this delivery does not place it** or replace greybox ground.

- `.02` may use the complete ±45.5 m span and the two 0.35 m flush shoulders,
  Z `[8.15,8.5]` and `[-8.5,-8.15]`, Y=0, for its low parapet pair. Suggested rail
  centre lines are Z=±8.325; the sibling owns final guard height/shape/collision.
  Keep the 9 m roadway reference (Z=±4.5) clear. The original 4 m side corridors
  include edge furniture space; a 0.35 m guard reservation leaves 3.65 m each side.
- `.03` mates at the two X=±45.5 end planes, Y=0. Do not create a new approach
  slope or a vertical step across the road. Exact trim depth remains sibling-owned.
- Generated road and walk visual reference datums are Y=0.025 and 0.06 respectively.
  At integration, keep one continuous walk/collision writer at the final approved
  surface datum; do not retain duplicate greybox/deck/generated coplanar colliders.
- This is an unguarded **structural component**, not a safe standalone placed route.
  Guarded assembly and final bank connections remain mandatory placement gates.

## Source, export, materials and prefab

- Editable source: `art/source/models/environment/city_harbour_bridge_01/city_harbour_bridge_01.blend`.
- Collection: `export_city_harbour_bridge_01`; root `CityHarbourBridge01`, mesh
  `CityHarbourBridge01_Mesh`. Both identity transforms, metre units, no modifiers left.
- Export: `art/models/environment/city_harbour_bridge_01/city_harbour_bridge_01.glb`
  and its preserved `.glb.import` sidecar.
- Wrapper: `scenes/prefabs/environment/city_harbour_bridge_01.tscn`.
  `Visuals/Model` remains an identity-transform linked imported instance.
- Opaque back-culling Principled surfaces: `bridge_civic_concrete`,
  `bridge_pale_fascia`, `bridge_petrol_steel`, `bridge_recess`. Exported PBR values
  are recorded in validation.json. No textures, embedded images, material overrides,
  rigs, clips, lights, destructive states or runtime node construction.
- Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**;
  export.py loads `tools/assets/blender/export_settings.json`, filters the named
  collection and disables animation/skins. Default Godot automatic LOD generation
  is retained; no explicit LOD set or performance budget is claimed.

Collision is separate at `Collision/Body/Deck`: **one** static BoxShape3D,
size `(91,0.55,17)`, centre `(0,-0.275,0)`, layer 1/mask 0. This gives exact
continuous top support without decorative snags. Lower girders are inaccessible
under-deck decoration rather than a second walk surface. The collider deliberately
fills the tiny lower shoulder chamfer; this does not change the top footprint.
No invisible edge guard is added in advance of `.02`.

The mandatory fallback used text-authored saved scenes, then pinned headless
load/pack/resave. Live owner Blender/Godot sessions were neither used nor touched.
No claim is made that headless import synchronizes a separate open editor scene.
The saved prefab and collision-only `walk_check.tscn` fixture both roundtrip with
stable bytes/UIDs. The fixture's bank boxes are test-only collision, not visual assets.

## Evidence and validation

[Hero](city_harbour_bridge_01-evidence/hero.png) ·
[side](city_harbour_bridge_01-evidence/side.png) ·
[bank/soffit detail](city_harbour_bridge_01-evidence/detail.png) ·
[47 m / 42° overhead](city_harbour_bridge_01-evidence/overhead_47m_42deg.png).
All four are isolated Blender renders, 1280×720, inspected by the producer.
The teal studio plane at Y=-2.1 illustrates water continuity; it is not exported.
Hero/side show the whole 91 m span. The true vertical-down, north-up, 47 m / 42°
vertical-FOV view intentionally crops the long span: do not mistake it for a fitted
whole-bridge overview. It shows a quiet deck field and two continuous pale edge
shoulders. Road dressing and guards are absent because their owners are separate.
During self-review, flat slab face normals replaced interpolated end-face shading,
and flush shoulders improved edge legibility without creating road markings.
These renders do not establish final guarded-road readability in Godot.

`city_harbour_bridge_01-evidence/validation.json` records:

- **3,600 triangles, 1,840 Blender vertices, 2,235 GLB vertices, one mesh, four surfaces**.
- **Zero degenerate faces, zero non-manifold edges**, consistent outward winding,
  finite vertices, unit source and exported normals, exact layout footprint/top datum.
  Joined manufactured subparts are separate closed overlapping shells, not a boolean
  engineering solid; all shell edges are manifold.
- Actual binary GLB position/normal/index inspection, source/imported AABB checks,
  no studio nodes/images/animation in the export, fresh-process reexport **byte-identical**.
- Pinned Godot **4.8.dev7.official.c971f93e7**: dependency and UID resolution,
  linked import identity, four opaque back-culling surfaces, stable saved roundtrip,
  exact box envelope and collision layers.
- Seven independent floor rays including both bank seams; one outside-edge miss;
  one unobstructed cross-mouth ray at Y=-1.6.
- Production `ActorMotion.step` with radius 0.35 / height 1.8 capsule and production
  `FootCommand`: **1,128 ticks per mode**, bank-to-bank through both seams,
  AUTHORITY and REPLAY results equal, ending `(46.9997368,0.001,0)` from X=-47.
  This is local simulation equivalence, **not network transport or vehicle driving**.
- Canonical checks: all owned scripts compile/style clean; **16 Python tests**;
  **142/142 GUT tests**, 6,705 assertions; expected-failure diagnostic test exits 1.

A first validator run passed geometry but could not write an absent evidence directory;
validate.py now creates it. The exact requested production-check command encountered a
Windows shim/cp1252 decoding failure before engine verification. The corrected command
uses explicit mise-resolved binary paths plus `PYTHONUTF8=1`; the full suite then passed.
Headless import emitted the third-party MCP 4.8-support warning. Direct editor-mode
normalization reached all successful assertions but emitted editor/plugin RID/ObjectDB
shutdown leaks. The subsequent runtime dependency/physics check and clean compiler
mirror completed without errors/warnings. These diagnostics are recorded, not suppressed
or attributed to missing bridge dependencies. Concise final receipt: `final.log`;
full scratch diagnostics remain under `C:/tmp/ft/assets/city_harbour_bridge_01/`.
`manifest.json` hashes every delivery payload, excluding itself.

## Exact reproduction (Git Bash, repository root)

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=tools/asset_production/city_harbour_bridge_01
S=art/source/models/environment/city_harbour_bridge_01/city_harbour_bridge_01.blend
O=C:/tmp/ft/assets/city_harbour_bridge_01
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
# Source rebuild also exports; do not run while source is being edited.
timeout 300 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 "$S" --python "$T/export.py" -- "$O/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$O/reexport/city_harbour_bridge_01.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
timeout 300 "$(mise which godot)" --headless --editor --path . --import --quit
timeout 180 "$(mise which godot)" --headless --editor --path . --script "res://$T/check.gd" -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script "res://$T/check.gd"
timeout 30 "$(mise which gdstyle)" "$T/check.gd"
# Output must be a fresh external directory; change checks-repro for each run.
PYTHONUTF8=1 timeout 1800 python tools/production_checks.py --godot "$(mise which godot)" --gdstyle "$(mise which gdstyle)" --output "$O/checks-repro"
python "$T/manifest.py" "$O/checks-repro"
```

## Remaining acceptance / integration gates

Independent technical/art review is pending. World owner must replace the old
solid greybox bridge footprint without duplicate support geometry, fit the two bank
joins to the existing network, add `.02` and `.03`, preserve visible water and verify
final generated road/sidewalk datums. Engineering/boat clearance is not certified.
Actor/car turning, braking, road-tool attachment, guarded-edge collision, final-camera
captures, separate-process multiplayer and packaged/Deck sustained performance remain
pending. No world placement, completed route, ready register status or new gameplay
mechanic is claimed by this component delivery.
