extends SceneTree
## Validate gangway resources, saved identities, sloped support, guards and production movement.

const ASSET := "city_marina_docks_03"
const PREFAB := "res://scenes/prefabs/environment/city_marina_docks_03.tscn"
const FIXTURE := "res://tools/asset_production/city_marina_docks_03/walk_check.tscn"
const EVIDENCE := "res://docs/assets/production/city_marina_docks_03-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-1, .25, -4), Vector3(2, 2.234, 8))
const TRAVERSE_TICKS := 144
const GUARD_TICKS := 36
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

	_check_dependencies(FIXTURE)
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
	print("CITY_MARINA_DOCKS_03_CHECK_PASS ", JSON.stringify(_report))
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
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparent deck")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	var body: StaticBody3D = instance.get_node("Collision/Body")
	var collider: CollisionShape3D = body.get_node("Deck")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Collision layers")
	_require(collider.shape is ConcavePolygonShape3D and not collider.disabled, "Deck shape")
	_require(collider.transform == Transform3D.IDENTITY, "Deck corrective transform")
	_require(collider.shape.get_faces().size() == 84, "Closed deck triangle count")
	_require(body.get_child_count() == 3, "Only one walk surface and two visible guards")
	for side: String in ["GuardLeft", "GuardRight"]:
		var guard: CollisionShape3D = body.get_node(side)
		_require(guard.shape is BoxShape3D and not guard.disabled, "Guard shape")
		_require(guard.shape.size.is_equal_approx(Vector3(.1, .986_394, 6.08276253)),
			"Guard envelope")
		_require(is_equal_approx(absf(guard.position.x), .94) and guard.position.y == 1.5,
			"Guard location")
		_require(absf(guard.rotation.x + .165_148_677_4) < .00001, "Guard slope")
	_report["bounds_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	instance.free()


## Check independent heights at both joins and the slope, then test both movement modes.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	_check_queries(space)

	var actor: ActorMotion = fixture.get_node("Actor")
	_require(actor.floor_max_angle > deg_to_rad(9.463), "Slope exceeds ActorMotion floor angle")
	var traversals: Array[Dictionary] = []
	for direction: float in [-1.0, 1.0]:
		var results: Array[Vector3] = []
		for mode: ActorMotion.StepMode in [
			ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY,
		]:
			results.append(await _traverse(actor, direction, mode))

		_require(results[0].is_equal_approx(results[1]), "Authority/replay traversal differs")
		traversals.append({ "direction": direction, "end_position": _coordinates(results[0]) })

	var guard_stops: Array[Dictionary] = []
	for direction: float in [-1.0, 1.0]:
		var results: Array[Vector3] = []
		for mode: ActorMotion.StepMode in [
			ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY,
		]:
			results.append(await _guard_stop(actor, direction, mode))

		_require(results[0].is_equal_approx(results[1]), "Authority/replay guard differs")
		guard_stops.append({ "side": direction, "position": _coordinates(results[0]) })

	_report["physics"] = {
		"walk_support_rays": 11, "blocking_guard_rays": 2,
		"clear_landing_side_rays": 4, "actor_motion_ticks_per_traversal": TRAVERSE_TICKS,
		"authority_replay_equal": true, "traversals": traversals, "guard_stops": guard_stops,
		"water_falloff_and_network_transport": "not tested; outside component scope",
	}
	fixture.free()


## Walk across both landing seams and the entire ramp with continuous support in either direction.
func _traverse(actor: ActorMotion, direction: float, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = Vector3(0, .501 if direction > 0 else 1.501, -5 * direction)
	actor.neutralize()
	actor.apply_floor_snap()
	await _move(actor, Vector2(0, direction), TRAVERSE_TICKS, mode)
	print("TRAVERSE ", direction, " ", actor.position)
	_require(actor.position.z * direction > 6 and actor.position.z * direction < 7.1,
		"Ramp traversal blocked or advanced incorrectly")
	_require(absf(actor.position.y - (1.5 if direction > 0 else .5)) < .01,
		"Actor did not follow slope elevation")
	_require(absf(actor.position.x) < .001, "Unexpected lateral movement")
	_require(actor.test_move(actor.global_transform, Vector3(0, -.05, 0)), "No floor support")
	return actor.position


## Run real fixed-tick production movement; the fixture never supplies vertical velocity or gravity.
func _move(actor: ActorMotion, move: Vector2, ticks: int, mode: ActorMotion.StepMode) -> void:
	for tick: int in ticks:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, move, 0.0, false, false
		)
		_require(actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step rejected")
		_require(actor.test_move(actor.global_transform, Vector3(0, -.08, 0)),
			"Movement lost ramp support")


## Serialize measured vectors as numeric arrays rather than display strings.
func _coordinates(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]


## Query saved walk heights, visible barriers and intentionally open landings independently.
func _check_queries(space: PhysicsDirectSpaceState3D) -> void:
	var samples: Array[Vector2] = [
		Vector2(-4.01, .5), Vector2(-4, .5), Vector2(-3.99, .5), Vector2(-3, .5),
		Vector2(-1.5, .75), Vector2(0, 1), Vector2(1.5, 1.25), Vector2(3, 1.5),
		Vector2(3.99, 1.5), Vector2(4, 1.5), Vector2(4.01, 1.5),
	]
	for sample: Vector2 in samples:
		var ray := PhysicsRayQueryParameters3D.create(
			Vector3(0, 3, sample.x), Vector3(0, 0, sample.x), 1
		)
		var hit: Dictionary = space.intersect_ray(ray)
		_require(not hit.is_empty(), "Missing walk support")
		if not hit.is_empty():
			_require(absf(hit["position"].y - sample.y) < .001, "Walk support height")
			_require(hit["normal"].y > .98, "Walk surface faces upwards")

	for side: float in [-1.0, 1.0]:
		var rail_ray := PhysicsRayQueryParameters3D.create(
			Vector3(0, 1.5, 0), Vector3(side * 1.2, 1.5, 0), 1
		)
		var hit: Dictionary = space.intersect_ray(rail_ray)
		_require(not hit.is_empty(), "Visible rail must block")
		if not hit.is_empty():
			_require(absf(absf(hit["position"].x) - .89) < .001, "Guard inner edge")

		for z: float in [-3.6, 3.6]:
			var open_ray := PhysicsRayQueryParameters3D.create(
				Vector3(0, 2.0, z), Vector3(side * 1.2, 2.0, z), 1
			)
			_require(space.intersect_ray(open_ray).is_empty(), "No invisible landing barrier")


## Drive the production capsule into one visible side guard and check the expected inner stop.
func _guard_stop(actor: ActorMotion, direction: float, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = Vector3(0, 1.006, 0)
	actor.neutralize()
	actor.apply_floor_snap()
	await _move(actor, Vector2(direction, 0), GUARD_TICKS, mode)
	_require(absf(actor.position.x) > .52 and absf(actor.position.x) < .55,
		"Actor must stop at visible guard, not pass through")
	return actor.position
