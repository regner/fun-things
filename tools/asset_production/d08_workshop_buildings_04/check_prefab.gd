@tool
extends SceneTree

const PREFAB_PATH: String = "res://scenes/prefabs/environment/d08_workshop_buildings_04.tscn"
const FAMILY_PATH: String = "res://scenes/prefabs/environment/d08_workshop_buildings_04_family.tscn"
const MODEL_PATH: String = (
	"res://art/models/environment/d08_workshop_buildings_04/d08_workshop_buildings_04.glb"
)
const OUTPUT_PATH: String = "C:/tmp/ft/assets/d08_workshop_buildings_04/prefab-check.json"
const EXPECTED_BOUNDS: AABB = AABB(Vector3(-3.08, 0, -1.74), Vector3(6.28, 3.55, 3.44))
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
func _roundtrip(path: String) -> void:
	var original: PackedScene = load(path) as PackedScene
	_expect(original != null, "Prefab must load before normalization")
	if original == null:
		return

	var instance: Node = original.instantiate()
	var packed: PackedScene = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Prefab pack")
	_expect(ResourceSaver.save(packed, path) == OK, "Prefab save")
	instance.free()
	var first: String = FileAccess.get_sha256(path)
	var reloaded: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	instance = reloaded.instantiate()
	packed = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Reloaded prefab pack")
	_expect(ResourceSaver.save(packed, path) == OK, "Reloaded prefab save")
	instance.free()
	_result[path] = { "save_reload_byte_stable": first == FileAccess.get_sha256(path) }
	_expect(_result[path]["save_reload_byte_stable"], "Second save changed bytes")


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
	_expect(mesh_instance.mesh.get_surface_count() == 8, "Eight material surfaces")
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
	_expect(body.get_child_count() == 1, "One simple closed-building collider")
	var solid_shape: CollisionShape3D = body.get_node("OfficeSolid") as CollisionShape3D
	_expect((solid_shape.shape as BoxShape3D).size == Vector3(6, 3, 3), "Office box")
	_expect(solid_shape.position == Vector3(0, 1.5, 0), "Office box ground datum")
	_result["aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["aabb_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_result["materials"] = materials
	_result["linked_model_identity"] = model.transform == Transform3D.IDENTITY
	_result["collision_shape_count"] = body.get_child_count()
	_inspect_uids()


## Require both the saved wrapper and imported model identities to resolve through the engine.
func _inspect_uids() -> void:
	var prefab_uid: int = ResourceLoader.get_resource_uid(PREFAB_PATH)
	var model_uid: int = ResourceLoader.get_resource_uid(MODEL_PATH)
	_expect(prefab_uid != ResourceUID.INVALID_ID, "Prefab UID resolves")
	_expect(model_uid != ResourceUID.INVALID_ID, "Model UID resolves")
	_result["prefab_uid"] = ResourceUID.id_to_text(prefab_uid)
	_result["model_uid"] = ResourceUID.id_to_text(model_uid)


## Assert solid walls, closed doors and clear perimeter independently of source construction.
func _queries(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = ACTOR_RADIUS_M
	capsule.height = ACTOR_HEIGHT_M
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = WORLD_LAYER
	var cases: Array[Dictionary] = [
		{ "name": "interior_solid", "point": Vector3(0, 0.9, 0), "solid": true },
		{ "name": "closed_door", "point": Vector3(1.6, 0.9, -1.4), "solid": true },
		{ "name": "closed_counter_window", "point": Vector3(-1.3, 1.5, -1.4), "solid": true },
		{ "name": "east_bypass_clear", "point": Vector3(3.6, 0.9, 0), "solid": false },
		{ "name": "west_bypass_clear", "point": Vector3(-3.6, 0.9, 0), "solid": false },
		{ "name": "rear_route_clear", "point": Vector3(0, 0.9, 2.1), "solid": false },
		{ "name": "front_route_clear", "point": Vector3(0, 0.9, -2.1), "solid": false },
		{ "name": "north_east_corner_solid", "point": Vector3(2.95, 0.9, -1.45), "solid": true },
		{ "name": "south_west_corner_solid", "point": Vector3(-2.95, 0.9, 1.45), "solid": true },
	]
	var observations: Array[Dictionary] = []
	for test: Dictionary in cases:
		query.transform.origin = test["point"]
		var solid: bool = not space.intersect_shape(query).is_empty()
		_expect(solid == test["solid"], "Capsule query: " + str(test["name"]))
		observations.append({ "case": test["name"], "solid": solid })

	_result["capsule_queries"] = observations
	var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
		Vector3(1.6, 1, -5), Vector3(1.6, 1, 0), WORLD_LAYER
	)
	var hit: Dictionary = space.intersect_ray(ray)
	_expect(not hit.is_empty(), "Closed facade aim ray")
	if not hit.is_empty():
		_expect(absf(hit["position"].z + 1.5) < TOLERANCE_M, "Front ray wall datum")
		_result["front_ray_z"] = hit["position"].z


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


## Keep literal movement expectations separate from the production step loop.
func _motion_cases() -> Array[Dictionary]:
	return [
		{ "name": "closed_door", "start": Vector3(1.6, 0, -5),
			"move": Vector2.DOWN, "end": Vector3(1.6, 0, -1.85) },
		{ "name": "counter_wall", "start": Vector3(-1.3, 0, -5),
			"move": Vector2.DOWN, "end": Vector3(-1.3, 0, -1.85) },
		{ "name": "east_wall", "start": Vector3(6, 0, 0),
			"move": Vector2.LEFT, "end": Vector3(3.35, 0, 0) },
		{ "name": "east_bypass", "start": Vector3(4, 0, -5),
			"move": Vector2.DOWN, "end": Vector3(4, 0, 0) },
	]


## Exercise the production ActorMotion authority and replay modes against identical static solids.
func _actor_motion_checks() -> void:
	var floor_body: StaticBody3D = _add_test_floor()
	var cases: Array[Dictionary] = _motion_cases()
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
		Transform3D(Basis.IDENTITY, Vector3(0, 0, -6)), Vector3(0, 0, 8)
	)
	var bypass: bool = car.test_move(
		Transform3D(Basis.IDENTITY, Vector3(5, 0, -6)), Vector3(0, 0, 8)
	)
	_expect(blocked and not bypass, "Car-sized box front stop and east bypass")
	_result["car_box_sweep"] = { "size_m": [1.9, 1.5, 4.3], "front_blocked": blocked,
		"east_bypass_blocked": bypass }
	car.free()


## Prove the saved comparison uses real siblings and an exactly mating closed office box.
func _inspect_family(family: Node3D) -> void:
	var shed: Node3D = family.get_node("PitchedShed") as Node3D
	var workshop: Node3D = family.get_node("SawtoothWorkshop") as Node3D
	var office: Node3D = family.get_node("AttachedOffice") as Node3D
	_expect(shed.position == Vector3(8, 0, -2), "Saved pitched-shed placement")
	_expect(workshop.position == Vector3(-13, 0, 1), "Saved sawtooth placement")
	_expect(office.position == Vector3(16, 0, 2.5), "Saved office attachment placement")
	_expect(shed.scene_file_path.ends_with("d08_workshop_buildings_01.tscn"), "Existing shed")
	_expect(
		workshop.scene_file_path.ends_with("d08_workshop_buildings_02.tscn"),
		"Existing sawtooth",
	)
	_expect(office.scene_file_path == PREFAB_PATH, "Existing office wrapper")
	var office_shape: CollisionShape3D = office.get_node("Collision/Body/OfficeSolid")
	var office_box: BoxShape3D = office_shape.shape as BoxShape3D
	var shed_shape: CollisionShape3D = shed.get_node("Collision/Body").get_child(0)
	var shed_box: BoxShape3D = shed_shape.shape as BoxShape3D
	var seam_x: float = office_shape.global_position.x - office_box.size.x / 2.0
	var shed_edge: float = shed_shape.global_position.x + shed_box.size.x / 2.0
	_expect(absf(seam_x - shed_edge) < TOLERANCE_M, "Office/host collision has no seam gap")
	_expect(absf(seam_x - 13.0) < TOLERANCE_M, "Independent attachment plane X=13")
	_expect(office.position.z - office_box.size.z / 2.0 == 1.0, "Bay start Z=1")
	_expect(office.position.z + office_box.size.z / 2.0 == 4.0, "Bay end Z=4")
	var yard_gap: float = _measure_yard_gap(shed_shape, workshop)
	_expect(absf(yard_gap - 9.0) < TOLERANCE_M, "Independent nine-metre yard gap")
	_result["family"] = { "office_host_seam_gap_m": seam_x - shed_edge,
		"join_x_m": seam_x, "office_span_z_m": [1, 4], "central_structural_gap_m": yard_gap,
		"composition": "Existing .01 at (8,0,-2), .02 at (-13,0,1), .04 at (16,0,2.5)" }


## Measure the yard from saved collision shapes rather than copied placement assumptions.
func _measure_yard_gap(shed_shape: CollisionShape3D, workshop: Node3D) -> float:
	var workshop_shape: CollisionShape3D = workshop.get_node("Collision/Body").get_child(0)
	var workshop_box: BoxShape3D = workshop_shape.shape as BoxShape3D
	var shed_box: BoxShape3D = shed_shape.shape as BoxShape3D
	return (
		shed_shape.global_position.x - shed_box.size.x / 2.0
		- workshop_shape.global_position.x - workshop_box.size.x / 2.0
	)


## Query both join corners and open yard exits without inventing an interior opening.
func _family_queries(family: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = family.get_world_3d().direct_space_state
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = ACTOR_RADIUS_M
	capsule.height = ACTOR_HEIGHT_M
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = WORLD_LAYER
	var observations: Array[Dictionary] = []
	var cases: Array[Dictionary] = [
		{ "name": "join_front_solid", "point": Vector3(13, 0.9, 1.05), "solid": true },
		{ "name": "join_middle_solid", "point": Vector3(13, 0.9, 2.5), "solid": true },
		{ "name": "join_rear_solid", "point": Vector3(13, 0.9, 3.95), "solid": true },
		{ "name": "front_reentrant_clear", "point": Vector3(13.6, 0.9, 0.4), "solid": false },
		{ "name": "rear_join_outside_clear", "point": Vector3(13.6, 0.9, 4.6), "solid": false },
		{ "name": "north_yard_exit_clear", "point": Vector3(-1.5, 0.9, -12), "solid": false },
		{ "name": "central_yard_clear", "point": Vector3(-1.5, 0.9, 0), "solid": false },
		{ "name": "south_yard_exit_clear", "point": Vector3(-1.5, 0.9, 12), "solid": false },
		{ "name": "outer_foot_bypass_clear", "point": Vector3(20, 0.9, 2.5), "solid": false },
	]
	for test: Dictionary in cases:
		query.transform.origin = test["point"]
		var solid: bool = not space.intersect_shape(query).is_empty()
		_expect(solid == test["solid"], "Family capsule: " + str(test["name"]))
		observations.append({ "case": test["name"], "solid": solid })

	_result["family"]["capsule_queries"] = observations


## Sweep the complete open yard and outside bypass with a car-sized box in both directions.
func _family_sweeps() -> void:
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
	var north_to_south: bool = car.test_move(
		Transform3D(Basis.IDENTITY, Vector3(-1.5, 0, -14)), Vector3(0, 0, 28)
	)
	var south_to_north: bool = car.test_move(
		Transform3D(Basis.IDENTITY, Vector3(-1.5, 0, 14)), Vector3(0, 0, -28)
	)
	var bypass: bool = car.test_move(
		Transform3D(Basis.IDENTITY, Vector3(21, 0, -14)), Vector3(0, 0, 28)
	)
	_expect(not north_to_south and not south_to_north and not bypass, "Open two-ended yard")
	_result["family"]["car_sweeps_blocked"] = [north_to_south, south_to_north, bypass]
	car.free()


## Load the authored family composition in isolation, then release every test instance.
func _family_checks() -> void:
	var packed: PackedScene = load(FAMILY_PATH) as PackedScene
	_expect(packed != null, "Family dependencies resolve")
	if packed == null:
		return

	var family: Node3D = packed.instantiate() as Node3D
	root.add_child(family)
	_inspect_family(family)
	await physics_frame
	await physics_frame
	_family_queries(family)
	await _family_sweeps()
	family.free()


## Run resource normalization separately from fresh runtime collision and production motion checks.
func _run() -> void:
	if Engine.is_editor_hint():
		await create_timer(EDITOR_STARTUP_SECONDS).timeout

	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.has("--normalize"):
		_roundtrip(PREFAB_PATH)
		_roundtrip(FAMILY_PATH)
		print(JSON.stringify(_result))
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
		instance.free()

	await _family_checks()
	_result["engine"] = Engine.get_version_info()["string"]
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var file: FileAccess = FileAccess.open(OUTPUT_PATH, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
