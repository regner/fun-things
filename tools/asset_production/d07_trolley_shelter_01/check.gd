extends SceneTree
## Check source-linked short shelter bounds, saved identities and bounded physics queries.

const ASSET := "d07_trolley_shelter_01"
const PREFAB := "res://scenes/prefabs/environment/d07_trolley_shelter_01.tscn"
const EVIDENCE := "res://docs/assets/production/d07_trolley_shelter_01-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-1.45, 0, -1.8), Vector3(2.9, 3.11, 3.6))

var _failed := false
var _report: Dictionary = { "resource_uids": {} }


## Wait for the tree before loading scenes or running physics checks.
func _initialize() -> void:
	_run.call_deferred()


## Roundtrip saved scenes and run physical checks in standalone headless mode.
func _run() -> void:
	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if "--normalize" in OS.get_cmdline_user_args():
		for path: String in [PREFAB]:
			_save_scene(path)
			var first_hash: String = FileAccess.get_sha256(path)
			_save_scene(path)
			_require(first_hash == FileAccess.get_sha256(path), "Save/reload drift")
		_report["save_reload_byte_stable"] = true

	_check_dependencies(PREFAB)
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
	print("D07_TROLLEY_SHELTER_01_CHECK_PASS ", JSON.stringify(_report))
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


## Verify actual imported mesh bounds, surfaces and the minimal three-box static compound.
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


## Confirm the compound blocks side rails and uprights while leaving the front open.
func _check_collision(instance: Node3D) -> void:
	var bodies: Array[Node] = instance.find_children("*", "CollisionObject3D", true, false)
	_require(bodies.size() == 1, "Expected one static body")
	var body: StaticBody3D = instance.get_node("Collision/ShelterBody")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Static-world filtering")
	var shapes: Array[Node] = body.find_children("*", "CollisionShape3D", true, false)
	_require(shapes.size() == 3, "Expected three simple boxes")
	for shape_node: CollisionShape3D in shapes:
		var box: BoxShape3D = shape_node.shape as BoxShape3D
		_require(box != null, "Expected box")
		if shape_node.name == "RearStop":
			_require(box.size.is_equal_approx(Vector3(2.48, 1.16, .14)), "Rear size")
			_require(shape_node.position.is_equal_approx(Vector3(0, .58, 1.47)), "Rear datum")
		else:
			_require(box.size.is_equal_approx(Vector3(.22, 2.73, 3.18)), "Side size")
			var expected_x: float = -1.24 if shape_node.name == "LeftSide" else 1.24
			_require(shape_node.position.is_equal_approx(Vector3(expected_x, 1.365, 0)),
				"Side datum")

	_report["static_compound"] = {
		"box_count": 3, "layer": 1, "mask": 0,
		"entry_clear_width_m": 2.26, "roof_collision": false,
	}


## Check capsule fit, all barriers, open entry and roof-only visual clearance.
func _check_physics() -> void:
	var fixture: Node3D = load(PREFAB).instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	for side: float in [-1.0, 1.0]:
		var ray := PhysicsRayQueryParameters3D.create(
			Vector3(side * 3, .9, 0), Vector3(0, .9, 0), 1,
		)
		var hit: Dictionary = space.intersect_ray(ray)
		_require(not hit.is_empty(), "Ray passed through side barrier")
		if not hit.is_empty():
			_require(hit["position"].is_equal_approx(Vector3(side * 1.35, .9, 0)),
				"Side contact plane")

	var rear_ray := PhysicsRayQueryParameters3D.create(Vector3(0, .9, 0), Vector3(0, .9, 3), 1)
	var rear_hit: Dictionary = space.intersect_ray(rear_ray)
	_require(not rear_hit.is_empty(), "Rear stop missing")
	if not rear_hit.is_empty():
		_require(rear_hit["position"].is_equal_approx(Vector3(0, .9, 1.4)), "Rear contact")

	var entry_ray := PhysicsRayQueryParameters3D.create(Vector3(0, .9, -3), Vector3(0, .9, 0), 1)
	_require(space.intersect_ray(entry_ray).is_empty(), "Entry blocked")
	var roof_ray := PhysicsRayQueryParameters3D.create(Vector3(0, 5, 0), Vector3(0, 2, 0), 1)
	_require(space.intersect_ray(roof_ray).is_empty(), "Decorative roof has collision")
	var capsule := CapsuleShape3D.new()
	capsule.radius = .35
	capsule.height = 1.8
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = 1
	for position: Vector3 in [Vector3(0, .9, -2), Vector3(0, .9, 0), Vector3(.75, .9, 0)]:
		query.transform.origin = position
		_require(space.intersect_shape(query).is_empty(), "Capsule entry/inside clearance blocked")
	for position: Vector3 in [Vector3(-1.24, .9, 0), Vector3(1.24, .9, 0), Vector3(0, .9, 1.47)]:
		query.transform.origin = position
		_require(not space.intersect_shape(query).is_empty(), "Capsule misses barrier")

	_report["physics"] = {
		"both_side_rays_blocked": true, "rear_ray_blocked": true, "entry_ray_clear": true,
		"roof_visual_only": true, "actor_capsule_radius_m": .35, "actor_capsule_height_m": 1.8,
		"capsule_inside_and_entry_clear": true, "capsule_all_barriers_blocked": true,
		"movement_vehicle_network_and_placement": "not tested",
	}
	fixture.free()
