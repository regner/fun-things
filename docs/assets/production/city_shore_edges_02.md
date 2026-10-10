# city_shore_edges.02 — Quay edge

10 October 2026. **Source/export, linked prefab and bounded physics checks delivered;
independent review and world/gameplay acceptance pending.** Original Blender construction
by the commissioned implementation specialist. References: [commission](commission.md),
[shore-edge family brief](../city_shore_edges.md), [low seawall sibling](city_shore_edges_01.md),
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street context](../../concepts/world-v1/stage-04-streets/README.md). The explicit
production task supersedes the historical concept-only restriction. No downloaded meshes,
image-to-mesh, real brands, external artwork or textures were used.

## Design and provisional dimensions

A heavy straight retaining component for Old Quay and East Docks: deep, broad slate
face, dark toe, narrow recessed mortar bed and thick pale chamfered coping with one
shallow centre joint. The shared four-material mineral palette and 4 m repeat match
`.01`; the wider coping and deep face distinguish the working quay without extra
furniture, warning stripes, noisy masonry or grime. District differences come from
placement and separately owned furnishings, not incompatible geometry variants.

Dimensions are **provisional authored values**, allowed by the production standing
rules, not measurements inferred from concepts or approval of coastline fit.
**The land datum is the coping TOP at Y=0, not the bottom of the retaining face.**
Place the body below existing land, never lift terrain 2.4 m to accommodate it.
The studio display floor in the evidence is below the toe, not proposed land or water.

| Contract | Godot local metres |
| --- | --- |
| Root/pivot | (0, 0, 0), centre of coping at the land-surface datum |
| Whole AABB | min (-2, -2.4, -.6), max (2, 0, .6) |
| Whole X/Y/Z size | 4.000 × 2.400 × 1.200 |
| Toe/body/bed/coping levels | -2.4–-2.1 / -2.1–-.31 / -.31–-.28 / -.28–0 |
| Coping | 1.200 wide, .280 deep; top edge chamfers .035 |
| Coping centre joint | X=0; .020 wide, .010 deep, closed profiled groove |
| End joins | X=-2 and X=+2, identical square planar sections |
| Repeated straight | Translate 4.000 along X, no scale or corrective rotation |
| Intended water-facing side | -Z (Blender +Y); symmetric section |
| Landward coping boundary | Z=+.600, surface Y=0 |
| Single static collider | 4 × 2.4 × 1.2 box centred (0, -1.2, 0) |

Envelope/datum tolerance is ±.001 m. Blender +Z maps to Godot +Y, Blender +Y
maps to Godot -Z. Root and mesh have identity transforms, metre units and applied
geometry. There are no sockets, imported collision suffixes or runtime attachment APIs.

### Family and placement interface

Only the straight quay is delivered here. `.04` owns corners, ends and transitions;
`.03` owns rocks; quay furniture owns rails, mooring bollards and ladders; boardwalk
and marina owners retain their decks/supports/connectors. No substitute geometry for
those assets, shoreline redesign, terrain change, tide level or water-entry mechanic
is introduced. This flush retaining face is **not an above-ground guardrail**.

The common 4 m length and X end planes allow aligned municipal and working layouts.
Unlike the low seawall's Y=0–1 barrier, this component supplies the below-datum face.
The seawall's .64 m ground footprint would fit on this 1.2 m coping at matching roots;
stacking is a dimensional placement option, **not a delivered or playtested assembly**.
Do not directly butt the different-height profiles as though their sections matched.
World integration and `.04` must resolve mixed-edge transitions, exposed terminations
and coast bends without gaps or altering saved coast/harbour polygons.

For `.04`, the ordered Blender (Y,Z) end profiles are below; negate Y for Godot Z.
They are recorded parametrically in `author.py`, and validation proves identical
end vertex sets at X=±2. No longitudinal end bevel creates daylight at butt joins.

- Toe: `(-.55,-2.4), (-.55,-2.14), (-.51,-2.1), (.51,-2.1), (.55,-2.14), (.55,-2.4)`.
- Body: `(-.51,-2.1), (-.50,-.34), (-.48,-.31), (.48,-.31), (.50,-.34), (.51,-2.1)`.
- Bed: `(-.51,-.31), (-.51,-.28), (.51,-.28), (.51,-.31)`.
- Coping: `(-.56,-.28), (-.60,-.24), (-.60,-.035), (-.565,0), (.565,0),
  (.60,-.035), (.60,-.24), (.56,-.28)`.

Collinear pieces share planar end faces. Arbitrary rotations are not a solution for
curved polygons. Preserve the land-surface datum; final face exposure/submergence and
where guards are needed remain placement decisions. No part of the city was placed.

## Source, export and materials

- Source: `art/source/models/environment/city_shore_edges_02/city_shore_edges_02.blend`.
- Collection: `export_city_shore_edges_02`; root `CityShoreEdges02`, child
  `CityShoreEdges02_Mesh`. Four closed solid component islands joined into one mesh.
- Explicit linked export: `art/models/environment/city_shore_edges_02/city_shore_edges_02.glb`
  and retained `.glb.import` settings/identity.
- Prefab: `scenes/prefabs/environment/city_shore_edges_02.tscn`.
- Author/export/validate/render/check/manifest recipes:
  `tools/asset_production/city_shore_edges_02/`.

Four opaque back-face-culled Principled surfaces, identical to `.01`, metallic 0,
no emission or image dependencies:

| Slot | Material | Linear RGB | Roughness |
| --- | --- | --- | --- |
| 0 | `shore_body_slate` | .20, .265, .29 | .72 |
| 1 | `shore_foot_dark_slate` | .095, .145, .16 | .78 |
| 2 | `shore_joint_recess` | .045, .075, .085 | .82 |
| 3 | `shore_coping_pale_slate` | .46, .52, .53 | .62 |

No textures, embedded images, material overrides, rigs, clips, destruction, interiors,
water simulation or lights. Broad flat mineral panels with narrow chamfer facets are
intentional. Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**.
Export uses `tools/assets/blender/export_settings.json`, the named collection only,
Y-up, no skins/animations. Studio objects are neither saved in the source nor exported.
Godot default auto-LOD and shadow mesh generation are retained; transitions and repeat
placement cost are not measured. No shared generic mesh-authoring helper exists;
local recipes follow the sibling conventions while reusing shared export/check tooling.

## Prefab, collision and engine checks

`Visuals/Model` is the identity-transform imported GLB instance, not copied geometry.
Separate `Collision/Body/Quay` supplies one world-layer-1/mask-0 static box. Its top
is Y=0, providing continuous walking across coping grooves and end joins; the lower
volume blocks the retaining face. Ignoring small side bevels and the bed recess gives
at most .12 m conservative side padding. No hidden above-cap barrier is added.
Adjacent land colliders must terminate at the coping boundary rather than overlap it.

Pinned Godot **4.8.dev7.official.c971f93e7** imported the GLB and loaded/packed/saved/
reloaded the wrapper and owned fixture twice, with byte-stable scene UIDs/node identities.
Every linked dependency and serialized UID resolves. Imported bounds, four materials,
identity model ancestry and the single-box envelope pass explicit checks.
Text-authored scenes plus isolated headless normalization are the prescribed fallback;
no live Blender/Godot session was accessed, and separate open-editor synchronization
is not claimed. There is no runtime hierarchy builder in this prefab.

The saved `physics_check.tscn` contains two real wrappers at X=0 and X=4, test-only
lower/land collision floors and production `ActorMotion` with radius .35 m, height 1.8 m.
No visible test geometry is generated. `check.gd` exercises:

- **16 rays**: lower-face and clear above-cap rays on either side of the join and
  exactly at X=2; downward rays confirm uninterrupted Y=0 coping collision.
- **12 movement cases** in AUTHORITY/REPLAY: lower-face stop, clear end bypass,
  joined-face stop, forward/reverse coping traversal over the seam, and flush
  land-to-coping traversal. Standard cases run 60 ticks, land-to-cap runs 24 ticks.
- Face stop Z=-.950520396; seam stop Z=-.949218333; clear bypass Z=2.999999762.
  Cap traversals reach X=3.999817848 / -.999817789 with feet within .001 m of Y=0.
  Land-to-cap ends at (0, .001, approximately 0).
- Authority/replay positions agree within **.001 m**, maximum measured difference
  **.000846863 m** in lower-floor settling. Bitwise mode equality is not claimed.
- A second standalone process reproduces the same recorded results.

Lower-floor contacts test the solid face, not a proposed underwater walking route.
These are bounded public movement/query checks, **not vehicle driving, network transport,
admission/prediction or world-route acceptance**.

## Evidence and validation

[Hero](city_shore_edges_02-evidence/hero.png) · [Side](city_shore_edges_02-evidence/side.png) ·
[Coping detail](city_shore_edges_02-evidence/detail.png) ·
[47 m / 42° overhead](city_shore_edges_02-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles/AgX **1280×720** renders, not engine captures.
Overhead is vertical-down perspective, 47 m above the land/coping datum, vertical
FOV 42°, Blender +Y at image top. The later 720-high production limit supersedes
the older 800-high reference. All views were inspected; hero framing was widened
to retain the full toe and cap. The broad pale cap reads clearly overhead while
its fine joint is subordinate, consistent with the low seawall's quiet boundary.
PNG compression 95 followed by RGB seven-significant-bit encoding/compression 9
keeps each final image below 400 KiB without limited-palette bands.

[validation.json](city_shore_edges_02-evidence/validation.json) records:

- **128 triangles, 72 source vertices, 234 exported split vertices**.
- **One mesh, four surfaces**; zero degenerate source faces/export triangles,
  zero non-manifold source edges, consistent winding and unit-length normals.
- Binary GLB positions/indices/normals checked, not just accessor metadata.
- 4 × 2.4 × 1.2 m bounds, identity land-datum pivot and identical square end profiles.
- Separate fresh export byte-identical to the **9,480-byte GLB**.
- Owned GDScript style/format and explicit individual compilation pass without diagnostics.
- Canonical production command **exited 1**: its global **120 s compilation deadline**
  expired, leaving 72 of 164 scripts (including this asset's check) deadline-limited.
  All failed compile logs contain the deadline marker and no script/error/warning diagnostic.
  This is not relabelled a canonical pass or ignored as a known fixture failure.
- Repository formatting/style passed for 164 scripts; **14 Python tests** and
  **137/137 GUT tests / 6,523 assertions** passed, as did pin/import and negative control.
- All **72 deadline-limited scripts subsequently compiled individually**, each with a
  separate 180 s bound, exit 0 and no diagnostics. Per-script source hashes and results
  are retained separately from the failed canonical result; shared tooling was not changed.

[manifest.json](city_shore_edges_02-evidence/manifest.json) contains SHA-256 and byte
counts for every delivered payload except itself. [final.log](city_shore_edges_02-evidence/final.log)
is the one concise retained command/diagnostic receipt. Raw logs/retries/scratch
exports remain under `C:/tmp/ft/assets/city_shore_edges_02/`.

Diagnostics: pinned Blender emits `Material.use_nodes` deprecation notices; operations
exit normally. Headless editor normalization emits known shutdown RID/ObjectDB leaks
and the addon version warning after successful scene checks. Standalone checks have
no script/error/warning diagnostics. Initial owned style length/spacing findings were
fixed by splitting the ray/outcome checks into named helpers. An initial native-Python
follow-up launcher resolved Windows TIMEOUT instead of GNU timeout and ran no engine;
the corrected invocation uses the explicit Git GNU timeout executable.

## Reproduction

From repository root in Bash; use isolated pins, never live sessions. Pillow is needed
for render recompression. Fresh production-check output directories avoid stale evidence.

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_shore_edges_02
S=C:/tmp/ft/assets/city_shore_edges_02
mkdir -p "$S"
for step in author export render; do
  timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
    --python-exit-code 1 --python "$T/$step.py" || exit $?
done
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/export.py" -- "$S/reexport.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/validate.py" -- "$S/reexport.glb"
timeout 300 "$G" --headless --editor --path . --import
timeout 180 "$G" --headless --editor --path . --script "$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "$T/check.gd"
timeout 180 "$G" --headless --path . --script "$T/check.gd"
timeout 60 "$(mise which gdstyle)" --max-warnings 0 "$T/check.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$S/checks-reproduction"
```

If the canonical compilation deadline expires, the exact follow-up below records
individual checks in a separate report. It does not overwrite the canonical result.
The explicit GNU timeout path avoids Windows' unrelated TIMEOUT command.

```sh
export G
export FT_TIMEOUT="$(cygpath -w "$(command -v timeout)")"
python - <<'PY'
import hashlib, json, os, re, subprocess
from pathlib import Path
root = Path('C:/tmp/ft/assets/city_shore_edges_02')
checks = root / 'checks-reproduction/script-checks'
results = []
for index, row in enumerate(json.loads((checks / 'compilation.json').read_text())):
    if row['ok']:
        continue
    original = (checks / f'compile-{index}.log').read_text()
    assert 'CHECK DEADLINE EXCEEDED' in original
    assert not re.search(r'(SCRIPT ERROR:|ERROR:|WARNING:)', original)
    command = [os.environ['FT_TIMEOUT'], '180', os.environ['G'], '--headless',
               '--path', str(checks / 'compiler-project'), '--check-only',
               '--script', 'res://' + row['script']]
    run = subprocess.run(command, capture_output=True, text=True)
    text = run.stdout + run.stderr
    (root / f'followup-{index}.log').write_text(text)
    ok = run.returncode == 0 and not re.search(r'(SCRIPT ERROR:|ERROR:|WARNING:)', text)
    results.append(dict(script=row['script'], ok=bool(ok), returncode=run.returncode,
                        sha256=hashlib.sha256(Path(row['script']).read_bytes()).hexdigest()))
    assert ok, text
(root / 'compilation-followup.json').write_text(json.dumps(results, indent=2) + '\n')
PY
python "$T/manifest.py" "$S/checks-reproduction"
```

## Remaining acceptance

Independent art/technical review, actual engine blue-hour/gameplay-camera views,
whole-coast fit and `.04` corners/transitions, water/land levels, boardwalk/furniture
alignment, stacked seawall review, vehicle contact/driving, actual network transports,
packaged builds, LOD transitions and sustained GPU/Deck/repetition profiling remain
pending. This component is not approval of a world placement or water-entry system.
No shared brief, queue, progress, road data, world scene, sibling asset, gameplay rule
or project setting was changed.
