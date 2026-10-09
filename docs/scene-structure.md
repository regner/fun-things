# Scene and authored-resource contracts

P0-02 draft, 7 October 2026. These paths and node contracts guide production composition.
M1-A1.1 now implements the Boot, main-menu and session-status scenes; later rows remain
reserved until their owning production task lands. Isolated [S01 fixtures](spikes/s01.md)
exercise linked imports and wrapper-level material inheritance. The isolated
[S03 fixture](spikes/s03.md) uses fixed Boot/Session and Match/Replication paths
with saved marker entities and a saved local rig. Create directories only when
their first resource is needed. [Architecture](architecture.md) owns responsibilities;
[API contracts](api-contracts.md) owns identity/data/lifecycle. S01/S06 refine the
resource and topology details before P0-GATE.

## Production layout

| Path | Purpose and lifetime |
| --- | --- |
| `res://scenes/boot/boot.tscn` | Main scene; process-lifetime Boot and services |
| `res://scenes/ui/main_menu.tscn`, `session_status.tscn` | Reusable main menu and connection/loading/error UI; settings moves to M1-D5 |
| `res://scenes/match/match.tscn` | One active Match; authoritative simulation or client replica |
| `res://scenes/world/district_01.tscn` | Saved CityRoot composition, fully loaded in M1 |
| `res://scenes/world/sectors/<sector_id>.tscn` | Saved sector composition with prefab instances and authored anchors |
| `res://scenes/prefabs/buildings/<type_id>.tscn` | Separate reusable scene per building type; repeated instances stay linked |
| `res://scenes/prefabs/{roads,sidewalks,props}/<type_id>.tscn` | Static kit wrappers around linked imports and deliberate collision |
| `res://scenes/entities/{player,pedestrian,vehicle,projectile}.tscn` | Dynamic gameplay entities, never world-placement writers |
| `res://scenes/local/local_rig.tscn` | One input/camera/HUD/minimap rig per process in Match |
| `res://scenes/effects/<effect_id>.tscn` | Bounded cosmetic effects with imported mesh carriers where required |
| `res://scripts/{session,match,actors,vehicles,combat,world,local,settings}/` | Scripts grouped by their state owner; UI scripts may live beside UI scenes |
| `res://resources/{weapons,vehicles,population,world}/` | Immutable tuning/definitions, authored topology and derived data |
| `res://art/source/` | Committed `.blend` authoring files under `.gdignore`; excluded from runtime export |
| `res://art/models/` | Explicit GLB exports plus source `.import` settings linked to source records |
| `res://art/{textures,materials,audio}/` | Runtime art and provenance; conventions follow [assets](assets.md) |
| `res://tests/fixtures/<spike_id>/` | Isolated proof scenes/resources; not production exports |

## Required tree and node boundaries

```text
/root/Boot                         boot.tscn, Node; never replaced during a session
├── Session                        SessionService and fixed admission RPC endpoint
└── View                           Control; contains MainMenu/SessionStatus or Match
    └── Match                      match.tscn, Node3D; fixed name on every peer
        ├── Replication            match RPC endpoint and replica state application
        ├── CityRoot               district_01.tscn instance, authored placement
        │   └── Sectors
        │       └── <sector_id>    saved sector instance
        │           ├── Geometry  building/road/sidewalk/prop prefab instances
        │           ├── Anchors   spawns, parked-car/population and route references
        │           └── Derived   navigation/occlusion references, if chosen
        ├── RuntimeEntities       host-created entities, names e_<id>_g_<generation>
        ├── RuntimeEffects        cosmetic instances; no authoritative collision
        └── LocalRig              exactly one local_rig.tscn instance
            ├── Input             intent collection and focus handling
            ├── CameraAnchor      local smoothed follow transform
            │   └── Camera3D
            └── UI                CanvasLayer with HUD, Minimap and local menu
```

M1-A1.1 saves `Boot/Session` and `Boot/View/{MainMenu,SessionStatus}` and uses no
project autoload for them. LocalSettings and its settings screen are intentionally absent until
M1-D5. Menu children replace Match only after session cleanup. Session exists before
attaching a peer so handshake messages have an endpoint while Match loads.
Match/Replication exists before world-ready is sent; do not send match RPCs before
that readiness. Admission messages use `/root/Boot/Session`; match messages use
`/root/Boot/View/Match/Replication`. Keep gameplay RPCs on these fixed endpoints,
not dynamically named entity children. Both peers must use matching paths and RPC
declarations, as required by [Godot high-level multiplayer](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html#remote-procedure-calls).
S03 checks these paths in separate processes.

Boot/Session holds provider nodes internally, without exposing their child paths to
gameplay. No production code depends on the development MCP autoload. Do not add
project autoloads until a concrete process-lifetime need cannot live under Boot.
All sectors initially load together; culling does not unload gameplay/navigation.
Streaming or runtime city reconstruction requires a separate measured decision.

## Prefab and entity interfaces

| Scene family | Required local paths / metadata | Allowed overrides |
| --- | --- | --- |
| Static kit/building | Root `Node3D`; `Visuals/Model` is an imported GLB instance; `Collision` contains deliberate static bodies/shapes; `Sockets` when used | Instance root transform and stable world ID in sector; documented material/sign variants |
| Player/pedestrian | S02-selected physics root; `PresentationAnchor/Visuals/Model`, `Collision`, `Motion`, `Health`; player additionally has `Sockets/WeaponMount` and `Weapons` | Definition/appearance and component tuning; no root/body type change without contract update |
| Vehicle | S04-selected physics root; `PresentationAnchor/Visuals/Model`, `Collision`, `Motion`, `Health`, `Sockets/DriverSeat`, `Sockets/EntryLeft`, `Sockets/EntryRight`, `Sockets/ExitLeft`, `Sockets/ExitRight` | Vehicle definition/color/model variant and reviewed collision; seat/control state is runtime-owned |
| Weapon visual | Imported model wrapper; `Sockets/Muzzle` points local -Z along the firing direction | Model/material variants preserving mount/muzzle contract |
| Projectile | S05-selected simulation root; `Visuals/Model`, contact/query component | Projectile definition; authority and shot ID configured before tree entry |
| Effects | Root with bounded lifetime; imported draw geometry if 3D meshes are used | Cosmetic parameters only; cannot apply damage or allocate gameplay shots |

Component paths are prefab-local contracts, not global lookup paths. Resolve them
on instantiation and fail usefully for missing required children/sockets. Attach
WeaponState to player actors; weapon visuals bind to the authored WeaponMount pose
under PresentationAnchor so they receive the same display smoothing as the actor.
Gameplay muzzle/seat/exit queries use physics pose and authored socket-relative
transforms, never a smoothed presentation transform. Pedestrians have no M1 weapons.
Sockets use metres, +Y up, -Z forward; S01 verifies imported socket orientation.
For a physics-body root, `Collision` is a direct CollisionShape3D child; additional
shapes also remain direct children of the body. Static wrappers use a `Collision`
container with static bodies and their direct shape children. The exact body classes
and rig/animation names remain S01/S02/S04 decisions, not implied by this table.

Reserve named collision roles `World`, `Actor`, `Vehicle`, `Wreck` and query-only
`Interaction`. S02/S04 choose project layer bits and body/query masks explicitly;
spawn/exit clearance includes solid world/actor/vehicle/wreck roles and excludes
cosmetics/interaction triggers. Damage queries include eligible damageable bodies
and occluding world collision. The selected masks live with their query owner;
visuals/effects never add gameplay collision implicitly.

Keep physics, PresentationAnchor smoothing, and model animation transforms separate.
Dynamic imported models are children of PresentationAnchor; static models use the
unsmoothed `Visuals/Model` path. Animation changes descendants of Model only.
Presentation must not move Collision to smooth a replica. DriverSeat and exit markers
are candidate poses, not permission to teleport into occupied space. Gameplay
clearance queries decide whether an authored candidate is usable.

## Authored identity and topology

Saved sectors assign unique district-scoped `world_id` values to gameplay-relevant
anchors/objects. Use explicit StringName properties with namespaced strings such as
`district_01/sector_02/spawn_03`. Repeated prefab instances receive distinct IDs in
their sector; a prefab's asset/definition ID is not its placed-object identity.
Decorative instances need no gameplay ID. Runtime entity IDs are allocated by Match
and link to an optional origin world ID; moving a car never moves its spawn anchor.

Sector IDs, road/link IDs, spawn IDs and source/import UIDs are distinct identities.
Do not derive gameplay identity from NodePath, sibling index or local instance ID.
Preserve explicit IDs through reparenting and model replacement. Deliberate identity
changes update links/content compatibility together. Editor-created resource UIDs,
node/inheritance metadata, `.uid` sidecars and `.import` files remain preserved.

CityData references saved anchor/world IDs and owns connectivity; it cannot become
a second placement writer. Derived navigation/minimap data records district ID,
topology revision, geometry/anchor fingerprint and bake-tool version. On stale/missing
data, editor validation fails and play/join reports `CONTENT_INVALID`; do not silently
rebake or shift geometry at runtime. S06 chooses the graph/navmesh/curve representation
and fingerprint method. The minimap projects shared road data onto world XZ; it
does not maintain a separately drawn street layout.

The initial dynamic descriptors refer to world anchors plus entity definition IDs.
Host runtime spawning/reset uses those descriptors and checked clearance. No script
recreates buildings, roads or authored sector transforms during `_ready` or reset.
One world integrator owns each shared district/sector file; independent contributors
work on distinct prefabs/source assets and hand them off for placement.

## Instantiation, inheritance and validation

Instantiate off-tree; validate definition IDs and required paths, assign EntityRef,
simulation role, participant/controller binding and revisions on the root and
children, then add to RuntimeEntities. Keep Godot multiplayer authority on the
server for gameplay bodies. Scene `owner` controls serialization and is not input
or simulation authority. Replicas begin with gameplay disabled even during `_ready`.
Install lifecycle/equipment/health/collision before movement, then bind the local rig
once baseline application succeeds. Spawn fails atomically if any required setup fails.

An inherited prefab may override exported tuning, approved materials and collision
variants. S01 accepts exported wrapper-level material tuning on the current engine
pin; direct editable imported-child overrides changed serialized child identities
and are not accepted by that proof. The fixture appearance script applies its
saved parameter to the linked mesh after tree entry, without changing placement.
Production component/body/socket APIs remain their own downstream contracts.
Preserve required paths/sockets and imported ancestry. Do not duplicate
embedded model vertex data, detach the model import or silently change a saved ID.
Reexport the source and outputs together; reopen/save affected base and inherited
scenes through Godot to check overrides, identities and authored instance transforms.

[S01 evidence](spikes/s01.md) covers repeated instances, a wrapper-level inherited
material variant, source reexport and saved wrapper/resource/node identity. The
asset-profile clean import excludes development/Steam plugins in the temporary
copy; full-project import still has recorded addon/editor diagnostics. No engine
pin change or direct imported-child identity acceptance is implied.
S02/S04 check actual actor/camera/vehicle clearance; S06 checks
two-sector seams, routes and map alignment. The [S03 proof](spikes/s03.md)
checks fixed RPC paths, pre-tree marker ownership and exactly one saved local rig
per process. Its rig has Input, CameraAnchor/Camera3D and UI placeholders; no device,
camera-follow or HUD behavior is claimed. Empty CityRoot/marker entities introduce
no visible models or collision fixtures. S01 provides P0-03's asset/resource
checks through the [development tasks](development.md#foundation-validation-tasks). Use the [asset workflow](assets.md) for handoffs/catalogue conventions;
S01 records export/import settings and their roundtrip.

## Prototype and test boundaries

Foundation spike scenes, scripts and art are archived under [`prototypes/`](../prototypes/README.md).
That tree is reference-only, carries a top-level `.gdignore`, and is excluded from exports. Historical
`res://tests/fixtures/...`, `res://tools/...` and spike-art paths inside the archive are not current
project contracts.

Production GUT coverage lives under `tests/unit/`; intentional GUT failure diagnostics live under
`tests/diagnostic/`. Runnable production-asset inspection scenes live under `tests/assets/` and remain
project-owned checks. New gameplay composition belongs under `scenes/` and `scripts/`, not under a
foundation fixture tree.
