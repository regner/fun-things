extends SceneTree
## Validate the linked guard pair, shoulder envelopes and production actor blocking.

const ASSET := "city_harbour_bridge_02"
const PREFAB := "res://scenes/prefabs/environment/city_harbour_bridge_02.tscn"
const FIXTURE := "res://tools/asset_production/city_harbour_bridge_02/guard_check.tscn"
const EVIDENCE := "res://docs/assets/production/city_harbour_bridge_02-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-45.5, 0, -8.5), Vector3(91, 1.1, 17))
const BLOCK_TICKS := 120
const WALK_TICKS := 240
const EDITOR_STARTUP_FRAMES := 10

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
	print("CITY_HARBOUR_BRIDGE_02_CHECK_PASS ", JSON.stringify(_report))
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
	_require(mesh.mesh.get_surface_count() == 5, "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque guard")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	var body: StaticBody3D = instance.get_node("Collision/Body")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Collision layers")
	_require(body.get_child_count() == 2, "Exactly two guard colliders")
	for side: int in [-1, 1]:
		var collider: CollisionShape3D = body.get_node("NorthGuard" if side < 0 else "SouthGuard")
		_require(collider.shape is BoxShape3D and not collider.disabled, "Guard shape")
		_require(collider.shape.size.is_equal_approx(Vector3(91, 1.1, .35)), "Guard envelope")
		_require(collider.position.is_equal_approx(Vector3(0, .55, side * 8.325)), "Guard datum")
	_report["bounds_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	instance.free()


## Query full-span barriers and open water, then exercise production authority/replay movement.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	_check_paths(space)
	var actor: ActorMotion = fixture.get_node("Actor")
	var contacts: Array[float] = []
	var walks: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		for side: int in [-1, 1]:
			actor.neutralize()
			actor.position = Vector3(0, .001, side * 7.0)
			actor.apply_floor_snap()
			await _move_actor(  # gdstyle:ignore=quality/await-in-loop
				actor, Vector2(0, side), BLOCK_TICKS, mode
			)
			_require(absf(absf(actor.position.z) - 7.8) < .01, "Actor crossed guard/wrong contact")
			_require(absf(actor.position.y) < .01, "Actor lost deck")
			contacts.append(actor.position.z)
			actor.neutralize()
			actor.position = Vector3(-10, .001, side * 7.5)
			actor.apply_floor_snap()
			await _move_actor(  # gdstyle:ignore=quality/await-in-loop
				actor, Vector2(1, 0), WALK_TICKS, mode
			)
			_require(absf(actor.position.x - 10) < .01, "Sidewalk traversal snagged")
			_require(absf(actor.position.z - side * 7.5) < .01, "Sidewalk lateral drift")
			walks.append(actor.position)

	_require(is_equal_approx(contacts[0], contacts[2]), "North authority/replay differs")
	_require(is_equal_approx(contacts[1], contacts[3]), "South authority/replay differs")
	_require(walks[0].is_equal_approx(walks[2]), "North walk authority/replay differs")
	_require(walks[1].is_equal_approx(walks[3]), "South walk authority/replay differs")
	_report["physics"] = {
		"guard_rays": 14, "water_clear_rays": 1, "above_guard_clear_rays": 1,
		"roadway_clear_rays": 1, "actor_block_ticks_per_side_per_mode": BLOCK_TICKS,
		"actor_walk_ticks_per_side_per_mode": WALK_TICKS,
		"authority_replay_equal": true, "actor_contact_z": contacts,
		"sidewalk_walk_end_x": walks[0].x,
		"car_driving_and_network_transport": "pending downstream gameplay integration",
	}
	fixture.free()


## Apply validated production commands once per fixed physics tick.
func _move_actor(actor: ActorMotion, direction: Vector2, ticks: int,
		mode: ActorMotion.StepMode) -> void:
	for tick: int in ticks:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, direction, 0.0, false, false
		)
		_require(actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step rejected")


## Confirm both full-span barriers, roadway clearance and the unchanged harbour water gap.
func _check_paths(space: PhysicsDirectSpaceState3D) -> void:
	var ray := PhysicsRayQueryParameters3D.new()
	ray.collision_mask = 1
	for side: int in [-1, 1]:
		for x: float in [-45.49, -35.0, -3.5, 0.0, 3.5, 35.0, 45.49]:
			ray.from = Vector3(x, .5, side * 7.5)
			ray.to = Vector3(x, .5, side * 9)
			var hit: Dictionary = space.intersect_ray(ray)
			_require(not hit.is_empty(), "Missing guard")
			if not hit.is_empty():
				_require(absf(absf(hit["position"].z) - 8.15) < .001, "Guard inner face")

	for height: float in [-1.6, 1.2]:
		ray.from = Vector3(0, height, -20)
		ray.to = Vector3(0, height, 20)
		_require(space.intersect_ray(ray).is_empty(), "Water/above-guard path obstructed")

	var roadway := PhysicsRayQueryParameters3D.create(Vector3(-46, .5, 0), Vector3(46, .5, 0), 1)
	_require(space.intersect_ray(roadway).is_empty(), "Roadway obstructed")
