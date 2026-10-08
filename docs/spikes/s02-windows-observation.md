# S02 — Windows drawability and native-focus observation

8 October 2026. Windows 11 `10.0.26200`, NVIDIA GeForce RTX 4070 Laptop GPU,
D3D12 Forward+, pinned Godot `4.8.dev7.official.c971f93e7`. The initial pass executed the
saved S02 corner and focus runner without changing either scene or gameplay behavior.
[Evidence](s02-windows-evidence/) binds that graphical observation to revision
`1b6b3a3abdfe5fd3839020b20e6da245b98c1ce1`; a corrected evidence-only focus harness ran
at `826bc029ebd4626d426a5ccc596aee3ef120fb78`. Full S02 remains open.

## Result

**Automatic drawability at the declared desktop size passes. Native focus remains
inconclusive.** The unchanged saved corner produced 30 genuine automatic
`RenderingServer.frame_post_draw` callbacks. Independent review found that the original
focus child did not own native foreground before synthetic keys and minimize, so its
focus/held-input result had an invalid precondition. A corrected gated follow-up could not
establish initial native foreground and injected no keys. Neither attempt proves native
focus handling passes or fails.

| Observation | Result |
| --- | --- |
| Existing headless `tools/s02/run.py` | **PASS**: import/outcomes/unchanged inputs, exit 0, no S02 failures. |
| Automatic Windows draw | **PASS**: callbacks 1–30 map to strictly increasing `Engine.get_frames_drawn()` 0–29; process exit 0; no engine/script diagnostic; empty stderr. |
| Native/viewport size | **PASS**: Windows backend, mode 0, `can_draw: true`, window 1280×800, viewport 1280×800 on every receipt. |
| Actual saved camera | **PASS**: current perspective `/root/S02/CameraRig/Camera3D`; vertical -Y/fixed yaw 0; FOV 42°; near 0.1/far 160; world position about `(0,47.001,6)` after normal actor settling. |
| Automatic callback images | **PASS**: callback 3/10/30 PNGs are 1280×800, nonblank and visually show the usable saved corner, actor, pistol/marker, buildings and target. |
| Original programmatic minimize focus-out/in | **INCONCLUSIVE — invalid precondition**: the child was not native foreground before press/minimize. The raw minimized/delayed-focus samples are retained but cannot establish native-focus behavior. |
| Corrected gated focus follow-up | **INCONCLUSIVE — initial native focus not established**: the runner never observed the child as foreground for the required 250 ms, so the fixture injected no keys and did not minimize. |
| Held-input cancellation | **INCONCLUSIVE**: original movement/fire samples occurred without initial native foreground; the corrected attempt intentionally performed no input. |

The three images have different hashes because the normal camera follow converged by tiny
subpixel amounts; inspection shows the same usable view. This is engine rendering for one
window, not physical scanout or visual-quality ratification.

## Headless Windows result

The existing command was run first against a fresh external directory:

```powershell
python tools/s02/run.py --godot <pinned-godot.exe> `
  --output C:\tmp\ft\lanes\s02\headless
```

It passed with `saved_files_unchanged: true`. Forward/reverse, facing-relative turning,
wall stop `(6,0.001,0.38021)`, passage/corner traversal, clear/blocked aiming, cadence,
alias cancellation, target overlap, camera/resource links and source-derived muzzle checks
all remained clean. This is isolated API/resource evidence, not a graphical or native-focus
substitute.

## Automatic Windows rendering

[`tools/s02/observe_windows.py`](../../tools/s02/observe_windows.py) stages only the S02
runtime closure and linked `s02_*` models into a fresh external project. Development
autoloads/editor plugins and the icon are removed only from that copy. It performs a clean
headless import, then launches a graphical observer at `--resolution 1280x800`.
[`observe_windows.gd`](../../tests/fixtures/s02/observe_windows.gd) instances only the
saved `corner.tscn`, subscribes to `frame_post_draw`, reads state, and saves callback
3/10/30 viewport images. It contains no `force_draw`, signal emission, input injection,
camera override or window resize.

```powershell
python tools/s02/observe_windows.py --godot <pinned-godot.exe> `
  --output C:\tmp\ft\lanes\s02\windows
```

The observer recorded Windows/D3D12 Forward+, 30 callbacks within 612 ms of scene setup,
strict frame indices 0–29, and the actual camera axes:

- basis X `(1,0,0)`;
- basis Y approximately `(0,0,-1)` and basis Z approximately `(0,1,0)`, so the camera
  looks vertically down;
- current perspective projection, FOV 42°, near approximately 0.1, far 160;
- native and viewport size both exactly 1280×800, mode 0, `can_draw: true`, focus true.

All staged inputs remained byte-identical after import and both graphical processes. The
processes exited and were reaped without parent cleanup action. Full commands, PID/exits,
telemetry, source ledger and image hashes are in `result.json` and `copy-ledger.json`.

## Native focus observations

### Original retained attempt — invalid precondition

The original tool launched the unchanged saved `focus_runner.tscn` windowed at 1280×800.
The fixture injected W+Space at fixture time 1.0 s, requested minimize at 1.5 s, requested
restore/release at 3.0 s, checked at 4.0 s, and stopped at 7.0 s. Raw samples reported mode
1 while Godot focus stayed true; movement and firing continued, then one transient fire
sample appeared after restore. The fixture later reported focus false and exited 1.

Those facts remain in the raw streams, but **the result is inconclusive, not a Windows
native-focus failure**. Native foreground telemetry shows the pre-existing
`π - fun-things` window owned foreground until runner offset 5.974 s. The child first
became foreground at restore; the pre-existing window regained foreground at 7.591 s.
Correlating the fixture
and process clocks gives about 2.93 s of startup, so the child did not own native foreground
before press or minimize. Synthetic input can move the fixture despite that invalid OS
precondition. The original result therefore cannot prove minimizing an initially focused
window did or did not cancel held input. No foreign third PID appeared, and the old retry
fence also used the wrong zero-startup clock origin.

### Corrected gated follow-up — initial focus unavailable

Revision `826bc029ebd4626d426a5ccc596aee3ef120fb78` changed only the evidence harness and
runner. The runner now creates a gate only after the child owns Windows foreground
continuously for at least 250 ms. The fixture waits for that gate before injecting keys and
emits process-clock stage markers for press, minimize, restore and check. The runner checks
sustained child ownership before press/minimize and evaluates foreign ownership between the
actual restore/check markers, including engine startup time. A nonzero-startup regression
test fences that mapping.

One permitted focus-only follow-up was run. The pre-existing `π - fun-things` window
remained foreground for every 50 ms runner sample. The child emitted
`await_initial_native_focus` at process 4513 ms, never received the gate, injected no keys,
and never minimized. At process 7452 ms it returned exit 1 with the explicit bounded result:

```text
S02_FOCUS_RESULT {"failures":["initial native focus not established"],
                  "os_focus_loss":false}
```

The runner classified this attempt `inconclusive: initial native focus not established`.
There was no foreign owner, so no retry was authorized. This cleanly preserves the native
precondition instead of interpreting Godot's stale `Window.has_focus()` value as OS focus.
The complete follow-up is in [`focus-fixed/`](s02-windows-evidence/focus-fixed/); the
original raw result and streams remain unchanged.

## Reproducibility and authoring boundary

The Godot editor was not running and editor/MCP tools were unavailable for this lane.
The separate observer, Python runner and documentation were therefore direct text-file
edits; the saved scene hierarchies were not edited. A pinned headless editor import created
the new script UID sidecar. That checkout import exited 0 but retained the known development
addon diagnostics; the isolated observation import removed those development plugins and
had no diagnostics. Explicit all-owned compilation passed. Pinned formatting covered 74
scripts; the only lint output was the three pre-existing accepted S07-driver warnings.
Offline unit tests cover receipt parsing, sustained initial ownership and the stage-marker
foreign-foreground retry fence, including a nonzero engine-startup delay.

The runner records native foreground HWND/PID/title before, during and after each child,
uses private Windows user directories, applies finite deadlines, and terminates only its
own exact child if required. Neither observed child needed forced termination. Scratch
projects/private user data remain under `C:\tmp\ft\lanes\s02\`, outside every checkout.

## Owner decision, next steps and human checklist

The owner has decided that a **later lane** will replace this candidate's facing-relative
W/S movement plus A/D turning with WASD movement and mouse-facing, and will remove the
building cutaway. Those product changes are intentionally not implemented here. Current
control/cutaway pixels remain technical draw evidence, not a recommendation to retain them.
Native focus and human camera/control ratification should use the later saved candidate.

After that lane lands, a human must perform all of the following before physical-input,
feel or camera ratification is claimed:

1. Launch the later candidate at 1280×800 and confirm it is native foreground. Hold a
   physical movement key plus the fire control, physically Alt-Tab to a normal non-Godot
   application, and verify motion/firing stop immediately. Release while away, Alt-Tab
   back, and verify neither resumes until a fresh physical press.
2. Walk through the four-metre passage with WASD, use mouse-facing to turn around the
   north-east corner, deliberately hit the previously blocked target, then reverse away
   from a wall. Record missed targets, facing/control confusion and camera-follow comfort.
3. Compare the retained 42°/50° camera candidates on the same route without the building
   cutaway. Record target/building/actor readability, roof occlusion and motion discomfort;
   choose neither by screenshot alone.
4. At native view size, compare pistol/SMG/launcher silhouettes and the actor marker while
   moving and aiming; record which remain distinguishable without pausing.

No physical key, physical Alt-Tab, latency, subjective feel, camera/FOV selection, future
control/cutaway implementation, Deck, Steam, packaged export, performance or production
acceptance was performed here.

## Disposition

The prior Linux Wayland boundary (`can_draw: false`, 2112×1320, focus false) is superseded
only for Windows drawability: this Windows desktop supplies genuine exact-size automatic
callbacks and usable pixels. Native focus remains open: the original attempt had an invalid
foreground precondition, and the corrected follow-up could not establish that precondition.
The later WASD/mouse-facing and cutaway-removal lane, human ratification, Deck/Gaming Mode
and dependent gates remain open.
