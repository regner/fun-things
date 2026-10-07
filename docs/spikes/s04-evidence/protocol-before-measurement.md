# S04 — bounded desktop body/control and ENet experiment

8 October 2026. Predeclared before any S04 measurement. Lead: existing Sol 6.1
HIGH workspace worker in `s04-desktop-enet-cars`, base LOCAL main
`8b6dc3083fcb875febe778e362da1182ac4d67d1`. Exclusive new S04 Godot/Blender writer.
One minimal fixture, one comparison, one ENet experiment and one independent
review/fix cycle, capped at 1–2 focused days of effort, not a delivery promise.
Full S04 remains OPEN. Regner owns feel/product selection.

## Question and alternatives

Which smallest body/control candidate supports fast facing-relative steering,
sliding, braking and solid wall contact while leaving authoritative replication
tractable? Compare **CharacterBody3D with custom planar velocity** against an
**upright RigidBody3D with custom velocity/force integration** on the same saved
flat track, same Blender car and collision box, and one shared handling rule owner.
The rigid candidate retains engine contact solving; neither assumes cross-peer
determinism. VehicleBody3D is excluded unless this comparison establishes a useful
missing suspension/contact question. This is a technical comparison, not fun tuning.

One source-linked Blender hatchback, road pad/walls and source sockets; separate
authored Godot collision/query data. New S04 files only. Accepted S01/S02/S03/S03-R,
assets/project/pins/vendor remain immutable. S02's accepted technical actor envelope
is radius0.38 m/height1.8 m; its 47 m/42° and inherited50° cameras are provisional.
S03 session `0436db7` and bounded S03-R `ae48eb3` supply admission and metric lessons,
not car results or a foot prediction choice. Fourth checkpoint `8b6dc30` assesses
readiness. The six-block district and native LCD/OLED1280×800/60FPS targets stay fixed.

## Independent criteria and measurement definitions

- Body outcomes through public simulation APIs: straight acceleration exceeds
  8 m/s within2 s without lateral drift >0.05 m; reverse goes along facing;
  steering at speed changes heading by at least45° within1 s; braking from10 m/s
  settles below0.2 m/s within1 s; handbrake produces more retained lateral speed
  than ordinary grip; no wall penetration >0.05 m; reverse recovers from contact.
  Record contacts, stopping distance, turning extent and all failures. Compare
  useful minimum cases, no endless tuning or production vehicle acceptance.
- Passive bodies configured **before tree entry**: character replicas have zero
  collision layers/masks and never call movement; rigid replicas additionally
  freeze STATIC, zero gravity/velocities, sleep and custom integration disabled
  as a simulation path. Disabling scripts alone cannot satisfy this criterion.
- Pose samples come from physics callbacks, with actual phase/tick semantics
  recorded. Character samples follow move_and_slide; rigid solver-entry samples
  represent the prior completed solver interval, before next command writes.
  Acknowledgement describes consumed/superseded held intent after simulation,
  never receipt and never one input sequence assumed to equal one physics tick.
- ENet: real separate paced60 Hz processes;30 Hz intent,20 Hz complete pose refresh;
  loopback, normal150 ms RTT ±30 ms one-way jitter/independent2% directional loss,
  adverse250 ms RTT ±50 ms/5%, one-second bidirectional interruption and250 ms host
  callback stall. Seeded actual UDP proxy, bounded queue/work and child-only cleanup.
  Retain datagram bytes/delays/drops separately from Variant message bytes.
- Synthetic input onset to first client **applied physics pose** acknowledges the
  onset sequence and moves >0.005 m or turns >0.2°. Nearest-rank p95 over declared
  pulses. Automatic drawn-frame receipt, if available, is a distinct metric and
  does not prove physical keys/scanout/feel. Provisional visible p95 ≤50 ms target
  stays unproved without drawn evidence. Snapshot age, matching-host-tick install
  error and update jumps are separate; no prediction means no correction metric
  and cannot close the normal0.5 m correction target.
- Adverse recovery: settled authoritative car pose within0.01 m/0.1° within1 s of
  actual delivery resumption/stall end; do not use normal samples as adverse proof.
  Intent expires after250 ms on the next available host tick, without extra steps.
  Admission/context/entity/generation/life/control/session/baseline fences reject
  obsolete intent/pose/ack; seat/equipment never written by movement. Seated resync
  retains injured player/entity/seat/equipment and pose while host reauthorizes a
  fresh control revision; commands closed until current handoff plus fresh motion.

## Stop boundaries and remaining gates

One bounded local launch/window diagnosis may establish drawability. No broad
driver/display/engine/vendor/service repairs, renderer/pin changes, forced render
timing substitute or unknown process kills. If unavailable, stop drawn claims,
finish useful technical evidence and name the next measurable drawable question.
No substantial replay/prediction machinery or general transport/lifecycle framework.
If required, record the next bounded host-tick/contact/replay question before expansion.

No production vehicles/combat/traffic/full seat system. Specify the complete future
seat race/exit/disconnect/death/destruction/reset/resync matrix for M1-B1; only the
bounded seated fixture reauthorization is executable here. No-seated-fire/reload
policy requires feel confirmation before P0-GATE. Physical keys/native focus,
camera/roof/target readability, user feel, Steam and Deck remain open; unavailable
facilities have already been stated and will not be requested again. S03-R drawn
response and local foot prediction choice remain independently open.

## Evidence and disposition

Pending measurements, source handoff, contracts, retained logs, independent review
and exact-final revision receipt. Nothing in this predeclaration closes S04 or
downstream gates. S05/S06/S07 may consume only the eventual accepted technical
envelope, not candidate dimensions/handling or subjective selections.
