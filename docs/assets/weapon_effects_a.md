# weapon_effects_a — Compact combustion

9 October 2026. **First reusable asset revision; independent technical handoff accepted.**
Regner selected A: “I really like both A and B. Lets start with A and we can review
again later.” B remains in the [concept gallery](../concepts/assets-v1/weapon-effects/gallery.html).
[Actual Godot camera sequence](../concepts/assets-v1/weapon-effects/production-a/index.html).

Producer: persistent weapon-effects lead. Concept/art selection: Regner. Technical
asset review: clean-context GPT-6.1-Sol high, accepted below. Equipped/world/gameplay/network
integration: external integrator. No foundation task or gameplay acceptance is closed.

## Current tracer addition (M1-C1.2a)

The family now also supplies `weapon_effects_a_tracer.tscn`: a presentation-only
0.075 s hitscan span with Blender-sourced geometry and the inherited family API.
The [tracer handoff](weapon_effects_a_tracer.md) owns endpoint configuration, culling
bounds, every-event allocation measurements and four native renders. Its owner
art-review checkpoint remains pending. The shared `.blend` and reproducible author/
reexport scripts now include the seventh mesh collection; the six older GLBs and
four original scenes are unchanged. The delivery history below describes those
original effects, not the tracer's current acceptance.

## Delivery and ancestry

The family supplies four collision-free, presentation-only saved scenes under
`scenes/effects/weapon_effects/`:

| Scene | Layers / particle capacity per instance | Lifetime and occupancy |
| --- | --- | --- |
| `weapon_effects_a_muzzle.tscn` | 1 flash + 2 sparks | 0.11/0.14 s; root settles at 0.17 s |
| `weapon_effects_a_hit.tscn` | 7 sparks + 3 dust puffs | 0.24/0.32 s; settles at 0.40 s |
| `weapon_effects_a_trail.tscn` | 5 hot + 6 cool puffs | Continuous; 0.25/0.50 s particles; settles 0.58 s after stop |
| `weapon_effects_a_explosion.tscn` | 9 fire + 7 smoke + 14 sparks + 5 chips | 0.50/1.15/0.52/0.75 s; settles at 1.45 s |

`weapon_effects_a_preview.tscn` composes those saved scenes, including four overlapping
independent explosion roots and a marker-only stationary trail. SPACE toggles playback, R restarts, ESC clears. Autoplay stops after 24 s.
The preview caps its own process at 60 FPS with VSync. Project main/settings unchanged.

One editable source: `art/source/models/effects/weapon_effects/weapon_effects_a.blend`.
Original geometry authoring: `author_a.py` in that directory; measurements and triangle
counts: `geometry.json`; saved-source reexport/check: `reexport_a.py`.
`art/source/.gdignore` excludes authoring files from engine import/export.

Each row below maps `export_weapon_effects_a_<kind>` in that source to
`art/models/effects/weapon_effects/weapon_effects_a_<kind>.glb` and its `.glb.import`:

| Kind | Triangles | Consumers |
| --- | ---: | --- |
| `muzzle_drop` | 336 | Muzzle/Flash, two material surfaces (amber shell / ivory core) |
| `fire_lobe` | 168 | Explosion/Fire |
| `smoke_puff` | 168 | Explosion/Smoke; Hit/Dust |
| `spark` | 168 | Muzzle/Sparks; Hit/Sparks; Explosion/Sparks |
| `chip` | 108 | Explosion/Chips |
| `trail_puff` | 168 | Trail/Hot and Cool |

Six particle GLBs use Godot's importer-owned external mesh extraction to adjacent
`weapon_effects_a_<kind>_mesh.res`. Their import settings retain the matching UID and
fallback path. Each emitter references that external mesh and retains a hidden linked
`MeshSource` GLB instance. No runtime-generated mesh or copied vertex array in a scene.
There are no physics bodies or collision shapes.

External family materials live in `art/materials/effects/weapon_effects/`: spark, smoke, chip
and trail StandardMaterial3D resources; fire_tint ShaderMaterial and the original
`weapon_effects_a_fire.gdshader`. The shader carries particle lifetime color into
albedo and emission, following Godot's [particle COLOR contract](https://docs.godotengine.org/en/latest/tutorials/shaders/shader_reference/particle_shader.html).
Opaque lobes shrink to zero; no alpha billboard/textures, skin, skeleton or animation
clips are required. Motion and size/color curves are saved GPUParticles3D resources.
Tiny particle carriers disable generated LODs; no global LOD/performance policy follows.

## Attachment and extent contract

Metres, unit roots, +Y up, -Z forward; Blender +Z up/+Y front converts once through glTF.
Muzzle origin is the weapon's emission marker. Flash extends -Z from that origin:
source length 0.660 m, width 0.380 m, height 0.242 m at maximum unit scale. The broad
flash leaves a pointed zero-width origin; it does not require a larger muzzle aperture.
No additional grip, support-hand or shoulder anchor is needed by this effects family.

- Pistol accepted dependency HEAD `2f1846e9d883bbd15a0bcda4f826170b55ea2b5c`, candidate
  `b8363f55a6cfe8ab6cf02b1458a3d193629de59b`: `socket_muzzle` → `Sockets/Muzzle`,
  `(0,0.122,-0.421)` m from grip, identity basis; aperture diameter 0.048 m.
  Reference only; no pistol files are copied or modified.
- Wedgewire candidate `bc1075c985e11ced6c2c23f948808ebf482ba178` (peer review pending):
  `socket_muzzle` → `Sockets/Muzzle`, `(0,0.140,-0.520)` m, identity basis;
  aperture diameter 0.028 m, outer rim diameter 0.052 m. Compatible anchor convention.
- Dock Thumper: `socket_trail` → `Sockets/Trail`, `(0,0,+0.230)` m, identity basis,
  5 mm behind exhaust rim; opening diameter 0.066 m. Emission extends +Z. Final reviewed
  rocket dependency remains pending; this preview contains a marker, no duplicate rocket.

Hit uses local +Y as the contact normal. Explosion assumes a stationary world-space
root placed at the accepted presentation origin. All one-shot emitters use local
coordinates; do not continue moving/reorienting an active impact/explosion root.
Trail particles use world coordinates; detach/retain its instance at projectile removal,
call `stop_emission()`, and keep it alive until `finished`. Destroying the rocket parent
and its child trail immediately would also destroy the residual puffs.

Saved conservative visibility boxes (minimum → maximum, metres relative to emitter):

| Effect | Visibility AABB |
| --- | --- |
| Muzzle | (-0.45,-0.30,-1.05) → (0.45,0.30,0.07) |
| Hit | (-1.30,-0.40,-1.30) → (1.30,1.60,1.30) |
| Explosion | (-4.50,-1.60,-4.50) → (4.50,4.20,4.50) |
| Trail | (-12,-3,-12) → (12,3,12), provisional for moving integration |

Boxes include mesh radius, authored scale and travel. They are culling bounds, **not
blast/damage radii or physics clearance**. Trail speed is not assumed: external
integrator must measure maximum displacement over the 0.50 s residual lifetime and
expand the box if needed, including turns/vertical motion, then check camera-edge culling.
No actual projectile path/speed or equipped-weapon city clearance has been tested here.

## Presentation API and ownership

`effect.gd` is shared only within this family. `play() -> bool` starts an idle saved
instance. An occupied root returns false without resetting its existing event.
`is_active()` reports occupancy; `finished` signals after authored settling time;
`clear()` is explicit presentation teardown; `stop_emission()` stops a continuous trail.

The integrator owns accepted event identity, duplicate suppression and lifetime-aware
allocation. **Every accepted explosion must get its own available visible instance.**
Never treat `play() == false` as permission to drop an event; allocate another instance
of the saved scene. There is no global limit, pool, tier switch or damage/chain/network
logic in this family. This preserves the owner policy in S05 uncapped effects and S15.
Existing spike fixtures and their differently oriented rocket remain untouched.

## Provenance, tools and saved evidence

Original project-owned Blender geometry, particle composition, shader and preview
stage authored by the weapon-effects lead for Regner; no third-party art, brands,
textures, fonts or audio were imported. Godot's existing default font renders preview
labels. Concept imagegen prompts and tool/output provenance remain in
`docs/concepts/assets-v1/weapon-effects/prompts.json` and `files.json`.
Historical Godot bootstrap is preserved as source-only `godot_bootstrap.gd.txt`; it
predates final tuning and must not be rerun over the final scenes. Final scene files
are authoritative. `author.gd`/`authoring.tscn` now provide only technical inspection
and narrowly scoped import UID/index repair, not hierarchy generation.

Pins: Blender 5.2.2 LTS (`d13f752e3b9c`), glTF exporter 5.2.40;
Godot 4.8.dev7.official.c971f93e7; gdstyle 0.3.0. GLBs use the production shared
`tools/assets/blender/export_settings.json` contract plus explicit collection and animations=false.
Sources contain no linked external libraries/images. Static root transforms are unit.

Evidence is in [production-a](../concepts/assets-v1/weapon-effects/production-a/):

- `reexport.json`: saved .blend → all seven GLBs byte-identical, source/output SHA256.
  Reexport completed all assertions and wrote its receipt. Blender's audio shutdown
  remained resident afterward; clean process exit is not claimed for that invocation.
- `clean-import.log`: fresh effects-only scratch project, no addons, no `.godot` copy;
  pinned headless editor import exited 0 without warnings/errors. This proves the
  asset profile only, not full-project addons/export/device compatibility.
- `api.log`: public-API checks exited 0 without warnings/errors. Twelve independent
  explosion roots, muzzle/hit, busy-root retention, completion signal, reuse/clear,
  continuous trail retention and stopped-trail settling. Node visibility is not pixels.
- `roundtrip.log` / `roundtrip.json`: six scenes save → close → reopen → save through
  the private editor, byte-identical. All owned scripts pass pinned gdstyle at 100 chars.
  Editor index refresh corrected initial stale extraction references before this pass.
- Six `weapon_effects_a_*.png` and `capture.log`: actual 1280×800, north-up vertical
  perspective, 47 m/42°, near 0.1/far 160, Forward+/Vulkan GTX1070. One second warmup,
  recorded actual simulation ages, bounded native process exit 0. Camera is saved.
  Muzzle/impact are brief small marks; fire separates into lobes and later porous smoke.
  These are local playback observations, not target occlusion or load acceptance.

Useful checks (from this worktree; set isolated XDG paths for private processes):

```sh
blender --background --factory-startup -noaudio --disable-autoexec --threads 2 \
  art/source/models/effects/weapon_effects/weapon_effects_a.blend \
  --python art/source/models/effects/weapon_effects/reexport_a.py -- /tmp/effects-reexport

godot --headless --path <fresh-effects-profile> \
  --script res://scenes/effects/weapon_effects/verify.gd

godot --path <effects-worktree> --max-fps 60 --resolution 1280x800 \
  res://scenes/effects/weapon_effects/weapon_effects_a_preview.tscn
```

Built-in Blender MCP was disconnected. Built-in Godot MCP could not authenticate
against isolated XDG registry. A private authenticated toolkit client verifies exact
project path, PID and port before editor writes; no shared registry/config is changed.
Private editor PID70915 owns 17550–17554; bounded checks used 17555–17558.
State: `/tmp/brackett-weapon-effects`. Initial author/export Blender PID74744 and
completed reexport PID104000 have retained shutdown processes; sources/outputs are
saved, neither is an unsaved interactive authoring session. No peer process was killed.
Earlier logs contain addon reimport warnings and sandbox user-data/socket diagnostics;
the corrected fresh import, final API and native capture logs above distinguish them.
`.mcp.json` is a local plugin-generated file, excluded from the delivery commit.

Owner routing instruction (9 October): modeling, geometry, spatial rigs/poses and
spatial VFX animation require Astra. Non-spatial imports/configuration may use Sol6.1.
Pre-instruction source is preserved. Before resumed spatial work Paseo verified
`runtimeInfo.model=gpt-6-astra`, high, session `01a12094-69c8-7453-91a5-7b108cae200e`,
active `codex-turn-13`. Reverify after any later model change. No duplicate lead/worktree.

## Review status and integration delta

Concept: accepted A by Regner. Source/export, saved prefab and asset-local technical
checks: completed producer checks above. Independent scoped review: accepted at `d015ae6cc5ad070a86c5025383f39f0f8cc79d08`;
[report and actual checks](../concepts/assets-v1/weapon-effects/production-a/independent-review/review.md).
The sole P3 formatting note is fixed; final delta changes one blank line plus documentation/evidence.
Final
owner art revision, equipped/world readability, moving trail/camera-edge checks,
12/24-burst overdraw/load, hardware/device and gameplay/network acceptance: pending
with Regner/external integrator. No system-wide performance claim.

For later reconciliation only, add catalogue family `weapon_effects_a` linking this
record and the four scenes. Mark approved-A source/GLB/saved preview delivered after
independent review; retain tasks for weapon/rocket attachment, every-event allocation,
residual trail lifetime/bounds, city readability and measured burst/device cost.
Shared catalogue/TODO/planning files are intentionally not edited by this track.

Dependency receipt update: direct peer handoff reads/messages for pistol/SMG later
reported missing worktree paths. Their immutable owner/peer measurements above remain
the reference; no worktree restoration or dependency-copy action was taken. Rocket
reported source cleanup after its review and is refreshing its own saved scenes.
Effects art does not depend on those models being copied into this workspace.

The completed embedded preview was ended through Godot’s normal `game.stop`; the private
editor remains open on the saved asset preview. Bounded capture processes exited normally.
