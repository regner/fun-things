# d03_apartment_family.11 — Height-step closure

10 October 2026. **Original flashing, linked component prefab and bounded checks delivered;
independent review and world acceptance pending.** Commissioned under the
[register commission](commission.md), superseding the concept-only restriction in the
[family brief](../d03_apartment_family.md). Producer: commissioned implementation worker.
Accepting art/technical reviewer: unassigned. No world, shared register, gameplay,
road or sibling asset files changed.

## Design and dimensions

A reusable **one-storey height-step closure** for Terrace Ward's stepped bars. It combines:

1. The unchanged [finished end wall](d03_apartment_family_07.md), elevated one storey.
2. The unchanged [roof end cap](d03_apartment_family_10.md), covering that wall.
3. One new Blender-authored continuous sloped flashing, with a pale counterflashing
   fold and two blue-grey end-return aprons at the lower-roof junction.

**Supervisor-approved reuse:** do not build another copy of the existing wall/cap.
The new source and GLB contain only the missing flashing. The saved wrapper composes
the two delivered sibling prefabs. Their blue-grey render, teal blind aprons, pale
pilasters and restrained coral terminal arrises remain unchanged. The new flashing
uses the roof set's two existing swatches, not another neon roof stripe.

All six earlier handoffs were inspected: [straight](d03_apartment_family_05.md),
[corners](d03_apartment_family_06.md), [end](d03_apartment_family_07.md),
[entrance](d03_apartment_family_08.md), [balcony](d03_apartment_family_09.md), and
[roof caps](d03_apartment_family_10.md). References also inspected:
[Terrace Ward identity](../../concepts/world-v1/stage-03-district-identities/README.md#terrace-ward--a-neighbourhood-of-shared-courts),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and
[District 03 map context](../../concepts/districts-v1/map-context.md#district-03).
The 4.80 ha district is context, not a plot allocation or a changed city grid.

Original Blender construction only: no downloads, brands, third-party geometry,
textures, image-to-mesh or runtime-generated visible meshes. No interior, working
window, door, roof access, climbing, drain simulation, destruction or interaction
state is introduced. The lower roof is **not** an accessible terrace or walking route.

### Provisional interface — metres, Godot local axes

The existing **6 m bay pitch, 12 m building depth, 3.2 m storey pitch and 0.24 m
end-wall thickness** are unchanged. Flashing dimensions are provisional authored
choices, explicitly approved by the supervisor, not inferred from concept imagery.

| Interface | Value |
| --- | --- |
| Root / new mesh pivot | (0, 0, 0), ground-reference centre of the end-wall footprint |
| Exposed direction / reverse | +X / rigid 180° yaw about Godot +Y |
| New flashing visual min / max | (-0.12, 3.18, -6.12) / (0.50, 3.80, 6.12) |
| New flashing size X/Y/Z | 0.62 × 0.62 × 12.24 m |
| Whole composed prefab min / max | (-0.12, 3.18, -6.12) / (0.50, 6.72, 6.12) |
| Whole composed prefab size X/Y/Z | 0.62 × 3.54 × 12.24 m |
| Linked upper wall local position | (0, 3.2, 0); core Y = 3.20…6.40 |
| Linked upper end cap local position | (0, 3.2, 0); underside Y = 6.40, coping top 6.72 |
| Main flashing longitudinal span | Z = -5.98…5.98 |
| Main flashing backing / toe | X = 0.10 / 0.50 |
| Main flashing bottom / head top | Y = 3.40 / 3.80 |
| Sloped apron folds | (X,Y) = (0.24,3.74), (0.46,3.60), (0.50,3.58) |
| Pale head fold | X = 0.10…0.24; Y = 3.74…3.80 |
| North / south return aprons | Z = -6.12…-5.98 / 5.98…6.12 |
| Return apron envelope | X = -0.12…0.50; Y = 3.18…3.80 |
| Low-roof field / coping top | Y = 3.42 / 3.52, from the unchanged roof set |
| Toe burial below field / coping | 0.02 / 0.12 m; toe top remains above both |
| Dimensional / source-to-export tolerance | ±0.001 / ±0.00001 m |

The full new geometry is above 2.5 m. Its ground-reference anchor is intentional;
do not move the imported model down to make a ground-contact prop. Blender +Z maps
once to Godot +Y; Blender +Y to Godot -Z. No sockets: numeric connector planes are
the static assembly interface. Keep `Visuals/Model` at identity.

### Placement and height-change contract

For a high west bay with two storeys and a low east bay with one storey:

| Component | Root position | Yaw |
| --- | --- | --- |
| High lower / upper straight bays | (0,0,0) / (0,3.2,0) | 0° |
| Low straight bay | (6,0,0) | 0° |
| High / low straight roof caps | (0,3.2,0) / (6,0,0) | 0° |
| **This complete height-step prefab** | **(3.12,0,0)** | **0°** |

The prefab already includes its exposed upper wall and that wall's roof end cap.
**Do not add a second .07 or .10_end at the same location.** The high/low straight
roofs and the run's other exposed-end closures remain separate existing kit pieces.
The wall's mating plane sits at world X = 3; its 0.24 m thickness overlaps the first
0.24 m of the low roof, not the six-metre bay pitch. This is a deliberate hidden
junction, not a reason to move the low bay or create a ground-level gap.

For a high east bay at X = 0 and low west bay at X = -6, place this prefab at
**(-3.12,0,0), yaw 180°**. Use rigid rotations and nonnegative whole-storey offsets;
never mirror, scale, pitch or roll. Translate the complete local arrangement upward
by 3.2 m for a three-storey to two-storey transition, and so on. Underlying ground
still stays flat: the offset identifies the top-storey mounting datum.

**Supervisor-approved limit: one-storey local drops only.** For a larger total
height change, use successive six-metre terraces rather than stacking this capped
prefab vertically at one edge. Example: three/two/one-storey runs at X = 0/6/12 use
height-step roots (3.12,3.2,0) and (9.12,0,0), respectively. Each intermediate bay
retains its ordinary roof cap. **Abrupt multi-storey drops are unsupported.** Do not
bury this prefab's top cap inside another .07 wall or leave false projecting flashing
bands halfway up a tall drop. Corner-height transitions and adjoining elevated
walkways are not certified by this straight-run component.

The new end-return aprons are an approved seam treatment: without them, the existing
wall and low cap would expose coplanar fascia faces at Z = ±6, Y = 3.20…3.40. The
returns extend to Z = ±6.12 and below the junction to Y = 3.18, covering both that
stripe and the wall's 0.10 m ribbon ends. They are only 0.12 m beyond the structural
facade, within the host windows' existing 0.18 m decorative envelope. No sibling
mesh or collision was changed. Placement must preserve open court mouths, cross-links
and actor sightlines; the component must never bridge an open court.

## Source, export and materials

- New source: `art/source/models/environment/d03_apartment_family_11/d03_apartment_family_11.blend`.
- Collection: `export_d03_apartment_family_11`.
- Root / mesh: `D03ApartmentFamily11` / `D03ApartmentFamily11_Mesh`.
- Export: `art/models/environment/d03_apartment_family_11/d03_apartment_family_11.glb`,
  with its committed `.import` sidecar.
- Wrapper: `scenes/prefabs/environment/d03_apartment_family_11.tscn`.
- Tools: `tools/asset_production/d03_apartment_family_11/` (`author.py`, `export.py`,
  `validate.py`, `check_prefab.gd` with UID, and `record.py`).

The wrapper links `UpperWall` to `d03_apartment_family_07.tscn` and `UpperEndCap` to
`d03_apartment_family_10_end.tscn`, both translated (0,3.2,0). Those prefabs retain
their own original sources, imports, UIDs, meshes, materials and wall collider.
There are no editable-child overrides, embedded meshes, material overrides, custom
runtime scripts or duplicate wall/cap meshes in this delivery.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export consumes
`tools/assets/blender/export_settings.json`, selecting only the named collection
with animation/skin export disabled. Metre units; applied identity transforms; no
unapplied modifiers. Three closed original profile extrusions are joined into one
mesh, with flat manufactured folds and triangulated faces. Studio lights, camera,
ground and hidden one-metre reference are outside export scope. Sibling collections
are loaded and instanced for rendering only **after** source save/export; no sibling
geometry is copied into the new `.blend` or GLB.

Two opaque, back-culled, texture-free Principled materials in exported slot order:

| Slot | Material | sRGB swatch | Roughness / metallic |
| --- | --- | --- | --- |
| 0 | `terrace_bluegrey_roof` | `#526B7B` | 0.80 / 0 |
| 1 | `terrace_pale_frame` | `#C5CABF` | 0.53 / 0 |

Actual imported names, colors, roughness and metallic values match the delivered
roof set. No images, textures, rigs, clips, external material dependencies or explicit
LODs. Default Godot automatic mesh LOD generation stays enabled; visual distance
behavior and repeat-instance cost remain unprofiled.

## Evidence and measured validation

[Mounted hero](d03_apartment_family_11-evidence/hero.png) ·
[reverse side](d03_apartment_family_11-evidence/side.png) ·
[junction close-up](d03_apartment_family_11-evidence/junction_detail.png) ·
[47 m / 42° overhead](d03_apartment_family_11-evidence/overhead_47m_42deg.png).

The producer inspected all four final renders. Isolated Blender Cycles CPU, 32 samples,
AgX, 1280 × 720, PNG compression 95, no dithering; largest image approximately 413 KiB.
The hero was widened after the initial framing cropped the high roof. All final
views use unchanged source-collection instances for the hosts, end walls and caps.
The new piece is the narrow blue-grey sloped strip and its terminal aprons; the
closed wall above and its pale top cap are reused assets. The close-up shows a solid
covered junction, with no visible gap or z-fighting at the north return. Side shows
the corresponding south junction. These are asset-context renders, not district
placements or in-engine captures.

The overhead is vertical-down, north-up, 47 m above ground, with 42° **vertical FOV**
at the standing 720 px height cap. The stepped roof silhouette and quiet junction
line remain visible. The wall's fine details are not essential gameplay information.
No actor/court-route visibility acceptance is inferred from this isolated view.

[validation.json](d03_apartment_family_11-evidence/validation.json) records measured
source, actual binary GLB, seam-ray and engine observations.
[manifest.json](d03_apartment_family_11-evidence/manifest.json) hashes every produced
payload except itself; linked dependency exports are separately pinned in validation.
[Final checks](d03_apartment_family_11-evidence/final-checks.log) summarize outcomes
and distinguish tool diagnostics from actual assertion results.

- New flashing: **72 triangles; 42 source vertices; 126 exported vertices; one mesh / two surfaces.**
- Whole linked prefab: **1,540 source triangles; three meshes / eight surfaces**, including
  the unchanged 1,444-triangle wall and 24-triangle end cap; not eight unique materials.
- Zero non-manifold edges, degenerate source faces or actual GLB triangles in the new mesh.
- Finite vertices, unit source corner/exported normals, identity transforms, ground-reference
  datum, literal dimensions and all three independent solid-island bounds pass.
- Fresh re-export from the final saved source is byte-identical to the delivered GLB.
- **40 actual-GLB first-hit samples** cover both return aprons at four heights/five X
  positions, rejecting an exposed coplanar sibling surface at every sampled point.
- Five lower-roof profiles check toe burial and the real field/coping heights on both
  sides of the toe. Five wall/flashing and five upper end-cap profiles pass.
- Forty reversed-yaw return samples preserve the same seam cover. These are bounded
  geometry checks, not an exhaustive engine rasterization or city-placement test.

### Final receipts

Copied from the final validation JSON; `record.py --check` verifies them against
both the manifest and actual files:

- Source: **102518 bytes**, SHA-256
  `8d4ec805889bf7f1f5fecfdd73d6746c4de32f0d66782b8b350c72b472408f3b`.
- New GLB: **5400 bytes**, SHA-256
  `1586ea07f581022e2a81bcd7fe96968ae6aa7d1d31c8f26ebebe25a8ea4e731e`.

### Prefab, collision and engine checks

The new flashing is entirely overhead and visual-only. The **sole collider is the
unchanged linked .07 wall box**, size (0.24,3.2,12), prefab-local centre
(0,4.8,0), layer 1 / mask 0, at `UpperWall/Collision/Body/Core`. Its AABB is
(-0.12,3.2,-6)…(0.12,6.4,6). No flashing collider, walk deck, guard, navigation,
new authority state or ground blocker is introduced. The actual host bays continue
to own their closed structural volumes.

Godot **4.8.dev7.official.c971f93e7** final headless import/runtime checks exit 0 with
no ERROR/SCRIPT ERROR lines or missing dependencies. The wrapper was authored as
text because live sessions are prohibited and the windowed editor is unavailable,
then loaded, packed and saved with the pinned headless editor. **Two subsequent
byte-stable reload/save cycles** preserve node identities, prefab UID and all three
resource links. Prefab UID `uid://cj6nbqeq5gax5`; new GLB UID `uid://bo0y88ic3coir`.
No other scene or sibling metadata changed during normalization/import.

The runtime check verifies actual new/composite bounds, surface counts, sibling
ancestry/transforms, material equality, UID resolution and the inherited collider.
It also uses the actual high/low host prefabs for six capsule solid/clear queries
(radius 0.35 m, height 1.8 m), one car-sized clearance query (1.9 × 1.5 × 4.3 m), and
an upper-wall ray hitting X = 0.1200000048 m. Four **production `ActorMotion.step`**
runs, 60 ticks each, test frontage bypass and closed-front stop in AUTHORITY and
REPLAY. Both modes give identical endpoints: bypass X = 2.0 m at Z = -6.80000019;
front stop Z = -6.35026121 m. These are bounded local API queries, not production
vehicle driving or multiplayer transport/admission/prediction proof.

Tool limitations: headless editor normalization exits 0 with successful stable-save
assertions but emits the same RID/ObjectDB shutdown-leak diagnostics recorded by
earlier siblings. Final import and runtime logs are clean; no errors are suppressed.
The addon warns that this engine version is untested. Blender's `use_nodes` notices
concern Blender 6, not this pin. An initial validator used `.startswith` on a
Collection instead of its name; that assertion implementation was corrected before
the passing run. One initial 102-character GDScript line was split; final formatting
and lint pass with zero warnings. A failed scratch shell-generation command wrote
no script and was replaced by the final direct-file write. No live session was used.

## Exact reproduction

From repository root in Git Bash. Scratch logs/reexports stay outside the repository.
Never connect to the owner's live Blender or Godot session.

```sh
NID=d03_apartment_family_11
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

`validate.py` opens the saved source and calls `export.py` into scratch before a
whole-file byte comparison; it requires the runtime/normalization receipt. Manual
export: open the saved `.blend` using the same bounded CLI flags and run `export.py
-- C:/tmp/ft/assets/d03_apartment_family_11/reexport`. A fresh `author.py` run is not
promised to serialize the source identically; the strict check is re-export from
the committed source. After intentional changes, refresh validation and handoff
receipts, run the final pinned import, then regenerate the manifest with `record.py`
without `--check` last. No `production_checks.py` was run (owner decision 52).

## Remaining acceptance

- Independent art/technical review of this component, reuse and provisional interface.
- World-integrator approval of storey counts, successive terrace layouts, plot fit,
  roof/actor visibility, open court mouths and cross-links in saved placements.
- Actual in-engine visual/gameplay-camera and moving-camera junction review, contextual
  gameplay, production vehicle motion, authoritative transport and packaged dependencies.
- Repeated-placement draw-call, GPU/frame-pacing, memory and Deck LCD/OLED profiling.

No whole-city placement, full gameplay or target-device acceptance is claimed.
None of the six earlier handoffs had a stale pending production item resolved by
this delivery; their contextual height-step/roof/placement checks remain pending,
so no sibling doc or manifest edits were necessary. The registry owns family progress.
