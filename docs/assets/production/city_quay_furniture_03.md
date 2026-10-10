# city_quay_furniture.03 — Edge ladder

10 October 2026. **Source/export and linked-prefab candidate delivered; independent
review and world/gameplay/device acceptance pending.** Production commissioned by
Regner under [commission](commission.md) and the current per-asset common brief,
which supersede the concept-only restrictions in the
[waterfront furniture brief](../city_quay_furniture.md).

Producer: commissioned implementation specialist on `lane/a-quay`. Supervisor owns
independent acceptance and integration. The preceding [bollard](city_quay_furniture_01.md)
and [rail kit](city_quay_furniture_02.md) were inspected and remain unchanged. Shared
briefs, register, progress, project settings, gameplay scripts and world scenes are
unchanged. This delivery adds no climbing, swimming, boat or shore-boundary system.

## Design and dimensions

Original Blender construction: two continuous hooked tubular stiles, eight broad
flat rungs, two quay-top mounting plates, four wall stand-offs and restrained anchor
heads. Dark teal tubes, slate rungs/hardware and two short amber return-grip bands
match the other quay members. Smooth bends and coarse manufactured masses replace
grime, textured tread noise and tiny decorative fittings. No downloaded geometry,
real brands, artwork, textures, interiors, rigging, animation or damage states.

Dimensions are **provisional authored values**, not measurements inferred from
concept images or an approved waterfront interface. The standing instruction permits
sensible family-compatible dimensions. Envelope/datum tolerance is **±0.001 m**;
source-to-export bounds tolerance is **0.00001 m**.

| Property | Metres, Godot local axes unless stated |
| --- | --- |
| Visual size X / Y / Z | **0.940 / 3.380 / 0.7425** |
| AABB minimum | **(-0.470, -2.400, -0.3525)** |
| AABB maximum | **(+0.470, +0.980, +0.390)** |
| Quay-top / wall datum | **Y=0 / Z=0**; landward is +Z, water-facing is -Z |
| Root and mesh pivot | **(0,0,0)**, midpoint of the quay edge at mounting-surface height |
| Below-datum descent / above-datum reach | **2.400 / 0.980** |
| Stile centre spacing / tube diameter | **0.720 / 0.090** |
| Front stile / return centre Z | **-0.300 / +0.270** |
| Hook centreline bend radius / spring height | **0.285 / 0.650** |
| Rung count / vertical centre spacing | **8 / 0.300** |
| Rung size X / Y / Z | **0.720 / 0.065 / 0.105** |
| Rung centres Y | **-0.150 to -2.250** |
| Top mounting plates | **0.220 / 0.060 / 0.240**, centres X=±0.360, Y=0.030, Z=+0.270 |
| Wall plate size X / Y / Z | **0.180 / 0.220 / 0.040** |
| Wall plate centres | X=±0.360, Y=-0.650/-1.850, Z=-0.020; back faces at Z=0 |
| Amber bands | Return stiles, Y=0.300–0.550; material assignment, not an overlapping sleeve |

The top plate undersides contact Y=0. The installation pivot is **not the bottom of
the ladder**, and the ladder must not be dropped onto ordinary ground at its lowest
vertex. The exported datum allows the descent below an existing quay surface without
changing flat terrain or inventing a water elevation. Waterline, wall depth and actual
mount fit belong to integration. Metric units, applied static rotation/scale, unit
root/mesh transforms, no negative scale. Blender +Z maps to Godot +Y; Blender +Y
maps to Godot -Z. No corrective rotation or scale is required in the wrapper.

Keep the 0.390 m landward projection outside through-routes and loading positions;
keep mounting plates clear of rail posts and bollards. A ladder can fit inside the
rail sibling's **provisional 1.400 m opening** with 0.230 m lateral visual margin per
side, but this is a dimension comparison, **not a tested assembled access route**.
Do not infer a climbable opening or remove an existing shoreline blocker. The family
brief's **continuous, unobstructed quay** criterion remains a world-placement gate.
Old Quay and East Docks are supporting uses to confirm, not automatic coast-wide use.

## Source, export and materials

- Source: `art/source/models/environment/city_quay_furniture_03/city_quay_furniture_03.blend`.
- Named export collection: `export_city_quay_furniture_03`.
- Root: `CityQuayFurniture03`; one child: `CityQuayFurniture03_Mesh`.
- Explicit export: `art/models/environment/city_quay_furniture_03/city_quay_furniture_03.glb`
  and the pinned-engine `.glb.import` sidecar.
- Wrapper: `scenes/prefabs/environment/city_quay_furniture_03.tscn`.
- Parametric author, export, validation, finalization and bounded engine checks:
  `tools/asset_production/city_quay_furniture_03/`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**.
The exporter uses shared `tools/assets/blender/export_settings.json`, explicit
collection selection and Y-up conversion, with animation/skin export disabled.
Studio lights, camera and ground remain editable in the source but outside export
scope. No prototype dependencies, embedded images, external machine-local resources
or runtime-generated render geometry.

| Slot | Material | Linear base RGB | Metallic | Roughness |
| --- | --- | --- | --- | --- |
| 0 | `quay_dark_metal` | (0.025, 0.075, 0.090) | 0.45 | 0.46 |
| 1 | `quay_working_amber` | (1.000, 0.527, 0.102) | 0.00 | 0.42 |
| 2 | `quay_hardware_slate` | (0.115, 0.165, 0.185) | 0.55 | 0.40 |

Opaque, back-culled Principled materials match the siblings' names/PBR values. No
emission, real lights, textures, UV maps, external material overrides, sockets, rigs,
clips or destruction states are required. Uniform paint needs no UV allocation.
Godot's automatic LODs, shadow meshes and compression remain enabled at import
defaults. These counts are not an approved repeated-placement performance budget.

All component shells are closed and joined into one static mesh. Rung ends seat
inside stiles; return feet seat inside top plates; stand-offs seat inside wall
plates and front stiles. Anchor heads seat slightly into plates. These intentional
manufactured overlaps are not boolean-welded joints or exposed coplanar surfaces.

## Prefab and bounded engine checks

The imported GLB remains linked at **`Visuals/Model`, identity transform**. No copied
mesh, imported-child override or authored placement generated at runtime. The scene
was text-authored because the production brief prohibits live/windowed editors, then
loaded, packed and resaved through the pinned headless Godot. Inline scene/node IDs
and the check script's `.gd.uid` are retained. No owner's live process was touched;
no separate open-editor synchronization is claimed.

One static body at **`Collision/LadderBody`**, layer **1**, mask **0**, has a minimal
three-box compound, separate from visuals:

| Shape | Size X/Y/Z | Centre X/Y/Z |
| --- | --- | --- |
| Lower ladder | **0.900 / 2.400 / 0.3525** | **0 / -1.200 / -0.17625** |
| Left handle | **0.220 / 0.980 / 0.7425** | **-0.360 / 0.490 / +0.01875** |
| Right handle | **0.220 / 0.980 / 0.7425** | **+0.360 / 0.490 / +0.01875** |

The lower box conservatively fills the rung and stand-off gaps; the handle boxes
fill the hooked returns and mounting feet without fine snagging hardware collision.
The upper centre remains open to rays, but its 0.500 m collision gap is narrower
than the 0.700 m actor capsule. This is **non-climbable decorative hardware**, not a
walkable ladder, water barrier or permission to cross a waterfront boundary. Later
integration owns the enclosing quay and shoreline collision. No navigation or
interaction component is added.

Pinned Godot **4.8.dev7.official.c971f93e7** checks establish:

- Recursive dependency and resource-UID resolution for wrapper, import and fixture.
- Linked ancestry, identity visual instance, one mesh/three opaque back-culled
  surfaces, and actual engine bounds matching the independent table above.
- Wrapper and collision-only fixture pack/save/reload/resave **byte-identically**;
  a subsequent fresh process loads and verifies the same registered IDs.
- A below-quay ray hits the actual ladder body; both handles block rays; the upper
  centre and a ray above the handles remain clear.
- Production **`ActorMotion.step`**, with production **radius 0.35 m / height 1.8 m
  capsule**, runs 48 ticks per case in AUTHORITY and REPLAY. A landward approach at
  X=0.36 stops at **(0.360000014, 0.001, 0.749999642)**. Bypass at X=1 reaches
  **(1, 0.001, -2.000000715)**. Both modes give identical outcomes.

The contact expectation is Z=0.740 m with 0.00001 m floating-point tolerance and a
maximum **0.030 m conservative precontact gap**. No collision or gameplay code was
changed to accommodate the observed approximately 10 mm gap. The saved fixture uses
only a linked ladder, production motion script, and collision-only floor/capsule
primitives in the owned tools folder. The floor supports a controlled contact test;
it is not a modeled shoreline, real placement or proof of water/fall behavior.
Vehicle contact/turning and actual multiplayer transport/admission/prediction remain
unproved. These bounded public-API checks do not replace those gates.

## Evidence and reproduction

[Hero](city_quay_furniture_03-evidence/hero.png),
[side](city_quay_furniture_03-evidence/side.png),
[handle/mount detail](city_quay_furniture_03-evidence/detail.png),
[47 m / 42° overhead](city_quay_furniture_03-evidence/overhead_47m_42deg.png).
All four are isolated **Blender** views, **1280×720**, Cycles CPU, 32 samples, AgX,
broad studio fill. Overhead is vertical-down perspective, 47 m above installation
Y=0, 42° vertical FOV, Blender +Y at image top. The common brief's 720-pixel maximum
supersedes the historical 1280×800 example. Ground is a studio plane below the
ladder bottom, not a claimed quay or waterline.

All final views were inspected. Close views preserve the broad rung rhythm, hooked
handles and quiet family metal/amber; overhead is intentionally small, dominated by
the two handles and upper rung rather than enlarged safety paint. Rungs and anchors
are not essential gameplay cues. The studio fill light was moved above the studio
floor after its initial intersection made a distracting lighting patch. No production
mesh change was involved. Engine lighting and populated-quay readability remain open.
RGB renders use seven significant bits/channel and maximum PNG compression, targeting
approximately 400 KB per image; exact final sizes are in validation.json.

Final source/export measures:

- **2,352 source vertices / 2,264 source faces / 4,576 triangles**.
- **2,480 exported vertices / one mesh / three surfaces**.
- **Zero degenerate faces, zero degenerate triangles, zero non-manifold edges**.
- Maximum unit-normal length error: source **1.50e-7**, exported **1.02e-7**.
- GLB **89,752 bytes**; fresh re-export **byte-identical**.
- Source/export/engine and production-check receipts:
  [validation.json](city_quay_furniture_03-evidence/validation.json).
- SHA-256 for every delivered payload except the self-referential manifest:
  [manifest.json](city_quay_furniture_03-evidence/manifest.json).
- Concise command/diagnostic receipt: [checks.log](city_quay_furniture_03-evidence/checks.log).

Run from repository root in Git Bash; all scratch outputs stay outside the checkout:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
NID=city_quay_furniture_03
SCRATCH="C:/tmp/ft/assets/$NID"
mkdir -p "$SCRATCH"

ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# Optional explicit export: validate.py already exports and byte-compares.
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$BLENDER" \
  -noaudio --background "art/source/models/environment/$NID/$NID.blend" \
  --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/export.py" -- "$SCRATCH/reexport"
python "tools/asset_production/$NID/finalize.py" --compress-renders

timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script "res://tools/asset_production/$NID/check.gd" -- --normalize
# Re-import after assigning new scene identities, before fresh-process checking.
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script "res://tools/asset_production/$NID/check.gd"
timeout 60 "$(mise which gdstyle)" check "tools/asset_production/$NID/check.gd"
# Requires a fresh output folder; use another suffix for later runs.
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks"
python "tools/asset_production/$NID/finalize.py" --checks "$SCRATCH/checks"
```

Repository production checks **passed**: script formatting/style/compilation,
**16 Python tests**, **149 GUT tests / 6,768 assertions**, and the intentional-failure
negative control. Asset GDScript passes pinned **gdstyle 0.3.0**, with initial local
format/function-length warnings corrected. No known-failure exemption was needed.
The attempted `gdstyle format --check` syntax is unsupported on this pin; the actual
canonical production formatting check passed. Final asset checks have no errors or
warnings. Blender source runs emit only future-6.0 `use_nodes` deprecation notices;
the separate `--version` call emitted a 23-byte shutdown allocation diagnostic.
Project import reports the existing MCP toolkit 4.8-versus-tested-4.7 warning. No
vendor code, diagnostic filter or global tool configuration was changed.

## Remaining acceptance

- Supervisor: independent art/technical review at the committed candidate.
- Layout/interface owners: approve provisional dimensions, quay-top/wall mounting,
  waterline and descending extent; check real rail/bollard adjacency.
- World owner: sparse supporting placements, uninterrupted pedestrian/loading routes,
  enclosing quay collision and authoritative waterfront boundaries. No climb/swim use.
- Art/integration owner: actual Godot lighting and populated gameplay-camera visibility;
  isolated Blender renders do not establish engine or final-camera acceptance.
- Gameplay owner: actual vehicle contacts/turns and separate-process multiplayer
  movement/query checks at selected placements.
- Device/performance owner: packaged build, repeated-placement and Deck profiling.

No source/export/prefab blocker remains. Shared export settings, production-check
runner and production motion APIs are reused; there is no new shared framework or
runtime system. These downstream gates are intentionally pending, not claimed ready.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
