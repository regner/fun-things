# S05 bounded executable damage/life contract

This is a new fixture supplement to the unchanged [API draft](../api-contracts.md),
[S03 session evidence](s03.md) and [S04 body/seat contract](s04-contracts.md).
It chooses provisional experiment policies, not production combat or ratified tuning.
The [predeclaration/results](s05.md) own scope and limits.

## Owners and callers

| Boundary | Sole writer / public API | Scope |
| --- | --- | --- |
| Connection/admission | Existing S03Session; S05Session adds lifetime-slot guard before its existing hello | Same offer/readiness/two-chunk baseline/journal/marker/grant/fresh-motion scheme; no replacement transport |
| Player marker/control | Existing S03Match with S05Match baseline/fire/teardown adapter | Up to four lifetime marker/shooter refs; no playable seats, weapon state or player death |
| Car health/life/seat sentinel | S05Damage `begin`, `register_shooter`, `resolve_shot`, `advance`, `cut`, `valid_cut`, `apply_cut`, `retire_shooter`, `clear` | One local experimental owner combines minimum Health/DamageResolver/Explosions responsibilities; no second field writer |
| Body/motion/collision | S05Car inherits unchanged S04Kinematic; `apply_life(host, phase)` | Neutralize and disable simulation before publication; original box remains stationary for wreck, then clears |
| Reliable current state/events | S05Replication extends S03Replication | New fire request and complete current car cut/live event use existing endpoints/channels; no Synchronizer/Spawner |
| Cosmetic reservation/history | S05Presentation `begin`, `advance`, `consume`, `clear` | Eight deadline tokens only; no authored explosion effect, audio or draw proof |
| Test coordination | S05Proof saved Boot root | Injects collaborators, duplicate live RPC, literal outcome expectations and bounded completion receipts |

Saved hierarchy: inherited S03 `Boot/Session` and `Boot/View/Match/{Replication,
RuntimeEntities,CityRoot}`, with new `Damage`, `Presentation`, and `Cars` children.
Cars are inherited S04 planar wrappers, not runtime-authored hierarchy. Root coordinates
children through APIs/signals. Simulation ownership is distinct from node owner and
Godot authority. Every saved car begins passive before its tree entry callbacks.

## Identity, work and retirement

Committed ShotId codec is exactly `{session, match, shooter, generation, sequence}`:
32-character session, match1, positive bounded integral IDs/sequence. Target is a
host-only fixed car ID, never client-reported amount/target. Canonical identity
meaning matches SessionId/MatchRevision/EntityRef/Sequence, using the fixture's
existing primitive vocabulary. This is not a production wire codec.

Each registered immutable shooter retains a monotonic high watermark until whole
session teardown, including after disconnect. Resolve equal/older sequence as
`DUPLICATE`; ahead >16 as `WINDOW`. Out-of-order lower unseen shots are intentionally
rejected; upstream committed WeaponState order is required. Reconnect allocates a
fresh marker ID. Four lifetime shooter slots include pending LOADING reservations;
a fifth initial peer is disconnected before provisional creation. No generation
reuse/reset exists. Invalid identity, ownership or admission cannot allocate a shot.

EventId is session/match plus monotonically allocated sequence. A direct shot
reserves its source EventId, then each first terminal car reserves exactly one blast
EventId/job. Car IDs1001..1012 and generation1 are immutable. The experiment never
accepts an external arbitrary blast or unreserved target set. At most one pending/
active job per saved car, twelve jobs total, with four **accepted** root resolutions
and four target visits per authoritative tick. Cheap rejected attempts are separately
bounded at the RPC receipt by per-peer4/s burst4 (at most three remote mappings).

Every job visits the finite saved target list once, retaining only its own active
visited target IDs (<=12); no newer EventId retires that older job. Its cache retires
at completion. `completed` holds <=12 bounded telemetry summaries, never a damage
acceptance cache. The per-shooter floor, not active target cache eviction, prevents
recreation of a completed shot. Terminal targets are immune to scheduling a second
blast. Roots at capacity/near identity exhaustion fail before spending sequence;
EventId headroom reserves all remaining car jobs. No accepted gameplay job depends
on cosmetic slots. No damage occurs on replicas or prediction/replay paths.

Jobs order by `(due_tick, EventId.sequence)`. Damage processing begins six ticks after
scheduling. A job may span ticks; the live explosion receipt is emitted **after** all
its target visits, following current state publication. Therefore presentation can
lag due tick by the bounded target work. With monotonic current ticks and fixed delay,
allocated blast order and due order agree; no general out-of-order event transport
or future-state buffer is implemented. At most36 complete current-cut publications
and12 distinct live events per finite fixture lifetime (terminal/completion/retirement
per car), independent of repeated shots at terminal cars.

## Life/collision and presentation policy

Flat centre-distance radius4.1 m; damage100/health100; no falloff and obstruction
ignored, friendly/self damage enabled. These finite saved bodies are the blast target
set, using host physical transforms. Decoration/culling never selects damage targets.
No hitscan muzzle, weapon/ammo/cooldown, projectile, historical world or lag compensation.

`LIVE` has health100/life1/collision1. First damage atomically neutralizes body commands,
sets health0/`WRECK`/life2/collision2, kills occupant sentinel9001 on A, and clears its
seat. Source car blast occurs once. Wreck retains the original stationary host layer4/
mask5 box until tick+300 AND completed blast, then `RETIRED`/life3/collision3 clears
collision and visibility. No deferred shape removal is needed: only immediate body
layer/mask/velocity flags change. Subsequent physics queries verify retained/cleared
collision. Replica bodies always have zero layers/masks and disabled simulation;
the current collision revision hydrates before any marker admission/motion dependency.
This verifies passive technical state, not a client's production world collider system.

The occupant is a nonrendering fixture sentinel, **not an admitted player**. The
contract specifies one driver death/release on destruction, never forced ejection;
production player health/control/respawn/equipment integration remains M1-B1/B2/B3.
No surviving-car seat race/exit or full destruction transaction architecture here.

Current wreck presentation retains the unchanged technical car mesh. Eight120-tick
cosmetic slot tokens, monotonically consumed live EventIds and durable dependencies
prove gameplay independence/deduplication. Saturated events advance history and drop
cosmetics, never defer/cancel damage. Future-dependency events drop without advancing
history; current historical hydration emits no events. No actual explosion slots,
particles, debris, sound, overdraw, drawn feedback or presentation CPU/GPU load measured.

## Reliable cut and admission boundary

`cars` extends the existing S03 immutable baseline with `{session, match, revision,
tick, rows}`. Up to12 fixed ordered rows have exact fields `id,generation,health,life,
collision,phase,deadline,occupant,occupant_alive,seat,explosions`; decoder preflights
all rows/coherence before mutation and normalizes integral JSON numbers. Current
reliable cuts accept only newer revisions; session/match/generation and malformed
cuts reject atomically. Movement owns only inherited player marker sample/tick/control,
never car state. Baseline restores current wreck rows before acknowledgement/input.
No historical explosions are transferred. No new baseline/journal framework exists.

New intent is exactly `{context, sequence, fire:true}` using the existing sender-bound
S03 context. S05Replication derives participant from actual RPC sender, refuses unknown
senders before rate allocation, bounds serialization at512 Variant bytes and per-peer
4/s burst4 with no request queue, then S05Match validates admission/context/shape.
Results are test observation, not a second state writer. Root local API checks and
remote intent use the same S05Damage resolver.

New current car JSON cut <=8192 UTF-8 bytes; events <=512 Variant bytes, no future queue.
Original baseline cap8192/two chunks and four-channel S03 protocol remain unchanged.
Application size checks do not certify engine predecoder allocation, transport MTU/
fragmentation, flood/stall capacity or Steam. Fifth-lifetime-peer graceful rejection
is a scoped admission guard; full reconnect/loading/abuse races remain unmeasured.

Publish current car rows/live events only to admitted mappings. This bounded fixture
joins its third process **after settled chains**. It does not journal arbitrary car
changes during an immutable in-flight baseline; full during-chain joining/retention
races must use the canonical reliable journal at M1-B3/M1-D. Do not use this supplement
as a production join implementation or infer correctness for that excluded case.

## Source reuse and evidence boundary

`car.tscn -> s04/kinematic.tscn -> s04_car.glb(.import) -> s04_kit.blend`;
`boot.tscn -> s04/track.tscn -> s04_track.glb(.import) ->` same source.
[Unchanged source handoff](../assets/s04_kit.md) owns collections/export membership,
Blender5.2.2LTS/exporter5.2.40, sockets/materials and source fingerprints. The new
consumer map lives here to avoid overlap with the concurrent guide/handoff worker.
No source edits/reexports, new assets, imported-child overrides or generated meshes.
New inherited resources have their own Godot-saved UIDs/node IDs and script sidecars.
`tools/s05/check_resources.py` checks every original technical file against the base,
new UID/path agreement, linked dependencies and absence of copied/generated render
meshes; live save/close/reopen and probe receipts separately check editor synchronization.

Only neutral technical fixture/source acceptance is requested. No art direction,
actual camera/physical input/feel/device/native target or production gate closure.
Rerun spacing/contact after final S04/S02 dimensions. S05's partial remaining work is
in TODO; full join/reset/sustained capacity and authored feedback belong to their
existing M1-B3/B4/M1-D and S07 gates.
