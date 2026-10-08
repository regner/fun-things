# S08 Windows evidence

Retained outputs for the [S08 Windows observation](../s08-windows-observation.md).
Paths are relative to this directory. Binaries, scratch projects, templates and
private user directories were not committed; their identities are in each
`summary.json`/`template-binding.json`.

| Directory | Contents |
| --- | --- |
| `prefix-observation/` | `tools/s08/windows_observation.py` at the pre-fix revision `fb1a372` (tool uncommitted at the time): import/export logs, release and debug sets, both stalled at the first post-admission held send. |
| `fixed-observation/` | Same tool at `828df12`: both sets pass with empty stderr and zero diagnostics. |
| `throttle-telemetry/` | Editor-run S03 with the scratch-only telemetry diff and an attempted deceleration-0 throttle configuration (scratch only, not committed). It shows `PEER_PACKET_THROTTLE_LIMIT` 32→1 before the lost send. |
| `bandwidth-fix-scratch-reset/` | Scratch run with the bandwidth workaround that failed on the Windows UDP reset (`WinError 10054`) before the proxy fix. |
| `s03-runner-prefix/`, `s03-runner-fixed-1…5/` | `tools/run_s03.py` before the fix (stall) and five passing runs after it. Runs 4–5 include the proof's throttle-limit assertion. |
| `s03r-prefix-baseline/`, `s03r-fixed-01/` | S03-R results before (baseline only, criteria failed with missing samples) and after the fix (all profiles pass). `s03r-fixed-01/baseline/` also keeps both role streams; `analyze_jitter.py` derives the uplink/apply-gap figures into `analyze_jitter.json`. |
| `s03r-scratch-no-deceleration/` | Scratch-only S03-R baseline with ENet throttle deceleration 0 on both peers (diff included; not adopted). Faster response; failed only the expiry criterion by 1 ms. |
| `s03r-windowed-baseline/`, `s03r-windowed-01/`, `s04-windowed-01/` | Windowed (drawn) S03-R/S04 results with sample 1280×800 client frames. |
| `s04-fixed-01/`, `s04-fixed-02/` | S04 results after the fix; normal profile fails the 500 ms response window in 2/20 samples both times. |

Two earlier scratch S03 runs that failed on staging mistakes (missing scratch
`project.godot`, then tool `.gd` dependencies) were ordinary tool errors and are
not retained. A pre-fix throttle-telemetry run without the limit field is
superseded by `throttle-telemetry/`.

Windows wrote several raw streams and runner JSON files with CRLF line endings
(CRT text mode). Git's `* text=auto eol=lf` attribute normalizes them to LF on
commit, so committed bytes differ from the scratch files only in line endings.
