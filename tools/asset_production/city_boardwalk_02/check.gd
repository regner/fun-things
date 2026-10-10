extends SceneTree
## Check linked bend resources, saved mating transforms and production movement across both joins.

const ASSET := "city_boardwalk_02"
const FIXTURE := "res://tools/asset_production/city_boardwalk_02/walk_check.tscn"
const EVIDENCE := "res://docs/assets/production/city_boardwalk_02-evidence/validation.json"
const SUFFIXES := ["", "_45", "_22p5"]
const ANGLES := [90.0, 45.0, 22.5]
const SEGMENTS := [32, 16, 8]
const EDITOR_STARTUP_FRAMES := 10
const WALK_SPEED_MPS := 5.0
const MAX_TICK_TRAVEL_M := 0.08
const RAY_EDGE_TOLERANCE_M := 0.0001

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
	var scenes: Array[String] = []
	for suffix: String in SUFFIXES:
		scenes.append("res://scenes/prefabs/environment/%s%s.tscn" % [ASSET, suffix])
	scenes.append(FIXTURE)
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
	for index: int in SUFFIXES.size():
		_check_model(scenes[index], index)
	_report["linked_models_checked"] = SUFFIXES.size()
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
	print("CITY_BOARDWALK_02_CHECK_PASS ", JSON.stringify(_report))


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


## Verify one identity-linked imported mesh, materials and the separate closed static slab.
func _check_model(path: String, index: int) -> void:
	var packed: PackedScene = load(path)
	var instance: Node3D = packed.instantiate()
	var model: Node3D = instance.get_node("Visuals/Model")
	var name: String = ASSET + SUFFIXES[index]
	_require(model.transform == Transform3D.IDENTITY, "Corrective model transform")
	_require(model.scene_file_path == "res://art/models/environment/%s/%s.glb" % [ASSET, name],
		"Unlinked model")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_require(meshes.size() == 1, "Mesh count")
	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh.transform * mesh.mesh.get_aabb()
	var expected: Array = _source["exports"][name]["actual_glb_aabb"]
	_require(bounds.position.distance_to(_vector(expected[0])) < .001, "Imported bounds min")
	_require(bounds.end.distance_to(_vector(expected[1])) < .001, "Imported bounds max")
	_require(mesh.mesh.get_surface_count() == 4, "Surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparent deck")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")

	_check_collision(instance, index)
	instance.free()


## Keep closed static collision independent from imported decorative timber seams.
func _check_collision(instance: Node3D, index: int) -> void:
	var body: StaticBody3D = instance.get_node("Collision/Body")
	var collider: CollisionShape3D = body.get_node("Deck")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Collision layers")
	_require(collider.shape is ConcavePolygonShape3D and not collider.disabled, "Static slab")
	_require(collider.transform == Transform3D.IDENTITY, "Collider placement")
	var shape: ConcavePolygonShape3D = collider.shape
	_require(shape.get_faces().size() == (SEGMENTS[index] * 8 + 4) * 3, "Collision face count")
	_require(not shape.backface_collision, "Slab must have outward-facing closed sides")


## Decode a recorded position into an engine vector for source-to-import comparison.
func _vector(values: Array) -> Vector3:
	return Vector3(values[0], values[1], values[2])


## Query edge/join support and traverse all angles in both directions and production step modes.
func _check_physics() -> void:
	var packed: PackedScene = load(FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var observations: Array[Dictionary] = []
	_report["support_rays"] = 0
	_report["outside_rays"] = 0
	_report["exact_edge_ray_misses"] = []
	for index: int in SUFFIXES.size():
		_check_support(fixture, index)
		for radius: float in [4.65, 6.0, 7.35]:
			for reverse: bool in [false, true]:
				observations.append(await _traverse(fixture, index, radius, reverse))
	_report["physics"] = {
		"support_and_outside_rays_pass": not _failed,
		"authority_replay_equal": not _failed,
		"traversals": observations,
		"actor_capsule_radius_m": .35, "actor_capsule_height_m": 1.8,
		"network_transport_vehicle_water_falloff": "not tested",
	}
	fixture.free()


## Sample continuous floor, clear annular void and both actual straight-to-bend connectors.
func _check_support(fixture: Node3D, index: int) -> void:
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	var origin := Vector3(index * 20, 0, 0)
	var angle: float = deg_to_rad(ANGLES[index])
	for radius: float in [4.3, 6.0, 7.7]:
		for sample: int in range(SEGMENTS[index] + 1):
			var theta: float = angle * sample / SEGMENTS[index]
			var position: Vector3 = origin + _arc_point(radius, theta)
			_require_floor_ray(space, position, true)
		var entry: Vector3 = origin + _arc_point(radius, 0)
		var exit_point: Vector3 = origin + _arc_point(radius, angle)
		var tangent := Vector3(sin(angle), 0, -cos(angle))
		for offset: float in [-.01, .01]:
			_require_floor_ray(space, entry + Vector3(0, 0, offset), true)
			_require_floor_ray(space, exit_point + tangent * offset, true)

	for radius: float in [4.0, 8.0]:
		_require_floor_ray(space, origin + _arc_point(radius, angle / 2), false)
	# Explicit inner void prevents an accidental convex hull from filling the elbow.
	_require_floor_ray(space, origin + Vector3(6, 0, 0), false)


## Require ray support on the exact datum, or an empty result outside the saved footprint.
func _require_floor_ray(
	space: PhysicsDirectSpaceState3D, position: Vector3, supported: bool
) -> void:
	var ray := PhysicsRayQueryParameters3D.create(
		position + Vector3.UP, position + Vector3.DOWN, 1
	)
	var hit: Dictionary = space.intersect_ray(ray)
	var counter: String = "support_rays" if supported else "outside_rays"
	_report[counter] += 1
	if supported and hit.is_empty():
		# Jolt can miss a ray exactly on a shared coplanar triangle edge. Do not
		# hide it: require four surrounding witnesses inside a 0.1 mm tolerance.
		_require_edge_witnesses(space, position)
		return

	_require(not hit.is_empty() == supported, "Unexpected floor support at " + str(position))
	if supported and not hit.is_empty():
		_require(absf(hit["position"].y) < .001, "Floor datum")
		_require(hit["normal"].dot(Vector3.UP) > .999, "Floor normal")


## Bound exact-edge ray precision without accepting geometric cracks or missing neighboring floor.
func _require_edge_witnesses(space: PhysicsDirectSpaceState3D, position: Vector3) -> void:
	_report["exact_edge_ray_misses"].append([position.x, position.y, position.z])
	for direction: Vector3 in [Vector3.LEFT, Vector3.RIGHT, Vector3.FORWARD, Vector3.BACK]:
		var witness: Vector3 = position + direction * RAY_EDGE_TOLERANCE_M
		var ray := PhysicsRayQueryParameters3D.create(  # gdstyle:ignore=quality/allocation-in-loop
			witness + Vector3.UP, witness + Vector3.DOWN, 1
		)
		var hit: Dictionary = space.intersect_ray(ray)
		_require(not hit.is_empty(), "Missing floor near triangle edge: " + str(witness))
		if not hit.is_empty():
			_require(absf(hit["position"].y) < .001, "Edge witness floor datum")
			_require(hit["normal"].dot(Vector3.UP) > .999, "Edge witness floor normal")


## Describe a nominal walking path independently from the collision tessellation.
func _arc_point(radius: float, angle: float) -> Vector3:
	return Vector3(6 - radius * cos(angle), 0, -radius * sin(angle))


## Test complete entry/bend/exit traversal at one lateral offset, including reverse left turns.
func _traverse(fixture: Node3D, index: int, radius: float, reverse: bool) -> Dictionary:
	var actor: ActorMotion = fixture.get_node("Actor")
	var origin := Vector3(index * 20, 0, 0)
	var angle: float = deg_to_rad(ANGLES[index])
	var points: Array[Vector3] = [origin + _arc_point(radius, 0) + Vector3(0, 0, 2)]
	for sample: int in range(SEGMENTS[index] + 1):
		points.append(origin + _arc_point(radius, angle * sample / SEGMENTS[index]))
	points.append(origin + _arc_point(radius, angle) + Vector3(sin(angle), 0, -cos(angle)) * 2)
	if reverse:
		points.reverse()
	var results: Array[Vector3] = []
	var ticks := 0
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		actor.position = points[0] + Vector3(0, .001, 0)
		actor.neutralize()
		actor.apply_floor_snap()
		ticks = 0
		for segment: int in range(1, points.size()):
			ticks += await _walk_segment(  # gdstyle:ignore=quality/await-in-loop
				actor, points[segment - 1], points[segment], ticks, mode
			)
		results.append(actor.position)

	_require(results[0].is_equal_approx(results[1]), "Authority/replay differs")
	return {
		"angle_degrees": ANGLES[index], "path_radius_m": radius, "reverse": reverse,
		"ticks_per_mode": ticks,
		"authority_end": [results[0].x, results[0].y, results[0].z],
		"replay_end": [results[1].x, results[1].y, results[1].z],
	}


## Execute precomputed intent rather than steering around collisions; assert every segment endpoint.
func _walk_segment(  # gdstyle:ignore=quality/max-parameters
	actor: ActorMotion, start: Vector3, end: Vector3, sequence: int, mode: ActorMotion.StepMode
) -> int:
	var delta: Vector3 = end - start
	var ticks: int = ceili(delta.length() / MAX_TICK_TRAVEL_M)
	var fixed_delta := 1.0 / Engine.physics_ticks_per_second
	var intent := Vector2(delta.x, delta.z) / (ticks * WALK_SPEED_MPS * fixed_delta)
	for tick: int in ticks:
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			sequence + tick + 1, sequence + tick, intent, 0.0, false, false
		)
		_require(actor.step(command, fixed_delta, mode), "Step rejected")
		_require(absf(actor.position.y) < .01, "Floor elevation changed")
		_require(actor.test_move(actor.global_transform, Vector3(0, -.05, 0)), "Lost support")
	_require(Vector2(actor.position.x - end.x, actor.position.z - end.z).length() < .002,
		"Traversal blocked: expected " + str(end) + " got " + str(actor.position))
	return ticks
