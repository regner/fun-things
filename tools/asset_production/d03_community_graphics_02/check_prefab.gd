extends SceneTree
## Validate the full-scale plaque, its four face options, mounting and saved identities.

const NID := "d03_community_graphics_02"
const PREFAB := "res://scenes/prefabs/environment/" + NID + ".tscn"
const FIXTURE := "res://tools/asset_production/" + NID + "/check_scene.tscn"
const GLB := "res://art/models/environment/" + NID + "/" + NID + ".glb"
const MATERIAL_DIR := "res://art/materials/environment/" + NID + "/"
const TEXTURE_DIR := "res://art/textures/environment/" + NID + "/"
const SCRATCH := "C:/tmp/ft/assets/" + NID + "/"
const MESH_PATH := "Visuals/Model/D03CommunityGraphics02/D03CommunityGraphics02_Mesh"

var _failures: Array[String] = []
var _result: Dictionary = {}
var _materials: Array[Material] = []


## Defer until isolated resource initialization is complete.
func _initialize() -> void:
	_run.call_deferred()


## Accumulate explicit contract failures and return nonzero rather than hiding errors.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Enumerate the one prefab, saved mounting fixture and four selectable material resources.
func _owned_resources() -> Array[String]:
	var paths: Array[String] = []
	for number: String in ["01", "02", "03", "04"]:
		paths.append(MATERIAL_DIR + "entrance_" + number + ".tres")
	paths.append(PREFAB)
	paths.append(FIXTURE)
	return paths


## Preserve embedded UIDs, allocating identities only on first normalization.
func _saved_uid(path: String) -> int:
	var header := FileAccess.get_file_as_string(path).get_slice("\n", 0)
	var uid := ResourceUID.INVALID_ID
	if header.contains("uid=\""):
		uid = ResourceUID.text_to_id(header.get_slice("uid=\"", 1).get_slice("\"", 0))
	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()
	if not ResourceUID.has_id(uid):
		ResourceUID.add_id(uid, path)
	return uid


## Retain explicit dependency UIDs even when the headless runtime saver omits them.
func _write_dependency_uids(path: String) -> void:
	var lines := FileAccess.get_file_as_string(path).split("\n")
	for index: int in range(lines.size()):
		var line := lines[index]
		if not line.begins_with("[ext_resource"):
			continue
		var dependency := line.get_slice("path=\"", 1).get_slice("\"", 0)
		var uid := ResourceLoader.get_resource_uid(dependency)
		_expect(uid != ResourceUID.INVALID_ID, "Dependency identity: " + dependency)
		if not line.contains("uid=\""):
			lines[index] = line.replace(" path=", " uid=\"%s\" path=" % ResourceUID.id_to_text(uid))
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string("\n".join(lines))


## Repack one editable scene while retaining its linked imported descendants.
func _repack(source: PackedScene) -> PackedScene:
	var node := source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_expect(packed.pack(node) == OK, "Scene pack")
	node.free()
	return packed


## Load, pack and resave only owned scenes and materials with stable UIDs and linked geometry.
func _save_resources() -> void:
	for path: String in _owned_resources():
		var uid := _saved_uid(path)
		var resource := ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_IGNORE)
		_expect(resource != null, "Resource load: " + path)
		if resource is PackedScene:
			resource = _repack(resource as PackedScene)
		_expect(ResourceSaver.save(resource, path) == OK, "Owned resource save")
		_expect(ResourceSaver.set_uid(path, uid) == OK, "Preserved UID")
		_write_dependency_uids(path)


## Hash every owned editable resource, including dependency and node identity text.
func _hashes() -> Dictionary:
	var result := {}
	for path: String in _owned_resources():
		result[path] = FileAccess.get_sha256(path)
	return result


## Prove two complete post-normalization save/reload cycles and optional fresh-process stability.
func _roundtrip() -> void:
	var before := _hashes()
	_save_resources()
	var hashes := _hashes()
	if OS.get_cmdline_user_args().has("--verify-stable"):
		_expect(before == hashes, "Fresh process initial stability")
		_result["fresh_process_initial_byte_stable"] = before == hashes
	for cycle: int in range(2):
		_save_resources()
		var stable := hashes == _hashes()
		_expect(stable, "Roundtrip drift: " + str(cycle))
		_result["roundtrip_%d_byte_stable" % (cycle + 1)] = stable
	_result["resource_hashes"] = hashes


## Inspect all four imported images, complete mips and opaque matte material settings.
func _check_materials() -> void:
	var bytes := 0
	var config := ConfigFile.new()
	for number: String in ["01", "02", "03", "04"]:
		var material := load(MATERIAL_DIR + "entrance_" + number + ".tres") as StandardMaterial3D
		_materials.append(material)
		_expect(material.albedo_color == Color.WHITE, "White texture multiplier")
		_expect(is_equal_approx(material.roughness, 0.84), "Matte ink")
		_expect(material.metallic == 0.0 and not material.emission_enabled, "Quiet ink")
		_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque")
		_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back culling")
		_expect(not material.texture_repeat, "Clamp")
		_expect(
			material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS,
			"Mipmapped linear filter"
		)
		var texture_path := TEXTURE_DIR + "entrance_" + number + "_albedo.png"
		_expect(material.albedo_texture.resource_path == texture_path, "Texture link")
		var image := material.albedo_texture.get_image()
		_expect(image.get_size() == Vector2i(280, 200), "Correct-scale face resolution")
		_expect(image.get_format() == Image.FORMAT_RGB8, "RGB8 data")
		_expect(image.has_mipmaps() and image.get_mipmap_count() == 8, "Complete mip chain")
		bytes += image.get_data_size()
		config.clear()
		_expect(config.load(texture_path + ".import") == OK, "Texture metadata")
		_expect(config.get_value("params", "compress/mode") == 0, "Lossless import")
		_expect(config.get_value("params", "detect_3d/compress_to") == 0, "No auto compression")
	_result["four_textures_cpu_bytes_with_mips"] = bytes


## Check the actual linked mesh and ensure variants change only the front-face material.
func _check_visuals(plaque: Node3D) -> void:
	var model := plaque.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == GLB, "Linked original Blender carrier")
	_expect(model.transform == Transform3D.IDENTITY, "Identity imported model")
	_expect((plaque.get_node("Visuals") as Node3D).transform == Transform3D.IDENTITY, "Visuals")
	_expect(model.find_children("*", "MeshInstance3D", true, false).size() == 1, "One mesh")
	var mesh := plaque.get_node(MESH_PATH) as MeshInstance3D
	_expect(mesh.transform == Transform3D.IDENTITY, "Identity mesh")
	_expect(mesh.material_override == null, "No whole-mesh override")
	_expect(mesh.mesh.get_surface_count() == 2, "Two surfaces")
	_expect(mesh.mesh.surface_get_material(0).resource_name == "entrance_number_face", "Face slot")
	_expect(mesh.mesh.surface_get_material(1).resource_name == "entrance_plaque_edge", "Edge slot")
	_expect(mesh.get_surface_override_material(0) == _materials[0], "Default 01")
	_expect(mesh.get_surface_override_material(1) == null, "Untouched edges")
	_expect(mesh.get_aabb().position.is_equal_approx(Vector3(-0.28, -0.2, -0.032)), "Bounds min")
	_expect(
		mesh.get_aabb().size.is_equal_approx(Vector3(0.56, 0.4, 0.032)),
		"Full-scale dimensions",
	)
	var original_mesh := mesh.mesh
	for material: Material in _materials:
		mesh.set_surface_override_material(0, material)
		_expect(mesh.mesh == original_mesh, "Variant cannot replace geometry")
		_expect(mesh.get_active_material(0) == material, "Variant front")
		_expect(
			mesh.get_active_material(1) == original_mesh.surface_get_material(1),
			"Variant edge",
		)
	_result["face_material_options_checked"] = 4


## Assert physical pier fit against the delivered module, with no duplicate wall collider.
func _check_mount() -> void:
	var fixture := (load(FIXTURE) as PackedScene).instantiate()
	var plaque := fixture.get_node("Plaque") as Node3D
	_expect(plaque.position.is_equal_approx(Vector3(0.785, 1.85, -6)), "Documented pier anchor")
	_expect(plaque.scale == Vector3.ONE and plaque.rotation == Vector3.ZERO, "Never scaled")
	_expect(plaque.find_children("*", "CollisionObject3D", true, false).is_empty(), "Flush visual")
	_expect(
		fixture.find_children("*", "CollisionShape3D", true, false).size() == 1,
		"One wall shape",
	)
	var mesh := plaque.get_node(MESH_PATH) as MeshInstance3D
	var bounds := plaque.transform * mesh.get_aabb()
	_expect(bounds.position.x > 0.45 and bounds.end.x < 1.12, "Fits clear pier width")
	_expect(bounds.position.y > 0.2 and bounds.end.y < 2.7, "Clear ribbon and brow")
	_expect(is_equal_approx(bounds.end.z, -6.0), "Wall-contact backing")
	var bay := fixture.get_node("Bay") as Node3D
	_expect(bay.transform == Transform3D.IDENTITY, "Unchanged bay placement")
	var shape := bay.get_node("Collision/Body/Core") as CollisionShape3D
	_expect((shape.shape as BoxShape3D).size == Vector3(6, 3.2, 12), "Unchanged building envelope")
	_result["pier_edge_clearance_m"] = [bounds.position.x - 0.45, 1.12 - bounds.end.x]
	_result["mounted_aabb"] = { "min": str(bounds.position), "max": str(bounds.end) }
	fixture.free()


## Verify every saved header/dependency/node identity and resolve each resource UID.
func _check_saved_identities() -> void:
	for path: String in _owned_resources():
		var text := FileAccess.get_file_as_string(path)
		_expect(text.get_slice("\n", 0).contains("uid=\""), "Header UID")
		for line: String in text.split("\n"):
			if line.begins_with("[ext_resource"):
				_expect(line.contains("uid=\""), "Explicit ext_resource UID")
				var uid := ResourceUID.text_to_id(line.get_slice("uid=\"", 1).get_slice("\"", 0))
				var dependency := line.get_slice("path=\"", 1).get_slice("\"", 0)
				_expect(ResourceLoader.get_resource_uid(dependency) == uid, "UID resolves")
			if line.begins_with("[node"):
				_expect(line.contains("unique_id="), "Saved node identity")


## Execute bounded checks and retain actual observations, never claim gameplay acceptance.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		_roundtrip()
	_check_materials()
	var plaque := (load(PREFAB) as PackedScene).instantiate() as Node3D
	_expect(plaque.transform == Transform3D.IDENTITY, "Identity plaque root")
	_check_visuals(plaque)
	plaque.free()
	_check_mount()
	_check_saved_identities()
	_result["engine"] = Engine.get_version_info().string
	_result["failures"] = _failures
	_result["ok"] = _failures.is_empty()
	var name := "roundtrip.json" if normalize else "prefab-check.json"
	var file := FileAccess.open(SCRATCH + name, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print("ENTRANCE_PREFAB_CHECK: ", JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
