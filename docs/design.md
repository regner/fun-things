# Fun Things — product brief and validation envelope

Ratified product scope, 7 October 2026, amended by the
[owner decisions of 8 October 2026](reviews/owner-decisions-2026-10-08.md).
**P0-01 is complete under the review decisions recorded below.** This describes the
first playable milestone (M1), not implemented behavior. The required experience and
transport paths come from [the plan](../TODO.md). M1 now targets Windows and Linux
desktop with ENet; Steam gameplay and Steam Deck delivery are later work. The 60 FPS
Deck envelope and Steam identifiers remain future-target constraints, not M1 gates.
Budgets are guidance for later implementation, not requirements or measured results.

Task owner: Codex prepares the brief and evidence; Regner owns product approval,
remaining hardware details and existing Steam-app access. Effort cap for this pass:
one focused documentation/research session. Gameplay proofs remain separate spikes.

## Experience and scope

A playful, irreverent, top-down 3D city sandbox with GTA2-style camera and controls.
Players can explore, steal and drive forgiving arcade cars, shoot pedestrians and
vehicles, and set off readable car explosion chains. A small authored district
should offer useful driving loops, narrow escapes and opportunities for mischief
within a few minutes of starting. Original art and humorous signage supply identity.
Favor chunky readable silhouettes and inexpensive effects; realistic graphics
are not a goal. Regner clarified during P0-04 on 7 October: use darker, vibrant
colors inspired by cyberpunk palettes with ordinary city architecture. Regner
subsequently preferred Petrol & Coral and rejected a pixel-art-like treatment.
Regner then liked the smooth 3D and high-rise concepts, requesting some buildings
that reach or pass camera height. Regner accepted the combined concepts as sufficient
to continue on 7 October. The [art direction](art-direction.md) and
[city brief](world-layout.md) close P0-04's concept selection with explicit proof
deferrals; palette balance, individual designs and dimensions refine through the spikes.

M1 has no missions, score target or timed victory condition. Defer police/wanted
systems, interiors, passengers, detailed civilian simulation, building destruction,
procedural cities, persistent worlds, host migration and production matchmaking.
Public store launch is outside this private friends-playtest milestone.

| Decision | Ratified M1 promise / explicitly deferred choice |
| --- | --- |
| Capacity | 1–4 players total, including the host; one local player per process |
| Topology | Authoritative listen server; no dedicated-server product promise |
| Primary targets | Windows 11 x86_64 and Linux x86_64 desktop for M1 |
| Later target | Steam Deck LCD and OLED, SteamOS Gaming Mode and 60 FPS at 1280×800 |
| Offline | Standalone sandbox with the same authoritative rules/content; no Steam requirement, world save or offline-to-online conversion |
| Required M1 transport | ENet loopback/direct LAN host/join; session APIs must permit a later Steam adapter |
| ENet joining | Explicit address/port; no LAN discovery or internet NAT-traversal promise |
| Deferred Steam joining | Later friends lobby plus invite/launch joining and gameplay transport without port forwarding |
| Admission | Late joining during play; current state applied before control; full/incompatible/unreachable attempts fail usefully and allow retry |
| Host loss | End the match, explain the loss and return clients to a usable menu; lobby ownership changes do not migrate simulation |
| Delivery route | Prove Windows and Linux desktop exports for M1; Steam and Deck delivery follow later |
| Renderer | Keep the current renderer decision open; S07 environment scaling supplies guidance rather than a capacity gate |
| Input | Keyboard and mouse for desktop/ENet testing; gamepad controls are deferred |

M1 uses ENet, which must work without Steam installed or running. Keep session and
transport boundaries capable of a later Steam adapter: friend joins, lobby identity
mapping, reliable/unreliable message lanes and connection lifecycle must fit without
changing gameplay ownership. Actual Steam integration and testing are deferred.
Cancellation and leave/rejoin must clean up the old attempt. Settings menus do not
pause a running shared world.

## Camera, controls and feel

Use a local camera following the controlled player or car, looking vertically
straight down with fixed world yaw and perspective projection. The ratified S02
camera is 47 m high with a 42° field of view and fixed north-up orientation. Buildings
do not use cutaway presentation for now. Roofs and effects must not hide the controlled
actor, road turns or an intended target. Camera rotation and zoom remain outside scope.

On foot, WASD moves in screen/world-relative directions and the character faces the
mouse ground point each physics tick. Diagonals are normalized, movement uses one
5 m/s speed with instant start/stop, and left mouse fires. This replaces the earlier
tank-turning model. E interacts with a nearby car, R reloads, number keys select
weapons and Escape opens the local menu. Held weapon silhouettes remain approved.
In a car, forward/back are throttle/reverse/brake, left/right steer and Space is the
handbrake. Gamepad movement and aim are deferred.

Car handling prioritizes quick steering response, controllable slides, readable
braking and recovery from walls/rollover. Physics-body choice is a spike decision.
There is no firing from cars. Exit is allowed only while speed is below 0.5 m/s;
otherwise it fails with `EXIT_MOVING`. Enter/exit should preserve camera/HUD
orientation and control ownership without an abrupt confusing view. Focus loss
releases held movement and firing.

S02/S04/M1-D2 retain captures and short playtest notes: can a new tester walk around
a corner, hit an intended target, enter a car, complete a loop and recover from a
wall without coaching after a brief control prompt? Do explosions remain readable
while driving? Record failures and concrete tuning changes rather than claiming
that timing metrics alone establish fun. Foot and vehicle responsiveness remain
separate tuning concerns. Prediction is required for both the local on-foot character
and the locally driven car: replay only shared permitted simulation without side
effects, and authoritative corrections win.

## Handheld input and presentation

Gamepad gameplay controls, Steam Input and Deck-specific mappings are deferred.
When that work resumes, it must adapt the ratified independent movement and aim model
rather than restoring tank controls. Menus/settings will still need complete focus,
button prompts and an on-screen keyboard path for address entry.

For later Deck delivery, validate HUD/minimap/sign readability on the actual handheld
at 1280×800 and Steam install/launch/invite/error flows in Gaming Mode using built-in
controls. No external keyboard should be needed for that friends-playtest flow. Offline
play must also work disconnected. Suspend/resume must release held input, recover
offline state, and either resume networking coherently or end with a useful retry
path. Record this behavior; seamless reconnect is not a delivery promise. Valve's
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
| Driver death | Release the seat and neutralize controls; the surviving car remains in the world. S04 still specifies safe stopping behavior |
| Driver disconnect | Release the seat and neutralize controls; the surviving car coasts to a stop without braking |
| Abandoned traffic car | Remains parked until bounded cleanup/replenishment; does not immediately resume AI driving |
| Weapons | Pistol and SMG are hitscan; rocket launcher fires a finite-lifetime projectile with blast damage. Distinct rates/ranges and readable feedback |
| Ammo/equipment | All three weapons available at spawn; magazines and reload for pistol/SMG, unlimited reserve; rockets use a cooldown. No pickup/inventory progression in M1 |
| NPC minimum | Pedestrians wander sidewalks/crossings and flee nearby gunfire/blasts; traffic follows lanes/turns and recovers from blockage. Both can be damaged; replenishment is bounded |
| Wrecks/dead NPCs | Temporary, bounded world state; live chains continue off-camera; late join hydrates current wreck/health state without replaying historical effects |
| Match reset | Only host (or standalone player) can request full reset. Restore authored initial dynamic state, players, seats, weapons and population; clear shots/effects/history; keep admitted peers |
| Persistence | Audio settings persist locally; match/world state is discarded on leave/reset |

S05 starts from the ratified defaults: cars have 100 HP, explosions deal 100 damage
within 4.1 m with no falloff or obstruction test, chains delay 0.1 s, wrecks remain
for 5 s, and friendly fire/self-damage stay on. Every explosion gets its presentation;
there is no on-screen explosion cap. Combat tuning, respawn clearance and reset
sequencing have one authoritative owner each in the
[P0-02 ownership draft](architecture.md).
Reset restores gameplay state around saved city placement; it never reconstructs
or overwrites the authored district.

## Required content

| Family | Ratified content scope; starting kit in the accepted art/city brief |
| --- | --- |
| District | One exterior district, roughly six connected blocks; at least two connected driving loops, an alley shortcut, a plaza/landmark and a stunt/chain-reaction area |
| World kit | Six starting building/landmark families including office/apartment towers; reusable roads/sidewalks and six prop/sign families as recorded in the accepted art brief; proof-driven refinement remains |
| Vehicles | Two recognizable car silhouettes with color variants, damaged/wreck presentation, driver interaction and arcade handling |
| People | Shared player/pedestrian rig with readable variants and idle/walk/run/death animation coverage; no modeled traffic occupants |
| Weapons/effects | Pistol, SMG, rocket launcher; muzzle/impact/tracer/rocket feedback, explosion/smoke/sparks and bounded cosmetic debris |
| HUD/map | Health, selected weapon/ammo or cooldown, useful control prompts; top-right road minimap with local controlled-entity marker. Position is accepted; size and look need UI iteration |
| Menus/settings | Standalone, Host, Join, Settings, Quit; in-match leave/reset/settings; Master/Music/SFX levels and mute saved locally |
| Audio | Weapon/hit/explosion, engine/tires, footsteps, UI and music/ambience with source/license records |

Every visible 3D model, including blockout/spike fixtures and mesh-based VFX,
comes from committed Blender sources and explicit linked GLB imports. Keep original
art, saved prefab/sector composition and authored placement as described in
[assets](assets.md). Collision/navigation, shaders/particle behavior, debug overlays
and 2D UI/minimap drawing remain separate concerns. P0-04's accepted art direction,
layout and starting kit inventory are recorded in the linked briefs; the proofs
refine them, and asset production follows the plan's foundation gate.

## Provisional validation envelope

M1 validation targets Windows 11 x86_64 and Linux x86_64 desktop. Record named
hardware, OS, driver, renderer and build identity for each result. The original LCD
and OLED Steam Deck envelope below is retained as guidance for the later handheld
target, not as an M1 or P0 gate. Physical Deck access remains unavailable.

The local Ryzen 7 3700X/GTX 1070/approximately 32 GiB/CachyOS desktop can assist
Linux development. The current Windows development machine supplies desktop evidence;
neither machine certifies Deck performance.

The numbers below remain proposed starting targets pending their existing measurements
and owner/gate decisions. S07 uses relevant graphical values only as guidance for its
environment cost-versus-block report; that investigation is not a capacity gate.
Deck-specific display, frame and shared-memory targets are owner-deferred to later
handheld delivery; the other applicable targets remain in the Windows/Linux M1
validation envelope. Do not silently relax or ratify them.

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
| Temporary state/effects | Up to 16 retained wrecks and 16 dead pedestrian presentations in addition to live caps; 16 active rockets. Every explosion receives its effect; S05 measures cost without dropping presentations |

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
| V2 — Capacity | Host + three clients at the global population caps, first together then in four distant areas, all driving/firing; record render/simulation/network costs on named desktop hardware |
| V3 — Chain burst | 12 clustered live cars, trigger one explosion and drive the chain to completion while players fire; present every explosion, record rocket/effect peaks and repeat off-camera |
| V4 — Lifecycle during load | Join during/after V3, driver destroyed, simultaneous seat claims, blocked exit, death/disconnect, reset while driving/firing; exactly-once outcomes, current state, clean control/history/effects |
| V5 — Delivery/recovery | V2 movement and V4 transitions in normal/adverse profiles; duplicates/stale identities/revisions, slow join and full session, focus loss, host loss, cancel/retry; bounded queues/work and correct authority |
| V6 — M1 delivery targets | Windows/Linux exports and ENet without Steam; Deck Gaming Mode and actual Steam-account delivery are later-target checks |

The 12-car chain presents all explosions; no cosmetic slot cap may hide an effect.
Damage/chain queue and per-tick work limits remain separate S05 implementation bounds.
Steam transport and external-route validation are deferred beyond M1.

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

Subsequent desktop rendering supplement, 7 October 2026: the original P0-01
observations above describe that inspection, before S02. The
[reviewed S02 handoff](spikes/s02.md#reviewed-desktop-handoff),
[capture record](spikes/s02.md#captures-and-visual-findings) and
[independent art review](reviews/s02-art-b826d38.md) now document actual Linux
Forward+ viewport rendering on the local NVIDIA GTX 1070 / Vulkan 1.4.312 desktop,
at 1280×800 with the unchanged 4.8-dev7 pin. The [source kit](assets/s02_kit.md)
is a bounded blockout, not production content. Its 47 m/42° camera is provisional;
50° remains an inherited comparison. This supplements the historical untested
Linux graphics observation without certifying a driver/target matrix, Windows,
packaged Windows/Linux exports or Deck compatibility/performance. Human feel,
physical-key Alt-Tab and moving-camera/roof/held-weapon readability remain pending;
current native focus revalidation is incomplete, historical passes separate.
Full S02, early S08's engine/input decision and dependent gates remain open.
[S07 preparation](spikes/s07.md) owns capacity methodology/diagnostics, with
measurements unexecuted; S06 topology, S08 exact exports/input and M1-D3 integrated
acceptance retain their boundaries. No renderer, engine or budget ratification
follows from these desktop observations.

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

**Development stays on Godot 4.8-dev7 for now.** The
[4.8-dev7 release notes](https://godotengine.org/article/dev-snapshot-godot-4-8-dev-7/)
list broken built-in Deck controls in Linux exports. The linked
[issue](https://github.com/godotengine/godot/issues/123704) is now closed by a
[fix merged on 1 October](https://github.com/godotengine/godot/pull/124017), after
the dev7 source snapshot; closure does not demonstrate a fix in our pinned binary.

Retain gdstyle 0.3.0 and Godot 4.8-dev7 for current development. The known Deck
input limitation remains a later-delivery concern, not an M1 blocker. Any future
engine change needs a deliberate decision, matching templates and reruns of affected
import/save/reload/physics/network/native-extension evidence.

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
not be settled now. As of 8 October, these fields belong to later Steam work, not
S03-S, S08, P0-GATE or M1 prerequisites. Do not guess values.

| Field | Current status / evidence required |
| --- | --- |
| Existing AppID and app type | AppID 5294580 confirmed from the user-designated VCS configs; its private-testing guide describes an unreleased main-game route, but actual app type/release status needs Steamworks verification |
| Authorized test accounts | 7 October availability supplement: Regner has no multiple Steam accounts; S03-S's two-account/separate-machine/network proof is explicitly deferred until access exists. Four-player capacity acceptance remains required |
| App/package access | Unknown; record package IDs and account entitlement route, including unreleased-app access where needed; verify ownership/install with a tester |
| Depots | Windows 5294581 and Linux 5294582 in the corresponding VCS VDFs; platform filters and tester-package inclusion still need live verification |
| Launch settings | VCS exports `VehiclePlayground.exe` / `VehiclePlayground.x86_64`; its guide proposes install directory `Vehicle Playground` and empty Windows launch args. These are repo recipes, not verified live settings or a Fun Things launch decision |
| Private test branch | Intended branch `fun-things`, selected by Regner on 7 October; live creation/access/build IDs not verified. VCS guide proposes `default` / `friends`, with no `SetLive` in its app VDF; preserve those existing delivery paths |
| Integration/SDK/peer pins | Unselected; [S03-S preparation](spikes/s03-s.md) identifies bundled GodotSteam 4.23/SDK 1.65 and Linux registration, with source transfer-mode/default-channel mismatches. Selection/gameplay/relay remain unproved |
| Installation/update evidence | Not run; later Steam delivery work proves tester install/update/launch and retains rollback build identity |

App/package entitlement and branch access are separate checks. Depot inclusion
also affects delivery; a branch password alone does not establish ownership.
See Valve's [Testing on Steam](https://partner.steamgames.com/doc/store/testing)
for the access/package distinction. Lobby/invite and actual transport evidence
remain required by [multiplayer](multiplayer.md).

### Availability and validation-status supplement — 7 October 2026

Regner explicitly deferred Steam testing because multiple Steam accounts/testing
access are unavailable, and reported no Steam Deck device access. S03-S retains
the distinct-account/separate-machine/network proof until those facilities exist;
S08 retains LCD/OLED Gaming Mode/input/native-init, performance and suspend proofs
until devices exist. The [preparation record](spikes/s03-s.md) separates repository
IDs, public sources and local registration from unknown live Steamworks state and
unperformed transport/device tests. No renewed access request or substitute
account/hardware is part of this preparation.

These availability facts remain relevant to the deferred Steam and Deck targets.
They do not block the ENet-only Windows/Linux M1. Keep native 1280×800, LCD/OLED,
60 FPS, controller/Gaming Mode and existing VCS delivery as later-target constraints.
Public specs and desktop checks cannot establish hardware compatibility. Current
development remains on Godot 4.8-dev7.

## Open decisions, owners and closure evidence

Owners below name accountable roles; Codex is the initial implementation/research
owner unless Regner assigns someone else. Review questions do not become approvals
through silence. Record each answer/date and any changed scope here.

| Decision | Owner | Evidence and checkpoint |
| --- | --- | --- |
| D01 — Scope and gameplay policy ratification | Regner | Closed 7 October and amended 8 October by the linked owner decisions |
| D02 — Reference hardware/input coverage | Regner (device access), Codex (record) | Windows/Linux desktop are M1 targets as of 8 October; Deck controls and hardware evidence move to later delivery |
| D03 — Existing Steam setup | Regner (access), Codex (record) | Steam integration/testing is deferred beyond the ENet-only initial game; review session/transport abstraction compatibility now |
| D04 — Development pin | Codex (proof), Regner (decision) | Stay on Godot 4.8-dev7; Linux confirmation is follow-up and does not block proceeding |
| D05 — Camera/control and car envelope | Codex, Regner (feel review) | 42° camera and WASD/mouse-facing are selected; validate the control change, car rules and required local prediction |
| D06 — Art/layout and kit counts | Codex, Regner (direction review) | Concept direction, starting district brief and inventory accepted 7 October in the art/layout records. Dimensions, actual-camera/held-weapon refinement and cost remain S02/S04/S06/S07 evidence before P0-GATE |
| D07 — Gameplay/network bounds and tuning | Codex | [P0-02 API draft](api-contracts.md) and S03/S03-S/S05 size/rate/load/chain results; ratify draft timeouts and settle damage/ammo/reload/cooldown/wreck/queue limits before P0-GATE |
| D08 — Renderer, targets and measured budgets | Codex, Regner (scope changes) | S07 reports graphical environment cost versus block count as guidance; M1-D3/D4 validate selected Windows/Linux delivery, with Deck later |

Historical review record, 7 October 2026: Regner selected Steam Deck, 60 FPS and
non-realistic graphics, confirmed LCD/OLED coverage and identified VCS as the source
of existing Steam IDs. Steamworks setup was unknown and the intended beta branch was
`fun-things`. The [8 October decisions](reviews/owner-decisions-2026-10-08.md)
supersede that review's M1 transport, target, pin and gate ordering: ENet-only
Windows/Linux desktop is M1, Steam and Deck are later, and development stays on 4.8-dev7.

P0-01 remains complete. Subsequent tasks use this brief and the dated owner decisions.
P0-GATE reviews remaining feasibility without making S07 guidance, Linux confirmation,
Steam/Deck evidence or P0-PROFILES blocking prerequisites.
