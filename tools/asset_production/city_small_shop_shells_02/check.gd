extends SceneTree
## Headless saved-prefab, resource, mount and bounded static-envelope checks.

const ASSET := "city_small_shop_shells_02"
const EDITOR_STARTUP_FRAMES := 10
const PREFIX := "res://scenes/prefabs/environment/"
const EVIDENCE := "res://docs/assets/production/city_small_shop_shells_02-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-6.48, 0, -4.62), Vector3(12.96, 5.05, 9.2))
const FITTINGS := {
	"Entrance": "entrance_single",
	"Door": "door_single",
	"Window": "display_window",
	"Canopy": "canopy",
	"Fascia": "fascia",
}

var _report: Dictionary = {}
var _failed := false


## Defer until the headless scene tree is ready for resource and physics checks.
func _initialize() -> void:
	_run.call_deferred()


## Normalize only requested owned scenes, then verify loaded production resources.
func _run() -> void:
	if Engine.is_editor_hint():
		# Yield to editor startup/UID discovery; the CLI timeout bounds this tool-only wait.
		for frame: int in EDITOR_STARTUP_FRAMES:
			await process_frame  # gdstyle:ignore=quality/await-in-loop
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame  # gdstyle:ignore=quality/await-in-loop

	_require(Engine.get_version_info()["major"] == 4)
	_require(Engine.get_version_info()["minor"] == 8)
	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"))
	var paths: Array[String] = [PREFIX + ASSET + ".tscn", PREFIX + ASSET + "_fitted.tscn"]
	if "--normalize" in OS.get_cmdline_user_args():
		for path: String in paths:
			_save_scene(path)
			var first_hash: String = FileAccess.get_sha256(path)
			_save_scene(path)
			_require(first_hash == FileAccess.get_sha256(path), "Scene roundtrip drift: " + path)
		_report["save_reload_byte_stable"] = true

	for path: String in paths:
		_check_dependencies(path)
		_check_prefab(path)

	await _check_physics(paths[1])
	if _failed:
		quit(1)
		return

	_report["engine"] = Engine.get_version_info()["string"]
	_report["status"] = "PASS: linked resources, bounds, mounts, single solid exterior envelope"
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(EVIDENCE))
	if not _report.has("save_reload_byte_stable") and data.has("godot"):
		_report["save_reload_byte_stable"] = data["godot"].get("save_reload_byte_stable", false)
	data["godot"] = _report
	var file: FileAccess = FileAccess.open(EVIDENCE, FileAccess.WRITE)
	file.store_string(JSON.stringify(data, "\t") + "\n")
	file.close()
	print("CITY_SMALL_SHOP_SHELLS_02_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Retain failures across helper calls; Godot assertions alone only abort the current function.
func _require(condition: bool, message: String = "Asset contract check failed") -> void:
	if not condition:
		_failed = true
		push_error(message)


## Preserve linked imported and inherited scene states while normalizing saved identities.
func _save_scene(path: String) -> void:
	var source: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	)
	var instance: Node = source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_require(packed.pack(instance) == OK)
	_require(ResourceSaver.save(packed, path) == OK)
	var uid: int = ResourceLoader.get_resource_uid(path)
	_require(uid != ResourceUID.INVALID_ID)
	if ResourceUID.has_id(uid):
		ResourceUID.set_id(uid, path)
	else:
		ResourceUID.add_id(uid, path)

	instance.free()


## Recursively load actual dependencies and reject unresolved UID/path fallback.
func _check_dependencies(path: String) -> void:
	_require(ResourceLoader.exists(path), path)
	_require(ResourceLoader.load(path) != null, path)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		var child_path: String = parts[-1]
		if parts[0].begins_with("uid://"):
			var uid: int = ResourceUID.text_to_id(parts[0])
			_require(ResourceUID.has_id(uid), dependency)
			_require(ResourceUID.get_id_path(uid) == child_path, dependency)
		_check_dependencies(child_path)


## Check shell ancestry and measured mesh bounds without authoring replacement geometry.
func _check_prefab(path: String) -> void:
	var packed: PackedScene = load(path)
	var instance: Node3D = packed.instantiate()
	root.add_child(instance)
	var model: Node3D = instance.get_node("Visuals/Model")
	_require(model.transform == Transform3D.IDENTITY)
	_require(model.scene_file_path == "res://art/models/environment/%s/%s.glb" % [ASSET, ASSET])
	var bounds: AABB = _mesh_bounds(model)
	_require(bounds.position.distance_to(EXPECTED_BOUNDS.position) < .001)
	_require(bounds.size.distance_to(EXPECTED_BOUNDS.size) < .001)
	var shape: CollisionShape3D = instance.get_node("Collision/Body/Footprint")
	_require(shape.shape is BoxShape3D)
	_require(shape.shape.size.is_equal_approx(Vector3(12.8, 4.3, 9)))
	_require(shape.position.is_equal_approx(Vector3(0, 2.15, 0)))
	_require(not shape.disabled)
	var body: StaticBody3D = instance.get_node("Collision/Body")
	_require(body.collision_layer == 1 and body.collision_mask == 0)
	if path.ends_with("_fitted.tscn"):
		_check_mounts(instance, model)

	_report["shell_bounds_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["shell_bounds_size"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	instance.free()


## Aggregate actual imported mesh AABBs in the shell's identity local space.
func _mesh_bounds(model: Node3D) -> AABB:
	var bounds := AABB()
	var first := true
	var count := 0
	for node: Node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh_node := node as MeshInstance3D
		_require(mesh_node.mesh != null)
		var local_bounds: AABB = mesh_node.transform * mesh_node.mesh.get_aabb()
		bounds = local_bounds if first else bounds.merge(local_bounds)
		first = false
		count += 1
		for surface: int in mesh_node.mesh.get_surface_count():
			var material: BaseMaterial3D = mesh_node.mesh.surface_get_material(surface)
			_require(material != null)
			_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
			_require(material.cull_mode == BaseMaterial3D.CULL_BACK)

	_require(count == 25, "Unexpected shell mesh count: " + str(count))
	_report["shell_mesh_count"] = count
	return bounds


## Verify all ten fitting placements against actual imported mount markers.
func _check_mounts(instance: Node3D, model: Node3D) -> void:
	var checked := 0
	for side: String in ["Left", "Right"]:
		for fitting: String in FITTINGS:
			var node: Node3D = instance.get_node("Fittings/" + side + fitting)
			var marker_name: String = "mount_" + side.to_lower() + "_" + FITTINGS[fitting]
			var marker: Node3D = model.find_child(marker_name, true, false)
			_require(marker != null)
			_require(node.global_transform.is_equal_approx(marker.global_transform))
			_require(node.scene_file_path.begins_with(PREFIX + "city_shop_fittings_"))
			_require(node.get_node("Visuals/Model").transform == Transform3D.IDENTITY)
			checked += 1
			for shape: Node in node.find_children("*", "CollisionShape3D", true, false):
				_require(shape.disabled, "Fitting must not duplicate the solid shell collision")

	_report["linked_fittings"] = checked
	_report["fitting_mount_error_m"] = 0
	_report["fitting_colliders_disabled"] = true


## Exercise native physics queries on the fitted saved exterior-only prefab.
func _check_physics(path: String) -> void:
	var packed: PackedScene = load(path)
	var instance: Node3D = packed.instantiate()
	root.add_child(instance)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = instance.get_world_3d().direct_space_state
	var samples: Array[Vector3] = [Vector3(0, 1, -10), Vector3(10, 1, 0), Vector3(0, 1, 10)]
	for start: Vector3 in samples:
		var query := PhysicsRayQueryParameters3D.create(start, Vector3(0, 1, 0), 1)
		var hit: Dictionary = space.intersect_ray(query)
		_require(not hit.is_empty())
		_require(hit["collider"] == instance.get_node("Collision/Body"))

	var clear := PhysicsRayQueryParameters3D.create(Vector3(7, 1, -10), Vector3(7, 1, 10), 1)
	_require(space.intersect_ray(clear).is_empty())
	var capsule := CapsuleShape3D.new()
	capsule.radius = .38
	capsule.height = 1.8
	var overlap := PhysicsShapeQueryParameters3D.new()
	overlap.shape = capsule
	overlap.collision_mask = 1
	overlap.transform.origin = Vector3(0, .9, 0)
	_require(space.intersect_shape(overlap).size() == 1)
	overlap.transform.origin = Vector3(0, .9, -5.5)
	_require(space.intersect_shape(overlap).is_empty())
	_report["physics"] = { "solid_rays": 3, "clear_bypass_ray": 1, "capsule_cases": 2 }
	instance.free()
