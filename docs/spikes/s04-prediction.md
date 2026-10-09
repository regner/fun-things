# S04-P — local car prediction and lifecycle rules

8 October 2026. This bounded follow-up implements the owner-required locally driven car prediction
in the existing two-process S04 fixture. It also executes the ratified moving-exit and disconnect
rules. It does not tune handling, add firing, implement the full foot/car seat system, or change the
existing driver-death rule.

## Implemented boundary

`S04DriveRules.advance` remains the only handling formula. The host and predicted client both call
`S04Kinematic.step`, including the same `move_and_slide` collision path. The client numbers one input
per local physics tick, retains at most 120 inputs keyed by tick, and sends the newest input tick with
the existing bounded held command. Host poses acknowledge the newest input tick actually used by a
host simulation step. Ticks are bounded and must increase strictly within the current control
revision before held state can mutate. On receipt, the local client restores authoritative position,
yaw and velocity, discards acknowledged input, and replays only the remaining permitted movement
frames. Overflow
selects a host-state snap and clears history rather than unbounded replay.

Replay can move only the local car. It has no entry point for seats, health, inventory, damage, world
mutation, audio or effects. Remote cars retain the prior authoritative pose installation path.
Small corrections are hidden on the saved `PresentationAnchor` and decay separately from the
`CharacterBody3D` simulation transform; collision adopts the corrected state immediately. Baseline
replacement, resync, teardown and retirement clear prediction state.

The host rejects exit while planar speed is **at least 0.5 m/s** with `EXIT_MOVING`. The predicted
client permits one outstanding reliable request; the host applies a small per-peer token bucket and
clears it on disconnect. The first denial before refill returns a matching reliable `RATE_LIMIT`;
further denied replies are suppressed until admitted work resets that notification interval. The
matching verdict clears the pending client guard, allowing a later request after refill. Rejection
does not change seat or prediction ownership. A
successful stopped verdict disables local input and prediction, clears history, releases the replicated
seat and returns
the car to passive host-pose installation. On remote-driver disconnect, the host releases the seat and
input owner immediately, retains binding-independent replication metadata, substitutes neutral
controls, and replicates the surviving car under the shared coast rule until stopped. Driver death
still uses the pre-existing neutralization path; this task did not change it. No firing from cars was
added.

The expiry analyzer now records the age used at the start of the host simulation callback. This fixes
the known Windows boundary where a later post-step telemetry timestamp could make the previous row
look older than 250 ms even though the rule correctly expired on the next host tick. The criterion
itself remains `previous decision age <= 250 < expiry decision age`.

## Measurements

Pinned `Godot 4.8.dev7.official.c971f93e7`, Windows 11, separate host/client processes, private user
directories, seeded native UDP proxy, and unchanged saved-source fingerprints. Percentiles use the
runner's nearest-rank calculation over 20 pulse onsets. "Authority" is the previous unpredicted
input-to-installed-host-state measure; "predicted" is input-to-local-predicted-physics. Drawn values
are separate.

| Receipt | Authority p95 | Predicted p95 | Correction p95 | Replay CPU p95/tick | Disposition |
| --- | ---: | ---: | ---: | ---: | --- |
| Pre-rebase headless baseline | 179 ms | 58 ms | 0.163 m | 64 us | PASS |
| Post-rebase baseline | 304 ms (14/20) | 62 ms (20/20) | 0.193 m | 90 us | FAIL: six historical authority samples exceeded the 500 ms window |
| Development normal, 75 ms +/-30 ms one-way, 2% loss | 286 ms | 46 ms | 0.285 m | 36.46 us | PASS |
| Post-rebase normal | 282 ms | 68 ms | 0.275 m | 44.82 us | PASS |
| Review-corrected normal | 310 ms | 76 ms | 0.238 m | 27.43 us | PASS |
| Development adverse, 125 ms +/-50 ms one-way, 5% loss | 417 ms | 68 ms | 0.473 m | 36.67 us | FAIL only on the superseded post-step expiry timestamp boundary |
| Post-rebase adverse | 487 ms (18/20) | 57 ms (20/20) | 0.576 m | 34.96 us | FAIL: authority sampling and 0.5 m correction target |

The useful adverse development receipt converged predicted correction after interruption/stall in
381/249 ms; authority settled-state receipt was 301/253 ms. The post-rebase adverse run converged in
157/176 ms but correction p95 was 0.576 m. Correction p95 was below the 0.5 m design target in both
baseline receipts, both normal passes and the useful adverse development run. The approximately
27.8 m correction maxima include the fixture's intentional wall-segment authority teleport; they are
retained rather than silently filtered. The exact post-rebase adverse proxy reached 282 ms one-way
against its configured 175 ms envelope and is not accepted as an adverse pass. This lane did not tune
simulation around the parallel Windows latency investigation.

The exact post-rebase drawn Windows baseline produced 20/20 samples: authority drawn p95 **391 ms**,
predicted drawn p95 **85 ms**, and correction p95 **0.498 m**. `window_can_draw` was true and paired
PNGs are retained. Its runner failed the later wall-stop outcome under severe graphical pacing, so it
is a drawn measurement rather than a full profile pass. An earlier developmental drawn baseline was
136/104 ms with correction p95 0.146 m. Prediction improved drawn response in both, but neither met
the provisional 50 ms visible target on this contended workstation. Synthetic input and automatic
frame receipts are not physical key, display scanout or subjective handling evidence.

The review-corrected normal pass has 693 matching-tick samples with 0 m maximum installation error.
Unlike older receipts, it records the actual body immediately after authoritative restoration and
before replay. An analyzer counterexample supplies a correct wire pose but a body displaced by 4 m
and reports 4 m error, proving the criterion fails if installation is skipped. Older receipts remain
historical response/pacing records; their tautological zero-error field is not accepted.

The focused final-source check passed all five cases. Its prediction case independently forces the
120-frame overflow policy and correction snap; its lifecycle case proves strictly monotonic bounded
input ticks, bounded denied-reply work and rate-limit recovery, exactly-0.5 m/s rejection,
0.49 m/s acceptance,
immediate authority release on disconnect, coast pose inclusion, continued displacement under
neutral coast, and eventual stop. Two separate-process lifecycle cases additionally prove a stopped
exit makes the predicted client passive and an abrupt client process exit leaves a diagnostic-free
host, 59 replicated coasting snapshots and a car at rest. The current stopped-exit receipt adds 32
denied RPCs after depletion, observes exactly one host rate-limit reply, and still completes the honest
retry after refill.

## Disposition and remaining risk

The implementation requirement is complete in the bounded S04 fixture: local prediction, host input
acknowledgement, rewind/replay, bounded history, separate visual smoothing, moving-exit rejection and
disconnect coasting are executable and independently checked. The exact post-rebase normal profile
passes; baseline authority sampling and adverse correction remain mixed because Windows process
pacing was unstable. The 50 ms drawn target and a clean exact-final adverse run remain open; do not
reinterpret a failed retained result as a pass.

This is not full-world rollback. Replay uses current static collision and does not preserve historical
world geometry. Moving-car contact, foot/car prediction handoff, rejected predicted entry, blocked
exit placement, traffic-driver stealing, death/destruction races, physical controls, handling feel,
Linux, Steam and exports remain for S04-T/M1 acceptance. Direct text editing was used because the
Godot editor was unavailable; no saved scene hierarchy changed. The new script UID was generated by
the pinned headless editor import, whose known MCP/GodotSteam plugin diagnostics remain separate from
the addon-free focused and runner checks.
