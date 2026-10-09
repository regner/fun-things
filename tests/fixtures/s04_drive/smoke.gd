extends SceneTree
## Drives the saved standalone scene through its public API and checks accelerate, turn and stop.

const DRIVE_SCENE: PackedScene = preload("res://tests/fixtures/s04_drive/drive.tscn")
const TUNING_SAVE_PATH: String = "user://drive_tuning.tres"
const NEUTRAL: Dictionary = {
	"throttle": 0.0, "steer": 0.0, "brake": 0.0, "handbrake": false,
}

var _failures: Array[String] = []


## Defers the asynchronous proof until the SceneTree root is ready.
func _initialize() -> void:
	_run.call_deferred()


## Exercises the same saved coordinator and body APIs used by interactive driving.
func _run() -> void:
	var drive: S04Drive = await _create_checked_drive()
	drive.set_test_command({
		"throttle": 1.0, "steer": 0.0, "brake": 0.0, "handbrake": false,
	})
	await _wait_physics_frames(60)
	var accelerated: Dictionary = drive.car_state()
	_expect((accelerated.velocity as Vector3).length() > 8.0, "forward speed rises")

	drive.set_test_command({
		"throttle": 0.5, "steer": 1.0, "brake": 0.0, "handbrake": false,
	})
	await _wait_physics_frames(45)
	var turned: Dictionary = drive.car_state()
	_expect(absf(float(turned.yaw)) > 0.5, "steering changes heading")
	await _capture_if_requested()

	drive.set_test_command({
		"throttle": 0.0, "steer": 0.0, "brake": 1.0, "handbrake": false,
	})
	await _wait_physics_frames(60)
	var stopped: Dictionary = drive.car_state()
	_expect((stopped.velocity as Vector3).length() < 0.2, "brake stops the car")

	drive.reset_car()
	var reset: Dictionary = drive.car_state()
	_expect((reset.velocity as Vector3).is_zero_approx(), "reset clears velocity")
	drive.clear_test_command()
	var result: Dictionary = {
		"ok": _failures.is_empty(),
		"event": "s04_drive_smoke",
		"accelerated_speed_mps": (accelerated.velocity as Vector3).length(),
		"turned_yaw_radians": turned.yaw,
		"stopped_speed_mps": (stopped.velocity as Vector3).length(),
		"failures": _failures,
	}
	print("S04_DRIVE_SMOKE ", JSON.stringify(result))
	drive.queue_free()
	await process_frame
	_remove_saved_tuning()
	quit(0 if _failures.is_empty() else 1)


## Creates a drive scene, saves edited tuning, reloads it, then restores defaults.
func _create_checked_drive() -> S04Drive:
	_remove_saved_tuning()
	var drive: S04Drive = DRIVE_SCENE.instantiate() as S04Drive
	root.add_child(drive)
	await process_frame
	_check_default_tuning(drive.tuning)
	await _check_tuning_shortcuts(drive)

	drive.queue_free()
	await process_frame
	drive = DRIVE_SCENE.instantiate() as S04Drive
	root.add_child(drive)
	await process_frame
	_expect(drive.tuning.handbrake_mps2 == S04DriveRules.HANDBRAKE_MPS2 + 0.5,
		"startup loads the saved tuning resource")
	_expect(drive.tuning_status().contains("Saved values active"),
		"HUD status reports that saved values are active")
	_key(KEY_BACKSPACE)
	await process_frame
	_check_default_tuning(drive.tuning)
	_expect(not FileAccess.file_exists(TUNING_SAVE_PATH),
		"Backspace removes the saved override")

	drive.queue_free()
	await process_frame
	var invalid: Resource = Resource.new()
	_expect(ResourceSaver.save(invalid, TUNING_SAVE_PATH) == OK,
		"smoke setup saves a wrong-type tuning resource")
	drive = DRIVE_SCENE.instantiate() as S04Drive
	root.add_child(drive)
	await process_frame
	_check_default_tuning(drive.tuning)
	_expect(drive.tuning_status().contains("defaults active"),
		"wrong-type saved tuning reports the default fallback")
	_remove_saved_tuning()
	return drive


## Exercises selection, adjustment and persistence through ordinary keyboard routing.
func _check_tuning_shortcuts(drive: S04Drive) -> void:
	_key(KEY_F2)
	_key(KEY_EQUAL)
	await process_frame
	_expect(drive.tuning.brake_mps2 == S04DriveRules.BRAKE_MPS2 + 0.5,
		"keyboard shortcut adjusts selected tuning")
	_key(KEY_MINUS)
	_key(KEY_F10)
	_key(KEY_EQUAL)
	await process_frame
	_expect(drive.tuning.handbrake_mps2 == S04DriveRules.HANDBRAKE_MPS2 + 0.5,
		"F10 selects handbrake braking tuning")
	_key(KEY_F12)
	await process_frame
	_expect(FileAccess.file_exists(TUNING_SAVE_PATH),
		"F12 saves the current tuning resource")


## Pushes one physical key press through ordinary unhandled input routing.
func _key(code: Key) -> void:
	var event: InputEventKey = InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = true
	root.push_input(event)


## Checks that scene-only tuning starts at the accepted fixture rule values.
func _check_default_tuning(tuning: S04DriveTuning) -> void:
	_expect(tuning.acceleration_mps2 == S04DriveRules.ACCELERATION_MPS2,
		"default acceleration matches shared rules")
	_expect(tuning.brake_mps2 == S04DriveRules.BRAKE_MPS2,
		"default braking matches shared rules")
	_expect(tuning.handbrake_mps2 == S04DriveRules.HANDBRAKE_MPS2,
		"default handbrake braking matches shared rules")
	_expect(tuning.coast_mps2 == S04DriveRules.COAST_MPS2,
		"default coast matches shared rules")
	_expect(tuning.max_forward_mps == S04DriveRules.MAX_FORWARD_MPS,
		"default forward speed matches shared rules")
	_expect(tuning.max_reverse_mps == S04DriveRules.MAX_REVERSE_MPS,
		"default reverse speed matches shared rules")
	_expect(tuning.grip_per_second == S04DriveRules.GRIP_PER_SECOND,
		"default grip matches shared rules")
	_expect(tuning.slide_grip_per_second == S04DriveRules.SLIDE_GRIP_PER_SECOND,
		"default handbrake grip matches shared rules")
	_expect(tuning.turn_rad_per_second == S04DriveRules.TURN_RAD_PER_SECOND,
		"default turn rate matches shared rules")
	_expect(tuning.full_steer_speed_mps == S04DriveRules.FULL_STEER_SPEED_MPS,
		"default full-steer speed matches shared rules")
	_expect(tuning.value_count() == 10, "all ten tuning rows are selectable")
	_expect(tuning.display_name(6) == "Handbrake side grip (/s)",
		"handbrake lateral grip has an unambiguous display label")


## Removes smoke-owned persistence without touching checked-in resources.
func _remove_saved_tuning() -> void:
	if FileAccess.file_exists(TUNING_SAVE_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TUNING_SAVE_PATH))


## Waits for a fixed number of ordinary physics callbacks without replacing simulation timing.
func _wait_physics_frames(count: int) -> void:
	for frame: int in count:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop


## Saves one real rendered viewport when a windowed evidence path was requested.
func _capture_if_requested() -> void:
	var output: String = _capture_path()
	if output.is_empty():
		return

	await process_frame
	RenderingServer.force_draw()
	await process_frame
	var error: Error = root.get_texture().get_image().save_png(output)
	_expect(error == OK, "windowed evidence PNG saved")


## Reads the optional capture path from user arguments without affecting normal scene launch.
func _capture_path() -> String:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--capture="):
			return argument.trim_prefix("--capture=")

	return ""


## Records an independent smoke outcome while allowing remaining checks to complete.
func _expect(condition: bool, label: String) -> void:
	if not condition:
		_failures.append(label)
