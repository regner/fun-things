# city_water_look.01 — Open sea surface look

10 October 2026. **Material-study delivery; independent review and world/visual acceptance pending.**
Production commissioned by Regner under [commission](commission.md) and the current per-asset
production brief. This supersedes the family brief's concept-only restriction, not its exclusion
of water simulation, custom shaders, tides or containment. Producer: Codex asset specialist.
Accepting owners: independent technical/art reviewer, then world integrator; neither gate is claimed.
Family: [city_water_look](../city_water_look.md). No sibling asset existed when this work began.

## Design and dimensions

Cool dark blue/teal body colour, broad smooth swell reflections, no foam or fine noise.
One shared open-sea appearance for coastal districts 01–05 and 07–09; not a separate water
system per district. It supports Old Quay's warm frontage, Glassward's cool accents and East
Docks' amber hardware without adding luminous water. Original analytic texture artwork and
original Blender construction; no downloaded geometry, images, brands or external artwork.
References inspected: accepted Petrol & Coral direction and world-v1 stages 03/04, especially
Old Quay's soft teal water and East Docks' cool water/warm equipment relationship.

The **provisional material-study swatch** is 16 × 0 × 16 m in Godot X/Y/Z, one plane, with
AABB (-8, 0, -8) → (8, 0, 8). This is a convenient physical texture sample, not approved sea
geometry or a placement dimension inferred from a concept. Surface-centred pivot (0,0,0),
metre units, identity root and mesh transforms. Blender +Z maps to Godot +Y and +Y to -Z.
Envelope tolerance ±0.001 m. Godot pads the zero-height AABB to 0.000010 m; actual GLB
vertices remain at Y=0. No displacement, tide amplitude, thickness or walkable surface is implied.

## Source, exports, material and texture contract

- Source: `art/source/models/environment/city_water_look_01/city_water_look_01.blend`.
- Export collection: `export_city_water_look_01`; root `CityWaterLook01`, child
  `CityWaterLook01_Mesh`, mesh `CityWaterLook01_Swatch`.
- Export: `art/models/environment/city_water_look_01/city_water_look_01.glb` plus `.import`.
- Material: `art/materials/environment/city_water_look_01/open_sea.tres`.
- Textures: `art/textures/environment/city_water_look_01/open_sea_albedo.png` and
  `open_sea_normal.png`, with committed import sidecars.
- Tools: `tools/asset_production/city_water_look_01/` contains `author_textures.py`,
  `author.py`, `export.py`, `preview.py`, `validate.py`, `test_textures.py` and
  `check_prefab.gd` with its Godot UID sidecar.

One stable material slot, `open_sea`. Godot's saved GLB import settings remap it to the
external material. The prefab has **no imported-child edits or material overrides**. The
source Principled material references the committed PNGs by relative paths. Export temporarily
disconnects texture inputs and restores them afterward: GLB contains a flat base-colour fallback,
not embedded images or a second copy of the texture set. Runtime appearance comes from the `.tres`.
No procedural material node is silently lost during export.

Both textures are original 512 × 512 RGB PNGs, 16 m per UV0 repeat, about 32 texels/m.
UV0 covers [0,1]² on the sample. Albedo is sRGB around **#174351**, with less than 7/255
channel variation and no baked directional highlights. Normal data is linear tangent-space
**+Y/OpenGL**, without green inversion. Integer-period swells and analytically differentiated
slopes provide seamless repeat; they do not displace geometry or animate. The source uses
IOR 1.333; Godot uses dielectric metallic=0 / specular=0.25 (approximately water's normal-incidence
reflectance), roughness=0.32, normal scale=1. Opaque, backface-culled, no emission, refraction,
screen sampling or transparency. Reflections depend on scene lighting/environment.

Godot texture imports use lossless compression, generated mipmaps, linear-with-mipmaps
filtering and repeat. Normal import is explicitly enabled; albedo remains colour data.
These small maps need no ORM texture or separate roughness image. Preserve 16 m physical UV
scale and aligned UV phase across adjoining surfaces when adopting this material. Do not scale
the swatch as a substitute for authoring coastline geometry. Lighting, coastline boundaries and
basin/open-sea transitions belong to downstream integration, not this prefab.

Family handoff to `.02`: reuse the same dark blue/teal direction, external PBR slot convention,
16 m texture reference scale and no-foam rule; distinguish the basin by calmer normal/reflection
variation. These are compatible provisional appearance inputs, not a commissioned water system.

## Prefab and collision

`scenes/prefabs/environment/city_water_look_01.tscn` is a saved `Node3D` wrapper with
`Visuals/Model` instancing the imported GLB at identity. UID and editor node identities were
normalized headlessly; a second load/pack/save was byte-identical. Geometry remains the imported
resource; there are no embedded meshes or runtime-authored nodes.

**No collision is intentional:** this is a material sample, not a freestanding solid, deck,
walkable ocean, boundary or gameplay actor. Authoritative water containment, actor/car exclusion,
coastline collisions and any future buoyancy remain wholly unimplemented and unaccepted. Do not
place this swatch as a walk surface. No rigs, sockets, animations, LOD variants or destruction states
are needed for a two-triangle material-study sample. Default importer tangent generation is enabled.

## Evidence and validation

[Hero](city_water_look_01-evidence/hero.png) · [side](city_water_look_01-evidence/side.png) ·
[detail](city_water_look_01-evidence/detail.png) ·
[47 m / 42° overhead](city_water_look_01-evidence/overhead_47m_42deg.png).

All four are isolated Blender Cycles CPU renders, 48 samples/denoising, AgX, 1280×720,
PNG compression 95, dithering disabled for lean evidence. Studio cool/warm area lights test
both accent families. Hero/side show the single sample; detail crops the same unchanged material.
Overhead uses nine translation-only instances of the same swatch, centred under a vertical-down,
north-up perspective camera at Z=47 m, **42° vertical FOV**. The 48 m-wide test field intentionally
has visible outer side edges; it is not an authored sea or district scene. The 720-pixel height
follows the newer evidence-size rule rather than the historical 800-pixel reference.

Producer inspected all four: broad muted highlights, dark quieter areas and no visible internal
repeat seam at the gameplay-camera distance. The low-angle view shows stronger grazing reflections.
Close-up softness is intentional broad reflection response, not detailed foam. This is **Blender
appearance evidence only**: no Godot raster capture, street/actor comparison, calibrated district
lighting acceptance or moving-camera shimmer result is claimed.

[validation.json](city_water_look_01-evidence/validation.json) records:

- **4 source/export vertices, 2 triangles, 1 mesh, 1 surface; 256 m² area**.
- Zero degenerate faces. Four non-manifold edges, all four the **intentional open perimeter**
  of the single-sided material swatch; no interior topology defects. Unit source/GLB normals.
- Actual GLB accessor checks: exact bounds, UV range, upward triangle winding, no images,
  cameras, rigs or animations. Fresh re-export is **byte-identical** to the 1,328-byte GLB.
- Actual Godot load: linked imported geometry, identity transforms, external material remap,
  4 vertices / 2 triangles, unit up normals/generated tangents, correct maps/mip/repeat settings,
  no collision, and stable second editor save/load/pack roundtrip.
- Four separate texture tests pass: quiet dark albedo; outward unit normals within 0.007
  quantization error; wrap jumps no greater than adjacent texels and ≤4/255; fresh PNG authoring
  byte-identical to both committed images.
- Canonical production checks passed: **171 scripts compiled; 16 repository Python tests;
  142/142 GUT tests, 6,705 assertions**; intentional negative GUT case returned 1 as expected.
  The four asset-specific texture tests were run explicitly in addition to that suite.

[final.log](city_water_look_01-evidence/final.log) retains a concise command/result and diagnostic
receipt; [manifest.json](city_water_look_01-evidence/manifest.json) hashes every delivered file
except itself. Scratch logs/reexports are outside the repository at
`C:/tmp/ft/assets/city_water_look_01/`.

## Exact reproduction commands

From the repository root, Git Bash. Python texture authoring uses NumPy 2.5.1 / Pillow 12.3.0;
Blender is 5.2.2 LTS build `d13f752e3b9c`, glTF exporter 5.2.40. Export loads the unmodified shared
`tools/assets/blender/export_settings.json`; collection filtering, no animations/skins/cameras/lights.
No live Blender/Godot session is used. Headless Godot is pinned 4.8.dev7.official.c971f93e7.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_water_look_01
S=art/source/models/environment/city_water_look_01/city_water_look_01.blend
python "$T/author_textures.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 600 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/preview.py"
timeout 300 "$G" --headless --editor --path . --import --quit
timeout 60 "$G" --headless --editor --path . --script "res://$T/check_prefab.gd" -- --prepare
timeout 300 "$G" --headless --editor --path . --import --quit
timeout 60 "$G" --headless --editor --path . --script "res://$T/check_prefab.gd" -- --normalize
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py"
timeout 60 "$G" --headless --path . --script "res://$T/check_prefab.gd"
python "$T/test_textures.py" -v
"$(mise which gdstyle)" fmt --check "$T/check_prefab.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd"
timeout 1800 env PYTHONUTF8=1 python tools/production_checks.py --godot "$G" --gdstyle "$(mise which gdstyle)" --output C:/tmp/ft/assets/city_water_look_01/checks
# Standalone re-export to scratch, without source mutation:
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup "$S" --threads 4 --python-exit-code 1 --python "$T/export.py" -- C:/tmp/ft/assets/city_water_look_01/reexport
```

The production-check output directory must be fresh on a rerun. `validate.py` consumes the preceding
Godot receipt and independently fresh-exports the source. Verify the complete producer manifest with:

```sh
python - <<'PY'
import hashlib, json
from pathlib import Path
p = Path('docs/assets/production/city_water_look_01-evidence/manifest.json')
for entry in json.loads(p.read_text())['files']:
    raw = Path(entry['path']).read_bytes()
    assert len(raw) == entry['bytes']
    assert hashlib.sha256(raw).hexdigest() == entry['sha256'], entry['path']
print('Manifest payload hashes verified')
PY
```

## Diagnostics and remaining acceptance

No editor tools are used: the commission prohibits live MCP sessions and the windowed editor is
unavailable. Resources were authored as text, then imported/normalized/reloaded by isolated headless
processes; this does not synchronize any separately open scene.

Initial tooling corrections: fixed a CLI-version-string versus engine-dictionary assertion, replaced
an exact zero-height Godot AABB expectation with the stated 1 mm tolerance (engine padding is 10 μm),
and corrected Blender `Vector.length` property access. Helper failures now prevent a PASS receipt.
A first premature editor quit aborted scanning; the check now waits for editor startup/scan completion.
Blender emits only its forward-looking `use_nodes` deprecation warning. No unchanged failed command
was repeated. Source geometry and appearance did not need corrective remodelling.

Final **plain headless load is diagnostic-free**. Headless import emits the existing MCP plugin's
untested-4.8 warning. The separate `--editor --script` normalization exits 0 and validates stable saves
but still emits editor shutdown RID/ObjectDB leak diagnostics; this is recorded, not called a clean
editor run. Canonical isolated compilation, import and gameplay tests all passed without suppressed
failures. No shared code or tooling was altered to hide diagnostics.

Pending: independent art/technical disposition; actual Godot lighting/reflection and actor/street
contrast review; world UV scale/phase/coastline and basin transition placement; moving-camera mip
aliasing; real-device/Deck performance and packaged-build appearance. Any later gameplay collision
or water interaction requires its own authority/movement/network validation. This delivery does not
mark the asset register ready, change world placement or implement a water system.
