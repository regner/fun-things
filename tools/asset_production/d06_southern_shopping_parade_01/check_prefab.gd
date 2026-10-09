@tool
extends SceneTree

const PREFAB_PATH: String = "res://scenes/prefabs/environment/d06_southern_shopping_parade_01.tscn"
const MODEL_PATH: String = (
	"res://art/models/environment/d06_southern_shopping_parade_01/"
	+ "d06_southern_shopping_parade_01.glb"
)
const DEFAULT_OUTPUT: String = "C:/tmp/ft/assets/d06_southern_shopping_parade_01/prefab-check.json"
const EXPECTED_BOUNDS: AABB = AABB(Vector3(-9.045, 0, -30.035), Vector3(18.085, 5.4, 60.07))
const TOLERANCE_M: float = 0.001
const WORLD_LAYER: int = 1
const EDITOR_STARTUP_SECONDS: float = 3.0

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


## Normalize only this owned prefab and prove that a second pack/save is byte-stable.
func _roundtrip() -> void:
	var original: PackedScene = load(PREFAB_PATH) as PackedScene
	_expect(original != null, "Prefab must load before normalization")
	if original == null:
		return

	var instance: Node = original.instantiate()
	var packed: PackedScene = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Prefab pack failed")
	_expect(ResourceSaver.save(packed, PREFAB_PATH) == OK, "Prefab save failed")
	instance.free()
	var first: String = FileAccess.get_sha256(PREFAB_PATH)
	var reloaded: PackedScene = ResourceLoader.load(
		PREFAB_PATH, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	instance = reloaded.instantiate()
	packed = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Reloaded prefab pack failed")
	_expect(ResourceSaver.save(packed, PREFAB_PATH) == OK, "Reloaded prefab save failed")
	instance.free()
	_result["save_reload_byte_stable"] = first == FileAccess.get_sha256(PREFAB_PATH)
	_expect(_result["save_reload_byte_stable"], "Second prefab save changed bytes")


## Inspect the linked import, its actual bounds/materials, and authored collision shapes.
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
	_expect(mesh_instance.mesh.get_surface_count() == 5, "Expected five material surfaces")
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
	_expect(body.get_child_count() == 1, "Expected single exterior solid box")
	_expect(
		(body.get_node("SolidFootprint").shape as BoxShape3D).size == Vector3(18, 5.25, 60),
		"Footprint box size"
	)
	_expect(body.get_node("SolidFootprint").position == Vector3(0, 2.625, 0),
		"Footprint box ground datum")
	_result["aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["aabb_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_result["materials"] = materials
	_result["mesh_count"] = meshes.size()
	_result["collision_shape_count"] = body.get_child_count()
	_result["linked_model_identity"] = model.transform == Transform3D.IDENTITY
	var prefab_uid: int = ResourceLoader.get_resource_uid(PREFAB_PATH)
	var model_uid: int = ResourceLoader.get_resource_uid(MODEL_PATH)
	_expect(prefab_uid != ResourceUID.INVALID_ID, "Prefab engine-generated UID must resolve")
	_expect(model_uid != ResourceUID.INVALID_ID, "Model UID must resolve from import sidecar")
	_result["prefab_uid"] = ResourceUID.id_to_text(prefab_uid)
	_result["model_uid"] = ResourceUID.id_to_text(model_uid)


## Verify the northmost fitting frame survives import with the intended westward orientation.
func _inspect_mount(model: Node3D) -> void:
	var station: Node3D = model.find_child("west_bay_01", true, false) as Node3D
	_expect(station != null, "West fitting station must survive import")
	if station != null:
		_result["west_bay_01_path_below_model"] = str(model.get_path_to(station))
		_expect(station.global_position.distance_to(Vector3(-9, 0, -25)) < TOLERANCE_M,
			"Northmost west station translation")
		_expect((-station.global_basis.z).distance_to(Vector3.LEFT) < TOLERANCE_M,
			"West fitting station outward axis")


## Query explicit solid/clear coordinates independent of the visual facade construction.
func _physics_checks(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var sphere: SphereShape3D = SphereShape3D.new()
	sphere.radius = 0.1
	var cases: Array[Dictionary] = [
		{ "name": "interior_solid", "point": Vector3(0, 1, 0), "solid": true },
		{ "name": "west_closed_entry", "point": Vector3(-8.95, 1, -26.95), "solid": true },
		{ "name": "north_forecourt_clear", "point": Vector3(0, 1, -30.4), "solid": false },
		{ "name": "south_route_clear", "point": Vector3(0, 1, 30.4), "solid": false },
		{ "name": "west_passage_clear", "point": Vector3(-9.4, 1, 0), "solid": false },
		{ "name": "east_passage_clear", "point": Vector3(9.4, 1, 0), "solid": false },
		{ "name": "above_roof_clear", "point": Vector3(0, 5.6, 0), "solid": false },
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
		Vector3(-15, 1, -26.95), Vector3(0, 1, -26.95), WORLD_LAYER
	)
	var hit: Dictionary = space.intersect_ray(ray)
	_expect(not hit.is_empty(), "Front ray should hit the closed parade")
	if not hit.is_empty():
		var hit_position: Vector3 = hit["position"]
		_expect(absf(hit_position.x + 9.0) < TOLERANCE_M, "West ray datum must be -9 m")
		_result["front_ray_hit"] = [hit_position.x, hit_position.y, hit_position.z]

	_result["physics_shape_queries"] = observations


## Run bounded resource and physics checks without starting the game or touching live editors.
func _run() -> void:
	if Engine.is_editor_hint():
		await create_timer(EDITOR_STARTUP_SECONDS).timeout

	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.has("--normalize"):
		_roundtrip()
		if Engine.is_editor_hint():
			print(JSON.stringify(_result))
			quit(0 if _failures.is_empty() else 1)
			return

	var packed: PackedScene = ResourceLoader.load(
		PREFAB_PATH, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	_expect(packed != null, "Prefab dependencies must resolve")
	if packed != null:
		var instance: Node3D = packed.instantiate() as Node3D
		root.add_child(instance)
		_inspect(instance)
		_inspect_mount(instance.get_node("Visuals/Model") as Node3D)
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
