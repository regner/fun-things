extends SceneTree
## Verify the linked coastal support, underside mating, contact queries and production motion.

const ASSET := "city_boardwalk_04"
const FIXTURE := "res://tools/asset_production/city_boardwalk_04/mating_check.tscn"
const EVIDENCE := "res://docs/assets/production/city_boardwalk_04-evidence/validation.json"
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
		"res://scenes/prefabs/environment/city_boardwalk_04.tscn", FIXTURE,
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
	print("CITY_BOARDWALK_04_CHECK_PASS ", JSON.stringify(_report))


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


## Verify imported identity, opaque surfaces, independent bounds and three simple blockers.
func _check_model(path: String) -> void:
	var packed: PackedScene = load(path)
	var instance: Node3D = packed.instantiate()
	var model: Node3D = instance.get_node("Visuals/Model")
	_require(model.transform == Transform3D.IDENTITY, "Corrective model transform")
	_require(model.scene_file_path ==
		"res://art/models/environment/city_boardwalk_04/city_boardwalk_04.glb", "Unlinked model")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_require(meshes.size() == 1, "Mesh count")
	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh.transform * mesh.mesh.get_aabb()
	_require(bounds.position.distance_to(Vector3(-1.68, 0, -.28)) < .001, "Imported bounds min")
	_require(bounds.end.distance_to(Vector3(1.68, 2, .28)) < .001, "Imported bounds max")
	_require(mesh.mesh.get_surface_count() == 2, "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparency")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	var body: StaticBody3D = instance.get_node("Collision/Body")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Collision layers")
	_require(body.get_child_count() == 3, "Minimal three-box compound")
	for entry: Array in [
		["LeftPost", Vector3(-1.38, .84, 0), Vector3(.5, 1.68, .56)],
		["RightPost", Vector3(1.38, .84, 0), Vector3(.5, 1.68, .56)],
		["Crosshead", Vector3(0, 1.84, 0), Vector3(3.36, .32, .48)],
	]:
		var collider: CollisionShape3D = body.get_node(entry[0])
		_require(not collider.disabled and collider.shape is BoxShape3D, "Enabled box")
		var shape: BoxShape3D = collider.shape
		_require(collider.position.is_equal_approx(entry[1]), "Collider position")
		_require(shape.size.is_equal_approx(entry[2]), "Collider envelope")
	_report["imported_aabb"] = [str(bounds.position), str(bounds.end)]
	_report["three_box_compound_verified"] = not _failed
	instance.free()


## Check straight and curved bearing fit, exposed structure queries and actor outcomes.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	_report["bearing_rays"] = 0
	for name: String in ["SupportA", "SupportB", "BendSupport"]:
		_check_bearing(fixture, space, name)

	_check_structure_queries(space, fixture)
	var observations: Array[Dictionary] = []
	for x: float in [-1.38, 1.38, 0.0, 2.4]:
		observations.append(await _walk_case(fixture, Vector3(12 + x, .001, 2), x, false))
	for x: float in [-1.3, 0.0, 1.3]:
		observations.append(await _walk_case(fixture, Vector3(x, 2.241, 2), x, true))
	_report["physics"] = {
		"authority_replay_equal": not _failed, "trajectories": observations,
		"actor_capsule_radius_m": .35, "actor_capsule_height_m": 1.8,
		"network_transport_vehicle_water_falloff": "not tested",
	}
	fixture.free()


## Independently sample the bearing footprint against the actual sibling underside collider.
func _check_bearing(fixture: Node3D, space: PhysicsDirectSpaceState3D, name: String) -> void:
	var support: Node3D = fixture.get_node(name)
	var deck: Node3D = fixture.get_node("Bend" if name == "BendSupport" else "Deck")
	var support_body: StaticBody3D = support.get_node("Collision/Body")
	_require(absf(support.position.y + 2 - (deck.position.y - .24)) < .001,
		"Bearing must meet sibling underside")
	for x: float in [-1.5, 0.0, 1.5]:
		for z: float in [-.20, .20]:
			var point: Vector3 = support.to_global(Vector3(x, 1.9, z))
			var ray := PhysicsRayQueryParameters3D.create(
				point, point + Vector3.UP * .2, 1, [support_body.get_rid()]
			)
			var hit: Dictionary = space.intersect_ray(ray)
			_require(not hit.is_empty(), "Missing deck above bearing")
			if not hit.is_empty():
				_require(hit["collider"] == deck.get_node("Collision/Body"), "Wrong bearing member")
				_require(absf(hit["position"].y - 2.0) < .001, "Sibling underside datum")
			_report["bearing_rays"] += 1


## Query the two posts and low crosshead while preserving the actual open central void.
func _check_structure_queries(space: PhysicsDirectSpaceState3D, fixture: Node3D) -> void:
	_report["structure_rays"] = 0
	for entry: Array in [
		[-1.38, .8, true, .28], [1.38, .8, true, .28],
		[0.0, .8, false, 0.0], [0.0, 1.84, true, .24], [2.0, .8, false, 0.0],
	]:
		var ray := PhysicsRayQueryParameters3D.create(
			Vector3(12 + entry[0], entry[1], 2), Vector3(12 + entry[0], entry[1], -2), 1
		)
		var hit: Dictionary = space.intersect_ray(ray)
		_require(not hit.is_empty() == entry[2], "Incorrect support ray obstruction")
		if not hit.is_empty():
			_require(hit["collider"] == fixture.get_node("ContactSupport/Collision/Body"),
				"Wrong support body hit")
			_require(absf(hit["position"].z - entry[3]) < .001, "Ray blocker envelope")
		_report["structure_rays"] += 1


## Run fixed intent through production ActorMotion and compare both simulation modes.
func _walk_case(fixture: Node3D, start: Vector3, x: float, on_deck: bool) -> Dictionary:
	var actor: ActorMotion = fixture.get_node("Actor")
	var ends: Array[Vector3] = []
	var fixed_delta := 1.0 / Engine.physics_ticks_per_second
	for mode: ActorMotion.StepMode in STEP_MODES:
		actor.position = start
		actor.neutralize()
		actor.apply_floor_snap()
		for tick: int in WALK_TICKS:
			await physics_frame  # gdstyle:ignore=quality/await-in-loop
			var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
				tick + 1, tick, Vector2(0, -1), 0.0, false, false
			)
			_require(actor.step(command, fixed_delta, mode), "Step rejected")
			_require(absf(actor.position.y - start.y) < .01, "Lost floor datum")
			_require(actor.test_move(actor.global_transform, Vector3(0, -.05, 0)), "Lost floor")
		_require(absf(actor.position.x - start.x) < .002, "Lateral drift")
		if on_deck or x > 2:
			_require(absf(actor.position.z + 2) < .002, "Unobstructed route blocked")
		elif absf(x) > 1:
			_require(absf(actor.position.z - .63) < .01, "Actor must stop before post")
		else:
			# A 1.8 m capsule cannot pass a 1.68 m crosshead: not an underwalk route.
			_require(actor.position.z > .45 and actor.position.z < .60,
				"Actor must stop at low crosshead")
		ends.append(actor.position)
	_require(ends[0].is_equal_approx(ends[1]), "Authority/replay differs")
	return {
		"start": [start.x, start.y, start.z], "on_deck": on_deck,
		"ticks_per_mode": WALK_TICKS,
		"authority_end": [ends[0].x, ends[0].y, ends[0].z],
		"replay_end": [ends[1].x, ends[1].y, ends[1].z],
	}
