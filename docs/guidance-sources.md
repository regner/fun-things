# Guidance sources and adaptation

The reusable guidance comes from the sibling Godot project
`~/Development/vcs`, reviewed on 7 October 2026. This checkout retains working
conventions and lessons that apply beyond VCS's vehicle combat game. It does not
depend on the sibling checkout at runtime or require its tooling to exist here.

## Source coverage

| VCS sources | Reusable guidance | Destination |
| --- | --- | --- |
| `AGENTS.md`, `README.md` | MCP-first editing, simplicity, ownership, style, saved identities, layered checks | `AGENTS.md`, development guide |
| `mise.toml`, `gdstyle.toml`, `.github/workflows/gdscript.yml`, compiler/style/resource tooling | Pinned dependencies, owned/vendor scope, all-script checks, resource integrity, matching local/CI tasks | Development guide |
| `docs/project-review.md` | Exact input types, shared formulas/IDs, restored telemetry, observer ordering, independent regression expectations, honest check limits | Repository and multiplayer guidance |
| `docs/art-pipeline.md`, pipeline audit/inventory | Saved-source ownership, import ancestry, scene placement authority, compact resources, source/export consistency, clean export contents | Asset and development guides |
| `docs/valley-level-design.md`, asset production/integration, playtest records | Measured dimensions, origins, collision contracts, real actor/camera checks, material conventions, profiling limits, explicit integration ownership | Asset guide |
| `docs/beauty-review/astra-review.md` | Comparable review cameras, visual hierarchy, preserve gameplay envelopes, distinguish screenshot evidence from runtime behavior | Asset guide |
| `docs/multiplayer-first-pass.md`, `docs/client-prediction-plan.md` | Session/match boundaries, admission, stale state, input bounds, simulation acknowledgement, replay, host-stall recovery, real-process tests | Multiplayer guide |
| `docs/destructible-environments.md`, `docs/street-props.md` | Stable world IDs, persistent baselines, deferred collision revisions, cosmetic effects, prediction limits | Asset and multiplayer guides |
| `docs/weapons-first-pass.md`, `art/audio/README.md` | Controller-independent APIs, atomic replacement, reliable equipment, projectile events, lifecycle cancellation, feedback ownership, licenses, bounded voices | All three guides |
| `docs/steam-private-testing.md`, release/version sections of `README.md` | Matching templates, complete exports, packaged revision, platform testing, separate upload/activation/installation stages | Development and multiplayer guides |
| `TODO.md` | Keep tasks actionable; completed work leaves the active list; outstanding gameplay issues are evidence for acceptance cases | Repository guidance |

Bundled addon manuals describe the addon rather than general project policy.
Use the installed toolkit's own documentation when operating it; upstream addon
formatting and lifecycle behavior remain separate from project-owned code.

## Adaptation decisions

- Preserve editor synchronization, single ownership, shared simulation rules,
  meaningful identities, bounded networking, and evidence-based validation.
- Generalize scene paths, components, naming, spawn policy, collision masks, and
  gameplay examples. Choose the concrete ownership map when this project has systems.
- Require ENet for local testing and Steam for friends playtesting on this project's
  existing app. Choose/pin the Steam integration through a technical proof; keep
  provider details behind the shared session boundary. A listen server remains a
  starting recommendation; dedicated servers and host migration remain deferred.
  Prediction needs feel/network evidence; car destruction is required by the product.
- Keep VCS's rates, player capacity, payload limits, and replay sizes as examples.
  They do not establish this project's performance or protocol requirements.
- Require Blender-authored visible 3D models and linked explicit exports, including
  blockouts and spike fixtures, following Fun Things' product requirements. This
  supersedes the initial adaptation that allowed primitive/procedural render meshes.
  Collision, navigation, occlusion data, and debug overlays remain separate.
- Retain documented style and manual review. The existing gdstyle configuration
  does not include VCS's custom spacing/documentation wrapper or its smoke tests.
- Describe compiler/resource/art checks and CI as future tooling. Copying task names
  without their implementations would create a misleading development workflow.
- Keep TODO updates with the resolving work without imposing VCS's automatic
  commit requirement. Do not copy its version-bump commit/tag side effects.
- Omit VCS assets, maps, exact gameplay tuning, Steam identities/credentials,
  branch/depot configuration, measured benchmark results, and project-specific defects.
  Extract the general acceptance cases from defects instead.

Some VCS documents retain superseded plans: old engine pins, targets later removed,
initial no-prediction behavior, earlier admission/interpolation designs, and retired
level rebuild utilities. Current ownership and implemented follow-ups take precedence
over those historical sections. New guidance avoids treating either historical
checkpoints or VCS's acceptance results as implemented behavior here.

## Primary documentation

Godot API and import details were checked against official documentation. This
project pins a development engine, so verify exact API behavior against that engine
when implementing; stable documentation is a baseline rather than the version pin.

- [Godot high-level multiplayer](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)
- [Godot MultiplayerSynchronizer](https://docs.godotengine.org/en/stable/classes/class_multiplayersynchronizer.html)
- [Godot version control guidance](https://docs.godotengine.org/en/stable/tutorials/best_practices/version_control_systems.html)
- [Godot 3D import formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html)
- [Valve Steam Datagram Relay](https://partner.steamgames.com/doc/features/multiplayer/steamdatagramrelay)
