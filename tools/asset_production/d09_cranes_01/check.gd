extends SceneTree
## Check the source-linked crane, saved identities and production capsule contact/bypass.

const ASSET := "d09_cranes_01"
const PREFAB := "res://scenes/prefabs/environment/d09_cranes_01.tscn"
const FIXTURE := "res://tools/asset_production/d09_cranes_01/check_scene.tscn"
const EVIDENCE := "res://docs/assets/production/d09_cranes_01-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-2.8, 0, -16.5173), Vector3(5.6, 22.0654, 22.0448))
const WALK_TICKS := 120
const BOUNDS_TOLERANCE_M := .001
const CONTACT_PLANE_Z_M := -3.15
const CONTACT_GAP_LIMIT_M := .03

var _failed := false
var _report: Dictionary = { "resource_uids": {} }


## Wait until the scene tree can register imported resources and physics bodies.
func _initialize() -> void:
	_run.call_deferred()


## Validate saved resources and physics, recording only a fully passing receipt.
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
	print("D09_CRANES_01_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Fail visibly and return nonzero after the bounded checks finish.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Normalize only owned scenes, preserving UIDs and imported instance ancestry.
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


## Recursively verify saved dependency paths and their registered identities.
func _check_dependencies(path: String) -> void:
	_require(ResourceLoader.load(path) != null, "Missing resource: " + path)
	var uid: int = ResourceLoader.get_resource_uid(path)
	_require(uid != ResourceUID.INVALID_ID and ResourceUID.has_id(uid), "Missing UID: " + path)
	_require(ResourceUID.get_id_path(uid) == path, "UID path mismatch: " + path)
	_report["resource_uids"][path] = ResourceUID.id_to_text(uid)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		var child: String = parts[-1]
		if parts[0].begins_with("uid://"):
			var child_uid: int = ResourceUID.text_to_id(parts[0])
			_require(ResourceUID.has_id(child_uid), "Missing dependency UID: " + dependency)
			_require(ResourceUID.get_id_path(child_uid) == child, "Dependency UID mismatch")
		_check_dependencies(child)


## Measure the actual imported model and its deliberate two-box pedestal collision.
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
	_require(bounds.position.distance_to(EXPECTED_BOUNDS.position) < BOUNDS_TOLERANCE_M,
		"Bounds minimum")
	_require(bounds.size.distance_to(EXPECTED_BOUNDS.size) < BOUNDS_TOLERANCE_M, "Bounds size")
	_require(mesh.mesh.get_surface_count() == 5, "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparency")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	var bodies: Array[Node] = instance.find_children("*", "CollisionObject3D", true, false)
	_require(bodies.size() == 1, "Expected one static body")
	var body: StaticBody3D = instance.get_node("Collision/PedestalBody")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Static-world filtering")
	_require(body.get_child_count() == 2, "Expected two simple boxes")
	_check_box(body.get_node("Plinth"), Vector3(5.6, .8, 5.6), Vector3(0, .4, 0))
	_check_box(body.get_node("Pedestal"), Vector3(3.34, 8.6, 3.34), Vector3(0, 5.1, 0))
	_report["bounds_min_m"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size_m"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	_report["static_collision"] = { "bodies": 1, "boxes": 2, "layer": 1, "mask": 0 }
	instance.free()


## Assert independent literal shape sizes and ground-relative centres.
func _check_box(node: CollisionShape3D, size: Vector3, center: Vector3) -> void:
	var shape: BoxShape3D = node.shape as BoxShape3D
	_require(shape != null, "Expected box")
	_require(shape.size.is_equal_approx(size), "Box size")
	_require(node.position.is_equal_approx(center), "Box centre")


## Verify base/tower ray contacts, overhead clearance and authority/replay equivalence.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	for height: float in [.4, 4.0]:
		var ray := PhysicsRayQueryParameters3D.create(
			Vector3(0, height, -6), Vector3(0, height, 6), 1,
		)
		var hit: Dictionary = space.intersect_ray(ray)
		_require(not hit.is_empty(), "Ray passed through pedestal")
		if not hit.is_empty():
			_require(hit["collider"] == fixture.get_node("Crane/Collision/PedestalBody"),
				"Ray hit wrong body")

	var overhead := PhysicsRayQueryParameters3D.create(Vector3(0, 10, -6), Vector3(0, 10, 6), 1)
	_require(space.intersect_ray(overhead).is_empty(), "Overhead decoration adds collision")
	var contact: Array[Vector3] = []
	var bypass: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		contact.append(await _walk(fixture.get_node("Actor"), 0, mode))
		bypass.append(await _walk(fixture.get_node("Actor"), 3.6, mode))

	print("PHYSICS_OBSERVATIONS contact=", contact, " bypass=", bypass)
	_require(contact[0].z <= CONTACT_PLANE_Z_M, "Actor penetrated plinth")
	_require(contact[0].z >= CONTACT_PLANE_Z_M - CONTACT_GAP_LIMIT_M, "Excess contact gap")
	_require(bypass[0].distance_to(Vector3(3.6, 0, 4)) < .015, "Clear apron bypass failed")
	_require(contact[0].is_equal_approx(contact[1]), "Authority/replay contact mismatch")
	_require(bypass[0].is_equal_approx(bypass[1]), "Authority/replay bypass mismatch")
	_report["physics"] = {
		"base_and_tower_rays_blocked": true, "overhead_ray_clear": true,
		"actor_capsule_radius_m": .35, "actor_capsule_height_m": 1.8,
		"ticks_per_case_per_mode": WALK_TICKS, "authority_replay_equal": true,
		"contact_stop_m": [contact[0].x, contact[0].y, contact[0].z],
		"bypass_end_m": [bypass[0].x, bypass[0].y, bypass[0].z],
		"vehicle_network_transport_and_placement": "not tested",
	}
	fixture.free()


## Drive the production capsule through the same saved world in both simulation modes.
func _walk(actor: ActorMotion, x: float, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = Vector3(x, .001, -6)
	actor.neutralize()
	actor.apply_floor_snap()
	for tick: int in WALK_TICKS:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, Vector2(0, 1), 0.0, false, false,
		)
		_require(actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step rejected")

	return actor.position
