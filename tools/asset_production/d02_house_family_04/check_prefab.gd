@tool
extends SceneTree

const PREFAB_PATH: String = "res://scenes/prefabs/environment/d02_house_family_04.tscn"
const MODEL_PATH: String = (
	"res://art/models/environment/d02_house_family_04/d02_house_family_04.glb"
)
const OUTPUT_PATH: String = "C:/tmp/ft/assets/d02_house_family_04/prefab-check.json"
const EXPECTED_BOUNDS: AABB = AABB(Vector3(-4.55, 0, -4.55), Vector3(9.1, 7.55, 9.1))
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
	_expect(mesh_instance.mesh.get_surface_count() == 7, "Seven material surfaces")
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
	_expect(body.get_child_count() == 2, "Two-box L-shaped corner footprint")
	var main_shape: CollisionShape3D = body.get_node("MainHome") as CollisionShape3D
	var east_shape: CollisionShape3D = body.get_node("EastWing") as CollisionShape3D
	_expect((main_shape.shape as BoxShape3D).size == Vector3(4.8, 5.3, 8.4), "Main home box")
	_expect(main_shape.position == Vector3(-1.8, 2.65, 0), "Main home box ground datum")
	_expect((east_shape.shape as BoxShape3D).size == Vector3(3.6, 5.3, 4.8), "East box")
	_expect(east_shape.position == Vector3(2.4, 2.65, 1.8), "East box ground datum")
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


## Assert capsule overlap and clear setback coordinates independently of source construction.
func _queries(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = ACTOR_RADIUS_M
	capsule.height = ACTOR_HEIGHT_M
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = WORLD_LAYER
	var cases: Array[Dictionary] = [
		{ "name": "main_solid", "point": Vector3(-1.8, 0.9, 0), "solid": true },
		{ "name": "wing_solid", "point": Vector3(2.4, 0.9, 2), "solid": true },
		{ "name": "front_closed_glass", "point": Vector3(-1.8, 0.9, -4.1), "solid": true },
		{ "name": "corner_closed_door", "point": Vector3(2.6, 0.9, -0.5), "solid": true },
		{ "name": "east_closed_glass", "point": Vector3(4.1, 0.9, 1.8), "solid": true },
		{ "name": "corner_setback_clear", "point": Vector3(2.6, 0.9, -2.6), "solid": false },
		{ "name": "east_bypass_clear", "point": Vector3(4.8, 0.9, 0), "solid": false },
		{ "name": "west_bypass_clear", "point": Vector3(-4.8, 0.9, 0), "solid": false },
		{ "name": "rear_route_clear", "point": Vector3(0, 0.9, 4.8), "solid": false },
	]
	var observations: Array[Dictionary] = []
	for test: Dictionary in cases:
		query.transform.origin = test["point"]
		var solid: bool = not space.intersect_shape(query).is_empty()
		_expect(solid == test["solid"], "Capsule query: " + str(test["name"]))
		observations.append({ "case": test["name"], "solid": solid })

	_result["capsule_queries"] = observations
	var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
		Vector3(-1.8, 1, -8), Vector3(-1.8, 1, 0), WORLD_LAYER
	)
	var hit: Dictionary = space.intersect_ray(ray)
	_expect(not hit.is_empty(), "Closed facade aim ray")
	if not hit.is_empty():
		_expect(absf(hit["position"].z + 4.2) < TOLERANCE_M, "Front ray wall datum")
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


## Provide independent literal expected contacts, including both open-corner approaches.
func _motion_cases() -> Array[Dictionary]:
	return [
		{ "name": "main_closed_front", "start": Vector3(-1.8, 0, -8),
			"move": Vector2.DOWN, "end": Vector3(-1.8, 0, -4.55) },
		{ "name": "corner_recessed_entry", "start": Vector3(2.6, 0, -5.2),
			"move": Vector2.DOWN, "end": Vector3(2.6, 0, -0.95) },
		{ "name": "east_side", "start": Vector3(8, 0, 1.8),
			"move": Vector2.LEFT, "end": Vector3(4.55, 0, 1.8) },
		{ "name": "corner_return_wall", "start": Vector3(3, 0, -2.6),
			"move": Vector2.LEFT, "end": Vector3(0.95, 0, -2.6) },
		{ "name": "east_bypass", "start": Vector3(5.3, 0, -8),
			"move": Vector2.DOWN, "end": Vector3(5.3, 0, -3) },
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
		Transform3D(Basis.IDENTITY, Vector3(-1.8, 0, -10)), Vector3(0, 0, 8)
	)
	var bypass: bool = car.test_move(
		Transform3D(Basis.IDENTITY, Vector3(5.5, 0, -10)), Vector3(0, 0, 8)
	)
	_expect(blocked and not bypass, "Car-sized box front stop and east bypass")
	_result["car_box_sweep"] = { "size_m": [1.9, 1.5, 4.3], "front_blocked": blocked,
		"east_bypass_blocked": bypass }
	car.free()


## Run resource normalization separately from fresh runtime collision and production motion checks.
func _run() -> void:
	if Engine.is_editor_hint():
		await create_timer(EDITOR_STARTUP_SECONDS).timeout

	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.has("--normalize"):
		_roundtrip()
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

	_result["engine"] = Engine.get_version_info()["string"]
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var file: FileAccess = FileAccess.open(OUTPUT_PATH, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
