# Quiet foundation remeasurement — 9 October 2026

## Scope and method

The owner reduced this pass to the S17 integrated host-tick measurement only: make the
integrated work function first, tune targets during implementation, and optimize later. This
record therefore compares S17's documented three-seed quiet reproduction with its original
contended result. All other requested spikes retain their contended records and are deferred.
No runner logic or acceptance criterion changed.

The command was run from repository revision `13722e0726237311fb044053ca9f92728b33e448`
with the Mise-pinned `Godot 4.8.dev7.official.c971f93e7`:

```sh
export PATH="$(dirname "$(mise -C C:/GameDev/git/fun-things which godot)"):$(dirname "$(mise -C C:/GameDev/git/fun-things which gdstyle)"):$PATH"
timeout 5000 python prototypes/s17/tools/s17/run.py --godot "$(command -v godot)" \
  --output C:/tmp/ft/lanes/quiet-pass/s17/run
```

The unchanged runner imported one isolated addon-free project, then ran seeds 171, 272 and
373 strictly sequentially. Each seed retained a 3,600-tick warmup and 36,000 measured ticks.
The pooled percentiles therefore cover the same 108,000 samples as the contended result.
Every process exited zero, all equivalence/outcome checks passed, and the logs contain no
engine or script diagnostic.

Before the outer command, `tasklist | grep -ci "godot.exe"` returned **0**. Two idle
`godot-ai.exe` MCP bridges and two idle `mcp-for-blender.exe` bridges were present; no
`blender.exe` or other heavy application was observed. The active power scheme was Balanced,
and the battery receipt reported 96%. The pre-launch query used Win32_Battery's ambiguous
`BatteryStatus` field, so it did not itself prove AC power. The instantaneous outer CPU
snapshot was 77%; seed-level pre-launch snapshots were 26%, 7%, and 54%. A post-run
`root/WMI BatteryStatus` receipt explicitly reports `PowerOnline=true`; the orchestrator also
guaranteed the quiet window. This receipt limitation is retained rather than overstated.

The unchanged S17 runner counts all names containing `godot`, including the two idle
`godot-ai.exe` bridges. Its raw snapshots consequently report 2 before, 3 while its own seed
process runs, and mechanically label rows `contended upper bound`. Under this pass's required
`godot.exe`-only definition, there were zero unrelated measurement engines and no other lane
ran Godot. This record therefore classifies the S17 result as the **quiet measurement**; the
raw label is a known naming mismatch retained only for receipt fidelity. CPU snapshots are
instantaneous, and one documentation-only agent was active, so they do not prove an otherwise
idle CPU or continuous utilization.

## Machine and source identity

- CPU: Intel(R) Core(TM) Ultra 7 165H, 22 logical CPUs.
- OS: Microsoft Windows 11 Enterprise 10.0.26200 build 26200, AMD64.
- Engine: Godot `4.8.dev7.official.c971f93e7`, headless Forward+.
- Repository identity, invocation, effective parameters, and hashes for the runner,
  `measurement_identity.py`, and S17 fixture are retained in
  [`measurement-identity.json`](quiet-remeasure-evidence/s17/measurement-identity.json).
- Compact result, complete runner result, precondition, AC follow-up, and short clean logs are
  under [`quiet-remeasure-evidence/s17/`](quiet-remeasure-evidence/s17/).

## S17 integrated host tick

Times are milliseconds. Each value is pooled median / p95 / p99 / worst across three seeds.
The whole-host target remains p95 <= 4 ms and p99 <= 8 ms. Internal p95 planning shares are
pedestrians 1.0, traffic 1.5, production snapshot capture/encoding 0.75, combat 0.25, and
chains 0.10 ms. The conservative snapshot row deliberately performs three full encodes every
tick and is not the proposed production schedule.

| Metric | Contended value | Quiet value | Budget / target | Quiet verdict |
| --- | ---: | ---: | ---: | --- |
| Pedestrians | 1.437 / 2.960 / 4.217 / 61.919 | 1.255 / 2.559 / 3.828 / 120.593 | p95 <= 1.0 | **Fail** |
| Traffic | 0.644 / 1.423 / 2.188 / 47.374 | 0.578 / 1.264 / 1.939 / 134.094 | p95 <= 1.5 | Pass |
| Combat/history | 0.051 / 0.141 / 0.272 / 14.819 | 0.043 / 0.119 / 0.232 / 23.347 | p95 <= 0.25 | Pass |
| Explosions/chains | 0.007 / 0.018 / 0.057 / 73.897 | 0.006 / 0.015 / 0.047 / 3.247 | p95 <= 0.10 | Pass |
| Three full encodes every tick | 1.176 / 2.478 / 3.636 / 182.232 | 1.029 / 2.159 / 3.265 / 82.000 | conservative comparison | No independent gate |
| One subset encode every four ticks | 0.001 / 0.664 / 1.038 / 53.321 | 0.001 / 0.499 / 0.917 / 39.865 | p95 <= 0.75 | Pass in fixture |
| **Conservative inclusive total** | **3.527 / 6.519 / 8.643 / 186.217** | **3.027 / 5.658 / 8.321 / 230.301** | **p95 <= 4; p99 <= 8** | **Fail both** |
| **Production-schedule substituted total** | **2.394 / 4.582 / 6.286 / 105.321** | **2.069 / 3.989 / 5.849 / 148.308** | **p95 <= 4; p99 <= 8** | **Pass both, p95 by 0.011 ms** |
| Empty timer bracket | 0.000 / 0.001 / 0.001 / 0.246 | 0.000 / 0.001 / 0.001 / 0.051 | instrumentation context | Pass |

Quiet pooled p95 improved by 13.2% for the conservative total and 12.9% for the
production-schedule total. The production-schedule p95 moved from a 0.582 ms miss to a
0.011 ms pass; its p99 remained within budget. The conservative path still misses both host
percentiles. Pedestrians remain the largest attributed p95 section and still exceed their
planning share. The larger quiet worst values for pedestrians, traffic, combat, and both
totals show that removing other Godot measurement processes did not remove all Windows
scheduler hitches; worst is retained for diagnosis but does not replace percentile gates.

This is fixture evidence, not production acceptance. It still omits real body physics,
prediction replay, socket service, and projectile movement, while its conservative codec
path overstates the intended production encoding schedule. The 0.011 ms production p95
margin is too small to claim integrated headroom for omitted work.

## Deferred spikes

Per the owner's mid-run scope decision, each row below has the same disposition:
**contended values retained; quiet re-measurement deferred by owner decision (make it work,
then pretty, then fast; targets are tuned during implementation).**

| Spike | Quiet-pass disposition |
| --- | --- |
| S10 pedestrian AI | Contended values retained; quiet re-measurement deferred by owner decision. |
| S09 traffic AI | Contended values retained; quiet re-measurement deferred by owner decision. |
| S11 population networking | Contended values retained; quiet re-measurement deferred by owner decision. |
| S12 combat | Contended values retained; quiet re-measurement deferred by owner decision. |
| S03-L Windows latency | Contended values retained; quiet re-measurement deferred by owner decision. |
| S03-P foot prediction | Contended values retained; quiet re-measurement deferred by owner decision. |
| S04-P car prediction | Contended values retained; quiet re-measurement deferred by owner decision. |
| S04-T foot/car transition | Contended values retained; quiet re-measurement deferred by owner decision. |
| S13 characters | Contended values retained; quiet re-measurement deferred by owner decision. |
| S15 VFX | Contended values retained; quiet re-measurement deferred by owner decision. |
| S14 audio | Contended values retained; quiet re-measurement deferred by owner decision. |
| S07 environment scale (6/24/96/384) | Contended values retained; quiet re-measurement deferred by owner decision. |

Before the scope cut arrived, the original brief had already caused one S10 command to stop
at isolated import and one S09 command to complete. Neither result is used, retained in this
repository, or treated as a quiet remeasurement; after the decision arrived, no further
spike runner was started.

Direct filesystem editing was used for this documentation and evidence copy because the
Godot editor was unavailable. No scene, script, runner, acceptance criterion, or saved
identity changed.
