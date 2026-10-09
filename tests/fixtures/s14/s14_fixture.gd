extends Node3D
## Runs the saved S14 audio stress fixture and writes one structured receipt.

const BUS_LAYOUT := preload("res://tests/fixtures/s14/bus_layout.tres")
const SAMPLE_FRAMES := 48
const SETTINGS_PATH := "user://s14_audio_settings.cfg"
const MALFORMED_SETTINGS_PATH := "user://s14_audio_settings_malformed.cfg"

@onready var _listener: AudioListener3D = %AudioListener
@onready var _voice_manager: S14VoiceManager = %VoiceManager


## Installs the fixture-local buses before saved audio children become ready.
func _enter_tree() -> void:
	AudioServer.set_bus_layout(BUS_LAYOUT)


## Executes settings and bounded-voice checks, then terminates the fixture process.
func _ready() -> void:
	Engine.max_fps = 60
	var output_path := _argument_value("--s14-output=")
	if output_path.is_empty():
		push_error("S14 requires --s14-output=<external JSON path>")
		get_tree().quit(2)
		return

	await get_tree().process_frame
	var result: Dictionary = await _run_fixture(_argument_value("--s14-mode="))
	var write_error := _write_json(output_path, result)
	await _stop_audio_and_settle()
	if write_error != OK:
		push_error("S14 could not write result: %s" % error_string(write_error))
		_quit_after_scene_cleanup(3)
		return

	_quit_after_scene_cleanup(0 if result["success"] else 1)


## Frees the fixture scene before a tree-owned timer exits the process.
func _quit_after_scene_cleanup(exit_code: int) -> void:
	var tree := get_tree()
	tree.create_timer(0.1).timeout.connect(tree.quit.bind(exit_code))
	queue_free()


## Runs the public settings, request, cap, and monitor checks.
func _run_fixture(mode: String) -> Dictionary:
	var failures: Array[String] = []
	if not _voice_manager.configure(_listener):
		failures.append("saved voice pool sizes do not match category caps")
	var settings_result := _check_settings_roundtrip()
	if not settings_result["passed"]:
		failures.append("ConfigFile settings roundtrip failed")

	var peak_report := _start_storm()
	_validate_peak_report(peak_report, failures)
	var monitor_samples: Array[Dictionary] = await _sample_monitors()
	var settled_report := _voice_manager.report()
	if settled_report["ducking_active"]:
		failures.append("explosion ducking did not restore within its bounded window")

	return _build_result(
		mode,
		failures,
		{
			"settings": settings_result,
			"peak": peak_report,
			"settled": settled_report,
			"monitors": monitor_samples,
		},
	)


## Starts the saved engine bed, explosion storm, and SMG burst.
func _start_storm() -> Dictionary:
	var speeds := PackedFloat32Array([0.0, 4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 30.0])
	_voice_manager.set_engine_speeds(speeds)
	for index in 24:
		var angle := TAU * float(index) / 24.0
		_voice_manager.request_explosion(Vector3(cos(angle) * 6.0, 0.5, sin(angle) * 6.0))
	for index in 12:
		_voice_manager.request_weapon_shot(Vector3(float(index % 4) - 1.5, 0.8, -2.0))
	return _voice_manager.report()


## Samples available engine monitors while advancing bounded ducking time.
func _sample_monitors() -> Array[Dictionary]:
	var samples: Array[Dictionary] = []
	for _frame in SAMPLE_FRAMES:
		# Each draw frame is one intentional sample; a timer would hide frame outliers.
		await get_tree().process_frame  # gdstyle:ignore=quality/await-in-loop
		_voice_manager.update_duck(Time.get_ticks_msec())
		samples.append(_read_monitors())
	return samples


## Builds the structured result shared by headless and windowed cases.
func _build_result(
	mode: String,
	failures: Array[String],
	observations: Dictionary,
) -> Dictionary:
	return {
		"success": failures.is_empty(),
		"failures": failures,
		"mode": mode,
		"engine_version": Engine.get_version_info()["string"],
		"audio_driver": AudioServer.get_driver_name(),
		"renderer": RenderingServer.get_current_rendering_method(),
		"listener":
		{
			"anchor": "character_ground_position",
			"orientation": "fixed_north_up_top_down_camera",
			"position": _listener.global_position,
			"rotation_degrees": _listener.global_rotation_degrees,
		},
		"requests":
		{
			"engine_emitters": 32,
			"explosions": 24,
			"smg_shots": 12,
		},
		"peak": observations["peak"],
		"settled": observations["settled"],
		"settings_roundtrip": observations["settings"],
		"performance": _summarize_monitors(observations["monitors"]),
		"performance_note":
		(
			"Godot exposes output latency but no per-bus or audio-mix CPU Performance monitor; "
			+ "process-frame time is context only and does not isolate audio cost."
		),
	}


## Stops all saved players and gives the audio server time to release playbacks.
func _stop_audio_and_settle() -> void:
	_voice_manager.stop_all()
	%Music.stop()
	%Ambience.stop()
	for _frame in 3:
		# Three frames are intentionally bounded audio teardown settling.
		await get_tree().process_frame  # gdstyle:ignore=quality/await-in-loop


## Saves, reloads, and applies non-default local audio settings.
func _check_settings_roundtrip() -> Dictionary:
	var written := S14Settings.new()
	written.master_level = 0.73
	written.music_level = 0.61
	written.sfx_level = 0.82
	written.master_muted = false
	written.music_muted = true
	written.sfx_muted = false
	var save_error := written.save(SETTINGS_PATH)

	var loaded := S14Settings.new()
	var load_error := loaded.load_settings(SETTINGS_PATH)
	var expected := written.snapshot()
	var actual := loaded.snapshot()
	var applied := load_error == OK and loaded.apply()
	var malformed_defaults := _check_malformed_settings_defaults()
	return {
		"passed": (
			save_error == OK
			and load_error == OK
			and expected == actual
			and applied
			and malformed_defaults["passed"]
		),
		"save_error": save_error,
		"load_error": load_error,
		"expected": expected,
		"actual": actual,
		"applied": applied,
		"malformed_defaults": malformed_defaults,
	}


## Proves malformed persisted types leave the settings object's safe defaults intact.
func _check_malformed_settings_defaults() -> Dictionary:
	var config := ConfigFile.new()
	config.set_value("audio", "master_level", "loud")
	config.set_value("audio", "master_muted", 1)
	config.set_value("audio", "music_muted", "true")
	config.set_value("audio", "sfx_muted", 0.0)
	var save_error := config.save(MALFORMED_SETTINGS_PATH)
	var loaded := S14Settings.new()
	var load_error := loaded.load_settings(MALFORMED_SETTINGS_PATH)
	var actual := loaded.snapshot()
	var expected := S14Settings.new().snapshot()
	return {
		"passed": save_error == OK and load_error == OK and actual == expected,
		"save_error": save_error,
		"load_error": load_error,
		"expected": expected,
		"actual": actual,
	}


## Checks independent request and cap outcomes at peak storm load.
func _validate_peak_report(report: Dictionary, failures: Array[String]) -> void:
	var caps: Dictionary = report["caps"]
	var active: Dictionary = report["active"]
	var requests: Dictionary = report["requests"]
	var expected_peak := {
		"engines": 8,
		"explosions": 8,
		"weapons": 6,
	}
	if caps != expected_peak:
		failures.append("category caps differ from independent expectations")
	if active != expected_peak:
		failures.append("instantaneous peak voices differ from independent expectations")
	if requests["explosions_accepted"] != 8 or requests["explosions_dropped"] != 16:
		failures.append("24-blast storm did not resolve as 8 accepted and 16 audio drops")
	if requests["weapon_accepted"] != 6 or requests["weapon_dropped"] != 6:
		failures.append("12-shot burst did not resolve as 6 accepted and 6 audio drops")


## Reads engine monitors available on the pinned build.
func _read_monitors() -> Dictionary:
	return {
		"process_ms": Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0,
		"physics_process_ms": Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0,
		"audio_output_latency_ms":
		Performance.get_monitor(Performance.AUDIO_OUTPUT_LATENCY) * 1000.0,
	}


## Summarizes monitor samples without representing process time as audio-only CPU.
func _summarize_monitors(samples: Array[Dictionary]) -> Dictionary:
	var process_values: Array[float] = []
	var physics_values: Array[float] = []
	var latency_values: Array[float] = []
	for sample: Dictionary in samples:
		process_values.append(float(sample["process_ms"]))
		physics_values.append(float(sample["physics_process_ms"]))
		latency_values.append(float(sample["audio_output_latency_ms"]))
	return {
		"sample_count": samples.size(),
		"process_ms_median": _median(process_values),
		"process_ms_worst": process_values.max(),
		"physics_process_ms_median": _median(physics_values),
		"physics_process_ms_worst": physics_values.max(),
		"audio_output_latency_ms_median": _median(latency_values),
		"audio_output_latency_ms_worst": latency_values.max(),
	}


## Returns the median of a non-empty floating-point sample set.
func _median(values: Array[float]) -> float:
	values.sort()
	var midpoint := values.size() / 2
	if values.size() % 2 == 0:
		return (values[midpoint - 1] + values[midpoint]) * 0.5
	return values[midpoint]


## Returns a user argument value with the requested prefix.
func _argument_value(prefix: String) -> String:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with(prefix):
			return argument.trim_prefix(prefix)
	return ""


## Writes a stable indented JSON result to the requested external path.
func _write_json(path: String, value: Dictionary) -> Error:
	var output := FileAccess.open(path, FileAccess.WRITE)
	if output == null:
		return FileAccess.get_open_error()
	output.store_string(JSON.stringify(value, "\t") + "\n")
	return OK
