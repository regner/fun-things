# S03-P — required local on-foot prediction

> **Historical run instructions.** Commands in this record that target `prototypes/` describe
> the original runnable checkout; they do not run in the current checkout because the archive
> is hidden by `.gdignore`. Follow the
> [restore-from-Git procedure](../../prototypes/README.md) at pre-cleanup commit
> `66400c26a01bf917dfe631af4762c2b444d9c48f`, then drop the `prototypes/<group>/`
> prefix from every listed archived path before running it. For example,
> `res://prototypes/s02/tests/fixtures/s02/corner.tscn` becomes
> `res://tests/fixtures/s02/corner.tscn`.

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

Each nominal 30 Hz unreliable envelope carries at most the canonical three consecutive
per-physics-tick frames. The bounded host queue accepts exact redundant copies but requires
every fresh frame to preserve one sequence-to-input-tick offset within the control
revision. Production retains at most eight queued frames per participant, separately from
the 120-sequence freshness window, and consumes at most one frame on each normal host
physics step. The step selects the oldest queued frame whose sequence and input tick are
within three ticks of the newest accepted frame and supersedes everything older; it never
runs extra simulation steps. Receipt age beyond 250 ms supersedes the remaining queue and
simulates neutral input on that step. Published watermarks advance only through that
simulated or explicitly superseded work. The deterministic probe covers isolated packet
loss, a 15-tick stall, the sparse `(1, 1)`/`(100, 100)` case, production capacity, and
neutral expiry with a specially sized 24-frame queue.

The analyzer computes accepted matching-tick error from received pose versus host source
pose; the immediate local restore remains a separate diagnostic. A regression with a
zero local diagnostic and a one-metre source mismatch fails that criterion. Windowed
acceptance additionally requires two drawable visible process states, all 20 authority
and predicted drawn samples, and predicted drawn p95 at or below 50 ms.

Producer silence still begins at tick 1002. Runtime acceptance now requires a non-empty
set of stale observations and inspects the first physics row whose decision age crosses
250 ms. That row and the remaining same-receipt stale rows must be neutral, and the
transition age must be no later than 250 ms plus its observed physics interval and a 2 ms
clock tolerance. Early queue underflow without a post-threshold observation and a late
transition both fail regressions. Batched held-result RPCs also return the newest frame
sequence; selected clients correlated hundreds of actual results rather than `-1`.

## Measurements

The selected runs used two real ENet processes, the existing seeded bounded UDP proxy and
Godot `4.8.dev7.official.c971f93e7`. Other lane processes were active on the workstation,
so timings are labelled contended upper bounds. Each response row has 20/20 samples.
All selected runs bind the final rebased fixture source. “Authority baseline” is the
first matching host-confirmed pose/sequence (and, windowed, the first subsequent drawn
receipt), i.e. when an unpredicted client could respond.

| Profile | Predicted physics p95 | Authority baseline p95 | Predicted drawn p95 | Authority drawn p95 | Correction p95 / max | Replay CPU p95 per frame | Max replay |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Headless loopback | 19 ms | 146 ms | unavailable | unavailable | 0.083 / 0.917 m | 43.50 us | 39 |
| Headless normal | 25 ms | 301 ms | unavailable | unavailable | 0.083 / 0.417 m | 25.00 us | 51 |
| Headless adverse | 19 ms | 413 ms | unavailable | unavailable | 0.250 / 3.750 m | 20.50 us | 81 |
| Windowed loopback | 29 ms | 139 ms | 39 ms | 170 ms | 0.000 / 0.917 m | 39.20 us | 39 |

All selected runs meet the provisional predicted response target (physics p95 <=50 ms)
and correction target (p95 <=0.5 m). Maxima are reported rather than hidden; visual
smoothing does not change authoritative physics. Exact authoritative installation error
and matching host-source error were 0 m, and no selected run exhausted 120-frame
history. The eight-frame authority queue ended every measured step with at most three
pending frames and enforced that lag by distance from the newest accepted frame. Selected
expiry transitions occurred at 251–268 ms and retained neutral same-receipt stale rows.
The adverse 1 s interruption and 250 ms host stall converged in 288.05 ms and 387 ms
respectively, both below 1 s. The maximum adverse replay was 81 frames and remained
bounded.

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
python prototypes/s03_r/tools/run_s03_r.py --godot C:/path/to/godot.exe --profiles baseline \
  --output C:/tmp/ft/lanes/s03-p/prediction-baseline
python prototypes/s03_r/tools/run_s03_r.py --godot C:/path/to/godot.exe --profiles normal adverse \
  --output C:/tmp/ft/lanes/s03-p/prediction-impaired
python prototypes/s03_r/tools/run_s03_r.py --godot C:/path/to/godot.exe --profiles baseline --windowed \
  --max-fps 60 --output C:/tmp/ft/lanes/s03-p/prediction-windowed
```

All output directories must be fresh and outside the checkout. The runner imports a
fresh addon-free fixture copy and stops only its own child processes. The standalone
history probe is:

```sh
godot --headless --path . \
  --script res://prototypes/s03_r/tests/fixtures/s03_r/prediction_history_probe.gd
```

## Disposition

The bounded required prediction mechanism passes its fixture criteria. Production still
needs the same core integrated under the production Match/local rig, explicit restore
state for slopes/grounding, moving actor/car contact trials, reset/respawn/seat-transfer
history policy, camera/aim continuity review, and physical-input feel. At P0-GATE the
owner must review the dated S03-P choice to consume queued input in order with a
three-frame pending-lag bound instead of the earlier newest-valid-frame wording. The
Windows headless authority variance remains S03-L evidence; prediction tuning did not
compensate for it. Steam-specific work is outside the ENet-only initial scope.
