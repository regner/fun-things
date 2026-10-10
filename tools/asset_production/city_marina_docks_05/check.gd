extends SceneTree
## Verify the linked small cleat, deck mounting, saved identities and unobstructed finger route.

const ASSET := "city_marina_docks_05"
const PREFAB := "res://scenes/prefabs/environment/city_marina_docks_05.tscn"
const FIXTURE := "res://tools/asset_production/city_marina_docks_05/mount_check.tscn"
const EVIDENCE := "res://docs/assets/production/city_marina_docks_05-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-.24, 0, -.08), Vector3(.48, .15, .16))
const WALK_TICKS := 48
const EDITOR_STARTUP_FRAMES := 10

var _failed := false
var _report: Dictionary = {}


## Begin after the scene tree exists and resources can be loaded.
func _initialize() -> void:
	_run.call_deferred()


## Normalize owned scenes separately from standalone production movement checks.
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
	_check_mounting()
	_require(_report.has("linked_model_identity"), "Model checks did not complete")
	_require(_report.has("mounting"), "Mounting checks did not complete")
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
	print("CITY_MARINA_DOCKS_05_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Keep contract failures visible in both logs and the process exit code.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Roundtrip a saved wrapper without flattening its imported ancestry.
func _save_scene(path: String) -> void:
	var source: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE,
	)
	var instance: Node = source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_require(packed.pack(instance) == OK, "Pack failed")
	_require(ResourceSaver.save(packed, path) == OK, "Save failed")
	instance.free()


## Resolve every saved resource path and UID, including linked sibling mounting surfaces.
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


## Measure actual imported bounds, surfaces, identity transforms and visual-only status.
func _check_model() -> void:
	var packed: PackedScene = load(PREFAB)
	var instance: Node3D = packed.instantiate()
	var model: Node3D = instance.get_node("Visuals/Model")
	_require(model.transform == Transform3D.IDENTITY, "Corrective model transform")
	_require(model.scene_file_path == "res://art/models/environment/%s/%s.glb" % [ASSET, ASSET],
		"Unlinked model")
	_require(instance.find_children("*", "CollisionObject3D", true, false).is_empty(),
		"Mounted cleat must remain visual-only under the family contract")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_require(meshes.size() == 1, "Mesh count")
	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh.transform * mesh.mesh.get_aabb()
	_require(bounds.position.distance_to(EXPECTED_BOUNDS.position) < .001, "Bounds minimum")
	_require(bounds.size.distance_to(EXPECTED_BOUNDS.size) < .001, "Bounds size")
	_require(mesh.mesh.get_surface_count() == 2, "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparency")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	_report["bounds_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	instance.free()


## Assert each base rests inside the composite inset, away from the raised pale edge.
func _check_mounting() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	for node_name: String in ["MainCleat", "FingerCleatLeft", "FingerCleatRight"]:
		var cleat: Node3D = fixture.get_node(node_name)
		var bounds: AABB = cleat.transform * EXPECTED_BOUNDS
		_require(absf(bounds.position.y - .5) < .001, "Floating or sunken base")
		_require(absf(bounds.end.y - .65) < .001, "Mount height")
		var centre_x: float = -5.0 if node_name == "MainCleat" else 0.0
		var composite_half_width: float = 1.38 if node_name == "MainCleat" else .63
		_require(bounds.position.x > centre_x - composite_half_width, "Base outside inset")
		_require(bounds.end.x < centre_x + composite_half_width, "Base on raised trim")
		_require(absf(bounds.size.z - .48) < .001, "Horn must run along dock edge")

	_report["mounting"] = {
		"visual_only": true, "examples": 3, "base_height_m": .5,
		"top_height_m": .65, "finger_clear_space_between_base_plates_m": .90,
		"main_and_finger_composite_inset_margin_m": .02,
	}
	fixture.free()


## Verify the deck, not the hardware, owns support and compare production route traversals.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	for x: float in [-3.72, -.53, 0.0, .53]:
		var ray := PhysicsRayQueryParameters3D.create(Vector3(x, 1, 0), Vector3(x, 0, 0), 1)
		var hit: Dictionary = space.intersect_ray(ray)
		_require(not hit.is_empty(), "Missing mounting deck")
		if not hit.is_empty():
			_require(absf(hit["position"].y - .5) < .001, "Cleat changed deck collision")

	var results: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [
		ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY,
	]:
		results.append(await _walk_finger(fixture.get_node("Actor"), mode))

	_require(results[0].distance_to(Vector3(0, .501, 2)) < .01, "Walk helper incomplete")
	_require(results[0].is_equal_approx(results[1]), "Authority/replay mismatch")
	_report["physics"] = {
		"deck_support_rays": 4, "actor_motion_ticks_per_mode": WALK_TICKS,
		"authority_replay_equal": true,
		"end_position": [results[0].x, results[0].y, results[0].z],
		"network_transport_and_world_placement": "not tested",
	}
	fixture.free()


## Walk a production-size capsule between mounted cleats while preserving floor support.
func _walk_finger(actor: ActorMotion, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = Vector3(0, .501, -2)
	actor.apply_floor_snap()
	for tick: int in WALK_TICKS:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, Vector2(0, 1), 0.0, false, false,
		)
		_require(actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step rejected")
		_require(actor.test_move(actor.global_transform, Vector3(0, -.05, 0)), "No floor support")
		_require(absf(actor.position.y - .5) < .01, "Deck height changed")

	return actor.position
