# city_quay_furniture.02 — Low quay rail

10 October 2026. **Source/export and linked-prefab candidate delivered; independent
review and world/gameplay/device acceptance pending.** Production commissioned by
Regner under [commission](commission.md) and the current per-asset common brief,
which supersede the concept-only restrictions in the
[waterfront furniture brief](../city_quay_furniture.md).

Producer: commissioned implementation specialist on `lane/a-quay`. Supervisor owns
independent acceptance and integration. The preceding
[mooring bollard](city_quay_furniture_01.md) was inspected and is unchanged. Its dark
teal/slate materials and restrained working amber supply the family language. No
shared brief, register, progress, project setting, other asset or world scene changed.

## Design and dimensions

Original Blender construction: a quiet two-height tubular rail with capped square
posts, a smoothly bent 90-degree corner, a closed hairpin terminal return, and three
mounting feet. The quay mount has a square anchor plate; the deck mount has a narrow
rectangular plate; the landward hardstanding mount has a round flange. All three are
surface-mounted at the same datum. Simple slate shoes and a narrow amber collar
connect visually to the bollard without repeating its broad mooring-head silhouette.
No ropes, brands, artwork, textures, interiors, rigging, damage or new interactions.

Dimensions are **provisional authored values**, not measurements from concept
images or an approved boardwalk interface. The standing production instruction
permits proceeding with sensible family-compatible values. Envelope tolerance:
**±0.001 m**; source/export bounds agreement: **0.00001 m**.

| Feature | Metres |
| --- | --- |
| Complete post height | **1.060**, ground contact at Godot Y=0 |
| Straight span connector spacing | **3.000** along X |
| Top handrail centre / diameter | **0.950 / 0.100** |
| Lower rail centre / diameter | **0.480 / 0.060** |
| Upright section | **0.110 × 0.110** |
| Slate post cap | **0.150 × 0.060 × 0.150**, X/Y/Z |
| Amber collar | **0.122 × 0.030 × 0.122**, centre Y=0.990 |
| Quay mounting plate | **0.300 × 0.060 × 0.300**, X/Y/Z |
| Deck mounting plate | **0.220 × 0.040 × 0.340**, X/Y/Z |
| Landward flange | **0.320 diameter × 0.050 high** |
| Corner nominal legs / centreline bend radius | **1.500 / 0.200** |
| End return outer reach from supporting post | **+0.535 X**, no loose projecting tube end |
| Terminal hairpin centreline radius | **0.235**, joins heights 0.950 and 0.480 |

Complete wrapper envelopes (Godot local X/Y/Z):

| Form | Quay size | Deck size | Landward size |
| --- | --- | --- | --- |
| Straight | 3.300 / 1.060 / 0.300 | 3.220 / 1.060 / 0.340 | 3.320 / 1.060 / 0.320 |
| Corner | 1.800 / 1.060 / 1.800 | 1.720 / 1.060 / 1.840 | 1.820 / 1.060 / 1.820 |
| End return | 0.685 / 1.060 / 0.300 | 0.645 / 1.060 / 0.340 | 0.695 / 1.060 / 0.320 |
| Post | 0.300 / 1.060 / 0.300 | 0.220 / 1.060 / 0.340 | 0.320 / 1.060 / 0.320 |

Straight, corner and post wrapper AABBs are centred in X/Z, with minimum Y=0 and
maximum Y=1.060. The terminal root is at its **ground-contact post centre**, not
its asymmetric overhang centre: X minimum is -0.150/-0.110/-0.160 for quay/deck/
landward respectively, X maximum +0.535; Z is half the listed depth each side.
The measured source, export and assembled engine AABBs are in
[validation.json](city_quay_furniture_02-evidence/validation.json).

Metric units, unit root scale, applied object rotation/scale, no negative scale.
Blender +Z maps to Godot +Y; Blender +Y maps to Godot -Z. Straight runs are along X;
the corner turns east toward north (-Z). The isolated span components use the
**installation ground datum**, so their pivots are Y=0 even though the tubes begin
above it. All complete wrappers have actual mounting feet at that datum.

## Components, connectors and reuse

One source: `art/source/models/environment/city_quay_furniture_02/city_quay_furniture_02.blend`.
Six collections, each `export_city_quay_furniture_02_<component>`, export explicitly
to `art/models/environment/city_quay_furniture_02/city_quay_furniture_02_<component>.glb`.
Each has root `CityQuayFurniture02_<component>` and one joined child named the same
plus `_Mesh`. Each GLB retains its engine-generated `.glb.import` sidecar.

| Component | Purpose / source-independent connector contract, Godot local metres |
| --- | --- |
| `straight` | Upper/lower tubes, ends at X=-1.500 and +1.500, Z=0; connector heights Y=0.950/0.480 |
| `corner` | Ends at X/Z=(-0.750,+0.750) and (+0.750,-0.750); same heights; end tangents +X and -Z |
| `end` | Both attachment ends at X/Z=(0,0), Y=0.950/0.480; return projects +X |
| `post_quay` | Complete square-plate post, installation pivot at the plate centre |
| `post_deck` | Complete rectangular-plate post, long plate axis Z |
| `post_landward` | Complete round-flange post for landward hardstanding |

The straight wrapper positions posts at X=±1.500. The corner has its two endpoint
posts and one supporting the midpoint of the actual rounded bend at
**(0.691421356, 0, 0.691421356)**, not at the nominal sharp corner. The terminal has
one post at the origin. Tube end caps are enclosed inside the receiving post; shoe,
flange, collar and cap overlaps are intentional seated manufactured parts. Each
individual source shell is closed and manifold; this is not a boolean-welded casting.

The six GLBs are the reusable building parts: **do not butt complete standalone
wrappers together at a shared post**, which would double the same support. For a
long or branching rail, author a saved assembly from these linked components with
one post per junction and one continuous simple collision envelope per run. For
example, two straight spans centred at X=0 and X=3 use posts at X=-1.5, +1.5 and
+4.5, not two posts at +1.5. Replace a shared final support with the terminal's post
rather than stacking another on it. No runtime construction or placement writer is
introduced. The component datums allow `city_barriers.02/.04` to compose the shared
rail without a second rail mesh family; those records and their assemblies are not
modified here.

Use sparse edge placement and deliberately omit spans at access/loading positions.
A saved test-only pair of opposite terminals demonstrates a **1.400 m clear opening**
with post centres X=±1.235. That provisional sample does not choose actual route
widths or locations. Keep mount/anchor footprints outside the walking line and fix
deck plates to structural support, not an assumed board thickness. Deck/coast fits,
corner placement and the brief's **continuous, unobstructed quay** criterion remain
world/interface gates. No continuous East Docks promenade, lighthouse gallery rail,
raised-bridge interface, shoreline change, climbing or swimming is authorized.

## Materials, source and export contract

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. `export.py`
uses shared `tools/assets/blender/export_settings.json`, explicit collection filters,
Y-up conversion, normals, and no animations/skins. No prototype dependencies,
embedded images, external machine-local assets or generated runtime render meshes.
Studio cameras, lights, ground and linked preview objects remain outside every
export collection. Construction is reproducible in the owned `author.py`; all six
editable meshes are retained in the source.

| Material | Linear base RGB | Metallic | Roughness |
| --- | --- | --- | --- |
| `quay_dark_metal` | (0.025, 0.075, 0.090) | 0.45 | 0.46 |
| `quay_hardware_slate` | (0.115, 0.165, 0.185) | 0.55 | 0.40 |
| `quay_working_amber` | (1.000, 0.527, 0.102) | 0.00 | 0.42 |

Opaque back-culled Principled materials; no emission or real lights. The three span
meshes have only dark-metal slot 0. Post meshes use slots 0 dark metal, 1 slate,
2 amber. Names and PBR values match the preceding bollard; cross-asset slot indices
are not an appearance API. No textures, UV maps, external materials, sockets, rigs,
clips, destruction states or explicit LODs are needed. Automatic Godot LODs, shadow
meshes and mesh compression remain at imported defaults; profiling is pending.

## Prefabs and bounded engine checks

Twelve wrappers under `scenes/prefabs/environment/`:

- `city_quay_furniture_02.tscn`: the default complete **straight/quay** assembly.
- `city_quay_furniture_02_straight_deck.tscn` and `_straight_landward.tscn`.
- `city_quay_furniture_02_corner_<mount>.tscn`, `_end_<mount>.tscn` and
  `_post_<mount>.tscn`, where `<mount>` is `quay`, `deck` or `landward`.

Each wrapper has its primary imported component at **`Visuals/Model`, identity
transform**. Complete rails also instance the same reusable post GLB as authored
`Visuals/Post0` etc. These are deliberate connector placements, not corrective
model transforms. No meshes are embedded or copied into scenes, and no imported
children or material slots are overridden. `prefabs.py` creates missing text scenes
only; it never overwrites existing scene/node identities. Godot then packs/resaves
them and checks a second byte-stable save. Scene UIDs are inline; the check script's
`.gd.uid` is retained.

All wrappers block actors/cars with **one `Collision/RailBody` static body**, layer
**1**, mask **0**, separate from visuals. Straight, terminal and post use one box
covering their installation footprint from Y=0 to 1.060. The corner uses **two thin
boxes in an L**, preserving its open interior; it is not a filled square. These
conservative envelopes intentionally fill the visual under-rail gaps and the narrow
space around feet, with no bolt, tube or shoe snag colliders. The visual rail is not
being delivered as a see-through physical barrier or as authorization for crawling.

Pinned Godot **4.8.dev7.official.c971f93e7** headless checks establish:

- All twelve wrappers load; recursively loaded dependency/resource UIDs resolve.
- Imported links, identity `Visuals/Model`, post positions, actual aggregate bounds,
  mesh/surface counts and opaque back-culled materials match independent expectations.
- Twelve wrappers plus the collision-only fixture and inherited opening fixture
  pack/save/reload/resave byte-identically. A post-normalization import registers
  newly created UIDs before the final fresh-process load check.
- Every mounting/form combination blocks a low ray and clears a ray above the rail;
  both corner arms block while the inner area is clear.
- Production **`ActorMotion.step`**, with the production **radius 0.35 m / height
  1.8 m capsule**, runs 48 ticks per contact/bypass case in both AUTHORITY and REPLAY.
  Results match across modes for all twelve wrappers. Bypass at X=2.5 ends at
  Z=2.000000715 m. Quay contact is approximately Z=-0.500000, deck -0.520833 and
  landward -0.511067; corner contact planes are 0.750 m farther north-to-south along
  the tested trajectory, yielding about +0.250000/+0.229167/+0.238933 respectively.
- The saved 1.4 m access opening passes the actor at X=0, while both terminal returns
  block at X=±0.9. AUTHORITY and REPLAY outcomes match.

Contact assertions allow **0.00001 m numeric tolerance**, not visible penetration,
and at most **0.030 m precontact gap** for conservative physics advancement. The
initial exact comparison rejected a sub-micrometre float difference; the initial
bounds helper also missed an imported grandparent transform. Both were test-harness
corrections, not collision or production-motion changes. The first fresh-process
opening check lacked the newly assigned UID in its cache; the subsequent import
and fresh check passed. No error was broadly suppressed.

These are bounded actor/query checks, not actual vehicle handling or multiplayer
transport/admission/prediction proof. Test fixtures are confined to the owned tools
folder, use only collision-only floor/capsule primitives, and do not place assets
in the city or add a test fixture under the prohibited shared path.

## Evidence and reproduction

[Hero kit view](city_quay_furniture_02-evidence/hero.png),
[straight side](city_quay_furniture_02-evidence/side.png),
[three mounting feet detail](city_quay_furniture_02-evidence/detail.png),
[47 m / 42° overhead](city_quay_furniture_02-evidence/overhead_47m_42deg.png).
All are isolated **Blender** renders at **1280×720**, Cycles CPU, 32 samples, AgX,
broad studio fill. The overhead is vertical-down perspective, 47 m above datum,
42° vertical FOV, Blender +Y image-up. The current common brief's 720-pixel maximum
supersedes the historical 1280×800 example. RGB PNGs use seven significant bits per
channel and maximum compression, approximately **352–435 KiB** each.

All four final views were inspected. The final side isolates the straight run and
avoids the first camera's ground crop; the detail isolates the three mounting feet.
Broad caps and tubes read as a thin, quiet boundary overhead; no oversized amber
stripe was added to compete with actors. The rail fits the bollard's manufactured
material language. Small anchors are close-view detail, not gameplay cues. These
renders do not claim Godot lighting or populated-quay readability acceptance.

| Component | Source vertices / faces | Triangles | Export vertices | Meshes / surfaces | GLB bytes |
| --- | --- | --- | --- | --- | --- |
| Straight span | 64 / 36 | 120 | 128 | 1 / 1 | 4,964 |
| Corner span | 352 / 324 | 696 | 416 | 1 / 1 | 15,332 |
| Terminal return | 304 / 290 | 604 | 336 | 1 / 1 | 12,876 |
| Quay post | 504 / 486 | 972 | 504 | 1 / 3 | 20,700 |
| Deck post | 504 / 486 | 972 | 504 | 1 / 3 | 20,700 |
| Landward post | 592 / 554 | 1,148 | 592 | 1 / 3 | 23,880 |

**4,512 unique component triangles**, 2,320 source vertices, 2,480 exported
vertices, six meshes and twelve surfaces across the six exports. **Zero degenerate
faces, zero degenerate triangles, zero non-manifold edges**. Maximum normal-length
error: source **1.73e-7**, export **1.09e-7**. All **six fresh exports byte-identical**.
The default complete quay straight draws three imported meshes/seven surfaces and
2,064 triangles; the complete quay corner is four meshes/ten surfaces, 3,612
triangles. These are counts, not an accepted performance budget.

Machine-readable measures, engine checks and production-check receipts:
[validation.json](city_quay_furniture_02-evidence/validation.json).
SHA-256 of every delivered payload, excluding the self-referential manifest:
[manifest.json](city_quay_furniture_02-evidence/manifest.json).
Concise command/diagnostic receipt:
[checks.log](city_quay_furniture_02-evidence/checks.log).

Run from the repository root in Git Bash. The production brief forbids live MCP and
windowed editors; original source construction uses isolated pinned Blender CLI.
Prefabs were text-authored and normalized in isolated pinned headless Godot. No
owner editor process was touched, and no open-scene synchronization is claimed.
Scratch renders, reexports and raw logs remain outside the checkout.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
NID=city_quay_furniture_02
SCRATCH="C:/tmp/ft/assets/$NID"
mkdir -p "$SCRATCH"

ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# Optional explicit export; validate.py already fresh-exports and compares all six.
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$BLENDER" \
  -noaudio --background "art/source/models/environment/$NID/$NID.blend" \
  --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/export.py" -- "$SCRATCH/reexport"
python "tools/asset_production/$NID/prefabs.py"
python "tools/asset_production/$NID/finalize.py" --compress-renders

timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script "res://tools/asset_production/$NID/check.gd" -- --normalize
# Register any newly assigned scene IDs before the fresh-process check.
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script "res://tools/asset_production/$NID/check.gd"
timeout 60 "$(mise which gdstyle)" check "tools/asset_production/$NID/check.gd"
# The output directory must be fresh; choose another suffix for subsequent runs.
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks"
python "tools/asset_production/$NID/finalize.py" --checks "$SCRATCH/checks"
```

Final repository production checks **passed**: owned-script style/format/compilation,
**16 Python tests**, **149 GUT tests / 6,768 assertions**, and the intentional-failure
negative control. Asset-specific GDScript passes pinned **gdstyle 0.3.0**. No known
failure exemption was needed. Final asset-check logs have no errors/warnings.
Blender reports only the pin's future-6.0 `use_nodes` deprecation; project import
reports the existing MCP toolkit 4.8-versus-tested-4.7 warning. No vendor changes or
broad diagnostic suppression.

## Remaining acceptance

- Supervisor: independent technical/art review at the committed candidate.
- Layout/interface owners: approve provisional dimensions, deck/quay/landward mount
  fit and saved component assemblies; preserve one support per shared junction.
- World owner: actual sparse placements, access openings, loading clearances,
  boardwalk terminals and unobstructed shoreline paths. No East Docks ring route.
- Art/integration owner: actual engine lighting, populated gameplay-camera visibility
  and actor contrast. Blender studio images are not engine captures.
- Gameplay owner: vehicle contacts/turns and real separate-process network behavior
  at selected placements. The conservative filled under-rail envelope is explicit.
- Device/performance owner: packaged builds, repeated-placement draw cost and Deck
  performance. No sustained GPU/frame-budget claim is made.

No source/export/prefab blocker remains. Shared export settings, production-check
runner and production motion APIs are reused; no speculative shared framework or
new gameplay system was introduced. Downstream acceptance remains deliberately open.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
