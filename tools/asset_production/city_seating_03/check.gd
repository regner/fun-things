extends SceneTree
## Validate the linked corner seat, saved identities, solid envelope and production actor movement.

const ASSET := "city_seating_03"
const PREFAB := "res://scenes/prefabs/environment/city_seating_03.tscn"
const FIXTURE := "res://tools/asset_production/city_seating_03/physics_check.tscn"
const EVIDENCE := "res://docs/assets/production/city_seating_03-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-1.05, 0, -1.05), Vector3(2.1, .46, 2.1))
const WALK_TICKS := 60
const EDITOR_STARTUP_FRAMES := 10

var _failed := false
var _report: Dictionary = {}


## Wait for the tree before loading resources or exercising physics.
func _initialize() -> void:
	_run.call_deferred()


## Normalize saved wrappers separately from standalone physics checks.
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

	_check_dependencies(FIXTURE)
	_check_model()
	_require(_report.has("linked_model_identity"), "Model checks did not complete")
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
	print("CITY_SEATING_03_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Fail visibly in logs and propagate contract failures to the process status.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Roundtrip a saved scene without flattening the imported model instance.
func _save_scene(path: String) -> void:
	var source: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE,
	)
	var instance: Node = source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_require(packed.pack(instance) == OK, "Pack failed")
	_require(ResourceSaver.save(packed, path) == OK, "Save failed")
	instance.free()


## Resolve every linked resource and its retained UID where serialized.
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


## Measure imported geometry and assert the deliberately separate two-box L-shaped static envelope.
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

	var body: StaticBody3D = instance.get_node("Collision/Body")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Static collision filters")
	_require(body.get_child_count() == 2, "Compound shape count")
	var rear: CollisionShape3D = body.get_node("RearArm")
	var left: CollisionShape3D = body.get_node("LeftArm")
	_require(rear.shape.size.is_equal_approx(Vector3(2.1, .46, .65)), "Rear arm envelope")
	_require(rear.position.is_equal_approx(Vector3(0, .23, .725)), "Rear arm datum")
	_require(left.shape.size.is_equal_approx(Vector3(.65, .46, 1.45)), "Left arm envelope")
	_require(left.position.is_equal_approx(Vector3(-.725, .23, -.325)), "Left arm datum")
	_report["bounds_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	_report["static_body_count"] = 1
	_report["box_shape_count"] = 2
	instance.free()


## Verify both arms, the open notch, the elbow seam and above-seat air through physics APIs.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	_check_queries(space)

	var results: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [
		ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY,
	]:
		results.append(await _walk(fixture.get_node("Actor"), Vector3(0, .001, -2),
			Vector2(0, 1), mode))
		results.append(await _walk(fixture.get_node("Actor"), Vector3(2, .001, 0),
			Vector2(-1, 0), mode))
		results.append(await _walk(fixture.get_node("Actor"), Vector3(1.55, .001, -2),
			Vector2(0, 1), mode))
		results.append(await _walk(fixture.get_node("Actor"), Vector3(0, .001, 2),
			Vector2(0, -1), mode))
		results.append(await _walk(fixture.get_node("Actor"), Vector3(.4, .001, -.4),
			Vector2(0, -1), mode))

	_require(results.size() == 10, "Movement helper incomplete")
	for offset: int in [0, 5]:
		_require(absf(results[offset].z - .049) < .02, "Inside rear arm contact")
		_require(absf(results[offset + 1].x + .049) < .02, "Inside left arm contact")
		_require(results[offset + 2].distance_to(Vector3(1.55, .001, 3)) < .01, "Clear bypass")
		_require(absf(results[offset + 3].z - 1.401) < .02, "Outside rear arm contact")
		_require(results[offset + 4].distance_to(Vector3(.4, .001, -5.4)) < .01,
			"Open corner exit")
	for index: int in 5:
		_require(results[index].is_equal_approx(results[index + 5]), "Authority/replay mismatch")

	_report["physics"] = {
		"ray_cases": 5, "actor_radius_m": .35, "actor_height_m": 1.8,
		"walk_ticks_per_case": WALK_TICKS, "movement_cases": 10,
		"inside_rear_stop_z_m": results[0].z, "inside_left_stop_x_m": results[1].x,
		"bypass_end_z_m": results[2].z, "outside_rear_stop_z_m": results[3].z,
		"open_corner_exit_z_m": results[4].z, "authority_replay_equal": true,
		"network_transport_and_world_placement": "not tested",
	}
	fixture.free()


## Check continuous limb tops and the elbow while preserving notch and overhead air.
func _check_queries(space: PhysicsDirectSpaceState3D) -> void:
	for point: Vector2 in [Vector2(0, .725), Vector2(-.725, 0), Vector2(-.725, .4)]:
		var ray := PhysicsRayQueryParameters3D.create(
			Vector3(point.x, 1, point.y), Vector3(point.x, .1, point.y), 1,
		)
		var hit: Dictionary = space.intersect_ray(ray)
		_require(not hit.is_empty(), "Arm or elbow top not solid")
		if not hit.is_empty():
			_require(absf(hit["position"].y - .46) < .001, "Seat top height")

	for ray: PhysicsRayQueryParameters3D in [
		PhysicsRayQueryParameters3D.create(Vector3(.4, 1, -.4), Vector3(.4, .1, -.4), 1),
		PhysicsRayQueryParameters3D.create(Vector3(-2, .7, 0), Vector3(2, .7, 0), 1),
	]:
		_require(space.intersect_ray(ray).is_empty(), "Notch or above-seat air blocked")


## Walk the production-size capsule toward either arm or out through the clear corner.
func _walk(actor: ActorMotion, start: Vector3, direction: Vector2,
		mode: ActorMotion.StepMode) -> Vector3:
	actor.position = start
	actor.neutralize()
	for tick: int in WALK_TICKS:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, direction, 0.0, false, false,
		)
		_require(actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step rejected")

	return actor.position
