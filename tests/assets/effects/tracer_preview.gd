extends Node3D
## Bounded saved-asset preview and optional actual-render/allocation receipt, not a fire system.

const TRACER: PackedScene = preload(
	"res://scenes/effects/weapon_effects/weapon_effects_a_tracer.tscn"
)
const PREVIEW_FPS: int = 60
const PREVIEW_SECONDS: float = 60.0
const BURST_SIZE: int = 40
const CAPTURE_SIZE: Vector2i = Vector2i(1280, 800)
const MIN_CHANGED_PIXELS: int = 200

var _elapsed_seconds: float = 0.0
var _capturing: bool = false

@onready var _tracer: Node3D = $Tracer
@onready var _edge_tracer: Node3D = $EdgeTracer
@onready var _game_camera: Camera3D = $GameCamera
@onready var _detail_camera: Camera3D = $DetailCamera
@onready var _oblique_camera: Camera3D = $ObliqueCamera


## Cap all preview work before warming the renderer or accepting local preview keys.
func _ready() -> void:
	Engine.max_fps = PREVIEW_FPS
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	_capturing = "--tracer-capture" in OS.get_cmdline_user_args()
	if _capturing:
		_capture()


## Close unattended previews instead of leaving a rendering process running indefinitely.
func _process(delta: float) -> void:
	_elapsed_seconds += delta
	if _elapsed_seconds > PREVIEW_SECONDS:
		get_tree().quit(1 if _capturing else 0)


## Exercise saved poses only; no hit queries, gameplay input, or duplicate-event policy lives here.
func _unhandled_key_input(event: InputEvent) -> void:
	if _capturing or not event is InputEventKey or not event.pressed or event.echo:
		return

	match event.keycode:
		KEY_SPACE:
			_tracer.play()
		KEY_E:
			_edge_tracer.play()
		KEY_1:
			_game_camera.make_current()
		KEY_2:
			_detail_camera.make_current()
		KEY_3:
			_oblique_camera.make_current()
		KEY_ESCAPE:
			get_tree().quit()


## Save four native draws and compare each with its quiet frame to prove nonzero visible pixels.
func _capture() -> void:
	get_window().size = CAPTURE_SIZE
	await get_tree().create_timer(1.0).timeout
	var output: String = OS.get_environment("TRACER_OUTPUT")
	if output.is_empty() or DirAccess.make_dir_recursive_absolute(output) != OK:
		get_tree().quit(1)
		return

	var samples: Array[Dictionary] = []
	for sample: Array in [
		["gameplay", _game_camera, _tracer],
		["detail", _detail_camera, _tracer],
		["oblique", _oblique_camera, _tracer],
		["camera_edge", _game_camera, _edge_tracer],
	]:
		var result: Dictionary = await _capture_sample(sample[0], sample[1], sample[2], output)
		if result.is_empty():
			get_tree().quit(1)
			return

		samples.append(result)

	var allocation: Dictionary = await _measure_allocation()
	var receipt: Dictionary = {
		"engine": Engine.get_version_info().string,
		"renderer": RenderingServer.get_current_rendering_method(),
		"device": RenderingServer.get_video_adapter_name(),
		"fps_cap": PREVIEW_FPS,
		"resolution": [CAPTURE_SIZE.x, CAPTURE_SIZE.y],
		"game_camera_height_m": _game_camera.position.y,
		"game_camera_fov_degrees": _game_camera.fov,
		"timing_context": "contended desktop; not a quiet or GPU performance acceptance",
		"owner_art_review": "pending",
		"renders": samples,
		"allocation": allocation,
	}
	var file: FileAccess = FileAccess.open(output.path_join("validation.json"), FileAccess.WRITE)
	if file == null or not allocation.passed:
		get_tree().quit(1)
		return

	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	print("TRACER_CAPTURE_PASS ", JSON.stringify(receipt))
	get_tree().quit()


## Draw one unextended event at its real age and retain a quiet-frame difference measurement.
func _capture_sample(
	label: String, camera: Camera3D, effect: Node3D, output: String
) -> Dictionary:
	camera.make_current()
	await get_tree().create_timer(0.2).timeout
	await RenderingServer.frame_post_draw
	var before: Image = get_viewport().get_texture().get_image()
	print("TRACER_VIEW ", label, " camera=", camera.global_transform,
		" origin_pixel=", camera.unproject_position(Vector3.ZERO))
	var start_usec: int = Time.get_ticks_usec()
	if not effect.play():
		return {}

	await RenderingServer.frame_post_draw
	var age_ms: float = (Time.get_ticks_usec() - start_usec) / 1000.0
	var image: Image = get_viewport().get_texture().get_image()
	var changed: int = _changed_pixels(before, image)
	var filename: String = "tracer_" + label + ".png"
	if image.get_size() != CAPTURE_SIZE or image.save_png(output.path_join(filename)) != OK:
		return {}

	if changed < MIN_CHANGED_PIXELS:
		push_error("Tracer did not produce readable pixels: " + label)
		return {}

	await get_tree().create_timer(0.15).timeout
	if effect.is_active() or effect.visible:
		return {}

	return { "file": filename, "age_ms": age_ms, "changed_pixels": changed }


## Count materially changed pixels against the same camera's quiet reference, excluding overlays.
func _changed_pixels(before: Image, after: Image) -> int:
	var count: int = 0
	for y: int in range(100, CAPTURE_SIZE.y):
		for x: int in range(CAPTURE_SIZE.x):
			var difference: Color = after.get_pixel(x, y) - before.get_pixel(x, y)
			if maxf(difference.r, maxf(difference.g, difference.b)) > 0.15:
				count += 1

	return count


## Measure a finite forty-event burst without pooling or silently dropping any requested effect.
func _measure_allocation() -> Dictionary:
	var tracers: Array[Node3D] = []
	var samples_usec: Array[int] = []
	var before: Dictionary = _allocation_counters()
	var accepted: int = 0
	for index: int in range(BURST_SIZE):
		var start: int = Time.get_ticks_usec()
		var tracer: Node3D = TRACER.instantiate()
		add_child(tracer)
		tracers.append(tracer)
		if tracer.play():
			accepted += 1

		samples_usec.append(Time.get_ticks_usec() - start)

	var peak: Dictionary = _allocation_counters()
	await get_tree().create_timer(0.15).timeout
	var settled: int = 0
	for tracer: Node3D in tracers:
		if not tracer.is_active() and not tracer.visible:
			settled += 1

		tracer.queue_free()

	tracers.clear()
	await get_tree().process_frame
	await get_tree().process_frame
	var nodes_after: int = int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT))
	samples_usec.sort()
	return {
		"events": BURST_SIZE,
		"accepted": accepted,
		"settled": settled,
		"nodes_added": peak.nodes - before.nodes,
		"objects_added": peak.objects - before.objects,
		"static_memory_delta_bytes": peak.memory - before.memory,
		"allocation_median_usec": samples_usec[floori(BURST_SIZE * 0.5)],
		"allocation_max_usec": samples_usec[-1],
		"nodes_after_free_minus_before": nodes_after - before.nodes,
		"passed": accepted == BURST_SIZE and settled == BURST_SIZE and nodes_after == before.nodes,
	}


## Sample process-wide counters; deltas are observations, not exact allocator or GPU byte counts.
func _allocation_counters() -> Dictionary:
	return {
		"nodes": int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)),
		"objects": int(Performance.get_monitor(Performance.OBJECT_COUNT)),
		"memory": OS.get_static_memory_usage(),
	}
