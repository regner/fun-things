# Repository guidance

Use this guidance for project-owned code and assets. Preserve third-party addon
formatting and contracts unless the task explicitly changes them. The longer
guides are [development](docs/development.md), [assets](docs/assets.md), and
[multiplayer](docs/multiplayer.md).

## Working approach

- Prefer the simplest implementation that meets the current requirement. Add
  abstractions, caches, or optimization when a demonstrated limitation warrants
  them, and record the reason. Keep complexity local.
- Inspect the affected subsystem, callers, serialized data, and tests before
  changing it. Search for existing rules before adding a second implementation.
- Give each gameplay rule and state transition one owner. Keep shared values
  with that owner rather than in a global collection of unrelated constants.
- Call down, signal up: parents coordinate children through their public APIs;
  children emit events instead of depending on a particular parent or sibling.
  See [development](docs/development.md#godot-scene-and-script-conventions) for
  scene boundaries, explicit dependency injection and other Godot conventions.
- Separate input collection, simulation, network replication, and presentation.
  Standalone, authoritative simulation, and prediction must share equivalent
  gameplay rules. HUDs and visual effects consume state; they do not decide it.
- Preserve Inspector exports, public APIs, serialized property names, and saved
  identities unless the requested change requires a coordinated migration.
- Keep behavior-preserving cleanup separately reviewable from behavior changes.
  Avoid unrelated refactoring. Update contract documentation when behavior changes.
- Keep branch history linear. Update from `main` by rebasing; do not create merge commits.

## Editor workflow

- Prefer Godot MCP Toolkit tools for editor-managed scripts, scenes, resources,
  and project settings when a suitable tool is available. Discover and inspect
  the relevant tools and affected editor state before making mutations.
- Make scene/node changes through editor tools. Save each mutation batch before
  switching scenes or playtesting; verify both editor state and the saved diff.
- If editor tools are unavailable or insufficient, explain the limitation before
  a direct-file fallback. Preserve unsaved work, then refresh external files and
  reload/reopen affected scenes before further saves or playtests. A filesystem
  scan or headless import does not prove a separate open scene is synchronized.
- Direct filesystem edits are appropriate for documentation and repository tools.
- Author UI, 2D and 3D node composition, layout and placement in saved scene files.
  Runtime code instantiates those scenes and supplies data/state; it must not build
  authored node hierarchies or overwrite editor placement. This includes menus,
  HUDs, reusable widgets, actors and effects. Document intentional procedural systems.

## GDScript style

- Use type hints, tabs, LF endings, and a 100-character line target. Use the pinned
  gdstyle configuration for member ordering and automated formatting.
- Give every named function a concise `##` purpose or contract comment immediately
  above its declaration, before annotations such as `@rpc`. Include callbacks,
  private helpers, and test helpers. Prefer named callbacks for meaningful behavior.
- Explain intent and constraints inside functions; avoid narrating statements.
  Preserve useful rationale and lint directives.
- Separate functions with two empty lines. Use one empty line between logical
  steps and after completed control blocks before unrelated following statements.
  Keep related assignments together and `elif`/`else` attached to their `if`.
- Separate `@export_group` and `@export_subgroup` blocks with an empty line.
  Review these spacing rules manually until a preserving formatter wrapper exists.
- Name significant thresholds, tuning factors, durations, collision masks, limits,
  and protocol values. Use constants for fixed values and exports for Inspector
  tuning. Include units where helpful and use engine enums instead of raw integers.
  Obvious zero/one values, indices, and explicit vector/color data need no wrappers.
- Preserve behavior during style changes, especially authority checks, ordering,
  numerical values, and serialized names. Split meaningful steps rather than
  compressing code to satisfy complexity limits.

## Saved resources and source assets

- Create visible 3D models in Blender, including blockouts and spike fixtures.
  Keep committed sources and explicit exports linked through imported model
  instances. Do not add generated render meshes; see [assets](docs/assets.md).
- Generated road infrastructure is the one exception (owner decision 42). The
  Blender-only rule exists to stop composing scenes from code; procedurally generated
  road content that is edited and visible in the editor is acceptable. Road, sidewalk,
  curb, procedural-intersection and crosswalk-marking surfaces may be generated from
  the saved road network by the pinned road addon and project road scripts, in the
  editor and at level load, with materials/textures from committed sources. Reusable
  fixtures (signals, street lights, signs, barriers, prefab intersection pieces) remain
  Blender-authored linked assets placed by the road tool. Road edits never require
  Blender. All other visible 3D models keep the Blender-only rule, and runtime code
  still must not compose authored scene hierarchies.
- Preserve scene/resource UIDs, dependency UIDs, editor-generated node identities,
  inheritance identifiers, required `.uid` sidecars, and source `.import` files.
  Commit these with the resources they describe. Keep `.godot/` untracked.
- Import new assets with the pinned engine, save project-owned scenes/resources
  through Godot, and inspect dependency resolution and saved IDs. Test affected
  inherited scenes through an editor save/reload roundtrip.
- Edit source assets and re-export their outputs together. Keep imported model
  instances linked to their sources; inspect unexpected embedded mesh data.
- Keep visual decoration separate from gameplay collision. Collision changes
  require affected movement, query, and multiplayer checks.

## Multiplayer invariants

For an authoritative host/server model, apply these rules from the first prototype:

- Clients submit intent. The authoritative process owns outcomes, spawning,
  damage, inventory/pickups, respawning, and persistent world mutation.
- Derive remote identity from the RPC sender, validate admission and ownership,
  and reject malformed values at the network boundary. Bound packet sizes,
  request rates, queues, history, and per-tick processing work.
- A driver's input ownership is separate from Godot multiplayer authority and
  scene `owner`. Configure simulation ownership before nodes enter the tree,
  including child scripts, so replicas cannot mutate gameplay during `_ready`.
- Use session identities, entity generations, and relevant state revisions to
  reject obsolete input and state. Do not let movement overwrite reliable
  lifecycle, equipment, health, or world state.
- Late joiners receive current authoritative state before admission. Apply
  dependent collision/lifecycle state before movement or prediction that needs it.
- Prediction replays only permitted local simulation. Suppress authoritative
  mutation and duplicate effects during replay. Authoritative corrections win.
- Complete lifecycle transitions before publishing them: stop stale commands,
  restore authoritative component state, update collision/presentation, then
  notify observers. Clear history and callbacks on teardown.
- Use one replication writer per state field. Test gameplay over real separate
  processes; validate each platform transport independently.

## Validation and task records

- Run checks appropriate to the change: formatting/lint, compilation, saved
  resource checks, affected gameplay/network tests, and visual review as needed.
  Do not claim an unavailable task ran or treat import alone as all-script validation.
- Assert outcomes through production APIs. Protect important contracts with
  independent expectations rather than copying implementation formulas into tests.
- Review runtime logs as well as exit status. Distinguish environment failures,
  known diagnostics, and new errors; avoid broad error suppression.
- Keep future tasks actionable. Remove completed items from a TODO list and keep
  the update with the resolving change. When a TODO is completed, commit its removal
  from `TODO.md` together with the changes that completed it.
- Report what changed, what was checked, and any material limitations. Keep current
  behavior distinct from historical plans and proposed work.
