extends SceneTree
## Check the saved short row, unchanged prefab links, passage envelopes and scene roundtrips.

const SCENE := "res://scenes/prefabs/environment/d06_shopfront_blocks_01.tscn"
const EVIDENCE := "res://docs/assets/production/d06_shopfront_blocks_01-evidence/validation.json"
const PREFIX := "res://scenes/prefabs/environment/"
const STARTUP_FRAMES := 10
const SHOPS := {
	"WestWide": ["city_small_shop_shells_02", Vector3(-13.7, 0, -1.25)],
	"RecessedCompact": ["city_small_shop_shells_04", Vector3(-.5, 0, 2.55)],
	"EastWide": ["city_small_shop_shells_02", Vector3(13.7, 0, .75)],
}
const EXPECTED_BOUNDS := AABB(Vector3(-20.18, 0, -6.85), Vector3(40.36, 5.05, 12.68))
const CAPSULE_RADIUS := .35
const CAPSULE_HEIGHT := 1.8

var _failed := false
var _report: Dictionary = {}
var _dependencies: Array[String] = []


## Defer resource loading until the tree exists.
func _initialize() -> void:
	_run.call_deferred()


## Preserve authored scene composition, then exercise the actual saved collision in runtime mode.
func _run() -> void:
	if Engine.is_editor_hint():
		for frame: int in STARTUP_FRAMES:
			await process_frame  # gdstyle:ignore=quality/await-in-loop
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame  # gdstyle:ignore=quality/await-in-loop

	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if FileAccess.file_exists(EVIDENCE):
		_report = JSON.parse_string(FileAccess.get_file_as_string(EVIDENCE))
	if "--normalize" in OS.get_cmdline_user_args():
		_require(Engine.is_editor_hint(), "Normalize in headless editor mode only")
		_save_scene()
		var stable: String = FileAccess.get_sha256(SCENE)
		for cycle: int in 2:
			_save_scene()
			_require(FileAccess.get_sha256(SCENE) == stable, "Scene roundtrip drift")
		_report["two_roundtrips_byte_stable"] = not _failed

	_check_dependencies(SCENE)
	var instance: Node3D = (load(SCENE) as PackedScene).instantiate()
	root.add_child(instance)
	_check_assembly(instance)
	if not Engine.is_editor_hint():
		await physics_frame
		await physics_frame
		_check_physics(instance)
	instance.free()
	_report["engine"] = Engine.get_version_info()
	_report["dependencies"] = _dependencies
	_report["status"] = "failed" if _failed else "passed"
	_report["scene_sha256"] = FileAccess.get_sha256(SCENE)
	_report["scene_bytes"] = FileAccess.get_file_as_bytes(SCENE).size()
	var file: FileAccess = FileAccess.open(EVIDENCE, FileAccess.WRITE)
	file.store_string(JSON.stringify(_report, "\t") + "\n")
	file.close()
	print("SHORT_ROW_CHECK ", JSON.stringify(_report))
	quit(1 if _failed else 0)


## Keep helper failures observable through the final process exit.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Pack without flattening child scene instances, registering a newly assigned UID.
func _save_scene() -> void:
	var packed: PackedScene = ResourceLoader.load(
		SCENE,
		"PackedScene",
		ResourceLoader.CACHE_MODE_IGNORE,
	)
	var instance: Node = packed.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	_require(saved.pack(instance) == OK, "Pack scene")
	_require(ResourceSaver.save(saved, SCENE) == OK, "Save scene")
	var uid: int = ResourceLoader.get_resource_uid(SCENE)
	_require(uid != ResourceUID.INVALID_ID, "Scene UID")
	if ResourceUID.has_id(uid):
		ResourceUID.set_id(uid, SCENE)
	else:
		ResourceUID.add_id(uid, SCENE)
	instance.free()


## Traverse all external references and reject missing resources or stale UID/path mappings.
func _check_dependencies(path: String) -> void:
	if path in _dependencies:
		return

	_dependencies.append(path)
	_require(ResourceLoader.load(path) != null, "Missing resource: " + path)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		var child: String = parts[-1]
		_require(parts[0].begins_with("uid://"), "Dependency missing UID: " + dependency)
		if parts[0].begins_with("uid://"):
			var uid: int = ResourceUID.text_to_id(parts[0])
			_require(ResourceUID.has_id(uid), "Unregistered UID: " + dependency)
			_require(ResourceUID.get_id_path(uid) == child, "UID mismatch: " + dependency)
		_check_dependencies(child)


## Check literal design expectations independently of saved placement and preserve nested links.
func _check_assembly(instance: Node3D) -> void:
	_require(instance.transform == Transform3D.IDENTITY, "Ground datum/root transform")
	_require(instance.get_node("Shops").get_child_count() == 3, "Three shops only")
	for shop_name: String in SHOPS:
		var shop: Node3D = instance.get_node("Shops/" + shop_name)
		var asset: String = SHOPS[shop_name][0]
		_require(shop.position.is_equal_approx(SHOPS[shop_name][1]), "Placement drift")
		_require(shop.basis == Basis.IDENTITY, "Unscaled, north-facing shops")
		_require(shop.scene_file_path == PREFIX + asset + "_fitted.tscn", "Fitted prefab link")
		var model: Node3D = shop.get_node("Visuals/Model")
		_require(model.transform == Transform3D.IDENTITY, "Imported model identity")
		_require(model.scene_file_path.ends_with(asset + ".glb"), "Shell GLB link")

	_check_collision_owners(instance)
	_measure_visuals(instance)
	for side: String in ["West", "East"]:
		var x: float = -5.5 if side == "West" else 5.0
		for end: String in ["Front", "Rear"]:
			var marker: Node3D = instance.get_node("Interfaces/" + side + "Passage" + end)
			var z: float = -8.0 if end == "Front" else 8.0
			_require(marker.position.is_equal_approx(Vector3(x, 0, z)), "Passage interface drift")


## Inherited solid footprint boxes remain the only enabled blocking volumes.
func _check_collision_owners(instance: Node3D) -> void:
	var enabled := 0
	for node: Node in instance.find_children("*", "CollisionShape3D", true, false):
		var shape := node as CollisionShape3D
		if shape.disabled:
			continue

		enabled += 1
		_require(shape.name == "Footprint" and shape.shape is BoxShape3D, "Footprint only")
		_require(shape.position.is_equal_approx(Vector3(0, 2.15, 0)), "Collision datum")
		var body := shape.get_parent() as StaticBody3D
		_require(body.collision_layer == 1 and body.collision_mask == 0, "Static world layers")
		var box := shape.shape as BoxShape3D
		var compact: bool = str(instance.get_path_to(shape)).contains("RecessedCompact")
		var expected := Vector3(6.4, 4.3, 6.4) if compact else Vector3(12.8, 4.3, 9)
		_require(box.size.is_equal_approx(expected), "Inherited collider size")
	_require(enabled == 3, "Exactly one collider per shop; no passage blocker")
	_report["enabled_static_boxes"] = enabled


## Record actual visual instances for Blender evidence so the saved scene is the placement owner.
func _measure_visuals(instance: Node3D) -> void:
	var models: Array[Dictionary] = []
	for node: Node in instance.find_children("Model", "Node3D", true, false):
		var model := node as Node3D
		_require(model.transform == Transform3D.IDENTITY, "No corrective model transforms")
		_require(model.global_basis == Basis.IDENTITY, "Translation-only assembly")
		models.append({"path": model.scene_file_path,
			"position": [
				model.global_position.x,
				model.global_position.y,
				model.global_position.z,
			]})
	_require(models.size() == 28, "Three shells and 25 fittings")
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
	_report["godot_aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["godot_aabb_max"] = [bounds.end.x, bounds.end.y, bounds.end.z]


## Sweep an actual production-sized capsule through both passage widths and around the rear.
func _check_physics(instance: Node3D) -> void:
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var capsule := CapsuleShape3D.new()
	capsule.radius = CAPSULE_RADIUS
	capsule.height = CAPSULE_HEIGHT
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = 1
	var sweeps := 0
	# Edge paths reserve 0.45 m from solids: capsule radius plus 0.10 m margin.
	for x: float in [-6.85, -5.5, -4.15, 3.15, 5.0, 6.85]:
		for direction: float in [-1.0, 1.0]:
			query.transform.origin = Vector3(x, .9, -8 * direction)
			query.motion = Vector3(0, 0, 16 * direction)
			_require(space.intersect_shape(query).is_empty(), "Passage start clear")
			var result: PackedFloat32Array = space.cast_motion(query)
			_require(result[0] == 1.0 and result[1] == 1.0, "Passage sweep blocked")
			sweeps += 1
	for direction: float in [-1.0, 1.0]:
		query.transform.origin = Vector3(-21 * direction, .9, 6.3)
		query.motion = Vector3(42 * direction, 0, 0)
		_require(space.cast_motion(query)[0] == 1.0, "Rear connection blocked")
		sweeps += 1
	query.motion = Vector3.ZERO
	for shop_name: String in SHOPS:
		query.transform.origin = SHOPS[shop_name][1] + Vector3(0, .9, 0)
		var hits: Array[Dictionary] = space.intersect_shape(query)
		_require(hits.size() == 1, "Each closed shop blocks exactly once")
		if hits.size() == 1:
			var expected: Node = instance.get_node("Shops/" + shop_name + "/Collision/Body")
			_require(hits[0]["collider"] == expected, "Correct solid owner")
	_report["physics"] = {"capsule_radius_m": CAPSULE_RADIUS, "capsule_height_m": CAPSULE_HEIGHT,
		"clear_bidirectional_sweeps": sweeps, "solid_overlap_cases": 3,
		"passage_structural_widths_m": [3.6, 4.6], "passage_visual_widths_m": [3.44, 4.44],
		"scope": "native shape queries only; no floor, actor simulation, traffic or network test"}
