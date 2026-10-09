class_name VehiclePreviewCapture
extends Node3D
## Optional bounded capture for saved vehicle previews; no gameplay simulation.

const CAPTURE_SIZE: Vector2i = Vector2i(1280, 800)
const PREVIEW_FPS: int = 60


## Caps interactive preview and captures requested saved-camera states in bounded CLI runs.
func _ready() -> void:
	Engine.max_fps = PREVIEW_FPS
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	var capture_name: String = ""
	var inspection: bool = false
	var opened: bool = false
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--vehicle-capture="):
			capture_name = argument.trim_prefix("--vehicle-capture=")
		inspection = inspection or argument == "--inspection"
		opened = opened or argument == "--doors-open"

	if capture_name.is_empty():
		return

	get_window().size = CAPTURE_SIZE
	get_window().content_scale_size = CAPTURE_SIZE
	var animation: AnimationPlayer = get_node("AnimationPlayer")
	animation.play("mechanical_demo")
	animation.seek(2.5 if opened else 0.0, true)
	animation.pause()
	if inspection:
		get_node("InspectionCamera").make_current()
	else:
		get_node("GameCamera").make_current()

	for frame: int in range(5):
		await RenderingServer.frame_post_draw  # gdstyle:ignore=quality/await-in-loop

	var target: String = "user://screenshots/" + capture_name
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("user://screenshots"))
	var captured: Image = get_viewport().get_texture().get_image()
	var error: Error = captured.save_png(target + ".png")
	var report: Dictionary = _report(captured, target, opened, error)
	var file: FileAccess = FileAccess.open(target + ".json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	print("VEHICLE_CAPTURE ", JSON.stringify(report))
	get_tree().quit(0 if error == OK and report.motion_check else 1)


## Records actual rendered state and independently checks each hinge angle and fixed root.
func _report(captured: Image, target: String, opened: bool, error: Error) -> Dictionary:
	var camera: Camera3D = get_viewport().get_camera_3d()
	var car: Node3D = get_node("Car")
	var asset: String = str(car.get_meta("asset_id"))
	var model: Node3D = car.get_node("Visuals/Model/" + asset)
	var hinges: Dictionary = {}
	var motion_ok: bool = car.transform.is_equal_approx(Transform3D.IDENTITY)
	for hinge: Node3D in model.get_node("Doors").get_children():
		hinges[str(hinge.name)] = rad_to_deg(hinge.rotation.y)
		var expected_angle: float = 50.0 if opened else 0.0
		motion_ok = motion_ok and absf(absf(rad_to_deg(hinge.rotation.y)) - expected_angle) < 0.01

	var bounds: AABB = _bounds(model, Transform3D.IDENTITY)
	return {"capture": target + ".png", "save_error": error,
		"size": [captured.get_width(), captured.get_height()],
		"can_draw": DisplayServer.window_can_draw(), "motion_check": motion_ok,
		"hinge_degrees": hinges, "visual_bounds": str(bounds), "frames": Engine.get_frames_drawn(),
		"camera": str(camera.name), "camera_position": str(camera.position),
		"camera_rotation": str(camera.rotation), "fov": camera.fov,
		"doors_open": opened, "engine": Engine.get_version_info().string,
		"renderer": RenderingServer.get_current_rendering_method(),
		"max_fps": Engine.max_fps, "project": ProjectSettings.globalize_path("res://")}


## Measures the rendered pose using imported mesh bounds, including open doors.
func _bounds(node: Node, parent_pose: Transform3D) -> AABB:
	var pose: Transform3D = parent_pose
	if node is Node3D:
		pose = parent_pose * node.transform

	var result: AABB = AABB()
	if node is MeshInstance3D:
		result = pose * node.get_aabb()

	for child: Node in node.get_children():
		var child_bounds: AABB = _bounds(child, pose)
		if child_bounds.size != Vector3.ZERO:
			result = child_bounds if result.size == Vector3.ZERO else result.merge(child_bounds)

	return result
