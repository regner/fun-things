extends SceneTree
## Check the source-linked head, unchanged pole mounting fit and visual-only head contract.

const ASSET := "city_traffic_fixtures_02"
const PREFAB := "res://scenes/prefabs/environment/city_traffic_fixtures_02.tscn"
const MOUNTED := "res://scenes/prefabs/environment/city_traffic_fixtures_02_mounted.tscn"
const EVIDENCE := "res://docs/assets/production/city_traffic_fixtures_02-evidence/validation.json"
const EXPECTED_BOUNDS := AABB(Vector3(-.25, -1.32, -.38), Vector3(.50, 1.32, .54))

var _failed := false
var _report: Dictionary = { "resource_uids": {} }


## Wait for the scene tree before loading linked resources.
func _initialize() -> void:
	_run.call_deferred()


## Check saved identities, source geometry and the mounted assembly without altering siblings.
func _run() -> void:
	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if "--normalize" in OS.get_cmdline_user_args():
		for path: String in [PREFAB, MOUNTED]:
			_save_scene(path)
			var first_hash: String = FileAccess.get_sha256(path)
			_save_scene(path)
			_require(first_hash == FileAccess.get_sha256(path), "Save/reload drift")
		_report["save_reload_byte_stable"] = true

	_check_dependencies(MOUNTED)
	_check_model()
	_require(_report.has("linked_model_identity"), "Model check incomplete")
	await _check_mount()
	_require(_report.has("mounted_clearance_m"), "Mount check incomplete")
	if _failed:
		quit(1)
		return

	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(EVIDENCE))
	if data.has("godot") and not _report.has("save_reload_byte_stable"):
		_report["save_reload_byte_stable"] = data["godot"].get("save_reload_byte_stable", false)
	_report["engine"] = Engine.get_version_info()["string"]
	data["godot"] = _report
	var file: FileAccess = FileAccess.open(EVIDENCE, FileAccess.WRITE)
	file.store_line(JSON.stringify(data, "  "))
	file.close()
	print("CITY_TRAFFIC_FIXTURES_02_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Keep failed assertions visible in logs and in the process exit status.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Preserve imported ancestry while packing and resaving authored wrappers.
func _save_scene(path: String) -> void:
	# A newly saved scene can precede the importer cache; its saved identity wins.
	var header: String = FileAccess.get_file_as_string(path).get_slice(String.chr(10), 0)
	var uid_match: RegExMatch = RegEx.create_from_string('uid="(uid://[^"]+)"').search(header)
	var uid: int = ResourceUID.INVALID_ID
	if uid_match != null:
		uid = ResourceUID.text_to_id(uid_match.get_string(1))
	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()
	if not ResourceUID.has_id(uid):
		ResourceUID.add_id(uid, path)

	var source: PackedScene = ResourceLoader.load(
		path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE,
	)
	var instance: Node = source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_require(packed.pack(instance) == OK, "Pack failed")
	_require(ResourceSaver.save(packed, path) == OK, "Save failed")
	_require(ResourceSaver.set_uid(path, uid) == OK, "Scene UID save failed")
	instance.free()


## Recursively prove each saved resource and dependency UID resolves.
func _check_dependencies(path: String) -> void:
	_require(ResourceLoader.load(path) != null, "Missing resource: " + path)
	var resource_uid: int = ResourceLoader.get_resource_uid(path)
	_require(resource_uid != ResourceUID.INVALID_ID, "Resource has no UID: " + path)
	_require(ResourceUID.has_id(resource_uid), "Unregistered resource UID: " + path)
	_require(ResourceUID.get_id_path(resource_uid) == path, "Resource UID path mismatch: " + path)
	_report["resource_uids"][path] = ResourceUID.id_to_text(resource_uid)
	for dependency: String in ResourceLoader.get_dependencies(path):
		var parts: PackedStringArray = dependency.split("::")
		var child: String = parts[-1]
		if parts[0].begins_with("uid://"):
			var uid: int = ResourceUID.text_to_id(parts[0])
			_require(ResourceUID.has_id(uid), "Missing UID: " + dependency)
			_require(ResourceUID.get_id_path(uid) == child, "UID mismatch: " + dependency)
		_check_dependencies(child)


## Verify actual imported surfaces, pivot and bounds; do not add a competing gameplay state.
func _check_model() -> void:
	var packed: PackedScene = load(PREFAB)
	var instance: Node3D = packed.instantiate()
	var model: Node3D = instance.get_node("Visuals/Model")
	_require(model.transform == Transform3D.IDENTITY, "Corrective model transform")
	_require(model.scene_file_path == "res://art/models/environment/%s/%s.glb" % [ASSET, ASSET],
		"Unlinked model")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_require(meshes.size() == 1, "Mesh count")
	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	_require(mesh.transform == Transform3D.IDENTITY, "Mesh pivot")
	_require(model.get_node("CityTrafficFixtures02").transform == Transform3D.IDENTITY,
		"Imported root transform")
	var bounds: AABB = mesh.mesh.get_aabb()
	_require(bounds.position.distance_to(EXPECTED_BOUNDS.position) < .001, "Bounds minimum")
	_require(bounds.size.distance_to(EXPECTED_BOUNDS.size) < .001, "Bounds size")
	_require(mesh.mesh.get_surface_count() == 6, "Surface count")
	var expected_materials: Array[String] = [
		"traffic_dark_metal", "traffic_fixture_rim", "traffic_service_recess",
		"signal_red_unlit", "signal_amber_unlit", "signal_green_unlit",
	]
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(material.resource_name == expected_materials[surface], "Material order")
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparency")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")
		_require(not material.emission_enabled, "Unexpected active signal appearance")

	_require(instance.find_children("*", "CollisionObject3D", true, false).is_empty(),
		"Overhead head must be visual-only")
	_require(instance.find_children("*", "Light3D", true, false).is_empty(), "Unexpected light")
	_report["bounds_min_m"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_report["bounds_size_m"] = [bounds.size.x, bounds.size.y, bounds.size.z]
	_report["linked_model_identity"] = true
	_report["static_unlit_materials"] = true
	instance.free()


## Prove the saved head uses the actual carrier socket and stays strictly above 2.5 metres.
func _check_mount() -> void:
	var packed: PackedScene = load(MOUNTED)
	var assembly: Node3D = packed.instantiate()
	root.add_child(assembly)
	var head: Node3D = assembly.get_node("Head")
	var socket: Marker3D = assembly.get_node("Pole/Sockets/SignalHead")
	var source_socket: Node3D = assembly.get_node(
		"Pole/Visuals/Model/CityTrafficFixtures01/socket_signal_head",
	)
	_require(head.global_transform.is_equal_approx(socket.global_transform), "Mount adapter drift")
	_require(head.global_transform.is_equal_approx(source_socket.global_transform),
		"Source mount drift")
	_require(head.basis.is_equal_approx(Basis.IDENTITY), "Mount orientation")
	var mesh: MeshInstance3D = head.find_children("*", "MeshInstance3D", true, false)[0]
	var bounds: AABB = mesh.global_transform * mesh.mesh.get_aabb()
	_require(absf(bounds.position.y - 2.88) < .001, "Ground clearance")
	_require(bounds.position.y > 2.5, "Head is below overhead-only threshold")
	_require(absf(bounds.end.y - 4.2) < .001, "Head/collar contact plane")
	var bodies: Array[Node] = assembly.find_children("*", "CollisionObject3D", true, false)
	_require(bodies.size() == 1, "Assembly must retain only the carrier collider")
	_require(bodies[0] == assembly.get_node("Pole/Collision/PoleBody"), "Wrong collision owner")
	await _check_queries(assembly)
	_report["mounted_clearance_m"] = bounds.position.y
	_report["mount_matches_source_and_adapter"] = true
	_report["head_collision_free_carrier_collision_retained"] = true
	assembly.free()


## Preserve the pole's existing blocking while keeping all head decoration collision-free.
func _check_queries(assembly: Node3D) -> void:
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = assembly.get_world_3d().direct_space_state
	var low_ray := PhysicsRayQueryParameters3D.create(Vector3(0, .5, -2), Vector3(0, .5, 2), 1)
	var low_hit: Dictionary = space.intersect_ray(low_ray)
	_require(not low_hit.is_empty(), "Carrier no longer blocks")
	var head_ray := PhysicsRayQueryParameters3D.create(
		Vector3(-1, 3.5, -1.4), Vector3(1, 3.5, -1.4), 1,
	)
	_require(space.intersect_ray(head_ray).is_empty(), "Head unexpectedly blocks")
