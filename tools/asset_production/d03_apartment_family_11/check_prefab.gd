@tool
extends SceneTree

const PREFAB: String = "res://scenes/prefabs/environment/d03_apartment_family_11.tscn"
const MODEL: String = (
	"res://art/models/environment/d03_apartment_family_11/d03_apartment_family_11.glb"
)
const WALL: String = "res://scenes/prefabs/environment/d03_apartment_family_07.tscn"
const CAP: String = "res://scenes/prefabs/environment/d03_apartment_family_10_end.tscn"
const ROOF: String = "res://scenes/prefabs/environment/d03_apartment_family_10_straight.tscn"
const BAY: String = "res://scenes/prefabs/environment/d03_apartment_family_05.tscn"
const OUTPUT: String = "C:/tmp/ft/assets/d03_apartment_family_11/prefab-check.json"
const EXPECTED: AABB = AABB(Vector3(-0.12, 3.18, -6.12), Vector3(0.62, 0.62, 12.24))
const TOLERANCE_M: float = 0.001
const CONTACT_TOLERANCE_M: float = 0.025
const WORLD_LAYER: int = 1
const ACTOR_RADIUS_M: float = 0.35
const ACTOR_HEIGHT_M: float = 1.8
const TEST_TICKS: int = 60
const EDITOR_STARTUP_SECONDS: float = 3.0

var _failures: Array[String] = []
var _result: Dictionary = {}


## Defer checks until the isolated headless tree is ready.
func _initialize() -> void:
	_run.call_deferred()


## Preserve failed expectations in logs and the final receipt.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Pack/save only the owned wrapper without rewriting linked siblings.
func _save_wrapper() -> void:
	var scene: PackedScene = ResourceLoader.load(
		PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	_expect(scene != null, "All dependencies load before saving")
	var instance: Node = scene.instantiate()
	var packed: PackedScene = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Pack wrapper")
	_expect(ResourceSaver.save(packed, PREFAB) == OK, "Save wrapper")
	instance.free()


## Prove two subsequent reload/save cycles preserve every saved byte and identity.
func _roundtrip() -> void:
	_save_wrapper()
	var first: String = FileAccess.get_sha256(PREFAB)
	_save_wrapper()
	var second: String = FileAccess.get_sha256(PREFAB)
	_save_wrapper()
	var third: String = FileAccess.get_sha256(PREFAB)
	_expect(first == second and second == third, "Two byte-stable roundtrips")
	_result["normalized_sha256"] = first
	_result["byte_stable"] = first == second and second == third
	_result["stable_reload_count"] = 2


## Verify identity-linked flashing and the unchanged elevated wall/cap instances.
func _inspect(instance: Node3D) -> void:
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == MODEL, "Linked flashing GLB")
	_expect(model.transform == Transform3D.IDENTITY, "Identity flashing model")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "One new mesh")
	var mesh_instance: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh_instance.global_transform * mesh_instance.get_aabb()
	_expect(bounds.position.distance_to(EXPECTED.position) < TOLERANCE_M, "Flashing min")
	_expect(bounds.size.distance_to(EXPECTED.size) < TOLERANCE_M, "Flashing size")
	_expect(mesh_instance.mesh.resource_path.begins_with(MODEL), "Flashing mesh linkage")
	_expect(bounds.position.y > 2.5, "Overhead-only new geometry")
	_materials(mesh_instance)
	var wall: Node3D = instance.get_node("UpperWall") as Node3D
	var cap: Node3D = instance.get_node("UpperEndCap") as Node3D
	_expect(wall.scene_file_path == WALL, "Reused end wall")
	_expect(cap.scene_file_path == CAP, "Reused end cap")
	var offset: Transform3D = Transform3D(Basis.IDENTITY, Vector3(0, 3.2, 0))
	_expect(wall.transform == offset and cap.transform == offset, "Elevated placements")
	_inspect_collision(instance)
	_composite_bounds(instance)
	_result["flashing_aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["flashing_aabb_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_result["linked_model_identity"] = true
	_result["unchanged_wall_and_cap_links"] = true
	_inspect_uids()


## Measure the full delivered component including both linked sibling meshes.
func _composite_bounds(instance: Node3D) -> void:
	var meshes: Array[Node] = instance.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 3, "Three linked meshes in complete component")
	var bounds: AABB
	var surface_count: int = 0
	for index: int in range(meshes.size()):
		var visual: MeshInstance3D = meshes[index] as MeshInstance3D
		var part: AABB = visual.global_transform * visual.get_aabb()
		bounds = part if index == 0 else bounds.merge(part)
		surface_count += visual.mesh.get_surface_count()

	_expect(bounds.position.distance_to(Vector3(-0.12, 3.18, -6.12)) < TOLERANCE_M,
		"Composite minimum")
	_expect(bounds.end.distance_to(Vector3(0.5, 6.72, 6.12)) < TOLERANCE_M, "Composite maximum")
	_expect(surface_count == 8, "Composite surface count")
	_result["composite_aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["composite_aabb_max"] = [bounds.end.x, bounds.end.y, bounds.end.z]
	_result["composite_mesh_count"] = meshes.size()
	_result["composite_surface_count"] = surface_count


## Require the sole collider to be the inherited wall slab, not a new flashing blocker.
func _inspect_collision(instance: Node3D) -> void:
	var shapes: Array[Node] = instance.find_children("*", "CollisionShape3D", true, false)
	_expect(shapes.size() == 1, "One unchanged inherited wall collider")
	var shape: CollisionShape3D = instance.get_node("UpperWall/Collision/Body/Core")
	_expect(shapes[0] == shape, "Collider belongs to linked wall")
	var box: BoxShape3D = shape.shape as BoxShape3D
	_expect(box.size == Vector3(0.24, 3.2, 12), "Unchanged wall dimensions")
	_expect(shape.global_position.distance_to(Vector3(0, 4.8, 0)) < TOLERANCE_M,
		"Elevated wall collider datum")
	var body: StaticBody3D = shape.get_parent() as StaticBody3D
	_expect(body.collision_layer == WORLD_LAYER and body.collision_mask == 0, "World-only layer")
	_result["collision_shape_count"] = shapes.size()
	_result["collision_min"] = [-0.12, 3.2, -6]
	_result["collision_max"] = [0.12, 6.4, 6]


## Compare both imported materials against the delivered roof cap by stable material name.
func _materials(mesh: MeshInstance3D) -> void:
	var sibling: Node = (load(ROOF) as PackedScene).instantiate()
	var reference: MeshInstance3D = sibling.get_node("Visuals/Model").find_children(
		"*", "MeshInstance3D", true, false)[0] as MeshInstance3D
	_expect(mesh.mesh.get_surface_count() == 2, "Two flashing surfaces")
	for index: int in range(2):
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(index) as BaseMaterial3D
		var original: BaseMaterial3D = reference.mesh.surface_get_material(
			2 if index == 0 else 1) as BaseMaterial3D
		_expect(material.resource_name == original.resource_name, "Family material name")
		_expect(material.albedo_color == original.albedo_color, "Family color")
		_expect(material.roughness == original.roughness, "Family roughness")
		_expect(material.metallic == original.metallic, "Family metallic")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Backface culling")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque material")

	_result["family_materials_match"] = true
	sibling.free()


## Require the wrapper, GLB and reused prefab identities to resolve through the engine.
func _inspect_uids() -> void:
	var identities: Dictionary = {}
	for path: String in [PREFAB, MODEL, WALL, CAP]:
		var uid: int = ResourceLoader.get_resource_uid(path)
		_expect(uid != ResourceUID.INVALID_ID, "UID resolves: " + path)
		identities[path] = ResourceUID.id_to_text(uid)

	_result["resource_uids"] = identities


## Probe inherited wall solids, lower-roof clearance and ground frontage of actual hosts.
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
		Vector4(0, 4.5, 0, 1), Vector4(0.6, 4.5, 0, 0),
		Vector4(0, 0.9, -6.8, 0), Vector4(0, 0.9, 6.8, 0),
		Vector4(-0.12, 1.1, -5.9, 1), Vector4(-0.12, 3.2, -5.9, 1),
	]
	for test: Vector4 in cases:
		query.transform.origin = Vector3(test.x, test.y, test.z)
		var solid: bool = not space.intersect_shape(query).is_empty()
		_expect(solid == bool(test.w), "Capsule solid/clear expectation")
		observations.append({ "position": [test.x, test.y, test.z], "solid": solid })

	_result["capsule_queries"] = observations
	_wall_ray(space)
	var car_box: BoxShape3D = BoxShape3D.new()
	car_box.size = Vector3(1.9, 1.5, 4.3)
	query.shape = car_box
	query.transform = Transform3D(Basis(Vector3.UP, PI / 2.0), Vector3(0, 0.75, -7.5))
	_expect(space.intersect_shape(query).is_empty(), "Frontage car-sized clearance")
	_result["frontage_car_box_clear"] = true


## Cast through the exposed upper wall at its exact positive-X datum.
func _wall_ray(space: PhysicsDirectSpaceState3D) -> void:
	var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
		Vector3(2, 4.8, 0), Vector3(-2, 4.8, 0), WORLD_LAYER)
	var hit: Dictionary = space.intersect_ray(ray)
	_expect(not hit.is_empty(), "Exposed wall remains solid")
	if not hit.is_empty():
		_expect(absf(hit["position"].x - 0.12) < TOLERANCE_M, "Wall hit datum")
		_result["wall_hit_x"] = hit["position"].x


## Add only a physics test floor, never generated visible content or a prefab dependency.
func _add_test_floor() -> StaticBody3D:
	var body: StaticBody3D = StaticBody3D.new()
	var shape: CollisionShape3D = CollisionShape3D.new()
	var box: BoxShape3D = BoxShape3D.new()
	box.size = Vector3(40, 0.2, 40)
	shape.shape = box
	shape.position.y = -0.1
	body.add_child(shape)
	root.add_child(body)
	return body


## Provide independent expected positions for seam crossing and the closed front stop.
func _motion_cases() -> Array[Dictionary]:
	return [
		{ "name": "frontage_bypass", "start": Vector3(-3, 0, -6.8),
			"move": Vector2.RIGHT, "end": Vector3(2, 0, -6.8) },
		{ "name": "closed_front", "start": Vector3(0, 0, -9),
			"move": Vector2.DOWN, "end": Vector3(0, 0, -6.35) },
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
	for index: int in range(2):
		_expect(observations[index]["end"] == observations[index + 2]["end"], "Mode equivalence")

	floor_body.free()


## Use the documented high/low transforms relative to the .11 anchor for bounded tests.
func _host_context() -> Array[Node3D]:
	var packed: PackedScene = load(BAY) as PackedScene
	var hosts: Array[Node3D] = []
	for position: Vector3 in [Vector3(-3.12, 0, 0), Vector3(-3.12, 3.2, 0), Vector3(2.88, 0, 0)]:
		var host: Node3D = packed.instantiate() as Node3D
		host.position = position
		root.add_child(host)
		hosts.append(host)

	_result["host_positions"] = [[-3.12, 0, 0], [-3.12, 3.2, 0], [2.88, 0, 0]]
	return hosts


## Wait for editor scans before serializing UIDs or stopping the isolated editor process.
func _wait_for_scan() -> void:
	if not Engine.is_editor_hint():
		return

	await create_timer(EDITOR_STARTUP_SECONDS).timeout
	while EditorInterface.get_resource_filesystem().is_scanning():
		await create_timer(1.0).timeout  # gdstyle:ignore=quality/await-in-loop


## Run clean runtime resource/physics checks separately from headless editor normalization.
func _run() -> void:
	await _wait_for_scan()
	var normalize: bool = OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		if not Engine.is_editor_hint():
			push_error("Normalization requires --editor to preserve UIDs")
			quit(1)
			return

		_roundtrip()
	else:
		var instance: Node3D = (load(PREFAB) as PackedScene).instantiate() as Node3D
		root.add_child(instance)
		_inspect(instance)
		var hosts: Array[Node3D] = _host_context()
		await physics_frame
		await physics_frame
		_queries(instance)
		await _motion_checks()
		for host: Node3D in hosts:
			host.free()

		instance.free()
		_result["roundtrip"] = JSON.parse_string(
			FileAccess.get_file_as_string(OUTPUT + ".roundtrip"))

	_result["engine"] = Engine.get_version_info()["string"]
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var path: String = OUTPUT + ".roundtrip" if normalize else OUTPUT
	var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	await _wait_for_scan()
	quit(0 if _failures.is_empty() else 1)
