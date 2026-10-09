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
host simulation step. On receipt, the local client restores authoritative position, yaw and velocity,
discards acknowledged input, and replays only the remaining permitted movement frames. Overflow
selects a host-state snap and clears history rather than unbounded replay.

Replay can move only the local car. It has no entry point for seats, health, inventory, damage, world
mutation, audio or effects. Remote cars retain the prior authoritative pose installation path.
Small corrections are hidden on the saved `PresentationAnchor` and decay separately from the
`CharacterBody3D` simulation transform; collision adopts the corrected state immediately. Baseline
replacement, resync, teardown and retirement clear prediction state.

The host rejects exit while planar speed is **at least 0.5 m/s** with `EXIT_MOVING`. The predicted
client sends a reliable request and does not change its seat or prediction owner before the host
verdict. A stopped fixture exit closes command admission and releases the seat. On remote-driver
disconnect, the host releases the seat and input owner immediately, substitutes neutral controls,
and continues the surviving car under the shared coast rule until stopped. Driver death still uses
the pre-existing neutralization path; this task did not change it. No firing from cars was added.

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
| Final headless baseline | 179 ms | 58 ms | 0.163 m | 64 us | PASS |
| Development normal, 75 ms +/-30 ms one-way, 2% loss | 286 ms | 46 ms | 0.285 m | 36.46 us | PASS |
| Final normal | 359 ms (19/20) | 89 ms (20/20) | 0.255 m | 37.63 us | FAIL: one historical authority sample exceeded the 500 ms observation window |
| Development adverse, 125 ms +/-50 ms one-way, 5% loss | 417 ms | 68 ms | 0.473 m | 36.67 us | FAIL only on the superseded post-step expiry timestamp boundary |
| Final contended adverse | 421 ms (9/20) | 117 ms (20/20) | 0.601 m | 38.06 us | FAIL: authority sampling, 0.5 m correction target, wall/recovery and expiry checks |

The useful adverse development receipt converged predicted correction after interruption/stall in
381/249 ms; authority settled-state receipt was 301/253 ms. Correction p95 was below the 0.5 m design
target in baseline, normal and that useful adverse run. The approximately 27.8 m correction maxima
include the fixture's intentional wall-segment authority teleport; they are retained rather than
silently filtered. The final adverse run occurred during severe local pacing contention (proxy delay
max 297.5 ms versus its 175 ms configured envelope, 11 missing authority samples) and is not accepted
as an adverse pass. It demonstrates that this lane did not tune simulation around the parallel
Windows latency investigation.

One actual drawn Windows baseline produced 20/20 samples: authority drawn p95 **136 ms**, predicted
drawn p95 **104 ms**, correction p95 **0.146 m**. `window_can_draw` was true and paired PNGs are
retained. The predicted drawn response improved but did not meet the provisional 50 ms visible target
on this contended workstation. Synthetic input and automatic frame receipts are not physical key,
display scanout or subjective handling evidence.

The focused final-source check passed all five cases. Its prediction case independently forces the
120-frame overflow policy and correction snap; its lifecycle case proves exactly-0.5 m/s rejection,
0.49 m/s acceptance, immediate authority release on disconnect, continued displacement under neutral
coast, and eventual stop.

## Disposition and remaining risk

The implementation requirement is complete in the bounded S04 fixture: local prediction, host input
acknowledgement, rewind/replay, bounded history, separate visual smoothing, moving-exit rejection and
disconnect coasting are executable and independently checked. The normal/adverse measurement set is
honestly mixed because Windows process pacing remained unstable. The 50 ms drawn target and a clean
exact-final adverse run remain open; do not reinterpret a failed retained result as a pass.

This is not full-world rollback. Replay uses current static collision and does not preserve historical
world geometry. Moving-car contact, foot/car prediction handoff, rejected predicted entry, blocked
exit placement, traffic-driver stealing, death/destruction races, physical controls, handling feel,
Linux, Steam and exports remain for S04-T/M1 acceptance. Direct text editing was used because the
Godot editor was unavailable; no saved scene hierarchy changed. The new script UID was generated by
the pinned headless editor import, whose known MCP/GodotSteam plugin diagnostics remain separate from
the addon-free focused and runner checks.
