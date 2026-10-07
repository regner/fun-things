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
pins through Mise; `GODOT_BIN` and `GDSTYLE_BIN` can select those same binaries when
Mise trust-state writes are unavailable. `tools/check.py` checks versions and honors
hidden/`.gdignore` trees, excluding the two current vendor addons explicitly.

| Task | Scope |
| --- | --- |
| `mise run gdstyle:check` | Every discovered owned `.gd`, pinned lint with zero warnings; comments/export/function spacing still reviewed manually |
| `mise run gdscript:check` | Explicit `--check-only --script` invocation for every owned script, including unused scripts; retains per-script logs |
| `mise run resources:check` | S01 source/export links, unique resource UIDs, external files/no copied meshes, engine dependencies and UID/path agreement, dimensions/axes/sockets/clips, saved IDs/transforms/inheritance |
| `mise run s01:reexport` | Opens both committed Blender sources with the selected Blender version, exports validated scratch GLBs and requires byte equality with committed outputs |
| `mise run s01:clean` | Isolated asset-profile clean import and resource checks, compares persisted files, then proves focused corruptions fail |

Logs default to ignored `builds/`; subprocesses have deadlines/private user dirs
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
P0-03 responsibility; no network runner is included in S01. Import remains separate:

```sh
mise exec -- godot --headless --editor --path . --import
```

An import command's success does not mean scripts compiled or logs were clean.

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
