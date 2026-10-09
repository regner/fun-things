extends SceneTree
## Measures capped whole-island loading, residency, draw work, and route frame receipts.

const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")
const CAPACITY_RIG_SCENE: PackedScene = preload(
	"res://tests/performance/world/capacity_rig.tscn"
)
const FRAME_CAP: int = 60
const WARMUP_SECONDS: float = 2.0
const MEASUREMENT_SECONDS: float = 30.0
const SAMPLE_FIELDS: int = 10

var _camera: Camera3D
var _measurement_started_usec: int = 0
var _previous_frame_usec: int = 0
var _samples := PackedFloat64Array()
var _viewport_rid: RID
var _route: Array[Vector3] = [
	Vector3(-410, 47, -150),
	Vector3(-350, 47, -88),
	Vector3(-165, 47, -150),
	Vector3(105, 47, -70),
	Vector3(-180, 47, 135),
	Vector3(-100, 47, -5),
	Vector3(75, 47, 175),
	Vector3(265, 47, 50),
	Vector3(460, 47, 69),
]
var _route_length_m: float = 0.0


## Applies the cap before loading measured content and starts the bounded run.
func _initialize() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = FRAME_CAP
	RenderingServer.frame_post_draw.connect(_on_frame_post_draw)
	_run.call_deferred()


## Loads the saved Match, traverses every district view, and writes external evidence.
func _run() -> void:  # gdstyle:ignore=quality/max-function-length,quality/max-local-variables
	var output_directory: String = OS.get_environment("BRACKETT_BASELINE_OUTPUT")
	if output_directory.is_empty():
		push_error("BRACKETT_BASELINE_OUTPUT_REQUIRED")
		quit(2)
		return
	DirAccess.make_dir_recursive_absolute(output_directory)

	var load_started_usec: int = Time.get_ticks_usec()
	var match_root: Node3D = MATCH_SCENE.instantiate() as Node3D
	var instantiated_usec: int = Time.get_ticks_usec()
	root.add_child(match_root)
	var rig: Node3D = CAPACITY_RIG_SCENE.instantiate() as Node3D
	match_root.add_child(rig)
	_camera = rig.get_node("Camera3D") as Camera3D
	_camera.make_current()
	await process_frame
	await RenderingServer.frame_post_draw
	var first_draw_usec: int = Time.get_ticks_usec()

	_viewport_rid = root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(_viewport_rid, true)
	_build_route_length()
	_measurement_started_usec = Time.get_ticks_usec()
	_previous_frame_usec = _measurement_started_usec
	while _elapsed_seconds() < WARMUP_SECONDS + MEASUREMENT_SECONDS:
		_update_camera(_elapsed_seconds())
		await process_frame  # gdstyle:ignore=quality/await-in-loop

	await RenderingServer.frame_post_draw
	var loading: Dictionary = {
		"instantiate_ms": (instantiated_usec - load_started_usec) / 1000.0,
		"first_draw_ms": (first_draw_usec - load_started_usec) / 1000.0,
	}
	_write_results(output_directory, match_root, loading)
	await _save_capture(output_directory.path_join("route-final.png"))
	quit()


## Computes the authored district-view route length for a reproducible sweep speed.
func _build_route_length() -> void:
	for index: int in range(1, _route.size()):
		_route_length_m += _route[index - 1].distance_to(_route[index])


## Moves continuously through the authored district views during the measured interval.
func _update_camera(elapsed_seconds: float) -> void:
	var measured_elapsed: float = maxf(0.0, elapsed_seconds - WARMUP_SECONDS)
	var distance: float = minf(
		measured_elapsed / MEASUREMENT_SECONDS * _route_length_m, _route_length_m
	)
	for index: int in range(1, _route.size()):
		var segment_length: float = _route[index - 1].distance_to(_route[index])
		if distance <= segment_length:
			_camera.position = _route[index - 1].lerp(
				_route[index], distance / segment_length
			)
			return
		distance -= segment_length
	_camera.position = _route.back()


## Returns wall-clock time since the bounded warmup and measurement began.
func _elapsed_seconds() -> float:
	return (Time.get_ticks_usec() - _measurement_started_usec) / 1_000_000.0


## Records actual post-draw receipts only after the declared warmup interval.
func _on_frame_post_draw() -> void:
	if _measurement_started_usec == 0:
		return

	var now_usec: int = Time.get_ticks_usec()
	if _elapsed_seconds() < WARMUP_SECONDS:
		_previous_frame_usec = now_usec
		return

	_samples.append_array([
		(_elapsed_seconds() - WARMUP_SECONDS),
		(now_usec - _previous_frame_usec) / 1000.0,
		RenderingServer.viewport_get_measured_render_time_cpu(_viewport_rid),
		RenderingServer.viewport_get_measured_render_time_gpu(_viewport_rid),
		Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0,
		Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0,
		Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),
		Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
	])
	_previous_frame_usec = now_usec


## Writes raw frame rows and self-describing run metadata outside the checkout.
func _write_results(output_directory: String, match_root: Node3D, loading: Dictionary) -> void:
	var frame_file: FileAccess = FileAccess.open(
		output_directory.path_join("frames.f64"), FileAccess.WRITE
	)
	frame_file.store_buffer(_samples.to_byte_array())
	frame_file.close()

	var result: Dictionary = {
		"engine": Engine.get_version_info().string,
		"match_scene": "res://scenes/match/match.tscn",
		"world_scene": match_root.get_node("World").scene_file_path,
		"content_identity": (match_root.get_node("CityData") as CityData).identity(),
		"fields": [
			"elapsed_s", "frame_interval_ms", "render_cpu_ms", "render_gpu_ms",
			"process_ms", "physics_ms", "draw_calls", "objects", "video_mem_bytes",
			"node_count",
		],
		"sample_fields": SAMPLE_FIELDS,
		"sample_count": _samples.size() / SAMPLE_FIELDS,
		"warmup_seconds": WARMUP_SECONDS,
		"measurement_seconds": MEASUREMENT_SECONDS,
		"instantiate_ms": loading.instantiate_ms,
		"first_draw_ms": loading.first_draw_ms,
		"scene_node_count": _count_nodes(match_root),
		"static_body_count": _count_static_bodies(match_root),
		"static_collision_shape_count": _count_static_shapes(match_root),
		"static_memory_peak_bytes": Performance.get_monitor(Performance.MEMORY_STATIC_MAX),
		"route_length_m": _route_length_m,
		"route_camera_speed_mps": _route_length_m / MEASUREMENT_SECONDS,
		"display": DisplayServer.get_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
		"adapter_vendor": RenderingServer.get_video_adapter_vendor(),
		"api_version": RenderingServer.get_video_adapter_api_version(),
		"window_size": [DisplayServer.window_get_size().x, DisplayServer.window_get_size().y],
		"vsync_mode": DisplayServer.window_get_vsync_mode(),
		"max_fps": Engine.max_fps,
	}
	var result_file: FileAccess = FileAccess.open(
		output_directory.path_join("result.json"), FileAccess.WRITE
	)
	result_file.store_string(JSON.stringify(result, "\t") + "\n")
	result_file.close()


## Saves one bounded final-route receipt after a completed draw.
func _save_capture(path: String) -> void:
	await RenderingServer.frame_post_draw
	var image: Image = root.get_texture().get_image()
	var error: Error = image.save_png(path)
	if error != OK:
		push_error("BRACKETT_BASELINE_CAPTURE_FAILED error=%d" % error)


## Counts every instantiated saved node, including the Match root.
func _count_nodes(node: Node) -> int:
	var count: int = 1
	for child: Node in node.get_children():
		count += _count_nodes(child)
	return count


## Counts static collision owners in the instantiated saved Match hierarchy.
func _count_static_bodies(node: Node) -> int:
	var count: int = 1 if node is StaticBody3D else 0
	for child: Node in node.get_children():
		count += _count_static_bodies(child)
	return count


## Counts enabled static shapes independently from their owning body count.
func _count_static_shapes(node: Node) -> int:
	var count: int = 0
	if node is CollisionShape3D and node.get_parent() is StaticBody3D and not node.disabled:
		count = 1
	for child: Node in node.get_children():
		count += _count_static_shapes(child)
	return count
