@tool
extends SceneTree

const PREFAB_PATH: String = "res://scenes/prefabs/environment/d03_apartment_family_07.tscn"
const MODEL_PATH: String = (
	"res://art/models/environment/d03_apartment_family_07/d03_apartment_family_07.glb"
)
const STRAIGHT_PATH: String = "res://scenes/prefabs/environment/d03_apartment_family_05.tscn"
const CORNER_PATH: String = (
	"res://art/models/environment/d03_apartment_family_06/d03_apartment_family_06_outside.glb"
)
const OUTPUT_PATH: String = "C:/tmp/ft/assets/d03_apartment_family_07/prefab-check.json"
const EXPECTED_BOUNDS: AABB = AABB(Vector3(-0.12, 0, -6.10), Vector3(0.34, 3.2, 12.20))
const TOLERANCE_M: float = 0.001
# Allow bounded solver separation; expected wall/capsule contact coordinates remain literal.
const MOTION_CONTACT_TOLERANCE_M: float = 0.025
const WORLD_LAYER: int = 1
const ACTOR_RADIUS_M: float = 0.35
const ACTOR_HEIGHT_M: float = 1.8
const TEST_TICKS: int = 60
const EDITOR_STARTUP_SECONDS: float = 3.0

var _failures: Array[String] = []
var _result: Dictionary = {}


## Defer checks until the isolated headless scene tree is ready.
func _initialize() -> void:
	_run.call_deferred()


## Keep all assertion failures visible and return a nonzero final exit.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Normalize this owned wrapper only and prove a second load/pack/save is byte-stable.
func _roundtrip() -> void:
	var original: PackedScene = load(PREFAB_PATH) as PackedScene
	_expect(original != null, "Prefab must load before normalization")
	if original == null:
		return

	var instance: Node = original.instantiate()
	var packed: PackedScene = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Prefab pack")
	_expect(ResourceSaver.save(packed, PREFAB_PATH) == OK, "Prefab save")
	instance.free()
	var first: String = FileAccess.get_sha256(PREFAB_PATH)
	_result["normalized_sha256"] = first
	var reloaded: PackedScene = ResourceLoader.load(
		PREFAB_PATH, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	instance = reloaded.instantiate()
	packed = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Reloaded prefab pack")
	_expect(ResourceSaver.save(packed, PREFAB_PATH) == OK, "Reloaded prefab save")
	instance.free()
	_result["save_reload_byte_stable"] = first == FileAccess.get_sha256(PREFAB_PATH)
	_expect(_result["save_reload_byte_stable"], "Second save changed bytes")


## Check real imported ancestry, transforms, bounds, opaque materials and collider envelopes.
func _inspect(instance: Node3D) -> void:
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == MODEL_PATH, "Linked GLB ancestry")
	_expect(model.transform == Transform3D.IDENTITY, "Identity imported model")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "One imported mesh")
	var mesh_instance: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh_instance.global_transform * mesh_instance.get_aabb()
	_expect(bounds.position.distance_to(EXPECTED_BOUNDS.position) < TOLERANCE_M, "Bounds min")
	_expect(bounds.size.distance_to(EXPECTED_BOUNDS.size) < TOLERANCE_M, "Bounds size")
	_expect(mesh_instance.mesh.resource_path.begins_with(MODEL_PATH), "Imported mesh resource")
	_expect(mesh_instance.mesh.get_surface_count() == 4, "Four material surfaces")
	var materials: Array[String] = []
	for index: int in range(mesh_instance.mesh.get_surface_count()):
		var material: BaseMaterial3D = (
			mesh_instance.mesh.surface_get_material(index) as BaseMaterial3D
		)
		_expect(material != null, "Material dependency")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque material")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back-culling material")
		materials.append(material.resource_name)

	var body: StaticBody3D = instance.get_node("Collision/Body") as StaticBody3D
	_expect(body.collision_layer == WORLD_LAYER and body.collision_mask == 0, "World layers")
	_expect(body.get_child_count() == 1, "One solid core collider")
	var core: CollisionShape3D = body.get_node("Core") as CollisionShape3D
	_expect((core.shape as BoxShape3D).size == Vector3(0.24, 3.2, 12), "Core dimensions")
	_expect(core.position == Vector3(0, 1.6, 0), "Core ground datum")
	_result["aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["aabb_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_result["materials"] = materials
	_result["linked_model_identity"] = model.transform == Transform3D.IDENTITY
	_result["collision_shape_count"] = body.get_child_count()
	_inspect_uids()
	_compare_family_materials(mesh_instance)


## Require both the saved wrapper and imported model identities to resolve through the engine.
func _inspect_uids() -> void:
	var prefab_uid: int = ResourceLoader.get_resource_uid(PREFAB_PATH)
	var model_uid: int = ResourceLoader.get_resource_uid(MODEL_PATH)
	_expect(prefab_uid != ResourceUID.INVALID_ID, "Prefab UID resolves")
	_expect(model_uid != ResourceUID.INVALID_ID, "Model UID resolves")
	_result["prefab_uid"] = ResourceUID.id_to_text(prefab_uid)
	_result["model_uid"] = ResourceUID.id_to_text(model_uid)


## Match actual imported family materials, including the corner's coral, by stable slot name.
func _compare_family_materials(mesh_instance: MeshInstance3D) -> void:
	var corner: Node3D = (load(CORNER_PATH) as PackedScene).instantiate() as Node3D
	var meshes: Array[Node] = corner.find_children("*", "MeshInstance3D", true, false)
	var sibling_mesh: Mesh = (meshes[0] as MeshInstance3D).mesh
	var palette: Dictionary = {}
	for index: int in range(sibling_mesh.get_surface_count()):
		var material: BaseMaterial3D = sibling_mesh.surface_get_material(index) as BaseMaterial3D
		palette[material.resource_name] = material

	for index: int in range(mesh_instance.mesh.get_surface_count()):
		var material: BaseMaterial3D = (
			mesh_instance.mesh.surface_get_material(index) as BaseMaterial3D
		)
		var sibling: BaseMaterial3D = palette[material.resource_name] as BaseMaterial3D
		_expect(material.albedo_color == sibling.albedo_color, "Family color match")
		_expect(material.roughness == sibling.roughness, "Family roughness match")
		_expect(material.metallic == sibling.metallic, "Family metallic match")

	_result["family_material_values_match"] = true
	corner.free()


## Assert the thin closed wall and its clear setbacks using literal independent coordinates.
func _queries(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = ACTOR_RADIUS_M
	capsule.height = ACTOR_HEIGHT_M
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = WORLD_LAYER
	var cases: Array[Dictionary] = [
		{ "name": "core_solid", "point": Vector3(0, 0.9, 0), "solid": true },
		{ "name": "north_end_solid", "point": Vector3(0, 0.9, -5.9), "solid": true },
		{ "name": "south_end_solid", "point": Vector3(0, 0.9, 5.9), "solid": true },
		{ "name": "north_clear", "point": Vector3(0, 0.9, -6.6), "solid": false },
		{ "name": "south_clear", "point": Vector3(0, 0.9, 6.6), "solid": false },
		{ "name": "exposed_side_clear", "point": Vector3(0.7, 0.9, 0), "solid": false },
		{ "name": "mating_side_clear", "point": Vector3(-0.7, 0.9, 0), "solid": false },
	]
	var observations: Array[Dictionary] = []
	for test: Dictionary in cases:
		query.transform.origin = test["point"]
		var solid: bool = not space.intersect_shape(query).is_empty()
		_expect(solid == test["solid"], "Capsule query: " + str(test["name"]))
		observations.append({ "case": test["name"], "solid": solid })

	_result["capsule_queries"] = observations
	var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
		Vector3(2, 1.5, 0), Vector3(-2, 1.5, 0), WORLD_LAYER
	)
	var hit: Dictionary = space.intersect_ray(ray)
	_expect(not hit.is_empty(), "Closed end-wall aim ray")
	if not hit.is_empty():
		_expect(absf(hit["position"].x - 0.12) < TOLERANCE_M, "Exposed wall datum")
		_result["end_wall_ray_x"] = hit["position"].x


## Add only a physics test plane; it is not visible content or a prefab dependency.
func _add_test_floor() -> StaticBody3D:
	var floor_body: StaticBody3D = StaticBody3D.new()
	var floor_shape: CollisionShape3D = CollisionShape3D.new()
	var floor_box: BoxShape3D = BoxShape3D.new()
	floor_box.size = Vector3(40, 0.2, 40)
	floor_shape.shape = floor_box
	floor_shape.position.y = -0.1
	floor_body.add_child(floor_shape)
	root.add_child(floor_body)
	return floor_body


## Exercise the production ActorMotion authority and replay modes against identical static solids.
func _actor_motion_checks() -> void:
	var floor_body: StaticBody3D = _add_test_floor()
	var cases: Array[Dictionary] = [
		{ "name": "exposed_side_stop", "start": Vector3(3, 0, 1.5),
			"move": Vector2.LEFT, "end": Vector3(0.47, 0, 1.5) },
		{ "name": "mating_side_stop", "start": Vector3(-3, 0, -1.5),
			"move": Vector2.RIGHT, "end": Vector3(-0.47, 0, -1.5) },
		{ "name": "north_tip_stop", "start": Vector3(0, 0, -8),
			"move": Vector2.DOWN, "end": Vector3(0, 0, -6.35) },
		{ "name": "east_bypass", "start": Vector3(1, 0, -8),
			"move": Vector2.DOWN, "end": Vector3(1, 0, -3) },
	]
	var observations: Array[Dictionary] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		for test: Dictionary in cases:
			# Each bounded test needs a fresh body, shape and contact history.
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
			# Fixed-step waits and new immutable commands are intentional in this bounded API test.
			await physics_frame  # gdstyle:ignore=quality/await-in-loop
			for tick: int in range(TEST_TICKS):
				var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
					tick + 1, tick, test["move"], 0, false, false
				)
				_expect(
					actor.step(command, 1.0 / Engine.physics_ticks_per_second, mode), "Motion step"
				)
				await physics_frame  # gdstyle:ignore=quality/await-in-loop

			_expect(
				actor.position.distance_to(test["end"]) < MOTION_CONTACT_TOLERANCE_M,
				"Motion end: " + test["name"]
			)
			observations.append({ "case": test["name"], "mode": mode,
				"end": [actor.position.x, actor.position.y, actor.position.z] })
			actor.free()

	_record_motion_results(observations, cases.size())
	floor_body.free()


## Retain both mode observations and reject any authority/replay contact divergence.
func _record_motion_results(observations: Array[Dictionary], case_count: int) -> void:
	_result["production_actor_motion"] = observations
	for index: int in range(case_count):
		_expect(observations[index]["end"] == observations[index + case_count]["end"],
			"Authority/replay contact equivalence")


## Sweep a documented car-sized test box; this is not production driving or turning acceptance.
func _car_sweep_checks() -> void:
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
		Transform3D(Basis.IDENTITY, Vector3(6, 0, 0)), Vector3(-8, 0, 0)
	)
	var bypass: bool = car.test_move(
		Transform3D(Basis.IDENTITY, Vector3(6, 0, 9)), Vector3(-8, 0, 0)
	)
	_expect(blocked and not bypass, "Car-sized box end stop and south bypass")
	_result["car_box_sweep"] = { "size_m": [1.9, 1.5, 4.3], "end_blocked": blocked,
		"south_bypass_blocked": bypass }
	car.free()


## Verify the actual straight bay closes at both ends and the wall stacks without collision gaps.
func _join_checks(packed: PackedScene, instance: Node3D) -> void:
	var straight: Node3D = (load(STRAIGHT_PATH) as PackedScene).instantiate() as Node3D
	var upper: Node3D = packed.instantiate() as Node3D
	var west: Node3D = packed.instantiate() as Node3D
	straight.position.x = -3.12
	upper.position.y = 3.2
	west.position.x = -6.24
	west.rotation.y = PI
	root.add_child(straight)
	root.add_child(upper)
	root.add_child(west)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var cases: Array[Dictionary] = [
		{ "name": "north_mating_seam", "from": Vector3(-0.12, 1, -8),
			"to": Vector3(-0.12, 1, -4), "hit": Vector3(-0.12, 1, -6) },
		{ "name": "south_mating_seam", "from": Vector3(-0.12, 1, 8),
			"to": Vector3(-0.12, 1, 4), "hit": Vector3(-0.12, 1, 6) },
		{ "name": "stacked_wall_seam", "from": Vector3(2, 3.2, 1),
			"to": Vector3(-1, 3.2, 1), "hit": Vector3(0.12, 3.2, 1) },
		{ "name": "reversed_west_wall", "from": Vector3(-8, 1, 0),
			"to": Vector3(-4, 1, 0), "hit": Vector3(-6.36, 1, 0) },
		{ "name": "west_north_seam", "from": Vector3(-6.12, 1, -8),
			"to": Vector3(-6.12, 1, -4), "hit": Vector3(-6.12, 1, -6) },
	]
	var observations: Array[Dictionary] = []
	for test: Dictionary in cases:
		var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
			test["from"], test["to"], WORLD_LAYER
		)
		var hit: Dictionary = space.intersect_ray(ray)
		_expect(not hit.is_empty(), "No join gap: " + test["name"])
		if not hit.is_empty():
			var point: Vector3 = hit["position"]
			_expect(point.distance_to(test["hit"]) < TOLERANCE_M, "Seam wall datum")
			observations.append({ "case": test["name"], "hit": [point.x, point.y, point.z] })

	_result["assembled_and_stacked_seam_rays"] = observations
	straight.free()
	upper.free()
	west.free()


## Seat the closure on each delivered corner's unused twelve-metre east connector.
func _corner_join_checks(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var observations: Array[Dictionary] = []
	var cases: Array[Dictionary] = [
		{ "variant": "outside", "origin": Vector3(-6.12, 0, 0) },
		{ "variant": "inside", "origin": Vector3(-9.12, 0, 3) },
	]
	for test: Dictionary in cases:
		var path: String = (
			"res://scenes/prefabs/environment/d03_apartment_family_06_%s.tscn" % test["variant"]
		)
		var corner: Node3D = (load(path) as PackedScene).instantiate() as Node3D
		corner.position = test["origin"]
		root.add_child(corner)
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		for side: float in [-1.0, 1.0]:
			var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
				Vector3(-0.12, 1, side * 8), Vector3(-0.12, 1, side * 4), WORLD_LAYER
			)
			var hit: Dictionary = space.intersect_ray(ray)
			_expect(not hit.is_empty(), "Corner closure seam: " + test["variant"])
			if not hit.is_empty():
				_expect(absf(hit["position"].z - side * 6) < TOLERANCE_M, "Corner seam datum")
				observations.append({ "variant": test["variant"], "hit_z": hit["position"].z })

		corner.free()

	_result["corner_closure_seam_rays"] = observations


## Wait for headless editor scans to finish before serializing IDs or shutting down.
func _wait_for_editor_scan() -> void:
	if not Engine.is_editor_hint():
		return

	await create_timer(EDITOR_STARTUP_SECONDS).timeout
	while EditorInterface.get_resource_filesystem().is_scanning():
		# Polling is intentional; the outer CLI timeout bounds a stuck import.
		await create_timer(1.0).timeout  # gdstyle:ignore=quality/await-in-loop


## Run resource normalization separately from fresh runtime collision and production motion checks.
func _run() -> void:
	await _wait_for_editor_scan()

	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.has("--normalize"):
		# Runtime ResourceSaver strips scene/dependency UIDs on this pin.
		if not Engine.is_editor_hint():
			push_error("Normalization requires --editor to retain saved UIDs")
			quit(1)
			return

		_roundtrip()
		var receipt: FileAccess = FileAccess.open(OUTPUT_PATH + ".roundtrip", FileAccess.WRITE)
		receipt.store_string(JSON.stringify(_result))
		receipt.close()
		print(JSON.stringify(_result))
		await _wait_for_editor_scan()
		quit(0 if _failures.is_empty() else 1)
		return

	var packed: PackedScene = load(PREFAB_PATH) as PackedScene
	_expect(packed != null, "All prefab dependencies resolve")
	if packed != null:
		var instance: Node3D = packed.instantiate() as Node3D
		root.add_child(instance)
		_inspect(instance)
		await physics_frame
		await physics_frame
		_queries(instance)
		await _actor_motion_checks()
		await _car_sweep_checks()
		await _join_checks(packed, instance)
		await _corner_join_checks(instance)
		instance.free()

	_result["roundtrip"] = JSON.parse_string(FileAccess.get_file_as_string(
		OUTPUT_PATH + ".roundtrip"))
	_result["engine"] = Engine.get_version_info()["string"]
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var file: FileAccess = FileAccess.open(OUTPUT_PATH, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
