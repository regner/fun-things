# S08-C — pinned-engine stability triage

9 October 2026. This is the bounded G6 follow-up to the historical S07-ENV
384-block `0xC0000005` process exit. It diagnoses saved-scene instantiation on the
current Godot `4.8.dev7.official.c971f93e7` pin and documents a safe GPU measurement
method. It does not raise the city-planning envelope, change a product budget, or certify
384 blocks for production.

[Evidence](s08-c-stability-evidence/) retains the tested source manifest, runner results,
raw short frame streams, memory samples, logs, process-count labels, and Windows Error
Reporting configuration receipt. Direct text editing was used for documentation and tool
changes because the Godot editor was not running and MCP editor mutation tools were
unavailable. The existing procedural authoring script produced the two new saved scenes.

## Historical failure and current content

The original retained run at revision `4e1021ef2bb4339937ca42a22c0722917f244009`
exited `3221225477` (`0xC0000005`) about four seconds after launch, before result or
frame telemetry. Its four memory samples reached 276,971,520 bytes. The engine log had
renderer identity but no diagnostic or backtrace. That scene expanded building instances
with the S02 cutaway script and per-instance materials.

Owner decision 3 subsequently removed cutaway. Commit `d6179af` removed the script and
shader references from the three building prefabs, all four original S07-ENV variants,
and runner staging. The current 192-, 288-, and 384-block scenes contain no
`building_view` or `actor_cutaway` reference. This task did not recreate deleted cutaway
behavior merely to provoke another crash.

The bounded bisect adds linked 16×12 and 18×16 saved variants through the existing
procedural authoring path. They preserve the same six prefab instances per block and do
not create render meshes.

| Blocks | Fresh processes | Result | Expanded nodes / colliders | Max working set | Contention label |
| ---: | ---: | --- | ---: | ---: | --- |
| 192 | 1 | exit 0, instantiated and drew | 26,502 / 1,536 | 463.5 MiB | contended, 6 Godot processes before / 8 after |
| 288 | 1 | exit 0, instantiated and drew | 39,750 / 2,304 | 498.6 MiB | contended, 8 before / 6 after |
| 384 | 2 | both exit 0, no diagnostics | 52,998 / 3,072 | 536.3 / 537.8 MiB | contended low-process attempt, 5 before / 3 after |

The 192/288 diagnostics deliberately used a one-second measured interval and zero warmup.
Their first-load frame made p99 exceed 20 ms, so the existing growth-stop guard ended each
variant after its first successful process. Those p99/FPS values are invalid for frame
performance; the rows establish only that saved loading, instantiation, tree entry, and
rendering completed.

The single bounded 384 rerun used a one-second warmup and one measured second per fresh
process. Both repeats remained capped at 60 FPS. Their cold first-load times were 865.006
and 556.086 ms, frame-interval p99 was 18.490 and 18.081 ms, and renderer-reported GPU
p99 was 0.246 and 0.344 ms. These timing values are **contended short diagnostics**, not a
replacement scale envelope.

Before that rerun, the worker temporarily configured per-executable Windows Error
Reporting minidumps (`DumpType=1`, count 2) under HKCU. Both processes exited normally,
so there was no exception from which Windows could produce a dump or backtrace. The
registry key was removed afterward. The absence of a dump is a non-reproduction result,
not missing crash evidence.

The retained [`run_with_wer_dumps.sh`](../../prototypes/s07_env/tools/s07_env/run_with_wer_dumps.sh) now
makes that transaction reproducible. It refuses to replace an existing per-executable
key, applies and queries `DumpFolder`/`DumpType`/`DumpCount`, bounds the runner, and uses
EXIT/INT/TERM cleanup to delete only its created key and query for absence. A registry-only
replay retained [pre/configured/post receipts](s08-c-stability-evidence/wer-procedure-check/)
and left the key absent. Exact commands are in the evidence `commands.txt`; the valid JSON
receipt records the same apply and revert operations.

## Disposition

The access violation is **not reproducible with the current no-cutaway 384-block saved
scene**. Successful 192, 288, and two 384 instantiations reject the narrow hypothesis that
Godot 4.8-dev7 deterministically fails merely because this linked saved scene contains
about 53,000 expanded nodes. It is therefore not classified as a demonstrated engine
defect in large saved-scene instantiation.

The historical crash cause remains unknown. The changed cutaway/material path and a
transient engine, driver, or concurrent-workstation condition are all possible, but this
bounded run cannot distinguish them. Do not claim that cutaway caused the crash. Keep 96
blocks as the last fully measured planning row; 384 is only a short stability
non-reproduction. Escalate only if the access violation returns in current content, at
which point the enabled-dump recipe should yield a dump for debugger analysis.

## Safe GPU measurement on this workstation

The normative workflow is now in [development.md](../development.md#safe-capped-gpu-measurement).
In short: never run uncapped rendering on this machine; set the cap before loading measured
content; collect post-draw viewport GPU/CPU timings and wall-clock frame intervals after a
warmup; and retain renderer, adapter, resolution, cap, logs, raw samples, and Godot-process
contention. Renderer timings provide capped workload headroom, not presentation latency or
an uncapped maximum-FPS claim.

## Owner question and planning text

`docs/design.md` was intentionally not edited. Owner question: replace the frame-time
row's “Record CPU/GPU times uncapped for headroom” clause with:

> Record capped frame intervals and `RenderingServer` viewport CPU/GPU timings after
> warmup for headroom. Do not run uncapped on hardware with a device-removal history;
> use named capped quality/content sweeps when additional headroom comparison is needed.

Suggested `docs/plans/task-requirements.md` one-liner (not applied):

> **S08-C:** Bounded no-cutaway 192/288/384 stability triage passed on the pin; the
> historical access violation did not reproduce, no dump was generated, and capped
> `RenderingServer` GPU timing is the safe workstation method. See
> `docs/spikes/s08-c-stability.md`.

Suggested TODO bullet (not applied):

> - [ ] **P0-GATE owner decision:** replace the unsafe uncapped GPU-headroom instruction
>   in `docs/design.md` with the S08-C capped `RenderingServer` timing method.
