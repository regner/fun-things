extends SceneTree
## Validate the linked shop-home, saved identities and production actor contact.

const ASSET := "d05_quay_frontages_01"
const PREFAB := "res://scenes/prefabs/environment/d05_quay_frontages_01.tscn"
const FIXTURE := "res://tools/asset_production/d05_quay_frontages_01/collision_check.tscn"
const EVIDENCE := "res://docs/assets/production/d05_quay_frontages_01-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-3.48, 0, -5.31), Vector3(6.96, 9.35, 10.62))
const MOVEMENT_TICKS := 60

var _failed := false
var _report: Dictionary = { "resource_uids": {} }


## Start after the scene tree exists and imports can be loaded.
func _initialize() -> void:
	_run.call_deferred()


## Normalize owned scenes only, then run imported-resource and native physics checks.
func _run() -> void:
	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if "--normalize" in OS.get_cmdline_user_args():
		for path: String in [PREFAB, FIXTURE]:
			_save_scene(path)
			var first_hash: String = FileAccess.get_sha256(path)
			_save_scene(path)
			_require(first_hash == FileAccess.get_sha256(path), "Save/reload drift")
		_report["save_reload_byte_stable"] = true
		_report["roundtrip_scenes"] = [PREFAB, FIXTURE]

	_check_dependencies(PREFAB)
	_check_dependencies(FIXTURE)
	_check_model()
	_require(_report.has("linked_model_identity"), "Model checks did not complete")
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
	print("D05_QUAY_FRONTAGES_01_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Preserve a nonzero exit for any contract violation across helper returns.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Roundtrip packed scenes without flattening the imported instance.
func _save_scene(path: String) -> void:
	var uid: int = ResourceLoader.get_resource_uid(path)
	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()
		ResourceUID.add_id(uid, path)

	var source: PackedScene = ResourceLoader.load(
		path,
		"PackedScene",
		ResourceLoader.CACHE_MODE_IGNORE,
	)
	var instance: Node = source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_require(packed.pack(instance) == OK, "Pack failed")
	_require(ResourceSaver.save(packed, path) == OK, "Save failed")
	_require(ResourceSaver.set_uid(path, uid) == OK, "Scene UID save failed")
	instance.free()


## Verify every dependency exists and UID references resolve to the declared path.
func _check_dependencies(path: String) -> void:
	_require(ResourceLoader.load(path) != null, "Missing resource: " + path)
	var resource_uid: int = ResourceLoader.get_resource_uid(path)
	_require(resource_uid != ResourceUID.INVALID_ID, "Resource has no UID: " + path)
	_require(ResourceUID.has_id(resource_uid), "Unregistered resource UID: " + path)
	_require(ResourceUID.get_id_path(resource_uid) == path, "UID path mismatch: " + path)
	_report["resource_uids"][path] = ResourceUID.id_to_text(resource_uid)
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
	_require(mesh.mesh.get_surface_count() == 5, "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(
			material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparent shop",
		)
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	var body: StaticBody3D = instance.get_node("Collision/Body")
	var collider: CollisionShape3D = body.get_node("Shell")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Collision layers")
	_require(collider.shape is BoxShape3D and not collider.disabled, "Shell box")
	_require(collider.position.is_equal_approx(Vector3(0, 3.425, 0)), "Collider datum")
	_require(collider.shape.size.is_equal_approx(Vector3(6.4, 6.85, 10)), "Solid envelope")
	_require(instance.find_children("*", "CollisionShape3D", true, false).size() == 1,
		"Exactly one collider; fittings are visual-only")
	_check_mounts(instance)
	_report["bounds_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	_check_fitted_bounds(instance)
	instance.free()


## Verify the overhang reservation includes all seven unchanged shared fitting instances.
func _check_fitted_bounds(instance: Node3D) -> void:
	var visual_bounds: Array[AABB] = []
	_collect_visual_bounds(instance, Transform3D.IDENTITY, visual_bounds)
	var fitted_bounds: AABB = visual_bounds[0]
	for part_bounds: AABB in visual_bounds:
		fitted_bounds = fitted_bounds.merge(part_bounds)

	_require(fitted_bounds.position.distance_to(Vector3(-3.48, 0, -6.1)) < .001,
		"Fitted envelope minimum")
	_require(fitted_bounds.size.distance_to(Vector3(6.96, 9.35, 11.41)) < .001,
		"Fitted envelope size")
	_report["fitted_bounds_min"] = _vector_to_array(fitted_bounds.position)
	_report["fitted_bounds_size"] = _vector_to_array(fitted_bounds.size)
	_report["fitted_mesh_count"] = visual_bounds.size()


## Measure the complete fitted envelope through imported transforms without adding tree state.
func _collect_visual_bounds(
	node: Node3D,
	parent_transform: Transform3D,
	bounds: Array[AABB],
) -> void:
	var combined: Transform3D = parent_transform * node.transform
	if node is MeshInstance3D:
		bounds.append(combined * node.mesh.get_aabb())

	for child: Node in node.get_children():
		if child is Node3D:
			_collect_visual_bounds(child, combined, bounds)


## Verify saved shared instances without geometry duplication or corrective scaling.
func _check_mounts(instance: Node3D) -> void:
	var mounts: Dictionary = {
		"Canopy": Vector3(-.95, 3, -5), "Fascia": Vector3(-.95, 3.8, -5),
		"Surround": Vector3(1.95, 0, -5), "Display": Vector3(-.95, .48, -5),
		"ClosedDoor": Vector3(1.95, 0, -5), "UpperFront": Vector3(0, 4.65, -5),
		"UpperRear": Vector3(0, 4.65, 5),
	}
	for name: String in mounts:
		var fitting: Node3D = instance.get_node("Fittings/" + name)
		_require(fitting.position.is_equal_approx(mounts[name]), "Mount: " + name)
		var expected_basis := Basis.IDENTITY
		if name == "UpperRear":
			expected_basis = Basis(Vector3.UP, PI)
		_require(fitting.basis.is_equal_approx(expected_basis), "Fitting basis: " + name)
		_require(not fitting.scene_file_path.is_empty(), "Unlinked fitting: " + name)
	_report["shared_mounts"] = mounts.size()


## Exercise the closed shell, clear side passage and overhead-only roof through physics APIs.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	for sign_value: float in [-1.0, 1.0]:
		var ray := PhysicsRayQueryParameters3D.create(
			Vector3(sign_value * 9, 1, 0), Vector3(0, 1, 0), 1,
		)
		var hit: Dictionary = space.intersect_ray(ray)
		_require(not hit.is_empty(), "Side wall ray")
		if not hit.is_empty():
			_require(hit["collider"] == fixture.get_node("Shop/Collision/Body"), "Ray body")
			_require(absf(hit["position"].x - sign_value * 3.2) < .002, "Side plane")

	var above := PhysicsRayQueryParameters3D.create(Vector3(0, 7, -9), Vector3(0, 7, 9), 1)
	_require(space.intersect_ray(above).is_empty(), "Overhead roof must remain visual-only")
	var bypass := PhysicsRayQueryParameters3D.create(Vector3(4, 1, -7), Vector3(4, 1, 7), 1)
	_require(space.intersect_ray(bypass).is_empty(), "Side route must remain clear")
	var actor: ActorMotion = fixture.get_node("Actor")
	var results: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		var cases: Array[Vector3] = await _movement_cases(  # gdstyle:ignore=quality/await-in-loop
			actor, mode,
		)
		results.append_array(cases)

	for index: int in 5:
		_require(results[index].distance_to(results[index + 5]) < .002,
			"Authority/replay differs beyond 2 mm: " + str(results))
	_report["physics"] = {
		"side_rays_hit": true, "roof_ray_clear": true, "outside_shell_ray_clear": true,
		"actor_capsule_radius_m": .35, "actor_capsule_height_m": 1.8,
		"movement_ticks_per_case_per_mode": MOVEMENT_TICKS,
		"authority_replay_within_2mm": true, "case_order": [
			"right_wall", "left_wall", "closed_front", "rear", "clear_side_bypass",
		],
		"all_case_positions": results.map(_vector_to_array),
		"car_and_network_transport": "pending downstream; not exercised by these actor checks",
	}
	fixture.free()


## Encode measured positions without stringifying vectors in the JSON evidence.
func _vector_to_array(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]


## Assert literal expected contacts through production movement, not visual-mesh collision.
func _movement_cases(actor: ActorMotion, mode: ActorMotion.StepMode) -> Array[Vector3]:
	var right: Vector3 = await _move_actor(actor, Vector3(5, 0, 0), Vector2(-1, 0), mode)
	_require(absf(right.x - 3.55) < .003, "Right wall contact")
	var left: Vector3 = await _move_actor(actor, Vector3(-5, 0, 0), Vector2(1, 0), mode)
	_require(absf(left.x + 3.55) < .003, "Left wall contact")
	var front: Vector3 = await _move_actor(actor, Vector3(1.95, 0, -7), Vector2(0, 1), mode)
	_require(absf(front.z + 5.35) < .003, "Closed frontage contact")
	var rear: Vector3 = await _move_actor(actor, Vector3(0, 0, 7), Vector2(0, -1), mode)
	_require(absf(rear.z - 5.35) < .003, "Rear contact")
	var bypass: Vector3 = await _move_actor(actor, Vector3(4, 0, -2), Vector2(0, 1), mode)
	_require(bypass.distance_to(Vector3(4, 0, 3)) < .003, "Invisible side blocker")
	return [right, left, front, rear, bypass]


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
