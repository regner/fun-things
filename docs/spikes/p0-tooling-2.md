# P0-TOOLING-2 runner safety and evidence binding

This follow-up closes the quiet-pass runner audit blockers without rerunning any long
measurement. Repository tools and documentation were edited directly because no Godot
editor or MCP editor tooling was running; no scene hierarchy or serialized identity was
changed.

## Window safety

`tools/window_safety.py` owns the exact 60 FPS command guard. Every windowed runner in
this lane now adds `--max-fps 60` explicitly, including the S05 draw/image observers,
S06 capture, S07 comparator/environment/graphical runners, S13–S15, and the S02 Windows
observer. S05 Card I retains disabled VSync but cannot launch without that cap.

S07 graphical now accepts only `capped60`. The fixture rejects any other mode before
starting and always sets `Engine.max_fps` to 60. The historical uncapped observations
remain retained in [the graphical record](s07-graphical-t.md), but uncapped execution is
withdrawn because those attempts caused `DXGI_ERROR_DEVICE_REMOVED` on this laptop.

## Quiet timing

S09–S15 runners no longer start task-list, PowerShell/CIM/Get-Counter, or equivalent
contention sampling inside or immediately before a timed case. The applicable runners
collect those observations only after the measured child has exited, then wait through an
explicit one-second settle before another case can launch. Receipts label the values as
post-case context that does not prove measurement-window exclusivity. S07-ENV keeps
only its intentional low-overhead owned-process working-set polling.

## Evidence and polling

`tools/measurement_identity.py` centralizes repository commit/tree/dirty status, source
fingerprints, top-level `sys.argv`, working directory, and effective parameters. S03,
S08 Linux, S07 driver/graphical/environment, and S09–S15 receipts use it. Their declared
source sets include the runner, imported measurement helpers, and staged fixture inputs;
existing staged-project manifests remain as a second byte-preservation check.

`tools/incremental_log.py` retains byte offsets and only decodes complete appended lines.
S05, Card I, and both S05 draw observers use it instead of rescanning growing logs during
polling. Complete final diagnostic review remains separate from timed polling where a
runner already had that final check.

## Validation

No long, graphical, or network measurement was rerun. Offline tests cover incorrect FPS
caps, withdrawn S07 modes, required runner integration, post-case sampler placement,
identity receipt content, and partial-line/retained-offset behavior. The pinned engine
compiled all owned GDScript through `tools/script_checks.py`; complete Python test
discovery also passed. Console output is retained in
[p0-tooling-2-evidence](p0-tooling-2-evidence/README.md).
