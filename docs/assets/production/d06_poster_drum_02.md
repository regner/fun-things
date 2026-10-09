# d06_poster_drum.02 — Cap variant

**Source/export and bounded prefab checks delivered; independent review and gameplay
acceptance pending.** Commission: [production commission](commission.md), resumed by
the per-asset task. Family: [poster drum](../d06_poster_drum.md). Producer: commissioned
implementation/modeling specialist. The supervisor approved the shallow dome, muted
coral inset, provisional dimensions, unchanged appended body and cylinder envelope
in the live task handoff. No shared register, brief, project setting or world changed.

## Design and dimensions

A shallow domed petrol cap replaces the [standard drum](d06_poster_drum_01.md)'s flat
cap. A narrow, non-emissive muted-coral annulus sits in the dome's shoulder. This is
one continuous closed cap mesh, not an overlapping decal or luminous ring. The broad
ivory poster carrier and cast petrol foot are unchanged. No advertisements, logos,
text, light, interaction, animation or changing-ad system is added. Commercial
artwork belongs to `d06_commercial_graphics`.

The approved delivery is a **complete alternate drum**, not a cap stacked on `.01`.
The author script appends `.01`'s body from its committed Blender source, reparents
and renames it, and constructs only the new cap. `.01`'s files remain untouched.
Validation compares all body vertices, faces, smooth flags, corner normals, UVs,
material indices and material values exactly against that saved family source.

Authored provisional dimensions, **not measurements from concept imagery**:

| Property | Metres |
| --- | --- |
| Complete Godot X/Y/Z size | 0.90 / 1.53 / 0.90 |
| Godot AABB min → max | (-0.45, 0, -0.45) → (0.45, 1.53, 0.45) |
| Replacement cap seating height / radius | 1.35 / 0.42 |
| Replacement cap top / maximum radius | 1.53 / 0.45 |
| Cap total height / rise above standard cap | 0.18 / 0.08 |
| Coral annulus outer / inner radius | 0.404 / 0.364 |
| Unchanged foot maximum diameter | 0.89 |
| Unchanged poster radius / bottom / top | 0.397 / 0.24 / 1.28 |
| Poster usable height / circumference | 1.04 / approximately 2.4945 |

Ground-centred root and mesh origins (0,0,0), metre units, applied identity transforms.
Blender +Z maps to Godot +Y; Blender +Y/front maps to Godot -Z. Dimension tolerance
±0.001 m; source/export coordinate tolerance 0.00001 m. The 1.53 m drum remains below
the 1.8 m reference actor and keeps the same small footprint. This supports the
subordinate scale intent but is not populated actor/hall or sightline acceptance.

### Family and graphic interfaces

Source collection `export_d06_poster_drum_02` contains root `D06PosterDrum02`, mesh
`D06PosterDrum02_Body`, and mesh `D06PosterDrum02_Cap`. Both meshes have ground origins;
the cap geometry starts at Y=1.35 m in Godot, not at local Y=0. This full alternate
prefab must replace a standard drum instance, not be added over one.

Body slots remain 0 `drum_frame_petrol`, 1 `poster_wrap`. Cap slots are
0 `drum_frame_petrol`, 1 `cap_inset_coral`. Poster `UVMap`/glTF TEXCOORD_0 is unchanged:
complete wrap once over [0,1]², U=0/1 rear seam (Godot +Z), U=0.5 front (-Z). Blender
V=0 is bottom, V=1 top; glTF image convention reverses V (top 0, bottom 1). Suggested
art aspect is approximately 2.40:1. Future artwork should be opaque and seamless
across U, edge-clamped with mipmaps; resolution/filtering remain its owner's choice.
No placeholder texture, extra poster mesh or artwork implementation is included.

## Source, exports, materials and prefab

- Source: `art/source/models/environment/d06_poster_drum_02/d06_poster_drum_02.blend`.
- Body authoring dependency: `.01`'s committed source at
  `art/source/models/environment/d06_poster_drum_01/d06_poster_drum_01.blend`, from
  lane commit `a9a32f4`; exact SHA-256 retained in validation.json. Appended data is
  local to `.02`'s saved source: runtime and ordinary reexport do not load `.01`.
- Export: `art/models/environment/d06_poster_drum_02/d06_poster_drum_02.glb` and its
  Godot `.import` metadata.
- Tools: `tools/asset_production/d06_poster_drum_02/author.py`, `validate.py`,
  `export.py`, `check_prefab.gd` and its engine-generated `.uid`.
- Prefab: `scenes/prefabs/environment/d06_poster_drum_02.tscn`, with embedded scene
  UID and engine-generated node identities; no separate TSCN `.uid` is needed.

Original project-owned Blender construction only: no downloads, paid models,
image-to-mesh, brands, external fonts or textures. Blender **5.2.2 LTS**, build
`d13f752e3b9c`, glTF exporter **5.2.40**. The explicit collection export loads the
shared `tools/assets/blender/export_settings.json` contract and disables skins and
animations. Three declared objects export; studio camera, lights and floor do not.
The recipe/check structure follows the preceding family asset; no shared scene or
export settings are edited. No shared parametric drum-authoring helper exists.

Three opaque backface-culled Principled materials, no textures or emission:

| Material | Linear RGB | Metallic | Roughness |
| --- | --- | --- | --- |
| drum_frame_petrol | (0.025, 0.075, 0.09) | 0.40 | 0.43 |
| poster_wrap | (0.922, 0.880, 0.716) | 0 | 0.70 |
| cap_inset_coral | (0.52, 0.16, 0.12) | 0.15 | 0.50 |

No material override is needed. Imported LODs and shadow meshes use existing import
defaults; there is no custom LOD or accepted per-asset performance budget.

The saved wrapper follows street-furniture conventions: identity imported instance
at `Visuals/Model`, separate `Collision/Body` StaticBody3D with direct `Shape` child.
CylinderShape3D radius 0.45 m, height 1.53 m, centre Y=0.765 m, static-world layer 1 /
mask 0. The conservative cylinder includes the dome without tiny decorative snag
surfaces. No runtime script, hierarchy construction, mesh copy, navigation,
destruction, sockets or gameplay component is attached.

## Evidence and validation

[Hero](d06_poster_drum_02-evidence/hero.png),
[side](d06_poster_drum_02-evidence/side.png),
[cap detail](d06_poster_drum_02-evidence/cap_detail.png),
[47 m / 42° overhead](d06_poster_drum_02-evidence/overhead_47m_42deg.png).
The first three are 900×900 isolated Blender renders. The overhead is 1280×800,
vertical-down north-up perspective, 47 m high / 42° vertical FOV. All four final
renders were visually inspected. An initial near-horizontal smoothing threshold
created concentric crown bands; smoothing the complete dome removed them before
final export. The muted coral edge distinguishes the cap while its quiet circular
roof stays roughly 20 pixels across overhead. Blank side artwork does not carry
essential overhead information. These are not actual Godot gameplay captures or
proof of actor contrast, populated streets, moving-camera readability or performance.

[validation.json](d06_poster_drum_02-evidence/validation.json) records:

- **3,064 triangles; 1,536 Blender vertices; 2,076 GLB vertices; two meshes;
  four material surfaces using three materials.** Body and cap each have 768 source
  vertices and 1,532 triangles; triangulation includes their closed end faces.
- Zero non-manifold edges, zero degenerate source faces, zero degenerate GLB
  triangles; unit-length source corner and exported normals.
- Literal approved bounds, cap seating plane/radius, ground pivot, identity
  transforms, full unchanged-body comparison and poster UV extents pass.
- Fresh export from the reopened source is **byte-identical** to the committed
  **87,912-byte** GLB. SHA-256:
  `58115616cd1adfadd9a485cc69027f64324e75ab6c8ef462736c1b999ad69f3c`.
- Pinned Godot **4.8.dev7.official.c971f93e7** imports and resolves dependencies;
  linked ancestry, mesh/surface counts, bounds, collision dimensions and UIDs pass.
  Pack/save/reopen/resave is byte-stable.
- Actual physics rays hit the body and raised cap envelope; side and overhead
  rays remain clear. These bounded ray tests do not establish actor/car motion,
  aiming in a populated scene or authoritative/predicted multiplayer equivalence.

Owned GDScript is formatter-clean, lint-clean and explicitly compiles; it also
passes the canonical 47-script compilation run. Nine Python tests and nine GUT
tests / 70 assertions pass, as do engine/vendor pins, GUT import and the deliberate
negative-test detector. The overall production suite **returns 1** only for the
authorized existing five `tests/fixtures/asset_production` compile failures (missing
S02ActorMotion/S02AimProbe), plus formatting in `batch_observation.gd`,
`integration/batch03_author.gd` and `integration/inspector.gd`. No unrelated file was
modified to conceal those failures.

The concise [final log](d06_poster_drum_02-evidence/final.log) records commands,
results and diagnostic classification. Headless editor save checks pass and exit 0,
but editor shutdown emits RID/ObjectDB leak diagnostics, as in `.01`; the toolkit
also warns that 4.8 is newer than its tested 4.7. A separate headless runtime load
and targeted compile both exit 0 with **no errors, warnings or missing dependencies**.
Blender emits pinned-API `use_nodes` deprecation warnings, not modeling failures.
Scratch renders, intermediate exports and raw logs remain outside the repository.

## Exact reproduction

Run from repository root in Bash. All Blender/Godot calls are isolated and bounded;
no owner live Blender/Godot session is touched. Prefab text was packed/resaved in
headless editor mode because this task prohibits live/windowed editor mutation.
Headless checks do not claim a separate open editor is synchronized.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
N=d06_poster_drum_02
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/$N/author.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/$N/validate.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  art/source/models/environment/$N/$N.blend --python-exit-code 1 \
  --python tools/asset_production/$N/export.py -- C:/tmp/ft/assets/$N/reexport
timeout 300 "$(mise which godot)" --headless --editor --path . --import --quit
timeout 180 "$(mise which godot)" --headless --editor --path . \
  --script res://tools/asset_production/$N/check_prefab.gd
timeout 180 "$(mise which godot)" --headless --path . \
  --scene res://scenes/prefabs/environment/$N.tscn --quit-after 3
timeout 180 "$(mise which godot)" --headless --path . --check-only \
  --script res://tools/asset_production/$N/check_prefab.gd
mise exec -- gdstyle fmt --check tools/asset_production/$N/check_prefab.gd
mise exec -- gdstyle --max-line-length 100 --max-warnings 0 \
  tools/asset_production/$N/check_prefab.gd
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/$N/checks
```

Production checks require a fresh output directory. `validate.py` itself performs
the scratch reexport/byte comparison. Reauthoring may change Blender save metadata;
GLB reexport identity, not `.blend` regeneration identity, is asserted. Run the
Godot check after validation to append engine evidence. `manifest.json` hashes every
retained produced file except itself, including source, GLB/import metadata,
script/UID, scene, documentation and lean evidence. `.01` is a hashed input, not a
produced file in this manifest.

## Remaining acceptance

Independent art/technical review is pending. Final dimension and placement approval,
actual gameplay-camera capture, actor/car movement, combat visibility, multiplayer
transport/prediction, packaged build and sustained target-device/Deck performance
remain downstream. World integration must keep this accent away from intersection
sightlines, passage mouths and bridge landings, and refresh any affected collision /
navigation data. Poster artwork remains its separate owner's scope. No world
placement, complete-register readiness or gameplay gate is marked accepted.
