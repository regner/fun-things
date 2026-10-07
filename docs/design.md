# Fun Things — product brief and validation envelope

Ratified product scope, 7 October 2026. **P0-01 is complete under the review decisions
recorded below.** This describes the first playable milestone (M1), not implemented behavior.
The required experience and transport paths come from [the plan](../TODO.md).
Confirmed during this review: Steam Deck LCD at native 1280×800 is the performance
baseline, 60 FPS is required on LCD and OLED, and graphics should be stylized rather
than realistic. Regner identified `../vcs` as the source of the existing Steam IDs.
Regner approved the remaining draft scope/gameplay defaults on the same date,
with budgets provisional and the engine pin open for the Deck proof. Live Steamworks
setup is explicitly deferred to the relevant proof, rather than blocking this brief.
Budgets are experiment targets, not measured results or minimum system requirements.

Task owner: Codex prepares the brief and evidence; Regner owns product approval,
remaining hardware details and existing Steam-app access. Effort cap for this pass:
one focused documentation/research session. Gameplay proofs remain separate spikes.

## Experience and scope

A playful, irreverent, top-down 3D city sandbox with GTA2-style camera and controls.
Players can explore, steal and drive forgiving arcade cars, shoot pedestrians and
vehicles, and set off readable car explosion chains. A small authored district
should offer useful driving loops, narrow escapes and opportunities for mischief
within a few minutes of starting. Original art and humorous signage supply identity.
Favor chunky readable silhouettes, restrained materials and inexpensive effects;
realistic graphics are not a goal. P0-04 still selects the specific visual direction.

M1 has no missions, score target or timed victory condition. Defer police/wanted
systems, interiors, passengers, detailed civilian simulation, building destruction,
procedural cities, persistent worlds, host migration and production matchmaking.
Public store launch is outside this private friends-playtest milestone.

| Decision | Ratified M1 promise / explicitly deferred choice |
| --- | --- |
| Capacity | 1–4 players total, including the host; one local player per process |
| Topology | Authoritative listen server; no dedicated-server product promise |
| Primary target (confirmed) | Steam Deck LCD and OLED, SteamOS Gaming Mode, 60 FPS at 1280×800; a Deck must support hosting as well as joining |
| Other targets | Windows 11 x86_64 and Linux x86_64 desktop; functional compatibility checks, with no separately approved 1080p performance promise |
| Offline | Standalone sandbox with the same authoritative rules/content; no Steam requirement, world save or offline-to-online conversion |
| Required transports | ENet loopback/direct LAN host/join and Steam friends over the internet, using the existing app |
| ENet joining | Explicit address/port; no LAN discovery or internet NAT-traversal promise |
| Steam joining | Friends lobby plus invite/launch joining, actual Steam gameplay transport across networks without port forwarding |
| Admission | Late joining during play; current state applied before control; full/incompatible/unreachable attempts fail usefully and allow retry |
| Host loss | End the match, explain the loss and return clients to a usable menu; lobby ownership changes do not migrate simulation |
| Delivery route | Start by evaluating native Linux on Deck; S08 must prove Gaming Mode/Steam Input/native dependencies. A Proton fallback requires a recorded decision and separate evidence |
| Renderer | Compare Mobile with the current Forward Plus setup on Deck; choose the simplest configuration meeting the visual/60 FPS requirements in S07/S08; retain Jolt for initial physics proofs |
| Input | Complete Deck gamepad gameplay/menu/settings flow without external keyboard/mouse; keyboard controls also supported for desktop/ENet testing |

Select ENet or Steam before host/join and keep it until teardown. ENet must work
without Steam installed or running. Steam service failures must leave offline/ENet
usable. Lobby membership alone is neither gameplay connectivity nor admission.
Invites arriving while loading or in a match use the common cancel/leave/join flow;
the UI must ask before leaving the current match. Cancellation and leave/rejoin
must clean up the old attempt. Settings menus do not pause a running shared world.

## Camera, controls and feel

Use a local camera following the controlled player or car, looking steeply down
with fixed world yaw. S02 chooses height, tilt, projection, follow/transition tuning
and obstruction treatment using gameplay-camera evidence. Roofs and effects must
not hide the controlled actor, road turns or an intended target. Camera rotation,
zoom controls and independent mouse aim are outside the starting scope.

Start with GTA2 turn/forward/back foot controls: W/S or Up/Down move along the
actor's facing, A/D or Left/Right turn, Space fires along facing, E interacts with
a nearby car, R reloads, and number keys select weapons. There is no starting strafe rule.
In a car, forward/back become throttle/reverse/brake, left/right steer and Space
is the handbrake. Escape opens the local menu. S02/S04 settle bindings and aim/turn
behavior; switching to another control model requires a deliberate product decision.

Car handling prioritizes quick steering response, controllable slides, readable
braking and recovery from walls/rollover. Physics-body choice is a spike decision.
Enter/exit should preserve camera/HUD orientation and control ownership without
an abrupt confusing view. Focus loss releases held movement and firing.

S02/S04/M1-D2 retain captures and short playtest notes: can a new tester walk around
a corner, hit an intended target, enter a car, complete a loop and recover from a
wall without coaching after a brief control prompt? Do explosions remain readable
while driving? Record failures and concrete tuning changes rather than claiming
that timing metrics alone establish fun. Foot and vehicle responsiveness decisions
are separate; prediction is chosen from S03-R/S04 evidence.

## Handheld input and presentation

Starting Deck mapping on foot: left-stick vertical axis moves forward/back and
horizontal axis turns, right trigger fires, A enters/exits, bumpers cycle weapons,
X reloads, and Menu opens local UI. In a car, triggers become throttle/brake/reverse
and B applies the handbrake. S02/S04 refine dead zones and bindings while preserving
the starting turn/forward/back intent; a twin-stick control model is a separate choice.
Menus/settings need D-pad/stick navigation, confirm/back, visible focus and correct
button prompts. Address entry must have an on-screen keyboard path. Gyro, touch-only
interaction and trackpad aiming are optional follow-ups.

Validate HUD/minimap/sign readability on the actual handheld display at 1280×800,
and Steam install/launch/invite/error flows in Gaming Mode using built-in controls.
No external keyboard should be needed for the normal friends-playtest flow. Offline
play must also work disconnected. Suspend/resume must release held input, recover
offline state, and either resume networking coherently or end with a useful retry
path. Record this behavior; seamless reconnect is not an M1 promise. Valve's
[Deck recommendations](https://partner.steamgames.com/doc/steamhardware/recommendations)
support full controller access and on-screen text entry. Public Deck Verified
certification remains outside M1.

## Ratified gameplay policies

| Rule | Ratified outcome |
| --- | --- |
| Friendly fire | Always on, including self-damage and player-caused car/blast damage; no toggle or teams in M1 |
| Death/respawn | Host respawns a player after 3 seconds at a reserved safe district spawn, with full health and the default weapon loadout; no lives or inventory penalty |
| Unsafe spawn | Retry for a bounded period; report failure if no valid spawn becomes available. The [P0-02 lifecycle draft](api-contracts.md#spawning-and-lifecycle) defines provisional clearance and a five-second search deadline |
| Car seats | One player driver; no passengers or visible NPC occupants. Entry transfers traffic control to the player through the host |
| Seat conflicts | Host grants one claimant; reject other claims. A blocked exit leaves the player seated rather than placing them inside collision |
| Car explosion occupant | Kill the seated driver as part of the same authoritative destruction transition; clear the seat and use normal respawn, with no forced ejection |
| Driver death/disconnect | Release the seat and neutralize controls; the surviving car remains in the world. S04 specifies safe stopping behavior |
| Abandoned traffic car | Remains parked until bounded cleanup/replenishment; does not immediately resume AI driving |
| Weapons | Pistol and SMG are hitscan; rocket launcher fires a finite-lifetime projectile with blast damage. Distinct rates/ranges and readable feedback |
| Ammo/equipment | All three weapons available at spawn; magazines and reload for pistol/SMG, unlimited reserve; rockets use a cooldown. No pickup/inventory progression in M1 |
| NPC minimum | Pedestrians wander sidewalks/crossings and flee nearby gunfire/blasts; traffic follows lanes/turns and recovers from blockage. Both can be damaged; replenishment is bounded |
| Wrecks/dead NPCs | Temporary, bounded world state; live chains continue off-camera; late join hydrates current wreck/health state without replaying historical effects |
| Match reset | Only host (or standalone player) can request full reset. Restore authored initial dynamic state, players, seats, weapons and population; clear shots/effects/history; keep admitted peers |
| Persistence | Audio settings persist locally; match/world state is discarded on leave/reset |

S05 settles blast radius, obstruction/falloff, chain timing/order, wreck collision
and cleanup duration. Combat tuning, respawn clearance and reset sequencing have
one authoritative owner each in the [P0-02 ownership draft](architecture.md).
Reset restores gameplay state around saved city placement; it never reconstructs
or overwrites the authored district.

## Required content

| Family | Ratified content scope; detailed kit choices remain P0-04 work |
| --- | --- |
| District | One exterior district, roughly six connected blocks; at least two connected driving loops, an alley shortcut, a plaza/landmark and a stunt/chain-reaction area |
| World kit | Reusable building types plus landmark, straight/turn/junction roads, continuous sidewalks/crossings and a small street-prop/sign kit; exact counts chosen in P0-04 |
| Vehicles | Two recognizable car silhouettes with color variants, damaged/wreck presentation, driver interaction and arcade handling |
| People | Shared player/pedestrian rig with readable variants and idle/walk/run/death animation coverage; no modeled traffic occupants |
| Weapons/effects | Pistol, SMG, rocket launcher; muzzle/impact/tracer/rocket feedback, explosion/smoke/sparks and bounded cosmetic debris |
| HUD/map | Health, selected weapon/ammo or cooldown, useful control prompts; road minimap with local controlled-entity marker; other markers chosen in P0-04 |
| Menus/settings | Standalone, Host, Join, Settings, Quit; in-match leave/reset/settings; Master/Music/SFX levels and mute saved locally |
| Audio | Weapon/hit/explosion, engine/tires, footsteps, UI and music/ambience with source/license records |

Every visible 3D model, including blockout/spike fixtures and mesh-based VFX,
comes from committed Blender sources and explicit linked GLB imports. Keep original
art, saved prefab/sector composition and authored placement as described in
[assets](assets.md). Collision/navigation, shaders/particle behavior, debug overlays
and 2D UI/minimap drawing remain separate concerns. P0-04 chooses the art direction,
layout and final kit inventory; asset production follows the plan's foundation gate.

## Provisional validation envelope

Confirmed reference **D1**: original LCD Steam Deck, AMD Zen 2 4-core/8-thread CPU,
8-CU RDNA 2 integrated GPU, 16 GB shared RAM, SteamOS, native 1280×800 handheld
display. Also require an **OLED Deck D2** compatibility/performance pass at 60 FPS.
Specifications are from Valve's [LCD specs](https://www.steamdeck.com/en/tech/deck).
Record each test device's storage model, SteamOS/client/driver versions, thermal
state and power settings. Baseline is the normal 15 W APU limit, no overclock,
native rendering and no frame generation; lowered power modes are not promised.
Measure both plugged-in and battery operation after warmup. Physical Deck access
and those installed-version details have not yet been established.

The local Ryzen 7 3700X/GTX 1070/approximately 32 GiB/CachyOS desktop can assist
development, but cannot certify Deck performance. Windows desktop test hardware
is still unspecified; functional export evidence remains required for that target.
Absent hardware is missing evidence, not a passed target.

The Deck/60 FPS/native-resolution requirement is confirmed. Other numbers below
are proposed starting budgets. S03/S03-S/S03-R/S04/S05/S07/S08 measure them and
P0-GATE records ratified values or explicit scope changes. Optimize or revise
provisional content/load choices with the user rather than silently relaxing 60 FPS.

| Measure | Initial target and measurement boundary |
| --- | --- |
| Display/render | Deck LCD/OLED: 1280×800 at 100% render scale; fixed documented stylized quality preset, real graphical exported build in Gaming Mode; 1080p desktop is an additional compatibility check |
| Frame time | Sustained 60 FPS on Deck in standalone, host and client capacity/burst cases; proposed pacing thresholds p95 ≤16.67 ms and p99 ≤20 ms, no sustained drops below 60. Record CPU/GPU times uncapped for headroom and capped at 60 for presentation review |
| Physics | Fixed 60 Hz (16.67 ms step); host physics/simulation work p95 ≤4 ms, p99 ≤8 ms per tick, including AI and chain work |
| Memory | Per-process peak resident memory ≤2 GiB and observed GPU allocations ≤1 GiB on Deck's shared memory; report measurement tool and overlap rather than adding counters blindly; no sustained growth after repeated reset/leave/rejoin |
| Bandwidth | At four players, host aggregate outgoing ≤256 KiB/s, incoming ≤128 KiB/s; each client incoming ≤96 KiB/s, outgoing ≤48 KiB/s. Use worst 10-second sustained windows including transport overhead; report short peaks separately |
| Join transfer | Authoritative baseline target ≤1 MiB per join, measured separately from ongoing bandwidth; [P0-02 limits](api-contracts.md#provisional-limits-and-failure-codes) draft bounded transfer/loading/admission deadlines for S03 validation |
| Normal network | RTT 0–150 ms, injected jitter up to ±30 ms one-way, independent packet loss 0–2% each direction; apply the same profiles to both providers and record actual delay/route |
| Adverse network | RTT 250 ms, jitter ±50 ms one-way, loss 5%; a 1-second delivery interruption and 250 ms host stall. Recovery/authority/bounded-work acceptance, with degraded feel allowed |
| Local response | p95 input-to-visible owned movement/turn/brake response ≤50 ms in the normal envelope on reference hardware; measure in windows/captures, not just command submission |
| Correction/recovery | Initial normal-envelope target: p95 positional correction ≤0.5 m; after delivery resumes in adverse tests, authoritative convergence within 1 second. S03-R/S04 define matching-tick telemetry and distinguish simulation error from presentation smoothing |
| World population | 64 live pedestrians and 32 live cars district-wide (initially 24 traffic + 8 parked; occupied cars count within 32), plus four players; replenishment never exceeds these caps |
| Temporary state/effects | Up to 16 retained wrecks and 16 dead pedestrian presentations in addition to live caps; 16 active rockets, 8 simultaneous explosion presentations and 64 total transient effect instances per client. S05 defines what each bound counts and cosmetic fallback |

Population is global, not multiplied per player. Far-apart views must not disable
off-camera authority or silently lower the accepted population. Quality settings,
sample definitions and network profiles must accompany results. Percentiles cover
the full measured interval, including effect bursts; report startup/loading apart.

Use a 60-second warmup and at least 10 minutes of measured normal/capacity play,
plus at least 20 repeated burst trials. Record build/engine/content identity,
hardware/OS/driver, renderer/API/quality, frame/physics percentiles, draw calls,
memory, bandwidth, population/effect peaks and retained logs. Compare memory at the
same settled lifecycle point after ten reset/leave/rejoin cycles. No existing run
has established any of these budgets. P0-03 builds only the harness needed for
small proofs; M1-D3 performs sustained integrated acceptance.

| Load case | Required observation |
| --- | --- |
| V1 — Normal sandbox | Standalone and host + one client, populated district, walking/aim/shoot and a driving loop; control/camera/audio/minimap readability |
| V2 — Capacity | Host + three clients at the global population caps, first together then in four distant areas, all driving/firing; run Deck as the host and separately as a client, recording render/simulation/network costs |
| V3 — Chain burst | 12 clustered live cars, trigger one explosion and drive the chain to completion while players fire; eight overlapping explosion presentations, rocket/effect peaks and bounded cosmetic fallback; repeat off-camera |
| V4 — Lifecycle during load | Join during/after V3, driver destroyed, simultaneous seat claims, blocked exit, death/disconnect, reset while driving/firing; exactly-once outcomes, current state, clean control/history/effects |
| V5 — Delivery/recovery | V2 movement and V4 transitions in normal/adverse profiles; duplicates/stale identities/revisions, slow join and full session, focus loss, host loss, cancel/retry; bounded queues/work and correct authority |
| V6 — Delivery targets | Deck LCD/OLED Gaming Mode controls/HUD/offline/suspend behavior and 60 FPS; Windows/Linux exports; ENet without Steam; distinct authorized Steam accounts on separate machines/networks, install/update/launch/invite/join and actual gameplay route diagnostics |

The 12-car chain intentionally exceeds the eight simultaneous explosion visuals:
all authoritative outcomes must occur, while excess cosmetic effects use the
documented fallback. Damage/chain queue and per-tick limits remain S05 decisions;
presentation caps cannot discard gameplay. Real Steam runs must establish the
external route independently; loopback or successful lobby creation cannot pass V6.

## Toolchain evidence and pin recommendation

Verified locally on 7 October 2026:

- `mise.toml` pins `github:godotengine/godot-builds` to `4.8-dev7`.
  `mise exec -- godot --version` reports `4.8.dev7.official.c971f93e7`.
- `mise.toml` and `.gdstyle-version` both pin `0.3.0`.
  `mise exec -- gdstyle --version` reports `gdstyle 0.3.0`.
- The project identifies Forward Plus, uses Jolt and selects D3D12 on Windows.
  Linux graphics/driver and Windows compatibility have not been tested here.
- The GodotSteam updater addon is present/enabled and reports plugin version
  `4.23`; this is inventory, not selection or proof of the gameplay peer/native SDK.

The official [4.8-dev7 release](https://github.com/godotengine/godot-builds/releases/tag/4.8-dev7)
and [download archive](https://godotengine.org/download/archive/4.8-dev7/) list matching
standard export templates. GitHub release API metadata checked on 7 October records
`Godot_v4.8-dev7_export_templates.tpz`, 1,436,879,719 bytes, updated 1 October 2026,
SHA-256 `95c2677555b4f66c7eeca1a41368674703497e1907aad3fe56576423ca3c8cc6`.
The local `~/.local/share/godot/export_templates/` directory is empty. Availability
is verified from publication metadata; archive contents, installation and exports
are not verified. S08 must check the archive's version and Windows/Linux debug/release
templates before exporting. A prior [missing-assets report](https://github.com/godotengine/godot/issues/123997)
is closed; publication alone should not substitute for that check.

**Pin decision remains open because Deck input is required.** The
[4.8-dev7 release notes](https://godotengine.org/article/dev-snapshot-godot-4-8-dev-7/)
list broken built-in Deck controls in Linux exports. The linked
[issue](https://github.com/godotengine/godot/issues/123704) is now closed by a
[fix merged on 1 October](https://github.com/godotengine/godot/pull/124017), after
the dev7 source snapshot; closure does not demonstrate a fix in our pinned binary.

Recommendation: retain gdstyle 0.3.0; keep 4.8-dev7 unchanged for this documentation
pass, but do not accept it as the Deck delivery pin. Move a minimal exported
Gaming Mode input/Steam initialization test to the start of S08, before S02 needs
handheld evidence. Prefer an official engine/template pair containing the fix;
compare a known working official release if necessary. Codex records the exact
candidate and results for a deliberate pin decision. A Desktop Mode workaround
does not satisfy the handheld promise. Any engine change needs matching templates
and reruns of affected import/save/reload/physics/network/native-extension evidence.
Regner approved leaving this pin decision open for the Deck proof. No engine
configuration changed in P0-01; the current development pin remains installed.

## Existing Steam-app setup record

Regner explicitly directed this project to use the IDs in `../vcs` on 7 October
2026. Read-only inspection found AppID **5294580**, Windows depot **5294581** and
Linux depot **5294582** in `tools/steam/app_build.vdf` and the corresponding depot
VDFs. `scripts/multiplayer/steam_runtime.gd` agrees on the AppID. VCS HEAD at
inspection: `9ccb14c356315f82c7d64369d40dca3fa7b6f985`; facts were read from the
working checkout. This deliberately supersedes earlier guidance against reusing
VCS application IDs. No sibling files or Steamworks configuration were changed.

Regner verifies live Steamworks setup; Codex records non-secret results and
S03-S/S08 test them. Keep credentials, keys and branch passwords outside this
document. Account aliases and verification status suffice. Use a separate private
Fun Things branch, preserving existing VCS builds/branches. Branch-specific content
still shares app-level launch configuration: settle executable names/launch settings
before uploading rather than assuming an isolated branch isolates those settings.
On 7 October Regner reported the live setup as unknown and directed that it need
not be settled now. The unknown fields below are S03-S/S08 prerequisites, not
P0-01 blockers. Obtain them when preparing those proofs; do not guess values.

| Field | Current status / evidence required |
| --- | --- |
| Existing AppID and app type | AppID 5294580 confirmed from the user-designated VCS configs; its private-testing guide describes an unreleased main-game route, but actual app type/release status needs Steamworks verification |
| Authorized test accounts | Not supplied; at least two distinct authorized accounts on separate machines/networks for S03-S, four players for capacity acceptance |
| App/package access | Unknown; record package IDs and account entitlement route, including unreleased-app access where needed; verify ownership/install with a tester |
| Depots | Windows 5294581 and Linux 5294582 in the corresponding VCS VDFs; platform filters and tester-package inclusion still need live verification |
| Launch settings | VCS exports `VehiclePlayground.exe` / `VehiclePlayground.x86_64`; its guide proposes install directory `Vehicle Playground` and empty Windows launch args. These are repo recipes, not verified live settings or a Fun Things launch decision |
| Private test branch | Intended branch `fun-things`, selected by Regner on 7 October; live creation/access/build IDs not verified. VCS guide proposes `default` / `friends`, with no `SetLive` in its app VDF; preserve those existing delivery paths |
| Integration/SDK/peer pins | Unselected; S03-S inspects the bundled candidate and chooses exact integration/native-library pins and proves gameplay traffic/relay route |
| Installation/update evidence | Not run; S08 proves tester install/update/launch, M1-D4 repeats with milestone gameplay and retains rollback build identity |

App/package entitlement and branch access are separate checks. Depot inclusion
also affects delivery; a branch password alone does not establish ownership.
See Valve's [Testing on Steam](https://partner.steamgames.com/doc/store/testing)
for the access/package distinction. Lobby/invite and actual transport evidence
remain required by [multiplayer](multiplayer.md).

## Open decisions, owners and closure evidence

Owners below name accountable roles; Codex is the initial implementation/research
owner unless Regner assigns someone else. Review questions do not become approvals
through silence. Record each answer/date and any changed scope here.

| Decision | Owner | Evidence and checkpoint |
| --- | --- | --- |
| D01 — Scope and gameplay policy ratification | Regner | Closed 7 October: approved the draft defaults with provisional budgets and open Deck pin proof |
| D02 — Reference hardware/input coverage | Regner (device access), Codex (record) | Reference selection closed: LCD baseline/both models/1280×800/60 FPS confirmed 7 October; Deck controls and desktop scope approved. Device access/installed versions/power settings recorded before S08/S07 tests |
| D03 — Existing Steam setup | Regner (access), Codex (record) | AppID/depot IDs and intended `fun-things` branch recorded; live setup unknown and explicitly deferred by Regner on 7 October. Complete app type/accounts/package/launch/branch facts before S03-S/S08 Steam proofs; does not block brief ratification |
| D04 — Development pin | Codex (proof), Regner (decision) | Installed pins/templates publication verified; current pin unchanged. Regner approved leaving exact engine choice open for early S08 Gaming Mode evidence before S02 handheld acceptance |
| D05 — Camera/control and car envelope | Codex, Regner (feel review) | S02/S03-R/S04 captures, response/correction measurements, corner/aim/drive/recovery tests; settle before P0-GATE |
| D06 — Art/layout and kit counts | Codex, Regner (direction review) | P0-04 concepts/layout, S06 route/clearance evidence; settle before P0-GATE |
| D07 — Gameplay/network bounds and tuning | Codex | [P0-02 API draft](api-contracts.md) and S03/S03-S/S05 size/rate/load/chain results; ratify draft timeouts and settle damage/ammo/reload/cooldown/wreck/queue limits before P0-GATE |
| D08 — Renderer, targets and measured budgets | Codex, Regner (scope changes) | S07 Mobile/Forward Plus cost/readability on Deck, S08 Gaming Mode/native exports/templates/Steam compatibility; ratify provisional budgets at P0-GATE, sustained 60 FPS acceptance M1-D3/D4 |

Review record, 7 October 2026: Regner selected Steam Deck, 60 FPS and non-realistic
graphics, then confirmed LCD baseline at 1280×800 with coverage for both models.
Regner also identified VCS as the source of the existing Steam AppID/depot IDs.
Regner then approved the remaining draft defaults, with budgets provisional and
the engine pin open for the Deck proof. Regner reported Steamworks setup as unknown
and directed that it should not be relevant at this stage. This deliberately defers
the original P0-01 live-setup requirement to S03-S/S08 and the final engine choice
to the early S08 Deck proof. Product scope is ratified; those proofs have not run.
Regner subsequently selected `fun-things` as the intended Steam beta branch.

P0-01 is complete with these explicit deferrals and owners. Subsequent tasks use
this brief and their decision records rather than independent copies of product
rules. P0-GATE still requires measured feasibility, final pin/renderer decisions
and the Steam transport/access evidence before production begins.
