extends Node3D
## Capped graphical VFX stress coordinator and telemetry writer for the S15 spike.

const CAPPED_FPS: int = 60
const EXPLOSION_PERIOD_SECONDS: float = 2.0
const DEFAULT_WARMUP_SECONDS: float = 5.0
const DEFAULT_DURATION_SECONDS: float = 20.0

var _explosion_count: int = 24
var _quality: String = "full"
var _warmup_seconds: float = DEFAULT_WARMUP_SECONDS
var _duration_seconds: float = DEFAULT_DURATION_SECONDS
var _explosion_elapsed_seconds: float = 0.0
var _measurement_active: bool = false
var _measurement_start_usec: int = 0
var _previous_frame_usec: int = 0
var _samples: Array[Array] = []
var _viewport_rid: RID

@onready var explosions: Node3D = $Effects/Explosions
@onready var rockets: Node3D = $Effects/Rockets


## Applies environment-selected load, starts capped rendering, and schedules the bounded run.
func _ready() -> void:
	_explosion_count = _explosion_count_from_environment()
	_quality = OS.get_environment("S15_QUALITY")
	if _quality not in ["full", "adaptive"]:
		_quality = "full"
	if OS.has_environment("S15_WARMUP_SECONDS"):
		_warmup_seconds = OS.get_environment("S15_WARMUP_SECONDS").to_float()
	if OS.has_environment("S15_DURATION_SECONDS"):
		_duration_seconds = OS.get_environment("S15_DURATION_SECONDS").to_float()

	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	Engine.max_fps = CAPPED_FPS
	_viewport_rid = get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(_viewport_rid, true)
	RenderingServer.frame_post_draw.connect(_post_draw)
	_configure_effects()
	call_deferred("_run")


## Advances only presentation motion and synchronized explosion recurrence.
func _process(delta: float) -> void:
	_explosion_elapsed_seconds += delta
	if _explosion_elapsed_seconds >= EXPLOSION_PERIOD_SECONDS:
		_explosion_elapsed_seconds = fmod(_explosion_elapsed_seconds, EXPLOSION_PERIOD_SECONDS)
		_trigger_explosions()

	for index: int in rockets.get_child_count():
		rockets.get_child(index).advance(delta)


## Returns the requested explosion count without replacing the default when no override exists.
func _explosion_count_from_environment() -> int:
	if not OS.has_environment("S15_EXPLOSIONS"):
		return _explosion_count
	return clampi(int(OS.get_environment("S15_EXPLOSIONS")), 1, 24)


## Executes warmup, measurement, optional capture, and clean fixture shutdown.
func _run() -> void:
	await get_tree().create_timer(_warmup_seconds).timeout
	_measurement_start_usec = Time.get_ticks_usec()
	_previous_frame_usec = 0
	_measurement_active = true
	_trigger_explosions()
	await get_tree().create_timer(0.25).timeout
	await _capture_if_requested()
	await get_tree().create_timer(maxf(0.0, _duration_seconds - 0.25)).timeout
	_measurement_active = false
	_write_result()
	get_tree().quit()


## Configures saved effect instances while retaining all requested explosion roots.
func _configure_effects() -> void:
	var quality_ratio: float = 0.5 if _quality == "adaptive" else 1.0
	for index: int in explosions.get_child_count():
		var explosion: Node = explosions.get_child(index)
		explosion.set_active(index < _explosion_count)
		explosion.set_quality(quality_ratio)
	for index: int in rockets.get_child_count():
		rockets.get_child(index).configure_lane(index)
	_trigger_explosions()


## Restarts each active explosion, preserving the owner's every-explosion feedback policy.
func _trigger_explosions() -> void:
	for index: int in _explosion_count:
		explosions.get_child(index).trigger()


## Records one telemetry row after each real rendered frame during the measured phase.
func _post_draw() -> void:
	if not _measurement_active:
		return
	var now_usec: int = Time.get_ticks_usec()
	if _previous_frame_usec == 0:
		_previous_frame_usec = now_usec
		return

	_samples.append([
		(now_usec - _measurement_start_usec) / 1000000.0,
		(now_usec - _previous_frame_usec) / 1000.0,
		RenderingServer.viewport_get_measured_render_time_cpu(_viewport_rid),
		RenderingServer.viewport_get_measured_render_time_gpu(_viewport_rid),
		Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0,
		Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0,
		Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),
	])
	_previous_frame_usec = now_usec


## Captures one actual viewport frame only when the runner supplies an external path.
func _capture_if_requested() -> void:
	var path: String = OS.get_environment("S15_CAPTURE_PATH")
	if path.is_empty():
		return

	await RenderingServer.frame_post_draw
	var image: Image = get_viewport().get_texture().get_image()
	image.save_png(path)


## Writes strict JSON telemetry to the fresh external runner directory.
func _write_result() -> void:
	var path: String = OS.get_environment("S15_RESULT_PATH")
	if path.is_empty():
		path = "res://s15-result.json"
	var result: Dictionary = {
		"explosions": _explosion_count,
		"quality": _quality,
		"warmup_seconds": _warmup_seconds,
		"duration_seconds": _duration_seconds,
		"fields": ["elapsed_s", "frame_interval_ms", "render_cpu_ms", "render_gpu_ms",
			"process_ms", "physics_ms", "draw_calls", "primitives", "objects",
			"video_mem_bytes"],
		"samples": _samples,
		"particle_capacity": _particle_capacity(self),
		"display": DisplayServer.get_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
		"api_version": RenderingServer.get_video_adapter_api_version(),
		"renderer": RenderingServer.get_current_rendering_method(),
		"max_fps": Engine.max_fps,
		"vsync_mode": DisplayServer.window_get_vsync_mode(),
	}
	var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		push_error("Unable to write S15 result: %s" % path)
		return
	file.store_string(JSON.stringify(result) + "\n")
	file.close()


## Counts configured particle capacity recursively for a reproducible load descriptor.
func _particle_capacity(node: Node) -> int:
	var total: int = 0
	for child: Node in node.get_children():
		if child is GPUParticles3D and child.is_visible_in_tree():
			total += ceili(child.amount * child.amount_ratio)
		total += _particle_capacity(child)
	return total
