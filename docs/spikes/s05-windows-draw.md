# S05 — Windows drawn eight-slot saturation and settled hydration

8 October 2026, Windows 11 desktop (NVIDIA RTX 4070 Laptop GPU, D3D12 Forward+),
pinned `4.8.dev7.official.c971f93e7`. The user authorized testing on this machine.
This executes the previously unexecuted
[saved draw observer](../../prototypes/s05_draw/tests/fixtures/s05_draw/observer.gd) through a new
Windows runner,
[`prototypes/s05_draw/tools/s05_draw/observe_windows.py`](../../prototypes/s05_draw/tools/s05_draw/observe_windows.py).
[Evidence](s05-windows-draw-evidence/).

## Result

On clean revision `1f39df05`, one windowed set passed every runner criterion:
three real graphical ENet processes (host, live client, settled late joiner), all
exits 0, zero `SCRIPT ERROR`/`ERROR`/`WARNING` lines, empty stderr, unchanged copied
inputs, and a 12.6 s set duration.

| Role | Drawn stages (1280×800 PNG, `can_draw: true`) | Max visible slots | Post-draw callbacks |
| --- | --- | --- | --- |
| Host | baseline, **burst**, expired | 8 | 895 |
| Live client | baseline, **burst**, expired | 8 | 514 |
| Late joiner | baseline, **hydrated** | 0 | 17 |

- **Burst** frames show eight drawn explosion carriers with four cosmetic drops,
  through the saved observation camera, while the authoritative chain still
  finished all twelve cars. This is the first actual drawn eight-slot saturation
  receipt. See [client burst](s05-windows-draw-evidence/client/burst.png).
- **Expired** frames show natural local physics expiry of the live effects.
- **Hydrated**: the settled late joiner installs current state and draws **no**
  historical effects ([frame](s05-windows-draw-evidence/late/hydrated.png)). This
  matches the contract that hydration must not replay past effects.

## Fixture changes needed to run graphically

1. **Chain allowance.** The host checked `damage.tick <= 180` counted from host
   start. Windowed D3D12 startup took 4.75 s before the host was ready, plus the
   client's own graphical startup, so the first run failed that check after
   drawing the burst ([run 01](s05-windows-draw-evidence/run-01-absolute-allowance/)).
   [S05Proof](../../prototypes/s05/tests/fixtures/s05/proof.gd) now applies the same 180-tick bound
   from the first destroyed root, which keeps the prompt-chain intent without
   counting process startup.
2. **Queue pacing (headless, pre-existing).** The headless queue-pressure row
   failed deterministically on Windows, including at the base revision
   ([receipt](s05-windows-draw-evidence/queue-base-failure/)). Ten-millisecond timer
   polls let physics catch up several ticks between batches, so early jobs became
   due before all twelve were queued. The batch wait now awaits `physics_frame`,
   still under the fixture deadline. The full headless
   `prototypes/s05/tools/run_s05.py` (API, ENet with late joiner, queue) then passed
   ([result](s05-windows-draw-evidence/headless-runner/result.json)).

## Limits and concerns

- S05 still **hides all car visuals** in the burst fixture, so neither live nor
  hydrated frames show wreck geometry. "Live versus hydrated presentation" is
  proven for effects, not for wreck art.
- No VSync-disabled image, frame-time or GPU cost was measured. This is a
  drawability and correctness receipt, not a performance or capacity result.
- One desktop GPU on Windows. Linux/Deck drawing, physical input and
  readability/feel review remain open, as do policy ratification and reruns
  after final S02/S04 dimensions.
- Runner windows are placed at x = 0/640/1280 and overlap on smaller displays;
  capture uses the viewport texture, so overlap does not affect pixels.
