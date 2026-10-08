class_name S05DrawProof
extends S05SavedProof
## Observes the accepted chain through a saved camera and genuine post-draw callbacks.

const CAMERA_SCENE: String = "res://tests/fixtures/s05_draw/camera.tscn"
const MAX_FRAME_RECEIPTS: int = 65_536
const MAX_EXPIRY_WAIT_TICKS: int = 120

var draw_callbacks: int = 0
var previous_render_index: int = -1
var capture_paths: Dictionary = {}
var observed_events: Array[Dictionary] = []
var draw_failures: Array[String] = []
var _camera: Camera3D
var _stream: FileAccess
var _last_signature: String = ""


## Instantiates authored observation nodes and subscribes before the existing workload starts.
func _ready() -> void:
	var packed: PackedScene = load(CAMERA_SCENE) as PackedScene
	var view: Node3D = packed.instantiate() as Node3D
	add_child(view)
	_camera = view.get_node("Camera3D") as Camera3D
	_camera.make_current()
	_stream = FileAccess.open("user://draw.jsonl", FileAccess.WRITE)
	state = $View/Match as S05Match
	state.damage.exploded.connect(_observed_blast)
	RenderingServer.frame_post_draw.connect(_post_draw)
	super._ready()
	_write("ready", {"pid": OS.get_process_id(),
		"project": ProjectSettings.globalize_path("res://"),
		"engine": Engine.get_version_info(), "camera_scene": view.scene_file_path})


## Lets real local physics expire the last live effect before the existing client completion.
func _remote_fire_cases() -> void:
	await super._remote_fire_cases()
	var presentation: S05SavedPresentation = state.effects as S05SavedPresentation
	var initial_tick: int = presentation.cosmetic_tick
	_write("expiry_wait", { "presentation": presentation.receipt() })
	while presentation.visible_count() > 0 and (
			presentation.cosmetic_tick - initial_tick <= MAX_EXPIRY_WAIT_TICKS):
		await get_tree().physics_frame  # gdstyle:ignore=quality/await-in-loop

	_check(presentation.visible_count() == 0, "natural local physics expiry observed")
	_write("expiry", {"presentation": presentation.receipt(),
		"wait_ticks": presentation.cosmetic_tick - initial_tick,
		"live": wire.live_received, "duplicates": wire.duplicate_live_rejected})
	# Permit a genuine automatic frame of expiry before the unchanged leave protocol.
	await get_tree().process_frame
	await get_tree().process_frame


## Binds each genuine host event to the already-consumed saved slot state.
func _observed_blast(event: Dictionary) -> void:
	observed_events.append(event.duplicate(true))
	_write("blast", { "event_id": event, "state": _snapshot() })


## Retains installed baseline state before admission without replaying historical events.
func _baseline(id: int) -> void:
	super._baseline(id)
	_write("baseline_installed", {"baseline_id": id, "cut": state.damage.cut(),
		"presentation": (state.effects as S05SavedPresentation).receipt(),
		"input_enabled": state.rig.get_meta("input_enabled")})


## Captures only completed automatic render callbacks and reads the actual current camera.
func _post_draw() -> void:
	if draw_callbacks >= MAX_FRAME_RECEIPTS:
		if draw_failures.is_empty():
			draw_failures.append("automatic callback observation ceiling exhausted")

		return

	if not is_instance_valid(state):
		return

	var render_index: int = Engine.get_frames_drawn()
	if render_index <= previous_render_index:
		draw_failures.append("non-increasing rendered index")

	previous_render_index = render_index
	draw_callbacks += 1
	var receipt: Dictionary = _snapshot()
	receipt["callback"] = draw_callbacks
	receipt["render_index"] = render_index
	receipt["physics_index"] = Engine.get_physics_frames()
	receipt["monotonic_ms"] = Time.get_ticks_msec()
	var stage: String = _capture_stage(receipt)
	if not stage.is_empty() and draw_callbacks >= 3 and not capture_paths.has(stage):
		_capture(stage, receipt)

	# Cosmetic/damage ticks advance without meaningful presentation changes; keep stages sparse.
	var signature: String = JSON.stringify([receipt.presentation.active,
		receipt.presentation.visible, receipt.presentation.epoch, receipt.accepted,
		receipt.dropped, receipt.watermark, receipt.live, receipt.duplicates,
		receipt.revision, receipt.camera, receipt.can_draw, receipt.vsync_mode,
		receipt.viewport, receipt.window_size])
	if signature != _last_signature or draw_callbacks <= 3 or receipt.has("png"):
		_write("frame", receipt)
		_last_signature = signature


## Selects finite baseline, saturation, expiry and settled hydration states from real owners.
func _capture_stage(receipt: Dictionary) -> String:
	if role == "late" and baseline_count > 0 and receipt.presentation.visible == 0:
		return "hydrated"

	if receipt.presentation.visible == 8 and receipt.dropped == 4:
		return "burst"

	if receipt.accepted == 8 and receipt.presentation.visible == 0 and receipt.settled:
		return "expired"

	if receipt.accepted == 0 and not state.session_id.is_empty():
		return "baseline"

	return ""


## Binds viewport pixels, dimensions and save status to this exact automatic callback.
func _capture(stage: String, receipt: Dictionary) -> void:
	var image: Image = get_viewport().get_texture().get_image()
	var path: String = "user://" + stage + ".png"
	var error: Error = image.save_png(path)
	capture_paths[stage] = path
	receipt["cut"] = state.damage.cut()
	receipt["png"] = {"stage": stage, "path": ProjectSettings.globalize_path(path),
		"width": image.get_width(), "height": image.get_height(), "save_error": error,
		"sha256": FileAccess.get_sha256(path) if error == OK else ""}
	if error != OK:
		draw_failures.append("PNG save failed: " + stage)


## Reads gameplay, cosmetic and source-linked node state without advancing any owner.
func _snapshot() -> Dictionary:
	var presentation: S05SavedPresentation = state.effects as S05SavedPresentation
	var viewport: Viewport = get_viewport()
	var current: Camera3D = viewport.get_camera_3d()
	var slots: Array[Dictionary] = []
	for slot: Node3D in $View/Match/Presentation/Slots.get_children():
		var model: Node3D = slot.get_node("Visuals/Model") as Node3D
		var car_id: int = 0
		for index: int in state.damage.rows.size():
			var body: S05Car = state.damage.bodies[index]
			if slot.visible and body.global_position.is_equal_approx(slot.global_position):
				car_id = state.damage.rows[index].id

		slots.append({"path": str(slot.get_path()), "scene": slot.scene_file_path,
			"model_scene": model.scene_file_path, "model_transform": str(model.transform),
			"visible": slot.visible, "visible_in_tree": slot.is_visible_in_tree(),
			"position": [slot.global_position.x, slot.global_position.y, slot.global_position.z],
			"car": car_id,
			"mesh_nodes": model.find_children("*", "MeshInstance3D", true, false).size()})

	var camera: Dictionary = { "path": "", "expected_current": current == _camera }
	if current != null:
		camera.merge({"path": str(current.get_path()), "transform": str(current.global_transform),
			"position": [current.global_position.x, current.global_position.y,
				current.global_position.z],
			"projection": current.projection, "fov": current.fov,
			"near": current.near, "far": current.far, "current": current.current}, true)

	return {"presentation": presentation.receipt(), "slots": slots, "camera": camera,
		"viewport": [viewport.get_visible_rect().size.x, viewport.get_visible_rect().size.y],
		"requested_project_size": [
			ProjectSettings.get_setting("display/window/size/viewport_width"),
			ProjectSettings.get_setting("display/window/size/viewport_height")],
		"vsync_mode": DisplayServer.window_get_vsync_mode(),
		"vsync_disabled": DisplayServer.window_get_vsync_mode() == DisplayServer.VSYNC_DISABLED,
		"can_any_window_draw": null,
		"can_any_window_draw_reason": "internal native method unavailable to GDScript",
		"session": state.session_id, "match_revision": state.damage.cut().match,
		"display": DisplayServer.get_name(), "can_draw": DisplayServer.window_can_draw(),
		"focus": DisplayServer.window_is_focused(), "mode": DisplayServer.window_get_mode(),
		"window_size": [DisplayServer.window_get_size().x, DisplayServer.window_get_size().y],
		"accepted": presentation.accepted, "dropped": presentation.dropped,
		"watermark": presentation.watermark, "damage_tick": state.damage.tick,
		"damage": state.damage.damage_outcomes, "visits": state.damage.total_visits,
		"settled": _settled(),
		"revision": state.damage.revision, "live": wire.live_received if wire != null else 0,
		"duplicates": wire.duplicate_live_rejected if wire != null else 0}


## Preserves complete observation rows separately from the original production proof stream.
func _write(kind: String, values: Dictionary) -> void:
	values["kind"] = kind
	values["role"] = role
	if _stream != null:
		_stream.store_line(JSON.stringify(values))
		_stream.flush()


## Reports the separate automatic-image result before the unchanged teardown result and quit.
func _result() -> void:
	_write("result", {"callbacks": draw_callbacks, "captures": capture_paths,
		"render_failures": draw_failures, "host_events": observed_events,
		"fixture_failures": failures, "user": OS.get_user_data_dir()})
	if _stream != null:
		_stream.close()
		_stream = null

	super._result()
