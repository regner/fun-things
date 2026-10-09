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

Each authoritative movement row now carries `last_input_tick`, advanced only after the
host simulates that held input. On receipt, the client restores authoritative pose,
velocity and yaw, removes acknowledged frames, and replays the bounded remainder. The
fixture has no prediction-time damage, inventory, firing or effect call: replay invokes
only foot motion/collision, while fire remains host-authoritative for S12. Exact authority
installation is measured before replay. Resets and large production corrections still
need a production snap policy.

Remote actors retain the existing 100 ms receipt-time interpolation. The predicted local
physics body receives static-world collision, while the presentation anchor decays each
correction over 100 ms independently of simulation. Remote dynamic bodies remain
non-colliding on the client, so contact with remote actors/cars is intentionally an
approximation rather than client authority.

The ring owns no foot-specific state and accepts complete command dictionaries. S04-P can
reuse it for drive frames, but its restore/replay adapter must own car velocity/steering
state and car collision; this lane does not edit S04.

## Protocol and analyzer corrections

The fixture's held envelope gained bounded `input_tick`; sequence remains the admission
and consumed/superseded acknowledgement, while `last_input_tick` identifies replay work.
The host records the held age sampled at the start of its physics callback. The analyzer
uses that decision age for the existing `<=250 ms` then `>250 ms` expiry boundary instead
of a later telemetry timestamp from the same callback. This resolves the previously
recorded Windows measurement artifact without extending gameplay expiry.

An initial two-tick producer-silence pulse could be lost on the intentionally unreliable
stream, making the independent expiry case observe no active command. The pulse now starts
12 ticks earlier but silence still begins at tick 1002; several replaceable frames establish
active held input without relying on one datagram. The failed run is retained.

## Measurements

The selected runs used two real ENet processes, the existing seeded bounded UDP proxy and
Godot `4.8.dev7.official.c971f93e7`. Other lane processes were active on the workstation,
so timings are labelled contended upper bounds. Each response row has 20/20 samples.
The headless loopback/adverse runs bind the final fixture source. The selected normal and
windowed runs precede only the telemetry-only held-decision-age field used by the final
expiry analyzer; motion, prediction, proxy and presentation behavior are unchanged, and
their result files retain exact source hashes. “Authority baseline” is the first matching
host-confirmed pose/sequence (and, windowed, the first subsequent drawn receipt), i.e.
when an unpredicted client could respond.

| Profile | Predicted physics p95 | Authority baseline p95 | Predicted drawn p95 | Authority drawn p95 | Correction p95 / max | Replay CPU p95 per frame | Max replay |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Headless loopback | 24 ms | 194 ms | unavailable | unavailable | 0.167 / 1.592 m | 78.0 us | 41 |
| Headless normal | 21 ms | 268 ms | unavailable | unavailable | 0.250 / 1.750 m | 30.0 us | 47 |
| Headless adverse | 18 ms | 426 ms | unavailable | unavailable | 0.250 / 3.917 m | 21.58 us | 83 |
| Windowed loopback | 22 ms | 123 ms | 35 ms | 149 ms | 0.250 / 0.527 m | 85.0 us | 42 |

All selected runs meet the provisional predicted response target (physics p95 <=50 ms)
and correction target (p95 <=0.5 m). Maxima are reported rather than hidden; visual
smoothing does not change authoritative physics. Exact authoritative installation error
was 0 m and no selected run exhausted 120-frame history. The adverse 1 s interruption
and 250 ms host stall converged in 320.47 ms and 564 ms respectively, both below 1 s.
The maximum adverse replay was 83 frames and remained bounded.

Selected correction classifiers were `none` or `held_timing_or_delivery`; no remote-actor
contact was observed in the final routes and no car exists in S03-R. The authoritative
wall case passed, but this run does not establish replay against other moving actors or
cars. That remains a production/S04-transition risk, not evidence of deterministic
whole-world rollback.

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
