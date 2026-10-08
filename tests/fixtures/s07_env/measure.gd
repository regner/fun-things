extends SceneTree
## Measures one saved S07 environment while a fixed top-down observer follows a saved grid.

const FIELDS: int = 10
const CAMERA_SPEED_MPS: float = 15.0
const CAPPED_FPS: int = 60
const EXPECTED_ARGUMENTS: int = 1

var city: Node3D
var camera: Camera3D
var route: Array[Vector3] = []
var route_length_m: float = 0.0
var measurement_start_usec: int = 0
var previous_frame_usec: int = 0
var samples := PackedFloat64Array()
var viewport_rid: RID


## Configures capped presentation and starts the asynchronous measurement sequence.
func _initialize() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = CAPPED_FPS
	RenderingServer.frame_post_draw.connect(_post_draw)
	call_deferred("_run")


## Loads, reloads, traverses, records telemetry, and exits with a bounded result.
func _run() -> void:  # gdstyle:ignore=quality/max-function-length,quality/max-local-variables
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	var output_directory: String = OS.get_environment("S07_ENV_OUTPUT")
	var warmup_seconds: float = OS.get_environment("S07_ENV_WARMUP").to_float()
	var duration_seconds: float = OS.get_environment("S07_ENV_DURATION").to_float()
	if arguments.size() != EXPECTED_ARGUMENTS or output_directory.is_empty():
		push_error("S07_ENV_MEASURE_INVALID_ARGUMENTS")
		quit(2)
		return

	var scene_path: String = arguments[0]
	var cold_started: int = Time.get_ticks_usec()
	var packed: PackedScene = load(scene_path) as PackedScene
	var cold_resource_loaded: int = Time.get_ticks_usec()
	if packed == null:
		push_error("S07_ENV_MEASURE_LOAD_FAILED path=%s" % scene_path)
		quit(1)
		return
	city = packed.instantiate() as Node3D
	root.add_child(city)
	await process_frame
	var cold_ready: int = Time.get_ticks_usec()
	var cold_resource_load_ms: float = (cold_resource_loaded - cold_started) / 1000.0
	var cold_first_load_ms: float = (cold_ready - cold_started) / 1000.0

	root.remove_child(city)
	city.free()
	city = null
	await process_frame
	var warm_started: int = Time.get_ticks_usec()
	packed = load(scene_path) as PackedScene
	city = packed.instantiate() as Node3D
	root.add_child(city)
	await process_frame
	var warm_reload_ms: float = (Time.get_ticks_usec() - warm_started) / 1000.0

	camera = city.get_node("Camera") as Camera3D
	if camera == null:
		push_error("S07_ENV_MEASURE_CAMERA_MISSING")
		quit(1)
		return
	camera.current = true
	viewport_rid = root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(viewport_rid, true)
	_build_route()
	measurement_start_usec = Time.get_ticks_usec()
	previous_frame_usec = measurement_start_usec

	while _elapsed_seconds() < warmup_seconds + duration_seconds:
		_update_camera(_elapsed_seconds())
		# Real presented frames and pacing are the behavior under measurement.
		await process_frame  # gdstyle:ignore=quality/await-in-loop

	await RenderingServer.frame_post_draw
	_write_results(
		output_directory,
		scene_path,
		warmup_seconds,
		duration_seconds,
		cold_resource_load_ms,
		cold_first_load_ms,
		warm_reload_ms,
	)
	quit()


## Builds a deterministic lawnmower route through every authored block center.
func _build_route() -> void:
	var columns: int = int(city.get_meta("grid_columns"))
	var rows: int = int(city.get_meta("grid_rows"))
	var block_size_m: float = float(city.get_meta("block_size_m"))
	for row_index: int in range(rows):
		var row: int = row_index
		for column_index: int in range(columns):
			var column: int = column_index if row % 2 == 0 else columns - column_index - 1
			route.append(Vector3(
				(column - (columns - 1) / 2.0) * block_size_m,
				camera.position.y,
				(row - (rows - 1) / 2.0) * block_size_m,
			))
	for index: int in range(1, route.size()):
		route_length_m += route[index - 1].distance_to(route[index])


## Moves at car speed along the route, reversing at its ends without teleporting.
func _update_camera(elapsed_seconds: float) -> void:
	if route.size() < 2 or is_zero_approx(route_length_m):
		return

	var cycle_distance: float = fmod(elapsed_seconds * CAMERA_SPEED_MPS, route_length_m * 2.0)
	var distance: float = cycle_distance
	var reversed: bool = distance > route_length_m
	if reversed:
		distance = route_length_m * 2.0 - distance
	for index: int in range(1, route.size()):
		var segment_length: float = route[index - 1].distance_to(route[index])
		if distance <= segment_length:
			camera.position = route[index - 1].lerp(route[index], distance / segment_length)
			return
		distance -= segment_length


## Returns wall-clock seconds since the warmup and measured traversal began.
func _elapsed_seconds() -> float:
	return (Time.get_ticks_usec() - measurement_start_usec) / 1000000.0


## Records one row after each drawn frame without writing in the rendering callback.
func _post_draw() -> void:
	if measurement_start_usec == 0:
		return

	var now: int = Time.get_ticks_usec()
	samples.append_array([
		(now - measurement_start_usec) / 1000000.0,
		(now - previous_frame_usec) / 1000.0,
		RenderingServer.viewport_get_measured_render_time_cpu(viewport_rid),
		RenderingServer.viewport_get_measured_render_time_gpu(viewport_rid),
		Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0,
		Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),
		Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
	])
	previous_frame_usec = now


## Writes binary frame samples and compact run metadata to the external evidence directory.
# gdstyle:ignore=quality/max-parameters
func _write_results(
	output_directory: String,
	scene_path: String,
	warmup_seconds: float,
	duration_seconds: float,
	cold_resource_load_ms: float,
	cold_first_load_ms: float,
	warm_reload_ms: float,
) -> void:
	var frame_path: String = output_directory.path_join("frames.f64")
	var frame_file: FileAccess = FileAccess.open(frame_path, FileAccess.WRITE)
	if frame_file != null:
		frame_file.store_buffer(samples.to_byte_array())
		frame_file.close()

	var result: Dictionary = {
		"scene": scene_path,
		"fields": ["elapsed_s", "frame_interval_ms", "render_cpu_ms", "render_gpu_ms",
			"physics_ms", "draw_calls", "objects", "primitives", "video_mem_bytes",
			"node_count"],
		"warmup_seconds": warmup_seconds,
		"duration_seconds": duration_seconds,
		"cold_resource_load_ms": cold_resource_load_ms,
		"cold_first_load_ms": cold_first_load_ms,
		"warm_reload_ms": warm_reload_ms,
		"block_count": int(city.get_meta("block_count")),
		"authored_instance_count": int(city.get_meta("block_count")) * 6,
		"scene_node_count": _count_nodes(city),
		"static_collider_count": _count_static_colliders(city),
		"route_length_m": route_length_m,
		"camera_speed_mps": CAMERA_SPEED_MPS,
		"display": DisplayServer.get_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
		"adapter_vendor": RenderingServer.get_video_adapter_vendor(),
		"api_version": RenderingServer.get_video_adapter_api_version(),
		"window_size": [DisplayServer.window_get_size().x, DisplayServer.window_get_size().y],
		"vsync_mode": DisplayServer.window_get_vsync_mode(),
		"max_fps": Engine.max_fps,
	}
	var result_path: String = output_directory.path_join("result.json")
	var result_file: FileAccess = FileAccess.open(result_path, FileAccess.WRITE)
	if result_file != null:
		result_file.store_string(JSON.stringify(result, "\t") + "\n")
		result_file.close()


## Counts the instantiated saved hierarchy, including the supplied root.
func _count_nodes(node: Node) -> int:
	var count: int = 1
	for child: Node in node.get_children():
		count += _count_nodes(child)
	return count


## Counts static collision bodies in the instantiated saved hierarchy.
func _count_static_colliders(node: Node) -> int:
	var count: int = 1 if node is StaticBody3D else 0
	for child: Node in node.get_children():
		count += _count_static_colliders(child)
	return count
