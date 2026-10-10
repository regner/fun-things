extends SceneTree
## Validate the saved chamfer, shared fittings, footprint collision and stable scene identities.

const PREFIX := "res://scenes/prefabs/environment/"
const ASSET := "d06_shopfront_blocks_03"
const EVIDENCE := "res://docs/assets/production/d06_shopfront_blocks_03-evidence/validation.json"
const STARTUP_FRAMES := 10
const CAPSULE_RADIUS := .35
const CAPSULE_HEIGHT := 1.8
const EXPECTED_BOUNDS := AABB(Vector3(-8.08, 0, -7.5), Vector3(17.18, 5.05, 13.98))
const FOOTPRINT: Array[Vector3] = [
	Vector3(-8, 0, -6.4), Vector3(3.2, 0, -6.4), Vector3(8, 0, -1.6),
	Vector3(8, 0, 6.4), Vector3(-8, 0, 6.4),
	Vector3(-8, 4.3, -6.4), Vector3(3.2, 4.3, -6.4), Vector3(8, 4.3, -1.6),
	Vector3(8, 4.3, 6.4), Vector3(-8, 4.3, 6.4),
]

var _failed := false
var _report: Dictionary = {}
var _dependencies: Array[String] = []


## Defer resource loading until the tree exists.
func _initialize() -> void:
	_run.call_deferred()


## Normalize both owned wrappers before validating the inherited fitted asset.
func _run() -> void:
	if Engine.is_editor_hint():
		for frame: int in STARTUP_FRAMES:
			await process_frame  # gdstyle:ignore=quality/await-in-loop
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame  # gdstyle:ignore=quality/await-in-loop

	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	_report = JSON.parse_string(FileAccess.get_file_as_string(EVIDENCE))
	var scenes: Dictionary = {}
	for suffix: String in ["", "_fitted"]:
		var path: String = PREFIX + ASSET + suffix + ".tscn"
		if "--normalize" in OS.get_cmdline_user_args():
			_require(Engine.is_editor_hint(), "Normalize only in headless editor")
			_save_scene(path)
			var stable: String = FileAccess.get_sha256(path)
			for cycle: int in 2:
				_save_scene(path)
				_require(FileAccess.get_sha256(path) == stable, "Roundtrip drift: " + path)
			_report["two_roundtrips_byte_stable"] = not _failed
		scenes[path] = {"sha256": FileAccess.get_sha256(path),
			"bytes": FileAccess.get_file_as_bytes(path).size()}

	var fitted_path: String = PREFIX + ASSET + "_fitted.tscn"
	_check_dependencies(fitted_path)
	var instance: Node3D = (load(fitted_path) as PackedScene).instantiate()
	root.add_child(instance)
	_check_assembly(instance)
	if not Engine.is_editor_hint():
		await physics_frame
		await physics_frame
		_check_physics(instance)
	instance.free()
	_report["engine"] = Engine.get_version_info()
	_report["dependencies"] = _dependencies
	_report["engine_status"] = "failed" if _failed else "passed"
	_report["scenes"] = scenes
	var file: FileAccess = FileAccess.open(EVIDENCE, FileAccess.WRITE)
	file.store_string(JSON.stringify(_report, "\t") + "\n")
	file.close()
	print("CHAMFERED_CORNER_CHECK ", _report["engine_status"])
	quit(1 if _failed else 0)


## Retain failures in both logs and the process exit code.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Pack without flattening imported or inherited children and register newly assigned UIDs.
func _save_scene(path: String) -> void:
	var packed: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE,
	)
	var instance: Node = packed.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	_require(saved.pack(instance) == OK, "Pack scene")
	_require(ResourceSaver.save(saved, path) == OK, "Save scene")
	var uid: int = ResourceLoader.get_resource_uid(path)
	_require(uid != ResourceUID.INVALID_ID, "Scene UID")
	if ResourceUID.has_id(uid):
		ResourceUID.set_id(uid, path)
	else:
		ResourceUID.add_id(uid, path)
	instance.free()


## Resolve every external dependency and its UID mapping through the pinned resource loader.
func _check_dependencies(path: String) -> void:
	if path in _dependencies:
		return

	_dependencies.append(path)
	_require(ResourceLoader.load(path) != null, "Missing resource: " + path)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		var child: String = parts[-1]
		_require(parts[0].begins_with("uid://"), "Missing dependency UID: " + dependency)
		if parts[0].begins_with("uid://"):
			var uid: int = ResourceUID.text_to_id(parts[0])
			_require(ResourceUID.has_id(uid), "Unregistered UID")
			_require(ResourceUID.get_id_path(uid) == child, "Dependency UID mismatch")
		_check_dependencies(child)


## Assert the independently specified convex footprint, fitting mounts and root datum.
func _check_assembly(instance: Node3D) -> void:
	_require(instance.transform == Transform3D.IDENTITY, "Ground-centred root")
	var model: Node3D = instance.get_node("Visuals/Model")
	_require(model.transform == Transform3D.IDENTITY, "Linked model identity")
	_require(model.scene_file_path.ends_with(ASSET + ".glb"), "Own linked shell GLB")
	var enabled := 0
	for node: Node in instance.find_children("*", "CollisionShape3D", true, false):
		var shape := node as CollisionShape3D
		if shape.disabled:
			continue
		enabled += 1
		_require(shape.name == "Footprint" and shape.shape is ConvexPolygonShape3D,
			"Only the dimension-authored convex footprint")
		_require(shape.transform == Transform3D.IDENTITY, "Collider ground datum")
		var convex := shape.shape as ConvexPolygonShape3D
		_require(convex.points.size() == FOOTPRINT.size(), "Ten hull points, not render mesh")
		for point: Vector3 in FOOTPRINT:
			var found := false
			for actual: Vector3 in convex.points:
				found = found or actual.is_equal_approx(point)
			_require(found, "Convex footprint vertex")
		var body := shape.get_parent() as StaticBody3D
		_require(body == instance.get_node("Collision/Body"), "Single collision owner")
		_require(body.collision_layer == 1 and body.collision_mask == 0, "Static world layers")
	_require(enabled == 1, "Exactly one enabled shape")
	_report["enabled_convex_shapes"] = enabled
	_check_fittings(instance, model)
	var rear := instance.get_node("Interfaces/RearLink") as Node3D
	_require(rear.position == Vector3(0, 0, 7.5), "Rear interface")
	var corner := instance.get_node("Interfaces/CornerForecourt") as Node3D
	_require(corner.position == Vector3(7, 0, -5.4), "Corner interface")
	_measure_visuals(instance)


## Each fitting is the unchanged existing carrier at its Blender-authored mount.
func _check_fittings(instance: Node3D, model: Node3D) -> void:
	var labels: Array[String] = ["Front", "Corner", "East"]
	var kinds: Dictionary = {"Entrance": "entrance_single", "Door": "door_single",
		"Window": "display_window", "Canopy": "canopy", "Fascia": "fascia"}
	var assets: Dictionary = {"Entrance": "city_shop_fittings_03_single",
		"Door": "city_shop_fittings_06_single", "Window": "city_shop_fittings_05",
		"Canopy": "city_shop_fittings_01", "Fascia": "city_shop_fittings_02"}
	_require(instance.get_node("Fittings").get_child_count() == 15, "Fifteen reused fittings")
	for index: int in labels.size():
		for kind: String in kinds:
			var fitting: Node3D = instance.get_node("Fittings/" + labels[index] + kind)
			var marker: Node3D = model.find_child("mount_%d_%s" % [index, kinds[kind]], true, false)
			_require(marker != null, "Imported marker exists")
			_require(fitting.global_transform.is_equal_approx(marker.global_transform), "Mount fit")
			_require(fitting.scene_file_path == PREFIX + assets[kind] + ".tscn", "Shared prefab")


## Record saved model transforms for evidence rendering rather than a second layout writer.
func _measure_visuals(instance: Node3D) -> void:
	var models: Array[Dictionary] = []
	for node: Node in instance.find_children("Model", "Node3D", true, false):
		var model := node as Node3D
		_require(model.transform == Transform3D.IDENTITY, "Unmodified imported transform")
		models.append({"path": model.scene_file_path, "position": [model.global_position.x,
			model.global_position.y, model.global_position.z],
			"yaw_degrees": rad_to_deg(model.global_rotation.y)})
	_require(models.size() == 16, "One shell and fifteen fittings")
	var bounds := AABB()
	var first := true
	var surfaces := 0
	var meshes: Array[Node] = instance.find_children("*", "MeshInstance3D", true, false)
	for node: Node in meshes:
		var mesh := node as MeshInstance3D
		var measured: AABB = mesh.global_transform * mesh.get_aabb()
		bounds = measured if first else bounds.merge(measured)
		first = false
		surfaces += mesh.mesh.get_surface_count()
	_require(bounds.position.distance_to(EXPECTED_BOUNDS.position) < .002, "Visual bounds min")
	_require(bounds.size.distance_to(EXPECTED_BOUNDS.size) < .002, "Visual bounds size")
	_report["model_instances"] = models
	_report["mesh_instances"] = meshes.size()
	_report["material_surfaces"] = surfaces
	_report["fitted_godot_aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["fitted_godot_aabb_max"] = [bounds.end.x, bounds.end.y, bounds.end.z]


## Probe both sides of the chamfer, its joins and the clear rear/side reservations.
func _check_physics(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var capsule := CapsuleShape3D.new()
	capsule.radius = CAPSULE_RADIUS
	capsule.height = CAPSULE_HEIGHT
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = 1
	var sweeps := 0
	var diagonal_normal := Vector3(1, 0, -1).normalized()
	for offset: float in [.55, 1.0, 1.8]:
		var first := Vector3(2.6, .9, -7) + diagonal_normal * offset
		var last := Vector3(8.6, .9, -1) + diagonal_normal * offset
		for direction: int in 2:
			query.transform.origin = first if direction == 0 else last
			query.motion = last - first if direction == 0 else first - last
			_require(space.intersect_shape(query).is_empty(), "Chamfer route starts clear")
			_require(space.cast_motion(query)[0] == 1.0, "Clipped corner has invisible blocker")
			sweeps += 1
	for endpoints: Array in [
		[Vector3(-9, .9, 7.05), Vector3(9, .9, 7.05)],
		[Vector3(-8.65, .9, -7.5), Vector3(-8.65, .9, 7.5)],
		[Vector3(-9, .9, -7.05), Vector3(3.3, .9, -7.05)],
	]:
		for direction: int in 2:
			query.transform.origin = endpoints[direction]
			query.motion = endpoints[1 - direction] - endpoints[direction]
			_require(space.intersect_shape(query).is_empty(), "Outside route starts clear")
			_require(space.cast_motion(query)[0] == 1.0, "Outside route blocked")
			sweeps += 1
	_check_solid_contacts(instance, space, query, diagonal_normal)
	_report["physics"] = {"capsule_radius_m": CAPSULE_RADIUS, "capsule_height_m": CAPSULE_HEIGHT,
		"clear_bidirectional_sweeps": sweeps, "solid_and_join_overlap_cases": 4,
		"cutaway_empty_overlap_cases": 3, "measured_chamfer_contact_sweeps": 3,
		"scope": "bounded native shape queries; not actor, floor, car, or network acceptance"}


## Distinguish the solid chamfer and both end joins from its genuinely empty clipped corner.
func _check_solid_contacts(instance: Node3D, space: PhysicsDirectSpaceState3D,
	query: PhysicsShapeQueryParameters3D, diagonal_normal: Vector3) -> void:
	query.motion = Vector3.ZERO
	for point: Vector3 in [Vector3(0, .9, 0), Vector3(3.1, .9, -6.25),
		Vector3(7.85, .9, -1.5), Vector3(5.4, .9, -3.8)]:
		query.transform.origin = point
		var hits: Array[Dictionary] = space.intersect_shape(query)
		_require(hits.size() == 1, "Solid footprint or chamfer join missing")
		for hit: Dictionary in hits:
			_require(hit["collider"] == instance.get_node("Collision/Body"), "Sole collision owner")
	for point: Vector3 in [Vector3(6.5, .9, -5), Vector3(7.3, .9, -5.7),
		Vector3(7.5, .9, -4)]:
		query.transform.origin = point
		_require(space.intersect_shape(query).is_empty(), "Cut-away corner must stay empty")
	var fractions: Array[float] = []
	for offset: float in [-2.7, 0, 2.7]:
		var tangent := Vector3(1, 0, 1).normalized()
		query.transform.origin = Vector3(5.6, .9, -4) + tangent * offset + diagonal_normal
		query.motion = -diagonal_normal * 2
		var fraction: float = space.cast_motion(query)[0]
		fractions.append(fraction)
		_require(fraction > .29 and fraction < .35, "Chamfer wall contact must match visible plane")
	_report["chamfer_contact_fractions"] = fractions
