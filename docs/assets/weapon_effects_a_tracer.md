# Weapon effects A — hitscan tracer (M1-C1.2a)

10 October 2026. **Technical delivery; owner art-review checkpoint remains pending.**
This extends [Compact combustion](weapon_effects_a.md), not the continuous rocket trail.
Base: `0dbcd0037a126c75fa72717e732ef1164bda3c88`.
Runtime attestation from the orchestrator: `portkey/gpt-6-astra:medium`, run
`2e8572d2-e17a-49da-a3ff-b364f9e4be5d`. Original project-owned geometry; no external art.

## Saved asset and presentation contract

`res://scenes/effects/weapon_effects/weapon_effects_a_tracer.tscn` is an instantaneous,
stationary amber-rim/ivory-core span. It inherits the unchanged family `effect.gd` API
through `tracer.gd`: `play() -> bool`, `is_active()`, `clear()`, `finished`, and the
one-shot no-op behavior of `stop_emission()`. `play()` makes the mesh visible immediately;
there is no particle warmup, projectile travel simulation, raycast, damage or RPC.
An occupied root rejects `play()` without restarting its lifetime.

- Lifetime: **0.075 s of local presentation process time**, then hidden/idle and one
  `finished` signal. Expiry occurs on the first process frame at/after the deadline;
  a stalled/paused process cannot promise a wall-clock visibility deadline.
- Default authored span: origin to local `(0,0,-1)` metres; +Y up, unit root.
- `configure_segment(from_m: Vector3, to_m: Vector3) -> bool` configures an idle root,
  including off-tree. Points are in its **stationary, unit-scale parent's space**
  (normally RuntimeEffects world space). Rotation maps -Z to the span and stretches
  only local Z; width stays constant. Vertical aim uses a safe alternate up vector.
- Rejects busy roots, nonfinite points and lengths outside **0.001–45 m**, without
  changing the old transform. The maximum covers decision 21's pistol/SMG ranges;
  it is a cosmetic envelope, not a second weapon-range rule. Callers handle false
  explicitly; this API neither clips gameplay nor invents an impact at its endpoint.
- Do not move, rotate or rescale the active root/parent. Retain it independently of
  the firing weapon/actor until settled; `clear()` is explicit teardown without
  a completion signal. The effect does not free itself; its allocator frees or reuses it.

**Decision 18 integration:** the local shooter calls this immediately with muzzle and
local cosmetic aim endpoints, alongside the muzzle flash, without waiting for a host
verdict. A tracer endpoint is **not** a hit indication. Impact effects, hit markers and
damage still wait for host confirmation. B2.1 owns this wiring, view-tick intents and
avoiding a second tracer when the host acknowledges a locally presented shot. Hydration
and prediction replay must not call `play()`. No gameplay/network owner was added here.

Every event gets its own idle saved instance. If one root is occupied, allocate another;
do not clear it or treat its false return as permission to drop the event. Event identity,
deduplication, admission and allocation scheduling remain the integrating owner's work.
There is no global pool/cap or speculative event manager in this asset lane.

## Source, mesh and culling

The existing source `art/source/models/effects/weapon_effects/weapon_effects_a.blend`
now includes `export_weapon_effects_a_tracer`, exported to
`art/models/effects/weapon_effects/weapon_effects_a_tracer.glb` with the shared
`tools/assets/blender/export_settings.json` contract and animations disabled.
`author_a.py -- --add-tracer` extends the pre-tracer saved source without rebuilding
its older geometry; the full authoring path also includes the new collection.
`reexport_a.py` checks **all seven current mesh GLBs byte-identically**, including the
six unchanged older exports. `geometry.json` records the added source bounds/counts.

The tracer has **64 triangles, one imported mesh, two material surfaces, three nodes**
per saved instance. All instances share the imported mesh/material resources. No
runtime mesh, copied vertex arrays, physics bodies, particles, textures or animations.
Unlike the family's particle carriers, the GLB is drawn directly: it needs neither a
hidden source copy nor an extracted duplicate `.res`. Import disables LOD generation
and animation import. The two source materials supply emission without a new shader.

The imported static mesh's measured local AABB is
**(-0.060,-0.060,-1.000) → (0.060,0.079,0.000) m**. Godot transforms that full box with
the configured span; at a 45 m local -Z span it extends to Z=-45 while X/Y remain
unchanged. There is no moving-particle travel or extra culling margin. This is a
visibility box, not collision, clearance or a damage radius. The camera-edge render
starts the 45 m span at X=-35 (offscreen) and still draws the intersecting visible part.

## Evidence and measured limits

[Evidence directory](../spikes/m1-c1-2a-evidence/) contains four actual 1280×800 Godot
renders, `validation.json`, `manifest.json`, `reexport.json` and `production-checks.json`.
The manifest links the source, GLB, saved scene, reproducible scripts and retained evidence.

| Render | View / visible result |
| --- | --- |
| `tracer_gameplay.png` | Native north-up 47 m / 42° camera; 10 m span; 390 changed pixels |
| `tracer_detail.png` | 18 m top-down detail; 4,738 changed pixels |
| `tracer_oblique.png` | Oblique form view with Courier/Sable scale references; 3,749 pixels |
| `tracer_camera_edge.png` | Native camera, offscreen-origin 45 m span; 1,677 pixels |

Pixel counts compare to the same quiet camera, below the overlay, using a >0.15 RGB
increase. They establish visible output, not owner aesthetic approval or city contrast.
Capture ages were 6.7–9.7 ms after `play()` with the **unextended** production lifetime.
Manual image inspection found a thin warm/ivory stroke at the native camera, a tapered
volume in detail, and no disappearance when only the middle of the long span was visible.
The dark asset stage does not establish bright-road, roof occlusion or equipped-muzzle fit.

A finite **40 simultaneous events** allocated and settled **40/40**. Measurements on
Windows, RTX 4070 Laptop GPU, Vulkan/Forward+, 60 FPS cap, **contended desktop**:
120 added nodes/objects (3 per event); process static-memory delta 187,784 bytes;
warm instantiate/add/play median 13 µs, maximum 87 µs; node count returned exactly to
baseline after free. Those timings and memory deltas are observations, not exact heap/GPU
allocation bytes or a performance gate. Per-event geometry/node work is constant and
occupancy lasts 0.075 s; no claim of bounded total memory for arbitrary unadmitted event
floods follows. B2/B4 retain sustained fire, scheduling and target-device acceptance.

GUT tests cover immediate play, busy retention, completion once/reuse/clear, stop-emission
semantics, finite/vertical/translated endpoints, invalid input retaining state, independent
40-event lifetimes, shared resources, no collision/particles, fixed AABB and saved-scene
roundtrip ancestry. Canonical production checks also clean-import a test mirror and
explicitly compile all owned scripts. Full canonical rerun after rebasing and trimming evidence: **62/62 GUT tests**
(including six tracer tests), **1,059 assertions**, **14 Python tests**, all owned
formatting/lint/compilation and clean import passed; the intentional negative GUT
fixture correctly returned 1. See `production-checks.json` for exact commands/results.

## Tooling and reproduction

No worktree MCP/editor tools were available; saved scenes were authored as text, then
loaded/packed/saved/reopened by the pinned headless engine with edit-state instance
preservation. Scene/node IDs and dependency UIDs are retained. Standalone ResourceSaver
omits dependency UID text, so the normalization pass restored the engine-resolved UIDs.
The retained GUT roundtrip checks saved instance ancestry and configured endpoint pose.
No separate open editor was used.

Initial capture exposed transposed camera/span matrices; correcting the saved transforms
produced the retained four-view results. An editor-script normalization attempt reported
exit RID leaks and was replaced by a clean standalone pass, not counted as a clean editor run.
The regular headless editor import prints the existing MCP 4.8 compatibility warning;
canonical mirrors disable that development plugin and require clean logs.

Use the mise-pinned Godot/gdstyle paths as in [development](../development.md), isolate
APPDATA/LOCALAPPDATA and XDG roots, and choose fresh output directories outside the repo.

```sh
# Saved-source reproducibility (Blender 5.2.2 LTS, glTF exporter 5.2.40):
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 \
  "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  art/source/models/effects/weapon_effects/weapon_effects_a.blend \
  --python art/source/models/effects/weapon_effects/reexport_a.py -- C:/tmp/ft/tracer-reexport

# Actual four-view capture + forty-event allocation receipt:
TRACER_OUTPUT=C:/tmp/ft/tracer-capture timeout 180 godot --path . --max-fps 60 \
  --rendering-method forward_plus --rendering-driver vulkan --resolution 1280x800 \
  res://tests/assets/effects/tracer_preview.tscn -- --tracer-capture

python tools/script_checks.py --output C:/tmp/ft/tracer-scripts
python -m unittest discover -s tools -p "*test*.py"
python tools/production_checks.py --output C:/tmp/ft/tracer-production
```

Without `--tracer-capture`, the preview supports SPACE fire, E camera-edge span,
1/2/3 camera selection, ESC exit and a 60-second automatic exit, always capped at 60 FPS.

## Remaining acceptance

**Regner must review the tracer look from the gameplay camera.** This checkpoint is
pending, not accepted by worker image inspection. Independent lane review was accepted
with no findings; this follow-up trims evidence only. B2.1 consumes the saved asset and owns actual firing/network timing; B4.1 owns
integrated city contrast and sustained effects/device cost. No Linux/Deck run, host/client
fire playtest, city-content change or damage rule is claimed. Planning/TODO/requirements
files are intentionally untouched; suggest marking technical C1.2a delivery ready for
B2.1 consumption after review while retaining the owner art checkpoint.
