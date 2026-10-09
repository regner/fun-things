extends SceneTree
## Read-only asset acceptance probes plus native runtime captures of the saved preview.

const PREVIEW: String = "res://tests/fixtures/pedestrian_civilian/pedestrian_worker_a_preview.tscn"
const EVIDENCE: String = "res://docs/assets/pedestrian_worker_a-evidence/"

var _failures: Array[String] = []


## Defer loading until engine singletons and scene tree are ready.
func _initialize() -> void:
	_check.call_deferred()


## Exercise real scene/resource APIs without building any visible geometry or hierarchy.
func _check() -> void:
	Engine.max_fps = 60
	root.size = Vector2i(1280, 800)
	var scene: Node3D = load(PREVIEW).instantiate()
	root.add_child(scene)
	current_scene = scene
	await process_frame
	var worker: Node3D = scene.get_node("Workers/Idle")
	var model: Node3D = worker.get_node("PresentationAnchor/Visuals/Model")
	var skeleton: Skeleton3D = model.find_child("Skeleton3D", true, false)
	var mesh: MeshInstance3D = model.find_child("WorkerMesh", true, false)
	var rest_error: float = _check_skeleton_contract(skeleton)
	_check_mesh_and_palette(scene, worker, model, mesh)
	var clips: Dictionary = _check_animations(worker, skeleton)
	_set_review_poses(scene)
	await process_frame
	await process_frame
	_check_camera(scene)
	if DisplayServer.get_name() != "headless":
		await _capture_evidence(scene)
	_write_receipt(skeleton, rest_error, clips)
	quit(0 if _failures.is_empty() else 1)


## Verify the imported skeleton against the shared humanoid contract.
func _check_skeleton_contract(skeleton: Skeleton3D) -> float:
	_expect(skeleton != null and skeleton.get_bone_count() == 28, "28 canonical bones")
	var contract: Dictionary = JSON.parse_string(
		FileAccess.get_file_as_string(
			"res://art/source/models/characters/shared_humanoid/shared_humanoid_v1.json"
		)
	)
	var rest_error: float = 0.0
	for row: Dictionary in contract.bones:
		var bone: int = skeleton.find_bone(row.name)
		_expect(bone >= 0, "bone exists: " + row.name)
		var parent: int = skeleton.get_bone_parent(bone)
		var expected_parent: String = "" if row.parent == null else row.parent
		_expect(
			("" if parent < 0 else skeleton.get_bone_name(parent)) == expected_parent,
			"canonical parent: " + row.name,
		)
		var point: Array = row.head_blender_m
		var expected := Vector3(point[0], point[2], -point[1])
		rest_error = maxf(
			rest_error,
			skeleton.get_bone_global_rest(bone).origin.distance_to(expected),
		)
	_expect(rest_error < 0.00001, "rest origins agree within 1e-5 m")
	return rest_error


## Verify source-linked mesh sharing and per-instance palette behavior.
func _check_mesh_and_palette(
	scene: Node3D, worker: Node3D, model: Node3D, mesh: MeshInstance3D
) -> void:
	_expect(mesh.mesh.get_surface_count() == 1, "one palette surface")
	_expect(worker.scale == Vector3.ONE and model.scale == Vector3.ONE, "unit scene/model roots")
	var other: Node3D = scene.get_node("Workers/Walk")
	var other_model: Node3D = other.get_node("PresentationAnchor/Visuals/Model")
	var other_mesh: MeshInstance3D = other_model.find_child("WorkerMesh", true, false)
	_expect(mesh.mesh == other_mesh.mesh, "instances share imported mesh")
	_expect(
		mesh.material_override == other_mesh.material_override,
		"instances share palette material",
	)
	var other_color: Variant = other_mesh.get_instance_shader_parameter("jacket_color")
	var recolor: PackedColorArray = worker.palette.duplicate()
	recolor[1] = Color("72aaee")
	worker.set("palette", recolor)
	_expect(
		mesh.get_instance_shader_parameter("jacket_color") == recolor[1],
		"exported palette edits refresh live instance uniforms",
	)
	_expect(worker.apply_palette(recolor), "palette API accepts nine regions")
	_expect(
		other_mesh.get_instance_shader_parameter("jacket_color") == other_color,
		"one instance recolor preserves another instance",
	)
	recolor[1] = Color("eca23e")
	worker.apply_palette(recolor)
	_expect(not worker.apply_palette(PackedColorArray()), "invalid palette rejected")


## Verify retained clip policy, endpoints, death hold, and fixed roots.
func _check_animations(worker: Node3D, skeleton: Skeleton3D) -> Dictionary:
	var player: AnimationPlayer = worker.animation_player()
	var clips: Dictionary = {}
	for clip: String in ["idle", "walk", "run", "death"]:
		_expect(worker.play_clip(clip, 0), "public animation API: " + clip)
		var animation: Animation = player.get_animation("npc/" + clip)
		var expected_loop: int = (
			Animation.LOOP_NONE if clip == "death" else Animation.LOOP_LINEAR
		)
		_expect(animation.loop_mode == expected_loop, "loop policy: " + clip)
		player.seek(0, true)
		player.advance(0)
		var first: Array[Transform3D] = _poses(skeleton)
		player.seek(animation.length, true)
		player.advance(0)
		var last: Array[Transform3D] = _poses(skeleton)
		var endpoint_error: float = _pose_error(first, last)
		if clip != "death":
			_expect(endpoint_error < 0.0001, "seamless loop endpoint: " + clip)
		else:
			player.advance(3.0)
			_expect(_pose_error(last, _poses(skeleton)) < 0.0001, "death retains final pose")
		var root_pose: Transform3D = skeleton.get_bone_pose(skeleton.find_bone("root"))
		_expect(root_pose.is_equal_approx(Transform3D.IDENTITY), "fixed root: " + clip)
		clips[clip] = {
			"seconds": animation.length,
			"loop": animation.loop_mode,
			"endpoint_error": endpoint_error,
		}
	_expect(not worker.play_clip("weapon_fire"), "NPC library does not expose player weapon clips")
	return clips


## Set each review actor to the same retained still pose used by the captures.
func _set_review_poses(scene: Node3D) -> void:
	for actor: Node3D in scene.get_node("Workers").get_children():
		actor.play_clip(actor.initial_clip, 0)
		actor.animation_player().seek(1.6 if actor.initial_clip == "death" else .17, true)
		actor.animation_player().pause()


## Verify the approved top-down gameplay camera contract.
func _check_camera(scene: Node3D) -> void:
	var camera: Camera3D = scene.get_node("GameCamera")
	_expect(
		camera.position == Vector3(0, 47, 0) and is_equal_approx(camera.fov, 42),
		"actual game camera height/FOV",
	)
	_expect(
		camera.rotation_degrees.is_equal_approx(Vector3(-90, 0, 0)),
		"north-up vertical camera",
	)


## Capture the gameplay and overview cameras when a native display is available.
func _capture_evidence(scene: Node3D) -> void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(EVIDENCE + "game_camera.png")
	scene.get_node("OverviewCamera").make_current()
	scene.get_node("ReviewLabels/Context").text = (
		"OFF-SHIFT WORKER / ASSET OVERVIEW\n"
		+ "Idle · walk · run · death / three independent palettes\n"
		+ "Game-camera evidence is in game_camera.png"
	)
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(EVIDENCE + "overview.png")


## Write the unchanged machine-readable acceptance receipt.
func _write_receipt(
	skeleton: Skeleton3D, rest_error: float, clips: Dictionary
) -> void:
	var receipt: Dictionary = {
		"project": ProjectSettings.globalize_path("res://"),
		"engine": Engine.get_version_info().string,
		"display": DisplayServer.get_name(),
		"renderer": RenderingServer.get_current_rendering_method(),
		"resolution": root.size,
		"bones": skeleton.get_bone_count(),
		"rest_origin_error_m": rest_error,
		"clips": clips,
		"failures": _failures,
		"scope": "asset preview only; no gameplay/network/performance acceptance",
	}
	var file := FileAccess.open(EVIDENCE + "godot_checks.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	print("WORKER_CHECK " + JSON.stringify(receipt))


## Record independent contract expectations without hiding later checks after one failure.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Sample local pose channels from every imported bone.
func _poses(skeleton: Skeleton3D) -> Array[Transform3D]:
	var result: Array[Transform3D] = []
	for bone: int in skeleton.get_bone_count():
		result.append(skeleton.get_bone_pose(bone))
	return result


## Compare animation endpoints numerically, including rotation and translation.
func _pose_error(a: Array[Transform3D], b: Array[Transform3D]) -> float:
	var error: float = 0.0
	for index: int in a.size():
		error = maxf(error, a[index].origin.distance_to(b[index].origin))
		for axis: int in 3:
			error = maxf(error, a[index].basis[axis].distance_to(b[index].basis[axis]))
	return error
