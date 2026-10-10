# d03_apartment_family.10 — Straight/end/corner roof-cap set

10 October 2026. **Original source, four linked exports and bounded prefab checks delivered;
independent review and world acceptance pending.** Commissioned under the
[register commission](commission.md), superseding the concept-only restriction in the
[family brief](../d03_apartment_family.md). Producer: commissioned implementation worker.
Accepting art/technical reviewer: unassigned. No world, shared register, road, gameplay
or sibling asset files changed.

## Design and dimensions

Four interchangeable **flat-roof caps** finish Terrace Ward's existing apartment kit:
straight, narrow end closure, outside elbow and inside elbow. A blue-grey structural
fascia supports a quiet recessed blue-grey roof field and a continuous pale coping.
The raised edge is only 0.10 m above the field: a roof detail, not a human guardrail.
The broad flat silhouette supplies the family brief's flat-roof option; no separate
pitched variant or whole-building roof mesh is introduced. Coral stays on the shared
wall corners and warm color at the entrances, not along every roof edge.

All five earlier sibling handoffs were inspected: [straight](d03_apartment_family_05.md),
[corners](d03_apartment_family_06.md), [end closure](d03_apartment_family_07.md),
[entrance](d03_apartment_family_08.md) and [balcony](d03_apartment_family_09.md).
Original Blender construction only: no downloads, third-party geometry, textures,
brands, image-to-mesh or runtime-generated visible meshes. References inspected:
[Terrace Ward identity](../../concepts/world-v1/stage-03-district-identities/README.md#terrace-ward--a-neighbourhood-of-shared-courts),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), and
[District 03 map context](../../concepts/districts-v1/map-context.md#district-03).
The district's 4.80 ha is context, not a plot allocation or approved replacement envelope.

### Provisional interface — metres, Godot local axes

The existing **6 m bay pitch, 12 m structural depth, 3.2 m storey pitch and 0.24 m
end-wall thickness** are unchanged. Cap thickness and coping width are provisional
authored choices permitted by the standing production brief, not image measurements.

| Interface | Value |
| --- | --- |
| Root / mesh pivot | (0, 0, 0), ground-reference anchor of the corresponding top-storey host |
| Roof underside | Y = 3.20, already elevated in source/export geometry |
| Structural fascia / slab | Y = 3.20…3.40, thickness 0.20 m |
| Recessed roof field | Y = 3.40…3.42, top at 3.42 m |
| Pale coping | Y = 3.40…3.52; 0.24 m wide inside exposed edges |
| Whole visual height | 0.32 m; minimum underside 3.20 m > 2.50 m |
| Eave projection | Zero beyond the host structural footprint |
| Straight bounds | Min (-3, 3.2, -6); max (3, 3.52, 6) |
| End bounds | Min (-0.12, 3.2, -6); max (0.12, 3.52, 6) |
| Outside bounds | Min (-6, 3.2, -6); max (6, 3.52, 6) |
| Inside bounds | Min (-9, 3.2, -9); max (9, 3.52, 9), with the 6 × 6 m southeast notch retained |
| Dimensional / source-to-export tolerance | ±0.001 / ±0.00001 m |

The inside footprint is (-9,-9), (9,-9), (9,3), (3,3), (3,9), (-9,9) in X/Z;
there is **no roof across its court notch**. Each cap exactly covers its host's core.
Existing shallow wall trim may project beyond the roof fascia; it does not require
an eave overhang. Square connector edges intentionally avoid bevel cracks or overlapping
coplanar eaves. Closed component mating faces are retained for manifold topology.

- **Straight:** open X connectors at ±3; pale coping only at Z = -6…-5.76 and
  +5.76…+6. The field continues through the X connectors without a transverse bar.
- **End:** the entire 0.24 m-wide top is coping, so it closes the straight roof's
  open end. It is an added terminal strip, not a replacement 6 m bay. No unused
  roof-field material is exported on this variant.
- **Outside:** north/west L-shaped coping follows X/Z = -6. A 0.24 × 0.24 m pale
  square at X/Z = 5.76…6 completes the court-side coping turn when both outgoing
  straight runs are attached. It is not a floating roof fixture.
- **Inside:** north/west coping follows X/Z = -9; the court-side L lies inside the
  X/Z = 3 wall planes, extending to 2.76. Both open connectors match straight profiles.

Blender +Z maps once to Godot +Y, Blender +Y to Godot -Z. No sockets: the numeric
mating planes are the static assembly interface. There are no interiors, roof access,
climbing, walkable decks, roof guards, working drains, equipment, destruction or state.

### Placement contract

Place each roof wrapper at the **same transform as its top-storey host**, not at
that host's top plane. The geometry already contains the 3.2 m vertical offset.
For a building with N storeys at ground Y = 0, set roof-root Y = 3.2 × (N − 1).
For example, a three-storey host uses roof root Y = 6.4 and underside Y = 9.6.
Keep `Visuals/Model` at identity; use only rigid yaw and nonnegative storey offsets.
Do not lower these caps to make ground platforms or place reachable elevated routes
beside them. Host walls continue to own all building collision.

Relative to a top-storey host at the origin:

| Placement | Roof-root position | Godot +Y yaw |
| --- | --- | --- |
| Straight or entrance roof | (0, 0, 0), straight variant | 0° |
| Outside / inside roof | (0, 0, 0), matching corner variant | 0° |
| Adjacent straight roof | (6, 0, 0) | 0° |
| Straight east / west end closure roof | (3.12, 0, 0) / (-3.12, 0, 0), end variant | 0° / 180° |
| Outside outgoing east / south straight | (9, 0, 0) / (0, 0, 9) | 0° / 90° |
| Inside outgoing east / south straight | (12, 0, -3) / (-3, 0, 12) | 0° / 90° |
| Outside unused east / south connector end | (6.12, 0, 0) / (0, 0, 6.12) | 0° / -90° |
| Inside unused east / south connector end | (9.12, 0, -3) / (-3, 0, 9.12) | 0° / -90° |

End caps require the corresponding actual end wall; never float them beyond an
unclosed host. One straight roof with two ends spans X = -3.24…3.24, matching the
6.48 m closed structural run. Do not insert end caps between connected bays. Corners
are rotatable modules, not mirrored/scaled windows. Connectors and roofs may only
cover existing solid hosts; they must not bridge open court mouths or cross-links.
Height changes require their own wall/junction composition; these caps do not hide
an exposed upper wall or independently resolve stepped-building placement.

## Source, exports and materials

- Source: `art/source/models/environment/d03_apartment_family_10/d03_apartment_family_10.blend`.
- Four collections: `export_d03_apartment_family_10_<variant>` where variant is
  `straight`, `end`, `outside` or `inside`.
- Roots / meshes: `D03ApartmentFamily10Straight`, `D03ApartmentFamily10End`,
  `D03ApartmentFamily10Outside`, `D03ApartmentFamily10Inside`; mesh names append `_Mesh`.
- Four exports: `art/models/environment/d03_apartment_family_10/d03_apartment_family_10_<variant>.glb`,
  each with committed `.import` metadata.
- Four wrappers: `scenes/prefabs/environment/d03_apartment_family_10_<variant>.tscn`.
- Tools: `tools/asset_production/d03_apartment_family_10/` (`author.py`, `export.py`,
  `validate.py`, `check_prefab.gd` with UID, and `record.py`).

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export consumes
`tools/assets/blender/export_settings.json`, selecting each explicit collection,
with animation/skin export disabled. Metres, applied transforms, identity roots and
meshes; no corrective scale. Closed planar extrusions are joined into one mesh per
variant; no unapplied modifiers. Studio camera, lights, ground and hidden one-metre
reference are excluded. Sibling render context is loaded only after source save and
export, so no sibling geometry is copied into the delivered source or GLBs.

Opaque, back-culled, texture-free Principled materials, in exported slot order:

| Slot | Material | sRGB swatch | Roughness / metallic |
| --- | --- | --- | --- |
| 0 | `terrace_bluegrey_render` | `#829398` | 0.76 / 0 |
| 1 | `terrace_pale_frame` | `#C5CABF` | 0.53 / 0 |
| 2, except end | `terrace_bluegrey_roof` | `#526B7B` | 0.80 / 0 |

The engine compares the first two materials to the actual delivered straight-bay
import and checks the roof swatch. No textures, embedded images, external materials,
rigs, clips, inherited variants, editable children or explicit LODs. Default automatic
Godot LOD generation remains enabled. Low source counts are not performance acceptance.

## Evidence and measured validation

[Mounted hero](d03_apartment_family_10-evidence/hero.png) ·
[reverse / mating sides](d03_apartment_family_10-evidence/side.png) ·
[end-coping detail](d03_apartment_family_10-evidence/roof_detail.png) ·
[47 m / 42° overhead](d03_apartment_family_10-evidence/overhead_47m_42deg.png).

All four final renders were inspected by the producer. Isolated Blender Cycles CPU,
32 samples, AgX, 1280 × 720, PNG compression 95, no dithering. Largest image is about
408 KiB. They show a straight bay with both end closures and two separate corners,
using unchanged source-linked sibling geometry as render-only mounting context.
The unclosed corner sides deliberately expose mating planes; these are component
samples, not completed apartment-group assemblies. Detail shows the continuous
terminal coping, not a roof equipment fixture.

The overhead is vertical-down, north-up, 47 m above ground, 42° **vertical FOV**, at
the standing 720 px evidence-height cap. Quiet blue-grey fields remain broad and the
pale rim differentiates the open connectors from closed perimeter edges. The inside
notch is visibly unroofed. These are not Godot captures, district placement, actor
visibility or proof that court mouths and cross-links remain clear in the city.

[validation.json](d03_apartment_family_10-evidence/validation.json) records source,
actual binary GLB and engine results. [manifest.json](d03_apartment_family_10-evidence/manifest.json)
hashes every delivered payload except itself. [Final checks](d03_apartment_family_10-evidence/final-checks.log)
distinguish successful assertions from tool diagnostics.

| Measurement | Straight | End | Outside | Inside |
| --- | --- | --- | --- | --- |
| Triangles | 48 | 24 | 64 | 80 |
| Source vertices | 32 | 16 | 40 | 48 |
| Exported vertices | 96 | 48 | 120 | 144 |
| Meshes / surfaces | 1 / 3 | 1 / 2 | 1 / 3 | 1 / 3 |
| Slab footprint / top coverage m² | 72 | 2.88 | 144 | 288 |
| Slab volume m³ | 14.4 | 0.576 | 28.8 | 57.6 |
| Non-manifold edges | 0 | 0 | 0 | 0 |
| Degenerate source faces / GLB triangles | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Fresh saved-source re-export | Byte-identical | Byte-identical | Byte-identical | Byte-identical |

Unit source corner/exported normals, finite source vertices, identities, dimensions,
actual binary-accessor bounds, literal slab corners, core volume and top coverage pass.
The closed roof-field/coping solids partition the upper surface; shared vertical/bottom
mating faces are intentional and hidden, not holes. Source triangle centroids reject
any fill across the inside court notch.

Binary-GLB triangle ray tests independently check **four five-point corner connector
profiles** (east and south connectors of both corners, compared to the straight cap),
plus three straight-repeat and three end-coping sample positions. Coping samples read 3.52 m and field samples 3.42 m within 0.00001 m.
The end strip deliberately raises the centre profile by 0.10 m to close the field.

### Final receipts

Copied from the final validation JSON; `record.py --check` checks them against the
manifest and actual payloads:

- Source: **106813 bytes**, SHA-256
  `b77104997ec797bd92db06c6809a8157ca92ff9f9949dc7c879add4a20b9dc16`.
- Straight GLB: **4956 bytes**, SHA-256
  `14fe74d3ecc526f9340d9002a3f4c3eda4017ab4b6a5fd23cd08b3dd69b10989`.
- End GLB: **2984 bytes**, SHA-256
  `d1937b9acc1ef65826dd36467700350904af89ef2b6763ae810ee51f44e74af1`.
- Outside GLB: **5828 bytes**, SHA-256
  `bab39ed0174193b2eb1d7d13959f4331c9320da57cae6c09d3e01c38e457ccad`.
- Inside GLB: **6252 bytes**, SHA-256
  `4f905df6c994489cc08fbb980f43896644a856a75a192bcbff46d2d996929508`.

### Prefab, collision and engine checks

These are **inaccessible overhead roof elements**, entirely above 2.5 m, so the
standing collision rule makes them visual-only. There are no PhysicsBody3D,
CollisionShape3D, navigation, gameplay scripts or new authoritative state. The host
continues to own its closed core. The cap has no overhang and creates no new ground
obstacle. No movement/network tests are claimed for this visual-only change.

Godot **4.8.dev7.official.c971f93e7** final headless import and runtime load check exit
0 without ERROR/SCRIPT ERROR lines or missing dependencies. Wrappers were authored
as text because live editor sessions are prohibited and the windowed editor is
unavailable, then loaded, packed and saved with the pinned headless editor. Each
wrapper passes **two subsequent byte-stable reload/save cycles**, preserving saved
UIDs, identities and linkage. `Visuals/Model` is an identity-transform GLB instance;
no mesh data or material override is copied into the scenes.

All four actual imported bounds and surface counts match. Actual sibling structural
collider bounds confirm the cap underside seats at the host top with equal X/Z
extents. Both material palette checks and prefab/GLB UID resolution pass. These are
resource/geometry checks, not in-engine visual or whole-building acceptance.

Tool limitations: editor-mode normalization exits 0 with successful stable-save
assertions but emits the same headless editor shutdown RID/ObjectDB leak diagnostics
observed in earlier sibling handoffs. Final import/runtime logs are clean; no errors
are hidden or suppressed. The addon warns that the engine version is untested.
Blender `use_nodes` deprecation notices concern Blender 6, not the required pin.
An initial lint pass found one overlong receipt-read line; splitting it resolved the
warning. Final formatting and lint pass with zero warnings. No live session was used.

## Exact reproduction

From repository root in Git Bash. Scratch exports and raw logs stay outside the
repository. Never connect to an owner's live Blender or Godot session.

```sh
NID=d03_apartment_family_10
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

`validate.py` loads the saved source and runs `export.py` into scratch before comparing
all four entire GLBs byte-for-byte; it requires the runtime/normalization receipt.
Manual export: open the saved `.blend` using the same bounded Blender invocation,
then run `export.py -- C:/tmp/ft/assets/d03_apartment_family_10/reexport`. A fresh
`author.py` run is not promised to serialize the source identically; re-export from
the committed source is the strict comparison. After intentional revisions, refresh
validation/handoff receipts, run the final pinned import, then run `record.py`
without `--check` last. No `production_checks.py` was run (owner decision 52).

## Remaining acceptance

- Independent art/technical review of the four caps and provisional interfaces.
- World-integrator approval of actual run lengths, storey/height-step compositions,
  roof visibility, plot fit, open court mouths, cross-links and actor sightlines.
- Actual in-engine visual/gameplay-camera review, contextual production gameplay,
  authoritative transport behavior and packaged dependency checks.
- Repeated-placement draw-call, GPU/frame-pacing, memory and Deck LCD/OLED profiling.

No whole-city placement, target-device or full gameplay acceptance is claimed. The
registry tracks other family records. None of the five earlier handoffs had a stale
pending production item resolved by this delivery; their contextual roof/placement
checks remain valid pending work, so no sibling doc/manifest edits were necessary.
