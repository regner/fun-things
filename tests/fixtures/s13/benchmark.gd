extends Node3D
## Measures the saved S13 crowd using engine telemetry in graphical or headless mode.

const CAPPED_FPS: int = 60
const HEADLESS_FPS_LIMIT: int = 1000
const DEFAULT_WARMUP_SECONDS: float = 2.0
const DEFAULT_DURATION_SECONDS: float = 6.0

var _mode: String = "full"
var _output_path: String
var _capture_path: String
var _warmup_seconds: float = DEFAULT_WARMUP_SECONDS
var _duration_seconds: float = DEFAULT_DURATION_SECONDS
var _started_usec: int
var _previous_frame_usec: int
var _capture_saved: bool = false
var _samples: Dictionary = {
	"frame_ms": [],
	"process_ms": [],
	"physics_ms": [],
	"render_cpu_ms": [],
	"render_gpu_ms": [],
	"draw_calls": [],
	"primitives": [],
	"objects": [],
}
var _viewport_rid: RID

@onready var _live: Node3D = $Live
@onready var _dead: Node3D = $Dead


## Applies benchmark options, validates the public character API and starts sampling.
func _ready() -> void:
	_mode = OS.get_environment("S13_MODE")
	if _mode not in ["full", "throttled"]:
		_mode = "full"
	_output_path = OS.get_environment("S13_OUTPUT")
	_capture_path = OS.get_environment("S13_CAPTURE")
	if OS.has_environment("S13_WARMUP_SECONDS"):
		_warmup_seconds = OS.get_environment("S13_WARMUP_SECONDS").to_float()
	if OS.has_environment("S13_DURATION_SECONDS"):
		_duration_seconds = OS.get_environment("S13_DURATION_SECONDS").to_float()
	if _output_path.is_empty():
		push_error("S13_OUTPUT is required")
		get_tree().quit(2)
		return

	var headless: bool = DisplayServer.get_name() == "headless"
	Engine.max_fps = HEADLESS_FPS_LIMIT if headless else CAPPED_FPS
	if not headless:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	_viewport_rid = get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(_viewport_rid, true)
	RenderingServer.frame_post_draw.connect(_on_frame_post_draw)
	_configure_characters()
	if not _validate_fixture():
		get_tree().quit(3)
		return

	_started_usec = Time.get_ticks_usec()
	_previous_frame_usec = _started_usec


## Records per-frame process telemetry and completes after the requested wall-clock duration.
func _process(_delta: float) -> void:
	if _started_usec == 0:
		return

	var now_usec: int = Time.get_ticks_usec()
	var elapsed_seconds: float = (now_usec - _started_usec) / 1000000.0
	if elapsed_seconds >= _warmup_seconds:
		_samples.frame_ms.append((now_usec - _previous_frame_usec) / 1000.0)
		_samples.process_ms.append(Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0)
		_samples.physics_ms.append(
			Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0
		)
	_previous_frame_usec = now_usec
	if elapsed_seconds >= _warmup_seconds + _duration_seconds:
		_finish()


## Configures locomotion states, corpse final poses and the requested update policy.
func _configure_characters() -> void:
	var states: Array[StringName] = [&"idle", &"walk", &"run"]
	var index: int = 0
	for child: Node in _live.get_children():
		child.call("set_animation_state", states[index % states.size()])
		child.call("set_animation_throttling", _mode == "throttled")
		index += 1
	for child: Node in _dead.get_children():
		child.call("set_death_final_pose")


## Validates population, clip, rig and triangle contracts through the wrapper's public API.
func _validate_fixture() -> bool:
	if _live.get_child_count() != 68 or _dead.get_child_count() != 16:
		push_error("S13 fixture requires 68 live and 16 dead presentations")
		return false
	var sample: Node = _live.get_child(0)
	var clips: Array = sample.call("get_animation_names")
	for required: StringName in [&"idle", &"walk", &"run", &"death"]:
		if required not in clips:
			push_error("S13 missing imported clip: %s" % required)
			return false
	var bones: PackedStringArray = sample.call("get_bone_names")
	for required: String in ["root", "spine", "head", "arm_l", "arm_r", "leg_l", "leg_r"]:
		if required not in bones:
			push_error("S13 missing imported bone: %s" % required)
			return false
	var triangles: int = sample.call("get_triangle_count")
	if triangles <= 0 or triangles >= 1500:
		push_error("S13 triangle contract failed: %d" % triangles)
		return false
	return true


## Captures completed-frame telemetry and one requested screenshot from the actual viewport.
func _on_frame_post_draw() -> void:
	if _started_usec == 0 or DisplayServer.get_name() == "headless":
		return

	var now_usec: int = Time.get_ticks_usec()
	var elapsed_seconds: float = (now_usec - _started_usec) / 1000000.0
	if elapsed_seconds >= _warmup_seconds:
		_samples.render_cpu_ms.append(
			RenderingServer.viewport_get_measured_render_time_cpu(_viewport_rid)
		)
		_samples.render_gpu_ms.append(
			RenderingServer.viewport_get_measured_render_time_gpu(_viewport_rid)
		)
		_samples.draw_calls.append(
			Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
		)
		_samples.primitives.append(
			Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
		)
		_samples.objects.append(
			Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)
		)
		if not _capture_saved and not _capture_path.is_empty():
			var image: Image = get_viewport().get_texture().get_image()
			var capture_error: Error = image.save_png(_capture_path)
			if capture_error != OK:
				push_error("S13 capture failed: %s" % error_string(capture_error))
			_capture_saved = true


## Writes raw telemetry and immutable run metadata before exiting cleanly.
func _finish() -> void:
	set_process(false)
	var active_count: int = 0
	for child: Node in _live.get_children():
		if child.call("is_animation_active"):
			active_count += 1
	var sample: Node = _live.get_child(0)
	var result: Dictionary = {
		"mode": _mode,
		"display": DisplayServer.get_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
		"api": RenderingServer.get_video_adapter_api_version(),
		"max_fps": Engine.max_fps,
		"vsync": DisplayServer.window_get_vsync_mode(),
		"warmup_seconds": _warmup_seconds,
		"duration_seconds": _duration_seconds,
		"live_count": _live.get_child_count(),
		"dead_count": _dead.get_child_count(),
		"active_animation_count": active_count,
		"clips": sample.call("get_animation_names"),
		"bones": sample.call("get_bone_names"),
		"triangles_per_character": sample.call("get_triangle_count"),
		"node_count": Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
		"video_memory_bytes": Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),
		"samples": _samples,
	}
	var file: FileAccess = FileAccess.open(_output_path, FileAccess.WRITE)
	if file == null:
		push_error("S13 could not open output: %s" % _output_path)
		get_tree().quit(4)
		return

	file.store_string(JSON.stringify(result) + "\n")
	file.close()
	get_tree().quit()
