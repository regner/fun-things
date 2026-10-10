extends SceneTree

const PREFAB_PATH: String = "res://scenes/prefabs/environment/d04_towers_03.tscn"
const MODEL_PATH: String = "res://art/models/environment/d04_towers_03/d04_towers_03.glb"
const DEFAULT_OUTPUT: String = "C:/tmp/ft/assets/d04_towers_03/prefab-check.json"
const EXPECTED_BOUNDS: AABB = AABB(Vector3(-12, 0, -10.2), Vector3(24, 43.2, 19.2))
const TOLERANCE_M: float = 0.001
const WORLD_LAYER: int = 1

var _failures: Array[String] = []
var _result: Dictionary = {}


## Start after the scene tree is ready to register isolated physics objects.
func _initialize() -> void:
	_run.call_deferred()


## Retain failed expectations and return a failing process exit.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Allocate the owned scene UID once, retaining it on subsequent headless saves.
func _save_scene() -> void:
	var header: String = FileAccess.get_file_as_string(PREFAB_PATH).get_slice("\n", 0)
	var uid: int = ResourceUID.INVALID_ID
	if header.contains("uid=\""):
		uid = ResourceUID.text_to_id(header.get_slice("uid=\"", 1).get_slice("\"", 0))

	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()

	if not ResourceUID.has_id(uid):
		ResourceUID.add_id(uid, PREFAB_PATH)

	var source: PackedScene = ResourceLoader.load(
		PREFAB_PATH, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	_expect(source != null, "Prefab dependencies must resolve before save")
	if source == null:
		return

	var instance: Node = source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed: PackedScene = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Prefab pack failed")
	_expect(ResourceSaver.save(packed, PREFAB_PATH) == OK, "Prefab save failed")
	_expect(ResourceSaver.set_uid(PREFAB_PATH, uid) == OK, "Prefab UID save failed")
	instance.free()


## Normalize and then prove two save/reload roundtrips preserve complete bytes and identities.
func _roundtrip() -> void:
	_save_scene()
	var first: String = FileAccess.get_sha256(PREFAB_PATH)
	_save_scene()
	var second: String = FileAccess.get_sha256(PREFAB_PATH)
	_save_scene()
	var stable: bool = first == second and second == FileAccess.get_sha256(PREFAB_PATH)
	_result["save_reload_byte_stable"] = stable
	_result["stable_roundtrip_count"] = 2
	_expect(stable, "Prefab save/reload changed bytes")


## Inspect all source-linked sections, aggregate bounds, imported materials and solid envelopes.
func _inspect(instance: Node3D) -> void:
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == MODEL_PATH, "Model lost linked GLB ancestry")
	_expect(model.transform == Transform3D.IDENTITY, "Model transform is not identity")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 3, "Expected lobby, facade and crown meshes")
	var bounds: AABB
	var initialized: bool = false
	var surface_count: int = 0
	var materials: Array[String] = []
	for node: Node in meshes:
		var mesh: MeshInstance3D = node as MeshInstance3D
		_expect(mesh.mesh.resource_path.begins_with(MODEL_PATH), "Mesh must remain imported")
		var section: AABB = mesh.global_transform * mesh.get_aabb()
		bounds = bounds.merge(section) if initialized else section
		initialized = true
		surface_count += mesh.mesh.get_surface_count()
		for index: int in range(mesh.mesh.get_surface_count()):
			var material: BaseMaterial3D = mesh.mesh.surface_get_material(index) as BaseMaterial3D
			_expect(material != null, "Missing imported material")
			_expect(
				material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED,
				"Opaque material",
			)
			_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back-culling material")
			if not materials.has(material.resource_name):
				materials.append(material.resource_name)

	_expect(bounds.position.distance_to(EXPECTED_BOUNDS.position) < TOLERANCE_M, "Bounds min")
	_expect(bounds.size.distance_to(EXPECTED_BOUNDS.size) < TOLERANCE_M, "Bounds size")
	_expect(surface_count == 12 and materials.size() == 7, "Twelve surfaces / seven materials")
	_result["aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["aabb_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_result["mesh_count"] = meshes.size()
	_result["surface_count"] = surface_count
	_result["materials"] = materials
	_result["linked_model_identity"] = model.transform == Transform3D.IDENTITY
	_inspect_collision_and_uids(instance)


## Verify the two-box envelope and registered identities independently from presentation.
func _inspect_collision_and_uids(instance: Node3D) -> void:
	var body: StaticBody3D = instance.get_node("Collision/Body") as StaticBody3D
	_expect(body.collision_layer == WORLD_LAYER and body.collision_mask == 0, "Static world layers")
	_expect(body.get_child_count() == 2, "Expected minimal two-box compound")
	var lobby: CollisionShape3D = body.get_node("Lobby") as CollisionShape3D
	var shaft: CollisionShape3D = body.get_node("Shaft") as CollisionShape3D
	_expect((lobby.shape as BoxShape3D).size == Vector3(24, 6, 18), "Lobby collision size")
	_expect(lobby.position == Vector3(0, 3, 0), "Lobby ground datum")
	_expect((shaft.shape as BoxShape3D).size == Vector3(22, 32.4, 16), "Shaft collision size")
	_expect(shaft.position == Vector3(0, 22.2, 0), "Shaft/lobby collision join")
	_result["collision_shape_count"] = body.get_child_count()
	var prefab_uid: int = ResourceLoader.get_resource_uid(PREFAB_PATH)
	var model_uid: int = ResourceLoader.get_resource_uid(MODEL_PATH)
	_expect(prefab_uid != ResourceUID.INVALID_ID, "Prefab UID must resolve after import")
	_expect(model_uid != ResourceUID.INVALID_ID, "GLB UID must resolve from import sidecar")
	_result["prefab_uid"] = ResourceUID.id_to_text(prefab_uid)
	_result["model_uid"] = ResourceUID.id_to_text(model_uid)


## Verify closed doors, corner coverage, facade setback and clear under-canopy ground.
func _physics_checks(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var sphere: SphereShape3D = SphereShape3D.new()
	sphere.radius = 0.1
	var cases: Array[Dictionary] = [
		{ "name": "interior_solid", "point": Vector3(0, 1, 0), "solid": true },
		{ "name": "closed_lobby_door", "point": Vector3(0, 1, -8.95), "solid": true },
		{ "name": "under_canopy_clear", "point": Vector3(0, 1, -9.5), "solid": false },
		{ "name": "rear_wall_solid", "point": Vector3(0, 1, 8.95), "solid": true },
		{ "name": "east_wall_solid", "point": Vector3(11.95, 1, 0), "solid": true },
		{ "name": "west_walk_clear", "point": Vector3(-12.2, 1, 0), "solid": false },
		{ "name": "east_walk_clear", "point": Vector3(12.2, 1, 0), "solid": false },
		{ "name": "front_left_corner", "point": Vector3(-11.95, 1, -8.95), "solid": true },
		{ "name": "rear_right_corner", "point": Vector3(11.95, 1, 8.95), "solid": true },
		{ "name": "lobby_top_solid", "point": Vector3(11.5, 5.5, 0), "solid": true },
		{ "name": "setback_clear", "point": Vector3(11.5, 6.5, 0), "solid": false },
		{ "name": "section_join_solid", "point": Vector3(0, 6, 0), "solid": true },
		{ "name": "shaft_top_solid", "point": Vector3(0, 38.2, 0), "solid": true },
		{ "name": "overhead_crown_visual_only", "point": Vector3(0, 42.5, 0), "solid": false },
		{ "name": "above_camera_clear", "point": Vector3(0, 50, 0), "solid": false },
		{ "name": "crown_trim_nonblocking", "point": Vector3(11.6, 42.6, 0), "solid": false },
	]
	var observations: Array[Dictionary] = []
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = sphere
	query.collision_mask = WORLD_LAYER
	for test: Dictionary in cases:
		query.transform.origin = test["point"]
		var solid: bool = not space.intersect_shape(query).is_empty()
		_expect(solid == test["solid"], "Shape query failed: " + str(test["name"]))
		observations.append({ "case": test["name"], "solid": solid })

	var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
		Vector3(0, 1, -15), Vector3(0, 1, 0), WORLD_LAYER
	)
	var hit: Dictionary = space.intersect_ray(ray)
	_expect(not hit.is_empty(), "Front ray should hit the closed tower lobby")
	if not hit.is_empty():
		var position: Vector3 = hit["position"]
		_expect(absf(position.z + 9) < TOLERANCE_M, "Front collision face at -9 m")
		_result["front_ray_hit"] = [position.x, position.y, position.z]

	_result["physics_shape_queries"] = observations
	_motion_checks(space)


## Exercise actor/car envelope casts without claiming controller or transport acceptance.
func _motion_checks(space: PhysicsDirectSpaceState3D) -> void:
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = 0.35
	capsule.height = 1.8
	var car: BoxShape3D = BoxShape3D.new()
	car.size = Vector3(1.8, 1.5, 4.4)
	var sweeps: Array[Dictionary] = [
		_sweep(space, capsule, "actor_front", Vector3(0, 0.9, -14), Vector3(0, 0, 8)),
		_sweep(space, capsule, "actor_rear", Vector3(0, 0.9, 14), Vector3(0, 0, -8)),
		_sweep(space, capsule, "actor_end", Vector3(16, 0.9, 0), Vector3(-8, 0, 0)),
		_sweep(space, capsule, "actor_bypass", Vector3(12.6, 0.9, -14), Vector3(0, 0, 28)),
		_sweep(space, capsule, "canopy_bypass", Vector3(-8, 0.9, -9.6), Vector3(16, 0, 0)),
		_sweep(space, car, "car_front", Vector3(0, 0.8, -16), Vector3(0, 0, 12)),
		_sweep(space, car, "car_bypass", Vector3(13.3, 0.8, -16), Vector3(0, 0, 32)),
	]
	for index: int in range(sweeps.size()):
		var expected_blocked: bool = index in [0, 1, 2, 5]
		_expect(sweeps[index]["blocked"] == expected_blocked, "Motion case " + str(index))

	_result["physics_motion_casts"] = sweeps


## Cast measured test envelopes through the actual PhysicsDirectSpaceState3D API.
func _sweep(
	space: PhysicsDirectSpaceState3D,
	shape: Shape3D,
	label: String,
	start: Vector3,
	motion: Vector3
) -> Dictionary:
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform.origin = start
	query.motion = motion
	query.collision_mask = WORLD_LAYER
	var fractions: PackedFloat32Array = space.cast_motion(query)
	_expect(fractions.size() == 2, "Expected safe/unsafe motion fractions")
	return { "case": label, "blocked": fractions[0] < 1.0, "safe_fraction": fractions[0] }


## Load, inspect and query the saved prefab in a fresh headless process.
func _run() -> void:
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.has("--normalize"):
		_roundtrip()

	var packed: PackedScene = ResourceLoader.load(
		PREFAB_PATH, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	_expect(packed != null, "Prefab dependencies must resolve")
	if packed != null:
		var instance: Node3D = packed.instantiate() as Node3D
		root.add_child(instance)
		_inspect(instance)
		await physics_frame
		await physics_frame
		_physics_checks(instance)
		instance.queue_free()
		await process_frame

	_result["engine"] = Engine.get_version_info()["string"]
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var output: String = DEFAULT_OUTPUT
	var index: int = arguments.find("--output")
	if index >= 0 and index + 1 < arguments.size():
		output = arguments[index + 1]

	var file: FileAccess = FileAccess.open(output, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
