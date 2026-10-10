extends SceneTree
## Verify the linked access, level connector mating, floor queries and production motion.

const ASSET := "city_boardwalk_05"
const FIXTURE := "res://tools/asset_production/city_boardwalk_05/mating_check.tscn"
const EVIDENCE := "res://docs/assets/production/city_boardwalk_05-evidence/validation.json"
const EDITOR_STARTUP_FRAMES := 10
const STEP_MODES := [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]
const WALK_TICKS := 48

var _failed := false
var _report: Dictionary = {}
var _source: Dictionary = {}


## Begin once the scene tree can load linked resources.
func _initialize() -> void:
	_run.call_deferred()


## Normalize only new owned scenes, inspect resources, then run native physics outside editor mode.
func _run() -> void:
	if Engine.is_editor_hint():
		for frame: int in EDITOR_STARTUP_FRAMES:
			await process_frame  # gdstyle:ignore=quality/await-in-loop
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame  # gdstyle:ignore=quality/await-in-loop

	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	_source = JSON.parse_string(FileAccess.get_file_as_string(EVIDENCE))
	var scenes: Array[String] = [
		"res://scenes/prefabs/environment/city_boardwalk_05.tscn", FIXTURE,
	]
	if "--normalize" in OS.get_cmdline_user_args():
		if not Engine.is_editor_hint():
			push_error("Use headless --editor for UID-preserving normalization")
			quit(1)
			return

		for path: String in scenes:
			_save_scene(path)
			var first_hash: String = FileAccess.get_sha256(path)
			_save_scene(path)
			_require(first_hash == FileAccess.get_sha256(path), "Save/reload drift")
		_report["save_reload_byte_stable"] = true

	for path: String in scenes:
		var header: String = FileAccess.get_file_as_string(path).get_slice("\n", 0)
		_require(header.contains("uid=\"uid://"), "Missing saved scene UID: " + path)
		_check_dependencies(path)
	_check_model(scenes[0])
	_report["linked_models_checked"] = 1
	_report["saved_scene_and_dependency_uids_present"] = not _failed
	if not Engine.is_editor_hint():
		await _check_physics()
		_require(_report.has("physics"), "Physics checks incomplete")
	if _failed:
		quit(1)
		return

	_save_report()
	quit(0)


## Retain measured geometry and editor roundtrip evidence alongside the fresh runtime checks.
func _save_report() -> void:
	if _source.has("godot") and not _report.has("save_reload_byte_stable"):
		_report["save_reload_byte_stable"] = _source["godot"].get("save_reload_byte_stable", false)
	_report["engine"] = Engine.get_version_info()["string"]
	_source["godot"] = _report
	var file: FileAccess = FileAccess.open(EVIDENCE, FileAccess.WRITE)
	file.store_string(JSON.stringify(_source, "\t") + "\n")
	file.close()
	print("CITY_BOARDWALK_05_CHECK_PASS ", JSON.stringify(_report))


## Preserve a nonzero exit for contract violations across helper returns.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Roundtrip packed scenes without flattening their imported instances.
func _save_scene(path: String) -> void:
	var source: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	)
	var instance: Node = source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_require(packed.pack(instance) == OK, "Pack failed")
	_require(ResourceSaver.save(packed, path) == OK, "Save failed")
	instance.free()


## Require dependency UIDs to resolve to their declared paths recursively.
func _check_dependencies(path: String) -> void:
	_require(ResourceLoader.load(path) != null, "Missing resource: " + path)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		var child: String = parts[-1]
		_require(parts[0].begins_with("uid://"), "Dependency missing UID: " + dependency)
		if parts[0].begins_with("uid://"):
			var uid: int = ResourceUID.text_to_id(parts[0])
			_require(ResourceUID.has_id(uid), "Missing UID: " + dependency)
			_require(ResourceUID.get_id_path(uid) == child, "UID mismatch: " + dependency)
		_check_dependencies(child)


## Verify independent imported dimensions, materials and a minimal convex walk slab.
func _check_model(path: String) -> void:
	var instance: Node3D = (load(path) as PackedScene).instantiate()
	var model: Node3D = instance.get_node("Visuals/Model")
	_require(model.transform == Transform3D.IDENTITY, "Corrective model transform")
	_require(model.scene_file_path ==
		"res://art/models/environment/city_boardwalk_05/city_boardwalk_05.glb", "Unlinked model")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_require(meshes.size() == 1, "Mesh count")
	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh.transform * mesh.mesh.get_aabb()
	_require(bounds.position.distance_to(Vector3(-2.4, -.24, -3)) < .006, "Imported bounds min")
	_require(bounds.end.distance_to(Vector3(2.4, 0, 0)) < .006, "Imported bounds max")
	_require(mesh.mesh.get_surface_count() == 5, "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparency")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	var body: StaticBody3D = instance.get_node("Collision/Body")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Collision layers")
	_require(body.get_child_count() == 1, "Single continuous walk collider")
	var collider: CollisionShape3D = body.get_node("Access")
	_require(not collider.disabled and collider.shape is ConvexPolygonShape3D, "Enabled convex")
	_require(collider.transform == Transform3D.IDENTITY, "Collider transform")
	var shape: ConvexPolygonShape3D = collider.shape
	var expected := PackedVector3Array([
		Vector3(-1.8, -.24, 0), Vector3(1.8, -.24, 0),
		Vector3(2.4, -.24, -3), Vector3(-2.4, -.24, -3),
		Vector3(-1.8, 0, 0), Vector3(1.8, 0, 0), Vector3(2.4, 0, -3), Vector3(-2.4, 0, -3),
	])
	_require(shape.points.size() == 8, "Eight-point tapered slab")
	for point: Vector3 in expected:
		_require(point in shape.points, "Incorrect convex envelope")
	_report["imported_aabb"] = [str(bounds.position), str(bounds.end)]
	_report["eight_point_convex_slab_verified"] = not _failed
	instance.free()


## Check both terminal and perpendicular landward openings against production motion.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	_report["floor_rays"] = 0
	_report["outside_rays"] = 0
	for side: bool in [false, true]:
		_check_floor(space, fixture, side)

	var observations: Array[Dictionary] = []
	for side: bool in [false, true]:
		for x: float in [-1.35, 0.0, 1.35]:
			for reverse: bool in [false, true]:
				observations.append(await _walk_case(fixture, side, x, reverse))
	_report["physics"] = {
		"authority_replay_equal": not _failed, "trajectories": observations,
		"actor_capsule_radius_m": .35, "actor_capsule_height_m": 1.8,
		"network_transport_vehicle_water_falloff": "not tested",
	}
	fixture.free()


## Sample level joins and the widening edges without accepting a rectangular collision overfill.
func _check_floor(space: PhysicsDirectSpaceState3D, fixture: Node3D, side: bool) -> void:
	var access: Node3D = fixture.get_node("SideAccess" if side else "Access")
	for z: float in [.1, .001, -.001, -.6, -1.5, -2.4, -2.999, -3.001, -3.1]:
		for x: float in [-1.7, 0.0, 1.7]:
			_floor_ray(space, access.to_global(Vector3(x, 0, z)), true)
	for point: Vector3 in [Vector3(2.15, 0, -2.5), Vector3(-2.15, 0, -2.5)]:
		_floor_ray(space, access.to_global(point), true)
	for point: Vector3 in [
		Vector3(1.95, 0, -.1), Vector3(-1.95, 0, -.1),
		Vector3(2.45, 0, -2.9), Vector3(-2.45, 0, -2.9),
	]:
		_floor_ray(space, access.to_global(point), false)


## Require each measured floor hit to stay on the upward-facing zero-height walking datum.
func _floor_ray(space: PhysicsDirectSpaceState3D, point: Vector3, expected: bool) -> void:
	var ray := PhysicsRayQueryParameters3D.create(
		point + Vector3.UP, point + Vector3.DOWN, 1
	)
	var hit: Dictionary = space.intersect_ray(ray)
	_require(not hit.is_empty() == expected, "Floor ray mismatch at " + str(point))
	if expected and not hit.is_empty():
		_require(absf(hit["position"].y) < .001, "Walk surface step")
		_require(hit["normal"].dot(Vector3.UP) > .999, "Non-level walk surface")
	_report["floor_rays" if expected else "outside_rays"] += 1


## Traverse both seams in both directions with equivalent authoritative and replay intent.
func _walk_case(fixture: Node3D, side: bool, x: float, reverse: bool) -> Dictionary:
	var access: Node3D = fixture.get_node("SideAccess" if side else "Access")
	var actor: ActorMotion = fixture.get_node("Actor")
	var start: Vector3 = access.to_global(Vector3(x, .001, -3.5 if reverse else .5))
	var goal: Vector3 = access.to_global(Vector3(x, .001, .5 if reverse else -3.5))
	var direction: Vector3 = (goal - start).normalized()
	var ends: Array[Vector3] = []
	var fixed_delta := 1.0 / Engine.physics_ticks_per_second
	for mode: ActorMotion.StepMode in STEP_MODES:
		actor.position = start
		actor.neutralize()
		actor.apply_floor_snap()
		for tick: int in WALK_TICKS:
			await physics_frame  # gdstyle:ignore=quality/await-in-loop
			var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
				tick + 1, tick, Vector2(direction.x, direction.z), 0.0, false, false
			)
			_require(actor.step(command, fixed_delta, mode), "Step rejected")
			_require(absf(actor.position.y - .001) < .01, "Lost floor datum")
			_require(actor.test_move(actor.global_transform, Vector3(0, -.05, 0)), "Lost floor")
		_require(actor.position.distance_to(goal) < .002, "Route blocked or drifted")
		ends.append(actor.position)
	_require(ends[0].is_equal_approx(ends[1]), "Authority/replay differs")
	return {
		"start": [start.x, start.y, start.z], "goal": [goal.x, goal.y, goal.z],
		"side_access": side, "reverse": reverse, "ticks_per_mode": WALK_TICKS,
		"authority_end": [ends[0].x, ends[0].y, ends[0].z],
		"replay_end": [ends[1].x, ends[1].y, ends[1].z],
	}
