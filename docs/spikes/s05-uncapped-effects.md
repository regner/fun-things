# S05 — every finite-fixture explosion is presented

> **Historical run instructions.** Commands in this record that target `prototypes/` describe
> the original runnable checkout; they do not run in the current checkout because the archive
> is hidden by `.gdignore`. Follow the
> [restore-from-Git procedure](../../prototypes/README.md) at pre-cleanup commit
> `66400c26a01bf917dfe631af4762c2b444d9c48f`, then drop the `prototypes/<group>/`
> prefix from every listed archived path before running it. For example,
> `res://prototypes/s02/tests/fixtures/s02/corner.tscn` becomes
> `res://tests/fixtures/s02/corner.tscn`.

8 October 2026, Windows 11 desktop, pinned
`4.8.dev7.official.c971f93e7`. This implements the owner's decision to remove the
on-screen explosion cap. [Retained evidence](s05-uncapped-effects-evidence/) binds
the runtime observations to clean revision
`a0e796de10bd872dba26482a08f09e2fd896cdb7`.

## Implementation and ownership

The bounded S05 fixture can produce at most 12 explosion events: one for each of
its 12 saved cars. Both saved effect fixtures now author 12 instances of the
existing saved [`explosion.tscn`](../../prototypes/s05_effect/tests/fixtures/s05_effect/explosion.tscn),
and `S05Presentation.MAX_SLOTS` derives from the authoritative fixture's
`S05Damage.MAX_CARS`. This is the smallest option because it preserves authored
composition, avoids a runtime allocation path, and exactly covers every event the
finite fixture can accept. It is not a proposed production-wide fixed cap; a
production system with an unbounded event lifetime will need a lifetime-owned pool
that grows by instancing the same saved effect scene.

`S05Damage` remains the only gameplay/chain writer. `S05Presentation` and
`S05SavedPresentation` still consume already-published events, and cosmetic expiry
never advances or cancels damage. Twelve simultaneous events now produce 12
reservations, 12 visible saved scene instances, and zero drops. Settled hydration
still produces no historical effect.

The comparator logic was deliberately unchanged: it continues to derive drawn and
dropped expectations as `min(explosions, configured capacity)` and
`max(0, explosions - configured capacity)`. Its current configured capacity is now
12. The offline evaluator's primary valid receipt was updated to 12/0 while retaining
a constrained 8/4 counterexample to protect capacity-derived evaluation.

The Godot editor was not running and no MCP editor tools were available. The brief
explicitly allowed enough saved slots for the fixture maximum, so the existing scene
files were edited directly without changing their UIDs, inherited identities, or
existing node identities; only four new saved explosion instances were added to each.

## Results

### Full S05 headless runner

The final full runner passed API, ENet host/live/settled-late, and reserved queue
pressure rows. The 12-car API, network, and queue receipts each report 12 effects,
zero effect drops, 144 target visits, and all authoritative outcomes complete. The
late process reports zero historical effects. Formatting, focused lint, seven
explicit S05 script compilations, copied-source preservation, and all child exits
also passed. See [result](s05-uncapped-effects-evidence/headless-result.json).

An initial post-change run reached correct 12/0 fixture outcomes but the Python
runner still expected the historical 8/4 values, so its independent evaluator
failed. The narrow correction changed those evaluator expectations without changing
gameplay or comparator formulas. That old failure remains in
[headless-old-evaluator-failure.json](s05-uncapped-effects-evidence/headless-old-evaluator-failure.json).

### Windowed S05 draw observation

One three-process windowed set passed in 14.58 s. Host and live client each reached
12 visible saved effect instances and captured a burst frame with zero drops; all
three processes exited 0 with no scanned diagnostics and were reaped. The settled
late joiner reached zero visible effects and captured the hydrated frame with no
historical presentation. Inputs were byte-preserved and clean at launch.

- [complete result](s05-uncapped-effects-evidence/windows-draw-result.json)
- [client 12-effect burst](s05-uncapped-effects-evidence/windows-client-burst.png),
  SHA-256 `f33f755456d675afa5d02b05de3f92b12f8045d2297d1795e8cae0dded94bbf7`
- [late hydrated frame](s05-uncapped-effects-evidence/windows-late-hydrated.png),
  SHA-256 `4b02ea837bc7818cc6c33fec947636cc468c60b06425bad2e556c7e4962c27b7`

### C0 comparator

The compressed 20-trial headless run passed in 45.29 s (driver 38.80 s). All 20
fresh sessions report configured capacity 12, expected/accepted 12, and dropped 0.
The three-trial windowed smoke passed in 15.39 s (driver 4.85 s); every trial drew
12 linked mesh instances, dropped 0, and saved its PNG through the existing camera.
The three PNGs share SHA-256
`bfea2ebda4c5a67cfb4cc5165aeb8c8afdf3f2776103c268f2b94f0b7a7fac68`.

- [headless summary](s05-uncapped-effects-evidence/comparator-headless-summary.json)
  and [20 rows](s05-uncapped-effects-evidence/comparator-headless-trials.jsonl)
- [windowed summary](s05-uncapped-effects-evidence/comparator-windowed-summary.json),
  [three rows](s05-uncapped-effects-evidence/comparator-windowed-trials.jsonl), and
  [trial 1 frame](s05-uncapped-effects-evidence/comparator-windowed-trial-01-burst.png)

## Commands

All outputs were fresh directories outside the worktree under
`C:/tmp/ft/lanes/s05-nocap/`.

```text
python prototypes/s05/tools/run_s05.py --godot <mise 4.8-dev7 godot.exe> --gdstyle <mise 0.3.0 gdstyle.exe> --output C:/tmp/ft/lanes/s05-nocap/s05-headless-final
python prototypes/s05_draw/tools/s05_draw/observe_windows.py --godot <mise 4.8-dev7 godot.exe> --output C:/tmp/ft/lanes/s05-nocap/s05-windowed-final
python prototypes/s07_comparator/tools/s07_comparator/run.py --godot <mise 4.8-dev7 godot.exe> --output C:/tmp/ft/lanes/s05-nocap/comparator-headless-20 --trials 20 --initial-delay 0 --spacing 2
python prototypes/s07_comparator/tools/s07_comparator/run.py --godot <mise 4.8-dev7 godot.exe> --output C:/tmp/ft/lanes/s05-nocap/comparator-windowed-3 --trials 3 --initial-delay 0 --spacing 2 --windowed
python -m unittest discover -s tools -p "test_*.py"
python tools/script_checks.py
```

The unittest suite passed all 14 tests. `script_checks.py` formatted and explicitly
compiled all 76 owned scripts successfully, then exited 1 only because its zero-warning
limit encountered the three accepted pre-existing S07 driver warnings named in the
repository brief: `fixture.gd` line length, `guards.gd` function length, and `run.gd`
function length. No new warning was reported. The exact commands, exit codes, counts,
diagnostics, and source identities are retained in the
[validation receipt](s05-uncapped-effects-evidence/validation-receipt.json), with the
[unittest](s05-uncapped-effects-evidence/validation-unittest.log) and
[script-checks](s05-uncapped-effects-evidence/validation-script-checks.log) output.

## Small review corrections

The comparator draw-wait purpose comment now describes all expected accepted saved
effect slots instead of the historical eight. The S06 Windows capture runner's clean
input scope now includes `prototypes/s06/tools/s06/capture_windows.py` and
`tools/script_checks.py`, and every result records both source byte counts and SHA-256
identities in `runner_sources`. The retained validation receipt records 10,562 bytes /
`9030b7305a0a706b092dd30fa378afb208a9526a69e9b98150007faf4d0ca644` and 6,705 bytes /
`f8efab7962fb39601038c69cfc9fc739d8fc39193f507f82f52e9c137ac9c9e0`, respectively.

## Limits

This closes the removed-cap behavior for the bounded 12-car technical fixture and
its real Windows draw observation. It does not measure frame cost, GPU/CPU headroom,
overdraw, readability, particles, debris, audio, sustained production event rates,
or Linux/Deck behavior. Cars remain hidden in the burst fixture, so these frames do
not assess combined wreck and explosion art. Final S02/S04 dimensions still require
the previously specified spacing/contact reruns. Full S05, S07 capacity, P0, M1, and
production acceptance remain open.
