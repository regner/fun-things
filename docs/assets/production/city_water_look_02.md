# city_water_look.02 — Quieter basin surface look

10 October 2026. **Material-study delivery; independent review and world acceptance pending.**
Commissioned by Regner under [commission](commission.md) and the current per-asset production
brief. Producer: Codex asset specialist. Accepting owners: independent technical/art reviewer,
then world integrator; acceptance is not claimed. Family: [city_water_look](../city_water_look.md).
The production commission supersedes the concept-only restriction, not the exclusion of water
simulation, custom shaders, tides or containment.

## Design and dimensions

A still, cool dark blue/teal basin with broad soft reflections and no foam. Intended for **Old
Quay (05)** only; this is a variation of the shared water appearance, not a district water system.
References inspected: accepted Petrol & Coral direction, world-v1 stages 03/04, and Old Quay's
warm frontage against soft teal water. No district geometry or layout is authored here.

The delivered [open-sea sibling](city_water_look_01.md) supplies the family conventions: body
colour **#174351**, 16 m physical texture repeat, external opaque PBR material and no foam.
The basin's decoded normal XY RMS is **0.013217**, versus **0.092110** for the sibling: **14.35%**
as much normal variation. Roughness is 0.40 rather than 0.32, softening the reflection field.
This deliberate near-stillness preserves room for Old Quay's warmer streets and accents. It
is not an animated or physically measured sea-state model.

Original analytic texture artwork and Blender construction; no downloaded meshes, images,
brands, fonts or external artwork. Asset-specific recipes follow the sibling's conventions;
the shared Blender export contract is reused unchanged. No sibling files were modified.

The **provisional material-study swatch** is 16 × 0 × 16 m (Godot X/Y/Z), AABB
(-8, 0, -8) → (8, 0, 8), surface-centred pivot (0,0,0), metre units, identity root/mesh
transforms. Envelope tolerance ±0.001 m. This matches the sibling sample, not approved basin
geometry or dimensions inferred from a concept. Godot pads the planar AABB to 0.000010 m high;
actual GLB positions are Y=0. Blender +Z maps to Godot +Y; +Y maps to Godot -Z.

## Source, export, material and textures

- Source: `art/source/models/environment/city_water_look_02/city_water_look_02.blend`.
- Export collection `export_city_water_look_02`; root `CityWaterLook02`, child
  `CityWaterLook02_Mesh`, mesh `CityWaterLook02_Swatch`.
- GLB: `art/models/environment/city_water_look_02/city_water_look_02.glb`, with `.import`.
- Material: `art/materials/environment/city_water_look_02/quiet_basin.tres`.
- Textures: `art/textures/environment/city_water_look_02/quiet_basin_albedo.png` and
  `quiet_basin_normal.png`, with `.import` sidecars.
- Tools: `tools/asset_production/city_water_look_02/`: `author_textures.py`, `author.py`,
  `export.py`, `preview.py`, `validate.py`, `test_textures.py`, `check_prefab.gd` plus its UID.

One stable material slot, **`quiet_basin`**, remapped by saved GLB import settings to the external
material. There are no imported-child edits or prefab material overrides. Source Principled nodes
reference committed PNGs through relative paths. Export temporarily disconnects texture inputs,
restores them after export, and retains a flat body-colour fallback in the GLB. No PNGs are embedded.

Both maps are original **512 × 512 RGB PNGs**, UV0 [0,1]² at **16 m/repeat** (~32 texels/m).
Albedo is sRGB, no alpha or baked highlights, maximum channel range 2/255. Normal data is linear
**+Y/OpenGL** tangent space, green not inverted. Three low-amplitude integer-period analytic waves
produce seamless repeat; there is no displacement or animation. Source IOR=1.333; runtime
metallic=0, specular=0.25 (approximate water reflectance), roughness=0.40, normal scale=1.
Opaque/backface-culled, no emission, refraction, screen sampling or transparency.

Imports use lossless compression, generated mipmaps, linear-with-mipmaps filtering and repeat.
Normal-map import is explicitly enabled. No ORM or roughness map is needed. Preserve 16 m UV
scale and aligned phase across adjacent basin surfaces. The basin/open-sea transition still needs
world-owner treatment: do not assume their different normal fields can be joined without a visible
appearance boundary. No blending shader is introduced. Do not scale the sample as a coastline mesh.

## Prefab and collision

`scenes/prefabs/environment/city_water_look_02.tscn` is a `Node3D` wrapper with an identity
`Visuals/Model` imported instance. Godot normalized scene/dependency UIDs and node identities;
a second load/pack/save was byte-identical. No embedded mesh or runtime node construction.

**No collision is intentional.** This is a material swatch, not a freestanding solid, deck,
walkable ocean, boundary or gameplay actor. Water containment, actor/car exclusion, coastline
collisions and buoyancy remain unimplemented. Do not place it as a walk surface. No sockets,
rigs, animation, destruction states or explicit LODs are needed for a two-triangle sample.
Default imported tangent generation remains enabled.

## Evidence and measured checks

[Hero](city_water_look_02-evidence/hero.png) · [side](city_water_look_02-evidence/side.png) ·
[detail](city_water_look_02-evidence/detail.png) ·
[47 m / 42° overhead](city_water_look_02-evidence/overhead_47m_42deg.png).

Four isolated Blender Cycles CPU renders, 48 samples/denoising, AgX, **1280×720**, PNG compression
95, no dithering; each is under 160 KB. Same studio/cameras as the sibling permit comparison.
Cool/warm area lights test both accent families. Hero and side show one sample; detail crops the
unchanged material. Overhead is north-up, vertical-down perspective, 47 m high, **42° vertical FOV**,
with a 3×3 translation-only repeat field. Outer field edges remain visible, internal seams do not.
The 720-pixel height follows the newer evidence-size limit rather than the historical 800 reference.

Producer inspected all four and compared the sibling overhead: the basin has a smooth, nearly
still reflection field instead of broken swell highlights. Detail intentionally reads as a soft
colour/reflection gradient, not rippled foam or fine texture. Low-angle reflections are stronger.
These are **Blender-only appearance observations**, not Godot raster, actual street/actor contrast,
calibrated district lighting or moving-camera evidence.

[validation.json](city_water_look_02-evidence/validation.json) records:

- **4 source/export vertices, 2 triangles, 1 mesh, 1 surface; 256 m² area**.
- **0 degenerate faces**; 4 non-manifold edges, exactly the intentional open plane perimeter.
  No interior topology defects. Unit source/GLB normals and upward triangle winding.
- Actual GLB accessor bounds/UV checks; no images, cameras, skins or animations. Fresh export is
  **byte-identical** to the committed **1,328-byte GLB**.
- Actual Godot load: linked geometry, identity transform, correct external material/maps,
  4 vertices/2 triangles, up normals/generated tangents, stable second editor save roundtrip.
- **5 texture tests passed**: quiet family albedo, unit/calm but non-flat normals, independent
  sibling slope comparison, repeat-edge jumps ≤1/255, and fresh PNG byte equality.
- Canonical checks **returned 1**, solely because the clean compiler-mirror setup import exceeded
  the shared checker's internal **30-second** deadline. All **172 individual scripts compiled**;
  repository formatting/style passed. Its subsequent isolated import passed, as did **16 Python
  tests, 142/142 GUT tests (6,705 assertions)** and the expected failing GUT negative case.
  This is a setup/environment limitation, not a clean whole-suite PASS or a suppressed error.

[final.log](city_water_look_02-evidence/final.log) is the concise command/diagnostic receipt.
[manifest.json](city_water_look_02-evidence/manifest.json) hashes all produced files except itself.
Scratch logs, compiler mirror and reexports stay at `C:/tmp/ft/assets/city_water_look_02/`.

## Exact reproduction commands

Run from repository root in Git Bash. Blender 5.2.2 LTS build `d13f752e3b9c`, glTF exporter
5.2.40; Godot 4.8.dev7.official.c971f93e7. Python artwork uses NumPy 2.5.1/Pillow 12.3.0.
No live Blender/Godot MCP session is used. Text resource authoring is the required fallback;
headless normalization does not synchronize any separately open scene.

```sh
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_water_look_02
S=art/source/models/environment/city_water_look_02/city_water_look_02.blend
python "$T/author_textures.py"
python "$T/test_textures.py" -v
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 600 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/preview.py"
timeout 300 "$G" --headless --editor --path . --import --quit
timeout 60 "$G" --headless --editor --path . --script "res://$T/check_prefab.gd" -- --prepare
timeout 300 "$G" --headless --editor --path . --import --quit
timeout 60 "$G" --headless --editor --path . --script "res://$T/check_prefab.gd" -- --normalize
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py"
timeout 60 "$G" --headless --path . --script "res://$T/check_prefab.gd"
"$(mise which gdstyle)" fmt --check "$T/check_prefab.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd"
timeout 1800 env PYTHONUTF8=1 python tools/production_checks.py --godot "$G" --gdstyle "$(mise which gdstyle)" --output C:/tmp/ft/assets/city_water_look_02/checks
# Independent re-export, without source mutation:
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup "$S" --threads 4 --python-exit-code 1 --python "$T/export.py" -- C:/tmp/ft/assets/city_water_look_02/reexport
```

The canonical check output must be a fresh directory. `validate.py` consumes the texture-test and
normalized Godot receipts before plain load writes its separate receipt. To verify the manifest:

```sh
python - <<'PY'
import hashlib, json
from pathlib import Path
p = Path('docs/assets/production/city_water_look_02-evidence/manifest.json')
for entry in json.loads(p.read_text())['files']:
    raw = Path(entry['path']).read_bytes()
    assert len(raw) == entry['bytes']
    assert hashlib.sha256(raw).hexdigest() == entry['sha256'], entry['path']
print('Manifest payload hashes verified')
PY
```

## Diagnostics and remaining acceptance

Plain headless load is diagnostic-free. Import emits the existing MCP plugin's untested-4.8
warning. Editor-script preparation/normalization succeeds but reports shutdown RID/ObjectDB leaks,
as observed for the sibling; this is not described as a clean editor run. Blender emits forward
`use_nodes` deprecation warnings. No asset assertion failed; no unchanged failing check was retried.
The canonical setup timeout is retained, not ignored as one of the historical fixture failures.

Pending: independent art/technical disposition; native Godot lighting/reflections and street/actor
contrast; Old Quay placement/UV phase/coastline and basin-to-sea transition; moving-camera mip
aliasing; packaged-build and real-device/Deck performance. Later water interaction or gameplay
collision needs its own authority/movement/network checks. This delivery changes no world scenes,
water simulation, shared brief, register, progress tracker or global tooling.
