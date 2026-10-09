# S03-P — required local on-foot prediction

8 October 2026. This bounded S03-R fixture trial implements the owner's required local
foot prediction. It is Windows technical evidence on the pinned engine, not production,
physical-input, subjective-feel, Linux, export or full-world rollback acceptance.
The Godot editor was not running and MCP editor tools were unavailable, so project-owned
scripts and documentation were edited directly. No saved scene hierarchy changed.

## Implemented boundary

The local client samples one numbered input on every physics tick and immediately applies
it through the same `S02ActorMotion.step` and `S02MotionRules.advance` path used by the
host. `S03PredictionHistory` is a small reusable 120-frame ring: it retains tick, complete
command and fixed delta; drops acknowledged frames; and reports exhaustion rather than
replaying across a missing prefix. A control revision, baseline, rollback or teardown
clears it.

Each authoritative movement row carries `last_input_tick`, advanced to the exact client
physics frame consumed by that host step. On receipt, the client restores authoritative
pose, velocity and yaw, removes acknowledged frames, and replays the bounded remainder.
The fixture has no prediction-time damage, inventory, firing or effect call: replay
invokes only foot motion/collision, while fire remains host-authoritative for S12. The
local restore diagnostic is separate from the accepted matching-tick comparison between
the received pose and the matching host source pose. Resets and large production
corrections still need a production snap policy.

Remote actors retain the existing 100 ms receipt-time interpolation. The predicted local
physics body receives static-world collision, while the presentation anchor decays each
correction over 100 ms independently of simulation. Remote dynamic bodies remain
non-colliding on the client, so contact with remote actors/cars is intentionally an
approximation rather than client authority.

The ring and `S03InputFrameQueue` own no foot-specific state and accept complete frame
or command dictionaries. S04-P can reuse those cores for drive frames, but its
restore/replay adapter must own car velocity/steering state and car collision; this lane
does not edit S04.

## Protocol and analyzer corrections

Each nominal 30 Hz unreliable envelope now redundantly carries at most four consecutive
per-physics-tick frames. The bounded host queue deduplicates them, consumes at most one
oldest frame for each participant on each normal host physics step, and advances the
published watermark only to that frame. A gap before the next available frame is
explicitly counted as superseded. Missing input produces neutral motion; the host never
repeats an already acknowledged frame and never runs extra simulation steps to drain a
stall backlog. The standalone deterministic probe executes all 120 matching numbered
frames with isolated packet losses and a 15-tick host stall and observes zero source-tick
correction.

The analyzer computes accepted matching-tick error from received pose versus host source
pose; the immediate local restore remains a separate diagnostic. A regression with a
zero local diagnostic and a one-metre source mismatch fails that criterion. Windowed
acceptance additionally requires two drawable visible process states, all 20 authority
and predicted drawn samples, and predicted drawn p95 at or below 50 ms.

Producer silence still begins at tick 1002. The analyzer now accepts neutralization no
later than 250 ms plus one tick, rather than requiring the authority to reuse stale held
input until that deadline. This keeps the safety bound while preserving one numbered
client frame per authoritative movement step.

## Measurements

The selected runs used two real ENet processes, the existing seeded bounded UDP proxy and
Godot `4.8.dev7.official.c971f93e7`. Other lane processes were active on the workstation,
so timings are labelled contended upper bounds. Each response row has 20/20 samples.
All selected runs bind the final rebased fixture source. “Authority baseline” is the
first matching host-confirmed pose/sequence (and, windowed, the first subsequent drawn
receipt), i.e. when an unpredicted client could respond.

| Profile | Predicted physics p95 | Authority baseline p95 | Predicted drawn p95 | Authority drawn p95 | Correction p95 / max | Replay CPU p95 per frame | Max replay |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Headless loopback | 22 ms | 164 ms | unavailable | unavailable | 0.000 / 1.917 m | 37.67 us | 39 |
| Headless normal | 20 ms | 390 ms | unavailable | unavailable | 0.000 / 1.924 m | 21.67 us | 47 |
| Headless adverse | 17 ms | 429 ms | unavailable | unavailable | 0.000 / 3.750 m | 21.86 us | 84 |
| Windowed loopback | 22 ms | 173 ms | 28 ms | 184 ms | 0.000 / 0.449 m | 37.0 us | 41 |

All selected runs meet the provisional predicted response target (physics p95 <=50 ms)
and correction target (p95 <=0.5 m). Maxima are reported rather than hidden; visual
smoothing does not change authoritative physics. Exact authoritative installation error
and matching host-source error were 0 m, and no selected run exhausted 120-frame
history. The largest pending authority queue was 20 frames. The adverse 1 s interruption
and 250 ms host stall converged in 385.22 ms and 309 ms respectively, both below 1 s.
The maximum adverse replay was 84 frames and remained bounded.

Selected correction classifiers were `none` and `held_timing_or_delivery`; no
remote-actor contact was observed in the final routes and no car
exists in S03-R. The authoritative wall case passed, but this run does not establish
replay against other moving actors or cars. That remains a production/S04-transition
risk, not evidence of deterministic whole-world rollback.

The windowed run drew both 1280x800 Windows views with no missing response samples. Its
retained before/after PNG pair is a technical receipt, not camera continuity or human
feel review. Headless drawn values remain honestly unavailable.

## Retained evidence and reproduction

Selected results, raw process telemetry, proxy delivery logs and two PNGs are under
[`s03-prediction-evidence/`](s03-prediction-evidence/). Failed attempts retain the
single-pulse expiry assumption, the old post-step expiry timestamp artifact and one
heavily contended headless baseline. No staged scratch project is committed.

```sh
python tools/run_s03_r.py --godot C:/path/to/godot.exe --profiles baseline \
  --output C:/tmp/ft/lanes/s03-p/prediction-baseline
python tools/run_s03_r.py --godot C:/path/to/godot.exe --profiles normal adverse \
  --output C:/tmp/ft/lanes/s03-p/prediction-impaired
python tools/run_s03_r.py --godot C:/path/to/godot.exe --profiles baseline --windowed \
  --output C:/tmp/ft/lanes/s03-p/prediction-windowed
```

All output directories must be fresh and outside the checkout. The runner imports a
fresh addon-free fixture copy and stops only its own child processes. The standalone
history probe is:

```sh
godot --headless --path . \
  --script res://tests/fixtures/s03_r/prediction_history_probe.gd
```

## Disposition

The bounded required prediction mechanism passes its fixture criteria. Production still
needs the same core integrated under the production Match/local rig, explicit restore
state for slopes/grounding, moving actor/car contact trials, reset/respawn/seat-transfer
history policy, camera/aim continuity review, and physical-input feel. The Windows
headless authority variance remains S03-L evidence; prediction tuning did not compensate
for it. Steam-specific work is outside the ENet-only initial scope.
