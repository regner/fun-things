extends SceneTree
## Focused S01 resource/animation contracts; no gameplay or transport runner.

const FIXTURES: String = "res://tests/fixtures/s01/"
const PETROL: String = "res://art/materials/s01_petrol.tres"
const CORAL: String = "res://art/materials/s01_coral.tres"
const TOLERANCE: float = 0.0001
const CLIP_SECONDS: float = 31.0 / 30.0

var _failures: Array[String] = []


## Runs saved resources through engine APIs and returns a useful exit code.
func _initialize() -> void:
	_run.call_deferred()


## Checks imports, inherited placement and animation without authoring nodes.
func _run() -> void:
	var packed: PackedScene = load(FIXTURES + "roundtrip.tscn")
	if packed == null:
		push_error("S01: roundtrip failed to load")
		quit(1)
		return

	var scene: Node3D = packed.instantiate()
	root.add_child(scene)
	await process_frame
	_placement(scene)
	_static(scene)
	await _rig(scene.get_node("RigA"))
	_check(scene.get_node("RigA/Visuals/Model/Rig/Skeleton3D/Skin").mesh ==
		scene.get_node("RigB/Visuals/Model/Rig/Skeleton3D/Skin").mesh, "rig repeats share mesh")
	_dependencies(FIXTURES + "roundtrip.tscn", [])
	scene.queue_free()
	await process_frame
	for failure: String in _failures:
		push_error("S01: " + failure)
	print("S01_RESULT checks complete; failures=", _failures.size())
	quit(0 if _failures.is_empty() else 1)


## Checks distinct saved identities and placement independently of model data.
func _placement(scene: Node3D) -> void:
	var ids: Array[StringName] = []
	var positions: Dictionary = {
		"StaticA": Vector3(-3, 0, 0), "StaticB": Vector3.ZERO,
		"Variant": Vector3(3, 0, 0),
		"RigA": Vector3(-1.5, 0, 3), "RigB": Vector3(1.5, 0, 3),
	}
	for name: String in positions:
		var fixture: Node3D = scene.get_node(name)
		_check(fixture.position.is_equal_approx(positions[name]), name + " authored position")
		_check(fixture.scale.is_equal_approx(Vector3.ONE), name + " unit scale")
		var expected_id: StringName = StringName("s01/roundtrip/" + name.to_lower())
		_check(fixture.world_id == expected_id, name + " authored world_id")
		_check(not ids.has(fixture.world_id), name + " distinct world_id")
		ids.append(fixture.world_id)

	_check(scene.get_node("StaticB").rotation_degrees.is_equal_approx(Vector3(0, 90, 0)),
		"StaticB authored yaw")
	_check(scene.get_node("RigB").rotation_degrees.is_equal_approx(Vector3(0, -90, 0)),
		"RigB authored yaw")


## Checks static dimensions, ancestry, material overrides and deliberate collision.
func _static(scene: Node3D) -> void:
	var static_model: Node3D = scene.get_node("StaticA/Visuals/Model")
	_check(static_model.scene_file_path == "res://art/models/spikes/s01_static.glb",
		"static source link")
	_check(static_model.transform.is_equal_approx(Transform3D.IDENTITY), "static root pivot")
	var body: MeshInstance3D = static_model.get_node("Body")
	_bounds(body, Vector3(-1, -0.5, -0.5), Vector3(2, 1, 1))
	_bounds(static_model.get_node("Front"), Vector3(-0.35, -0.125, -0.125),
		Vector3(0.7, 0.25, 0.25))
	_bounds(static_model.get_node("Meter"), Vector3(-0.05, -0.5, -0.05), Vector3(0.1, 1, 0.1))
	_check(body.position.is_equal_approx(Vector3(0, 0.5, 0)), "ground centred body")
	_check(static_model.get_node("Front").position.z < -0.5, "front is -Z")
	_check(static_model.get_node("right_axis").position == Vector3.RIGHT, "+X right")
	_check(static_model.get_node("up_axis").position == Vector3.UP, "+Y up")
	var muzzle: Node3D = static_model.get_node("socket_muzzle")
	_check(muzzle.position.is_equal_approx(Vector3(0, 0.75, -0.75)), "static socket metres")
	_check(muzzle.basis.is_equal_approx(Basis.IDENTITY), "static socket -Z forward")
	_check(body.mesh.surface_get_material(0).resource_path == PETROL, "import material remap")
	var material: StandardMaterial3D = body.mesh.surface_get_material(0)
	_check(material.albedo_texture.resource_path == "res://art/textures/spikes/s01_palette.png",
		"external texture link")
	_check(material.albedo_texture.get_size() == Vector2(8, 8), "texture dimensions")
	_check(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "opaque material")
	_check(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS,
		"linear mipmapped material filter")
	_check(material.texture_repeat, "material UV repeat")
	var variant_body: MeshInstance3D = scene.get_node("Variant/Visuals/Model/Body")
	_check(variant_body.material_override.resource_path == CORAL, "inherited coral override")
	_check(body.material_override == null, "base material not overridden")
	_check(body.mesh == scene.get_node("StaticB/Visuals/Model/Body").mesh,
		"repeated instances share imported mesh")
	_check(body.mesh == variant_body.mesh, "variant shares imported mesh")
	var shape: CollisionShape3D = scene.get_node("StaticA/Collision/Body/Shape")
	_check(shape.shape.size == Vector3(2, 1, 1), "deliberate static collision envelope")
	_check(shape.position == Vector3(0, 0.5, 0), "collision ground datum")
	_check(scene.get_node("Variant/Collision/Body/Shape").shape == shape.shape,
		"variant inherits collision")


## Checks imported bounds and normalized normals against the measured brief.
func _bounds(mesh_node: MeshInstance3D, minimum: Vector3, size: Vector3) -> void:
	var bounds: AABB = mesh_node.get_aabb()
	_check(bounds.position.distance_to(minimum) < TOLERANCE, mesh_node.name + " AABB min")
	_check(bounds.size.distance_to(size) < TOLERANCE, mesh_node.name + " AABB size")
	var arrays: Array = mesh_node.mesh.surface_get_arrays(0)
	for normal: Vector3 in arrays[Mesh.ARRAY_NORMAL]:
		_check(absf(normal.length() - 1.0) < TOLERANCE, mesh_node.name + " normalized normals")


## Exercises bone attachment, loop seams, skin binds and final-pose retention.
func _rig(fixture: Node3D) -> void:
	var model: Node3D = fixture.get_node("Visuals/Model")
	_check(model.scene_file_path == "res://art/models/spikes/s01_rig.glb", "rig source link")
	_check(model.transform.is_equal_approx(Transform3D.IDENTITY), "rig ground pivot")
	var skeleton: Skeleton3D = model.get_node("Rig/Skeleton3D")
	_check(skeleton.get_bone_count() == 2, "two fixture bones")
	_check(skeleton.get_bone_name(0) == "root" and skeleton.get_bone_name(1) == "hand",
		"stable bone names")
	_check(skeleton.get_bone_parent(1) == 0, "hand parent")
	var skin: MeshInstance3D = skeleton.get_node("Skin")
	_check(skin.skin.get_bind_count() == 2, "two skin binds")
	_bounds(skin, Vector3(-0.375, 0, -0.2), Vector3(0.975, 1.6, 0.4))
	var attachment: BoneAttachment3D = skeleton.get_node("hand")
	_check(attachment.bone_name == "hand" and not attachment.override_pose, "hand attachment")
	var socket: Node3D = attachment.get_node("socket_grip")
	var rest_socket: Transform3D = model.global_transform.affine_inverse() * socket.global_transform
	_check(rest_socket.origin.distance_to(Vector3(0.5, 1.6, -0.15)) < TOLERANCE,
		"bone socket rest position")
	_check(rest_socket.basis.is_equal_approx(Basis.IDENTITY), "bone socket rest -Z forward")
	var player: AnimationPlayer = model.get_node("AnimationPlayer")
	player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	_clips(player, skeleton)
	player.play("run")
	player.seek(0.5, true)
	skeleton.force_update_all_bone_transforms()
	await process_frame
	var inverse: Transform3D = model.global_transform.affine_inverse()
	var moved_socket: Transform3D = inverse * socket.global_transform
	_check(moved_socket.origin.distance_to(rest_socket.origin) > 0.1, "socket follows animation")
	_check(fixture.position == Vector3(-1.5, 0, 3), "animation leaves placement unchanged")
	player.stop()


## Checks exact clip names, durations, loop seams and one-shot final pose.
func _clips(player: AnimationPlayer, skeleton: Skeleton3D) -> void:
	_check(player.get_animation_list() == PackedStringArray(["death", "idle", "run", "walk"]),
		"exact animation names")
	for clip: String in ["idle", "walk", "run", "death"]:
		var animation: Animation = player.get_animation(clip)
		_check(absf(animation.length - CLIP_SECONDS) < TOLERANCE, clip + " duration")
		var loop: int = Animation.LOOP_NONE if clip == "death" else Animation.LOOP_LINEAR
		_check(animation.loop_mode == loop, clip + " loop mode")
		player.play(clip)
		player.seek(0, true)
		skeleton.force_update_all_bone_transforms()
		var start: Quaternion = skeleton.get_bone_pose_rotation(1)
		player.seek(animation.length - TOLERANCE, true)
		skeleton.force_update_all_bone_transforms()
		var finish: Quaternion = skeleton.get_bone_pose_rotation(1)
		if clip != "death":
			_check(absf(start.dot(finish)) > 0.9999, clip + " seam matches")
		else:
			_check(absf(start.dot(finish)) < 0.9, "death changes pose")
			player.advance(0.5)
			_check(absf(finish.dot(skeleton.get_bone_pose_rotation(1))) > 0.9999,
				"death retains final pose")


## Recursively resolves dependencies and checks UID/path agreement, including fallbacks.
func _dependencies(path: String, visited: Array[String]) -> void:
	if visited.has(path):
		return

	visited.append(path)
	_check(ResourceLoader.exists(path), "resource exists: " + path)
	_check(ResourceLoader.load(path) != null, "resource loads: " + path)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		var fallback: String = parts[parts.size() - 1]
		if dependency.begins_with("uid://"):
			var identity: int = ResourceUID.text_to_id(parts[0])
			_check(ResourceUID.has_id(identity), "registered dependency UID: " + dependency)
			if ResourceUID.has_id(identity):
				_check(ResourceUID.get_id_path(identity) == fallback,
					"UID/path agree: " + dependency)
		_dependencies(fallback, visited)


## Accumulates failures so a single run reports all independently checked contracts.
func _check(condition: bool, contract: String) -> void:
	if not condition:
		_failures.append(contract)
