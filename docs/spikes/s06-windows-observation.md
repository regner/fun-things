# S06 — Windows topology proof and drawn review captures

> **Historical run instructions.** Commands in this record that target `prototypes/` describe
> the original runnable checkout; they do not run in the current checkout because the archive
> is hidden by `.gdignore`. To reproduce them, follow the
> [restore-from-Git procedure](../../prototypes/README.md) in a separate worktree at the recorded
> pre-cleanup commit.

8 October 2026, Windows 11 desktop, NVIDIA GeForce RTX 4070 Laptop GPU,
D3D12 Forward+, pinned `4.8.dev7.official.c971f93e7`. This reruns the accepted
partial topology proof and supplies drawn material for a human layout review. It
does **not** ratify the layout, camera, crossing, minimap or body dimensions.
[Evidence](s06-windows-evidence/).

The Godot editor was not running and no MCP editor tools were available. The new
capture tool and observer were authored as text. The observer instances each saved
intersection scene in an external copied project and uses `S06Fixture.start_route`;
it does not edit a scene or write a body pose. Each capture records the camera,
public body position, minimap marker world position and both projected minimap
positions in the matching [`observation.json`](s06-windows-evidence/captures/camera-42/observation.json).

## Windows proof rerun

Both fresh external runs passed with no engine diagnostics and unchanged copied
fixture/model bytes:

| Mode | Result | Checks / trajectories | Receipts |
| --- | --- | --- | --- |
| Full | PASS | 47 content checks plus 15 route outcome checks; foot 477 ticks, east→north 721, west→south 721; no failure | [summary](s06-windows-evidence/proof-full/summary.json), [result](s06-windows-evidence/proof-full/s06-result.json), [log](s06-windows-evidence/proof-full/proof.log) |
| `--content-only` | PASS | 47 content checks; no body route run | [summary](s06-windows-evidence/proof-content-only/summary.json), [result](s06-windows-evidence/proof-content-only/s06-result.json), [log](s06-windows-evidence/proof-content-only/proof.log) |

The commands were:

```text
python prototypes/s06/tools/s06/run.py --godot <mise 4.8-dev7 godot.exe> --output C:\tmp\ft\lanes\s06\full
python prototypes/s06/tools/s06/run.py --godot <mise 4.8-dev7 godot.exe> --content-only --output C:\tmp\ft\lanes\s06\content-only
```

No Windows-specific proof harness correction was needed.

## Automatic drawn captures

`prototypes/s06/tools/s06/capture_windows.py` imported one fresh external copy, then launched
`intersection.tscn` and inherited `intersection_wide.tscn` windowed at 1280×800.
Both processes exited 0 with no diagnostic lines. Each produced one static frame
and three frames during each existing route. All 20 PNG saves passed. Every captured
marker/body difference is 0 m and 0 px in the receipts. Both camera runs again
completed foot/east→north/west→south in 477/721/721 ticks without timeout.
The runner is bound to clean tool revision `6b9bfb95d049d45cbe2baeb326779b3deb1db678`;
see its [complete result](s06-windows-evidence/captures/result.json). The command was:

```text
python prototypes/s06/tools/s06/capture_windows.py --godot <mise 4.8-dev7 godot.exe> --output C:\tmp\ft\lanes\s06\windows-captures
```

| Saved camera | Static | Foot crossing | Eastbound → northbound left turn | Westbound → southbound left turn |
| --- | --- | --- | --- | --- |
| 42°, 47 m | [static](s06-windows-evidence/captures/camera-42/static.png) | [120](s06-windows-evidence/captures/camera-42/foot-120.png), [240/seam](s06-windows-evidence/captures/camera-42/foot-240.png), [360](s06-windows-evidence/captures/camera-42/foot-360.png) | [180](s06-windows-evidence/captures/camera-42/east_to_north-180.png), [360/junction](s06-windows-evidence/captures/camera-42/east_to_north-360.png), [540](s06-windows-evidence/captures/camera-42/east_to_north-540.png) | [180](s06-windows-evidence/captures/camera-42/west_to_south-180.png), [360/junction](s06-windows-evidence/captures/camera-42/west_to_south-360.png), [540](s06-windows-evidence/captures/camera-42/west_to_south-540.png) |
| 50°, 47 m | [static](s06-windows-evidence/captures/camera-50/static.png) | [120](s06-windows-evidence/captures/camera-50/foot-120.png), [240/seam](s06-windows-evidence/captures/camera-50/foot-240.png), [360](s06-windows-evidence/captures/camera-50/foot-360.png) | [180](s06-windows-evidence/captures/camera-50/east_to_north-180.png), [360/junction](s06-windows-evidence/captures/camera-50/east_to_north-360.png), [540](s06-windows-evidence/captures/camera-50/east_to_north-540.png) | [180](s06-windows-evidence/captures/camera-50/west_to_south-180.png), [360/junction](s06-windows-evidence/captures/camera-50/west_to_south-360.png), [540](s06-windows-evidence/captures/camera-50/west_to_south-540.png) |

At the seam frames, the foot is `(0.000005, 0.001, 6.5)` and its minimap marker is
`(80.000015, 99.5)` px. At the opposing junction frames, east→north is
`(0.139926, 0, 0.663153)` with marker `(80.419777, 81.989456)` px, and west→south
is `(-0.139926, 0, -0.663153)` with marker `(79.580223, 78.010536)` px. Values are
the same in both camera variants because only FOV differs.

## Human ratification checklist

Use the linked full-size PNGs and check each item explicitly; this record claims no
human approval.

- **Layout dimensions:** confirm the drawn 48×48 m road extent, 9 m carriageways and
  4 m sidewalks read as the intended provisional block scale with the actual
  1.8 m-tall/0.38 m-radius actor and 1.88×1.54×3.4 m car visual.
- **Lane widths and turns:** inspect both 180/360/540 sequences for lane centering,
  whole-car clearance, believable left-turn shape and exit alignment. The existing
  sampled collision proof passes, but visual desirability remains a human decision.
- **Crossing:** inspect foot 120/240/360 for approach continuity, the marked 3 m
  crossing at Z=6.5, seam passage and whether the marking is prominent enough.
- **Minimap orientation/readability:** confirm world +X reads right and +Z reads
  down, the road cross matches the world, and the coral marker remains legible at
  the recorded positions. Exact marker projection is measured; readability is not.
- **42° versus 50°:** compare matched captures. The historical analytical spans are
  about 57.73×36.08 m at 42° and 70.13×43.83 m at 50°. Decide whether tighter body
  readability or wider route context is preferred; neither view contains every
  48 m road extent vertically.

## Limits

These captures show one provisional flat fixture on one Windows GPU. They do not
approve final body envelopes, handling, controls, physical-input feel, street art,
raised curbs/slopes, opposing traffic, contested crossings, recovery, population,
capacity, Linux/Deck or production. Full S06 and the existing product gates remain
open. Any final S02/S04 dimension or authored layout change still requires affected
route/contact/seam/map reruns.
