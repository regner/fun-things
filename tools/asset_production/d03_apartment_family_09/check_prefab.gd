@tool
extends SceneTree

const PREFAB_PATH: String = "res://scenes/prefabs/environment/d03_apartment_family_09.tscn"
const MODEL_PATH: String = (
	"res://art/models/environment/d03_apartment_family_09/d03_apartment_family_09.glb"
)
const STRAIGHT_PATH: String = "res://scenes/prefabs/environment/d03_apartment_family_05.tscn"
const OUTPUT_PATH: String = "C:/tmp/ft/assets/d03_apartment_family_09/prefab-check.json"
const EXPECTED_BOUNDS: AABB = AABB(Vector3(-2.7, 3.2, -1.5), Vector3(5.4, 1.28, 1.5))
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


## Check real imported ancestry, transforms, bounds, opaque materials and overhead-only bounds.
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
	_expect(mesh_instance.mesh.get_surface_count() == 3, "Three material surfaces")
	_materials(mesh_instance)

	_expect(instance.find_children("*", "CollisionObject3D", true, false).is_empty(),
		"Approved unreachable balcony is visual-only")
	_expect(instance.find_children("*", "CollisionShape3D", true, false).is_empty(),
		"No walkable deck or guard collider")
	_expect(bounds.position.y > 2.5, "Entire balcony is above the overhead-only threshold")
	_result["aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["aabb_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_result["linked_model_identity"] = model.transform == Transform3D.IDENTITY
	_result["collision_shape_count"] = 0
	_result["minimum_underside_m"] = bounds.position.y
	_inspect_uids()


## Compare imported slot names and PBR values to the already-delivered straight bay.
func _materials(mesh: MeshInstance3D) -> void:
	var sibling: Node = (load(STRAIGHT_PATH) as PackedScene).instantiate()
	var sibling_mesh: MeshInstance3D = sibling.get_node("Visuals/Model").find_children(
		"*", "MeshInstance3D", true, false)[0] as MeshInstance3D
	for index: int in range(3):
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(index) as BaseMaterial3D
		_expect(material != null, "Material dependency")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque material")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Backface culling")
		if index < 3:
			var original: BaseMaterial3D = (
				sibling_mesh.mesh.surface_get_material(index) as BaseMaterial3D
			)
			_expect(material.resource_name == original.resource_name, "Family slot names")
			_expect(material.albedo_color == original.albedo_color, "Family color matching")
			_expect(material.roughness == original.roughness, "Family roughness matching")
			_expect(material.metallic == original.metallic, "Family metallic matching")

	_result["family_materials_match"] = true
	sibling.free()


## Require both the saved wrapper and imported model identities to resolve through the engine.
func _inspect_uids() -> void:
	var prefab_uid: int = ResourceLoader.get_resource_uid(PREFAB_PATH)
	var model_uid: int = ResourceLoader.get_resource_uid(MODEL_PATH)
	_expect(prefab_uid != ResourceUID.INVALID_ID, "Prefab UID resolves")
	_expect(model_uid != ResourceUID.INVALID_ID, "Model UID resolves")
	_result["prefab_uid"] = ResourceUID.id_to_text(prefab_uid)
	_result["model_uid"] = ResourceUID.id_to_text(model_uid)


## Prove the real mounted balcony does not obstruct the ground, while its host facade stays closed.
func _queries(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = ACTOR_RADIUS_M
	capsule.height = ACTOR_HEIGHT_M
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = WORLD_LAYER
	var observations: Array[Dictionary] = []
	for x: float in [-2.0, 0.0, 2.0]:
		query.transform.origin = Vector3(x, 0.9, -0.8)
		var solid: bool = not space.intersect_shape(query).is_empty()
		_expect(not solid, "Ground capsule below balcony stays clear")
		observations.append({ "x": x, "solid": solid })

	_result["below_balcony_capsule_queries"] = observations
	var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
		Vector3(0, 4.0, -3), Vector3(0, 4.0, 2), WORLD_LAYER
	)
	var hit: Dictionary = space.intersect_ray(ray)
	_expect(not hit.is_empty(), "Host upper facade remains closed")
	if not hit.is_empty():
		_expect(absf(hit["position"].z) < TOLERANCE_M, "Unchanged host facade datum")
		_result["closed_host_front_ray_z"] = hit["position"].z

	var car_box: BoxShape3D = BoxShape3D.new()
	car_box.size = Vector3(1.9, 1.5, 4.3)
	query.shape = car_box
	query.transform = Transform3D(Basis(Vector3.UP, PI / 2.0), Vector3(0, 0.75, -1.2))
	_expect(space.intersect_shape(query).is_empty(), "Car-sized box below balcony stays clear")
	_result["below_balcony_car_box_clear"] = true


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


## Traverse the ground beneath the actual overhang without introducing balcony access.
func _motion_cases() -> Array[Dictionary]:
	return [
		{ "name": "under_balcony", "start": Vector3(-4, 0, -0.8),
			"move": Vector2.RIGHT, "end": Vector3(1, 0, -0.8) },
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


## Instance existing closed bays at the numeric mounting interface for bounded checks only.
func _host_context() -> Array[Node3D]:
	var packed: PackedScene = load(STRAIGHT_PATH) as PackedScene
	var lower: Node3D = packed.instantiate() as Node3D
	var upper: Node3D = packed.instantiate() as Node3D
	lower.position = Vector3(0, 0, 6)
	upper.position = Vector3(0, 3.2, 6)
	root.add_child(lower)
	root.add_child(upper)
	_result["host_ground_origin"] = [0, 0, 6]
	_result["host_upper_origin"] = [0, 3.2, 6]
	return [lower, upper]


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
		var hosts: Array[Node3D] = _host_context()
		await physics_frame
		await physics_frame
		_queries(instance)
		await _actor_motion_checks()
		for host: Node3D in hosts:
			host.free()

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
