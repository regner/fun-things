# d08_workshop_buildings.04 — Attached office

10 October 2026. **Source/export, linked office and saved family comparison delivered;
independent review and world/gameplay/device acceptance pending.** Regner's
[production commission](commission.md) and per-record brief supersede the concept-only
status of the [workshop family brief](../d08_workshop_buildings.md), not its revision-02
Ironreach design requirements.

Producing owner: commissioned asset-production worker, original Blender construction,
technical integration and visual self-review. Accepting owners: independent asset reviewer
and supervising production lead (pending); downstream layout/gameplay/device owners retain
their gates. No register, progress, catalogue, world scene or shared tooling changed. The
approved sibling-status exception updates only stale family-comparison/office-pending text
in the .01/.02/.03 handoffs and those documents' current manifest entries. Their models,
prefabs, validation and historical receipts remain unchanged.

## Design and dimensions

A low **6 × 3m lean-to office**, attached along its bare west wall to one shared 3m shed bay.
Its broad counter window, separate occupied personnel door and subordinate roof distinguish
it from the taller roller-shutter sheds. The office stays ordinary and practical: faded
petrol walls, pale framing, three oversized worn-brick courses, localized rust and two broad
mismatched corrugated roof patches. A small amber entry marker and door/task lens are the
only bright accents. No cyan, brands, downloaded art, generated-image geometry or external
textures. Ironreach's liked revision-02 concept was inspected for style, never measured.

All dimensions are **provisional authored values**, permitted by the production brief and
reconciled with the three delivered siblings; they do not allocate district parcels/routes.

| Contract | Metres, Godot local axes unless stated |
| --- | --- |
| Closed structural footprint | X 6.00 × Z 3.00, ground-centred |
| Solid wall / collision height | Y 3.00; lower than the siblings' 4m datum |
| Visual AABB minimum | (-3.08, 0, -1.74) |
| Visual AABB maximum | (3.20, 3.55, 1.70) |
| Overall visual dimensions X/Y/Z | 6.28 × 3.55 × 3.44 |
| Roof upper plane | Y 3.42 at X -3, falling to Y 3.11 at X 3.20 |
| Closed roof sheet | 0.16 vertical thickness, 0.20 front/rear/east overhang |
| High-side attachment flashing | X -3.08…-2.80; Y 3.37…3.55; Z ±1.70 |
| Brick base | Y 0…0.72, shared 0.24m courses |
| Pale office lintel band | Y 2.65…2.90, subordinate to shed band Y 3.65…3.90 |
| Counter-window outer frame | 2.70 wide × 1.41 high; centre X -1.23 |
| Closed personnel door | 1.20 wide × 2.35 high; centre X 1.60; top Y 2.39 |
| Applied detail | mortar 0.006, pilasters 0.055, window sill 0.20, door pull 0.23 |
| Integral task lamp | projection 0.24; lowest lens Y 2.715, above actor head |
| Numeric tolerance | envelope/ground ±0.001; source → GLB mapping ±0.00001 |

Root and joined mesh pivots are (0,0,0), centred on the structural ground footprint.
Metre units, applied rotation/scale, unit root scale, no corrective wrapper transforms.
Blender +Y front maps to Godot -Z; Blender +Z maps to Godot +Y. No interior, opening doors,
walkable roof, stairs, ramp, destruction, rig, animation, runtime socket or interaction API.
Amber emission 0.3 is appearance-only; no real lights or yard-lighting budget is implied.

### Family attachment contract

The office's bare west **X -3** wall mates to the siblings' documented right-rear planes.
Place the office at the following translations **relative to an identity-oriented host**;
no rotation or scaling is required. The shells remain closed; this is not a passage.

| Host | Host join plane/span | Office root translation | Sampled roof clearance |
| --- | --- | --- | --- |
| [.01 pitched shed](d08_workshop_buildings_01.md) | X 5; Z 3…6 | (8,0,4.5) | 0.469439m |
| [.02 sawtooth workshop](d08_workshop_buildings_02.md) | X 7; Z 3…6 | (10,0,4.5) | 0.370000m |
| [.03 larger depot](d08_workshop_buildings_03.md) | X 9; Z 4.5…7.5 | (12,0,6) | 0.495442m |

The validator loads each actual sibling source without saving it, casts upward to its roof
underside 0.10m outward from the join, and compares the office flashing's measured top.
These are **sampled vertical clearances**, not a whole-mesh collision-distance calculation.
The office's 3.55m maximum is below all three local roof interfaces; the flashing projects
0.08m into the host and covers its at-most-0.05m trim seam. Front/rear/end trim is small
applied decoration; no hidden collar enlarges the solid footprint. Whole-building placement
must still preserve camera visibility and route clearances.

### Saved unequal-shed comparison

`scenes/prefabs/environment/d08_workshop_buildings_04_family.tscn` instances **existing
prefabs only**: .01 at **(8,0,-2)**, .02 at **(-13,0,1)**, and this office at **(16,0,2.5)**.
It supplies the family brief's two unequal offset sheds plus one attached office, without a
new landmark mesh. The office joins .01 at world X 13 / Z 1…4. The central structural gap
is **9.00m** (8.30m between roof overhangs), open at both north and south ends. The office
is on the outside flank rather than occupying this yard. An outer foot bypass is checked
at X 20; a car-sized sweep also clears X 21.

This is an **unplaced reusable comparison**, not a district scene or approved yard layout.
It contains no authored ground/road surface, fence, traffic topology, spawn, lights or
runtime composition script. World integration owns usable connections, chain spacing,
turning, final ground and any separate foot-route designation. The overhead evidence uses
exactly these translations, loading the unchanged sibling Blender export collections only
for rendering after the office source has been saved/exported.

## Source, exports and materials

| Deliverable | Path / identity |
| --- | --- |
| Editable Blender source | `art/source/models/environment/d08_workshop_buildings_04/d08_workshop_buildings_04.blend` |
| Export collection | `export_d08_workshop_buildings_04` |
| Root → mesh | `D08WorkshopBuildings04` → `D08WorkshopBuildings04_Mesh` |
| Explicit linked export | `art/models/environment/d08_workshop_buildings_04/d08_workshop_buildings_04.glb` |
| Import sidecar | adjacent `.glb.import`, model UID `uid://c2oj8fnpnigbw` |
| Office wrapper | `scenes/prefabs/environment/d08_workshop_buildings_04.tscn`, UID `uid://d12favqhc3yl3` |
| Family comparison | `scenes/prefabs/environment/d08_workshop_buildings_04_family.tscn`, UID `uid://d15hpy5mqnuu1` |
| Tools | `tools/asset_production/d08_workshop_buildings_04/{author.py,export.py,validate.py,check_prefab.gd,record.py}` plus GDScript `.uid` |

Eight opaque, back-culling Principled materials reuse the siblings' **exact names and PBR
values**, checked against all three committed GLBs. Office surface order is:

1. `ironreach_worn_brick` — masonry base.
2. `ironreach_faded_petrol` — wall paint, quiet mortar and lean-to infill.
3. `ironreach_pale_band` — framing, structural bands and attachment flashing.
4. `ironreach_local_rust` — localized wall/base repairs and small roof patch.
5. `ironreach_dark_recess` — opaque windows, closed door and lamp casing.
6. `ironreach_replacement_sheet` — window sill and galvanized roof repair.
7. `ironreach_working_amber` — occupied door, task lens and short entry marker.
8. `ironreach_roof_petrol` — main lean-to sheet and broad corrugations.

Full PBR values are in [validation.json](d08_workshop_buildings_04-evidence/validation.json).
No textures, embedded images, external materials, overrides or UV artwork are required.
No extra variants, rigs, clips, sockets or custom LODs. Default Godot mesh LOD generation
remains enabled; native transition/repetition costs are still pending.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. `export.py` loads
`tools/assets/blender/export_settings.json`, filters the named collection and disables
animation/skins. Closed editable manufactured components are joined into one mesh, not
boolean-unioned. Applied bevel/weighted-normal treatment follows the sibling convention.
Studio camera, lights and plane are outside the export collection; sibling comparison
geometry is not stored in the office source or export. Collision remains independent.

## Evidence and reproduction

[Hero](d08_workshop_buildings_04-evidence/hero.png) ·
[Side](d08_workshop_buildings_04-evidence/side.png) ·
[Office detail](d08_workshop_buildings_04-evidence/office_detail.png) ·
[47m / 42° family overhead](d08_workshop_buildings_04-evidence/overhead_47m_42deg.png).

All four are **isolated Blender renders**, Cycles CPU, 32 samples, AgX, soft studio light.
The vertical-down perspective camera is (0,0,47), north/+Y at image top, **42° vertical
FOV, 1280×720**. The current 720px maximum supersedes the older example's 800px height.
Obliques are rendered at 1280×720 then reduced to 1152×648 by `record.py`. Blender PNG
compression 95, evidence-only 6-bit RGB quantization and lossless PNG compression level 9
produce 213–275KB files. Quantization bands the studio gradients; model materials are not
changed. Self-review inspected all final views: the office reads as a subordinate lean-to
attachment, roof patches and amber entry marker remain visible overhead, and the broad
windows/door distinguish it from the work bays in close views. Facade detail is not claimed
readable directly overhead. Initial hero/side framing was widened to retain the silhouette.

Exact reproduction from repository root, isolated processes only:

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
T=tools/asset_production/d08_workshop_buildings_04
X=C:/tmp/ft/assets/d08_workshop_buildings_04
mkdir -p "$X"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py" > "$X/author-final.log" 2>&1
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" > "$X/validate-final.log" 2>&1
python "$T/record.py" --compress-renders
G="$(mise which godot)"
timeout 300 "$G" --headless --path . --import > "$X/import-final.log" 2>&1
timeout 180 "$G" --headless --editor --path . --script "res://$T/check_prefab.gd" -- --normalize > "$X/normalize.log" 2>&1
timeout 180 "$G" --headless --path . --script "res://$T/check_prefab.gd" > "$X/prefab-final.log" 2>&1
{ "$(mise which gdstyle)" fmt --check "$T/check_prefab.gd" && "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd"; } > "$X/style-final.log" 2>&1
python "$T/record.py"
python "$T/record.py" --verify
```

`validate.py` opens the saved source, measures raw GLB position/normal/index buffers,
asserts literal independent bounds, material face rays and actual sibling roof clearances,
compares palette definitions, and runs a fresh scratch export whose complete bytes must
match production. `export.py` also accepts `-- <output-directory>` against the saved source.
The [producer manifest](d08_workshop_buildings_04-evidence/manifest.json) hashes every produced
payload except itself. Scratch renders, retries and raw logs remain outside the repository;
one [concise final log](d08_workshop_buildings_04-evidence/final.log) retains final results
and unsuppressed editor diagnostics. `tools/production_checks.py` was **not run**, per owner
decision 52 for unplaced assets; import is not described as all-script validation.

## Validation and prefab collision

**5,412 triangles; 2,888 source vertices; 3,608 exported vertices (normal splits); one mesh;
eight surfaces.** Zero non-manifold source edges, degenerate source faces or degenerate
exported triangles. Source/export normals are unit length; winding agrees with exported
normals. Bounds, ground datum and source/export axis mapping pass. Exactly two exported
nodes; no cameras, lights, images, textures, skins or animation.

Final GLB: **125,772 bytes**, SHA-256
`7129a79526dbc7c92b8d3094be0924b9f4d073241aff8ff97a00c1f601649b19`.
The fresh export is byte-identical; these values are copied from the final validation
receipt and checked against the producer manifest before commit.

The office and family scenes were text-authored, loaded/packed/resaved by the pinned
headless editor, then reloaded/resaved byte-identically, retaining node IDs and UIDs.
`Visuals/Model` is an identity-transform linked GLB instance. One direct-child `BoxShape3D`,
`OfficeSolid`, under `Collision/Body` is **6 × 3 × 3m**, centred at **(0,1.5,0)**,
static-world layer 1 / mask 0. It blocks the complete closed office, including window and
door faces. Small applied trim is deliberately excluded; roof/infill above Y 3 is overhead
visual-only, not walkable. No copied render geometry, runtime-authored hierarchy or interior
opening. The family scene reuses the siblings' existing independent colliders.

Pinned Godot **4.8.dev7.official.c971f93e7** checks passed:

- Model/wrapper dependencies and identities, imported mesh ancestry, identity transforms,
  literal measured AABB, eight opaque/back-culling materials, one exact office collider.
- **Nine office capsule queries**, radius 0.35m / height 1.8m: closed volume, door/window
  wall and opposite corners solid; four perimeter routes clear. Front ray hits **Z -1.5**.
- Production `ActorMotion.step`, **60 ticks per case**, **AUTHORITY and REPLAY**: door and
  counter wall stop at **Z -1.850261m**, east wall at **X 3.350257m**, east bypass reaches
  approximately **Z 0**. All four paired endpoints are exactly equal. These are bounded
  static-physics checks, not multiplayer transport/admission proof.
- A **1.9 × 1.5 × 4.3m car-sized test box** is stopped at the office facade and clears
  the east bypass. This is a sweep, not production driving or turning-radius acceptance.
- Saved family ancestry/transforms, **zero office/host collider seam gap**, correct 3m bay,
  measured **9m central structural gap**, **nine family capsule queries** (three solid join
  samples, clear outside corners, both yard exits, yard centre and outer foot bypass),
  and three clear car-sized sweeps (both directions through the yard and outer bypass).
- Pinned **gdstyle 0.3.0** formatting and zero-warning lint on the added GDScript; Python
  syntax checks on all four added Python scripts.

Final import exited 0 without ERROR/SCRIPT ERROR; the existing toolkit 4.8 compatibility
warning remains. Headless editor normalization exited 0 with stable scenes but emitted the
existing aborted-scan and shutdown RID/ObjectDB leak diagnostics, retained in the final log.
Fresh non-editor resource/motion runtime exited 0 without ERROR/WARNING. Initial validation
needed its appended sibling mesh linked into the isolated scene before ray evaluation;
this was corrected. A GDScript local-variable warning and evidence-recorder string error
were corrected before final receipts. No failing check is counted as passing. No windowed
editor or owner's live Blender/Godot MCP session was accessed; headless import does not
synchronize any separate open editor, and no such synchronization is claimed.

## Remaining acceptance

- Independent technical/art review of this exact source/export/prefab candidate.
- World integration: selected district fit, actual placement of the comparison or equivalent
  linked instances, office joins in their final surroundings, usable two-exit yard and foot
  bypass, route clearances, production car turns and chain spacing. No world asset is placed.
- Native 47m/42° camera with actors/combat, populated-city visibility/occlusion, and actual
  authoritative/predicted behavior over separate network processes.
- Packaged-platform and Deck LCD/OLED review, sustained frame pacing, repeat-building
  draw/LOD/shadow cost and any future task lights. Isolated source/import evidence alone
  does not establish full game-ready production acceptance.
