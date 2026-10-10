# d05_harbour_hall.02 — Entry canopy

10 October 2026. **Source/export and linked prefabs delivered; bounded checks pass.
Independent review and world-placement acceptance pending.** Produced by the isolated
asset-production worker on `lane/a-hhall` under the current asset-common brief and
[production commission](commission.md). Parent/reviewer owns acceptance.
Family: [Harbour hall](../d05_harbour_hall.md); completed sibling:
[hall exterior](d05_harbour_hall_01.md). No sibling or shared tracker files changed.

## Design and dimensions

Original Blender construction: a shallow cantilevered teal hood with clipped front
corners, a warm rolled-edge tray, dark inset soffit and three broad underside ribs.
The slight frontward roof fall and narrow wall contact rail read as ordinary civic
architecture, not a luminous commercial fascia. No posts, hanging rods, added steps,
interiors, sign carrier/artwork, runtime lights or interaction systems are included.
The hall owns its steps and closed entrance; the square remains separate open space.

References inspected: accepted Petrol & Coral direction, Stage 3 Old Quay identity,
Stage 4 streets, Old Quay v03/breakdown, and the completed .01 source/handoff/render.
No downloaded geometry, textures, real brands, external fonts or image-to-mesh process.

**All dimensions are provisional production choices**, following the standing dimension
rule and the sibling's explicit mounting contract. Envelope tolerance: ±0.001 m.

| Element | Dimensions / Godot coordinates in metres |
| --- | --- |
| Local visual AABB | min **(-4, -0.05, -2.4)**, max **(4, 0.4, 0)** |
| Whole component size | **8.0 X × 0.45 Y × 2.4 Z** |
| Wall contact rail | 7.8 wide × 0.45 high × 0.12 deep; back at Z=0 |
| Warm tray | 8.0 wide × 2.4 deep; front corners clipped by 0.32 |
| Teal hood | 7.92 wide × 2.34 deep; roof top falls from local Y=0.39 to 0.24 |
| Mount relative to hall at identity | **(0, 3.85, -9)**, identity rotation and scale |
| Mounted visual AABB | min **(-4, 3.8, -11.4)**, max **(4, 4.25, -9)** |
| Lintel clearance | Lowest canopy Y=3.8 minus sibling lintel top 3.74 = **0.06** |
| Landing clearance | Lowest canopy Y=3.8 minus sibling landing top 0.30 = **3.50** |
| Forward extent | 2.4 from wall; 1.6 beyond hall eave; 0.6 beyond lowest step |

The root and mesh origin are (0,0,0), a **wall-contact mounting datum**, not a ground
pivot. This attachment convention follows the sibling's .02 handoff and accepted
wall-fitting prefabs. Back contact is local Z=0; the hood projects toward local -Z.
Blender +Y maps to Godot -Z, Blender +Z to Godot +Y. Metre units, zero translation
and rotation, applied unit scale at both exported objects. No exported socket was
requested; the saved preview records the mounting transform, not runtime placement code.

## Source, export and materials

- Source: `art/source/models/environment/d05_harbour_hall_02/d05_harbour_hall_02.blend`.
- Named export collection: `export_d05_harbour_hall_02`.
- Root: `D05HarbourHall02`; child: `D05HarbourHall02_Mesh`.
- Export: `art/models/environment/d05_harbour_hall_02/d05_harbour_hall_02.glb`.
- Tools: `tools/asset_production/d05_harbour_hall_02/author.py`, `validate.py`,
  `export.py`, `check_prefab.gd`, `record.py`.

One joined mesh preserves closed disconnected construction pieces. Bevels are applied,
coincident bevel vertices welded, degenerate edges dissolved and normals recalculated
before weighted normals. The studio floor/camera/lights are excluded by collection
export. The sibling source is read only **after** the canopy source is saved/exported
for two mounted evidence renders; no sibling geometry is stored in this .blend or GLB.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. The exporter
loads the shared `tools/assets/blender/export_settings.json`, selects only the named
collection, disables animations/skins and preserves the project's Y-up conversion.
Fresh export from the saved source is byte-identical to the committed GLB.

Three opaque, back-culled Principled material surfaces, in exported order:

1. `harbour_hall_teal_metal`: linear RGB (0.035, 0.15, 0.15), metallic 0.35,
   roughness 0.42; exact sibling teal values.
2. `harbour_hall_limestone_trim`: (0.78, 0.70, 0.53), metallic 0, roughness 0.56;
   exact sibling warm trim values.
3. `harbour_hall_canopy_soffit`: (0.022, 0.065, 0.09), metallic 0.2, roughness 0.48;
   a quieter rough underside using the sibling's dark glazing color.

No textures, embedded images, emission, material overrides, rig, clips or LOD variants.
Standard Godot automatic LOD/shadow mesh/compression import settings remain intact;
actual LOD/device performance is pending, not an approved budget.

## Linked prefabs and collision

`scenes/prefabs/environment/d05_harbour_hall_02.tscn` instances the GLB at
`Visuals/Model`, identity transform, without embedded mesh resources or editable children.
Its UID is `uid://b2fihoe3wget1`; model UID is `uid://cvksxy51ix22c`.

`scenes/prefabs/environment/d05_harbour_hall_02_hall_preview.tscn` is a **mounting
reference**, not a district placement. It contains only linked .01 hall and .02 canopy
prefabs: hall at identity; canopy at (0,3.85,-9). UID `uid://npy2sm1wl6m7`.
The sibling remains byte-unchanged. Both scenes were loaded, packed, saved, reloaded
and resaved headlessly; the second save preserves exact bytes and generated identities.
Godot stores scene UIDs in their headers, not separate `.tscn.uid` files. The script's
engine-generated `.gd.uid` and GLB `.import` sidecar are committed.

**Visual-only overhead component:** every mounted vertex is above 3.8 m, exceeding the
standing 2.5 m rule. No ground supports, walkable roof or new collider is appropriate.
The reference composition retains exactly the hall's three existing collision shapes
under its one static-world body (layer 1 / mask 0). Decoration does not inflate them.
The mounting checker measures the actual imported AABB, queries two radius 0.35 m /
height 1.8 m capsules under the canopy, and verifies the existing closed-wall ray still
hits Z=-9.2. It does not introduce or certify door traversal, car routes or combat aims.

## Evidence and validation

[Hero](d05_harbour_hall_02-evidence/hero.png) ·
[Side/soffit](d05_harbour_hall_02-evidence/side.png) ·
[Mounted detail](d05_harbour_hall_02-evidence/mount_detail.png) ·
[Mounted gameplay overhead](d05_harbour_hall_02-evidence/overhead_47m_42deg.png).

All four were visually inspected. Isolated Blender Cycles CPU, 32 samples, AgX,
RGB8 PNG compression 95, no dithering. Hero/side/overhead are 1280×720; the detail is
1152×648 to keep it below 400 KiB. Every render is below 400 KiB. The side's studio
floor horizon was removed; no image editing or postprocessing was used.
The detail shows clear central mounting above the closed entry and no posts obstructing
steps. The **47 m height / 42° vertical-FOV**, vertical-down perspective view shows a
restrained teal entrance tab beyond the hall's broad roof. It is not a Godot screenshot,
a whole-square orientation proof or actor-visibility acceptance. The roof hides most
of the rear canopy at this camera, intentionally leaving the front outline as the cue.

Lean retained evidence: [validation.json](d05_harbour_hall_02-evidence/validation.json),
[manifest.json](d05_harbour_hall_02-evidence/manifest.json), and
[final.log](d05_harbour_hall_02-evidence/final.log). Raw tool logs and intermediate
receipts remain outside the checkout under `C:/tmp/ft/assets/d05_harbour_hall_02/`.
The manifest hashes every produced file except itself; no scratch or backup files ship.

- **792 source vertices; 1,556 triangles; 871 exported vertices including splits.**
- **1 mesh / 3 surfaces; zero degenerate source faces/exported triangles;
  zero non-manifold source edges.** Maximum normal-length error below 0.000001.
- Source/GLB/engine bounds match the independent literal expectations within 0.001 m.
- GLB **40,368 bytes**, saved-source fresh re-export byte-identical.
- Both scenes pass save/reload byte stability; all four linked scene/model UIDs resolve.
- Two fresh pinned runtime processes return identical mounting/physics receipts,
  no ERROR/WARNING diagnostics. Both capsule queries pass; front ray Z=-9.1999998 m.
- Canonical production checks **PASS**: all **209** discovered GDScripts compile;
  lint/format pass; **17 Python tests; 149 GUT tests / 6,768 assertions**.
  Intentional negative-control failure detected. No known-failure exemptions used.

Initial relative Blender script invocation resolved to `tools/` and exited 1; using
an absolute script path fixed it. One gdstyle local-variable warning was fixed by a
named UID helper. Normalization exited 0 and saved stable scenes, but the pinned
headless editor emitted RID/ObjectDB shutdown leaks (retained in final.log). Final
worktree import exited 0 with only the existing MCP 4.8 compatibility warning. These
are not clean-editor-log claims; fresh runtime checks are diagnostic-free. No owner
live editor/MCP session was used, synchronized, saved or changed.

## Exact reproduction

From this worktree root in Git Bash (all tools bounded; sources never use the live editor):

```sh
NID=d05_harbour_hall_02
P="$(pwd -W)"
B="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$P/tools/asset_production/$NID/author.py" > "$T/author-final.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$P/tools/asset_production/$NID/validate.py" > "$T/validate-final.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$T/import-final.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize \
  > "$T/prefab-normalize-final.log" 2>&1
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-fresh-final.json" > "$T/prefab-fresh-final.log" 2>&1
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-second-process.json" > "$T/prefab-second-process.log" 2>&1
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd"
timeout 60 "$(mise which gdstyle)" fmt --check "tools/asset_production/$NID/check_prefab.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks"
python "tools/asset_production/$NID/record.py"
```

`validate.py` opens the saved source, checks source and actual GLB accessors, re-exports
to the external `reexport/` scratch directory and compares bytes. `export.py` can also
run independently with the saved .blend loaded; an optional directory after `--`
redirects output. `record.py` requires the final receipts, verifies second-process
agreement and records file hashes. There is no general shared asset authoring/geometry
validator library here; this asset follows the existing family scripts and shared
export settings rather than adding a new abstraction or changing shared tooling.

## Remaining acceptance

1. Independent art/technical review of this exact candidate.
2. Actual district placement with hall and open square; gameplay camera/aim checks,
   especially actors directly under the canopy and edge-of-camera roof occlusion.
3. Populated-world movement/vehicle routes, multiplayer transport/admission/prediction,
   packaged build, Godot lighting/LOD and sustained GPU/Deck performance.
4. Separate civic graphics/support production; no duplicated carrier or placeholder copy.
5. Pinned headless-editor shutdown leaks remain an integration/tooling limitation.

No shared brief, queue/progress/TODO, world scene, road data, gameplay rule or sibling
asset was changed. This is bounded source/export/prefab delivery, not full-world or
target-device readiness.
