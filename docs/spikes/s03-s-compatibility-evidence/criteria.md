# Predeclared S03-S compatibility experiment criteria

8 October 2026; written before probe implementation/execution. One question/session:
can the exact bundled 4.23 public narrow Sockets API carry plain unreliable packets,
provide bounded ordered freshness, and expose four independent lanes to a Godot
MultiplayerPeer without reliable substitution? Static/API/model evidence only;
no Steam initialization, connection, socket send, lobby or live callback experiment.
Stop if the minimum requires substantial framing/peer/lifecycle machinery. No fix,
contract change or integration selection is authorized by this probe.

## Existing contract expectations

Source: docs/api-contracts.md common identity, asynchronous operations, transport,
admission/replication and provisional limits; docs/multiplayer.md and accepted S03.

| Channel | Mode | Independent expectation |
| --- | --- | --- |
| 0 session/admission/actions | reliable | ordered delivery per stream; baseline lane cannot put actions behind missing baseline chunks |
| 1 baseline/durable/results/events | reliable | complete transactions and journal/handoff retain order; duplicate install has no second mutation |
| 2 held intent | unreliable ordered | loss may skip packets; received sequence never regresses; duplicates ignored; no retransmission dependency or conversion to reliable |
| 3 movement subsets | unreliable ordered | packet freshness belongs to this stream alone; application freshness still per EntityRef/control binding; unchanged relevant subsets revisited within 250 ms before loss |

No ordering across channels, no guarantee of delivery under sustained loss, and no
claim of bandwidth isolation: lanes share congestion/send-buffer resources. Plain
unreliable is permissible as a native primitive only if peer ordering and metadata
are supplied faithfully above it. Reorder 2,1,2 yields only 2 on one ordered stream;
channel 2 sequence 20 must not discard channel 3 sequence 1. Lost A100, B101,
lost A102, B103, A104 must leave A/B refreshed at 104/103. Movement cannot overwrite
durable health/life/control. Old session/match/generation/control packets remain
rejected independently of any stream sequence. No unbounded reorder wait/history.

Connection is not admission: four players including host and pending slots,
authenticated native binding -> fresh ParticipantId only after handshake, baseline,
reliable journal/handoff and matching state. Exactly one accepted-operation
completion; BUSY during non-IDLE; cancel invalidates producers/mappings before release.
Five-second local closing deadline; native-handle correlation where present;
uncorrelated lobby work serialized/drained with cleanup-only obsolete callbacks.
Late canceled result must never attach to retry; unsafe reuse means adapter
unavailable until proven safe/restart. Host loss ends match, no lobby migration.

## Bounds and observation plan (not newly ratified budgets)

Existing draft: connect 15 s/handshake 5 s/load 30 s/attempt 60 s;
baseline 1 MiB, <=128 chunks of <=16 KiB, transfer 10 s/handoff 5 s;
journal <=2 MiB or 4096 records; reliable transaction batch <=16 KiB;
actions <=4096 bytes, 16/s burst32, queue16, work4/participant/tick, cache64/ahead64;
held/movement <=1200 serialized bytes; held <=3 frames, queue8/participant,
60 messages/s burst8, ahead120, expiry250 ms; future motion latest row/entity,
<=256 rows or256 KiB/1 s then one bounded resync. Simulation60 Hz/input<=30 Hz/
movement<=20 Hz. Preserve upstream allocation limits separately from app bounds.

Synthetic probe cap: fixed finite traces only, four stream watermarks (no history),
one freshness value per two example entities, no codec/replay/service/peer class.
Static extraction bounded to exact source function bodies and exact hashes.
If registration is needed, copied addon/project and fresh /tmp XDG/cache/process,
30 s subprocess deadline; only reflection and version/settings getters. No imports
into original project or shared editor/service queries.

Before any future actual delivery experiment: record configure-lanes EResult,
send acceptance/error per lane/mode/size, receive lane/mode/message number, and
connection/per-lane pending bytes, unacknowledged reliable bytes and queue time.
Withhold lane1 acknowledgement while sending lane0 actions and lane2/3 updates;
check independent lane ordering and continued fresh traffic when capacity permits.
Increase bounded lane1 load until shared-buffer pressure: record LimitExceeded,
Ignored (NoDelay), invalid connection/state/parameter and oversized errors. No
success on failed send, no fallback lane0/reliable, no unbounded retry; replace/drop
obsolete unreliable work, bounded reliable failure/recovery. Observe <=1200,
4096 and16 KiB payload edges plus overhead, invalid/over-ceiling rejection and
native receive allocation. No safe MTU or tested logical limit inferred from512 KiB.
These are required future native observations, unavailable in this experiment.
