# S07 C0 — fresh-session effect comparator driver

8 October 2026. This implements the bounded C0 prerequisite for the separate S05
comparator in [technical card T](s07-run-cards.md#t--technical-two-sector-calibration-blocked-not-representative-capacity).
It is a standalone correctness driver and short draw smoke, not any of the card's
six cap/repeat measurements, a 600-second capacity run, or representative R/G
acceptance. [Retained evidence](s07-comparator-driver-evidence/).

## Ownership and implementation

[`tests/fixtures/s07_comparator/run.gd`](../../tests/fixtures/s07_comparator/run.gd)
is only an experiment coordinator. It parameterizes trial count, initial delay and
spacing (bounded by the card's 20 trials, 15-second initial delay and 30-second
spacing), and defaults to the measured schedule `t = 15 + 30k`. It loads the saved
[`s05_effect/burst.tscn`](../../tests/fixtures/s05_effect/burst.tscn) afresh for every
trial, removes the inherited finite-proof coordinator before tree entry, sets the
new match's standalone authority/session before adding it to the tree, and leaves
all saved cars passive through their pre-tree role setup. It does not add a gameplay
writer or an in-place reset API.

Each trial validates the literal 4 m saved grid, zero velocity and passive collision,
then calls unchanged `S05Match.prepare_initial`, `admit`, `context` and `submit_fire`
to fire one root. `S05Damage` remains the sole damage/lifecycle writer and
`S05SavedPresentation` the sole cosmetic writer. After the accepted chain finishes,
the coordinator uses existing rollback/clear boundaries, verifies no active job or
local effect, queues the whole fixture for deletion, observes it freed, and only
then loads the next saved fixture. It never calls `begin` to reuse an old session and
never assigns a saved pose.

Fresh-session checks retain a previous intent, event and callback. On the next trial,
the old intent/event are rejected by the new session and the callback/object is
invalid after observed retirement. Root and all 12 body instance IDs must also differ
from the previous trial. Literal independent checks require 12 wreck rows, one blast
per row, 12 completed jobs × 12 visits = 144 visits, peak four target visits per tick,
zero held/body velocity, and all saved positions restored. Effect expectations are
not fixed at eight/four: expected drawn is `min(actual explosions, configured saved
slot count)` and expected drops are `max(0, actual explosions - configured saved slot
count)`. The current 12-explosion/eight-slot fixture therefore expects eight/four; a
12-slot fixture expects all 12/zero. Loading, first draw, chain and reset spans are
separate receipt fields.

The graphical path instances the existing saved S05 observation camera, subscribes
to `RenderingServer.frame_post_draw`, and captures only after the configured expected
number of saved slots are visible in-tree with the derived drop count. It records the
actual explosions, configured slots, derived expectations, completed render index,
linked mesh nodes, `window_can_draw`, viewport dimensions/hash and a PNG per trial.
The node hierarchy remains authored in the existing S05 scenes; no new scene was
hand-authored. The editor was not running and no MCP editor tools were available, so
the new script, runner and documentation were edited directly. A pinned headless
editor import generated the script UID sidecar; its known project-plugin diagnostics
were not treated as validation. Runtime staging removes addon/autoload/plugin sections.

[`tools/s07_comparator/run.py`](../../tools/s07_comparator/run.py) stages a minimal
fresh external project, verifies the pinned engine, imports once, applies one absolute
run deadline, scans all streams for diagnostics, checks the complete trial receipts,
verifies staged inputs byte-for-byte, requires clean source inputs, and terminates or
kills only its own child if needed. The run uses standalone authority and no ENet port.
Offline evaluator tests corrupt sessions, visits, lifecycle flags, draw visibility,
drawability and PNG save status.

## Development observations

Both commissioned runs used pinned `4.8.dev7.official.c971f93e7`, revision
`26e6e16711b0f41a13d45545d6bea84c76c4c0b7`, fresh output under
`C:\tmp\ft\lanes\c0\`, and clean staged inputs. Import and runtime exited 0 with no
scanned `ERROR`, `SCRIPT ERROR` or `WARNING`; inputs were preserved and the owned
child was reaped.

| Group | Schedule and result | Separate phase spans |
| --- | --- | --- |
| Headless development | 20/20 fresh standalone trials, compressed `t = 0 + 2k`; all literal gameplay, stale-session, placement, velocity, cleanup and retirement criteria passed. Total driver elapsed 38.803 s. | load 0.021–0.180 s; chain 0.635–0.785 s; reset 0.0006–0.0029 s. First draw is explicitly unavailable headless. |
| Windowed smoke | 3/3 fresh trials, `t = 0 + 2k`; all gameplay checks plus the configured eight DRAWN saved slots/four derived drops on every trial. Total driver elapsed 4.861 s. | load 0.029–0.374 s; first draw 0.0018–0.0383 s; chain 0.799–0.822 s; reset 0.0009–0.0011 s. |

All three 1280×800 burst captures have the deterministic SHA-256
`e69bf878890d76ef7b90aa296038ad620d8ebc206095a05ab412dfe5ee5f425c`.
Each receipt reports `visible: 8`, `visible_in_tree: 8`, `mesh_nodes: 8`,
`dropped: 4`, `can_draw: true`, and a successful PNG save through the saved camera.
See [trial 1](s07-comparator-driver-evidence/windowed-3/trial-01-burst.png),
[trial 2](s07-comparator-driver-evidence/windowed-3/trial-02-burst.png), and
[trial 3](s07-comparator-driver-evidence/windowed-3/trial-03-burst.png).

Reproduction, with fresh external directories:

```sh
python tools/s07_comparator/run.py --output C:/tmp/ft/lanes/c0/headless-20 \
  --trials 20 --initial-delay 0 --spacing 2
python tools/s07_comparator/run.py --output C:/tmp/ft/lanes/c0/windowed-3 \
  --trials 3 --initial-delay 0 --spacing 2 --windowed
python -m unittest tools/s07_comparator/test_offline.py
```

## Limits and disposition

C0's executable fresh-session reset/event prerequisite and short saved-camera draw
smoke pass these development observations. The owner has since decided to remove the
on-screen explosion cap so every explosion gets an effect. That later S05 change is
outside this lane; this driver is ready for it because expectations come from the
fixture's configured slot capacity and actual completed explosions rather than an
immutable eight/four rule. The comparator's planned uncapped/60-capped × three-repeat
card cases remain unexecuted and still require the card's named build, hardware and
telemetry launch decision. The smoke is not a frame-cost, VSync,
headroom, 600-second capacity, ENet, in-flight join, production VFX, Match reset,
player death, Linux, Deck, or final-dimension result. It does not change S05 tuning,
identity limits, gameplay ownership or presentation policy. Full S07, R/G, P0 and M1
remain open.
