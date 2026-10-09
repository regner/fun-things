extends SceneTree
## Validate linked pontoon resources, saved identities, support and production movement seams.

const ASSET := "city_marina_docks_02"
const PREFAB := "res://scenes/prefabs/environment/city_marina_docks_02.tscn"
const FIXTURE := "res://tools/asset_production/city_marina_docks_02/walk_check.tscn"
const EVIDENCE := "res://docs/assets/production/city_marina_docks_02-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-.75, -0.3, -3), Vector3(1.5, 0.82, 6))
const SEAM_TICKS := 48
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
	print("CITY_MARINA_DOCKS_02_CHECK_PASS ", JSON.stringify(_report))
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
	_require(collider.shape is BoxShape3D and not collider.disabled, "Deck shape")
	_require(collider.shape.size.is_equal_approx(Vector3(1.5, .16, 6)), "Deck envelope")
	_require(collider.position.is_equal_approx(Vector3(0, .42, 0)), "Deck top datum")
	_report["bounds_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	instance.free()


## Query both butt interfaces and exercise the production actor across each saved seam.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	for x: float in [0.0, 1.49, 1.5, 1.51, 4.5, 7.49, 7.5, 7.51, 10.5, 13.4]:
		var ray := PhysicsRayQueryParameters3D.create(Vector3(x, 2, 0), Vector3(x, -1, 0), 1)
		var hit: Dictionary = space.intersect_ray(ray)
		_require(not hit.is_empty(), "Missing support")
		if not hit.is_empty():
			_require(absf(hit["position"].y - .5) < .001, "Support height")

	for z: float in [-.85, .85]:
		var clear := PhysicsRayQueryParameters3D.create(Vector3(4.5, 2, z), Vector3(4.5, -1, z), 1)
		_require(space.intersect_ray(clear).is_empty(), "Outside finger edge must be clear")

	var actor: ActorMotion = fixture.get_node("Actor")
	var traversals: Array[Dictionary] = []
	# 0 -> 4 crosses main side/finger end; 6 -> 10 crosses finger/finger end join.
	for start_x: float in [0.0, 6.0]:
		var results: Array[Vector3] = []
		for mode: ActorMotion.StepMode in [
			ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY,
		]:
			results.append(await _cross_seam(actor, start_x, mode))

		_require(results[0].is_equal_approx(results[1]), "Authority/replay differs")
		traversals.append({
			"start_x": start_x,
			"end_position": [results[0].x, results[0].y, results[0].z],
		})

	_report["physics"] = {
		"deck_support_rays": 10, "outside_edge_clear_rays": 2,
		"actor_motion_seam_ticks_per_mode": SEAM_TICKS,
		"authority_replay_equal": true, "traversals": traversals,
		"water_falloff_and_network_transport": "not tested; outside component scope",
	}
	fixture.free()


## Move four metres across one seam and assert destination support in either simulation mode.
func _cross_seam(actor: ActorMotion, start_x: float, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = Vector3(start_x, .501, 0)
	actor.apply_floor_snap()
	for tick: int in SEAM_TICKS:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, Vector2(1, 0), 0.0, false, false
		)
		_require(
			actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode),
			"Step rejected",
		)

	_require(absf(actor.position.x - (start_x + 4.0)) < .01, "Seam traversal blocked")
	_require(absf(actor.position.y - .5) < .01, "Deck elevation changed")
	_require(absf(actor.position.z) < .001, "Unexpected lateral movement")
	_require(actor.test_move(actor.global_transform, Vector3(0, -.05, 0)), "No floor support")
	return actor.position
