# S07 — Graphical T calibration on a Windows desktop

8 October 2026. The user authorized testing on this machine. This adds a graphical
layer to the accepted [sustained driver](s07-sustained-driver.md) and runs the
[T primary card](s07-run-cards.md) shape: 60 s warmup plus 600 s measured,
uncapped and 60-capped, three repeats each. [Evidence](s07-graphical-t-evidence/)
keeps summaries, per-case results, frame metadata and memory samples. The three capped
runs' raw frame and traversal samples are retained with deterministic gzip compression;
[`raw-manifest.json`](s07-graphical-t-evidence/s07g-capped/raw-manifest.json) binds source
and compressed byte counts and SHA-256s.

## Setup

| Item | Value |
| --- | --- |
| Hardware/OS | NVIDIA GeForce RTX 4070 Laptop GPU, Windows 11 10.0.26200, D3D12 12_0, Forward+ |
| Build | Pinned editor binary `4.8.dev7.official.c971f93e7`. Editor-binary runs are **labeled diagnostics** under the card; no exported graphical build was used. |
| Revision | `6efa3c9` (clean staged inputs) |
| Window/quality | 1280×800 windowed, project defaults; VSync disabled; `Engine.max_fps` 0 (uncapped) or 60 (capped60) |
| Content/route | Unchanged S06 two-sector intersection via the accepted driver: foot, east→north, west→south in turn; a saved-fixture reload per traversal |
| Telemetry | [`tests/fixtures/s07_graphical/run.gd`](../../tests/fixtures/s07_graphical/run.gd) subclasses the driver and logs per drawn frame: interval, `viewport_get_measured_render_time_cpu/gpu`, `TIME_PROCESS`/`TIME_PHYSICS_PROCESS`, draw calls, primitives, objects and video memory, held in memory until exit. [`tools/s07_graphical/run.py`](../../tools/s07_graphical/run.py) samples the owned process's working set every second. |
| Not measured | OS frame-pacing/presentation capture, GPU vendor tool capture, thermal/power state (laptop on its current power plan), cold-start/exported launch |

## Results — 60-capped (3/3 PASS)

All three cases ran 62 traversals each, with exit 0, no diagnostics and no driver
failures. Measured phase, about 602 s and 36,108–36,120 frames per run:

| Metric (measured) | Run 1 | Run 2 | Run 3 |
| --- | --- | --- | --- |
| Mean FPS | 59.99 | 59.98 | 60.00 |
| Frame interval p50 / p95 / p99 / max (ms) | 16.67 / 17.82 / 18.67 / 87.2 | 16.67 / 17.86 / 18.73 / 240.3 | 16.67 / 17.86 / 18.73 / 42.2 |
| Render CPU p95 / max (ms) | 0.48 / 2.93 | 0.48 / 3.51 | 0.47 / 3.62 |
| Render GPU p95 / max (ms) | 2.05 / 5.14 | 2.05 / 4.04 | 2.05 / 5.08 |
| Physics p95 / p99 (ms) | 3.87 / 4.57 | 3.79 / 4.68 | 3.79 / 4.33 |
| Frames > 33.4 ms | 46 | 45 | 43 |
| Draw calls / primitives / objects (constant) | 63 / 4,256 / 65 | same | same |
| Video memory max | 82.9 MB | 84.5 MB | 82.1 MB |
| Working set p50 / max | 363 / 367 MB | 363 / 366 MB | 360 / 362 MB |

Independent analysis of the retained raw samples gives:

| Hitch analysis | Run 1 | Run 2 | Run 3 |
| --- | --- | --- | --- |
| Long frames >33.4 ms | 46 | 45 | 43 |
| In load or teardown windows | 42 | 42 | 43 |
| Traversal-only interval p95 (ms) | 17.797 | 17.838 | 17.834 |
| Traversal-only interval p99 (ms) | 18.518 | 18.577 | 18.565 |
| Traversal-only interval max (ms) | 87.195 | 240.285 | 25.78 |

- **Hitches are predominantly lifecycle work.** The load window is
  `[load_start_seconds, traversal_start_seconds + 0.1]`; teardown is
  `[traversal_end_seconds - 0.05, retired_seconds + 0.1]`. Those are reported
  saved-scene reload phases, not route cost. Traversal-only intervals use
  `[traversal_start_seconds + 0.1, traversal_end_seconds - 0.05]`. The 87.195 ms
  and 240.285 ms traversal outliers are unattributed and may be OS scheduling.
  [`analyze_hitches.py`](s07-graphical-t-evidence/analyze_hitches.py) reads only the
  retained gzip inputs and reproduces the committed
  [`hitch-analysis.json`](s07-graphical-t-evidence/hitch-analysis.json).
- Against the design's provisional desktop targets (frame p95 ≤ 16.67 ms, p99
  ≤ 20 ms, sustained 60 FPS; host simulation p95 ≤ 4 ms): p99 and the mean rate
  pass, and physics p95 (3.8 ms) is just inside 4 ms. **p95 17.8 ms exceeds
  16.67 ms**, which is expected for a non-VSync `max_fps` limiter whose interval
  jitters around the cap. Judge it with presentation-timed VSync before treating
  it as a breach. This is a desktop observation, not Deck evidence.
- Physics p95 of 3.8 ms for one moving body is mostly fixed driver/S06 per-tick
  cost, not scaled AI or population load.
- `TIME_PROCESS` p95 is about 21 ms in every run. That idle-time-inclusive
  monitor rises when the frame waits on the cap, so it is not used as a budget.

## Results — uncapped (FAILED, environment)

Both uncapped attempts (the planned first case and one controlled rerun) reported
**GPU device removal** (`DXGI_ERROR_DEVICE_REMOVED` 0x887A0005). A later System-log
query for 21:00–22:15 retained six NVIDIA `nvlddmkm` event 153 errors: one at
21:11:36, two at 21:12:05, one at 22:02:02 and two at 22:02:30 local time. No
`Display` provider event matched. The compact query result is
[`windows-system-events.json`](s07-graphical-t-evidence/windows-system-events.json).

The first process exited with 0xC0000005. Its retained traversal stream contains 34
completed traversals, last retired at 442.302784 s; memory sampling continued through
563.252 s. The rerun exited with code 4294967295. It retained 10 completed traversals,
last retired at 382.392357 s, and memory samples through 492.160 s. The retained
working-set p50/max pairs are 389,906,432/401,895,424 bytes and
380,956,672/384,065,536 bytes respectively. These bounded samples show no resident-set
increase matching the prolonged error period, but do not diagnose the removal.
Compressed traversal streams, memory samples, complete-log hashes and counts, and
60-line stderr excerpts are retained in each uncapped case's evidence directory; full
5–12 MB error logs are not committed.

The retained 30 s smoke case at the same revision reports measured mean 978.576 FPS
and render GPU p95 0.173 ms before the failures. Whether the trigger is the laptop
driver/thermal limits under high uncapped load or a Godot D3D12 defect is unknown.
Uncapped headroom on this machine is therefore **not measured**. The card's single
controlled rerun is spent. As of the runner-safety follow-up, uncapped mode is withdrawn:
the runner and fixture accept only an explicit 60 FPS cap because uncapped execution caused
`DXGI_ERROR_DEVICE_REMOVED` on this laptop. Historical failure evidence above is retained;
any future higher-cap experiment requires a separately reviewed changed condition.

## Scope

This is T calibration for one desktop: a small two-sector scene (63 draw calls)
with one moving body. It is not capacity, R/G representativeness, Deck
performance or an exported-build result, and it makes no optimization or budget
decision. The comparator (S05 burst) case still needs the C0 trial-reset driver.
Graphical R/G remain blocked on Regner's D1–D4 decisions.
