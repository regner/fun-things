# S04 standalone drive scene

> **Historical run instructions.** Commands in this record that target `prototypes/` describe
> the original runnable checkout; they do not run in the current checkout because the archive
> is hidden by `.gdignore`. To reproduce them, follow the
> [restore-from-Git procedure](../../prototypes/README.md) in a separate worktree at the recorded
> pre-cleanup commit.

8 October 2026. This is the no-network owner feel harness requested after the bounded S04
body experiment. It instances the accepted saved track and kinematic car, starts with the local
player controlling that car immediately (seated), and uses the ratified fixed-north 47 m / 42°
perspective camera. It does not add firing, entry/exit, prediction or network behavior.

## Run

From the repository root:

```sh
mise exec -- godot --path . res://prototypes/s04_drive/tests/fixtures/s04_drive/drive.tscn
```

The equivalent direct pinned-binary command on the current Windows workstation is:

```powershell
& 'C:\Users\regner.blokandersen\AppData\Local\mise\installs\github-godotengine-godot-builds\4.8-dev7\godot.exe' --path . res://prototypes/s04_drive/tests/fixtures/s04_drive/drive.tscn
```

Confirm `--version` is `4.8.dev7.official.c971f93e7` if resolving the binary on another machine.

## Controls and live tuning

- **W / S**: throttle forward; opposite input brakes, then selects reverse once stopped.
- **A / D**: steer left / right. Arrow-key aliases also work.
- **Space**: handbrake. The shared `S04DriveRules` applies 10.0 m/s² braking to the complete
  planar velocity while retaining lower sideways grip for a sliding turn.
- **R**: reset the car to its authored start pose and clear carried speed/input.
- **Escape**: pause/resume the existing desktop input collector.
- **F1–F10**: select the value shown by that row in the tuning panel. F10 selects handbrake
  braking strength; `Handbrake side grip` remains the sideways-slide control.
- **+ / -** (main keyboard or keypad): adjust the selected value by its displayed category's fixed
  increment.
- **F12**: print one `S04_DRIVE_TUNING {...}` JSON line to stdout and save a copy to
  `user://drive_tuning.tres`. The checked-in scene resource remains unchanged.
- **Backspace**: restore all checked-in defaults and remove the saved override.

The saved `S04DriveTuning` resource is used only by this standalone path. Its ten defaults exactly
match the `S04DriveRules` constants. The scene loads a valid `user://drive_tuning.tres` at startup
and marks saved values active in the HUD; a missing or wrong-type resource falls back to checked-in
defaults. The HUD reads state and values; the scene coordinator owns shortcut handling and asks the
resource to adjust values.

## Suggested feel pass

1. Accelerate straight to full speed and note whether start response and top speed feel playful or
   sluggish.
2. Hold a broad turn, then try short steering taps at low and high speed. Note steering response,
   not just whether the car completes the turn.
3. Release throttle to compare coasting with pressing the opposite direction to brake.
4. Enter a turn and hold Space, then release it and recover. Compare `Grip`, `Handbrake side grip`
   and `Handbrake brake`.
5. Drive into the north wall, reverse away, and press R after a deliberately bad approach.

Please report the complete F12 JSON line plus concrete observations: what maneuver was attempted,
what felt wrong or right, and any preferred value set. A useful response names acceleration,
braking, coast, forward/reverse caps, ordinary/handbrake side grip, handbrake braking, turn rate and
full-steer speed rather than only saying “faster” or “more arcade.” These are feel candidates, not
production ratification.

The owner's initial 9 October play test preferred `coast_mps2 = 10.0` and
`grip_per_second = 9.0` over the checked-in 4.0 and 6.0 defaults. That session also exposed the
handbrake behavior corrected below; the later decision-30 values supersede these initial candidates.

## Handbrake and persistence follow-up — 9 October 2026

The shared rule now slows the car at 10.0 m/s² while the handbrake is held, suppresses throttle, and
uses the stronger service-brake deceleration when both brakes apply. Lower lateral grip remains in
place, so handbrake turns still slide. The standalone panel adds the F10 handbrake-braking row and
renames the serialized `slide_grip_per_second` property's display label to `Handbrake side grip`.
F12 still saves and prints; startup loads a valid saved tuning resource, and Backspace restores the
checked-in values and removes that override. Direct text editing was used because the Godot editor
was unavailable; the saved HUD scene change only enlarges the existing panel and updates its text.

## Handbrake turning follow-up — 9 October 2026

The owner re-test found that braking improved, but a turning handbrake slide lost yaw authority and
continued sideways because braking and steering scale used only the car's forward velocity component.
The shared rule now reduces the complete planar velocity magnitude without crossing zero, then applies
the existing 1.0/s handbrake side grip to its travel direction. Steering authority scales from planar
speed only while the handbrake is held, so a sideways-moving slide can keep turning without changing
ordinary steering. During a handbrake slide, reverse steering flips only with at least 0.05 m/s of
reverse forward-component speed, avoiding direction jitter as the slide rotates through sideways.
Ordinary steering retains its original forward-speed authority and reverse sign rule exactly. Service
braking still wins when it is stronger, throttle remains suppressed, and the four-field network
contract is unchanged. The owner's saved tuning resource was not read or modified.

Decision 29's full-vector braking invalidated the earlier body comparison's absolute requirement that
handbrake lateral speed exceed ordinary lateral speed by 1.0 m/s after 0.5 seconds: the complete car
now deliberately loses 5.0 m/s during that interval. With supervisor approval, the independent slide
criterion now requires at least four times ordinary lateral speed plus a slip share at least 0.25
higher. The final kinematic result is 1.070 versus 0.212 m/s and 0.517 versus 0.070 slip share; the
dynamic result is 0.901 versus 0.212 m/s and 0.489 versus 0.070. A separate public-rule case measures
a pure sideways 15 m/s car at 5.000 m/s after one second and full-steer yaw at -1.5 rad/s. The old
absolute-bound failure is retained with the round-2 evidence rather than hidden.

Round 2 directly edited only project-owned scripts and documentation because the Godot editor was
unavailable; no scene, resource, UID, or saved `user://drive_tuning.tres` data changed.

## Owner-approved starting handling (decision 30) — 9 October 2026

After the fixes and re-tests, the owner ratified these playtest-tunable M1-B1 starting values:

| Tuning value | Fixture default | Owner-approved M1-B1 start |
| --- | ---: | ---: |
| Acceleration (m/s²) | 12.0 | 12.0 |
| Brake (m/s²) | 18.0 | 12.0 |
| Coast (m/s²) | 4.0 | 9.25 |
| Maximum forward speed (m/s) | 20.0 | 24.0 |
| Maximum reverse speed (m/s) | 6.0 | 6.0 |
| Grip (1/s) | 6.0 | 8.0 |
| Handbrake side grip (1/s) | 1.0 | 3.0 |
| Turn rate (rad/s) | 1.5 | 1.5 |
| Full-steer speed (m/s) | 4.0 | 4.0 |
| Handbrake brake (m/s²) | 10.0 | 10.0 |

The first owner session (decision 26) found that the handbrake did not slow the car longitudinally.
Commit `caf4b9b` added handbrake braking while preserving reduced side grip for a slide. The next
re-test found that a sideways slide lost yaw authority and did not scrub its full planar velocity;
commits `77e3731` and `2a91594` corrected turning and full-vector deceleration. The owner then
reported the result was “looking much better” and saved the values above.

The `S04DriveRules` fixture defaults intentionally stay unchanged as stable evidence baselines.
M1-B1 production handling starts from the owner-approved values above and remains playtest-tunable.
The exact sparse resource saved by the owner is retained in the
[evidence directory](s04-drive-scene-evidence/owner-drive-tuning-2026-10-09.tres).

## Saved-scene authoring and checks

The Godot editor was unavailable for this lane. Under the lane's explicit fallback, the three
minimal compositions (`camera_rig.tscn`, `drive_hud.tscn`, and `drive.tscn`) were authored as text,
using instances of the existing saved track/car and saved camera/HUD scenes. A small external
SceneTree serializer script loaded, packed and resaved all three with the pinned engine; the saved
files then loaded in direct windowed and automated smoke runs. New scripts received engine-generated
`.uid` sidecars after the required headless import. The full import's known editor-plugin diagnostics
are not treated as clean runtime evidence; addon-free all-owned compilation and focused runtime logs
are recorded separately in [the evidence index](s04-drive-scene-evidence/README.md).
