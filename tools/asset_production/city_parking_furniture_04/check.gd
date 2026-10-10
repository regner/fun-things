extends SceneTree
## Verify the saved bus-stop face override, shared carrier identity and inherited collision.

const PREFAB := "res://scenes/prefabs/environment/city_parking_furniture_04.tscn"
const SUPPORT := "res://scenes/prefabs/environment/city_traffic_fixtures_03.tscn"
const MODEL := "res://art/models/environment/city_traffic_fixtures_03/city_traffic_fixtures_03.glb"
const MATERIAL := "res://art/materials/environment/city_parking_furniture_04/bus_stop.tres"
const EVIDENCE := "res://docs/assets/production/city_parking_furniture_04-evidence/validation.json"
const MESH_PATH := "Visuals/Model/CityTrafficFixtures03/CityTrafficFixtures03_Mesh"

var _failed := false
var _report: Dictionary = {}


## Wait for startup before normalizing owned resources or accessing the physics world.
func _initialize() -> void:
	if Engine.is_editor_hint():
		await EditorInterface.get_resource_filesystem().filesystem_changed

	_run.call_deferred()


## Check saved dependencies and the sole material difference against an unmodified carrier.
func _run() -> void:
	_require(Engine.get_version_info().hash.begins_with("c971f93e7"), "Godot pin")
	if OS.get_cmdline_user_args().has("--normalize"):
		if not Engine.is_editor_hint():
			push_error("Normalization requires --editor to retain serialized dependency UIDs")
			quit(1)
			return

		_require(ResourceSaver.save(load(MATERIAL), MATERIAL) == OK, "Save material")
		_register_saved_uid(MATERIAL)
		_roundtrip()
		var first := FileAccess.get_file_as_bytes(PREFAB)
		_roundtrip()
		_require(first == FileAccess.get_file_as_bytes(PREFAB), "Saved identity drift")
		_report["save_reload_byte_stable"] = true

	_check_dependencies(PREFAB)
	var instance := (load(PREFAB) as PackedScene).instantiate() as Node3D
	var reference := (load(SUPPORT) as PackedScene).instantiate() as Node3D
	_check_model(instance, reference)
	_check_material()
	_check_collision(instance, reference)
	reference.free()
	root.add_child(instance)
	await physics_frame
	await physics_frame
	_check_physics(instance)
	instance.free()
	if _failed:
		quit(1)
		return

	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(EVIDENCE))
	if data.has("godot") and not _report.has("save_reload_byte_stable"):
		_report["save_reload_byte_stable"] = data["godot"].get("save_reload_byte_stable", false)
	_report["engine"] = Engine.get_version_info().string
	data["godot"] = _report
	var file := FileAccess.open(EVIDENCE, FileAccess.WRITE)
	file.store_string(JSON.stringify(data, "\t") + "\n")
	file.close()
	print("BUS_STOP_PREFAB_PASS ", JSON.stringify(_report))
	quit(0)


## Accumulate explicit failures so the headless process cannot report success after a bad check.
func _require(condition: bool, message: String) -> void:
	if not condition:
		_failed = true
		push_error(message)


## Save only this inherited wrapper, preserving its base scene and imported model ancestry.
func _roundtrip() -> void:
	var packed: PackedScene = ResourceLoader.load(
		PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_REPLACE,
	)
	var instance := packed.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	_require(saved.pack(instance) == OK, "Pack inherited wrapper")
	_require(ResourceSaver.save(saved, PREFAB) == OK, "Save inherited wrapper")
	_register_saved_uid(PREFAB)
	instance.free()


## Register freshly saved identities before the next filesystem scan sees those files.
func _register_saved_uid(path: String) -> void:
	var uid := ResourceLoader.get_resource_uid(path)
	if not ResourceUID.has_id(uid):
		ResourceUID.add_id(uid, path)


## Resolve every actual serialized dependency and verify UID-to-path registration.
func _check_dependencies(path: String) -> void:
	_require(ResourceLoader.load(path) != null, "Missing resource: " + path)
	var uid := ResourceLoader.get_resource_uid(path)
	_require(uid != ResourceUID.INVALID_ID, "Missing resource UID: " + path)
	_require(ResourceUID.has_id(uid), "Unregistered UID: " + path)
	_require(ResourceUID.get_id_path(uid) == path, "UID path mismatch: " + path)
	if path == PREFAB or path == MATERIAL:
		var header := FileAccess.get_file_as_string(path).get_slice("\n", 0)
		_require(header.contains('uid="' + ResourceUID.id_to_text(uid) + '"'),
			"UID missing from saved header: " + path)

	for dependency: String in ResourceLoader.get_dependencies(path):
		_check_dependencies(dependency.split("::")[-1])


## Permit exactly one front-face override and no transformed or replaced shared geometry.
func _check_model(instance: Node3D, reference: Node3D) -> void:
	var model := instance.get_node("Visuals/Model") as Node3D
	_require(model.transform == Transform3D.IDENTITY, "Corrective model transform")
	_require(model.scene_file_path == MODEL, "Unlinked model")
	var mesh := instance.get_node(MESH_PATH) as MeshInstance3D
	var original := reference.get_node(MESH_PATH) as MeshInstance3D
	_require(mesh.mesh == original.mesh, "Shared mesh replaced")
	_require(mesh.transform == Transform3D.IDENTITY, "Mesh transform")
	_require(mesh.material_override == null, "Whole-mesh override")
	_require(mesh.mesh.get_surface_count() == 3, "Surface count")
	_require(model.find_children("*", "MeshInstance3D", true, false).size() == 1, "Mesh count")
	for surface: int in mesh.mesh.get_surface_count():
		var override := mesh.get_surface_override_material(surface)
		if surface == 2:
			_require(override == load(MATERIAL), "Missing face override")
			_require(mesh.mesh.surface_get_material(surface).resource_name == "road_sign_face",
				"Wrong face slot")
		else:
			_require(override == null, "Hardware recolored")

	var bounds := mesh.get_aabb()
	_require(bounds.position.distance_to(Vector3(-.35, 0, -.14)) < .001, "Bounds minimum")
	_require(bounds.size.distance_to(Vector3(.70, 3.25, .28)) < .001, "Bounds size")
	_report["linked_model_identity"] = true
	_report["unchanged_mesh_one_face_override"] = true
	_report["godot_aabb_min_m"] = [-.35, 0, -.14]
	_report["godot_aabb_size_m"] = [.70, 3.25, .28]


## Keep the front artwork opaque, clamped, unlit and correctly filtered with mipmaps.
func _check_material() -> void:
	var material := load(MATERIAL) as StandardMaterial3D
	_require(material.albedo_texture.get_size() == Vector2(512, 512), "Texture size")
	_require(material.albedo_texture.get_image().has_mipmaps(), "Missing imported mipmaps")
	_require(material.albedo_color == Color.WHITE, "Texture multiplier")
	_require(not material.texture_repeat and not material.emission_enabled, "Repeat/emission")
	_require(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS,
		"Filtering")
	_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparency")
	_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Backface culling")
	_report["material"] = "512x512 opaque RGB, clamped linear mipmaps, no emission"


## Reuse the support's one static cylinder rather than authoring a second collision envelope.
func _check_collision(instance: Node3D, reference: Node3D) -> void:
	var body := instance.get_node("Collision/PoleBody") as StaticBody3D
	var shape := body.get_node("Shape") as CollisionShape3D
	var original := reference.get_node("Collision/PoleBody/Shape") as CollisionShape3D
	_require(instance.find_children("*", "CollisionObject3D", true, false).size() == 1,
		"Body count")
	_require(body.find_children("*", "CollisionShape3D", true, false).size() == 1, "Shape count")
	_require(shape.shape == original.shape and shape.transform == original.transform,
		"Inherited collision changed")
	var cylinder := shape.shape as CylinderShape3D
	_require(is_equal_approx(cylinder.radius, .14), "Cylinder radius")
	_require(is_equal_approx(cylinder.height, 2.5), "Cylinder height")
	_require(shape.position.is_equal_approx(Vector3(0, 1.25, 0)), "Ground datum")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Collision filtering")
	_report["inherited_collision_unchanged"] = true


## Exercise actual world queries: low post blocks, overhead plate and lateral bypass clear.
func _check_physics(instance: Node3D) -> void:
	var space := instance.get_world_3d().direct_space_state
	var low := PhysicsRayQueryParameters3D.create(Vector3(0, .5, -2), Vector3(0, .5, 2), 1)
	var hit := space.intersect_ray(low)
	_require(not hit.is_empty(), "Low ray missed post")
	if not hit.is_empty():
		_require(hit.collider == instance.get_node("Collision/PoleBody"), "Wrong body hit")

	var high := PhysicsRayQueryParameters3D.create(Vector3(0, 2.9, -2), Vector3(0, 2.9, 2), 1)
	_require(space.intersect_ray(high).is_empty(), "Overhead panel has collision")
	var capsule := CapsuleShape3D.new()
	capsule.radius = .35
	capsule.height = 1.8
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = 1
	query.transform.origin = Vector3(0, .9, 0)
	_require(not space.intersect_shape(query).is_empty(), "Capsule passed through post")
	query.transform.origin = Vector3(.8, .9, 0)
	_require(space.intersect_shape(query).is_empty(), "Clear bypass blocked")
	_report["physics_queries"] = {
		"low_ray_blocked": true, "overhead_ray_clear": true,
		"capsule_post_overlap": true, "capsule_x_0_8_bypass_clear": true,
		"capsule_radius_m": .35, "capsule_height_m": 1.8,
		"actor_movement_vehicle_network": "not tested; unchanged inherited collider",
	}
