# city_roof_details.05 — Simplified dormer window and roof housing

10 October 2026. **Original source, explicit export, linked prefab and bounded checks delivered;
independent review, building attachment and gameplay/device acceptance pending.** Produced by the
assigned implementation specialist on `lane/a-roof`. The direct assignment and
[commission](commission.md) supersede the historical concept-only status of the
[roof family brief](../city_roof_details.md). No register, progress record, shared brief,
sibling asset or world placement was changed.

## Design and provisional dimensions

A broad two-light dormer: sealed gabled housing, two folded cap leaves, inclined contained
flashing and raised boot, one recessed window face, continuous frame/bead, a single meeting
stile and shallow drip sill. Original Blender construction; no downloads, purchased assets,
external model libraries, textures, generated runtime meshes, brands or image-to-mesh process.
No interior, opening window, roof-access behaviour, traversal, smoke, animation or destruction.

Read the accepted art direction, district identities, Stage 4 streets and Old Quay breakdown;
inspected Old Quay v03 and the completed `.03`/`.04` lane outputs. The main surfaces match their
quiet petrol/folded-metal/shadow palette. The opaque teal pane and narrow warm bead use the exact
swatches of the shared upper-facade window `.07`, with two large lights rather than a miniature
window grid. This is an integral small dormer face, not a rescaled copy of the 4.8 m facade
window carrier. No sibling geometry is copied or changed. Intended reuse is The Crescents and
Old Quay; Terrace Ward remains a candidate. Do not place one on every roof.

These are **reversible provisional production dimensions**, not inferred concept-image
measurements or an approved building interface. One fixed 30° attachment is delivered.

| Interface | Metres / contract |
| --- | --- |
| Plan footprint X × Z | 2.80 × 3.00 |
| Nominal height above centre roof datum | 1.925 |
| Nominal complete vertical extent | 2.791025; includes downslope flashing below the root |
| Measured Godot AABB | (-1.400000, -0.865684, -1.500000) → (1.400000, 1.924655, 1.500000) |
| Measured Godot dimensions X / Y / Z | 2.800000 / 2.790339 / 3.000000 |
| Numeric bounds and overall-size tolerance | ±0.001 |
| Apron plan / vertical thickness | 2.80 × 3.00 / .035 |
| Raised boot plan / top above roof plane | 2.40 × 2.60 / .16 |
| Housing plan / eave / ridge | 2.20 × 2.24 / 1.18 / 1.84 |
| Cap plan / nominal eave top / ridge top | 2.50 × 2.56 / 1.175 / 1.925 |
| Window outer frame width / height | 2.00 / 1.44; vertical centre .30 |
| Two opaque panes, each width / height / depth | .88 / 1.22 / .045 |
| Meeting stile width / pane recess behind stile | .07 / .0435 |
| Drip sill width / projection depth | 2.10 / .20; entirely inside flashing footprint |
| Proposed support patch, horizontal plan | 3.00 × 3.20, wholly within one matching roof face |

Root and mesh origin are at **the centre of the 30° roof-contact plane**, not the lowest
flashing point. Metre units, applied transforms and identity root/mesh. Blender +Y is the
**window front and downhill**, mapped once to Godot -Z; Blender +Z maps to Godot +Y. The plane
at identity yaw is `Godot Y = Z * tan(30°)`. Mount upright at unit scale and align with yaw
only; do not tilt the gable to fit another pitch.

Sibling `.04` uses its -Z axis **uphill**. On the same roof face, its yaw is therefore **180°
relative to this dormer**, with each root translated onto its own centre roof datum. They use
the same pitch magnitude, not the same forward direction. The level-roof `.03` interface is
unchanged. Other pitches, ridge-straddling, hipped corners and roof cuts are not supplied.

The 1 mm prism bevels reduce both vertical extremes slightly; the broad underside remains on
the intended roof plane. Independent source rays at Blender X=1.33, Y=±1.40 hit apron tops at
-.773290 / +.843290 m respectively. Front rays through both pane centres hit Y=1.210500;
the meeting stile hits Y=1.254000. Two cap rays hit height 1.325 m. The sealed cheek extends
inside the cap, avoiding daylight gaps. Manufactured solids overlap intentionally; this is
not a boolean-unified engineering or weatherproofing model.

No supporting roof opening is required: this is a sealed exterior fitting, and its window
is opaque. Initial edge/ridge-clearance proposal is .50 m outside the flashing envelope,
consistent with the family's sparse placement intent; final fit belongs to the building owner.

## Source, export and materials

- Source: `art/source/models/environment/city_roof_details_05/city_roof_details_05.blend`.
- Collection: `export_city_roof_details_05`; root `CityRoofDetails05`, mesh
  `CityRoofDetails05_Mesh`. No studio objects, camera or lights in the saved export collection.
- Export: `art/models/environment/city_roof_details_05/city_roof_details_05.glb`, with pinned
  Godot-generated `.import` sidecar.
- Prefab: `scenes/prefabs/environment/city_roof_details_05.tscn`.
- Authoring, export, validation, rendering and receipt tools:
  `tools/asset_production/city_roof_details_05/`.

**1,368 source vertices, 2,696 triangles, one mesh, five surfaces**; actual GLB vertices after
material/normal splits: **1,467**. Twelve closed manufactured solids are joined into one
editable mesh. **Zero degenerate faces/triangles and zero non-manifold edges**; consistently
wound edges, positive total volume and unit-length source/export normals. Binary GLB positions,
indices and normals are decoded and checked, rather than trusting accessor bounds alone.
No live modifiers, rigs, clips, sockets, embedded images or texture dependency.

| GLB surface / Principled material | sRGB swatch | Metallic / roughness |
| --- | --- | --- |
| 0 — `dormer_folded_metal` | `#314D50` | .30 / .55 |
| 1 — `dormer_shadow` | `#172B30` | .05 / .78 |
| 2 — `dormer_dark_petrol` | `#273F43` | .28 / .52 |
| 3 — `dormer_warm_bead` | `#C8C2AD` | .22 / .48 |
| 4 — `dormer_opaque_tint` | `#345D64` | .18 / .28 |

Opaque back-culled PBR, sRGB converted to linear, no emission/transmission/alpha. No external
material remapping or speculative texture maps. Default Godot automatic LOD generation stays
enabled; there is no hand-authored LOD or measured performance budget.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. `export.py` reads the
shared `tools/assets/blender/export_settings.json`, filters the named collection, disables
skins/animations and performs the single Y-up conversion. Existing accepted author/export/
validation conventions were followed; no shared geometry-helper module exists in
`tools/assets/blender/`, so the small asset-specific constructors remain local.

Fresh-process export of the saved source is byte-identical to the **68,200-byte GLB**, SHA-256:
`a0082ec1a278e78612e996dcb1d63fe568a83488f60dbf4f3fa95ee4bdfda12f`.
The [producer manifest](city_roof_details_05-evidence/manifest.json) hashes every delivered
payload except itself, including scripts, source, export, normalized import metadata, prefab,
this record and lean evidence. Byte-identical regeneration of the `.blend` container is not
claimed; the saved-source reexport is the reproducibility gate.

## Prefab, collision and bounded engine checks

`Visuals/Model` is an identity-transform linked GLB instance, not copied mesh data. No editable
imported children, material overrides, runtime hierarchy builder or gameplay script. The wrapper
has its engine-generated scene UID and node identities. Pinned Godot
**4.8.dev7.official.c971f93e7** imports the model, resolves recursive dependencies and retained
UIDs, verifies one mesh/five opaque back-culled surfaces and independent bounds, and checks
model linkage/identity. Two headless pack/save/load rounds are byte-stable. A fresh standalone
engine process loads and checks the final resources without error/warning diagnostics.

**Visual-only, above-head roof decoration.** No collision body/shape: the brief excludes
rooftop traversal and the standing production rule permits purely overhead fittings. Every
point must remain **above 2.5 m world height**: at unit scale and yaw-only placement, use a
root height of at least **3.367 m** (the evidence uses 8 m). The enclosing building owns roof
and route collision. Do not place this prefab freestanding on a street or accessible roof;
that use would require newly reviewed collision and movement/network checks. The asset test
asserts no collision objects; it does not certify a saved world placement meets the restriction.
No movement, car-contact or multiplayer transport checks are claimed for this noncolliding
fitting, and no physics/replication code changed.

## Evidence and visual review

[Hero](city_roof_details_05-evidence/hero.png),
[side/profile](city_roof_details_05-evidence/side.png),
[window detail](city_roof_details_05-evidence/detail.png),
[47 m / 42° overhead](city_roof_details_05-evidence/overhead_47m_42deg.png).
Four isolated Blender Cycles CPU renders, 32 samples/denoise, AgX, **1280×720**, PNG compression
95 then evidence-only RGB six-significant-bit encoding / PNG level 9. Final files are
203–275 KiB each. Quantization can band studio gradients; runtime geometry/materials are
unaffected. No engine capture or image-generated geometry is represented by these views.

Visually inspected all four final compressed views. The gabled outline, sealed cheeks, sparse
two-pane window and inclined apron read in the close views. The side view deliberately exposes
the inclined underside above a horizontal studio floor; it is not a flat-footed prop.
The glazing remains opaque, without implied interior detail or roof-access behaviour.

The overhead is **vertical-down, north-up, 47 m world height / 42° vertical FOV**, with the
root translated to 8 m on a temporary matching 30° studio slope. Its footprint occupies about
65×73 pixels. The cap's two broad planes and contained apron remain the read; the window face
and fine bead appropriately disappear directly overhead. It is intentionally not a bright
roof marker. This isolated slope is neither exported nor saved as a building or world asset.
Actual building-silhouette dominance, production-roof contrast, repetition, off-centre
perspective and district mounting still need placement review.

## Exact reproduction

Run Git Bash from the worktree with the pinned tools and Pillow available. All asset Blender
jobs are isolated, factory-started, audio-disabled and bounded; every direct engine invocation
is bounded/headless. Live/windowed editor use is prohibited by the brief, so the prefab was
authored as text then packed/resaved privately. No owner live session was touched, and these
checks do not synchronize a separate open editor.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_roof_details_05
S=art/source/models/environment/city_roof_details_05/city_roof_details_05.blend
X=C:/tmp/ft/assets/city_roof_details_05
mkdir -p "$X" docs/assets/production/city_roof_details_05-evidence
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy

timeout 300 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 300 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 "$S" --python "$T/export.py" -- "$X/reexport"
timeout 300 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$X/reexport/city_roof_details_05.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --editor --path . --script "res://$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" > "$X/check.log" 2>&1
timeout 30 "$(mise which gdstyle)" check "$T/check.gd"
# Use a fresh output directory for each canonical run.
PYTHONUTF8=1 timeout 1800 python tools/production_checks.py --godot "$G" --gdstyle "$(mise which gdstyle)" --output "$X/checks-final"
python "$T/manifest.py" "$X/checks-final"
# Import final compact PNG bytes and refresh hashes after any owned metadata normalization.
timeout 300 "$G" --headless --path . --import
python "$T/manifest.py" "$X/checks-final"
```

[validation.json](city_roof_details_05-evidence/validation.json) records source/export numbers,
attachment/window rays, camera, engine, render sizes and canonical checks.
[final.log](city_roof_details_05-evidence/final.log) is the concise final command/diagnostic
receipt. Scratch outputs, earlier images and full logs stay outside Git under
`C:/tmp/ft/assets/city_roof_details_05/`.

## Diagnostics and remaining acceptance

- Owned GDScript format/lint/compilation and canonical checks pass: **17 Python tests,
  149 GUT tests / 6,768 assertions**, plus correct detection of the intentional failing test.
  No known-failure exemption was needed.
- First engine bound-size check failed: two 2 mm edge bevels cumulatively shortened the
  complete height by 1.37 mm. Reduced prism bevels to 1 mm, regenerated source/export/renders
  and revalidated; no dimensional tolerance was widened. Final size error is .687 mm.
- Before first rendering, raised the sealed gable slightly into the cap to prevent an eave
  gap. Final source/export/window-ray and visual checks pass.
- Blender emits `Material/World.use_nodes` deprecation notices. The version-only probe emits
  one 0.000023 MB unfreed allocation; all final asset jobs exit 0.
- Headless import has the existing MCP plugin Godot 4.8 compatibility warning. Editor
  normalization passes assertions but emits renderer/text RID and ObjectDB shutdown leaks.
  These diagnostics are retained, not suppressed or represented as clean. Standalone asset
  loading has no error/warning diagnostics.

**Pending:** independent technical/art review at the exact commit; final roof pitch, mounting,
edge/ridge clearances and district selection; actual engine gameplay-camera/building silhouette,
roof contrast and repeated placement; packaged build, sustained GPU/frame pacing and Deck checks.
Accessible placement must reopen collision and relevant movement/network validation. No city
placement, performance approval, completed shared TODO or blanket READY status is claimed.
