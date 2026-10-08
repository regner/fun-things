extends "res://tests/fixtures/s07_driver/run.gd"
## Graphical T telemetry around the accepted sustained driver; the route driver is unchanged.

const WARMUP_SECONDS_DEFAULT: float = 60.0
const FIELDS: int = 10
const CAPPED_FPS: int = 60

var warmup_seconds: float = WARMUP_SECONDS_DEFAULT
var mode: String = "uncapped"
var samples: PackedFloat64Array = PackedFloat64Array()
var previous_frame_usec: int = 0
var viewport_rid: RID


## Applies the requested presentation cap and subscribes to completed automatic frames.
## The base driver accepts exactly one user argument, so options arrive by environment.
func _initialize() -> void:
	mode = OS.get_environment("S07_GRAPHICAL_MODE")
	if mode not in ["uncapped", "capped60"]:
		mode = "uncapped"
	if OS.has_environment("S07_GRAPHICAL_WARMUP"):
		warmup_seconds = OS.get_environment("S07_GRAPHICAL_WARMUP").to_float()

	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = CAPPED_FPS if mode == "capped60" else 0
	viewport_rid = root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(viewport_rid, true)
	RenderingServer.frame_post_draw.connect(_post_draw)
	super._initialize()


## Keeps the driver's own duration as measured time and adds a separately tagged warmup.
func _more_work() -> bool:
	for case_name: String in CASES:
		if counts[case_name] < MIN_TRAVERSALS_PER_ROUTE:
			return true

	return _elapsed_seconds() < duration_seconds + warmup_seconds


## Runs the unchanged driver, then writes the retained frame samples and run metadata.
func _run() -> void:
	var stream_path: String = "res://frames.f64"
	await super._run()
	var file: FileAccess = FileAccess.open(stream_path, FileAccess.WRITE)
	if file != null:
		file.store_buffer(samples.to_byte_array())
		file.close()

	var meta: Dictionary = {"fields": ["elapsed_s", "frame_interval_ms", "render_cpu_ms",
		"render_gpu_ms", "process_ms", "physics_ms", "draw_calls", "primitives", "objects",
		"video_mem_bytes"], "mode": mode, "warmup_seconds": warmup_seconds,
		"duration_seconds": duration_seconds, "frames": samples.size() / FIELDS,
		"display": DisplayServer.get_name(), "adapter": RenderingServer.get_video_adapter_name(),
		"adapter_vendor": RenderingServer.get_video_adapter_vendor(),
		"api_version": RenderingServer.get_video_adapter_api_version(),
		"window_size": [DisplayServer.window_get_size().x, DisplayServer.window_get_size().y],
		"vsync_mode": DisplayServer.window_get_vsync_mode(), "max_fps": Engine.max_fps,
		"static_memory_peak": Performance.get_monitor(Performance.MEMORY_STATIC_MAX),
		"node_count_end": Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
		"object_count_end": Performance.get_monitor(Performance.OBJECT_COUNT)}
	var meta_file: FileAccess = FileAccess.open("res://frames.json", FileAccess.WRITE)
	if meta_file != null:
		meta_file.store_string(JSON.stringify(meta, "\t") + "\n")
		meta_file.close()


## Records one row per drawn frame in memory; disk writes wait until the driver finishes.
func _post_draw() -> void:
	var now: int = Time.get_ticks_usec()
	if previous_frame_usec == 0 or measurement_start_usec == 0:
		previous_frame_usec = now
		return

	samples.append_array([
		(now - measurement_start_usec) / 1000000.0, (now - previous_frame_usec) / 1000.0,
		RenderingServer.viewport_get_measured_render_time_cpu(viewport_rid),
		RenderingServer.viewport_get_measured_render_time_gpu(viewport_rid),
		Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0,
		Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0,
		Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)])
	previous_frame_usec = now
