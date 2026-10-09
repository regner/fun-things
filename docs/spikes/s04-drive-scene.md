# S04 standalone drive scene

8 October 2026. This is the no-network owner feel harness requested after the bounded S04
body experiment. It instances the accepted saved track and kinematic car, starts with the local
player controlling that car immediately (seated), and uses the ratified fixed-north 47 m / 42°
perspective camera. It does not add firing, entry/exit, prediction or network behavior.

## Run

From the repository root:

```sh
mise exec -- godot --path . res://tests/fixtures/s04_drive/drive.tscn
```

The equivalent direct pinned-binary command on the current Windows workstation is:

```powershell
& 'C:\Users\regner.blokandersen\AppData\Local\mise\installs\github-godotengine-godot-builds\4.8-dev7\godot.exe' --path . res://tests/fixtures/s04_drive/drive.tscn
```

Confirm `--version` is `4.8.dev7.official.c971f93e7` if resolving the binary on another machine.

## Controls and live tuning

- **W / S**: throttle forward; opposite input brakes, then selects reverse once stopped.
- **A / D**: steer left / right. Arrow-key aliases also work.
- **Space**: handbrake. This uses S04DriveRules' existing lower lateral-grip path; it is not a new
  inert or scene-only handling rule.
- **R**: reset the car to its authored start pose and clear carried speed/input.
- **Escape**: pause/resume the existing desktop input collector.
- **F1–F9**: select the value shown by that row in the tuning panel.
- **+ / -** (main keyboard or keypad): adjust the selected value by its displayed category's fixed
  increment.
- **F12**: print one `S04_DRIVE_TUNING {...}` JSON line to stdout and save a copy to
  `user://drive_tuning.tres`. The checked-in scene resource remains unchanged.

The saved `S04DriveTuning` resource is used only by this standalone path. Its nine defaults exactly
match the existing `S04DriveRules` constants, so the established S04 fixture continues to call the
same rule with its unchanged defaults. The HUD reads state and values; the scene coordinator owns
shortcut handling and asks the resource to adjust values.

## Suggested feel pass

1. Accelerate straight to full speed and note whether start response and top speed feel playful or
   sluggish.
2. Hold a broad turn, then try short steering taps at low and high speed. Note steering response,
   not just whether the car completes the turn.
3. Release throttle to compare coasting with pressing the opposite direction to brake.
4. Enter a turn and hold Space, then release it and recover. Compare `Grip` with `Handbrake grip`.
5. Drive into the north wall, reverse away, and press R after a deliberately bad approach.

Please report the complete F12 JSON line plus concrete observations: what maneuver was attempted,
what felt wrong or right, and any preferred value set. A useful response names acceleration,
braking, coast, forward/reverse caps, ordinary/handbrake grip, turn rate and full-steer speed rather
than only saying “faster” or “more arcade.” These are feel candidates, not production ratification.

## Saved-scene authoring and checks

The Godot editor was unavailable for this lane. Under the lane's explicit fallback, the three
minimal compositions (`camera_rig.tscn`, `drive_hud.tscn`, and `drive.tscn`) were authored as text,
using instances of the existing saved track/car and saved camera/HUD scenes. A small external
SceneTree serializer script loaded, packed and resaved all three with the pinned engine; the saved
files then loaded in direct windowed and automated smoke runs. New scripts received engine-generated
`.uid` sidecars after the required headless import. The full import's known editor-plugin diagnostics
are not treated as clean runtime evidence; addon-free all-owned compilation and focused runtime logs
are recorded separately in [the evidence index](s04-drive-scene-evidence/README.md).
