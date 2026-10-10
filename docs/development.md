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

Every tracked project-owned `.tscn`/`.tres` must save its header UID and every external
resource UID; every owned scene node must retain Godot's `unique_id`, except an
`instance_placeholder` declaration for which the engine may omit it. Every tracked
owned `.gd` has a tracked `.gd.uid`. `python tools/saved_identity_check.py` enforces
these rules outside `addons/`, `prototypes/`, and `docs/` and reports exact source
lines; the canonical production checks run it as a required layer.

When normalizing a resource, first warm the UID cache with the pinned engine, then save
through an editor-mode process and repeat the save to prove stable bytes:

```sh
timeout 300s godot --headless --editor --path . --import --quit
timeout 180s godot --headless --editor --path . --script <reviewed-save-tool>
```

Inspect the resulting header, dependencies, node IDs, and diff. A cold-cache
`ResourceSaver` run may silently omit dependency UIDs, so it is not an acceptable
substitute for this sequence.

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

## Prototype archive

Completed foundation fixtures, their runners and spike-only art are retained under
[`prototypes/`](../prototypes/README.md). The archive is hidden from Godot by `.gdignore`, excluded
from exports, and not runnable in place. Use it for implementation reference or restore a complete
old checkout at the commit recorded in its README. Production code and current checks must not load
resources from that tree.

Repository Python tests now cover production tools only. Production gameplay tests use GUT under
`tests/unit/`; `tests/diagnostic/` owns intentional framework-failure checks. Focused runnable asset
checks live under `tests/assets/`.

## Canonical production checks

Run the complete production check from the repository root with the exact Mise pins:

```sh
export PATH="$(dirname "$(mise which godot)"):$(dirname "$(mise which gdstyle)"):$PATH"
python tools/production_checks.py --output /tmp/ft/production-checks
```

On Windows, use a fresh directory such as `C:/tmp/ft/lanes/<lane>/production-checks`.
The entrypoint requires engine version `4.8.dev7.official.c971f93e7`, then runs owned-script
formatting, zero-warning lint and explicit compilation, complete Python unittest discovery,
a clean headless test-mirror import, and the test-only GUT suite under `tests/unit/`. It also
runs the isolated intentional GUT failure under `tests/diagnostic/` and passes that check only
when GUT exits nonzero with the expected failure marker. Logs, JUnit XML and a JSON summary stay
in the external output directory. To run one unit-test owner subtree while retaining the other
canonical layers, select it explicitly:

```sh
python tools/production_checks.py --gut-dir tests/unit/session \
  --output /tmp/ft/production-checks-session
```

GUT is pinned to v9.7.1 under `addons/gut/`; its editor plugin is not enabled. Vendor scripts
are excluded by exact path from project-owned style and compile discovery, while production and
test scripts remain covered. Export presets exclude `addons/gut/**` and `tests/**`, and the
package inspector rejects either path. The GitHub Actions workflow can run the same entrypoint on
Windows and Linux through `mise.toml`; it is currently manual-only (`workflow_dispatch`) and does
not run on pushes or pull requests. Local Linux execution remains required when a Linux machine is
available rather than inferred from Windows.

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

The project has a saved `scenes/boot/boot.tscn` entrypoint and four x86-64 presets:
Windows/Linux, debug/release. The ENet-only M1 project no longer contains GodotSteam;
the presets exclude MCP and the package inspector still rejects any GodotSteam or
Steamworks library accidentally reintroduced. A future Steam-adapter task must select a
pinned release, add and enable its plugin deliberately, then decide and test export
inclusion. The exact template hashes, bounded commands, package inspector, Windows smoke
and Linux launch checklist are in [S08-X](spikes/s08-x.md). Use matching pinned
4.8-dev7 templates, fresh external output directories and the documented timeouts.

## Windows workstation tooling

Use Mise's pinned `python`, `godot` and `gdstyle` executables on Windows. Redirect both
`APPDATA`/`LOCALAPPDATA` and XDG data/config/cache roots for isolated Godot children. Write runner
outputs outside the checkout, inspect runtime logs as well as process status, and stop only children
started by the current command. Windows logs may be written with CRLF; committed text is normalized
to LF.

For graphical measurements, set the intended FPS cap before loading measured content, retain raw
samples and effective renderer/VSync/cap settings, and record unrelated-process contention. Never
substitute an uncapped workstation run after device-removal or reset evidence.

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
