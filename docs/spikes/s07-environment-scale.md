# S07 — visual environment scale envelope

8 October 2026. This is a **visual/graphical environment planning investigation**, not
a capacity requirement or release gate. It measures saved static roads/buildings while a
single observer traverses them. Network, AI, population, actors, cars, combat, effects,
replication and authority are intentionally out of scope because those systems depend on
the players' surroundings rather than total city extent. The result guides how large a
city to plan; it does not authorize a larger M1 district or establish a universal maximum.

[Evidence](s07-environment-scale-evidence/) retains summaries, per-case results, raw frame
samples, memory samples, complete short logs and fixed-camera captures of passing rows.
`SHA256SUMS` binds all evidence files and
`manifest.json` binds each generated scene's size, SHA256, saved node entries, saved prefab
instances and clean run revision. The initially incomplete staged shader dependency and its
failure remain under `initial-missing-shader/`; the runner was corrected narrowly before
accepted measurements.

## Authored content and method

[`author_city.gd`](../../tools/s07_env/author_city.gd) is intentional procedural
**authoring**, never runtime city generation. It instances existing saved S06 west/east
road sectors and S02 low/near/tall building prefabs, then saves their unique names and
transforms. It creates no mesh, material, collision geometry or topology. Its exact grid,
spacing, density and camera parameters are in the adjacent
[README](../../tools/s07_env/README.md).

Each 48 m-pitch block has both road-sector halves and four buildings at the existing
16.25 m island centres. Thus every block retains S06's 9 m carriageways and 4 m sidewalks,
with six top-level saved prefab instances per block. Heights rotate low/near/tall/low
between neighboring blocks. All four generated scenes are below the 2 MiB retention limit,
so they are committed rather than represented only by hashes.

| Blocks / grid | Saved scene | Size | Saved entries / prefab instances | Expanded nodes / static colliders |
| ---: | --- | ---: | ---: | ---: |
| 6 / 3×2 | `city_6.tscn` | 9,895 B | 42 / 36 | 834 / 48 |
| 24 / 6×4 | `city_24.tscn` | 34,378 B | 150 / 144 | 3,318 / 192 |
| 96 / 12×8 | `city_96.tscn` | 132,788 B | 582 / 576 | 13,254 / 768 |
| 384 / 24×16 | `city_384.tscn` | 527,038 B | 2,310 / 2,304 | not reached; composition implies 52,998 / 3,072 |

The final row's expanded counts are the exact successful-series relations
`nodes = 138 × blocks + 6` and `colliders = 8 × blocks`, not observations from the
crashed process. Scene SHA256s are in the manifest.

[`run.py`](../../tools/s07_env/run.py) stages only required linked fixtures/models and
sanitized `project.godot` in a fresh external directory. Its clean-input query includes
`project.godot`, the runner/authoring directory, generated scenes, source fixtures and
models. One import warms the import cache; every repeat then starts a fresh process in
which the scene has not yet loaded. The fixture records resource-load time and first
load through instantiation/tree entry/one frame, frees that instance, performs a cached
warm reload, then measures the second instance.

The saved 42°/47 m top-down camera follows a deterministic lawnmower route through block
centres at 15 m/s. Runs are windowed 1280×800, VSync disabled and capped at 60 FPS. There
were two repeats per passing variant, each with 10 s warmup then 30 s measured. The next
variant was authored only after its predecessor remained comfortably within load, RAM and
frame limits. The run stopped immediately when 384 blocks crashed, so it correctly has no
second repeat.

| Environment | Observed value |
| --- | --- |
| Hardware/OS | `Intel64 Family 6 Model 170 Stepping 4, GenuineIntel`; NVIDIA RTX 4070 Laptop GPU; Windows 11 10.0.26200 |
| Renderer/build | D3D12 12_0, Forward+, pinned editor binary `4.8.dev7.official.c971f93e7` |
| Run identity | Clean per-variant revisions listed in `manifest.json`; external roots were `C:/tmp/ft/lanes/s07-env/` |
| Scope not measured | Exported build, OS presentation capture, power/thermal state, Deck, textures/production art, actors/effects/network/AI/population |

## Results and stop disposition

Passing rows report the mean of two repeat summaries. RAM is mean sampled maximum working
set; video memory is the maximum `RENDER_VIDEO_MEM_USED` monitor value. These accounting
domains must not be added, particularly on a shared-memory device.

| Blocks | Cold first load / warm reload (ms) | RAM max (MiB) | Frame interval p50 / p95 / p99 (ms) | Mean FPS | Video memory max (MiB) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 296.2 / 29.0 | 355.7 | 16.664 / 17.483 / 17.997 | 60.00 | 102.8 |
| 24 | 306.3 / 57.6 | 360.2 | 16.664 / 17.337 / 18.042 | 60.00 | 147.8 |
| 96 | 376.9 / 181.6 | 423.6 | 16.670 / 17.435 / 18.405 | 59.86 | 328.1 |
| 384 | process crashed before result | sampled max 264.1 | unavailable | unavailable | unavailable |

| Blocks | Render CPU p50 / p95 / p99 (ms) | Render GPU p50 / p95 / p99 (ms) | Physics p50 / p95 / p99 (ms) |
| ---: | ---: | ---: | ---: |
| 6 | 0.341 / 0.480 / 0.571 | 1.858 / 2.130 / 2.179 | 0.444 / 1.004 / 1.103 |
| 24 | 0.447 / 0.618 / 0.977 | 1.943 / 2.181 / 2.238 | 0.106 / 0.550 / 0.614 |
| 96 | 0.490 / 0.685 / 1.149 | 1.918 / 2.154 / 2.202 | 0.100 / 0.153 / 0.242 |

Physics is an engine monitor sampled at draw completion and the scene is static, so its
small non-monotonic variation is timing noise rather than evidence that larger layouts
reduce physics cost.

| Blocks | Draw calls p50 / p95 | Objects p50 / p95 | Primitives p50 / p95 |
| ---: | ---: | ---: | ---: |
| 6 | 58 / 64 | 68 / 72 | 4,512 / 5,424 |
| 24 | 57 / 64 | 68 / 72 | 4,464 / 5,110 |
| 96 | 59 / 65 | 68 / 72 | 4,535 / 5,204 |

Stable in-frame render counts support the expected local-view behavior: automatic frustum
and far-plane culling keep visible density nearly fixed while total saved/resident content
grows. This says nothing about required off-camera simulation, which is outside this run.

The 384-block process exited with Windows code `0xC0000005` about four seconds after
launch, before `result.json` or frame telemetry. Its logs contain the renderer identity and
no engine diagnostic; four OS samples reached 264.1 MiB. Cause is unknown. A crash itself
is a predeclared stop condition, so **96 blocks is the last passing observed row and 384
blocks the first failing row**. No retry, tuning, uncapped run or larger variant was made.
The failing sample is not evidence that 384 blocks consumes only 264.1 MiB.

All passing rows are well below 30 s first/warm load, 2 GiB working set and 20 ms measured
frame p99. This is therefore an observed desktop envelope of at least 96 blocks for this
shared grey-block content—not a product map limit. The 384 crash prevents interpolation
from being treated as admission evidence.

## Per-block fit and art-residency adjustment

A simple least-squares line over the three passing row means gives:

| Cost | Fitted line for `B` blocks | Increment per block |
| --- | --- | ---: |
| Cold first load | `0.2878 + 0.000921 B` seconds | 0.921 ms |
| Warm reload | `0.0179 + 0.001703 B` seconds | 1.703 ms |
| Working set | `346.6 + 0.790 B` MiB | 0.790 MiB |
| Expanded nodes | `6 + 138 B` | 138 nodes |
| Static colliders | `8 B` | 8 colliders |

Three points with shared assets are enough for a planning slope, not a predictive model.
Cold-load fixed startup dominates small rows; caches, allocation thresholds and the first
failing crash can make larger behavior nonlinear. `RENDER_VIDEO_MEM_USED` separately fit
about `87.8 + 2.503 B` MiB, but that engine estimate includes per-instance cutaway
materials and is not used as a dedicated-VRAM budget.

The grey-block scenes reuse five tiny imported models and their materials. Production
residency will be materially higher. If production contributes **K unique MiB of art per
block**, a rough RAM planning adjustment is:

`adjusted working set ≈ 346.6 + (0.790 + K) × B MiB`.

For illustration only, at 96 blocks K=1/4/8 adds 96/384/768 MiB beyond this fixture. A
naive 2 GiB crossing from that line would be roughly 950/355/193 blocks respectively,
but these are not admitted sizes: asset loading/upload, textures, LODs, shaders, driver
allocation and the observed 384-block crash invalidate literal extrapolation. On Deck,
CPU and GPU allocations share about 16 GB, so do not add this desktop RAM line to the
video-memory monitor as if they were disjoint pools.

## Planning guidance and caveats

- Plan against the **last observed passing static layout (96 blocks)** only as graphical
  grey-block headroom. Keep the six-block M1 district unchanged until product scope says
  otherwise. Do not use the fit to waive integrated M1-D3 testing.
- City-size residency/load scales with total saved instances; local frame rendering mostly
  tracks visible density. The nearly flat draw/object/primitive and GPU rows demonstrate
  that distinction for this camera, far plane and repeated content.
- Reusing the same road/building meshes and simple materials substantially understates
  production art residency and shader/texture variety. Repeat representative rows after
  real production subsets exist.
- The 384 crash needs a separate bounded diagnosis before anyone treats layouts between
  96 and 384 as usable. This investigation deliberately made no renderer, streaming,
  batching, LOD or scene-granularity change.
- Deck was not measured. It has about 16 GB shared RAM and a much weaker GPU. City-wide
  residency remains relevant there, while frame cost should still mostly follow local
  visible density; only native 1280×800 device evidence can validate that inference.
- Network, AI and population remain out of scope by owner decision. Their independent
  local-surroundings and lifecycle costs belong to integrated gameplay experiments, not
  this environment-size guidance envelope.

Direct text editing was used because the Godot editor was not running and no MCP editor
mutation tools were available. The pinned engine authored and loaded every generated saved
scene. No new render mesh was generated and no existing UID or source asset was changed.
