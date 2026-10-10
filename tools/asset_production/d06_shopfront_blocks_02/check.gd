extends SceneTree
## Validate the saved U-shell, shared fittings, court collision and stable scene identities.

const PREFIX := "res://scenes/prefabs/environment/"
const ASSET := "d06_shopfront_blocks_02"
const EVIDENCE := "res://docs/assets/production/d06_shopfront_blocks_02-evidence/validation.json"
const STARTUP_FRAMES := 10
const CAPSULE_RADIUS := .35
const CAPSULE_HEIGHT := 1.8
const EXPECTED_BOUNDS := AABB(Vector3(-9.68, 0, -10.1), Vector3(19.36, 5.05, 19.18))
const BOXES := {
	"FrontBar": [Vector3(0, 2.15, -5.8), Vector3(19.2, 4.3, 6.4)],
	"WestWing": [Vector3(-6.4, 2.15, 3.2), Vector3(6.4, 4.3, 11.6)],
	"EastWing": [Vector3(6.4, 1.925, 1.6), Vector3(6.4, 3.85, 8.4)],
}

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
	print("REAR_COURT_CHECK ", _report["engine_status"])
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


## Assert the independently specified box union, fitting mounts and root datum.
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
		_require(shape.name in BOXES and shape.shape is BoxShape3D, "Only three shell boxes")
		if shape.name not in BOXES:
			continue
		_require(shape.position.is_equal_approx(BOXES[shape.name][0]), "Collider position")
		_require((shape.shape as BoxShape3D).size.is_equal_approx(BOXES[shape.name][1]),
			"Collider size")
		var body := shape.get_parent() as StaticBody3D
		_require(body == instance.get_node("Collision/Body"), "Single collision owner")
		_require(body.collision_layer == 1 and body.collision_mask == 0, "Static world layers")
	_require(enabled == 3, "Exactly three enabled shapes")
	_report["enabled_static_boxes"] = enabled
	_check_fittings(instance, model)
	_require((instance.get_node("Interfaces/CourtRear") as Node3D).position == Vector3(0, 0, 10),
		"Rear interface")
	var east_interface := instance.get_node("Interfaces/CourtEast") as Node3D
	_require(east_interface.position == Vector3(10.6, 0, 7.4), "East interface")
	_measure_visuals(instance)


## Each fitting is the unchanged existing carrier at its Blender-authored mount.
func _check_fittings(instance: Node3D, model: Node3D) -> void:
	var labels: Array[String] = ["West", "Centre", "East"]
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


## Record exact saved model positions for evidence rendering rather than a second layout writer.
func _measure_visuals(instance: Node3D) -> void:
	var models: Array[Dictionary] = []
	for node: Node in instance.find_children("Model", "Node3D", true, false):
		var model := node as Node3D
		_require(model.transform == Transform3D.IDENTITY, "Unmodified imported transform")
		_require(model.global_basis == Basis.IDENTITY, "Translation-only assembly")
		models.append({"path": model.scene_file_path, "position": [model.global_position.x,
			model.global_position.y, model.global_position.z]})
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


## Sweep the production-sized capsule through the court and offset east exit; probe solid seams.
func _check_physics(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var capsule := CapsuleShape3D.new()
	capsule.radius = CAPSULE_RADIUS
	capsule.height = CAPSULE_HEIGHT
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = 1
	var sweeps := 0
	for x: float in [-2.65, 0, 2.65]:
		for direction: float in [-1.0, 1.0]:
			query.transform.origin = Vector3(x, .9, -2.05 if direction > 0 else 10.5)
			query.motion = Vector3(0, 0, 12.55 * direction)
			_require(space.intersect_shape(query).is_empty(), "Court start clear")
			_require(space.cast_motion(query)[0] == 1.0, "Court sweep blocked")
			sweeps += 1
	for z: float in [6.35, 7.4, 8.45]:
		for direction: float in [-1.0, 1.0]:
			query.transform.origin = Vector3(0 if direction > 0 else 11, .9, z)
			query.motion = Vector3(11 * direction, 0, 0)
			_require(space.intersect_shape(query).is_empty(), "East exit start clear")
			_require(space.cast_motion(query)[0] == 1.0, "East exit sweep blocked")
			sweeps += 1
	query.motion = Vector3.ZERO
	for point: Vector3 in [Vector3(0, .9, -5.8), Vector3(-6.4, .9, 3.2),
		Vector3(6.4, .9, 1.6), Vector3(-6.4, .9, -2.6), Vector3(6.4, .9, -2.6)]:
		query.transform.origin = point
		var hits: Array[Dictionary] = space.intersect_shape(query)
		_require(not hits.is_empty(), "Solid mass or wing seam is missing")
		for hit: Dictionary in hits:
			_require(hit["collider"] == instance.get_node("Collision/Body"), "Sole collision owner")
	for motion: Vector3 in [Vector3(-5, 0, 0), Vector3(5, 0, 0), Vector3(0, 0, -5)]:
		query.transform.origin = Vector3(0, .9, 0)
		query.motion = motion
		_require(space.cast_motion(query)[0] < 1.0, "Court wall fails to block")
	_report["physics"] = {"capsule_radius_m": CAPSULE_RADIUS, "capsule_height_m": CAPSULE_HEIGHT,
		"clear_bidirectional_sweeps": sweeps, "solid_and_seam_overlap_cases": 5,
		"blocking_sweeps": 3, "court_structural_width_m": 6.4,
		"scope": "bounded native shape queries; not actor, floor, car, or network acceptance"}
