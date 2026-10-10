extends SceneTree

const PREFAB_PATH: String = "res://scenes/prefabs/environment/d09_warehouses_01.tscn"
const MODEL_PATH: String = (
	"res://art/models/environment/d09_warehouses_01/d09_warehouses_01.glb"
)
const DEFAULT_OUTPUT: String = "C:/tmp/ft/assets/d09_warehouses_01/prefab-check.json"
const EXPECTED_BOUNDS: AABB = AABB(Vector3(-24.38, 0, -9.49), Vector3(48.76, 9.265, 18.98))
const TOLERANCE_M: float = 0.001
const WORLD_LAYER: int = 1

var _failures: Array[String] = []
var _result: Dictionary = {}


## Defer until the headless scene tree can register physics objects.
func _initialize() -> void:
	_run.call_deferred()


## Record a failed assertion and return a nonzero final exit rather than silently continuing.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Normalize only the owned prefab and prove two subsequent saves preserve bytes and identities.
func _roundtrip() -> void:
	_save_scene()
	var first: String = FileAccess.get_sha256(PREFAB_PATH)
	_save_scene()
	var second: String = FileAccess.get_sha256(PREFAB_PATH)
	_save_scene()
	_result["save_reload_byte_stable"] = first == second and second == FileAccess.get_sha256(
		PREFAB_PATH
	)
	_result["stable_roundtrip_count"] = 2
	_expect(_result["save_reload_byte_stable"], "Prefab save/reload changed bytes")


## Allocate a Godot UID once and preserve it across headless PackedScene saves.
func _save_scene() -> void:
	var header: String = FileAccess.get_file_as_string(PREFAB_PATH).get_slice("
", 0)
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


## Inspect the linked import, its actual bounds/materials, and the authored collision shape.
func _inspect(instance: Node3D) -> void:
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == MODEL_PATH, "Model lost linked GLB ancestry")
	_expect(model.transform == Transform3D.IDENTITY, "Model transform is not identity")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "Expected one imported mesh")
	var mesh_instance: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh_instance.global_transform * mesh_instance.get_aabb()
	_expect(bounds.position.distance_to(EXPECTED_BOUNDS.position) < TOLERANCE_M, "Bounds min")
	_expect(bounds.size.distance_to(EXPECTED_BOUNDS.size) < TOLERANCE_M, "Bounds size")
	_expect(mesh_instance.mesh.resource_path.begins_with(MODEL_PATH), "Mesh is not imported")
	_expect(mesh_instance.mesh.get_surface_count() == 7, "Expected seven material surfaces")
	var materials: Array[String] = []
	for index: int in range(mesh_instance.mesh.get_surface_count()):
		var material: BaseMaterial3D = (
			mesh_instance.mesh.surface_get_material(index) as BaseMaterial3D
		)
		_expect(material != null, "Missing imported material")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque material")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back-culling material")
		materials.append(material.resource_name)

	var body: StaticBody3D = instance.get_node("Collision/Body") as StaticBody3D
	_expect(body.collision_layer == WORLD_LAYER and body.collision_mask == 0, "Static world layers")
	_expect(body.get_child_count() == 1, "Expected one solid shell collider")
	var collision: CollisionShape3D = body.get_node("Shell") as CollisionShape3D
	_expect(
		(collision.shape as BoxShape3D).size.is_equal_approx(Vector3(48, 6.4, 18)),
		"Shell collision dimensions"
	)
	_expect(collision.position.is_equal_approx(Vector3(0, 3.2, 0)), "Ground collision datum")
	_result["aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["aabb_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_result["materials"] = materials
	_result["mesh_count"] = meshes.size()
	_result["collision_shape_count"] = body.get_child_count()
	_result["linked_model_identity"] = model.transform == Transform3D.IDENTITY
	var prefab_uid: int = ResourceLoader.get_resource_uid(PREFAB_PATH)
	var model_uid: int = ResourceLoader.get_resource_uid(MODEL_PATH)
	_expect(prefab_uid != ResourceUID.INVALID_ID, "Saved prefab UID must resolve after import")
	_expect(model_uid != ResourceUID.INVALID_ID, "Model UID must resolve from import sidecar")
	_result["prefab_uid"] = ResourceUID.id_to_text(prefab_uid)
	_result["model_uid"] = ResourceUID.id_to_text(model_uid)


## Query the saved solid envelope and independent actor/car sweeps through Godot physics APIs.
func _physics_checks(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var sphere: SphereShape3D = SphereShape3D.new()
	sphere.radius = 0.1
	var cases: Array[Dictionary] = [
		{ "name": "interior_solid", "point": Vector3(0, 1, 0), "solid": true },
		{ "name": "closed_loading_face", "point": Vector3(-9, 1, -8.95), "solid": true },
		{ "name": "front_apron_clear", "point": Vector3(-9, 1, -9.3), "solid": false },
		{ "name": "rear_annex_wall_solid", "point": Vector3(0, 1, 8.95), "solid": true },
		{ "name": "end_wall_solid", "point": Vector3(23.95, 1, 0), "solid": true },
		{ "name": "west_passage_clear", "point": Vector3(-24.4, 1, 0), "solid": false },
		{ "name": "east_passage_clear", "point": Vector3(24.4, 1, 0), "solid": false },
		{ "name": "roof_visual_only", "point": Vector3(0, 8, 0), "solid": false },
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
		Vector3(-9, 1, -15), Vector3(-9, 1, 0), WORLD_LAYER
	)
	var hit: Dictionary = space.intersect_ray(ray)
	_expect(not hit.is_empty(), "Front ray should hit the closed warehouse")
	if not hit.is_empty():
		var hit_position: Vector3 = hit["position"]
		_expect(absf(hit_position.z + 9.0) < TOLERANCE_M, "Front ray datum must be -9 m")
		_result["front_ray_hit"] = [hit_position.x, hit_position.y, hit_position.z]

	_result["physics_shape_queries"] = observations
	_motion_checks(space)


## Sweep actor and car envelopes into walls and through independent clear side routes.
func _motion_checks(space: PhysicsDirectSpaceState3D) -> void:
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = 0.35
	capsule.height = 1.8
	var car: BoxShape3D = BoxShape3D.new()
	car.size = Vector3(1.8, 1.5, 4.4)
	var sweeps: Array[Dictionary] = [
		_sweep(space, capsule, "actor_front", Vector3(-9, 0.9, -14), Vector3(0, 0, 8)),
		_sweep(space, capsule, "actor_rear", Vector3(0, 0.9, 14), Vector3(0, 0, -8)),
		_sweep(space, capsule, "actor_end", Vector3(28, 0.9, 0), Vector3(-8, 0, 0)),
		_sweep(space, capsule, "actor_bypass", Vector3(24.6, 0.9, -14), Vector3(0, 0, 28)),
		_sweep(space, car, "car_front", Vector3(-9, 0.8, -16), Vector3(0, 0, 12)),
		_sweep(space, car, "car_bypass", Vector3(25.3, 0.8, -16), Vector3(0, 0, 32)),
	]
	for index: int in range(sweeps.size()):
		var expected_blocked: bool = index in [0, 1, 2, 4]
		_expect(sweeps[index]["blocked"] == expected_blocked, "Motion case " + str(index))

	_result["physics_motion_casts"] = sweeps


## Cast measured test envelopes without claiming gameplay controller or transport acceptance.
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
	var collided: bool = fractions[0] < 1.0
	return { "case": label, "blocked": collided, "safe_fraction": fractions[0] }


## Run bounded resource and physics checks without starting the game or touching live editors.
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
	var output_index: int = arguments.find("--output")
	if output_index >= 0 and output_index + 1 < arguments.size():
		output = arguments[output_index + 1]

	var file: FileAccess = FileAccess.open(output, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
