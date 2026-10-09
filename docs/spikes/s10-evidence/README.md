# S10 pedestrian evidence

The accepted measurement receipt is [result.json](result.json). It contains the exact
pinned-engine commands, twelve run summaries (three seeds, two scenarios, two motion
options), contention/CPU snapshots, aggregate calculations and zero harness failures.
The short retained import and seed stdout logs are under [logs](logs/).

`history/initial-boundary-failure.json` preserves the first complete three-seed run.
That run rejected every case because the independent legal-corridor metric compared
clamped float transforms to exact decimal boundaries. Values such as `4.8999996` were
counted outside a `4.9` boundary. The correction added a 1 mm measurement tolerance;
it did not expand steering bounds. The accepted rerun has zero off-sidewalk and
road-outside-crossing agent-ticks. Historical timings are not substituted for the
accepted rerun.

All retained timing is labelled **contended upper bound**. The accepted repetitions
observed 8/8/9 Godot processes before launch and 11/9/10 during their snapshots. CPU
load snapshots are retained as reported by `Win32_Processor`, including implausibly
low instantaneous values; they are not treated as continuous utilization telemetry.
