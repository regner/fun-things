# d03_apartment_family.05 — Straight one-storey apartment bay

10 October 2026. **Original source, linked export and bounded prefab checks delivered;
independent review and world acceptance pending.** Production commissioned under the
[register commission](commission.md), superseding the concept-only restriction in the
[family brief](../d03_apartment_family.md). Producer: commissioned implementation worker.
Accepting art/technical reviewer: unassigned. No shared register, district placement,
road, gameplay or other asset files changed.

## Design and dimensions

A repeatable, closed-exterior Terrace Ward storey with paired broad domestic windows
on both long-run facades, pale frames/sills, teal aprons and a continuous pale floor
ribbon. Blue-grey render stays quiet; coral is reserved for shared corners and warm
bands for entrances rather than repeated on every bay. The unadorned side faces and
top are **mating planes**, not finished end-wall or roof designs. No interior,
operable window, doorway, roof traversal or destruction state is implied.

Original Blender construction, without downloads, third-party geometry, textures,
brands, image-to-mesh, or runtime-generated visible meshes. References inspected:
[Terrace Ward identity](../../concepts/world-v1/stage-03-district-identities/README.md#terrace-ward--a-neighbourhood-of-shared-courts),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and
[District 03 map context](../../concepts/districts-v1/map-context.md#district-03).
The selected district's 4.80 ha and existing 24 × 15 / 32 × 14 / 18 × 16 m greybox
footprints are context, not an allocation or accepted replacement envelope.

### Provisional family interface — metres, Godot local axes

These are authored provisional values permitted by the standing production brief,
not measurements inferred from concept imagery or a city-wide grid. They establish
this first component's compatibility contract; placements must not stretch windows.

| Interface | Value |
| --- | --- |
| Bay / stack pitch | X = 6.0 m; Y = 3.2 m |
| Structural depth | Z = 12.0 m |
| Origin | Ground-centred structural footprint, (0, 0, 0) |
| Closed core / collider AABB | Min (-3, 0, -6); max (3, 3.2, 6) |
| Whole visual AABB | Min (-3, 0, -6.18); max (3, 3.2, 6.18) |
| Whole visual size X/Y/Z | 6.0 × 3.2 × 12.36 m |
| Left / right joins | X = -3 / +3; no overhang beyond these planes |
| Bottom / top joins | Y = 0 / 3.2; square core edges, no bevel gaps |
| Front / rear wall planes | Z = -6 / +6 |
| Front / rear trim envelope | At most 0.18 m outward from the wall |
| Window centres | X = -1.5 / +1.5, identical on front and rear |
| Closed visible glazing | 2.10 m wide; Y = 1.00…2.55 m |
| Frame / apron / head extents | Frame Y = 0.90…2.65; apron 0.35…1.01; head to 2.74 m |
| Floor ribbon | Full 6 m width; Y = 0.04…0.20; 0.10 m outward |
| Dimensional tolerance | ±0.001 m; source-to-GLB coordinate comparison ±0.00001 m |

Place an adjoining copy at (6, 0, 0) and a stacked copy at (0, 3.2, 0), without
rotation/scale correction. Core end/top faces deliberately remain closed to keep each
component manifold; their coincident mating surfaces are hidden inside assemblies.
Window trim does not cross X or storey connector planes. Finished end treatments must
cover the exposed core face; roof components seat at the top-storey Y = 3.2 datum.
An entrance replacement should preserve the same core footprint and stacking pitch.
A frontage add-on must account for the 0.18 m trim envelope; glazing here is an opaque
closed surface, **not a through-opening for a traversable loggia**. Corners and height
changes must use their own compatible treatment rather than exposing internal seams.
No sockets are needed: these static numeric planes are the assembly interface.

## Source, export and materials

- Source: `art/source/models/environment/d03_apartment_family_05/d03_apartment_family_05.blend`.
- Collection: `export_d03_apartment_family_05`.
- Root / mesh: `D03ApartmentFamily05` / `D03ApartmentFamily05_Mesh`.
- Export: `art/models/environment/d03_apartment_family_05/d03_apartment_family_05.glb`.
- Prefab: `scenes/prefabs/environment/d03_apartment_family_05.tscn`.
- Tools: `tools/asset_production/d03_apartment_family_05/` (`author.py`, `export.py`,
  `validate.py`, `check_prefab.gd`, `record.py`).

Blender 5.2.2 LTS, build `d13f752e3b9c`, glTF exporter 5.2.40. The exporter consumes
`tools/assets/blender/export_settings.json`, limiting export to the named collection
with animation and skin export disabled. Metre units; transforms applied; root and
mesh at identity. Blender +Y front maps once to Godot -Z, +Z to +Y. Editable closed
parts are joined into one static mesh; bevel/weighted-normal modifiers are applied.
Studio lights, camera, ground and hidden 1 m reference remain outside the collection.

Four opaque, back-culled, texture-free Principled surfaces, in export order:

| Slot | Material | sRGB swatch | Roughness / metallic |
| --- | --- | --- | --- |
| 0 | `terrace_bluegrey_render` | `#829398` | 0.76 / 0 |
| 1 | `terrace_pale_frame` | `#C5CABF` | 0.53 / 0 |
| 2 | `terrace_teal_spandrel` | `#31656A` | 0.65 / 0 |
| 3 | `terrace_petrol_closed_glass` | `#1E3645` | 0.29 / 0.12 |

No textures, embedded images, external material dependencies, rigs, clips or explicit
LODs. Engine import defaults retain automatic mesh LOD generation; distance behavior
and repeat-instance cost are not performance-accepted.

## Evidence and measured validation

[Hero](d03_apartment_family_05-evidence/hero.png) ·
[side/mating face](d03_apartment_family_05-evidence/side.png) ·
[window detail](d03_apartment_family_05-evidence/window_detail.png) ·
[47 m / 42° overhead](d03_apartment_family_05-evidence/overhead_47m_42deg.png).
All four final renders were inspected by the producer. Isolated Blender Cycles CPU,
32 samples, AgX, 1280 × 720, PNG compression 95, dithering disabled for lean evidence;
each PNG is under 304 KB. The overhead is vertical-down, north-up perspective with
42° **vertical FOV**, at 47 m, using the standing 720 px evidence-height cap. It shows
the quiet unfinished top mating plane; window information is not legible overhead
and is not required gameplay information. This is not a completed roof composition,
a Godot capture, or evidence that court routes/actors remain visible in placement.

[validation.json](d03_apartment_family_05-evidence/validation.json) retains source,
actual binary GLB and Godot observations. [manifest.json](d03_apartment_family_05-evidence/manifest.json)
hashes every delivered payload except itself. [Final check summary](d03_apartment_family_05-evidence/final-checks.log)
distinguishes successful assertions from tool diagnostics.

- **2,532 triangles; 1,320 source vertices; 1,744 exported vertices; one mesh / four surfaces.**
- Zero non-manifold edges, zero degenerate source faces or actual GLB triangles.
- Source corner normals and actual exported normals are unit length; finite vertices,
  independent literal connector corners, dimensions, ground datum and axes pass.
- Fresh re-export from the final saved source is byte-identical to the delivered GLB.
- Final source: **140198 bytes**, SHA-256
  `a51e4ee2110bb71d9d82f8daea3f063566764cdd26754b8c87028fcefd44a2bc`.
- Final GLB: **74984 bytes**, SHA-256
  `25cd2902d8d7516d7a88364c2f06d276c0af2460bbc234bedbc461a92a5cb6b6`.

### Prefab, collision and engine checks

Godot 4.8.dev7.official.c971f93e7 headless import succeeds without ERROR/SCRIPT ERROR
lines. The wrapper was authored as text because live editor sessions are prohibited,
then loaded, packed, saved and reloaded headlessly. Its second editor-mode save is
byte-stable, preserving imported linkage, UIDs and node identities. No inherited
variant or editable-child override is used. `Visuals/Model` instances the imported
GLB at identity; mesh data is not copied into the scene.

`Collision/Body/Core` is the only collider: BoxShape3D (6, 3.2, 12) centred at
(0, 1.6, 0), StaticBody3D layer 1 / mask 0. It matches the full closed core exactly;
shallow decorative frames/sills/aprons do not produce snagging colliders. There is
no usable interior, entrance hole or overhanging solid volume added to the collider.

The final runtime check has no errors, missing dependencies or assertion failures:
seven actor-capsule solid/clear queries; a front aim hit at Z = -6; actual adjacent
and stacked prefab seam rays at X = 3 and Y = 3.2 both hit Z = -6; and a 1.9 × 1.5 ×
4.3 m car-box sweep blocks at the facade while the east bypass remains clear.
Production `ActorMotion.step` checks front, rear, side and bypass in AUTHORITY and
REPLAY modes: both modes produce identical positions, including Z = ±6.3502574 m
front/rear stops, X = 3.3502574 m side stop, and bypass Z ≈ -2.9999936 m. This is
bounded local physics/API evidence, not car handling or multiplayer transport proof.

Tool limitation: custom SceneTree normalization under `--editor` exits 0 and passes
byte-stability assertions but emits headless editor RID/ObjectDB shutdown-leak
diagnostics (and the addon's untested-engine-version warning). Waiting for editor
scanning removed the aborted-scan warning, not the shutdown leaks. Runtime-only
normalization avoided those diagnostics but stripped serialized UIDs; that trial was
superseded by the final editor-mode normalization. The tool now rejects runtime-only
normalization. Final import and runtime checks are clean; no errors are suppressed.
Blender's `use_nodes` deprecation notices are for Blender 6, not failures on the pin.

## Exact reproduction

From repository root, Git Bash; each Blender call uses the required isolated flags.
Scratch output is outside the repository. Never attach to a live editor session.

```sh
NID=d03_apartment_family_05
TOOLS=tools/asset_production/$NID
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
mkdir -p C:/tmp/ft/assets/$NID
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/author.py"
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --editor --path . --script "$TOOLS/check_prefab.gd" -- --normalize
timeout 180 "$GODOT" --headless --path . --script "$TOOLS/check_prefab.gd"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/validate.py"
mise exec -- gdstyle fmt --check "$TOOLS/check_prefab.gd"
mise exec -- gdstyle --max-line-length 100 --max-warnings 0 "$TOOLS/check_prefab.gd"
python "$TOOLS/record.py" --check
```

`validate.py` loads the saved source and calls `export.py` into scratch before comparing
bytes. To export manually, open the saved `.blend` in the same bounded Blender CLI
and run `export.py -- C:/tmp/ft/assets/d03_apartment_family_05/reexport`. After an
intentional source revision, refresh the validation/handoff receipts and run
`record.py` without `--check` last. Source `.blend` serialization is not promised
byte-identical across a new `author.py` run; re-export from the committed source is.

## Remaining acceptance

- Independent art/technical review of this component and its provisional interface.
- World-integrator approval of actual plot fit, run lengths, storey counts, court
  mouths/cross-links and roof/actor sightlines using saved placements.
- Actual in-engine visual/gameplay-camera review, production vehicle movement,
  authoritative network/transport behavior in context, and packaged dependency checks.
- Repeated-placement draw-call, GPU/frame pacing, memory and Deck LCD/OLED profiling.

No full city placement or target-device/gameplay acceptance is claimed. The registry,
not this handoff, tracks production of other family records.
