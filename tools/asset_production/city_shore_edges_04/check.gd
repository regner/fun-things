extends SceneTree
## Check six corner/end prefabs, matching sibling assemblies and production actor movement.

const ASSET := "city_shore_edges_04"
const FIXTURE := "res://tools/asset_production/city_shore_edges_04/physics_check.tscn"
const EVIDENCE := "res://docs/assets/production/city_shore_edges_04-evidence/validation.json"
const FAMILIES := ["wall", "quay", "rock"]
const WIDTHS := [.72, 1.2, 1.6]
const BOTTOMS := [0.0, -2.4, -.6]
const TOPS := [1.0, 0.0, .65]
const WALK_TICKS := 60
const EDITOR_STARTUP_FRAMES := 10
const PHYSICS_POSITION_TOLERANCE_M := .001
const COLLISION_SEAM_PADDING_M := .001
const CONTACT_TOLERANCE_M := .025
const SEAM_RAY_CASES := 30

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
		for path: String in _scene_paths():
			_save_scene(path)
			var first_hash: String = FileAccess.get_sha256(path)
			_save_scene(path)
			_require(first_hash == FileAccess.get_sha256(path), "Save/reload drift")

		_report["save_reload_byte_stable"] = true

	_check_dependencies(FIXTURE)
	for index: int in FAMILIES.size():
		for variant: String in ["corner", "end"]:
			_check_model(index, variant)

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
	print("CITY_SHORE_EDGES_04_CHECK_PASS ", JSON.stringify(_report))
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


## List authored wrappers and their saved assembly without inventing a runtime hierarchy.
func _scene_paths() -> Array[String]:
	var paths: Array[String] = [FIXTURE]
	for family: String in FAMILIES:
		for variant: String in ["corner", "end"]:
			paths.append(_prefab_path(family, variant))

	return paths


## Resolve the stable variant wrapper name.
func _prefab_path(family: String, variant: String) -> String:
	return "res://scenes/prefabs/environment/%s_%s_%s.tscn" % [ASSET, family, variant]


## Assert linked geometry, literal family bounds and intentionally separate collision.
func _check_model(index: int, variant: String) -> void:
	var instance: Node3D = load(_prefab_path(FAMILIES[index], variant)).instantiate()
	var model: Node3D = instance.get_node("Visuals/Model")
	var glb := "res://art/models/environment/%s/%s_%s_%s.glb" % [
		ASSET, ASSET, FAMILIES[index], variant,
	]
	_require(model.transform == Transform3D.IDENTITY, "Corrective model transform")
	_require(model.scene_file_path == glb, "Unlinked model")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_require(meshes.size() == 1, "Mesh count")
	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh.transform * mesh.mesh.get_aabb()
	var half: float = WIDTHS[index] / 2.0
	var low := Vector3(-2, BOTTOMS[index], -2)
	var high := Vector3(half, TOPS[index], half)
	if variant == "end":
		low = Vector3(-.5, BOTTOMS[index], -half)
		high = Vector3(.5, TOPS[index], half)

	_require(bounds.position.distance_to(low) < .001, "Bounds minimum")
	_require(bounds.end.distance_to(high) < .001, "Bounds maximum")
	_require(mesh.mesh.get_surface_count() == (2 if index == 2 else 4), "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparency")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	_check_collision(instance, index, variant)
	_report["linked_model_identity"] = true
	_report[FAMILIES[index] + "_" + variant] = {
		"bounds_min": [low.x, low.y, low.z], "bounds_max": [high.x, high.y, high.z],
		"static_bodies": 1, "box_shapes": 2 if variant == "corner" else 1,
	}
	instance.free()


## Check L-arm boxes; 1 mm overlap at the outgoing seam prevents floating-point query cracks.
func _check_collision(instance: Node3D, index: int, variant: String) -> void:
	var body: StaticBody3D = instance.get_node("Collision/Body")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Collision filters")
	var width: float = WIDTHS[index]
	var height: float = TOPS[index] - BOTTOMS[index]
	var middle: float = (TOPS[index] + BOTTOMS[index]) / 2.0
	var sizes: Array[Vector3] = [Vector3(1, height, width)]
	var positions: Array[Vector3] = [Vector3(0, middle, 0)]
	if variant == "corner":
		sizes = [Vector3(2 + width / 2, height, width),
			Vector3(width, height, 2 - width / 2 + 2 * COLLISION_SEAM_PADDING_M)]
		positions = [Vector3(-1 + width / 4, middle, 0), Vector3(0, middle, -1 - width / 4)]

	_require(body.get_child_count() == sizes.size(), "Shape count")
	for index_shape: int in sizes.size():
		var shape: CollisionShape3D = body.get_child(index_shape) as CollisionShape3D
		_require(shape.shape is BoxShape3D, "Non-box collider")
		_require(shape.shape.size.is_equal_approx(sizes[index_shape]), "Box dimensions")
		_require(shape.position.is_equal_approx(positions[index_shape]), "Box datum")


## Query three real straight/corner/end joins per family and clear space above them.
func _check_rays(fixture: Node3D) -> int:
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	for index: int in FAMILIES.size():
		var offset := Vector3(index * 12, 0, 0)
		var height: float = (BOTTOMS[index] + TOPS[index]) / 2.0
		for delta: float in [-.001, 0.0, .001]:
			for seam: int in 3:
				var start := Vector3(-2 + delta, height, 2)
				var end := Vector3(-2 + delta, height, -2)
				if seam > 0:
					var z: float = (-2.0 if seam == 1 else -6.0) + delta
					start = Vector3(2, height, z)
					end = Vector3(-2, height, z)

				var hit := _ray(space, offset + start, offset + end)
				_require(
					not hit.is_empty(),
					"Gap %s seam %d delta %f" % [FAMILIES[index], seam, delta],
				)
				if not hit.is_empty():
					var contact: Vector3 = hit["position"] - offset
					var plane: float = contact.z if seam == 0 else contact.x
					_require(absf(plane - WIDTHS[index] / 2) < .001, "Contact plane")

		var above := Vector3(0, TOPS[index] + .1, 0)
		_require(_ray(space, offset + above + Vector3(-4, 0, 2),
			offset + above + Vector3(-4, 0, -2)).is_empty(), "Unwanted overhead barrier")

	return SEAM_RAY_CASES + _check_walk_surface(space)


## Confirm uninterrupted flush quay walking across incoming, mitre, outgoing and terminal joins.
func _check_walk_surface(space: PhysicsDirectSpaceState3D) -> int:
	var positions: Array[Vector3] = [
		Vector3(8, 0, 0), Vector3(10, 0, 0), Vector3(12, 0, 0),
		Vector3(12, 0, -2), Vector3(12, 0, -4), Vector3(12, 0, -6),
		Vector3(12, 0, -6.9),
	]
	for position: Vector3 in positions:
		var hit := _ray(space, position + Vector3.UP, position + Vector3.DOWN)
		_require(not hit.is_empty(), "Quay walking gap at %s" % position)
		if not hit.is_empty():
			_require(absf(hit["position"].y) < .001, "Quay walking datum")

	return positions.size()


## Query production collision without test-visible geometry or broad filtering.
func _ray(space: PhysicsDirectSpaceState3D, start: Vector3, end: Vector3) -> Dictionary:
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(start, end, 1))


## Compare public movement outcomes in authority and replay on the saved three-family assembly.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var rays: int = _check_rays(fixture)
	var cases: Array[Dictionary] = _movement_cases()
	var results: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		for test: Dictionary in cases:
			var result: Vector3 = await _walk(  # gdstyle:ignore=quality/await-in-loop
				fixture.get_node("Actor"), test, mode,
			)
			results.append(result)
			_require(
				result.distance_to(test["expected"]) < CONTACT_TOLERANCE_M,
				"Movement: " + test["name"],
			)

	var error := 0.0
	for index: int in cases.size():
		error = maxf(error, results[index].distance_to(results[index + cases.size()]))

	_require(error < PHYSICS_POSITION_TOLERANCE_M, "Authority/replay mismatch")
	_report["physics"] = {
		"ray_cases": rays, "actor_radius_m": .35, "actor_height_m": 1.8,
		"movement_cases": results.size(), "positions": results,
		"max_authority_replay_error_m": error, "authority_replay_within_tolerance": true,
		"network_transport_and_world_placement": "not tested",
	}
	print("MOVEMENT_RESULTS ", results)
	fixture.free()


## Define independent contact/clearance expectations for barriers and the flush quay.
func _movement_cases() -> Array[Dictionary]:
	var cases: Array[Dictionary] = []
	for index: int in [0, 2]:
		var offset := Vector3(index * 12, .001, 0)
		var stop: float = .711 if index == 0 else 1.151
		cases.append({"name": FAMILIES[index] + " incoming seam", "ticks": WALK_TICKS,
			"start": offset + Vector3(-2, 0, 2), "direction": Vector2(0, -1),
			"expected": offset + Vector3(-2, 0, stop)})
		cases.append({"name": FAMILIES[index] + " terminal nose", "ticks": WALK_TICKS,
			"start": offset + Vector3(0, 0, -8), "direction": Vector2(0, 1),
			"expected": offset + Vector3(0, 0, -7.351)})
		cases.append({"name": FAMILIES[index] + " clear bypass", "ticks": WALK_TICKS,
			"start": offset + Vector3(-6.5, 0, 2), "direction": Vector2(0, -1),
			"expected": offset + Vector3(-6.5, 0, -3)})

	cases.append({"name": "quay incoming to mitre", "ticks": 48,
		"start": Vector3(8, .001, 0), "direction": Vector2(1, 0),
		"expected": Vector3(12, .001, 0)})
	cases.append({"name": "quay mitre to terminal", "ticks": 78,
		"start": Vector3(12, .001, 0), "direction": Vector2(0, -1),
		"expected": Vector3(12, .001, -6.5)})

	return cases


## Apply real FootCommand inputs to the production actor on each physics tick.
func _walk(actor: ActorMotion, test: Dictionary, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = test["start"]
	actor.neutralize()
	for tick: int in test["ticks"]:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, test["direction"], 0.0, false, false,
		)
		_require(actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step rejected")

	return actor.position
