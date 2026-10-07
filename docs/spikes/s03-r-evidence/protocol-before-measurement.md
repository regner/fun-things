# S03-R — bounded desktop ENet foot responsiveness

7 October 2026. Experiment protocol declared before measurement, based on local
main `35adb47042fe6b27c1653d38636f5eaf7d47578b`. S03-R remains OPEN: Steam,
reference hardware, physical input and user feel are unavailable/pending. This
experiment cannot close S02, S03-S, S08, P0-GATE or any production gate.

## Question, budget and independent criteria

Does authoritative foot movement with snapshot presentation meet the provisional
response envelope using the accepted actual S02 controller? One bounded two-process
ENet experiment, baseline and representative adverse profiles; one independent
review/fix cycle. Do not modify accepted S02/S03 resources, source/export evidence,
vendor, engine pin, production scene, vehicles, weapons or services.

The [ratified brief](../design.md#provisional-validation-envelope) owns the targets;
[command contracts](../api-contracts.md#commands-and-control-transfer) own newest-held
consumption, acknowledgement after simulation and neutralization. Criteria:

- Normal: loopback baseline and 150 ms RTT, ±30 ms one-way jitter, independent 2%
  loss in each direction. Provisional p95 input-to-visible owned movement/turn
  ≤50 ms; record automated event-to-simulation and event-to-rendered-frame separately.
  A rendered frame receipt is not physical key latency, display scanout or user feel.
- Normal correction target: p95 matching-tick positional correction ≤0.5 m.
  An authoritative-only client has no predicted matching-tick error. Report snapshot
  application error, update jumps and state age separately; do not call jumps
  prediction corrections or use zero application error to claim this target met.
- Adverse: 250 ms RTT, ±50 ms one-way jitter, independent 5% loss; a one-second
  bidirectional delivery interruption; a 250 ms host stall. Following delivery
  resumption, authoritative convergence ≤1 second, measured against a stationary
  settled host pose within 0.01 m and 0.1°; no stale motion after lifecycle teardown.
- Gameplay expectations through S02 APIs: walk forward along facing, turn changes
  facing/aim without strafing, independent host/client controls, actual solid-wall
  stop; aim telemetry uses the source muzzle and facing (no firing/combat system).
- Host acknowledges consumed/superseded intent only after one fixed simulation step;
  no client time grants extra steps. Admission/context/sequence/rate/byte bounds
  reject invalid intent; held input expires to neutral within 250 ms plus one tick
  after the last accepted receipt. Local input API cancellation clears held values
  immediately and sends neutral; this is not native OS focus revalidation.
- Teardown removes bindings/markers, neutralizes and hides bodies, clears replication
  and presentation buffers; host loss ends both processes cleanly through S03 APIs.

Use deterministic seeded native UDP impairment, retain actual proxy delays/drops,
structured readiness, raw per-tick/input/snapshot/render telemetry, source hashes,
engine/OS/process identities and exits. Use independent writable user/log dirs,
bounded proxy queues/work, runner deadlines and cleanup of owned Popen children only.
The small paced run is decision evidence, not the brief's ten-minute capacity or
reference-device acceptance.

Start with authoritative outcomes and remote presentation interpolation. Trial only
the smallest shared-rule prediction if evidence warrants and it fits this budget.
If acknowledgement-to-tick replay, contact restoration or a new production contract
needs substantial machinery, stop at measured evidence and leave an actionable
follow-up with its acceptance requirements.
