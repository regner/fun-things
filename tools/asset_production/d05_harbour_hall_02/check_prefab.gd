extends SceneTree

const PREFAB_PATH: String = "res://scenes/prefabs/environment/d05_harbour_hall_02.tscn"
const PREVIEW_PATH: String = (
	"res://scenes/prefabs/environment/d05_harbour_hall_02_hall_preview.tscn"
)
const HALL_PATH: String = "res://scenes/prefabs/environment/d05_harbour_hall_01.tscn"
const MODEL_PATH: String = (
	"res://art/models/environment/d05_harbour_hall_02/d05_harbour_hall_02.glb"
)
const DEFAULT_OUTPUT: String = "C:/tmp/ft/assets/d05_harbour_hall_02/prefab-check.json"
const EXPECTED_BOUNDS: AABB = AABB(Vector3(-4, -.05, -2.4), Vector3(8, .45, 2.4))
const MOUNT: Vector3 = Vector3(0, 3.85, -9)
const LINTEL_TOP_M: float = 3.74
const LANDING_TOP_M: float = .3
const TOLERANCE_M: float = .001
const EDITOR_STARTUP_FRAMES: int = 10
const WORLD_LAYER: int = 1
const ACTOR_RADIUS_M: float = .35
const ACTOR_HEIGHT_M: float = 1.8

var _failures: Array[String] = []
var _result: Dictionary = {}


## Defer until the headless scene tree is initialized.
func _initialize() -> void:
	_run.call_deferred()


## Record assertion failures and return a nonzero final exit.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Normalize only owned scenes and prove a second pack/save preserves bytes and identities.
func _roundtrip(path: String) -> void:
	var original: PackedScene = load(path) as PackedScene
	_expect(original != null, "Prefab must load before normalization: " + path)
	if original == null:
		return

	var instance: Node = original.instantiate()
	var packed: PackedScene = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Prefab pack failed")
	_expect(ResourceSaver.save(packed, path) == OK, "Prefab save failed")
	instance.free()
	var first: String = FileAccess.get_sha256(path)
	var reloaded: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	instance = reloaded.instantiate()
	packed = PackedScene.new()
	_expect(packed.pack(instance) == OK, "Reloaded prefab pack failed")
	_expect(ResourceSaver.save(packed, path) == OK, "Reloaded prefab save failed")
	instance.free()
	_expect(first == FileAccess.get_sha256(path), "Second prefab save changed bytes")


## Inspect the actual imported mesh and confirm a wall-pivot visual-only component.
func _inspect(instance: Node3D) -> AABB:
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
	_expect(mesh_instance.mesh.get_surface_count() == 3, "Expected three material surfaces")
	var materials: Array[String] = []
	for index: int in range(mesh_instance.mesh.get_surface_count()):
		var material: BaseMaterial3D = (
			mesh_instance.mesh.surface_get_material(index) as BaseMaterial3D
		)
		_expect(material != null, "Missing imported material")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque material")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back-culling material")
		materials.append(material.resource_name)

	_expect(instance.find_children("*", "CollisionObject3D", true, false).is_empty(),
		"Above-head canopy must not add collision")
	_result["aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["aabb_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_result["materials"] = materials
	_result["mesh_count"] = meshes.size()
	_result["collision_object_count"] = 0
	_result["linked_model_identity"] = model.transform == Transform3D.IDENTITY
	return bounds


## Check the saved sibling attachment, literal clearances and unchanged hall collision ownership.
func _inspect_mount(preview: Node3D, local_bounds: AABB) -> void:
	var hall: Node3D = preview.get_node("Hall") as Node3D
	var canopy: Node3D = preview.get_node("Canopy") as Node3D
	_expect(hall.scene_file_path == HALL_PATH, "Hall must remain a linked sibling prefab")
	_expect(hall.transform == Transform3D.IDENTITY, "Hall placement must stay at identity")
	_expect(canopy.scene_file_path == PREFAB_PATH, "Canopy must remain a linked prefab")
	_expect(canopy.position == MOUNT and canopy.basis == Basis.IDENTITY, "Wrong canopy mount")
	var mounted: AABB = canopy.global_transform * local_bounds
	_expect(absf(mounted.end.z + 9) < TOLERANCE_M, "Canopy back must contact wall Z=-9")
	_expect(absf(mounted.position.y - 3.8) < TOLERANCE_M, "Lowest point must be Y=3.8")
	_expect(absf(mounted.position.z + 11.4) < TOLERANCE_M, "Front projection must reach Z=-11.4")
	_expect(mounted.position.y - LINTEL_TOP_M > .059, "Canopy must clear the lintel")
	_expect(mounted.position.y - LANDING_TOP_M > 3.49, "Canopy must clear landing by 3.5 m")
	_expect(preview.find_children("*", "CollisionShape3D", true, false).size() == 3,
		"Mount preview must retain only the hall's three colliders")
	_result["mount_godot"] = [canopy.position.x, canopy.position.y, canopy.position.z]
	_result["mounted_min"] = [mounted.position.x, mounted.position.y, mounted.position.z]
	_result["mounted_max"] = [mounted.end.x, mounted.end.y, mounted.end.z]
	_result["lintel_gap_m"] = mounted.position.y - LINTEL_TOP_M
	_result["landing_clearance_m"] = mounted.position.y - LANDING_TOP_M


## Query the actual combined scene to confirm clear overhead space and the existing closed facade.
func _query_mount(preview: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = preview.get_world_3d().direct_space_state
	var capsule: CapsuleShape3D = CapsuleShape3D.new()
	capsule.radius = ACTOR_RADIUS_M
	capsule.height = ACTOR_HEIGHT_M
	var query: PhysicsShapeQueryParameters3D = PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = WORLD_LAYER
	var observations: Array[Dictionary] = []
	for point: Vector3 in [Vector3(0, 1.21, -9.8), Vector3(3, 1.21, -10.5)]:
		query.transform.origin = point
		var clear: bool = space.intersect_shape(query).is_empty()
		_expect(clear, "Standing capsule must fit under mounted canopy")
		observations.append({ "point": [point.x, point.y, point.z], "clear": clear })

	var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
		Vector3(0, 1, -15), Vector3(0, 1, 0), WORLD_LAYER
	)
	var hit: Dictionary = space.intersect_ray(ray)
	_expect(not hit.is_empty(), "Closed hall must still block the front ray")
	if not hit.is_empty():
		var position: Vector3 = hit["position"]
		_expect(absf(position.z + 9.2) < TOLERANCE_M, "Hall collision moved")
		_result["front_ray_hit"] = [position.x, position.y, position.z]

	_result["standing_capsule_queries"] = observations


## Verify the engine-generated identities for both owned scenes and both linked assets.
func _inspect_uids() -> void:
	var uids: Dictionary = {}
	for path: String in [PREFAB_PATH, PREVIEW_PATH, MODEL_PATH, HALL_PATH]:
		var uid: int = ResourceLoader.get_resource_uid(path)
		_expect(uid != ResourceUID.INVALID_ID, "Resource UID must resolve: " + path)
		uids[path] = ResourceUID.id_to_text(uid)

	_result["resource_uids"] = uids


## Run bounded resource/mounting checks without touching live editor sessions or world placement.
func _run() -> void:
	if Engine.is_editor_hint():
		for frame: int in range(EDITOR_STARTUP_FRAMES):
			await process_frame  # gdstyle:ignore=quality/await-in-loop

		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame  # gdstyle:ignore=quality/await-in-loop

	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.has("--normalize"):
		_roundtrip(PREFAB_PATH)
		_roundtrip(PREVIEW_PATH)
		_result["two_scene_save_reload_byte_stable"] = _failures.is_empty()

	var packed: PackedScene = load(PREFAB_PATH) as PackedScene
	var comparison: PackedScene = load(PREVIEW_PATH) as PackedScene
	_expect(packed != null and comparison != null, "All prefab dependencies must resolve")
	if packed != null and comparison != null:
		var instance: Node3D = packed.instantiate() as Node3D
		root.add_child(instance)
		var bounds: AABB = _inspect(instance)
		instance.queue_free()
		var preview: Node3D = comparison.instantiate() as Node3D
		root.add_child(preview)
		_inspect_mount(preview, bounds)
		if not Engine.is_editor_hint():
			await physics_frame
			await physics_frame
			_query_mount(preview)

		preview.queue_free()
		await process_frame

	_inspect_uids()
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
