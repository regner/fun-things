# S02 — Windows drawability and native-focus observation

8 October 2026. Windows 11 `10.0.26200`, NVIDIA GeForce RTX 4070 Laptop GPU,
D3D12 Forward+, pinned Godot `4.8.dev7.official.c971f93e7`. This executes the saved
S02 corner and saved focus runner without changing either scene or any gameplay behavior.
[Evidence](s02-windows-evidence/) binds the graphical observation to revision
`1b6b3a3abdfe5fd3839020b20e6da245b98c1ce1` and the exact copied runtime inputs.
Full S02 remains open.

## Result

**Automatic drawability at the declared desktop size passes. Native focus handling does
not.** The unchanged saved corner produced 30 genuine automatic
`RenderingServer.frame_post_draw` callbacks, but the saved minimize/restore runner did
not receive focus loss during its minimized interval. Held movement and fire continued.
No fixture behavior or acceptance criterion was weakened to convert that failure into a
pass.

| Observation | Result |
| --- | --- |
| Existing headless `tools/s02/run.py` | **PASS**: import/outcomes/unchanged inputs, exit 0, no S02 failures. |
| Automatic Windows draw | **PASS**: callbacks 1–30 map to strictly increasing `Engine.get_frames_drawn()` 0–29; process exit 0; no engine/script diagnostic; empty stderr. |
| Native/viewport size | **PASS**: Windows backend, mode 0, `can_draw: true`, window 1280×800, viewport 1280×800 on every receipt. |
| Actual saved camera | **PASS**: current perspective `/root/S02/CameraRig/Camera3D`; vertical -Y/fixed yaw 0; FOV 42°; near 0.1/far 160; world position about `(0,47.001,6)` after normal actor settling. |
| Automatic callback images | **PASS**: callback 3/10/30 PNGs are 1280×800, nonblank and visually show the usable saved corner, actor, pistol/marker, buildings and target. |
| Programmatic minimize focus-out/in | **FAIL**: minimized mode was observed, but native/collector focus stayed true through the interval; a delayed focus-out arrived only after the restored-state check, and no subsequent focus-in was observed. |
| Held-input cancellation | **FAIL**: movement/fire stayed held while minimized; actor Z moved from about 3.33 to -4.00 and shots rose from 2 to 8 before scripted release/restore. One additional transient fire sample raised shots to 9 after restore. |

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

## Native focus observation

The same tool next launched the unchanged saved `focus_runner.tscn` windowed at 1280×800.
The fixture injected W+Space at 1.0 s, requested minimize at 1.5 s, requested restore and
released both keys at 3.0 s, checked restored state at 4.0 s, and stopped at 7.0 s.

Windows reported mode 1 from the first 1.542 s sample through 2.930 s, but
`Window.has_focus()` and the input collector both remained true. During that interval the
sampled command remained `{move: 1, fire: true}`; motion and firing continued. The restore
request made mode 0 and the explicit releases initially made command neutral at 3.046 s.
A transient stale fire sample appeared at 3.688 s and produced shot 9. At the fixture's
4.0 s check, movement was neutral and did not resume, but that came from scripted release,
not from timely OS focus cancellation.

The fixture finally observed collector focus false at 4.656 s and native focus false at
4.763 s, after its restored-state check. It saw no focus-in before exit and returned exit 1:

```text
S02_FOCUS_RESULT {"failures":["OS minimize did not deliver focus loss"],
                  "os_focus_loss":false}
```

Native foreground telemetry independently recorded the pre-existing `π - fun-things`
window before/after. The S02 focus child became foreground only from runner offsets about
5.974–7.591 s; otherwise the same pre-existing window remained foreground. No third PID or
foreign foreground owner appeared, so the runner's one allowed foreign-steal retry was not
used. This is a failed Windows native-focus result, not a reason to repeat or loosen the
fixture.

## Reproducibility and authoring boundary

The Godot editor was not running and editor/MCP tools were unavailable for this lane.
The separate observer, Python runner and documentation were therefore direct text-file
edits; the saved scene hierarchies were not edited. A pinned headless editor import created
the new script UID sidecar. That checkout import exited 0 but retained the known development
addon diagnostics; the isolated observation import removed those development plugins and
had no diagnostics. Explicit all-owned compilation passed. Pinned formatting covered 74
scripts; the only lint output was the three pre-existing accepted S07-driver warnings.
Offline unit tests cover receipt parsing and the foreign-foreground retry fence.

The runner records native foreground HWND/PID/title before, during and after each child,
uses private Windows user directories, applies finite deadlines, and terminates only its
own exact child if required. Neither observed child needed forced termination. Scratch
projects/private user data remain under `C:\tmp\ft\lanes\s02\`, outside every checkout.

## Required human checklist (not performed)

A human must perform all of the following before physical-input, feel or camera
ratification is claimed:

1. Launch `corner.tscn` at 1280×800. Hold physical W+Space, physically Alt-Tab to a normal
   non-Godot application, and verify motion and firing stop immediately. Release both keys
   while away, Alt-Tab back, and verify neither resumes until a fresh physical press.
2. Walk through the four-metre passage, turn around the north-east corner, deliberately hit
   the previously blocked target, then reverse away from a wall. Record missed targets,
   facing/control confusion and whether 5 m/s forward, 3 m/s reverse and 180°/s turn feel
   controllable.
3. Play the same route in `corner.tscn` (42°) and `corner_wide.tscn` (50°). Choose neither
   by screenshot alone: record target/building/actor readability, camera-follow comfort,
   roof/cutaway distraction and any motion discomfort.
4. At native view size, compare pistol/SMG/launcher silhouettes and record which are
   distinguishable without pausing. Report the actor marker and abrupt cutaway separately.

No physical key, physical Alt-Tab, latency, subjective feel, camera/FOV selection, Deck,
Steam, packaged export, performance or production acceptance was performed here.

## Disposition

The prior Linux Wayland boundary (`can_draw: false`, 2112×1320, focus false) is superseded
only for Windows drawability: this Windows desktop supplies genuine exact-size automatic
callbacks and usable pixels. Native focus remains open and now has a current Windows failure
with delayed focus delivery and stale held input. Full S02, human control/camera ratification,
Deck/Gaming Mode and dependent gates remain open.
