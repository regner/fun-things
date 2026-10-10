extends SceneTree
## Check source-linked barrier bounds, saved identities and production capsule movement.

const ASSET := "city_barriers_03"
const PREFAB := "res://scenes/prefabs/environment/city_barriers_03.tscn"
const FIXTURE := "res://tools/asset_production/city_barriers_03/check_scene.tscn"
const EVIDENCE := "res://docs/assets/production/city_barriers_03-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-1.2, 0, -.275), Vector3(2.4, .6, .55))
const WALK_TICKS := 48

var _failed := false
var _report: Dictionary = { "resource_uids": {} }


## Wait for the tree before loading scenes or running physics checks.
func _initialize() -> void:
	_run.call_deferred()


## Roundtrip saved scenes and run physical checks in standalone headless mode.
func _run() -> void:
	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if "--normalize" in OS.get_cmdline_user_args():
		for path: String in [PREFAB, FIXTURE]:
			_save_scene(path)
			var first_hash: String = FileAccess.get_sha256(path)
			_save_scene(path)
			_require(first_hash == FileAccess.get_sha256(path), "Save/reload drift")
		_report["save_reload_byte_stable"] = true

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
	print("CITY_BARRIERS_03_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Keep failed assertions visible in logs and in the process exit status.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Preserve imported ancestry while packing and resaving authored wrappers.
func _save_scene(path: String) -> void:
	var uid: int = ResourceLoader.get_resource_uid(path)
	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()
		ResourceUID.add_id(uid, path)

	var source: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE,
	)
	var instance: Node = source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_require(packed.pack(instance) == OK, "Pack failed")
	_require(ResourceSaver.save(packed, path) == OK, "Save failed")
	_require(ResourceSaver.set_uid(path, uid) == OK, "Scene UID save failed")
	instance.free()


## Recursively prove each saved resource and dependency UID resolves.
func _check_dependencies(path: String) -> void:
	_require(ResourceLoader.load(path) != null, "Missing resource: " + path)
	var resource_uid: int = ResourceLoader.get_resource_uid(path)
	_require(resource_uid != ResourceUID.INVALID_ID, "Resource has no UID: " + path)
	_require(ResourceUID.has_id(resource_uid), "Unregistered resource UID: " + path)
	_require(ResourceUID.get_id_path(resource_uid) == path, "Resource UID path mismatch: " + path)
	_report["resource_uids"][path] = ResourceUID.id_to_text(resource_uid)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		var child: String = parts[-1]
		if parts[0].begins_with("uid://"):
			var uid: int = ResourceUID.text_to_id(parts[0])
			_require(ResourceUID.has_id(uid), "Missing UID: " + dependency)
			_require(ResourceUID.get_id_path(uid) == child, "UID mismatch: " + dependency)
		_check_dependencies(child)


## Verify actual imported mesh bounds, surfaces and the one simple static envelope.
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
	_require(mesh.mesh.get_surface_count() == 3, "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparency")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	_check_collision(instance)
	_report["bounds_min_m"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size_m"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	instance.free()


## Confirm the saved collider is separate from imported decorative geometry.
func _check_collision(instance: Node3D) -> void:
	var bodies: Array[Node] = instance.find_children("*", "CollisionObject3D", true, false)
	_require(bodies.size() == 1, "Expected one static body")
	var body: StaticBody3D = instance.get_node("Collision/BarrierBody")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Static-world filtering")
	var shapes: Array[Node] = body.find_children("*", "CollisionShape3D", true, false)
	_require(shapes.size() == 1, "Expected one shape")
	var shape_node: CollisionShape3D = shapes[0] as CollisionShape3D
	var box: BoxShape3D = shape_node.shape as BoxShape3D
	_require(box != null, "Expected box")
	_require(box.size.is_equal_approx(Vector3(2.4, .6, .55)), "Collision envelope")
	_require(shape_node.position.is_equal_approx(Vector3(0, .3, 0)), "Collision datum")
	_report["static_box"] = { "size_m": [2.4, .6, .55], "layer": 1, "mask": 0 }


## Check a low ray hit, clear above-cap ray and authority/replay contact and bypass.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	var low_ray := PhysicsRayQueryParameters3D.create(Vector3(0, .5, -2), Vector3(0, .5, 2), 1)
	var low_hit: Dictionary = space.intersect_ray(low_ray)
	_require(not low_hit.is_empty(), "Ray passed through barrier")
	if not low_hit.is_empty():
		_require(low_hit["collider"] == fixture.get_node("Barrier/Collision/BarrierBody"),
			"Ray hit the wrong body")

	var high_ray := PhysicsRayQueryParameters3D.create(Vector3(0, .7, -2), Vector3(0, .7, 2), 1)
	_require(space.intersect_ray(high_ray).is_empty(), "Collider extends above cap")
	var contact: Array[Vector3] = []
	var bypass: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [
		ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY,
	]:
		contact.append(await _walk(fixture.get_node("Actor"), 0, mode))
		bypass.append(await _walk(fixture.get_node("Actor"), 1.8, mode))

	_require(contact[0].distance_to(Vector3(0, 0, -.625)) < .015, "Wrong actor contact stop")
	_require(bypass[0].distance_to(Vector3(1.8, 0, 2)) < .015, "Clear bypass failed")
	_require(contact[0].is_equal_approx(contact[1]), "Authority/replay contact mismatch")
	_require(bypass[0].is_equal_approx(bypass[1]), "Authority/replay bypass mismatch")
	_report["physics"] = {
		"low_ray_blocked": true, "above_cap_ray_clear": true,
		"actor_capsule_radius_m": .35, "actor_capsule_height_m": 1.8,
		"ticks_per_case_per_mode": WALK_TICKS, "authority_replay_equal": true,
		"contact_stop_m": [contact[0].x, contact[0].y, contact[0].z],
		"bypass_end_m": [bypass[0].x, bypass[0].y, bypass[0].z],
		"vehicle_network_transport_and_placement": "not tested",
	}
	fixture.free()


## Walk the production ActorMotion capsule over the saved collision-only test floor.
func _walk(actor: ActorMotion, x: float, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = Vector3(x, .001, -2)
	actor.neutralize()
	actor.apply_floor_snap()
	for tick: int in WALK_TICKS:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, Vector2(0, 1), 0.0, false, false,
		)
		_require(actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step rejected")

	return actor.position
