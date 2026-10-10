# d09_freight_graphics.03 — Loading-location sign

10 October 2026. **Artwork/material set and inherited sign prefabs delivered; independent
review, placement and gameplay/device acceptance pending.** Commissioned by Regner under
[production commission](commission.md) and current asset-common standing rules, superseding
historical concept-only restrictions. Producer: assigned isolated worker on `lane/a-freight`.
Accepting owners: independent art/technical reviewers, then world/gameplay/device owners.
This delivery is not a registry-ready or world-placement verdict.

References: [freight family](../d09_freight_graphics.md), earlier
[warehouse fascia](d09_freight_graphics_01.md) and [container IDs](d09_freight_graphics_02.md),
[wall carrier](city_sign_supports_01.md), [low carrier](city_sign_supports_02.md),
[East Docks identity](../../concepts/world-v1/stage-03-district-identities/README.md#east-docks--the-city-ends-at-work),
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md).
Neither earlier freight handoff has a stale pending loading-sign item, so neither its
handoff nor manifest needed editing. No sibling, shared source, brief, queue, progress,
world scene, project settings or historical receipt was changed.

## Design, provenance and family seam

Two native-aspect layouts for the same fictional location **04**:

- Wall: broad amber **LOADING**, large ivory **04**, amber parcel-clock, quiet steel
  **FREIGHT** and three cargo bars.
- Low freestanding: parcel-clock beside **FREIGHT / LOAD 04**, with three separated steel
  cargo bars in the upper corner.

The original rounded industrial capital paths, parcel-clock joke and palette continue
**Urgent Eventually Freight** from the earlier siblings. `author.py` imports the container
art's glyphs read-only (which imports the fascia glyphs) and adds only O/D outlines. No
external font, real brand, downloaded image, image generation, purchased geometry, raster
pixel font or borrowed logo. All graphics are original Python/Pillow vector construction.
Location 04 is decorative visual copy, **not a saved entity identity, gameplay destination,
navigation instruction, inventory state or road/loading-bay marking**. No directional arrow,
route rule, crane control or freight simulation is introduced. Final copy remains provisional.

| Family role | sRGB | Use |
| --- | --- | --- |
| Quiet field | `#143344` | Cool petrol-steel; more than 60% of each texture |
| Emblem / heading | `#FFC05A` | Warm amber working accent |
| Location | `#F6F1DC` | Large ivory primary copy |
| Cargo bars / secondary copy | `#85929D` | Quiet cool steel |

Keep these as **separated loading-edge clusters**, not dense bright sign walls. The two
layouts are alternatives for different existing supports, not a request to place both at
every bay. Large quiet aprons and broad warehouse roofs must remain dominant. The district's
5.03 ha is context, not this family's allocation or a new placement plan.

## Source, outputs and dimensions

The standing **reuse rule** applies: both shared supports already own Blender-sourced,
UV-mapped face geometry. No redundant per-ID `.blend`, GLB, new panel mesh or export script
is produced. Owned `validate.py` delegates fresh export to the existing carrier owners,
using only scratch destinations. New prefabs **inherit the existing carrier wrappers**,
preserving their linked geometry and collision instead of copying either.

| Variant | Existing owner | New prefab |
| --- | --- | --- |
| Wall | `city_sign_supports_01` | `scenes/prefabs/environment/d09_freight_graphics_03.tscn` |
| Low freestanding | `city_sign_supports_02` | `scenes/prefabs/environment/d09_freight_graphics_03_low.tscn` |

For each `<carrier>` above:

- Source: `art/source/models/environment/<carrier>/<carrier>.blend`.
- Collection: `export_<carrier>`; root `CitySignSupports01` or `CitySignSupports02`.
- Export: `art/models/environment/<carrier>/<carrier>.glb`, with existing `.import`.
- Wrapper: `scenes/prefabs/environment/<carrier>.tscn`.
- Existing exporter: `tools/asset_production/<carrier>/export.py`; wall owner validates its
  selected member set through `perform`, low owner uses the shared
  `tools/assets/blender/export_settings.json`. No shared export settings were changed.

New runtime outputs for `<variant>` = `wall` or `low`:

- `art/textures/environment/d09_freight_graphics_03/loading_<variant>_albedo.png`, plus
  engine-generated `.import`: wall **1220 x 820**, low **1440 x 390**, opaque RGB sRGB,
  1000 px/metre. Python **3.14.2**, Pillow **12.3.0**, 3x supersampled paths with one Lanczos
  downsample. No alpha, normal, ORM or embedded image dependencies.
- `art/materials/environment/d09_freight_graphics_03/loading_<variant>.tres`: white
  multiplier, metallic **0**, roughness **0.62**, opaque, back-culled, no emission.
  Linear mipmapped filter, clamp/no repeat, lossless texture import, mipmaps enabled,
  automatic 3D compression conversion disabled.
- Owned `author.py`, `validate.py`, `preview.py`, artwork tests, headless prefab check and
  receipt tool under `tools/asset_production/d09_freight_graphics_03/`.

| Interface | Wall | Low freestanding |
| --- | --- | --- |
| Whole Godot X/Y/Z metres | **1.40 / 1.00 / 0.10** | **1.60 / 1.35 / 0.40** |
| AABB minimum | **(-0.70,-0.50,-0.10)** | **(-0.80,0,-0.20)** |
| AABB maximum | **(0.70,0.50,0)** | **(0.80,1.35,0.20)** |
| Pivot `(0,0,0)` | Wall-contact centre | Ground-centred feet |
| Face width / height metres | **1.22 / 0.82** | **1.44 / 0.39** |
| Face Godot Z | **-0.088** | **-0.071** |
| Face centre Godot Y | **0** | **1.075** |
| Safe copy width / height | **1.14 / 0.74** | **1.38 / 0.33** |
| Authored quiet outer margin | **40 pixels / 0.040 m** | **30 pixels / 0.030 m** |
| Image aspect | **61:41** | **48:13** |

Dimensions are the existing carriers' **provisional authored values**, not measurements
inferred from district images or newly accepted world clearance. The wall's provisional
**1.60 m centre mounting** gives lower/upper edges at **1.10 / 2.10 m**. Mount it flush on
an existing opaque facade away from openings and passage mouths. Do not use the wall variant
as freestanding hardware. Low sign feet sit on local ground; its full blocking envelope
must stay outside escape routes, loading turns and sightlines.

UV0 is the existing `UVMap`: U increases toward Blender/Godot -X (screen-right when facing
the sign); V increases toward Blender +Z, with glTF stored V=0 at image top. Rounded carrier
corners clip the field, not the safe-copy area. Front is Blender +Y, mapped once to Godot -Z;
up is Blender +Z to Godot +Y. Root, Visuals, Model and imported mesh transforms remain
identity, without corrective scaling/rotation. Envelope tolerance ±0.001 m; source/binary
bounds and UV mapping are checked within 0.000001 m. No rig, animation, sockets, interior,
destruction, LOD redesign or new runtime script is needed for these static graphics.

## Saved face overrides, collision and identity retention

Only `surface_material_override/0` on the original `sign_face` slot is changed:

- Wall: `Visuals/Model/CitySignSupports01/artwork_carrier`.
- Low: `Visuals/Model/CitySignSupports02/CitySignSupports02_ArtworkCarrier`.

The rear/side `mount_metal` slot and all remaining hardware stay unchanged. This uses the
[authorized static-artwork editable-child face-slot exception](../../assets.md#prefabs-and-authored-placement):
linked GLBs unchanged, no geometry copied, no whole-object override, **two byte-stable
save/reload cycles per prefab/material**, plus a fresh-process initial-byte stability check.
The engine check compares every mesh resource, local transform, material override and
collision resource with an independently instantiated pristine carrier wrapper. Saved bytes
retain imported-child identities/UIDs; future carrier hierarchy changes require a fresh
check, not an assumption that arbitrary reexports preserve the interface.

The wall stays visual-only: its opaque facade owns blocking; flush art adds no collider.
The low sign retains the original **one StaticBody3D / one BoxShape3D**, size
**(1.60,1.35,0.40)**, centre **(0,0.675,0)** at `Collision/Body/Shape`, layer **1**, mask **0**.
It is the same inherited shape resource, not a duplicate. Its intentional full box blocks
the visual under-panel gap, as approved by the support owner. No physics/gameplay authority
or collision envelope changes; the support's historical movement tests are not claimed as
newly run here.

| Resource | Wall UID | Low UID |
| --- | --- | --- |
| New prefab | `uid://bk7p6d2yyghbc` | `uid://blih3uh44drmc` |
| New material | `uid://beawdbl265nnn` | `uid://dljgdwuts225q` |
| New texture | `uid://dwh6dn3nbsk56` | `uid://dc2cis5tghcj` |
| Inherited carrier prefab | `uid://byqodl735ss1a` | `uid://bi65yynmg6q4t` |

Godot stores scene/material UIDs inline, texture UIDs in `.import`, and the check script UID
in `.gd.uid`. It emits no separate `.tscn.uid` or `.tres.uid` here. Live MCP/editor sessions
were forbidden and the windowed editor unavailable, so text resources were loaded, packed
and resaved through isolated pinned headless Godot resource APIs. Final import and fresh
checks resolve all dependencies. No live open scene was touched or claimed synchronized.

## Evidence and measured checks

[Wall hero](d09_freight_graphics_03-evidence/hero.png) ·
[low sign side](d09_freight_graphics_03-evidence/side.png) ·
[parcel-clock/frame detail](d09_freight_graphics_03-evidence/detail.png) ·
[both supports at 47 m / 42 degrees](d09_freight_graphics_03-evidence/overhead_47m_42deg.png).

All four are isolated **Blender Cycles CPU, 32 samples, AgX, 1280 x 720**, PNG compression
100 with evidence-only seven-bit RGB reduction. Each is below 400 KiB; runtime artwork is
not color-reduced. Exact cameras and two area lights are in `preview.py`; source files are
opened read-only and never saved. Overhead is vertical-down perspective, north-up, camera
**(0,8,47)** in Blender with **42-degree vertical FOV**. Only translations separate existing
carriers: wall root **(-1.5,0,1.6)**, low root **(1.5,0,0)**. No facade fixture, artificial
tilt, geometry scaling or runtime placement was created to improve that view.

Producer inspected both runtime textures, all four final compressed renders and the earlier
fascia hero. Copy is upright/unmirrored, the emblem remains intact, quiet gutters separate
clusters, rounded edge clipping stays clear of copy, and the original frame remains visible.
The detail intentionally crops the headline/right number to inspect parcel and frame seating.
At gameplay distance each sign is roughly a **30-pixel-wide strip**, only a few pixels high;
**neither location nor headline is reliably readable**. They are warm local accents, not
an essential overhead navigation cue or landmark. A centred vertical face can be fully
edge-on. Actual populated-world camera readability/occlusion remains pending; this limitation
is not addressed by inventing a roof sign, enlarging hardware or introducing road markings.

Final [validation.json](d09_freight_graphics_03-evidence/validation.json):

| Measured unchanged carrier | Wall | Low |
| --- | ---: | ---: |
| Source vertices | **1,380** | **1,244** |
| Export vertices with splits | **1,792** | **1,596** |
| Triangles | **2,720** | **2,448** |
| Meshes / surfaces | **12 / 13** | **2 / 5** |
| Front artwork triangles | **34** | **26** |
| Degenerate source faces / exported triangles | **0 / 0** | **0 / 0** |
| Non-manifold source edges | **0** | **0** |
| Maximum source normal-length error | **1.5701515287958046e-7** | **1.6880220243820077e-7** |
| Maximum GLB normal-length error | **1.2842246266409063e-7** | **1.0989605780942213e-7** |
| Fresh byte-identical GLB size | **75,768 bytes** | **70,712 bytes** |

**No new geometry.** Applied metre transforms, pivots, bounds, source topology, outward
binary winding and actual front UV accessors pass. Blender **5.2.2 LTS**, build
**d13f752e3b9c**, glTF exporter **5.2.40** reproduce both shared GLBs byte-for-byte:

- Wall SHA-256: `5f54105825e00bb73c038bed252910abec548ad1beb81603b2713c2c69796e0b`.
- Low SHA-256: `022dd559334d79c482182083be775c692ab4adf2a5277d3fb7ca7ec266ec76b7`.

Four artwork tests pass: exact format/dimensions/quiet safety margins; independent emblem,
clock-hand, gutter and cargo-bar pixels; preserved family/native aspects; both fresh PNG byte
streams identical to committed artwork. Pinned **Godot 4.8.dev7.official.c971f93e7** final
import, fresh resource/face-only/collision-retention checks and normalization exit 0 with
no ERROR/SCRIPT ERROR. Both scene/material pairs retain bytes through two roundtrips.
**gdstyle 0.3.0** format check and 100-column/zero-warning lint pass. The only new GDScript
is compiled/executed by the headless check, not production gameplay.

[manifest.json](d09_freight_graphics_03-evidence/manifest.json) hashes every produced payload
except itself and uncommitted Python cache, plus unchanged carrier/glyph/export dependencies.
[final.log](d09_freight_graphics_03-evidence/final.log) is the concise final receipt; raw logs
and fresh exports remain in `C:/tmp/ft/assets/d09_freight_graphics_03/`, not Git.

## Exact reproduction

Run in Git Bash from the worktree root. All engine processes are bounded/headless; never
use live editor sessions. First-time authoring normalizes without `--verify-stable`; the
committed delivery supports the strict fresh-process command below. `record.py` defaults
to read-only verification; `--write` explicitly rebuilds final receipts/manifest.

```sh
NID=d09_freight_graphics_03
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="$(mise which gdstyle)"
OUT="C:/tmp/ft/assets/$NID"
mkdir -p "$OUT"
export PYTHONIOENCODING=utf-8
python tools/asset_production/$NID/author.py
python -m unittest discover -s tools/asset_production/$NID -p 'test_*.py' -v > "$OUT/tests.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/validate.py > "$OUT/source.log" 2>&1
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/preview.py > "$OUT/render.log" 2>&1
python tools/asset_production/$NID/record.py --compress-renders
timeout 300 "$G" --headless --path . --import > "$OUT/import-initial.log" 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/$NID/check_prefab.gd -- --normalize --verify-stable > "$OUT/normalize.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$OUT/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/$NID/check_prefab.gd > "$OUT/prefab.log" 2>&1
"$S" fmt --check tools/asset_production/$NID/check_prefab.gd > "$OUT/format.log" 2>&1
"$S" --max-line-length 100 --max-warnings 0 tools/asset_production/$NID/check_prefab.gd > "$OUT/style.log" 2>&1
python tools/asset_production/$NID/record.py --write
python tools/asset_production/$NID/record.py
```

## Diagnostics and remaining acceptance

Initial tests exposed Pillow's deprecated `getdata` API; it was replaced with
`get_flattened_data`, and final tests emit no deprecation warning. A receipt writer's
initial newline escaping syntax error was corrected before generating evidence. Blender
preview retains forward-looking `use_nodes` deprecation notices. Import retains the
installed MCP toolkit warning about Godot 4.8 versus tested 4.7; no asset import errors.
Final fresh prefab/normalization checks have no warning/error diagnostics. No vendor tools
were changed and no errors suppressed.

Pending: independent art/technical review of the exact candidate and final fictional copy
selection; sparse district loading-edge placement, facade attachment, vehicle turn clearance,
actor/target occlusion; actual renderer filtering/mips/LOD, gameplay-camera and district-light
review; packaged device, Deck and sustained repetition performance. Existing support
movement/network gates remain their owners' responsibility. No new gameplay authority,
collision, road-tool, navigation, world identity or multiplayer behavior was introduced.
No new movement/network acceptance is claimed. No `tools/production_checks.py` run, under
owner decision 52. No TODO closure or world placement is authorized by this asset alone.

## Saved identity normalization

Identity normalized; imported-child override ids migrated by Godot 4.8 editor save; override target verified.
