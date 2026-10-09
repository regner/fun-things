extends SceneTree
## Windowed observer that instances one saved S06 scene and drives only its public route API.

const EXPECTED_SIZE: Vector2i = Vector2i(1280, 800)
const SETTLE_FRAMES: int = 30
const ROUTES: Array[String] = ["foot", "east_to_north", "west_to_south"]
const CAPTURE_TICKS: Dictionary = {
	"foot": [120, 240, 360],
	"east_to_north": [180, 360, 540],
	"west_to_south": [180, 360, 540],
}
const ALLOWED_SCENES: Array[String] = [
	"res://tests/fixtures/s06/intersection.tscn",
	"res://tests/fixtures/s06/intersection_wide.tscn",
]

var _fixture: S06Fixture
var _output: String
var _scene_label: String
var _captures: Array[Dictionary] = []
var _failures: Array[String] = []
var _route_finished: bool = false
var _route_samples: Array[Dictionary] = []
var _route_timed_out: bool = false
var _route_results: Dictionary = {}


## Defers scene loading until the graphical SceneTree can admit the saved hierarchy.
func _initialize() -> void:
	root.show()
	_run.call_deferred()


## Captures the static view and three automatic frames during every public route.
func _run() -> void:
	var options: Dictionary = _options()
	var scene_path: String = options.get("scene", "")
	_output = options.get("output", "")
	_scene_label = options.get("label", "")
	if scene_path not in ALLOWED_SCENES or _output.is_empty() or _scene_label.is_empty():
		_failures.append("expected allowed --scene, --label and --output arguments")
		_finish()
		return

	var packed: PackedScene = load(scene_path) as PackedScene
	if packed == null:
		_failures.append("saved scene unavailable")
		_finish()
		return

	_fixture = packed.instantiate() as S06Fixture
	_fixture.route_finished.connect(_on_route_finished)
	root.add_child(_fixture)
	await process_frame
	if root.size != EXPECTED_SIZE:
		_failures.append("viewport is %s, expected %s" % [root.size, EXPECTED_SIZE])

	var minimap: S06Minimap = _fixture.get_node("Ui/Minimap") as S06Minimap
	minimap.set_marker(_fixture.body_state("foot").position)
	await _settle()
	await _capture("static", "foot", 0)
	for case_name: String in ROUTES:
		await _run_route(case_name)  # gdstyle:ignore=quality/await-in-loop

	_finish()


## Parses only explicit key-value user arguments supplied after the engine separator.
func _options() -> Dictionary:
	var result: Dictionary = {}
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--") and argument.contains("="):
			var parts: PackedStringArray = argument.substr(2).split("=", false, 1)
			result[parts[0]] = parts[1]

	return result


## Waits for ordinary graphical frames before taking the static observation.
func _settle() -> void:
	for frame: int in SETTLE_FRAMES:
		await process_frame  # gdstyle:ignore=quality/await-in-loop


## Drives one existing route and captures its declared approach/middle/exit samples.
func _run_route(case_name: String) -> void:
	_route_finished = false
	_route_samples = []
	_route_timed_out = false
	var code: String = _fixture.start_route(case_name)
	if code != "OK":
		_failures.append(case_name + " admission: " + code)
		return

	for target_tick: int in CAPTURE_TICKS[case_name]:
		while not _route_finished and _fixture.ticks < target_tick:
			await physics_frame  # gdstyle:ignore=quality/await-in-loop
		if _route_finished:
			_failures.append(case_name + " ended before capture tick " + str(target_tick))
			return
		await _capture(  # gdstyle:ignore=quality/await-in-loop
			case_name + "-%03d" % target_tick, case_name, target_tick
		)

	while not _route_finished:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
	_route_results[case_name] = {
		"samples": _route_samples.size(),
		"timed_out": _route_timed_out,
	}
	if _route_timed_out or _route_samples.is_empty():
		_failures.append(case_name + " timed out or returned no samples")


## Retains completion state without changing body placement or controller intent.
func _on_route_finished(case_name: String, samples: Array[Dictionary], timed_out: bool) -> void:
	_route_finished = true
	_route_samples = samples
	_route_timed_out = timed_out
	print("S06_CAPTURE_ROUTE ", case_name, " ", samples.size(), " ", timed_out)


## Saves one viewport image with matching camera, body and minimap-marker coordinates.
func _capture(  # gdstyle:ignore=quality/max-local-variables
	label: String, body_case: String, requested_tick: int
) -> void:
	paused = true
	await process_frame
	RenderingServer.force_draw()
	var state: Dictionary = _fixture.body_state(body_case)
	var minimap: S06Minimap = _fixture.get_node("Ui/Minimap") as S06Minimap
	var camera: Camera3D = _fixture.get_node("Camera") as Camera3D
	var body_position: Vector3 = state.position
	var marker_position: Vector3 = minimap.marker
	var marker_local_px: Vector2 = minimap.project_point(marker_position)
	var body_local_px: Vector2 = minimap.project_point(body_position)
	var image: Image = root.get_texture().get_image()
	var png_name: String = label + ".png"
	var png_path: String = _output.path_join(png_name)
	var error: Error = image.save_png(png_path)
	var camera_transform: Transform3D = camera.global_transform
	_captures.append({
		"capture": label,
		"scene": _scene_label,
		"body_case": body_case,
		"requested_tick": requested_tick,
		"actual_tick": _fixture.ticks,
		"png": png_name,
		"png_sha256": FileAccess.get_sha256(png_path) if error == OK else "",
		"save_error": error,
		"viewport_px": [image.get_width(), image.get_height()],
		"camera": {
			"position_m": _vector3(camera_transform.origin),
			"basis_x": _vector3(camera_transform.basis.x),
			"basis_y": _vector3(camera_transform.basis.y),
			"basis_z": _vector3(camera_transform.basis.z),
			"fov_degrees": camera.fov,
			"near_m": camera.near,
			"far_m": camera.far,
		},
		"body_position_m": _vector3(body_position),
		"body_yaw_radians": state.yaw,
		"minimap_marker_position_m": _vector3(marker_position),
		"minimap_marker_local_px": _vector2(marker_local_px),
		"body_expected_local_px": _vector2(body_local_px),
		"marker_body_distance_m": marker_position.distance_to(body_position),
		"marker_body_distance_px": marker_local_px.distance_to(body_local_px),
		"body_viewport_px": _vector2(camera.unproject_position(body_position)),
		"renderer": RenderingServer.get_current_rendering_method(),
	})
	print("S06_CAPTURE_FRAME ", _scene_label, " ", label, " ", image.get_size())
	paused = false


## Converts a three-dimensional engine value to strict JSON numbers.
func _vector3(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]


## Converts a two-dimensional engine value to strict JSON numbers.
func _vector2(value: Vector2) -> Array[float]:
	return [value.x, value.y]


## Writes the complete observation receipt and exits after freeing the owned fixture.
func _finish() -> void:
	var result: Dictionary = {
		"ok": _failures.is_empty(),
		"failures": _failures,
		"scene": _scene_label,
		"captures": _captures,
		"routes": _route_results,
		"engine": Engine.get_version_info(),
		"display_server": DisplayServer.get_name(),
	}
	var file: FileAccess = FileAccess.open(_output.path_join("observation.json"), FileAccess.WRITE)
	if file == null:
		push_error("could not write observation receipt")
		quit(1)
		return

	file.store_string(JSON.stringify(result, "\t") + "\n")
	file.close()
	if _fixture != null:
		_fixture.queue_free()
		await process_frame
	print("S06_CAPTURE_RESULT ", JSON.stringify({ "ok": result.ok, "failures": _failures }))
	quit(0 if result.ok else 1)
