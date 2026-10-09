# Godot development workflow

Build small, inspectable features around clear ownership. Save authored state in
the editor, keep dependencies reproducible, and validate the behavior affected by
each change. [AGENTS.md](../AGENTS.md) defines the working rules.

## Project organization and ownership

Create directories as they become useful. A simple starting layout is `scenes/`
for reusable scenes and levels, `scripts/` for gameplay, `art/` for source assets
and imports, `tests/` for checks, `tools/` for repository utilities, and `docs/`
for current contracts. Keep vendor addons separate from project-owned addons.
Use consistent names and avoid multiple unrelated systems hidden in a level script.

The P0-02 [ownership](architecture.md), [scene](scene-structure.md), and
[API](api-contracts.md) drafts reserve concrete paths and boundaries for the spikes;
they describe planned systems, not code already present. Use their owner map rather
than introducing a second state owner. The [product brief](design.md) owns scope.

For each system, identify its owner, inputs, outputs, state, and lifecycle. A
movement component accepts commands without reading keyboard/gamepad input. Input
controllers translate local devices, AI, or network intent into that API. Resource
definitions own shared tuning and identifiers. Presentation reads simulation state
and may calculate display values without deciding gameplay outcomes.

Introduce autoloads only for responsibilities that actually persist across scenes,
such as a session service. Keep level-specific simulation under the level/match.
Start with process services under the persistent Boot scene as specified in the
scene draft; there are no planned project autoloads for the first proof. Keep the
[ownership map](architecture.md#state-and-rule-owners) current as systems arrive;
avoid speculative managers.
Apply commands before simulation and capture state after simulation. Use explicit
physics processing priorities when order matters rather than incidental sibling order.

Validate replacement resources before removing the current component. Restore all
state needed by observers before emitting completion signals. Clear commands and
transient state on disable, focus loss where appropriate, reset, and teardown.

## Godot scene and script conventions

These conventions apply to project-owned UI, 2D and 3D systems. Review relevant
conventions for the changed subsystem rather than requiring unused features.

### Saved composition and reusable boundaries

Author node hierarchies, layout, placement, default properties and reusable assemblies
in `.tscn`/`.scn` files. Include menus, HUDs, widgets, actors, cameras, colliders,
timers and effects. Scripts implement behavior, instantiate saved `PackedScene`s and
configure instance data/state; they must not rebuild those assemblies with sequences
of `Node.new()`/`add_child()` calls. Dynamic lists instantiate a saved item scene and
populate its data. Runtime spawning of saved scenes is expected.

Pure logic and data types may remain scripts, `RefCounted`s or Resources without an
empty wrapper scene. Intentional procedural systems must document their source of
truth and boundaries; they cannot silently replace authored UI or world composition
or bypass the [Blender model/source contract](assets.md). This scene-file requirement
is a project convention, not a claim that Godot forbids creating nodes in code.

Keep reusable scenes independent of a particular enclosing hierarchy. Expose a small
public API on the scene root; consumers should not reach through another scene's
internal children. Structure parentage around lifetime and intended inherited
transforms, so deleting a temporary parent cannot remove a longer-lived object.
Prefer composition of focused scenes/components; introduce inheritance only for a
real shared contract, preserving intentional inherited scene overrides.

### Call down, signal up

Parents coordinate children by calling their public methods. Children report events
through signals connected by the enclosing coordinator. That coordinator mediates
sibling interactions. A reusable child must not assume its parent implements a
method through `get_parent().some_method()`, climb `../..`, or use an absolute tree
path to reach a particular enclosing scene. Paths to the scene's own required
children are part of its internal contract.

When a component needs an external collaborator or synchronous query, inject an
explicit typed reference or callable and define its lifetime. Do not force every
query into a signal or build a global event bus for local relationships. Prefer
typed methods and signal connections when the interface is known; use groups for
intentional discovery/broadcast, not to hide ownership or bypass admission rules.
Validate required bindings before use and make missing configuration diagnosable.

### Engine lifecycle, Resources and presentation

- Initialize configuration needed by `_ready` before tree entry; use `@onready` or
  `_ready` for bindings that require children to exist. Guard against callbacks,
  timers and awaited work outliving their node/session or applying an obsolete result.
  Use `queue_free()` for normal node removal; defer tree/physics changes when their
  engine callback requires it. Review owned connections and references on teardown
  and rebinding so callbacks cannot accumulate or target a freed object.
- Keep reusable definitions in Resources, with per-entity mutable state owned by
  the instance. Loaded Resources may be shared: changing one actor's material,
  definition or nested Resource must not inadvertently change every actor. Choose
  explicit duplication or scene-local data only where mutation requires isolation.
- Run physics movement and collision simulation on physics ticks with the appropriate
  time step; keep rendering/interpolation in presentation. Use InputMap actions and
  gameplay input handling that respects GUI consumption, such as `_unhandled_input`
  for events the UI should handle first. Keep device collection out of simulation.
- Author UI layout with suitable Containers, anchors, size flags and shared Themes.
  Check keyboard/gamepad focus, mouse filtering, text growth and supported resolutions.
  A Container owns its children's layout; scripts must not fight it by resetting
  those transforms every frame. Cache stable scene bindings instead of repeatedly
  searching the tree in hot callbacks; add wider optimization only with evidence.

These conventions follow Godot's guidance on
[scene organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html),
[scenes versus scripts](https://docs.godotengine.org/en/stable/tutorials/best_practices/scenes_versus_scripts.html),
[Resources](https://docs.godotengine.org/en/stable/tutorials/scripting/resources.html),
[node lifecycle](https://docs.godotengine.org/en/stable/classes/class_node.html),
[physics processing](https://docs.godotengine.org/en/stable/tutorials/scripting/idle_and_physics_processing.html),
[input propagation](https://docs.godotengine.org/en/stable/tutorials/inputs/inputevent.html)
and [Containers](https://docs.godotengine.org/en/stable/tutorials/ui/gui_containers.html).
Verify API details against the pinned engine when implementing.

## Safe change sequence

1. Read the owner, callers, existing tests, and current contract. Establish which
   saved properties, resource references, and public APIs must survive.
2. Inspect the affected editor scene and preserve unsaved work. Use the editor
   workflow in AGENTS.md for editor-managed mutations.
3. Make a focused change and save it. Keep a necessary behavior-preserving refactor
   separately reviewable from the new behavior.
4. Import changed assets with the pinned engine. Reopen affected scenes, including
   inherited scenes, and verify links and local overrides after saving.
5. Run relevant checks and inspect the saved diff. Update current contracts and
   actionable future tasks; clearly label historical plans.

## Resource identities and version control

Godot's local import cache belongs in `.godot/` and is already ignored. Source
import settings and `.uid` sidecars belong with their assets in version control.
Preserve saved scene/resource UIDs, dependency UIDs, node identities, and inheritance
data generated by the pinned engine. Do not strip unfamiliar metadata during cleanup.
[Godot version control guidance](https://docs.godotengine.org/en/stable/tutorials/best_practices/version_control_systems.html)
describes the distinction between source metadata and generated caches.

Move or rename resources through Godot where possible. Check UID/path agreement,
missing dependencies, and inherited overrides after a move. A successful path
fallback can hide an incorrect UID, so merely loading once is weak evidence.
Validate from a clean import cache as well as the existing editor when establishing
resource tooling. Save/reload tests should preserve identities and authored values.

Commit cohesive source, output, scene, and import-setting changes together. Keep
generated builds, local tools, credentials, and caches out of Git. Consider Git LFS
when binary asset size/history warrants it rather than introducing it by default.
Editor-authored IDs are meaningful diff content; harmless serialization changes
still deserve review for unintended property or transform changes.

## Validation layers

For a requested project-owned GDScript review or focused subsystem audit, use
[`gdscript-review`](../.agents/skills/gdscript-review/SKILL.md). It traces owners,
callers and saved data, reports severity/evidence/fixes, and distinguishes observed
bugs from unavailable checks. Review findings do not replace the validation below.

| Layer | What it establishes | When to use it |
| --- | --- | --- |
| Style and lint | Formatting, type-hint policy, static quality rules | Owned script changes |
| All-script compilation | Syntax and configured engine warnings, including unused scripts | Script and engine changes |
| Import and resource checks | Dependencies, UID agreement, persisted scene integrity | Asset, scene, and resource changes |
| Component and physics checks | Independent gameplay contracts through production APIs | Rules, state, collision, and lifecycle changes |
| Real-process network checks | Admission, authority, ordering, replication, and cleanup | Multiplayer behavior changes |
| Windowed playtests | Real input, focus/cursor handling, camera, HUD, sound, and smoothing | Player-facing changes |
| Exported-build checks | Packaged resources, native libraries, target renderer, and launch | Release/export changes |

Tests should exercise important outcomes. Use actual movement, collision queries,
firing, overlaps, and lifecycle APIs where those are the contract. Keep expected
results independent of the production formula. Preserve failure logs and use
bounded deadlines. Check new script/engine errors and teardown diagnostics even
when a process exits successfully.

Standalone deterministic fixtures may use fixed stepping; live network tests need
normal paced simulation and wall-clock deadlines. Compare authoritative states at
matching ticks, not a smoothed current client transform to an earlier host transform.

## Foundation validation tasks

S01 adds only the P0-03 tooling required for its owned fixtures. Run the installed
pins through Mise. Shared script/style checks accept `--godot`/`--gdstyle`;
S01 asset tools accept `GODOT_BIN` when Mise trust-state writes are unavailable. The shared tasks check versions and honor
hidden/`.gdignore` trees, excluding the two current vendor addons explicitly.

| Task | Scope |
| --- | --- |
| `mise run gdstyle:check` | Every discovered owned `.gd`, pinned lint with zero warnings; comments/export/function spacing still reviewed manually |
| `mise run gdscript:check` | Explicit `--check-only --script` invocation for every owned script, including unused scripts; retains per-script logs |
| `mise run resources:check` | S01 source/export links, unique resource UIDs, external files/no copied meshes, engine dependencies and UID/path agreement, dimensions/axes/sockets/clips, saved IDs/transforms/inheritance |
| `mise run s01:reexport` | Opens both committed Blender sources with the selected Blender version, exports validated scratch GLBs and requires byte equality with committed outputs |
| `mise run s01:clean` | Isolated asset-profile clean import and resource checks, compares persisted files, then proves focused corruptions fail |

S01 asset logs default to ignored `builds/`; script/session logs use printed fresh
external directories. Subprocesses have deadlines/private user dirs
and do not stop unrelated processes. Checks fail on error/warning logs as well as
exit status. The clean asset profile omits development autoload/editor plugins and
ignores vendor addons only in its temporary copy; it preserves owned resources and
renderer/physics settings. This isolates source/resource checks from known
full-project plugin diagnostics, retained in [S01](spikes/s01.md). It is not a
full-project, packaged-export, gameplay or transport compatibility test.

After changing a Blender source, `python tools/s01/reexport.py --install` validates
both scratch outputs before installing them, preserving `.import` sidecars. Refresh
and close/reopen/save affected scenes in the existing editor separately; headless
checks cannot synchronize an open tab. S01 records the toolkit helper required by
this session's limited callable surface and the direct-child identity limitation.

A preserving formatter/fix wrapper, broader production resource discovery/coverage,
CI and gameplay checks remain future work. The bounded two-process runner is S03's
P0-03 contribution.

### Session and script tooling

The working commands are:

```sh
mise run gdstyle:check
mise run gdscript:check
mise run tools:check
mise run spike:s03

# Equivalent direct validation baseline (from the repository root):
python tools/script_checks.py
python -m unittest discover -s tools -p "*test*.py"
```

The first checks pinned formatting and lint. The second also discovers every owned
`.gd`, honors hidden and `.gdignore` directories, excludes the two named vendor
addons, and explicitly invokes `--check-only --script` for each file, including
unused scripts. A fresh dependency mirror retains project settings, gameplay autoloads
and resources, but disables editor plugins and the development-only MCP runtime autoload
only in that mirror. Its import discovers classes;
separate compilation remains mandatory even when that setup reports errors.
The source editor and its `.godot` cache are not the compiler's inputs. Logs,
manifest and per-file outcomes remain in the printed evidence directory.

`tools:check` discovers the root tests and packaged tool tests, including S04, S05 image,
S07 comparator/driver and S08 cadence checks. It covers diagnostics with zero exit status
and child-process ownership. The [S03 runner](spikes/s03.md) copies the saved fixture
into an addon-free project, then uses real ENet host/client processes and a focused UDP
fault proxy.
It supplies independent process user/log directories, configurable host/proxy ports,
structured readiness/results, case/runner deadlines, and child-only cleanup.
Both tools accept explicit executables and an external evidence directory; defaults
use tools on PATH. Mise pins Python 3.14.2 so task commands use the same `python`
executable name on Windows and Linux. Use the exact installed engine pin.

Review function purpose comments, two empty lines between functions, export groups,
and intent inside functions manually. The preserving formatter wrapper remains
future work; no `gdstyle:fix` task is claimed. Runtime loops intentionally await
paced polling to let Godot process networking; their narrow lint exemptions explain
that contract. S01 owns resource/source-link and Blender fixture checks. CI and gameplay
coverage grow in M1-D1; S07 owns capacity methodology/decisions, S08 exact exports/input,
and M1-D3 integrated target acceptance. S03 is an isolated session proof.

The import command remains available:

```sh
mise exec -- godot --headless --editor --path . --import
```

An import command's success does not mean scripts compiled or logs were clean.

### Real-project desktop exports

The project has a saved `run/main_scene.tscn` entrypoint and four x86-64 presets:
Windows/Linux, debug/release. Current ENet-only M1 presets keep the vendor addons in
source but exclude GodotSteam and MCP from packages. This is a provisional export
boundary pending the owner decision on removing GodotSteam, not a Steam integration
choice. The exact template hashes, bounded commands, package inspector, Windows smoke
and Linux launch checklist are in [S08-X](spikes/s08-x.md). Use matching pinned
4.8-dev7 templates, fresh external output directories and the documented timeouts.

### S02 desktop fixture tooling

The [reviewed desktop handoff](spikes/s02.md#reviewed-desktop-handoff) and
[source/prefab handoff](assets/s02_kit.md) discover the linked corner/alley harness,
inherited 50° comparison and held-weapon study. Run from the repository root with
the exact pinned engine (explicit binaries are useful when Mise trust writes are restricted):

```sh
mise exec -- godot --path . res://tests/fixtures/s02/corner.tscn
python3 tools/s02/run.py --godot /path/to/pinned/godot --output /tmp/s02-my-run
python3 tools/s02/reexport.py --output /tmp/s02-my-reexport
```

There is no `spike:s02` Mise task. `run.py` requires `--godot`; its optional
`--output` must be fresh and outside the checkout, otherwise it creates a temporary
evidence directory. It imports an isolated project with development autoloads/editor
plugins removed and addons ignored only in that copy, then exercises the fixture's
motion/input/query APIs and supplementary source/dependency/UID checks. It compares
persisted scene/import/UID fingerprints and retains import/outcome logs, summary
and identities. These bounded S02 checks supplement `resources:check`'s S01 scope;
they are not broad production-resource discovery, all-script compilation, native
focus or packaged/network acceptance. Continue to compile every owned script separately.

`reexport.py` uses Blender on PATH to reexport the committed source into scratch
outputs, rejecting any of the nine GLBs that differ or contain images/extensions;
it retains Blender logs/fingerprints. It installs no output. Author source and
explicit exports together and follow the editor refresh/reopen contract after changes.
Actual-camera captures and native focus use separate graphical tools documented in
[S02 reproducibility](spikes/s02.md#tools-authoring-and-reproducibility); a headless
API pass cannot substitute for an observed OS focus switch or physical-key Alt-Tab.

Accepted receipts support the bounded desktop technical fixture only. Its 47 m/42°
camera, speed/turn/follow, marker/cutaway and held silhouettes remain candidates.
Current native OS focus revalidation is incomplete; historical passes do not close
it. Physical-key playtesting, human feel/latency, moving-camera/roof/weapon readability
and LCD/OLED Deck controls/Gaming Mode/native 1280×800/60 FPS remain unproved.
The fixture's fixed engine-step motion is not a validated arbitrary-delta/prediction
replay contract; S03-R owns that decision. [S07](spikes/s07.md) preparation supplies
capacity axes and diagnostic method, with actual measurements still unexecuted.

### S03-R foot-response tooling

The accepted [bounded S03-R record](spikes/s03-r.md) supplements the S03 session
proof with actual unchanged S02 movement/collision/aim and linked source assets.
Saved [boot](../tests/fixtures/s03_r/boot.tscn) inherits S03; its two bodies instance
the [S03-R actor](../tests/fixtures/s03_r/actor.tscn), which inherits S02.
The [source handoff](assets/s02_kit.md#accepted-s03-r-downstream-consumers) maps
the actor and CityRoot consumers. These are isolated technical fixtures.

Run from the repository root when assigned the required process/display access:

```sh
python3 tools/run_s03_r.py --godot /path/to/pinned/godot --output /tmp/s03-r-my-run
# Select one existing profile, alternate ports and a bounded case deadline:
python3 tools/run_s03_r.py --godot /path/to/pinned/godot --profiles adverse --port 24910 --proxy-port 24911 --deadline 45 --output /tmp/s03-r-adverse
```

There is no `spike:s03-r` Mise task. Static reads of the
[runner](../tools/run_s03_r.py) and its shared
[script helpers](../tools/script_checks.py)/[child cleanup](../tools/run_s03.py)
establish the existing options:

| Flag | Default and constraint |
| --- | --- |
| `--godot` | Godot on PATH, falling back to `godot`; exact `4.8.dev7.official.c971f93e7` version required, version query timeout 10 s |
| `--profiles` | `baseline normal adverse`, run sequentially; one or more choices from those names |
| `--port`, `--proxy-port` | `24900`, `24901`; distinct UDP ports in 1–65535, reused across sequential profiles |
| `--deadline` | 45 s per host/client case, starts after isolated import; accepted range 1–90 s, separate import timeout 30 s |
| `--output` | Printed `s03-r-` temporary directory if omitted; supplied directory may be absent or empty, must resolve outside the checkout |
| `--windowed` | Off; attempts actual graphical frame receipts at 1280×800, host/client positions (0,0)/(1280,0); requires exactly `--max-fps 60` and rejects every other value before engine launch; no forced-draw substitute or automatic visible/feel acceptance |
| `--bypass-proxy` | Off; baseline-only direct loopback diagnosis, connecting the client to the host port |
| `--high-resolution-timer` | Off; balances Windows `timeBeginPeriod(1)`/`timeEndPeriod(1)` around the run; retained as a diagnostic, not a default fix |
| `--max-fps` | `0`, range 0–1000 for headless runs; windowed runs require exactly 60; records and applies `Engine.max_fps` in both fixture processes |
| `--low-processor-mode` | Off; records and applies `OS.low_processor_usage_mode` in both fixture processes |
| `--disable-vsync` | Off; passes the engine's VSync-disable option to both fixture processes |

Each profile stages a fresh project containing saved `s02`, `s03`, `s03_r` fixture
trees and `art/models/spikes/s02_*.*` imports/sidecars. It copies project settings
with development autoload/editor-plugin sections and the icon reference removed;
no addons or authoring sources are copied. Renderer/physics/input settings remain
from the copied project. Headless import checks diagnostics and exit status.
Import, host and client receive separate XDG data/config/cache directories.
The runner does **not** invoke all-script compilation or Blender reexport;
continue using the separate foundation checks for those scopes.

Two paced ENet processes use a seeded bidirectional native UDP proxy on
`127.0.0.1`: baseline has no delay/loss; normal uses 75 ms ±30 ms one-way delay
and independent 2% loss; adverse uses 125 ms ±50 ms and 5%, plus one second of
delivery interruption and the fixture's 250 ms host stall. Proxy work is bounded
to 128 receive/delivery entries per poll and a 1024-entry queue. Cleanup terminates
only owned Popen children, with a shared 2 s wait then kill/wait fallback.
This is Linux loopback evidence, not LAN/Windows/Steam/Deck or packaged validation.
Same-machine wall clocks support snapshot-age/stationary-recovery diagnostics;
engine elapsed time supports synthetic local response. No cross-device clock
or physical-key latency assumption is established.

The printed evidence directory retains a top-level `result.json` and per-profile
copied project, `import.log`, `proxy.jsonl`, host/client `stdout.log`, `engine.log`,
private user directories and capture directories. A completed profile result
retains commands, PIDs/exits, ports, source SHA256 fingerprints, saved-source
comparison and measurements. Failures retain logs and a top-level failure result;
an early failure may leave no completed per-profile result. Host/client results,
nonzero exits and `SCRIPT ERROR:`, `ERROR:` or `WARNING:` diagnostics are checked.
Technical success also requires collision/expiry/resync, matching-tick installation,
all 20 applied-physics response samples, stationary convergence and unchanged
copied source. Missing drawn-frame samples do not alone fail those technical criteria.
The [analyzer ownership regression](../tools/test_s03_r_analysis.py) fences client
response to entity 2; host acknowledgements cannot count as owned response.

Accepted baseline/normal/adverse synthetic input-to-applied-client-physics p95 is
**69/235/365 ms**. Adverse stationary convergence is **220.12/415.32 ms** after
actual proxy resumption/host-stall end. The separately recorded baseline-floor fix
follow-up is **366 ms** physics response and **124.71/493.79 ms** stationary
convergence; it does not replace the original three-profile result. Retained old
analyzer response fields are historical; owned-entity reanalysis supersedes them.
Drawn response was unavailable. Zero matching-tick installation error and update
jumps are not predicted corrections: there is no predicted state. The
[reviewed resync P2 is closed](reviews/s03-r-b87f889.md); full S03-R remains open
for drawable owned/remote response, camera/aim continuity and human feel, then a
separately bounded shared-rule replay trial only if warranted. Native OS focus/
physical-key, S02/Steam/Deck/Windows/export, P0-GATE and production gates remain open.
Historical editor-relocation receipts do not certify current shared editor state;
future authoring/reexports still need the existing save/refresh/reopen workflow.

The dated [S03-L Windows diagnosis](spikes/s03-l.md) adds sequence-correlated engine timing and
separately measured proxy receive/forward boundaries; every timing remains labelled contended.
It did not prove the Python proxy, timer resolution, VSync or one pacing setting as the sole
Windows floor. Unsafe historical uncapped window rows and pre-fix zero-by-construction proxy
telemetry are explicitly invalid. Corrected VSync on/off rows both use a 60 FPS cap. Until a quiet
rerun replaces it, prediction/S12 should carry its provisional 350 ms p95 local Windows scheduling
allowance. The expiry analyzer reads Match's exact decision age and preserves the strict 250 ms
criterion.

### S04 car fixture tooling

Accepted [exact-final S04 disposition](spikes/s04.md#accepted-exact-final-disposition)
and [source handoff](assets/s04_kit.md) discover the saved linked car/track wrappers,
[comparison](../tests/fixtures/s04/body_comparison.tscn) and
[boot](../tests/fixtures/s04/boot.tscn) inherited from S03. These are technical fixtures.
The [body/seat record](spikes/s04-contracts.md) refines the canonical API and owns the
bounded handling/capture details and future M1-B1 matrix.

Existing recipes, from the repository root when assigned the required access:

```sh
python3 tools/run_s04.py --godot /path/to/pinned/godot --output /tmp/s04-my-run
python3 tools/run_s04.py --godot /path/to/pinned/godot --profiles normal adverse --port 25010 --proxy-port 25011 --deadline 45 --output /tmp/s04-followup
python3 tools/s04/run_checks.py --godot /path/to/pinned/godot --output /tmp/s04-my-checks
python3 tools/s04/reexport.py --output /tmp/s04-my-reexport
```

There is no `spike:s04` Mise task. Static source mapping:

| Tool / option | Existing behavior and bound |
| --- | --- |
| [run_s04.py](../tools/run_s04.py) `--godot` | PATH Godot or `godot` by default; exact `4.8.dev7.official.c971f93e7` required, version timeout 10 s |
| `--profiles` | Sequential `baseline normal adverse` default; one or more of these names |
| `--port`, `--proxy-port` | 24900/24901; distinct UDP ports in 1–65535, reused sequentially |
| `--deadline` | 45 s per host/client case after import; accepted range 1–90 s; separate import timeout 30 s |
| `--output` | Printed temporary `s04-` directory if omitted; absent/empty external directory required |
| `--windowed` | Off by default; attempts actual 1280×800 graphical receipts, never forced draws or automatic visual acceptance |
| [run_checks.py](../tools/s04/run_checks.py) | Required `--godot`; optional fresh empty external `--output`, otherwise `s04-checks-` temporary directory; exact pin, 30 s import and 35 s per check |
| [reexport.py](../tools/s04/reexport.py) | Optional `--output`, otherwise `s04-reexport-` temporary directory; Blender on PATH, 90 s subprocess deadline; no `--godot`, `--install` or engine/import check |

`run_s04.py` stages saved S02/S03/S04 fixture trees (excluding editor harnesses) and
S02/S04 models/import sidecars, without addons or Blender authoring sources. Copied
settings retain renderer/physics/input; autoload/editor-plugin sections and icon
reference are removed. Import, host and client have separate XDG directories.
Two paced ENet processes use a seeded loopback UDP proxy: baseline no impairment,
normal 75 ms ±30 ms one-way/2% loss, adverse 125 ms ±50 ms/5% with one-second
interruption and fixture 250 ms host stall. Proxy queue/work are bounded at
1024 entries/128 receive and delivery entries per poll. Child cleanup uses the
shared S03 owner-only termination/wait/kill fallback. This is Linux loopback,
one-host/one-remote evidence, not four-player, LAN, Windows, Steam or Deck proof.

Top-level `result.json` and per-profile copied project, `import.log`, `proxy.jsonl`,
host/client `stdout.log`, `engine.log`, private user/capture directories retain
commands, exits, fingerprints and measurements when the case completes. Failures
retain available logs and a failure summary; an early failure need not have a
completed case receipt. Exits and engine/script errors or warnings fail technical
checks, as do collision/expiry/fences/resync, matching-tick install, all20 physics
samples, stationary recovery or unchanged-source failures. Missing drawn samples
alone do not fail the technical criteria. No all-script compilation is invoked.

`run_checks.py` stages the same dependency mirror and runs four public API cases:
body comparison/passive physics, baseline preflight, pose fences and the actual
saved-composition producer admission regression. Its result binds commands, source
hashes and unchanged copied files; logs retain import and each outcome. It does not
run ENet profiles, graphical focus or all-script compilation. Use foundation checks
separately. The accepted guard-only negative's14 outcome failures are historical
regression evidence, not a recipe to modify the source checkout.

`reexport.py` opens the committed `.blend`, uses the exact export-member manifest,
and requires byte-identical car/track GLBs without images/extensions. It retains
`blender.log` and `fingerprints.json` with private cache/config. Use a fresh external
output by convention: this tool itself permits an existing output and does not
validate outside-checkout placement. It installs nothing. Its exact optional
MeshOptimizer-library diagnostic is allowed and retained; other ERROR/Traceback
lines fail. Source changes still require source/output coordination and separate
Godot refresh/reopen/save; scratch reexport or import cannot synchronize an editor.

Original physics p95 **97/269/401 ms** remains distinct from corrected
normal/adverse **248/380 ms**,20/20 each. Corrected adverse stationary convergence
is **163.215/150.120 ms** after interruption/stall. Zero matching-tick installation
error and update jumps are not prediction corrections; acknowledged speed/heading
changes are not isolated causality, physical input or visible latency. One bounded
window diagnosis had `can_draw=false`, zero drawn receipts. Exact-final acceptance
closes producer P2 and mask-naming P3 only. No command ran for this docs task.
Full S02/S03-R/S04, physical controls/focus, camera/readability/feel, final body/
dimensions/turning/prediction, Steam/Deck/Windows/exports/capacity and P0/M1/production
acceptance remain open. The saved main-editor relocation receipt is time-specific
supplied history, never a current query or authoring lease.

### S03-S stopped compatibility tooling

The [accepted exact-final compatibility record](spikes/s03-s-compatibility.md#accepted-exact-final-compatibility-disposition)
is a stopped source/model/reflection/copied-registration result, not a Steam peer
or selected integration. The [predeclared criteria](spikes/s03-s-compatibility-evidence/criteria.md)
derive from the canonical API's four streams, modes, identities, limits and
cancel/drain requirements. The [full original review](reviews/s03-s-compatibility-review.md)
and complete historical/final/rebase/integration note preserve exact source/result
binding and limitations. Do not repeat the finite model expecting native proof.

Existing reproduction recipes are for a separately assigned bounded check; none
was executed for this docs task:

```sh
# Supply the four exact files named by the saved source manifest:
python3 tools/probe_s03_s_compatibility.py --source-dir /tmp/s03-s-compatibility/sources
# New destination under /tmp; exact pinned engine executable is positional:
python3 docs/spikes/s03-s-compatibility-evidence/run_registration.py /tmp/s03-s-registration-new /path/to/pinned/godot
# Read the complete accepted reviews/checks/handoff/integration without experiments:
git notes --ref=paseo-orchestration show ca38e4fc55b32a379ef7e3bf947e27d4ca8edc4c
```

The [probe source](../tools/probe_s03_s_compatibility.py) requires only `--source-dir`;
there is no `--godot` or `--output` option and no Mise task. It checks all four
[source-manifest](spikes/s03-s-compatibility-evidence/sources.json) SHA256s at immutable
ref `532740f3f9c6a826c68914db81af9de1e32d5dc3` before extracting exact bodies.
It prints JSON facts and finite counterexamples to stdout; it fetches nothing,
imports no Godot and makes no native networking calls. Retain stdout/stderr separately
when reproducing; accepted [probe.json](spikes/s03-s-compatibility-evidence/probe.json)
and [negative hash guard](spikes/s03-s-compatibility-evidence/hash-guard-negative.log)
are historical evidence. The [saved fetch script text](spikes/s03-s-compatibility-evidence/fetch.py.txt)
records four exact public URLs with 30 s download timeouts. It assumes its scratch
source directory already exists and writes scratch `sources.json`; the committed
manifest remains the authority. Historical restricted-DNS/browser failures and
successful public downloads are separate receipts, not permission for a new fetch.

The [registration recipe](spikes/s03-s-compatibility-evidence/run_registration.py)
takes two positional paths, requires a nonexistent destination under `/tmp`, copies
only the addon into a fresh project, sets auto-init false and seeds that copied
project's extension discovery list. Separate XDG data/config/cache and 30 s
subprocess timeouts apply to version and headless reflection/getters. It retains
`version.log`, `registration.log`, full `project/registration.json`, selected API/
commands/returncodes in `registration-selected.json`, and checks22 accepted native
hashes. It verifies exact `4.8.dev7.official.c971f93e7`, GodotSteam4.23 and auto-init
false; the retained getters report default4 channels. No editor/import/all-script
suite, Steam initialization/send, lobby or native lifecycle is exercised.

Accepted [registration data](spikes/s03-s-compatibility-evidence/registration-selected.json),
[original report/retention](reviews/s03-s-compatibility-review.md) and complete
ca38e4f note distinguish original substantive/final/rebase SHAs and bases/counts.
Original empty stdout, raw JSON without terminal newline and retention-check failures
stay byte-faithful. New authored docs use LF; raw historical receipts are not sanitized.

Source inferences and finite freshness/lane-information-loss traces (including the
independent review's1,555 traces) cannot establish actual delivery/reorder/loss,
saturation/send errors, safe payload/MTU, native queue/allocation/work bounds,
authentication/admission, cancel/drain/retry/late callbacks or relay. API presence
and published-byte linkage do not show source bodies executed. Installed-package,
app/tester entitlement, invite/launch/external route, Windows/Linux exports and Deck
input/Gaming Mode/performance remain unproved. Root's existing options are exact
immutable upstream-revision evidence, separately bounded native-boundary design,
or continued unavailability. No adapter/peer/five-lane/reliable fallback/SDK/vendor/
pin selection is made; full S03-S/Steam/Deck/S04/P0/M1/production gates stay open.

### S05 partial damage/chain tooling

[Exact accepted partial S05](spikes/s05.md#accepted-exact-final-disposition) adds a
saved minimum authoritative damage/life/chain fixture, using unchanged S03 session
and S04 body/source APIs. The [single fixture contract](spikes/s05-contracts.md)
owns experimental identities, work, lifecycle and presentation limits.
[Evidence catalogue](spikes/s05-evidence/README.md) maps original protocols,
canonical API/ENet, all-owned compilation, failed/corrected pressure, retired-ShotId
negative and saved-resource receipts. These are historical results, not new checks.

The existing recipes, from the repository root under separately assigned process
access, are:

```sh
python3 tools/run_s05.py --godot /path/to/4.8-dev7/godot --gdstyle /path/to/0.3.0/gdstyle --output /tmp/s05-my-run
python3 tools/run_s05.py --godot /path/to/4.8-dev7/godot --gdstyle /path/to/0.3.0/gdstyle --queue-only --output /tmp/s05-pressure-my-run
python3 tools/s05/check_resources.py --base c8096b55ef97412552366fdaa74c220b976ed82e --output /tmp/s05-resources-my-run.json
# Complete same-reviewer final disposition, lossless payloads and root receipts:
git notes --ref=paseo-orchestration show 754a0b501fe705c93675ff09b43d5bfca201cd94
```

There is no `spike:s05` Mise task. Read the actual
[runner](../tools/run_s05.py), [resource checker](../tools/s05/check_resources.py),
[S04 staging](../tools/run_s04.py), [version/log/user helpers](../tools/script_checks.py)
and [owned-child cleanup](../tools/run_s03.py) for the implemented scope:

| Runner flag | Default and constraint |
| --- | --- |
| `--godot` | Required executable path; shared helper verifies exact `4.8.dev7.official.c971f93e7`, with 10 s version timeout |
| `--gdstyle` | Required executable path; use pinned0.3.0, aligned with `.gdstyle-version`; runner invokes fmt/check and lint, without a separate gdstyle version query |
| `--output` | Printed `s05-` temporary directory if omitted; absent or empty directory resolving outside repository ROOT, nonempty/internal outputs rejected |
| `--port` | 25040, range1–65534; boot uses this port, burst uses port+1, sequentially |
| `--deadline` | 18 s for each three-process ENet case after staging/checks, range1–30 s; not a total runner deadline |
| `--api-only` | Off; runs boot/burst public APIs and queue pressure, omits ENet |
| `--queue-only` | Off; skips both API/ENet rows, runs pressure; takes precedence if both mode flags supplied |

All modes stage saved s02/s03/s04 dependencies and s05 car/boot/burst plus scripts,
with S02/S04 model imports/sidecars. S04 staging removes autoload/editor-plugin
sections and icon reference from copied settings; no addons or Blender authoring
sources are copied. S05 staging excludes editor harness/probe patterns. Headless
import precedes seven explicit S05 script compiles and S05 formatting/lint. It does
not call the all-owned compiler: retained `all-owned-checks` covers48 owned affected
scripts separately, while final seven-script checks cover the proof amendment.
Use the separate [foundation checks](#foundation-validation-tasks) for all-owned
scope; an import alone is neither all-script nor editor-synchronization evidence.

Check/import/compiler operations use `check-user`; each API, queue and ENet role
gets its own XDG data/config/cache scope and stdout/engine logs. Shared checked
commands have 30 s default timeout; API/queue commands use12 s. Default mode runs
boot API then boot ENet, burst API then burst ENet, and finally finite reserved
queue pressure. Each ENet case has actual host/live/post-chain-joiner processes. No proxy, windowed option or drawn
receipt exists in this runner. ENet late launch waits for host `settled`; it does
not test changes during an in-flight car baseline/journal.

The printed directory retains copied project, import/compiler/style logs, per-row
stdout/engine logs and private users, plus `result.json` with commands/source hashes
and available API/network/queue outcomes. Failures keep logs and a failure result;
an early failure may lack completed row/source manifests. Checked commands reject
`SCRIPT ERROR:`, `ERROR:` and `WARNING:` even with exit0; network rows also require
one successful result per role, correct outcomes and zero exits. Each network case
finally terminates only its own Popen children, waits a shared2 s, then kills/waits
remaining owned children. No name/PID scan or shared editor cleanup is performed.

The resource checker is static: `--base` defaults to original experiment base
`c0eda26f7f010af75bbf10c272ec5cb001442331`; the recipe explicitly selects accepted
base `c8096b5`. Required `--output` is a JSON file; its parent is created and an
existing file is overwritten. Unlike the runner, it has no external/fresh-output
guard: deliberately choose a new external filename. It reads Git/base and working
bytes for original technical prefixes, checks three saved scene dependency UID/path/
node identity sets and seven script sidecars, and rejects copied/generated meshes.
It performs no engine/import/reexport/save/reload or gameplay operation; those
historical receipts have separate owners.

Accepted health0/0/100 and twelve terminal outcomes, retired ShotId fences, normal
queue5/46 ticks and finite pressure queue12/tick41 establish scoped gameplay work.
Both twelve-car rows complete144 visits at peak4/tick with8 TOKEN reservations/
4 drops and hidden visuals. They measure no actual effect draw cost. Occupant9001
is a nonrendering sentinel, not an admitted player. Current wreck hydration precedes
input with zero historical tokens only for settled post-chain joining. Full S05
requires source-linked actual eight-effect drawable saturation/live-versus-hydrated
receipts, Regner policy ratification and affected spacing/contact reruns after final
S02/S04 dimensions. Production player/seat/journal/reset/reconnect/sustained load and
all Steam/Deck/input/feel/capacity/P0/M1 gates remain open. Original raw sandbox,
class-index/vector, pressure-timing and editor diagnostics/EOF receipts remain exact;
the full note preserves same-reviewer exact-final ACCEPT partial, P3 resolved and
root's time-specific integration/relocation history. Wrapper metadata additions may
change note hash; decoded original payload hashes establish preservation.

### S06 partial topology tooling

[Exact accepted partial S06](spikes/s06.md#accepted-exact-final-disposition), its
[one bounded contract](spikes/s06-contracts.md), [source handoff](spikes/s06-source-handoff.md)
and [raw catalogue](spikes/s06-evidence/README.md) discover the saved two-sector
intersection, inherited 50° camera comparison, actual immutable S02/S04 bodies,
shared routes/map and stale-data counterexamples. These are historical accepted
receipts; this guide reconciliation executes no tool experiment.

Existing recipes from the repository root, only when separately commissioned:

```sh
python3 tools/s06/run.py --godot /path/to/4.8-dev7/godot --output /tmp/s06-my-run
python3 tools/s06/run.py --godot /path/to/4.8-dev7/godot --content-only --output /tmp/s06-content-my-run
# Current clean committed checkout, existing /tmp parent, new JSON filename:
python3 tools/s06/check_resources.py --base "$(git rev-parse HEAD)" --output /tmp/s06-resources-my-run.json
# Read full final report, manifest, raw checks, condition-MET acknowledgement:
git notes --ref=paseo-orchestration show 7fb302ba2829966c9a687a12a7f00d09ce6a7824
```

There is no `spike:s06` Mise task. The [runner](../tools/s06/run.py) requires
`--godot`, verifying exact `4.8.dev7.official.c971f93e7` with the shared 10 s version
check. Optional `--output` defaults to a printed temporary `s06-` directory; it must
resolve outside ROOT and be absent or empty. `--content-only` is off by default and
is the only mode flag: it retains content/public-role/map/negative checks but omits
body trajectories. There are no port, deadline, windowed or gdstyle runner flags.

All modes copy entire S02/S03/S04/S06 fixture trees and S02/S04/S06 model/import
files into an external project. Copied settings omit autoload/editor-plugin sections
and icon reference. No addon or Blender source tree is staged. Editor-only harness
class dependencies require copied `tools/s01`, `tools/s02`, `tools/s04`, `tools/s06`;
copying the bridges does not execute editor authoring or source export. Import is
headless, 60 s; the proof is a separate headless script invocation, 75 s, only if
import passed. One private `user` XDG data/config/cache scope is shared by these
sequential children, separate from the checkout/editor. Unlike network runners,
there are no simultaneous host/client roles or transport/proxy processes.

[Shared helpers](../tools/script_checks.py) retain merged stdout/stderr in
`import.log`/`proof.log`, with separate `import.engine.log`/`proof.engine.log`.
Nonzero exits or `SCRIPT ERROR:`, `ERROR:` or `WARNING:` in plain/engine logs fail
checked commands. Timeout appends `CHECK DEADLINE EXCEEDED`; `subprocess.run` kills
and waits its own timed-out direct child. This runner has no process-name/PID scan,
shared-editor cleanup or separate group/descendant cleanup guarantee. Version or
early setup exceptions may precede a summary; available logs remain in the output.

`summary.json` records version, import/outcomes, commands, copied source fingerprints,
result availability and unchanged saved fixture/model bytes. Actual checks and full
per-tick body records, when run, are in `project/s06-result.json`, alongside saved
changed-placement/rebake counterexamples. Success requires import/proof success,
unchanged fingerprints, an available result and no semantic failures. The runner
neither invokes gdstyle nor explicitly compiles all owned scripts. Accepted R1
receipts separately establish **47 content checks / ALL58 owned explicit compiles**;
use [foundation validation](#foundation-validation-tasks) for compilation, including
unused scripts. Import is neither all-script compilation nor open-editor synchronization.

The [resource checker](../tools/s06/check_resources.py) requires `--output` as a
JSON file, overwrites an existing file and does **not** create its parent, require
fresh/external output or validate the engine. Choose a new external filename in an
existing directory. Default `--base` is original experiment
`096469f25db2617858d49f88860991c1c84c222e`. It checks new S06 resource/script UIDs,
external dependency UID/path agreement, saved node IDs, no generated/copied render
meshes, GLB member lists/format and source presence. It also compares **every file
in the selected base tree except TODO.md** with working bytes, not just technical
prefixes. Thus this historical recipe is valid only in immutable accepted `7fb302b`
with its unchanged accepted `6c36c12` base files:

```sh
# Historical accepted checkout7fb302b only; not the later reconciled guide tree:
python3 tools/s06/check_resources.py --base 6c36c1232cc2403b6cbac03248ac28006bc83bd9 --output /tmp/s06-accepted-resources.json
```

Later accepted DOC8/9 and checkpoint/guide changes make the original default/base
comparison inappropriate for the current tree. The current-HEAD recipe above
satisfies the guard in a **clean committed checkout**, while checking current
ancestry/dependencies. It does not certify the old base: separately inspect the
exact accepted-base→current changed path/mode/blob set and unchanged working bytes,
allowing only documented Markdown deltas. Never weaken the guard, silently exclude
base files, or describe a current-base comparison as immutable-base preservation.
This task's completion record retains that static docs-only audit, without running
the historical checker or importing/compiling anything.

[Editor-only probe](../tools/s06/editor_probe.gd) `bake_city(path)` calls City's
`bake_content`, saves the external resource, reloads with `CACHE_MODE_REPLACE` and
assigns it; invalid content/save failure is reported. `author_topology` is bounded
editor authoring, `inspect_city` reads validation/map/routes. None is a runtime
rebake path or standalone CLI recipe. Any future mutation needs the assigned editor
lease, saved batch and affected base/inherited refresh/reopen workflow.

Accepted crossing477 ticks/7.95 s and opposing legal LEFT turns721 ticks/12.0167 s
are actual unchanged-body planar/seam evidence, not continuous sweep or final
handling/dimensions/contact acceptance. Larger footprint/camera projections are
geometric sensitivity only. Actual recovery is finite neutralized timeout;
specified blockage/contested junction/stuck/wreck M1-C3 policies are unimplemented.
No drawn runtime/minimap/feel, actual eight-effect saturation, capacity/hardware,
Steam/Deck/Windows/export or P0/M1/production gate is closed by these recipes.
The premeasurement RIGHT→LEFT amendment, crash/recovery and raw failure history
remain retained, as do all359 original/all509 current entries and full reports.

## Current foundation helper discovery — 8 October 2026

This dated supplement supersedes stale *next-prerequisite* discovery above, not the
historical recipes/results or normative workflow. Accepted revisions and exact note
selectors are in [DOC14](reviews/p0-doc14.md); no existing helper is rerun here.
Read helper source before separately commissioning any use. Offline means no engine,
editor, native load or service experiment; it does not mean every archived invocation
is ready on today's checkout.

| Accepted record / current consumer | Existing helper and usable boundary |
| --- | --- |
| [S05 source](spikes/s05-effect-preparation.md) → [saved slots](spikes/s05-saved-presentation.md) | [Resource check](../tools/s05_effect/check_resources.py) is static but writes fixed `/tmp/s05-author-56eb6b28-run04/resource-check.json`; [network check](../tools/s05_effect/check_network.py) launches Godot from fixed run01 mirror. Both are historical tools, not fresh-path recipes. Source/export/slot links can be read directly. |
| [S05 render observation](spikes/s05-render-observation.md) → saved observation camera | [Checker](../tools/s05_draw/check.py) accepts `--output`, optional `--group`/`--base`; absent group checks static preservation, supplied group evaluates retained observations (failed images stay failed). [Budget tests](../tools/s05_draw/budget_check.py) use fake clock/socket/children only. Corrected runner/observer remain runtime-unexecuted; authoring and both graphical groups consumed. |
| [S05 Card I](spikes/s05-vsync-image-observation.md) | [Checker](../tools/s05_vsync_image/check.py) accepts `--output`, optional `--group`/`--base`; [offline tests](../tools/s05_vsync_image/test_offline.py) cover synthetic endpoint/phase/evaluator boundaries without an engine. Corrected lookup coverage is not the missing historical fd/table snapshot. The one import/host attempt is consumed; [runner](../tools/s05_vsync_image/run.py) is not a retry recipe. |
| [S03-S upstream](spikes/s03-s-upstream-peer-evidence.md) / [Valve proposal](spikes/s03-s-valve-api-interface.md) | [Upstream verifier](spikes/s03-s-upstream-peer-evidence/verify.py) and [Valve checker](spikes/s03-s-valve-api-evidence/check.py) inspect committed public-source snapshots and claims. Retrieval/discovery texts preserve historical public reads, not native tests or integration selection. |
| [S07 cards](spikes/s07-run-cards.md) / [driver](spikes/s07-sustained-driver.md) | [Inventory](../tools/s07/inventory.py) takes `--output`/optional `--base`; it binds saved files, not loaded/GPU bytes. [Driver resource check](../tools/s07_driver/check_resources.py) takes output and optional base; [static checks](../tools/s07_driver/static_checks.py) orchestrate style/source checks but overwrite committed historical evidence paths (not a current invocation recipe); [offline tests](../tools/s07_driver/test_offline.py) mutate retained receipts to check analyzer rejection and stage/check the saved closure without an engine. [Analyzer](../tools/s07_driver/analyze.py) takes retained project/output paths; it cannot replace absent interrupted receipts. All historical author/import/development/sustained groups exhausted; do not rerun accepted T. |
| [S08 standard](spikes/s08-standard-editor-release.md), [handoff](spikes/s08-exported-enet-handoff.md), [lifecycle](spikes/s08-release-lifecycle.md) | [Handoff offline](../tools/s08/handoff_offline.py) takes an output path, compiles a C buffering fixture with `/usr/bin/cc` and launches two real logger processes (one via `/usr/bin/stdbuf -oL`) before mocked coordination. It is a historical native fixture experiment, not a compiler-free static recipe; separate appropriate commissioning is required. [Boundary tests](../tools/s08/handoff_boundaries.py) take an output path and use pipes/fake clocks/mock children without a compiler or engine. [Cadence test](../tools/s08/lifecycle_cadence_test.py) checks literal 20 ms owner/import and rejects recorded 10 ms regression. [Analyzer](../tools/s08/lifecycle_analyze.py) takes `--debug`/`--release` retained directories; vanished scratch paths are not available inputs. Restored [diagnostic source](../tools/s08/lifecycle_diagnostic.py) is unexecuted, not a clean release recipe. |

Choose new external output filenames/directories and inspect each helper's output
and immutable-base guards; a helper may assume an existing parent, overwrite a file,
or reject later documentation by design. Do not invent substitutions for historical
private editor/settings/package paths. The upstream/Valve checkers also enforce
historical branch/TODO/scope guards, so the complete old invocation does not pass on
this reconciled branch; Valve's optional `--source-readback` requires original
scratch inputs. Read committed receipts or immutable notes instead of rebuilding
evidence from vanished scratch directories. Offline check
availability neither authorizes runtime nor transfers old acceptance to new bytes.

The preceding paragraph's historical S05/S08 status is superseded by the Windows
supplement below. R/G still require ratified pre-P0 representative preparation, not
M1 completion. Native/API/Steam/device/target/feel/P0/M1 gates remain OPEN.

## Windows workstation tooling — 8 October 2026

The foundation tools now also run on Windows 11 with the Mise-pinned engine
(`mise which godot`). Practical notes:

- `python3` may resolve to the Microsoft Store stub. Mise pins Python 3.14.2 and all
  repository tasks invoke `python`, which is also the direct-command spelling on Windows
  and Linux. Put the pinned engine and gdstyle directories on `PATH`; do not use an
  auto-installing Godot shim in place of Mise's binary.
- `script_checks.environment()` redirects `APPDATA`/`LOCALAPPDATA` as well as XDG,
  because Godot on Windows ignores XDG. Without this, host/client user directories
  overlap and S05's base import aborted its scan.
- UDP proxies ignore Windows `ConnectionResetError` reports caused by earlier
  ICMP port-unreachable sends.
- Windows runs write CRLF raw logs; Git normalizes committed evidence to LF.
- Headless Windows pacing is slower and burstier than windowed runs. Use windowed
  runs for response/feel numbers and physics-frame waits for tick-sensitive
  harness steps.
- Windowed measurement runners must carry an explicit 60 FPS cap. Shared
  `tools/window_safety.py` guards exact cap construction and rejects withdrawn or
  incorrectly capped modes; fixture VSync defaults are not treated as the safety boundary.
- Quiet timing runners collect task-list, PowerShell/CIM/Get-Counter, or equivalent
  workstation snapshots only after the measured child exits, followed by an explicit
  one-second settle before another case can launch. Such snapshots are post-case context
  and do not prove that the timed window was uncontended.
- `tools/measurement_identity.py` records the repository commit/tree/dirty state,
  fingerprints the runner, imported helpers and declared staged inputs, and retains
  `sys.argv`, the runner working directory and effective parameters. Measurement receipts
  use this shared shape rather than each runner implementing a partial identity format.
- Polling runners use retained byte offsets for growing logs. They decode only complete
  appended lines, so polling work does not grow with all previously retained output.

New Windows runners take `--output` outside the checkout and fail on their scoped
diagnostics/process criteria. Their source-binding behavior differs: S08 stages committed
bytes with `git show`; S05 draw and S07 graphical copy staged paths from the working tree
and reject dirty copied inputs. The existing S03-R/S04 windowed runners copy working-tree
inputs without that dirty-input rejection, so commit identity alone does not bind those
copies.

| Tool | Scope |
| --- | --- |
| [S08 Windows observation](../tools/s08/windows_observation.py) | Verifies the 4.8-dev7 TPZ (`--templates`), exports the saved S08 main for Windows release/debug and runs one 20 ms host/client set per mode. [Record](spikes/s08-windows-observation.md). |
| [S05 Windows draw](../tools/s05_draw/observe_windows.py) | Windowed host/live/settled-late draw observer: burst, expiry and hydrated frames. [Record](spikes/s05-windows-draw.md). |
| [S07 graphical T](../tools/s07_graphical/run.py) | Accepted sustained driver plus per-frame telemetry, now 60-capped only; retained historical evidence includes the withdrawn uncapped failures. [Record](spikes/s07-graphical-t.md). |
| `run_s03_r.py`/`run_s04.py --windowed` | Existing runners; real drawn receipts on Windows. |

### Safe capped GPU measurement

Do not run uncapped rendering on a workstation where an uncapped attempt has caused GPU
reset or device removal. In particular, the current RTX 4070 Laptop GPU workstation has
two retained uncapped S07 device removals; an uncapped maximum-FPS or headroom run is not
an acceptable validation method there.

For a bounded graphical measurement:

1. Set the intended FPS cap before loading measured content. For the 60 FPS fixtures,
   disable VSync explicitly and set `Engine.max_fps = 60`; record both effective settings.
2. Enable viewport timing with
   `RenderingServer.viewport_set_measure_render_time(viewport_rid, true)`. After each
   `RenderingServer.frame_post_draw`, sample
   `viewport_get_measured_render_time_cpu(viewport_rid)` and
   `viewport_get_measured_render_time_gpu(viewport_rid)`. Also sample monotonic wall-clock
   frame intervals; renderer timings do not include every presentation or pacing delay.
3. Warm shaders and content before selecting samples. Retain raw samples and report
   p50/p95/p99 rather than only an average. Keep the run deadline and resource stop limits
   bounded.
4. Record the exact engine, renderer/API, adapter, window and render resolution, quality
   settings, cap/VSync state, content case, process exits, and diagnostics. Count concurrent
   Godot processes immediately around the run and label timings contended when any unrelated
   processes remain.
5. Treat GPU time below the capped frame budget as renderer-work headroom for that exact
   content and quality only. It is not an uncapped throughput, end-to-end presentation,
   power, thermal, or other-device result. Use named capped quality/content sweeps when a
   comparative headroom curve is required.

The [S08-C record](spikes/s08-c-stability.md) applies this method to the current
no-cutaway S07 environment and preserves the non-reproduced 384-block crash diagnosis.
Changing the product frame-time instruction from uncapped to this method remains an owner
question; do not silently reinterpret `docs/design.md`.

## Versions and releases

When release builds exist, make version and source revision visible in startup
logs and the UI. Package build metadata at export time so the exported build reports
its actual revision and dirty status. Keep build identity distinct from protocol
and content compatibility; matching display versions alone prove neither.

Install templates matching the exact engine pin. Exclude tests, authoring sources,
review captures, and development MCP tooling from production exports while retaining
required native dependencies. Test the complete exported folder on each target OS,
including launch, renderer, input, audio, networking, and native extension loading.
Record build/version, hardware, renderer, settings, and results. Upgrade the engine
deliberately and rerun affected import, identity, addon, gameplay, and export checks.

Publishing a build, activating a distribution branch, and proving installation
are separate stages. Keep rollback builds available. Keep version/tag operations
explicit and avoid tools that silently commit unrelated work.
