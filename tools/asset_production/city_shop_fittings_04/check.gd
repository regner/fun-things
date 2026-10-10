extends SceneTree
## Validate the linked shutter, saved identities, static envelope and production actor contact.

const ASSET := "city_shop_fittings_04"
const PREFAB := "res://scenes/prefabs/environment/city_shop_fittings_04.tscn"
const FIXTURE := "res://tools/asset_production/city_shop_fittings_04/collision_check.tscn"
const EVIDENCE := "res://docs/assets/production/city_shop_fittings_04-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-1.6, 0, -.28), Vector3(3.2, 2.48, .27))
const MOVEMENT_TICKS := 60
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
	print("CITY_SHOP_FITTINGS_04_CHECK_PASS ", JSON.stringify(_report))
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
	_require(mesh.mesh.get_surface_count() == 4, "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(
			material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparent shutter",
		)
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	var body: StaticBody3D = instance.get_node("Collision/Body")
	var collider: CollisionShape3D = body.get_node("Shape")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Collision layers")
	_require(collider.shape is BoxShape3D and not collider.disabled, "Shutter shape")
	_require(collider.shape.size.is_equal_approx(Vector3(3.2, 2.48, .19)), "Shutter envelope")
	_require(collider.position.is_equal_approx(Vector3(0, 1.24, -.105)), "Ground datum")
	_report["bounds_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	instance.free()


## Exercise production motion in both modes and query solid versus above-header rays.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	var ray := PhysicsRayQueryParameters3D.create(Vector3(0, .5, -2), Vector3(0, .5, 2), 1)
	var hit: Dictionary = space.intersect_ray(ray)
	_require(not hit.is_empty(), "Ray must hit shutter")
	if not hit.is_empty():
		_require(
			hit["collider"] == fixture.get_node("Shutter/Collision/Body"), "Wrong ray collider",
		)
		_require(absf(hit["position"].z + .2) < .001, "Ray collision envelope")

	var above := PhysicsRayQueryParameters3D.create(Vector3(0, 2.6, -2), Vector3(0, 2.6, 2), 1)
	_require(space.intersect_ray(above).is_empty(), "Above-header ray must remain clear")
	var actor: ActorMotion = fixture.get_node("Actor")
	var results: Array[Vector3] = []
	# The two modes must finish the same sequential, physics-frame-driven test cases.
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		var cases: Array[Vector3] = await _movement_cases(  # gdstyle:ignore=quality/await-in-loop
			actor, mode,
		)
		results.append_array(cases)

	for index: int in 4:
		_require(
			results[index].distance_to(results[index + 4]) < .001,
			"Authority/replay differs beyond 1 mm: " + str(results),
		)
	_report["physics"] = {
		"body_ray_hit": true, "above_header_ray_clear": true,
		"actor_capsule_radius_m": .35, "actor_capsule_height_m": 1.8,
		"movement_ticks_per_case_per_mode": MOVEMENT_TICKS,
		"authority_replay_within_1mm": true,
		"all_case_positions": results.map(_vector_to_array),
		"front_stop": [results[0].x, results[0].y, results[0].z],
		"side_stop": [results[1].x, results[1].y, results[1].z],
		"rear_stop": [results[2].x, results[2].y, results[2].z],
		"bypass_end": [results[3].x, results[3].y, results[3].z],
		"car_and_network_transport": "pending downstream; not exercised by these actor checks",
	}
	fixture.free()


## Encode measured positions without stringifying vectors in the JSON evidence.
func _vector_to_array(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]


## Assert literal contact and clear-bypass outcomes for one simulation mode.
func _movement_cases(actor: ActorMotion, mode: ActorMotion.StepMode) -> Array[Vector3]:
	var front: Vector3 = await _move_actor(actor, Vector3(0, 0, -2), Vector2(0, 1), mode)
	_require(absf(front.z + .55) < .002, "Front contact")
	var side: Vector3 = await _move_actor(actor, Vector3(3, 0, -.105), Vector2(-1, 0), mode)
	_require(absf(side.x - 1.95) < .002, "Side contact")
	var rear: Vector3 = await _move_actor(actor, Vector3(0, 0, 2), Vector2(0, -1), mode)
	_require(absf(rear.z - .34) < .002, "Rear contact")
	var bypass: Vector3 = await _move_actor(actor, Vector3(2.05, 0, -2), Vector2(0, 1), mode)
	_require(absf(bypass.z - 3) < .002, "Clear bypass blocked")
	return [front, side, rear, bypass]


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
