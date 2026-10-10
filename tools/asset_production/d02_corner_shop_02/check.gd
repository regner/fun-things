extends SceneTree
## Validate the linked annex, saved attachment fixture and production actor contacts.

const ASSET := "d02_corner_shop_02"
const PREFAB := "res://scenes/prefabs/environment/d02_corner_shop_02.tscn"
const FIXTURE := "res://tools/asset_production/d02_corner_shop_02/collision_check.tscn"
const EVIDENCE := "res://docs/assets/production/d02_corner_shop_02-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-2.35, 0, -1.8), Vector3(4.7, 3.39, 3.815))
const MOVEMENT_TICKS := 60
const EDITOR_STARTUP_FRAMES := 10
const BOX_CONTACT_SKIN_M := .02

var _failed := false
var _report: Dictionary = {}


## Start after the scene tree exists and imports can be loaded.
func _initialize() -> void:
	_run.call_deferred()


## Normalize owned scenes only, then run imported-resource and native physics checks.
func _run() -> void:
	if Engine.is_editor_hint():
		for frame: int in EDITOR_STARTUP_FRAMES:
			await process_frame  # gdstyle:ignore=quality/await-in-loop
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame  # gdstyle:ignore=quality/await-in-loop

	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if "--normalize" in OS.get_cmdline_user_args():
		for path: String in [PREFAB, FIXTURE]:
			_save_scene(path)
			var first_hash: String = FileAccess.get_sha256(path)
			_save_scene(path)
			_require(first_hash == FileAccess.get_sha256(path), "Save/reload drift")
		_report["save_reload_byte_stable"] = true

	_check_dependencies(PREFAB)
	_check_model()
	_require(_report.has("linked_model_identity"), "Model checks did not complete")
	# Non-tool ActorMotion methods are intentionally unavailable in the editor process.
	if not Engine.is_editor_hint():
		await _check_physics()
		_require(_report.has("physics"), "Physics checks did not complete")
	if _failed:
		quit(1)
		return

	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(EVIDENCE))
	if data.has("godot") and not _report.has("save_reload_byte_stable"):
		_report["save_reload_byte_stable"] = data["godot"].get("save_reload_byte_stable", false)
	_report["engine"] = Engine.get_version_info()["string"]
	data["godot"] = _report
	var file: FileAccess = FileAccess.open(EVIDENCE, FileAccess.WRITE)
	file.store_string(JSON.stringify(data, "\t") + "\n")
	file.close()
	print("D02_CORNER_SHOP_02_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Preserve a nonzero exit for any contract violation across helper returns.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Roundtrip packed scenes without flattening the imported instance.
func _save_scene(path: String) -> void:
	var source: PackedScene = ResourceLoader.load(
		path,
		"PackedScene",
		ResourceLoader.CACHE_MODE_IGNORE,
	)
	var instance: Node = source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_require(packed.pack(instance) == OK, "Pack failed")
	_require(ResourceSaver.save(packed, path) == OK, "Save failed")
	instance.free()


## Verify every dependency exists and UID references resolve to the declared path.
func _check_dependencies(path: String) -> void:
	_require(ResourceLoader.load(path) != null, "Missing resource: " + path)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		var child: String = parts[-1]
		if parts[0].begins_with("uid://"):
			var uid: int = ResourceUID.text_to_id(parts[0])
			_require(ResourceUID.has_id(uid), "Missing UID: " + dependency)
			_require(ResourceUID.get_id_path(uid) == child, "UID mismatch: " + dependency)
		_check_dependencies(child)


## Measure the imported mesh and deliberate collision independently of authoring formulas.
func _check_model() -> void:
	var packed: PackedScene = load(PREFAB)
	var instance: Node3D = packed.instantiate()
	var model: Node3D = instance.get_node("Visuals/Model")
	_require(model.transform == Transform3D.IDENTITY, "Corrective model transform")
	_require(model.scene_file_path == "res://art/models/environment/%s/%s.glb" % [ASSET, ASSET],
		"Unlinked model")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_require(meshes.size() == 1, "Mesh count")
	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh.transform * mesh.mesh.get_aabb()
	_require(bounds.position.distance_to(EXPECTED_BOUNDS.position) < .001, "Bounds minimum")
	_require(bounds.size.distance_to(EXPECTED_BOUNDS.size) < .001, "Bounds size")
	_require(mesh.mesh.get_surface_count() == 6, "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(
			material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparent shop",
		)
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	var body: StaticBody3D = instance.get_node("Collision/Body")
	var collider: CollisionShape3D = body.get_node("Envelope")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Collision layers")
	_require(collider.shape is BoxShape3D and not collider.disabled, "Annex box shape")
	_require(collider.position == Vector3(0, 1.4, 0), "Collider datum")
	_require(collider.shape.size == Vector3(4.4, 2.8, 3.6), "Solid footprint envelope")
	_require(instance.find_children("*", "CollisionShape3D", true, false).size() == 1,
		"Exactly one annex collider")
	_report["bounds_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	instance.free()


## Probe both wall planes beside the joint and an unobstructed overhead route.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var annex: Node3D = fixture.get_node("Annex")
	_require(annex.position.is_equal_approx(Vector3(0, 0, 6.3)), "Attachment translation")
	_require(annex.basis == Basis.IDENTITY, "Attachment basis")
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	_check_joint_rays(space)
	var actor: ActorMotion = fixture.get_node("Actor")
	var results: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		var cases: Array[Vector3] = await _movement_cases(  # gdstyle:ignore=quality/await-in-loop
			actor, mode,
		)
		results.append_array(cases)

	for index: int in 6:
		_require(results[index].distance_to(results[index + 6]) < .002,
			"Authority/replay differs beyond 2 mm: " + str(results))
	_report["physics"] = {
		"joint_and_side_rays_hit": true, "roof_ray_clear": true,
		"attachment_root_godot_m": [0, 0, 6.3],
		"actor_capsule_radius_m": .35, "actor_capsule_height_m": 1.8,
		"movement_ticks_per_case_per_mode": MOVEMENT_TICKS,
		"authority_replay_within_2mm": true, "case_order": [
			"attached_right", "attached_left", "standalone_front", "attached_rear",
			"right_joint_bypass", "left_joint_bypass",
		],
		"all_case_positions": results.map(_vector_to_array),
		"car_and_network_transport": "pending downstream; not exercised by these actor checks",
	}
	fixture.free()


## Keep attachment-plane probes distinct from simulation contact cases.
func _check_joint_rays(space: PhysicsDirectSpaceState3D) -> void:
	for sign_value: float in [-1.0, 1.0]:
		for depth: float in [4.49, 4.5, 4.51, 6.3, 8.09]:
			_check_wall_ray(space, sign_value, depth)

	var front_ray := PhysicsRayQueryParameters3D.create(Vector3(12, 1, -4), Vector3(12, 1, 0), 1)
	var front_hit: Dictionary = space.intersect_ray(front_ray)
	_require(not front_hit.is_empty(), "Standalone front ray missed")
	if not front_hit.is_empty():
		_require(absf(front_hit["position"].z + 1.8) < .001, "Standalone front plane")

	var above := PhysicsRayQueryParameters3D.create(Vector3(12, 3.5, -4), Vector3(12, 3.5, 4), 1)
	_require(space.intersect_ray(above).is_empty(), "Overhead roof must remain visual-only")


## Verify the true side plane on either side of the coplanar building joint.
func _check_wall_ray(space: PhysicsDirectSpaceState3D, side: float, depth: float) -> void:
	var ray := PhysicsRayQueryParameters3D.create(
		Vector3(side * 5, 1, depth), Vector3(0, 1, depth), 1,
	)
	var hit: Dictionary = space.intersect_ray(ray)
	_require(not hit.is_empty(), "Joint/wall ray must not find a gap")
	if hit.is_empty() or depth == 4.5:
		# At the coplanar joint either closed body's surface may win.
		return

	var expected_x: float = 2.40444 if depth < 4.5 else 2.2
	_require(absf(hit["position"].x - side * expected_x) < .002, "Wall plane mismatch")


## Encode measured positions without stringifying vectors in the JSON evidence.
func _vector_to_array(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]


## Assert literal contact and bypass positions independently of authored shape coordinates.
func _movement_cases(actor: ActorMotion, mode: ActorMotion.StepMode) -> Array[Vector3]:
	var right: Vector3 = await _move_actor(actor, Vector3(5, 0, 6.3), Vector2(-1, 0), mode)
	_require(absf(right.x - 2.55) < .003, "Right contact: " + str(right))
	var left: Vector3 = await _move_actor(actor, Vector3(-5, 0, 6.3), Vector2(1, 0), mode)
	_require(absf(left.x + 2.55) < .003, "Left contact: " + str(left))
	var front: Vector3 = await _move_actor(actor, Vector3(12, 0, -4), Vector2(0, 1), mode)
	# Box contacts can retain a small conservative skin in the pinned physics backend.
	_require(front.z <= -2.149 and front.z >= -2.15 - BOX_CONTACT_SKIN_M,
		"Standalone front contact: " + str(front))
	var rear: Vector3 = await _move_actor(actor, Vector3(0, 0, 11), Vector2(0, -1), mode)
	_require(absf(rear.z - 8.45) < .003, "Attached rear contact")
	var right_bypass: Vector3 = await _move_actor(actor, Vector3(2.8, 0, 4.5), Vector2(0, 1), mode)
	_require(right_bypass.distance_to(Vector3(2.8, 0, 9.5)) < .003, "Right joint route snag")
	var left_bypass: Vector3 = await _move_actor(actor, Vector3(-2.8, 0, 4.5), Vector2(0, 1), mode)
	_require(left_bypass.distance_to(Vector3(-2.8, 0, 9.5)) < .003, "Left joint route snag")
	return [right, left, front, rear, right_bypass, left_bypass]


## Replay one fixed-duration movement case through the production command and simulation APIs.
func _move_actor(
	actor: ActorMotion, start: Vector3, direction: Vector2, mode: ActorMotion.StepMode,
) -> Vector3:
	actor.position = start
	actor.neutralize()
	for tick: int in MOVEMENT_TICKS:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, direction, 0.0, false, false
		)
		_require(
			actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step rejected",
		)
	return actor.position
