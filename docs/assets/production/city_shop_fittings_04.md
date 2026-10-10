# city_shop_fittings.04 — Closed shutter

10 October 2026. **Source/export and bounded headless prefab candidate delivered;
independent review and world/gameplay/device acceptance pending.** Production follows
[commission](commission.md) and the explicit per-record production task, superseding
the historical concept-only status in [city_shop_fittings](../city_shop_fittings.md).
Produced by the commissioned implementation specialist on `lane/a-fittings`.

## Design and dimensions

An original static shopfront closure: fourteen broad folded curtain courses, quiet
slate/petrol guide casings, a chamfered roll-cover headbox, weighted satin bottom rail,
two small grip recesses and a ground seal. Rounded edges and broad highlights match
accepted `.03` surround and `.05` display-bay hardware. The shop-family brief, Signal
Row v03 breakdown/image, district identities, street hierarchy, existing fittings and
accepted light/prefab evidence were inspected before authoring. No external geometry,
textures, real brands, image-to-mesh, generated runtime render meshes or artwork.

This is a **closed frontage component**, not a larger workshop/depot roller door,
service door, replacement entrance surround or working shutter mechanism. There is
one size and one static state. No interiors, opening animation, interaction, loot,
destruction, replication code or moving collision is introduced.

The following are **provisional authored dimensions**, not measured concept-image
values, approved shell interfaces or building-code certification. They follow the
standing production permission for compatible reversible dimensions.

| Measurement | Metres / contract |
| --- | --- |
| Width × height × depth | 3.200 × 2.480 × 0.270 |
| Godot AABB minimum | (-1.600, 0.000, -0.280) |
| Godot AABB maximum | (1.600, 2.480, -0.010) |
| Blender AABB minimum / maximum | (-1.600, 0.010, 0.000) / (1.600, 0.280, 2.480) |
| Pivot | Finished-floor centre on facade plane, (0,0,0) |
| Front/up | Blender +Y/+Z → Godot -Z/+Y, exactly one glTF conversion |
| Guide casings | 0.120 wide × 0.190 deep; outer X ±1.600 |
| Curtain | 2.980 wide; height 0.100–2.200; 0.150 course pitch |
| Curtain depth | Blender Y 0.045–0.125 (Godot Z -0.125–-0.045) |
| Headbox | Height 2.210–2.480; maximum forward projection 0.280 |
| Bottom rail | Height 0.024–0.120; seal contacts finished floor at zero |
| Bounds/ground tolerance | ±0.001 m |
| Proposed placement tolerance | ±0.002 m; axes aligned, unit scale |

The datum deliberately stays on the wall plane rather than the centre of the
asymmetric depth. Root and mesh are identity transforms with metre units. An excluded
`authoring_1m_reference` cube in the source verifies scale; it is not exported.

**Mounting contract:** reserve a flat 3.400 m frontage width, finished floor at the
pivot and no unrelated trim inside the visual envelope. All visible geometry is
street-side of the wall, leaving a 10 mm back stand-off. This may dress a blank closed
bay, or close a shell-owned aperture no larger than 2.900 m wide × 2.180 m high from
floor level; the guide/head coverage must be checked against the selected shell.
The shell owns all structural wall/trim. There is no rear insertion sleeve.
Do not stack this onto the `.05` display bay or an existing door/frame: their
forward projections would intersect the curtain. It is not a drop-in replacement
for those different rough openings. Do not stretch it or claim existing-shell fit.

Width matches the 3.200 m display-bay rhythm; the 2.480 m top aligns with that bay at
its proposed 0.480 m mounting height and the entrance surround. The existing canopy
at its proposed 3.000 m pivot has a 2.580 m low edge, providing 0.100 m nominal space
above this shutter. These are interface arithmetic only, not an assembled placement
acceptance. Tenant fascia/artwork remains a separate fitting; the headbox is not a
new sign carrier.

## Source, exports and materials

- Source: `art/source/models/environment/city_shop_fittings_04/city_shop_fittings_04.blend`.
- Named export collection: `export_city_shop_fittings_04`.
- Root / mesh: `CityShopFittings04` / `CityShopFittings04_Mesh`.
- Linked export: `art/models/environment/city_shop_fittings_04/city_shop_fittings_04.glb`.
- Import settings/identity: adjacent `.glb.import`, UID `uid://b8o7bop7am8ns`.
- Prefab: `scenes/prefabs/environment/city_shop_fittings_04.tscn`, UID `uid://mytrg07lj5ic`.
- Parametric author, export, topology/raw-GLB validator, isolated render, engine check,
  collision fixture and manifest tools: `tools/asset_production/city_shop_fittings_04/`.

All visible geometry is constructed in Blender. Closed subparts are joined into one
mesh; select linked topology to edit individual solids, or change the author recipe.
Applied bevels and weighted normals remain in saved editable geometry. Intentional
manufactured overlaps do not imply one boolean-unioned volume.

Four opaque, back-culled Principled surfaces, actual exported slot order:

| Slot | Material | sRGB swatch | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `shutter_satin_curtain` | `#70888D` | .40 / .48 |
| 1 | `shutter_dark_rebate` | `#23333B` | .05 / .70 |
| 2 | `shutter_slate_petrol` | `#405B68` | .25 / .46 |
| 3 | `shutter_satin_hardware` | `#929D9F` | .65 / .38 |

Swatches are converted to linear shader values. No transparency, emission, textures,
embedded images, material overrides, UV-dependent artwork, lights, rigs, clips or
sockets are needed. No speculative LOD variant is authored; default Godot automatic
LOD/shadow-mesh import remains enabled and has not been performance-certified.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; exporter **5.2.40**. Export uses the shared
`tools/assets/blender/export_settings.json`, with only collection and static
animation/skin exclusions plus output path supplied locally. Cameras, studio ground,
lights and the metre fixture never enter the export. No `prototypes/` dependencies.

## Validation and prefab collision

[validation.json](city_shop_fittings_04-evidence/validation.json) records measured
source and actual binary GLB values: **2,952 triangles, 1,502 source vertices,
1,674 exported vertices, one mesh, four surfaces; 75,436-byte GLB**. Zero degenerate
source faces/export triangles, zero non-manifold source edges; consistently wound
closed solids, positive signed source volume, finite unit normals, identity transforms
and source/export/Godot bounds all pass. A fresh process opened the committed source
and produced a **byte-identical GLB** (SHA-256
`8d32d92c187385d612f4c36bde740437826d7f7416e0ef05d5f9e3ceac450648`).

The prefab retains the actual imported model at identity under `Visuals/Model`, not
copied mesh data. Its separate `Collision/Body` is one static-world layer-1/mask-0
body, with a **3.200 × 2.480 × 0.190 m BoxShape3D**, centre `(0,1.240,-0.105)`.
This deliberately smooth barrier covers the closed frontage/guide envelope; slat
grooves and grip details cannot snag actors. The overhead headbox's last 80 mm forward
projection is visual-only. Collision spans Godot Z [-0.200,-0.010]. No opening or
runtime collision transition is provided.

Pinned Godot headless import and dependency/UID traversal pass. Both owned scenes
were loaded, packed/resaved, reloaded and saved again with byte-stable second saves;
normalized scene UIDs and node identities are retained. No inherited variant exists.
The direct-file scene fallback is mandated by the unavailable/crashing windowed
editor and the isolated-CLI commission; this does not claim live-editor synchronization.
No owner live Blender/Godot session was used.

The saved owned collision fixture exercises real `ActorMotion.step` / `FootCommand`
with the production capsule (radius 0.350 m, height 1.800 m) for 60 physics ticks per
case in both AUTHORITY and REPLAY modes. Independent expected contacts pass:

- Front stop Z **-0.550781 m**; side stop X **1.950522 m**; rear stop Z **0.340494 m**.
- Clear bypass at X=2.050 reaches Z **3.000000 m**.
- Front ray hits the intended static body at Z=-0.200; a ray at height 2.600 stays clear.
- All four mode-paired positions agree within **1 mm**, not bitwise equality. The
  first authority contact retains a 0.878 mm vertical floor recovery offset; replay
  starts with cached floor contact after fixture teleports. All eight raw positions
  are recorded. Initial exact-equality assertion failed; it was corrected to the
  declared millimetre tolerance without changing any production simulation or
  contact/bypass expectations.

`production_checks.py` **passes all layers**: 152 owned scripts compile, formatting/
lint pass, 14 Python tests pass, 119 GUT tests / 6,362 assertions pass, and the intentional
negative test correctly exits 1. No known-failure exclusions were used. Owned `check.gd`
also passes the pinned gdstyle 0.3.0 formatter check and zero-warning lint directly.

## Evidence and reproduction

[Hero](city_shop_fittings_04-evidence/hero.png),
[side](city_shop_fittings_04-evidence/side.png),
[headbox/fold detail](city_shop_fittings_04-evidence/detail.png),
[47 m / 42° overhead](city_shop_fittings_04-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU / AgX renders, 1280×720, 32 samples and
PNG compression 95 followed by RGB seven-bit channel compaction / PNG level 9.
The overhead camera is at Blender `(0,11,47)`, rotation `(0,0,0)`, vertical FOV 42°:
off-centre frontage with true vertical-down fixed-yaw perspective, not a tilted closeup.

Self-inspected all four views. The close hero reads as a closed shutter with quiet
broad courses and smooth manufactured edges. The first side framing clipped the
headbox; final side framing includes the entire asset. At gameplay height it reduces
to a small subdued header/frontage strip, like the existing fittings; grips/courses
are not essential gameplay signals. No bright noise or added roof-scale icon attempts
to force readability. Actual blue-hour shell/roof occlusion and gameplay camera
readability remain unproved.

Exact reproduction from the worktree root (fresh scratch/output directory required
for production checks; all Blender/Godot invocations bounded):

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T='tools/asset_production/city_shop_fittings_04'
S='art/source/models/environment/city_shop_fittings_04/city_shop_fittings_04.blend'
TMP='C:/tmp/ft/assets/city_shop_fittings_04'
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
mkdir -p "$TMP"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 "$S" --python-exit-code 1 --python "$T/export.py" -- "$TMP/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$TMP/reexport/city_shop_fittings_04.glb"
timeout 600 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
timeout 300 "$G" --headless --editor --path . --import --quit
timeout 180 "$G" --headless --editor --path . --script "res://$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "res://$T/check.gd"
"$(mise which gdstyle)" fmt --check "$T/check.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$TMP/checks"
python "$T/manifest.py" "$TMP/checks"
python "$T/manifest.py" --verify
```

The compact [final log](city_shop_fittings_04-evidence/final.log) records final
outcomes and diagnostic classification. Raw retries/import/test logs and scratch
reexports are outside Git at `C:/tmp/ft/assets/city_shop_fittings_04/`.
[manifest.json](city_shop_fittings_04-evidence/manifest.json) hashes every produced
source/export/import/prefab/tool/doc/evidence payload, excluding only itself. It is a
producer inventory, not independent acceptance. No byte-identical `.blend` rebuild is
claimed; the saved-source GLB reexport is strict.

Diagnostics retained rather than suppressed: Blender `use_nodes` deprecation warnings
and version-probe one-block 23-byte shutdown warning; import's existing MCP plugin
4.8-versus-4.7 warning; editor-normalization shutdown renderer/text/Canvas/ObjectDB
leak diagnostics after successful checks. Runtime checks have no ERROR/WARNING/SCRIPT
ERROR diagnostics. The project's existing MCP autoload/plugins briefly initialize in
the owned CLI processes; no endpoint was called and no live session/configuration was
modified. Production checks use their shared isolated compile mirror and pass cleanly.

## Remaining acceptance

Independent source/art/prefab review is pending. Actual shell placement, wall opening
coverage, canopy/fascia spacing, populated-city/blue-hour camera views, actor corner
handling on the selected world floor, car impacts/turning, real multiplayer transport/
admission/prediction, export packaging, repeated-placement cost and Steam Deck sustained
performance remain downstream. The bounded AUTHORITY/REPLAY fixture is not network
proof. No register, shared progress, TODO, world scene or sibling asset was changed,
and no world placement or blanket production-ready verdict is claimed.
