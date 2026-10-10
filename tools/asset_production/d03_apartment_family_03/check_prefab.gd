@tool
extends SceneTree

const PREFAB: String = "res://scenes/prefabs/environment/d03_apartment_family_03.tscn"
const OUTPUT: String = "C:/tmp/ft/assets/d03_apartment_family_03/prefab-check.json"
const TOLERANCE_M: float = 0.001
const CONTACT_TOLERANCE_M: float = 0.025
const WORLD_LAYER: int = 1
const ACTOR_RADIUS_M: float = 0.35
const ACTOR_HEIGHT_M: float = 1.8
const TEST_TICKS: int = 60

var _failures: Array[String] = []
var _result: Dictionary = {}


## Start after the isolated SceneTree is ready.
func _initialize() -> void:
	_run.call_deferred()


## Retain every failed expectation and fail the process.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Serialize vector values without engine-specific JSON strings.
func _vector(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]


## Pack only the owned assembly; inherited dependencies remain linked and unmodified.
func _save_wrapper() -> void:
	var packed: PackedScene = ResourceLoader.load(
		PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	_expect(packed != null, "Assembly and dependencies load")
	var instance: Node = packed.instantiate()
	var saved: PackedScene = PackedScene.new()
	_expect(saved.pack(instance) == OK, "Pack assembly")
	_expect(ResourceSaver.save(saved, PREFAB) == OK, "Save assembly")
	instance.free()


## Require two byte-stable reload/save cycles including node identities and resource UIDs.
func _roundtrip() -> void:
	_save_wrapper()
	var first: String = FileAccess.get_sha256(PREFAB)
	_save_wrapper()
	var second: String = FileAccess.get_sha256(PREFAB)
	_save_wrapper()
	var third: String = FileAccess.get_sha256(PREFAB)
	_expect(first == second and second == third, "Two byte-stable reload/save cycles")
	_result["normalized_sha256"] = first
	_result["byte_stable"] = first == second and second == third
	_result["stable_reload_count"] = 2


## Inspect real imported visuals and emit render placements derived from this saved scene only.
func _inspect(instance: Node3D) -> void:
	_expect(instance.transform == Transform3D.IDENTITY, "Assembly ground datum")
	_expect(instance.get_child_count() == 16, "Sixteen linked component placements")
	var placements: Array[Dictionary] = []
	for child: Node in instance.get_children():
		var item: Node3D = child as Node3D
		_expect(item != null and not item.scene_file_path.is_empty(), "Existing prefab instance")
		_expect(item.scale.is_equal_approx(Vector3.ONE), "No stretched component")
		_expect(absf(item.rotation.x) + absf(item.rotation.z) < TOLERANCE_M, "Yaw only")
		placements.append({ "name": item.name, "prefab": item.scene_file_path,
			"position": _vector(item.position), "yaw_degrees": rad_to_deg(item.rotation.y) })

	_result["placements"] = placements
	_measure_visuals(instance)
	_measure_collision(instance)
	var uid: int = ResourceLoader.get_resource_uid(PREFAB)
	_expect(uid != ResourceUID.INVALID_ID, "Assembly UID resolves")
	_result["prefab_uid"] = ResourceUID.id_to_text(uid)


## Require imported mesh ancestry and measure the complete assembled envelope without copies.
func _measure_visuals(instance: Node3D) -> void:
	var meshes: Array[Node] = instance.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 16, "Sixteen inherited meshes")
	var bounds: AABB
	var surfaces: int = 0
	var models: Array[Dictionary] = []
	for index: int in range(meshes.size()):
		var mesh: MeshInstance3D = meshes[index] as MeshInstance3D
		var model: Node3D = mesh.get_parent() as Node3D
		while model != instance and not model.scene_file_path.ends_with(".glb"):
			model = model.get_parent() as Node3D

		_expect(model.scene_file_path.ends_with(".glb"), "Original imported model ancestry")
		_expect(model.transform == Transform3D.IDENTITY, "Identity Visuals/Model")
		_expect(mesh.mesh.resource_path.begins_with(model.scene_file_path), "Linked mesh resource")
		_expect(mesh.material_override == null, "No material replacement")
		var part: AABB = mesh.global_transform * mesh.get_aabb()
		bounds = part if index == 0 else bounds.merge(part)
		surfaces += mesh.mesh.get_surface_count()
		models.append({ "path": model.scene_file_path,
			"position": _vector(model.global_position),
			"yaw_degrees": rad_to_deg(model.global_rotation.y) })

	_expect(bounds.position.distance_to(Vector3(-9.34, 0, -7.5)) < TOLERANCE_M, "Visual min")
	_expect(bounds.end.distance_to(Vector3(9.34, 6.72, 6.18)) < TOLERANCE_M, "Visual max")
	_result["models"] = models
	_result["mesh_count"] = meshes.size()
	_result["surface_count"] = surfaces
	_result["aabb_min"] = _vector(bounds.position)
	_result["aabb_max"] = _vector(bounds.end)


## Inherited simple boxes own all solids; no assembly-wide or decorative blockers are added.
func _measure_collision(instance: Node3D) -> void:
	var shapes: Array[Node] = instance.find_children("*", "CollisionShape3D", true, false)
	_expect(shapes.size() == 10, "Ten inherited core and closure boxes")
	var bounds: Array[Dictionary] = []
	for node: Node in shapes:
		var shape: CollisionShape3D = node as CollisionShape3D
		var box: BoxShape3D = shape.shape as BoxShape3D
		_expect(box != null and not shape.disabled, "Enabled simple inherited box")
		var body: StaticBody3D = shape.get_parent() as StaticBody3D
		_expect(body != null, "Static sibling collision")
		_expect(body.collision_layer == WORLD_LAYER and body.collision_mask == 0, "World-only")
		var area: AABB = shape.global_transform * AABB(-box.size / 2.0, box.size)
		bounds.append({ "path": str(instance.get_path_to(shape)),
			"min": _vector(area.position), "max": _vector(area.end) })

	_result["collision_boxes"] = bounds


## Probe solid facade seams and unobstructed infill side links through the actual physics world.
func _queries(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = ACTOR_RADIUS_M
	capsule.height = ACTOR_HEIGHT_M
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = WORLD_LAYER
	var observations: Array[Dictionary] = []
	var cases: Array[Vector4] = [
		Vector4(-13, 0.9, 0, 0), Vector4(13, 0.9, 0, 0), Vector4(0, 0.9, -10, 0),
		Vector4(0, 0.9, 8, 0), Vector4(6, 0.9, -6.8, 0), Vector4(0, 0.9, 0, 1),
		Vector4(-3, 0.9, 0, 1), Vector4(3, 0.9, 0, 1), Vector4(-0.9, 0.9, -5.9, 1),
		Vector4(-9.2, 0.9, 0, 1), Vector4(9.2, 0.9, 0, 1),
		Vector4(-9.8, 0.9, 0, 0), Vector4(9.8, 0.9, 0, 0),
	]
	for test: Vector4 in cases:
		query.transform.origin = Vector3(test.x, test.y, test.z)
		var solid: bool = not space.intersect_shape(query).is_empty()
		_expect(solid == bool(test.w), "Capsule solid/clear expectation")
		observations.append({ "position": [test.x, test.y, test.z], "solid": solid })

	_result["capsule_queries"] = observations
	_seam_rays(space)
	_open_corridors(space, query)


## Check connector/end/stack seams and the both finished-end datums independently.
func _seam_rays(space: PhysicsDirectSpaceState3D) -> void:
	var samples: Array[Array] = [
		[Vector3(-3, 1.5, -10), Vector3(-3, 1.5, 0), Vector3(-3, 1.5, -6)],
		[Vector3(3, 1.5, -10), Vector3(3, 1.5, 0), Vector3(3, 1.5, -6)],
		[Vector3(-3, 1.5, 10), Vector3(-3, 1.5, 0), Vector3(-3, 1.5, 6)],
		[Vector3(3, 1.5, 10), Vector3(3, 1.5, 0), Vector3(3, 1.5, 6)],
		[Vector3(-8.999, 1.5, -10), Vector3(-8.999, 1.5, 0), Vector3(-8.999, 1.5, -6)],
		[Vector3(-9.001, 1.5, -10), Vector3(-9.001, 1.5, 0), Vector3(-9.001, 1.5, -6)],
		[Vector3(8.999, 1.5, -10), Vector3(8.999, 1.5, 0), Vector3(8.999, 1.5, -6)],
		[Vector3(9.001, 1.5, -10), Vector3(9.001, 1.5, 0), Vector3(9.001, 1.5, -6)],
		[Vector3(0, 3.2, -10), Vector3(0, 3.2, 0), Vector3(0, 3.2, -6)],
		[Vector3(-12, 3.2, 0), Vector3(0, 3.2, 0), Vector3(-9.24, 3.2, 0)],
		[Vector3(12, 3.2, 0), Vector3(0, 3.2, 0), Vector3(9.24, 3.2, 0)],
	]
	var hits: Array[Array] = []
	for sample: Array in samples:
		var ray := PhysicsRayQueryParameters3D.create(  # gdstyle:ignore=quality/allocation-in-loop
			sample[0], sample[1], WORLD_LAYER)
		var hit: Dictionary = space.intersect_ray(ray)
		_expect(not hit.is_empty(), "Seam remains solid")
		if not hit.is_empty():
			_expect(hit["position"].distance_to(sample[2]) < TOLERANCE_M, "Exact seam datum")
			hits.append(_vector(hit["position"]))

	_result["seam_ray_hits"] = hits


## Sample two unroofed links and sweep a car-sized box along the east side.
func _open_corridors(
	space: PhysicsDirectSpaceState3D,
	query: PhysicsShapeQueryParameters3D,
) -> void:
	var clear_rays: int = 0
	for offset: int in range(25):
		var point: Vector3 = Vector3(-13, 0.05, -12 + offset)
		var ray := PhysicsRayQueryParameters3D.create(  # gdstyle:ignore=quality/allocation-in-loop
			point, point + Vector3.UP * 20, WORLD_LAYER)
		_expect(space.intersect_ray(ray).is_empty(), "West link unblocked above ground")
		point = Vector3(13, 0.05, -12 + offset)
		ray.from = point
		ray.to = point + Vector3.UP * 20
		_expect(space.intersect_ray(ray).is_empty(), "East link unblocked above ground")
		clear_rays += 2

	var box: BoxShape3D = BoxShape3D.new()
	box.size = Vector3(1.9, 1.5, 4.3)
	query.shape = box
	query.transform = Transform3D(Basis.IDENTITY, Vector3(13, 0.75, -10))
	query.motion = Vector3(0, 0, 20)
	var sweep: PackedFloat32Array = space.cast_motion(query)
	_expect(sweep[0] == 1.0 and sweep[1] == 1.0, "Car-sized side bypass sweep clear")
	_result["open_link_vertical_rays"] = clear_rays
	_result["side_car_sweep"] = [sweep[0], sweep[1]]


## Wait for the private headless editor's scan before serializing resource identities.
func _wait_for_scan() -> void:
	if not Engine.is_editor_hint():
		return

	await create_timer(3.0).timeout
	while EditorInterface.get_resource_filesystem().is_scanning():
		await create_timer(1.0).timeout  # gdstyle:ignore=quality/await-in-loop


## Separate editor serialization from clean runtime geometry and production motion checks.
func _run() -> void:
	await _wait_for_scan()
	var normalize: bool = OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		if not Engine.is_editor_hint():
			push_error("Normalization requires --editor to retain UIDs")
			quit(1)
			return

		_roundtrip()
	else:
		var instance: Node3D = (load(PREFAB) as PackedScene).instantiate() as Node3D
		root.add_child(instance)
		_inspect(instance)
		await physics_frame
		await physics_frame
		_queries(instance)
		await _motion_checks()
		instance.free()
		_result["roundtrip"] = JSON.parse_string(
			FileAccess.get_file_as_string(OUTPUT + ".roundtrip"))

	_result["engine"] = Engine.get_version_info()["string"]
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var file: FileAccess = FileAccess.open(OUTPUT + ".roundtrip" if normalize else OUTPUT,
		FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	await _wait_for_scan()
	quit(0 if _failures.is_empty() else 1)


## Add only a physics test floor, never generated visible content or a prefab dependency.
func _add_test_floor() -> StaticBody3D:
	var body: StaticBody3D = StaticBody3D.new()
	var shape: CollisionShape3D = CollisionShape3D.new()
	var box: BoxShape3D = BoxShape3D.new()
	box.size = Vector3(100, 0.2, 100)
	shape.shape = box
	shape.position.y = -0.1
	body.add_child(shape)
	root.add_child(body)
	return body


## Provide independent expected positions for seam crossing and the closed front stop.
func _motion_cases() -> Array[Dictionary]:
	return [
		{ "name": "west_cross_link", "start": Vector3(-13, 0, -2),
			"move": Vector2.DOWN, "end": Vector3(-13, 0, 3) },
		{ "name": "east_cross_link", "start": Vector3(13, 0, -2),
			"move": Vector2.DOWN, "end": Vector3(13, 0, 3) },
		{ "name": "front_seam_below_balcony", "start": Vector3(1, 0, -6.8),
			"move": Vector2.RIGHT, "end": Vector3(6, 0, -6.8) },
		{ "name": "closed_entry_stop", "start": Vector3(-0.9, 0, -9),
			"move": Vector2.DOWN, "end": Vector3(-0.9, 0, -6.35) },
	]


## Exercise production ActorMotion in authority/replay modes against actual linked colliders.
func _motion_checks() -> void:
	var floor_body: StaticBody3D = _add_test_floor()
	var observations: Array[Dictionary] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		for test: Dictionary in _motion_cases():
			var actor := ActorMotion.new()  # gdstyle:ignore=quality/allocation-in-loop
			var shape := CollisionShape3D.new()  # gdstyle:ignore=quality/allocation-in-loop
			var capsule := CapsuleShape3D.new()  # gdstyle:ignore=quality/allocation-in-loop
			capsule.radius = ACTOR_RADIUS_M
			capsule.height = ACTOR_HEIGHT_M
			shape.shape = capsule
			shape.position.y = ACTOR_HEIGHT_M / 2.0
			actor.add_child(shape)
			actor.position = test["start"]
			actor.collision_layer = 0
			actor.collision_mask = WORLD_LAYER
			root.add_child(actor)
			await physics_frame  # gdstyle:ignore=quality/await-in-loop
			for tick: int in range(TEST_TICKS):
				var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
					tick + 1, tick, test["move"], 0, false, false)
				_expect(actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Step")
				await physics_frame  # gdstyle:ignore=quality/await-in-loop

			_expect(actor.position.distance_to(test["end"]) < CONTACT_TOLERANCE_M, test["name"])
			observations.append({ "case": test["name"], "mode": mode,
				"end": [actor.position.x, actor.position.y, actor.position.z] })
			actor.free()

	_result["production_actor_motion"] = observations
	for index: int in range(4):
		_expect(observations[index]["end"] == observations[index + 4]["end"], "Mode equivalence")

	floor_body.free()
