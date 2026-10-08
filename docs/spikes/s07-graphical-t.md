# S07 — Graphical T calibration on a Windows desktop

8 October 2026. The user authorized testing on this machine. This adds a graphical
layer to the accepted [sustained driver](s07-sustained-driver.md) and runs the
[T primary card](s07-run-cards.md) shape: 60 s warmup plus 600 s measured,
uncapped and 60-capped, three repeats each. [Evidence](s07-graphical-t-evidence/)
keeps summaries, per-case results, frame metadata and memory samples; raw
per-frame binaries (5–40 MB each) were not committed.

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

- **Hitches are lifecycle work.** Of the 43–46 long frames per run, 42–43 fall
  within the driver's per-traversal load or teardown windows. Those are reported
  phases (saved-scene reload), not route cost. Traversal-only frames have p95
  17.8 ms, p99 18.5–18.6 ms and max 25.8–240 ms. The two traversal outliers
  (87 ms, 240 ms) are unattributed and may be OS scheduling. This analysis was
  run on the raw frame binaries and is reproducible with them; only summaries
  are retained.
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

Both uncapped attempts (the planned first case and one controlled rerun) ended in
**GPU device removal** (`DXGI_ERROR_DEVICE_REMOVED` 0x887A0005). NVIDIA
`nvlddmkm` event 153 was logged at 21:11/21:12 and again at 22:02. The first
attempt then crashed (0xC0000005) after about 442 s and 34 traversals. The rerun
stalled into error spam about 2 minutes in and was stopped. The 30 s smoke run at
the same revision sustained about 978 FPS uncapped (render GPU p95 0.17 ms)
before this showed up. Resident memory stayed flat (about 380–400 MB), so this is
not a project leak. Whether the trigger is the laptop driver/thermal limits under
roughly 1000 FPS or a Godot D3D12 defect is unknown. Uncapped headroom on this
machine is therefore **not measured**. The card's single controlled rerun is
spent, and a further attempt needs a changed condition (another GPU or driver,
Vulkan, or an FPS ceiling above 60 such as 240).

## Scope

This is T calibration for one desktop: a small two-sector scene (63 draw calls)
with one moving body. It is not capacity, R/G representativeness, Deck
performance or an exported-build result, and it makes no optimization or budget
decision. The comparator (S05 burst) case still needs the C0 trial-reset driver.
Graphical R/G remain blocked on Regner's D1–D4 decisions.
