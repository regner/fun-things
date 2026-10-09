extends SceneTree

const PREFAB_PATH: String = "res://scenes/prefabs/environment/d06_harbour_footbridge_01.tscn"
const MODEL_PATH: String = (
	"res://art/models/environment/d06_harbour_footbridge_01/d06_harbour_footbridge_01.glb"
)
const OUTPUT: String = "C:/tmp/ft/assets/d06_harbour_footbridge_01/prefab-check.json"
const EXPECTED_BOUNDS: AABB = AABB(Vector3(-3, -0.35, -3), Vector3(6.2526912, 0.35, 6.2526912))
const TOLERANCE_M: float = 0.001
const WORLD_LAYER: int = 1
const EDITOR_STARTUP_SECONDS: float = 3.0
const PROVISIONAL_SURFACE_HEIGHT_M: float = 5.5

var _failures: Array[String] = []
var _result: Dictionary = {}


## Wait for the headless tree to initialize before resource and physics checks.
func _initialize() -> void:
	_run.call_deferred()


## Accumulate explicit failures so a failed assertion always produces a nonzero exit.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Normalize only this new owned prefab and require an identical second saved serialization.
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


## Inspect actual imported geometry, source-linked materials and the four simple slab prisms.
func _inspect(instance: Node3D) -> void:
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == MODEL_PATH, "Model lost linked GLB ancestry")
	_expect(model.transform == Transform3D.IDENTITY, "Model must retain identity transform")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "Expected one imported mesh")
	if meshes.is_empty():
		return

	var mesh_instance: MeshInstance3D = meshes[0] as MeshInstance3D
	var bounds: AABB = mesh_instance.global_transform * mesh_instance.get_aabb()
	_expect(bounds.position.distance_to(EXPECTED_BOUNDS.position) < TOLERANCE_M, "AABB minimum")
	_expect(bounds.size.distance_to(EXPECTED_BOUNDS.size) < TOLERANCE_M, "AABB size")
	_expect(mesh_instance.mesh.resource_path.begins_with(MODEL_PATH), "Mesh must remain imported")
	_expect(mesh_instance.mesh.get_surface_count() == 3, "Three material surfaces")
	var materials: Array[String] = []
	for index: int in range(mesh_instance.mesh.get_surface_count()):
		var material: BaseMaterial3D = (
			mesh_instance.mesh.surface_get_material(index) as BaseMaterial3D
		)
		_expect(material != null, "Imported material must resolve")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque material")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back-culling material")
		materials.append(material.resource_name)

	var body: StaticBody3D = instance.get_node("Collision/Body") as StaticBody3D
	_expect(body.collision_layer == WORLD_LAYER and body.collision_mask == 0, "Static world layers")
	_expect(body.get_child_count() == 4, "Four slab-only convex collision shapes")
	for child: Node in body.get_children():
		var collision: CollisionShape3D = child as CollisionShape3D
		_expect(collision.shape is ConvexPolygonShape3D, "Only simple convex slab collision")

	_result["aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_result["aabb_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_result["materials"] = materials
	_result["mesh_count"] = meshes.size()
	_result["collision_shape_count"] = body.get_child_count()
	_result["linked_model_identity"] = model.transform == Transform3D.IDENTITY
	var prefab_uid: int = ResourceLoader.get_resource_uid(PREFAB_PATH)
	var model_uid: int = ResourceLoader.get_resource_uid(MODEL_PATH)
	_expect(prefab_uid != ResourceUID.INVALID_ID, "Prefab UID must exist after editor save")
	_expect(model_uid != ResourceUID.INVALID_ID, "Imported model UID must resolve")
	_result["prefab_uid"] = ResourceUID.id_to_text(prefab_uid)
	_result["model_uid"] = ResourceUID.id_to_text(model_uid)
	_check_sockets(instance, model)


## Compare public snapping markers with source empties and independent position/axis expectations.
func _check_sockets(instance: Node3D, model: Node3D) -> void:
	var expected: Array[Dictionary] = [
		{ "public": "North", "source": "socket_north", "position": Vector3(0, 0, -3),
			"forward": Vector3(0, 0, -1) },
		{ "public": "SouthEast", "source": "socket_south_east",
			"position": Vector3(2.121320344, 0, 2.121320344),
			"forward": Vector3(0.707106781, 0, 0.707106781) },
		{ "public": "West", "source": "socket_west", "position": Vector3(-3, 0, 0),
			"forward": Vector3(-1, 0, 0) },
	]
	var observations: Array[Dictionary] = []
	for test: Dictionary in expected:
		var marker: Node3D = instance.get_node("Sockets/" + str(test["public"])) as Node3D
		var source: Node3D = model.find_child(test["source"], true, false) as Node3D
		_expect(source != null, "Missing source marker " + str(test["source"]))
		if source == null:
			continue

		_expect(marker.global_transform.is_equal_approx(source.global_transform), "Socket mapping")
		_expect(marker.position.distance_to(test["position"]) < TOLERANCE_M, "Socket position")
		_expect((-marker.basis.z).distance_to(test["forward"]) < TOLERANCE_M, "Outward -Z")
		_expect(marker.basis.y.distance_to(Vector3.UP) < TOLERANCE_M, "Socket up axis")
		observations.append({ "socket": test["public"], "source_mapping_matches": true })

	_result["sockets"] = observations


## Check independent solid/void positions and slab-only headroom with public physics ray queries.
func _physics_checks(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var cases: Array[Dictionary] = [
		{ "name": "centre", "xz": Vector2(0, 0), "solid": true },
		{ "name": "north_portal", "xz": Vector2(0, -2.99), "solid": true },
		{ "name": "west_portal", "xz": Vector2(-2.99, 0), "solid": true },
		{ "name": "south_east_portal", "xz": Vector2(2.1, 2.1), "solid": true },
		{ "name": "north_west_recess", "xz": Vector2(-2.5, -2.5), "solid": false },
		{ "name": "south_west_recess", "xz": Vector2(-2.5, 2.5), "solid": false },
		{ "name": "east_recess", "xz": Vector2(2.8, -1), "solid": false },
		{ "name": "north_beyond_portal", "xz": Vector2(0, -3.1), "solid": false },
	]
	var observations: Array[Dictionary] = []
	for test: Dictionary in cases:
		var xz: Vector2 = test["xz"]
		var top: Vector3 = Vector3(xz.x, PROVISIONAL_SURFACE_HEIGHT_M + 1, xz.y)
		var bottom: Vector3 = Vector3(xz.x, PROVISIONAL_SURFACE_HEIGHT_M - 1, xz.y)
		var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
			top, bottom, WORLD_LAYER
		)
		var hit: Dictionary = space.intersect_ray(ray)
		_expect(not hit.is_empty() == test["solid"], "Ray case: " + str(test["name"]))
		if not hit.is_empty():
			var position: Vector3 = hit["position"]
			_expect(absf(position.y - PROVISIONAL_SURFACE_HEIGHT_M) < TOLERANCE_M, "Top datum")
			_expect(hit["collider"] == instance.get_node("Collision/Body"), "Owned slab collider")

		observations.append({ "case": test["name"], "solid": not hit.is_empty() })

	_result["physics_ray_queries"] = observations
	_check_headroom(space)


## Measure underside height and absence of accidental pillars using independent ray expectations.
func _check_headroom(space: PhysicsDirectSpaceState3D) -> void:
	var underside: Dictionary = space.intersect_ray(PhysicsRayQueryParameters3D.create(
		Vector3.ZERO, Vector3(0, 6, 0), WORLD_LAYER
	))
	_expect(not underside.is_empty(), "Upward ray must find slab underside")
	if not underside.is_empty():
		var position: Vector3 = underside["position"]
		_expect(absf(position.y - 5.15) < TOLERANCE_M, "Underside must be at 5.15 m")
		_result["slab_only_underside_height_m"] = position.y

	var below: Dictionary = space.intersect_ray(PhysicsRayQueryParameters3D.create(
		Vector3(-4, 5, 0), Vector3(4, 5, 0), WORLD_LAYER
	))
	_expect(below.is_empty(), "No slab collision below provisional underside")
	_result["horizontal_ray_at_5m_clear"] = below.is_empty()


## Save when requested, then check the isolated asset without launching gameplay or live editors.
func _run() -> void:
	if Engine.is_editor_hint():
		await create_timer(EDITOR_STARTUP_SECONDS).timeout
		# No-change scans need not emit filesystem_changed. The CLI timeout bounds this wait.
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame  # gdstyle:ignore=quality/await-in-loop

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
		# Test-only translation; the saved component keeps its deck-surface-centre pivot.
		instance.position.y = PROVISIONAL_SURFACE_HEIGHT_M
		await physics_frame
		await physics_frame
		_physics_checks(instance)
		instance.queue_free()
		await process_frame

	_result["engine"] = Engine.get_version_info()["string"]
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var output: String = OUTPUT
	var output_index: int = arguments.find("--output")
	if output_index >= 0 and output_index + 1 < arguments.size():
		output = arguments[output_index + 1]

	var file: FileAccess = FileAccess.open(output, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print(JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
