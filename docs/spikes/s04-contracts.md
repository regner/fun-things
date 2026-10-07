# S04 bounded body and future seat contract

This record refines the [canonical API draft](../api-contracts.md) without selecting
production feel. The executable fixture is two pre-seated participants on ENet;
M1-B1 owns the full transition implementation and matrix below. S03-S, M1-D3 and
P0-GATE retain transport, adverse lifecycle and feel acceptance. See [S04](s04.md).

## Executable technical envelope

`S04DriveRules` alone owns facing-relative acceleration, speed caps, reverse,
steering, coast, braking and grip. Input collection converts the existing S02
physical bindings into four primitive car controls; test injection is labelled.
`S04Kinematic.step` adapts the rule to actual `move_and_slide` and uses solved
velocity after collision. `S04Dynamic` compares the same rule through solver-owned
integration. Neither provides cross-peer determinism, a rollback history or effects.
Pre-tree `configure(false)` establishes roles. Character replicas have zero layers
and masks and install host poses only; rigid passive bodies freeze STATIC, zero
velocities/gravity, sleep, and never take the authoritative integration branch.
`custom_integrator=true` disables built-in force integration; freezing disables the
remaining engine solver motion. Retiring clears commands, collision and visibility.

The host's physics callback advances each admitted driver's held intent once per
60 Hz tick, neutralizes expired intent after250 ms on the next available tick,
then captures actual position/yaw/solved velocity and consumed-or-superseded sequence.
A held sequence may drive many ticks. Rigid comparison receipts are solver-entry
state for the previous completed interval, before writing the next velocities.
Replica installation occurs at physics phase, not render interpolation. There is
one writer per body pose; presentation and camera consume it. No predicted state
exists, so jump distance cannot be called prediction correction.

The fixed fixture inherits S03 session/admission/RPC sender validation. One held
message has context/sequence/four primitive finite bounded drive values; inherited
120-sequence window, byte/rate limits and no unadmitted mutation apply. Snapshots
carry12 fields: player marker entity, tick, control/durable dependencies, position,
yaw, velocity, sequence, explicit vehicle ID, generation/life and collision revision.
Vehicle IDs1001/1002 are distinct from preserved player marker IDs1/2. This is a
**fixture compatibility adapter**: inherited S03 context uses the player marker ID;
production drive context must address the controlled vehicle EntityRef, as the
canonical API requires. No production wire compatibility is asserted.

Baselines preflight both unique player/participant rows, both unique matching poses
and both fixed seats before inherited lifecycle mutation. JSON integral fields are
normalized on a copied cut; malformed/dependency-mismatched cuts leave state intact.
Installed baseline ticks fence stale/equal delivery separately from fresh movement
admission. Session/control/entity/generation/life/collision dependencies fence poses;
future durable state is dropped, never buffered without its reliable dependency.
Grant plus fresh dependent pose opens local input; replacing/clearing/rollback
clears queued poses and floors. There is no general future-state/reset framework.

Seated resync retains the injured player, vehicle/driver seat and equipment sentinel
(`pistol`, magazine7), closes admission, neutralizes velocity/old commands, advances
control, installs a fresh cut and waits for grant plus fresh movement. This verifies
reauthorization on the existing S03 handoff, not a playable seat transaction, firing
policy or production equipment schema. Full match reset/late join seat conflicts
remain future tests; the initial two-client hydration is the bounded late join case.

## M1-B1 transition matrix (specified, not implemented)

The Match/Seat owner serializes reliable actions by `(accepted_tick, participant_id,
action_sequence)`. Each committed transaction updates player and vehicle together,
neutralizes old ownership, clears prediction/history/actions, applies collision and
presentation before publishing the durable revision. Rejects preserve all state.
Reliable action results never become a second state writer. Movement cannot write
seat, equipment, health, death or destruction. Query sockets use physics poses and
the S02 actor envelope, not smoothed presentation. Entry range/speed, full exit
clearance/ground tests and surviving-car stopping are **unratified tuning**; no values
are invented from the flat fixture.

| Trigger/race | Required authoritative outcome | Essential cases for M1-B1/M1-D3 |
| --- | --- | --- |
| Entry into eligible car | Alive unseated player, available nonterminal car, current revisions, range/speed/socket/clearance pass; disable foot simulation/collision, assign driver and new control revision in one transaction | Valid left/right entry; moving/out-of-range/blocked/no socket/stale car/dead player rejection |
| Two claims in one tick | First valid ordered claim wins; other receives `SEAT_OCCUPIED`; exactly one driver | Same/different peer, reversed receipt order, duplicate request/result and retry after vacancy |
| Player claims two cars / car has existing driver | First committed valid claim determines state; subsequent request validates new control/life and rejects | Same-tick pair, stale pre-entry context, NPC possession stopped before player admission; no immediate AI restart |
| Exit | Query authored left then right candidates with complete actor clearance/ground; first safe candidate restores foot pose/collision and transfers control atomically | Left free; left blocked/right free; both blocked => `EXIT_BLOCKED` with entire seat/foot/control unchanged; moving/terminal car policy pending feel |
| Entry versus exit / death / destruction / reset | Ordered validation uses latest life/control/terminal revisions; no partial ownership or resurrection | Every pair in both orders, duplicate callbacks and delayed reliable/movement packets |
| Driver disconnect / admission failure | Close commands and cancel reservations/actions, release seat exactly once; neutralize surviving vehicle; never immediately resume traffic AI | Before claim, during provisional handoff, admitted, resync loading, duplicate disconnect; stopping/park policy awaits feel |
| Driver death | Close commands, clear driver seat once, cancel seat/action/reload/prediction work; surviving vehicle neutral; dead player foot simulation disabled | Death before/after exit, during resync, delayed baseline cannot preserve a subsequently killed driver |
| Vehicle destruction / retirement | Commit terminal car state and occupant death/release once; disable old collision/controller and reject old generation | Driver occupied/unoccupied, simultaneous player death, pending exit/entry, cleanup plus late movement; S05/M1-B3 own damage/chains |
| Seated resync | Retain live injured player, seat/vehicle and equipment; close old control until current handoff and fresh dependent pose | Window overflow, loss/retry, death/destruction/exit during loading; stale grants/acks/input cannot reopen old control |
| Late join | Install reliable collision/lifecycle/seat/equipment dependencies before poses; joiner cannot claim before admission | Occupied/moving/terminal car, handoff while seat changes, duplicate cut/journal, current membership epoch |
| Host match reset | Close all commands, cancel claims/exits/jobs, clear seat/controller/history/callbacks, new match/control/entity revisions and collision cut before fresh poses | Driving, blocked exit, joining/resyncing, dead/destructing; retain admitted peers per accepted Match reset draft |
| Leave / host loss / reconnect | Retire bodies and clear all bindings/queues/input/callbacks; new session never admits old intent/pose/result | Host/client leave, reconnect, delayed old-session traffic, no ghost driver or collision |

No seated firing/reloading remains a draft policy for Regner's feel review before
P0-GATE. The fixture equipment sentinel does not confirm it. LCD/OLED/native input,
roof/target/camera readability and Steam evidence remain open. The S04 flat pad has
no grounded exits, ramps, suspension, rollover or two-way district route proof.
