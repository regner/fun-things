class_name DockThumperCaptureCheck
extends SceneTree
## Verifies saved linked visual contracts and optionally captures authored cameras.

const PREVIEW_PATH: String = "res://tests/fixtures/rocket_launcher/preview.tscn"
const EVIDENCE_PATH: String = "res://docs/assets/rocket_launcher_evidence/"
const TOLERANCE_METRES: float = 0.001
const CAPTURE_SETTLE_FRAMES: int = 6

var _report: Dictionary = {}


## Starts the bounded inspection after the engine has created its root viewport.
func _initialize() -> void:
	_run.call_deferred()


## Loads the saved composition and runs bounded contract and presentation checks.
func _run() -> void:
	root.size = Vector2i(1280, 800)
	var packed: PackedScene = load(PREVIEW_PATH)
	assert(packed != null)
	var preview: Node3D = packed.instantiate()
	root.add_child(preview)
	await process_frame
	await process_frame
	_check_assets(preview)
	_check_camera(preview)

	if "--capture" in OS.get_cmdline_user_args():
		assert(DisplayServer.get_name() != "headless")
		await _capture_view(preview.get_node("GameCamera"), "game_camera")
		await _capture_view(preview.get_node("DetailCamera"), "detail_camera")
		await _capture_view(preview.get_node("RocketCamera"), "rocket_camera")

	var output: FileAccess = FileAccess.open(
		EVIDENCE_PATH + "imported_checks.json", FileAccess.WRITE
	)
	assert(output != null)
	output.store_string(JSON.stringify(_report, "\t") + "\n")
	print("DOCK_THUMPER_CHECKS_PASS ", JSON.stringify(_report))
	preview.queue_free()
	await process_frame
	quit()


## Verifies source-linked visuals, contact sockets and independently bounded dimensions.
func _check_assets(preview: Node3D) -> void:
	var launcher: Node3D = preview.get_node("Samples/North")
	var rocket: Node3D = preview.get_node("Samples/Rocket")
	_check_visual(launcher)
	_check_visual(rocket)
	_check_socket(launcher, "WeaponMount", "socket_grip", Vector3.ZERO)
	_check_socket(launcher, "Muzzle", "socket_muzzle", Vector3(0, 0.30, -0.905))
	_check_socket(launcher, "SupportHand", "socket_support_hand", Vector3(0, -0.0825, -0.43))
	_check_socket(launcher, "Shoulder", "socket_shoulder", Vector3(0, 0.085, 0.28))
	_check_socket(rocket, "Trail", "socket_trail", Vector3(0, 0, 0.23))
	var launcher_bounds: AABB = _bounds(launcher)
	var rocket_bounds: AABB = _bounds(rocket)
	assert(launcher_bounds.size.x > 0.39 and launcher_bounds.size.x < 0.42)
	assert(absf(launcher_bounds.size.z - 1.43) < TOLERANCE_METRES)
	assert(absf(rocket_bounds.size.z - 0.45) < TOLERANCE_METRES)
	assert(rocket_bounds.size.x > 0.16 and rocket_bounds.size.x < 0.25)
	_report["launcher_bounds"] = {
		"position": str(launcher_bounds.position), "size": str(launcher_bounds.size),
	}
	_report["rocket_bounds"] = {
		"position": str(rocket_bounds.position), "size": str(rocket_bounds.size),
	}


## Records the exact renderer and verifies the authored native gameplay camera.
func _check_camera(preview: Node3D) -> void:
	var camera: Camera3D = preview.get_node("GameCamera")
	assert(camera.projection == Camera3D.PROJECTION_PERSPECTIVE)
	assert(is_equal_approx(camera.position.y, 47.0))
	assert(is_equal_approx(camera.fov, 42.0))
	assert((-camera.global_basis.z).is_equal_approx(Vector3.DOWN))
	assert(camera.global_basis.x.is_equal_approx(Vector3.RIGHT))
	_report["engine"] = Engine.get_version_info().string
	_report["display"] = DisplayServer.get_name()
	_report["renderer"] = RenderingServer.get_current_rendering_method()
	_report["adapter"] = RenderingServer.get_video_adapter_name()
	_report["camera"] = {
		"height_m": 47, "fov_degrees": 42, "viewport": str(root.size),
		"near_m": camera.near, "far_m": camera.far,
	}
	_report["launcher_projected_rect"] = str(
		_projected_bounds(camera, preview.get_node("Samples/North"))
	)
	_report["rocket_projected_rect"] = str(
		_projected_bounds(camera, preview.get_node("Samples/Rocket"))
	)


## Lets each saved camera settle before capturing its actual rendered viewport.
func _capture_view(camera: Camera3D, filename: String) -> void:
	camera.make_current()
	# This finite frame wait is intentional: capture follows completed presentation.
	for frame: int in range(CAPTURE_SETTLE_FRAMES):
		await process_frame  # gdstyle:ignore=quality/await-in-loop

	await RenderingServer.frame_post_draw
	var image: Image = root.get_texture().get_image()
	assert(image.get_size() == Vector2i(1280, 800))
	assert(image.save_png(EVIDENCE_PATH + filename + ".png") == OK)


## Rejects detached imports, scaling compensation and any implicit gameplay collision.
func _check_visual(instance: Node3D) -> void:
	assert(instance.scale.is_equal_approx(Vector3.ONE))
	var model: Node3D = instance.get_node("Visuals/Model")
	assert(model.transform.is_equal_approx(Transform3D.IDENTITY))
	assert(model.scene_file_path.begins_with("res://art/models/weapons/dock_thumper/"))
	assert(model.scene_file_path.ends_with(".glb"))
	for child: Node in instance.find_children("*", "CollisionObject3D", true, false):
		assert(child == null, "Cosmetic asset unexpectedly owns gameplay collision")


## Checks source-derived socket parity, fixed expected positions and the project frame.
func _check_socket(instance: Node3D, wrapper: String, source: String, expected: Vector3) -> void:
	var socket: Node3D = instance.get_node("Sockets/" + wrapper)
	var marker: Node3D = instance.get_node("Visuals/Model/" + source)
	assert(socket.transform.is_equal_approx(marker.transform))
	assert(socket.position.distance_to(expected) < TOLERANCE_METRES)
	assert(socket.basis.is_equal_approx(Basis.IDENTITY))
	_report[instance.name + "/" + wrapper] = {
		"position": str(socket.position), "basis": str(socket.basis),
	}


## Measures imported mesh bounds in the visual wrapper's local space.
func _bounds(instance: Node3D) -> AABB:
	var result: AABB
	var initialized: bool = false
	for child: Node in instance.find_children("*", "MeshInstance3D", true, false):
		var mesh: MeshInstance3D = child
		var relative: Transform3D = (
			instance.global_transform.affine_inverse() * mesh.global_transform
		)
		var bound: AABB = relative * mesh.get_aabb()
		result = result.merge(bound) if initialized else bound
		initialized = true

	assert(initialized)
	return result


## Measures the drawn-world geometry projection rather than a fabricated thumbnail.
func _projected_bounds(camera: Camera3D, instance: Node3D) -> Rect2:
	var bound: AABB = _bounds(instance)
	var result: Rect2
	for index: int in range(8):
		var world: Vector3 = instance.global_transform * bound.get_endpoint(index)
		var point: Vector2 = camera.unproject_position(world)
		result = Rect2(point, Vector2.ZERO) if index == 0 else result.expand(point)

	return result
