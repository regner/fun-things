extends SceneTree
## Observes automatic Windows draws for the unchanged saved S02 corner and camera.

const FIXTURE: PackedScene = preload("res://tests/fixtures/s02/corner.tscn")
const CAPTURE_CALLBACKS: Array[int] = [3, 10, 30]
const REQUIRED_CALLBACKS: int = 30
const DEADLINE_SECONDS: float = 10.0

var _fixture: S02Fixture
var _callbacks: int = 0
var _previous_render_index: int = -1
var _started_ms: int = 0
var _finishing: bool = false
var _failures: Array[String] = []
var _captures: Array[Dictionary] = []


## Subscribes before instancing the saved corner so every receipt is an automatic draw.
func _initialize() -> void:
	_started_ms = Time.get_ticks_msec()
	RenderingServer.frame_post_draw.connect(_post_draw)
	_run.call_deferred()


## Instances only the saved scene and waits for a bounded number of genuine callbacks.
func _run() -> void:
	_fixture = FIXTURE.instantiate() as S02Fixture
	root.add_child(_fixture)
	await process_frame
	while not _finishing and _elapsed_seconds() < DEADLINE_SECONDS:
		await process_frame  # gdstyle:ignore=quality/await-in-loop

	if not _finishing:
		_failures.append("automatic post-draw callback deadline expired")
		_finish()


## Records actual window, viewport and current-camera state after each completed draw.
func _post_draw() -> void:
	if _finishing or not is_instance_valid(_fixture) or not _fixture.is_node_ready():
		return

	var render_index: int = Engine.get_frames_drawn()
	if render_index <= _previous_render_index:
		_failures.append("non-increasing rendered frame index")
	_previous_render_index = render_index
	_callbacks += 1
	var receipt: Dictionary = _snapshot()
	receipt["event"] = "frame"
	receipt["callback"] = _callbacks
	receipt["render_index"] = render_index
	receipt["monotonic_ms"] = Time.get_ticks_msec()
	if CAPTURE_CALLBACKS.has(_callbacks):
		_capture(receipt)
	print("S02_DRAW ", JSON.stringify(receipt))
	if _callbacks >= REQUIRED_CALLBACKS:
		_finishing = true
		_finish.call_deferred()


## Reads presentation state without changing the saved camera, actor, viewport or window size.
func _snapshot() -> Dictionary:
	var viewport: Viewport = root
	var camera: Camera3D = viewport.get_camera_3d()
	var camera_state: Dictionary = { "path": "", "current": false }
	if camera != null:
		camera_state = {
			"path": str(camera.get_path()),
			"transform": str(camera.global_transform),
			"position": _vector3(camera.global_position),
			"basis_x": _vector3(camera.global_basis.x),
			"basis_y": _vector3(camera.global_basis.y),
			"basis_z": _vector3(camera.global_basis.z),
			"projection": camera.projection,
			"fov": camera.fov,
			"near": camera.near,
			"far": camera.far,
			"current": camera.current,
		}
	var viewport_size: Vector2 = viewport.get_visible_rect().size
	var window_size: Vector2i = DisplayServer.window_get_size()
	return {
		"elapsed_ms": Time.get_ticks_msec() - _started_ms,
		"frames_drawn": Engine.get_frames_drawn(),
		"display": DisplayServer.get_name(),
		"can_draw": DisplayServer.window_can_draw(),
		"focus": DisplayServer.window_is_focused(),
		"mode": DisplayServer.window_get_mode(),
		"window_size": [window_size.x, window_size.y],
		"viewport_size": [viewport_size.x, viewport_size.y],
		"camera": camera_state,
		"input_active": _fixture.input_collector.active,
	}


## Saves viewport pixels from selected automatic callbacks and binds their dimensions and hash.
func _capture(receipt: Dictionary) -> void:
	var image: Image = root.get_texture().get_image()
	var name: String = "s02-draw-%02d.png" % _callbacks
	var path: String = "user://" + name
	var error: Error = image.save_png(path)
	var capture: Dictionary = {
		"callback": _callbacks,
		"name": name,
		"width": image.get_width(),
		"height": image.get_height(),
		"save_error": error,
		"sha256": FileAccess.get_sha256(path) if error == OK else "",
	}
	if error != OK:
		_failures.append("PNG save failed at callback %d" % _callbacks)
	_captures.append(capture)
	receipt["png"] = capture


## Validates the declared Windows observation facts and quits with a structured result.
func _finish() -> void:
	if not _finishing:
		_finishing = true
	_expect(_callbacks >= 3, "fewer than three automatic post-draw callbacks")
	var state: Dictionary = _snapshot()
	var camera: Dictionary = state.camera
	_expect(state.display == "Windows", "display backend is not Windows")
	_expect(state.can_draw, "native window cannot draw")
	_expect(state.window_size == [1280, 800], "native window is not 1280x800")
	_expect(state.viewport_size == [1280.0, 800.0], "viewport is not 1280x800")
	_expect(
		str(camera.get("path", "")).ends_with("/S02/CameraRig/Camera3D"),
		"saved S02 camera is not current",
	)
	_expect(
		camera.get("current", false)
		and camera.get("projection", -1) == Camera3D.PROJECTION_PERSPECTIVE,
		"camera is not current perspective",
	)
	_expect(absf(camera.get("fov", 0.0) - 42.0) <= 0.001,
		"camera FOV differs from saved 42 degrees")
	_expect(
		absf(camera.get("near", 0.0) - 0.1) <= 0.001
		and absf(camera.get("far", 0.0) - 160.0) <= 0.001,
		"camera clipping differs from saved state",
	)
	_expect(_captures.size() == CAPTURE_CALLBACKS.size(),
		"automatic callback captures are incomplete")
	var result: Dictionary = {
		"event": "result",
		"ok": _failures.is_empty(),
		"callbacks": _callbacks,
		"failures": _failures,
		"captures": _captures,
		"final": state,
		"engine": Engine.get_version_info().string,
	}
	print("S02_DRAW ", JSON.stringify(result))
	_fixture.queue_free()
	quit(0 if _failures.is_empty() else 1)


## Accumulates one independent observation failure while preserving later receipts.
func _expect(condition: bool, failure: String) -> void:
	if not condition:
		_failures.append(failure)


## Returns elapsed monotonic time for the bounded callback wait.
func _elapsed_seconds() -> float:
	return float(Time.get_ticks_msec() - _started_ms) / 1000.0


## Encodes vectors explicitly so JSON receipts preserve camera axes numerically.
func _vector3(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]
