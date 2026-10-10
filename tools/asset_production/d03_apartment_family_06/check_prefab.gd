@tool
extends SceneTree

const PREFIX: String = "res://scenes/prefabs/environment/d03_apartment_family_06_"
const MODEL_PREFIX: String = (
	"res://art/models/environment/d03_apartment_family_06/d03_apartment_family_06_"
)
const STRAIGHT_PATH: String = "res://scenes/prefabs/environment/d03_apartment_family_05.tscn"
const OUTPUT: String = "C:/tmp/ft/assets/d03_apartment_family_06/prefab-check.json"
const TOLERANCE_M: float = 0.001
const CONTACT_TOLERANCE_M: float = 0.025
const ACTOR_RADIUS_M: float = 0.35
const ACTOR_HEIGHT_M: float = 1.8
const WORLD_LAYER: int = 1
const TEST_TICKS: int = 60

var _failures: Array[String] = []
var _result: Dictionary = {}
var _variant: String = ""


## Defer until the isolated scene tree can load imported resources.
func _initialize() -> void:
	_run.call_deferred()


## Record every failed expectation and keep the process exit meaningful.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(_variant + ": " + message)
		push_error(_variant + ": " + message)


## Normalize only the two owned wrappers and prove a second save has identical bytes.
func _roundtrip() -> void:
	for variant: String in ["outside", "inside"]:
		var path: String = PREFIX + variant + ".tscn"
		var hashes: Array[String] = []
		for pass_index: int in range(2):
			var packed: PackedScene = ResourceLoader.load(
				path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
			) as PackedScene
			_expect(packed != null, "Load for normalization")
			var instance: Node = packed.instantiate()
			var saved := PackedScene.new()  # gdstyle:ignore=quality/allocation-in-loop
			_expect(saved.pack(instance) == OK, "Pack wrapper")
			_expect(ResourceSaver.save(saved, path) == OK, "Save wrapper")
			instance.free()
			hashes.append(FileAccess.get_sha256(path))

		_expect(hashes[0] == hashes[1], "Second save byte stability")
		_result[variant] = { "normalized_sha256": hashes[1], "byte_stable": hashes[0] == hashes[1] }


## Check the imported mesh, exact solid boxes, family materials, and saved UIDs.
func _inspect(instance: Node3D, edge: float) -> void:
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	var model_path: String = MODEL_PREFIX + _variant + ".glb"
	_expect(model.scene_file_path == model_path, "Linked imported model")
	_expect(model.transform == Transform3D.IDENTITY, "Identity model transform")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "One imported mesh")
	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh.global_transform * mesh.get_aabb()
	var expected: AABB = AABB(Vector3(-edge - 0.18, 0, -edge - 0.18),
		Vector3(edge * 2 + 0.18, 3.2, edge * 2 + 0.18))
	_expect(bounds.position.distance_to(expected.position) < TOLERANCE_M, "Bounds min")
	_expect(bounds.size.distance_to(expected.size) < TOLERANCE_M, "Bounds size")
	_expect(mesh.mesh.resource_path.begins_with(model_path), "No copied mesh")
	_expect(mesh.mesh.get_surface_count() == 5, "Five opaque surfaces")
	_materials(mesh)
	var body: StaticBody3D = instance.get_node("Collision/Body") as StaticBody3D
	_expect(body.collision_layer == WORLD_LAYER and body.collision_mask == 0, "World layer/mask")
	if _variant == "outside":
		_expect(body.get_child_count() == 1, "One outside collider")
		_box(body.get_node("Core"), Vector3(12, 3.2, 12), Vector3(0, 1.6, 0))
	else:
		_expect(body.get_child_count() == 2, "Two nonoverlapping inside collider boxes")
		_box(body.get_node("NorthWing"), Vector3(18, 3.2, 12), Vector3(0, 1.6, -3))
		_box(body.get_node("WestReturn"), Vector3(12, 3.2, 6), Vector3(-3, 1.6, 6))

	var prefab_uid: int = ResourceLoader.get_resource_uid(PREFIX + _variant + ".tscn")
	var model_uid: int = ResourceLoader.get_resource_uid(model_path)
	_expect(prefab_uid != ResourceUID.INVALID_ID, "Wrapper UID")
	_expect(model_uid != ResourceUID.INVALID_ID, "Model UID")
	_result[_variant] = { "bounds_min": [bounds.position.x, bounds.position.y, bounds.position.z],
		"bounds_size": [bounds.size.x, bounds.size.y, bounds.size.z],
		"collider_count": body.get_child_count(), "family_materials_match": true,
		"prefab_uid": ResourceUID.id_to_text(prefab_uid),
		"model_uid": ResourceUID.id_to_text(model_uid), "linked_model_identity": true }


## Compare imported slot names and PBR values to the already-delivered straight bay.
func _materials(mesh: MeshInstance3D) -> void:
	var sibling: Node = (load(STRAIGHT_PATH) as PackedScene).instantiate()
	var sibling_mesh: MeshInstance3D = sibling.get_node("Visuals/Model").find_children(
		"*", "MeshInstance3D", true, false)[0] as MeshInstance3D
	for index: int in range(5):
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(index) as BaseMaterial3D
		_expect(material != null, "Material dependency")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque material")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Backface culling")
		if index < 4:
			var original: BaseMaterial3D = (
				sibling_mesh.mesh.surface_get_material(index) as BaseMaterial3D
			)
			_expect(material.resource_name == original.resource_name, "Family slot names")
			_expect(material.albedo_color == original.albedo_color, "Family color matching")
			_expect(material.roughness == original.roughness, "Family roughness matching")
			_expect(material.metallic == original.metallic, "Family metallic matching")

	sibling.free()


## Compare explicit collision dimensions independently of visible geometry.
func _box(node: CollisionShape3D, size: Vector3, position: Vector3) -> void:
	_expect(node.shape is BoxShape3D, "Simple box collision")
	_expect((node.shape as BoxShape3D).size == size, "Box size")
	_expect(node.position == position, "Box ground/footprint datum")


## Test the free court and each solid return, including the internal two-box seam.
func _queries(instance: Node3D, edge: float) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = ACTOR_RADIUS_M
	capsule.height = ACTOR_HEIGHT_M
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = WORLD_LAYER
	var cases: Array[Dictionary] = [
		{ "point": Vector3(0, 0.9, 0), "solid": true },
		{ "point": Vector3(0, 0.9, -edge + 0.1), "solid": true },
		{ "point": Vector3(-edge + 0.1, 0.9, 0), "solid": true },
		{ "point": Vector3(0, 0.9, -edge - 0.6), "solid": false },
		{ "point": Vector3(-edge - 0.6, 0.9, 0), "solid": false },
		{ "point": Vector3(edge + 0.6, 0.9, 0), "solid": false },
	]
	if _variant == "inside":
		cases.append_array([
			{ "point": Vector3(6, 0.9, 6), "solid": false },
			{ "point": Vector3(3.6, 0.9, 3.6), "solid": false },
			{ "point": Vector3(3.1, 0.9, 6), "solid": true },
			{ "point": Vector3(6, 0.9, 3.1), "solid": true },
			{ "point": Vector3(-8.9, 0.9, 3), "solid": true },
		])

	var observations: Array[Dictionary] = []
	for test: Dictionary in cases:
		query.transform.origin = test["point"]
		var solid: bool = not space.intersect_shape(query).is_empty()
		_expect(solid == test["solid"], "Capsule solid/clear at " + str(test["point"]))
		var point: Vector3 = test["point"]
		observations.append({ "point": [point.x, point.y, point.z], "solid": solid })

	_result[_variant]["capsule_queries"] = observations


## Probe both perpendicular straight-bay joins and the stacked corner through real prefabs.
func _joins(instance: Node3D, edge: float) -> void:
	var straight: PackedScene = load(STRAIGHT_PATH) as PackedScene
	var east: Node3D = straight.instantiate() as Node3D
	var south: Node3D = straight.instantiate() as Node3D
	var upper: Node3D = (load(PREFIX + _variant + ".tscn") as PackedScene).instantiate() as Node3D
	var offset: float = 0 if _variant == "outside" else -3
	east.position = Vector3(edge + 3, 0, offset)
	south.position = Vector3(offset, 0, edge + 3)
	south.rotation.y = PI / 2
	upper.position.y = 3.2
	root.add_child(east)
	root.add_child(south)
	root.add_child(upper)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var probes: Array[Vector3] = [Vector3(edge, 1, -edge - 2),
		Vector3(-edge - 2, 1, edge), Vector3(0, 3.2, -edge - 2)]
	if _variant == "inside":
		probes.append(Vector3(-edge - 2, 1, 3))

	_seam_rays(space, probes, edge)
	east.free()
	south.free()
	upper.free()


## Ray-test explicit seam coordinates without deriving collision from render meshes.
func _seam_rays(
	space: PhysicsDirectSpaceState3D, probes: Array[Vector3], edge: float
) -> void:
	var observations: Array[Dictionary] = []
	for point: Vector3 in probes:
		var direction: Vector3 = Vector3.RIGHT if point.x < -edge else Vector3.BACK
		var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
			point, point + direction * 4, WORLD_LAYER)
		var hit: Dictionary = space.intersect_ray(ray)
		_expect(not hit.is_empty(), "No corner/straight/stack seam ray gap")
		if not hit.is_empty():
			var position: Vector3 = hit["position"]
			_expect(position.distance_to(point + direction * 2) < TOLERANCE_M, "Seam datum")
			observations.append({ "from": [point.x, point.y, point.z],
				"hit": [position.x, position.y, position.z] })

	_result[_variant]["straight_and_stacked_seam_rays"] = observations


## Exercise production motion in authority/replay, including a diagonal concave-corner stop.
func _motion(edge: float) -> void:
	var floor_body: StaticBody3D = _test_floor()
	var cases: Array[Dictionary] = [
		{ "name": "north_stop", "start": Vector3(0, 0, -edge - 2),
			"move": Vector2.DOWN, "end": Vector3(0, 0, -edge - 0.35) },
		{ "name": "west_stop", "start": Vector3(-edge - 2, 0, 0),
			"move": Vector2.RIGHT, "end": Vector3(-edge - 0.35, 0, 0) },
		{ "name": "east_bypass", "start": Vector3(edge + 1, 0, -edge - 2),
			"move": Vector2.DOWN, "end": Vector3(edge + 1, 0, -edge + 3) },
	]
	if _variant == "inside":
		cases.append({ "name": "court_corner_stop", "start": Vector3(6, 0, 6),
			"move": Vector2(-1, -1).normalized(), "end": Vector3(3.35, 0, 3.35) })

	var observations: Array[Dictionary] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		for test: Dictionary in cases:
			var actor := ActorMotion.new()  # gdstyle:ignore=quality/allocation-in-loop
			var shape := CollisionShape3D.new()  # gdstyle:ignore=quality/allocation-in-loop
			var capsule := CapsuleShape3D.new()  # gdstyle:ignore=quality/allocation-in-loop
			capsule.radius = ACTOR_RADIUS_M
			capsule.height = ACTOR_HEIGHT_M
			shape.shape = capsule
			shape.position.y = ACTOR_HEIGHT_M / 2
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

			_expect(actor.position.distance_to(test["end"]) < CONTACT_TOLERANCE_M,
				"Actor contact " + test["name"])
			observations.append({ "case": test["name"], "mode": mode,
				"end": [actor.position.x, actor.position.y, actor.position.z] })
			actor.free()

	for index: int in range(cases.size()):
		_expect(observations[index]["end"] == observations[index + cases.size()]["end"],
			"Authority/replay contact equivalence")

	_result[_variant]["actor_motion"] = observations
	floor_body.free()


## Create only a physics test floor, never visible authored content.
func _test_floor() -> StaticBody3D:
	var floor_body: StaticBody3D = StaticBody3D.new()
	var floor_shape: CollisionShape3D = CollisionShape3D.new()
	var floor_box: BoxShape3D = BoxShape3D.new()
	floor_box.size = Vector3(50, 0.2, 50)
	floor_shape.shape = floor_box
	floor_shape.position.y = -0.1
	floor_body.add_child(floor_shape)
	root.add_child(floor_body)
	return floor_body


## Sweep a car-sized box against the facade and through the unobstructed east bypass.
func _car_sweep(edge: float) -> void:
	var car: CharacterBody3D = CharacterBody3D.new()
	var shape: CollisionShape3D = CollisionShape3D.new()
	var box: BoxShape3D = BoxShape3D.new()
	box.size = Vector3(1.9, 1.5, 4.3)
	shape.shape = box
	shape.position.y = 0.75
	car.add_child(shape)
	car.collision_layer = 0
	car.collision_mask = WORLD_LAYER
	root.add_child(car)
	await physics_frame
	var blocked: bool = car.test_move(
		Transform3D(Basis.IDENTITY, Vector3(0, 0, -edge - 4)), Vector3(0, 0, 8))
	var bypass: bool = car.test_move(
		Transform3D(Basis.IDENTITY, Vector3(edge + 2, 0, -edge - 4)), Vector3(0, 0, 8))
	_expect(blocked and not bypass, "Car box stop and clear bypass")
	_result[_variant]["car_box_sweep"] = { "front_blocked": blocked, "bypass_blocked": bypass }
	car.free()


## Let the editor finish scanning before its UID-preserving serialization operation.
func _wait_for_scan() -> void:
	if not Engine.is_editor_hint():
		return

	await create_timer(3.0).timeout
	while EditorInterface.get_resource_filesystem().is_scanning():
		await create_timer(1.0).timeout  # gdstyle:ignore=quality/await-in-loop


## Separate editor-only normalization from clean runtime resource and physics checks.
func _run() -> void:
	await _wait_for_scan()
	if OS.get_cmdline_user_args().has("--normalize"):
		if not Engine.is_editor_hint():
			push_error("Use --editor for UID-preserving normalization")
			quit(1)
			return

		_roundtrip()
		var receipt: FileAccess = FileAccess.open(OUTPUT + ".roundtrip", FileAccess.WRITE)
		receipt.store_string(JSON.stringify(_result))
		receipt.close()
		print(JSON.stringify(_result))
		await _wait_for_scan()
		quit(0 if _failures.is_empty() else 1)
		return

	for variant: String in ["outside", "inside"]:
		_variant = variant
		var edge: float = 6 if variant == "outside" else 9
		var packed: PackedScene = load(PREFIX + variant + ".tscn") as PackedScene
		_expect(packed != null, "Dependencies resolve")
		var instance: Node3D = packed.instantiate() as Node3D
		root.add_child(instance)
		_inspect(instance, edge)
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		_queries(instance, edge)
		await _joins(instance, edge)  # gdstyle:ignore=quality/await-in-loop
		await _motion(edge)  # gdstyle:ignore=quality/await-in-loop
		await _car_sweep(edge)  # gdstyle:ignore=quality/await-in-loop
		instance.free()

	_result["roundtrip"] = JSON.parse_string(FileAccess.get_file_as_string(OUTPUT + ".roundtrip"))
	_result["engine"] = Engine.get_version_info()["string"]
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var file: FileAccess = FileAccess.open(OUTPUT, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
