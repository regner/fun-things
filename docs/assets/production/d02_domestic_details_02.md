# d02_domestic_details.02 — Wall return

**Source/export, linked prefab and bounded headless checks delivered; independent
review and placement acceptance pending.** Production commissioned by Regner under
[the commission](commission.md) and the current per-asset production brief. Original
Blender construction by the commissioned worker on `lane/a-d02`; supervisor/reviewer
owns acceptance and world integration. No live Blender/Godot session was touched.

Family: [Domestic boundary and porch details](../d02_domestic_details.md).
Direction: [The Crescents](../../concepts/world-v1/stage-03-district-identities/README.md),
[selected revision 02](../../concepts/districts-v1/02-the-crescents-v02.png), and
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md).
The production commission supersedes historical concept-only restrictions.

## Design and dimensions

A low L-shaped garden-wall return with warm rendered faces, a quiet slate plinth,
a chunky ivory corner coping and two straight end stones. The continuous mitred
elbow avoids overlapping straight-wall caps. Broad highlights and sparse coping
joints retain domestic scale without brick noise. Palette and section match the
[delivered straight run](d02_domestic_details_01.md), which follows the Crescents
house palette: render `#ACA69E`, ivory `#D4CEBB`, slate `#58636B`.
No gate, interior, working hardware, interaction, animation or destruction state.
No downloaded/purchased mesh, external artwork, texture or image-to-mesh source.

Dimensions are **provisional authoring proposals**, consistent with the standing
rule and sibling section; they are not inferred from concept imagery or approved
home/plot clearances. Tolerance is 0.001 m, unit-normal tolerance 0.0001.

| Contract | Metres, Godot local axes |
| --- | --- |
| Whole visual X / Y / Z | 1.600 / 0.940 / 1.600 |
| Whole AABB | (-0.800, 0, -0.800) to (0.800, 0.940, 0.800) |
| Origin | Ground-centred **AABB**, not solid-area centroid; (0,0,0) is in the open quadrant |
| South arm centreline | Z=0.620, from X=-0.620 to X=0.800 |
| West arm centreline | X=-0.620, from Z=0.620 to Z=-0.800 |
| Core | 0.260 thick; Y=0.140 to 0.800 |
| Plinth | 0.300 thick; Y=0 to 0.140 |
| Coping | 0.360 thick; Y=0.800 base, 0.910 shoulder, 0.940 crest |
| Coping joints | 0.006 gaps at X=0.090 on south arm and Z=-0.090 on west arm |
| East end interface | (0.800, 0, 0.620), outward +X |
| North end interface | (-0.620, 0, -0.800), outward -Z |

The corner and both arms are one continuous rendered core, one continuous plinth,
and three closed coping pieces joined into a single editable mesh. Soft bevels
are 0.012 m on render and 0.008 m on plinth/coping, matching the sibling.
Blender +Z maps to Godot +Y and Blender +Y to Godot -Z; all export members retain
identity transforms and metre units. A non-export hidden-render 1 m cube remains
in the source. No sockets or runtime procedural geometry are needed.

### Straight-run interface

With this return at identity, put the straight sibling root at **(2.400,0,0.620)**
with zero yaw to continue east. Put another at **(-0.620,0,-2.400)** with +90-degree
Y yaw to continue north. Both roots remain unit scale. This is a tested connector
example, not saved world placement. Rotate the entire return to other plot corners;
do not mirror with negative scale or stretch it to fit curved streets.

Both actual exported end-plane profiles match the sibling's 14 distinct profile
points after translation/axis mapping, to five decimal places; full exported
material definitions and slot order also match. Six engine seam rays check either
side and the exact plane of both joins at the shared 0.940 m crest. Small bevel
reveals remain visual seams; the continuous colliders have no join gap.

## Source, export and materials

- Source: `art/source/models/environment/d02_domestic_details_02/d02_domestic_details_02.blend`.
- Collection: `export_d02_domestic_details_02`.
- Root / mesh: `D02DomesticDetails02` / `D02DomesticDetails02_Mesh`.
- GLB: `art/models/environment/d02_domestic_details_02/d02_domestic_details_02.glb`
  with its engine-normalized `.import`.
- Prefab: `scenes/prefabs/environment/d02_domestic_details_02.tscn`.
- Author/export/validator/render/receipt tools and engine check:
  `tools/asset_production/d02_domestic_details_02/`.

One mesh, three opaque Principled surfaces in actual exported order:

| Slot | Material | Roughness | Metallic |
| --- | --- | --- | --- |
| 0 | `crescents_warm_render` | 0.65 | 0 |
| 1 | `crescents_slate_plinth` | 0.75 | 0 |
| 2 | `crescents_ivory_trim` | 0.55 | 0 |

Original flat colors converted from sRGB to linear in the author script; backface
culling enabled. No textures, embedded images, external material remaps, custom
shaders, rigs, clips, skins, morphs or LOD variants. Applied bevel and weighted-normal
modifiers keep the saved geometry editable; glTF triangulates at export.
Blender **5.2.2 LTS**, build `d13f752e3b9c`, exporter **5.2.40**; export uses the
shared `tools/assets/blender/export_settings.json` with explicit collection and
animation/skins disabled. Studio content is never saved/exported. Godot
**4.8.dev7.official.c971f93e7** imports scale 1, automatic LODs and shadow meshes.
No repeated-placement or device budget is claimed.

## Prefab and collision

`Visuals/Model` is an identity-transform linked imported instance. Separate
`Collision/Body` is one static body, layer 1 / mask 0, with two simple boxes:

| Shape | Size X / Y / Z | Centre |
| --- | --- | --- |
| SouthArm | 1.600 / 0.940 / 0.360 | (0, 0.470, 0.620) |
| WestArm | 0.360 / 0.940 / 1.240 | (-0.620, 0.470, -0.180) |

These partition the L-shaped coping footprint, meeting at Z=0.440 without overlap
or a corner gap. The empty inner quadrant X>-0.440 / Z<0.440 is **not** filled by
an invisible bounding box. The six-sided outer footprint in X/Z is
(-0.8,-0.8), (-0.44,-0.8), (-0.44,0.44), (0.8,0.44), (0.8,0.8), (-0.8,0.8).
The boxes span coping joints/bevels and expand at most 0.050 m per side over the
unbevelled core, matching the straight sibling's anti-snag envelope. This is a low
blocking boundary, not a walkable deck or a climb/vault mechanic. No nav, world IDs,
destructibility, whole-plot collider or gameplay code changes.

Editor tools were prohibited and the windowed editor is unavailable. The commissioned
text fallback was loaded/packed/resaved by pinned headless Godot; the second save was
byte-stable. Prefab UID `uid://j0iw30gj13yw`, model UID `uid://dx5bvm1yw4yp1`, linked
ancestry and saved node identities resolve. No separate open editor synchronization
is claimed. Place short returns beside plots, never across shortcut mouths.

## Evidence and reproduction

[Hero](d02_domestic_details_02-evidence/hero.png),
[side](d02_domestic_details_02-evidence/side.png),
[corner detail](d02_domestic_details_02-evidence/detail.png),
[gameplay overhead](d02_domestic_details_02-evidence/overhead_47m_42deg.png).
All four were inspected after compression: clean elbow, matching quiet bands,
readable L-shaped pale coping and open inner quadrant. At the reference camera the
return spans approximately 34 pixels; joints are close-view detail, not route cues.
These are isolated Blender Cycles CPU renders, 32 samples, AgX, 1280×720, PNG
compression 95 plus six-bit RGB compression, each below 400 KB. Overhead is
vertical-down perspective at 47 m / 42-degree vertical FOV, north at image top.
The standing 1280×720 evidence-size rule supersedes the older 1280×800 reference.
No image is an engine capture or proof of populated-city shortcut visibility.

Run from repository root in Bash; scratch remains outside Git:

```sh
N=d02_domestic_details_02
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="C:/tmp/ft/assets/$N"
mkdir -p "$S" "docs/assets/production/$N-evidence"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy PYTHONIOENCODING=utf-8

timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/author.py"
timeout 600 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/render.py"
python "tools/asset_production/$N/record.py" --compress-renders
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  "art/source/models/environment/$N/$N.blend" \
  --python "tools/asset_production/$N/export.py" -- "$S/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$N/validate.py" -- "$S/reexport/$N.glb"

timeout 300 "$G" --headless --path . --import > "$S/import-initial.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "tools/asset_production/$N/check_prefab.gd" -- --normalize \
  > "$S/normalize-editor.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script "tools/asset_production/$N/check_prefab.gd" \
  > "$S/prefab-final.log" 2>&1
"$(mise which gdstyle)" fmt --check "tools/asset_production/$N/check_prefab.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$N/check_prefab.gd"
python "tools/asset_production/$N/record.py"
python "tools/asset_production/$N/record.py" --verify
```

Tools follow the accepted sibling patterns and shared export contract. The validator
reads the sibling GLB, and connector checks load its prefab without modifying either.
`production_checks.py` was not run, per owner decision 52.

## Validation results

[Final receipt](d02_domestic_details_02-evidence/validation.json),
[concise diagnostic log](d02_domestic_details_02-evidence/final.log),
[producer manifest](d02_domestic_details_02-evidence/manifest.json).

- **1,328 triangles, 674 Blender vertices, 674 GLB vertices; one mesh, three surfaces.**
- **Zero degenerate faces/triangles and zero non-manifold edges**; contiguous winding,
  positive signed source volume, outward binary triangle winding and unit normals.
- Source, actual binary GLB and imported Godot bounds match the table within 0.001 m;
  ground is zero and transforms are identity. Both end profiles and materials match
  the straight sibling, independently of the return authoring recipe.
- Separate-process fresh reexport is byte-identical: **24,992 bytes**, SHA-256
  `a8a16137ccdc1ecfbaed43dacbb5dfd0f4725e3ddb38d8e6541992d2673c05df`.
- Final pinned import exits 0 without ERROR/SCRIPT ERROR lines. Fresh runtime load
  resolves all dependencies, opaque/back-culling surfaces, mesh ancestry and UIDs.
- Nine capsule cases, 56 footprint rays and six sibling-join seam rays pass. The
  inner arm ray hits Z=0.440000057 m. Inner corner and both end bypasses stay clear.
- Production `ActorMotion.step`, r=0.35 m / h=1.8 m capsule: five cases over 60 fixed
  ticks each pass in AUTHORITY and REPLAY with identical endpoints. Inner contacts
  are Z=0.083334 / X=-0.083334; outer contacts Z=1.166666 / X=-1.166666; east bypass
  reaches Z=3.000000. Literal expected contacts allow 0.025 m solver separation.
- A 1.9×1.5×4.3 m car-sized test box is blocked frontally and clear at X=3 m. This
  is an envelope sweep, **not** production car handling or turning evidence.
- Pinned format check and strict lint pass. Initial lint flagged a 52-line motion
  function; extracting the independent cases into a named helper resolved it.
  Function-purpose comments and spacing were manually checked.

Blender authoring reports known future-6.0 `use_nodes` deprecations. Headless import
reports the existing MCP 4.8 compatibility warning. Editor normalization proves
byte stability and exits 0 but emits scan-aborted/RID/ObjectDB shutdown diagnostics;
exact diagnostic lines are retained in `final.log`. Fresh runtime has no ERROR or
WARNING lines. No diagnostics are suppressed, no live owner processes accessed.

## Remaining acceptance

- Independent source/technical and art review at the committed candidate.
- World integrator: chosen home setbacks, actual placed joins/gaps, curved-street
  fit, short domestic plots and visible pedestrian shortcuts; do not scale modules.
- Gameplay/camera owner: native 47 m/42-degree actor/combat visibility, real car
  movement around placed returns and walking alternatives.
- Network owner: actual separate-process transport/admission/prediction/lifecycle
  evidence if used in a replicated world; local authority/replay is not acceptance.
- Device/performance owner: native material/LOD appearance, repeat-placement profile,
  packaged dependencies and sustained Deck LCD/OLED evidence.

Only the earlier straight-run handoff's return-junction status is clarified with a
link to this delivery, and its current manifest doc hash refreshed under the standing
sibling-status exception. Historical receipts, sibling assets, shared queue/progress,
world scenes and project settings remain unchanged.
