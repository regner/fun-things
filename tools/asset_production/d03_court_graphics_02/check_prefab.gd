extends SceneTree

const PREFAB: String = "res://scenes/prefabs/environment/d03_court_graphics_02.tscn"
const MODEL: String = (
	"res://art/models/environment/d03_court_graphics_02/d03_court_graphics_02.glb"
)
const MATERIAL: String = (
	"res://art/materials/environment/d03_court_graphics_02/play_steps.tres"
)
const SCRATCH: String = "C:/tmp/ft/assets/d03_court_graphics_02/"
const BOUNDS_TOLERANCE_M: float = 0.001

var _failures: Array[String] = []
var _receipt: Dictionary = {}


## Defer checks until the headless tree has completed startup.
func _initialize() -> void:
	_run.call_deferred()


## Accumulate failures and return a nonzero exit rather than relying on debug assertions.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


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


## Require serialized identities, not merely successful fallback-path loading.
func _check_saved_identities(path: String) -> void:
	var text := FileAccess.get_file_as_string(path)
	_expect(text.get_slice("
", 0).contains("uid=\""), "Header UID: " + path)
	var dependencies: Dictionary = {}
	for line: String in text.split("
"):
		if line.begins_with("[ext_resource"):
			var dependency := line.get_slice("path=\"", 1).get_slice("\"", 0)
			_expect(line.contains("uid=\""), "Serialized dependency UID: " + dependency)
			if not line.contains("uid=\""):
				continue

			var saved_uid := line.get_slice("uid=\"", 1).get_slice("\"", 0)
			var uid := ResourceUID.text_to_id(saved_uid)
			_expect(uid != ResourceUID.INVALID_ID, "Valid dependency UID: " + dependency)
			_expect(ResourceUID.has_id(uid), "Registered dependency UID: " + dependency)
			if ResourceUID.has_id(uid):
				_expect(ResourceUID.get_id_path(uid) == dependency, "UID path: " + dependency)

			_expect(
				ResourceLoader.get_resource_uid(dependency) == uid,
				"UID resolves: " + dependency,
			)
			dependencies[dependency] = saved_uid

		if line.begins_with("[node"):
			_expect(line.contains("unique_id="), "Saved node identity: " + path)

	_receipt.get_or_add("serialized_dependency_uids", {})[path] = dependencies


## Save only the owned wrapper, retaining the external GLB instance and its ancestry.
func _save_prefab() -> void:
	var uid: int = ResourceLoader.get_resource_uid(PREFAB)
	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()
		ResourceUID.add_id(uid, PREFAB)

	var packed := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	_expect(packed is PackedScene, "Prefab dependency load")
	if not packed is PackedScene:
		return

	var instance: Node = (packed as PackedScene).instantiate()
	var saved := PackedScene.new()
	_expect(saved.pack(instance) == OK, "Prefab pack")
	_expect(ResourceSaver.save(saved, PREFAB) == OK, "Prefab save")
	_expect(ResourceSaver.set_uid(PREFAB, uid) == OK, "Retain scene UID")
	_write_dependency_uids(PREFAB)
	_check_saved_identities(PREFAB)
	instance.free()


## Compare two fresh load/pack/save passes after the first UID-generating normalization.
func _normalize(material: StandardMaterial3D) -> void:
	var uid: int = ResourceLoader.get_resource_uid(MATERIAL)
	if uid == ResourceUID.INVALID_ID:
		uid = ResourceUID.create_id()
		ResourceUID.add_id(uid, MATERIAL)

	_expect(ResourceSaver.save(material, MATERIAL) == OK, "Material normalization")
	_expect(ResourceSaver.set_uid(MATERIAL, uid) == OK, "Retain material UID")
	_write_dependency_uids(MATERIAL)
	_check_saved_identities(MATERIAL)
	_save_prefab()
	var scene_hash := FileAccess.get_sha256(PREFAB)
	var material_hash := FileAccess.get_sha256(MATERIAL)
	for pass_index: int in range(2):
		_save_prefab()
		var fresh := ResourceLoader.load(
			MATERIAL, "StandardMaterial3D", ResourceLoader.CACHE_MODE_IGNORE
		)
		_expect(ResourceSaver.save(fresh, MATERIAL) == OK, "Material resave")
		_expect(ResourceSaver.set_uid(MATERIAL, uid) == OK, "Retain material UID")
		_write_dependency_uids(MATERIAL)
		_check_saved_identities(MATERIAL)
		_expect(FileAccess.get_sha256(PREFAB) == scene_hash, "Roundtrip scene bytes")
		_expect(FileAccess.get_sha256(MATERIAL) == material_hash, "Roundtrip material bytes")
		_receipt["roundtrip_%s_byte_stable" % (pass_index + 1)] = (
			FileAccess.get_sha256(PREFAB) == scene_hash
			and FileAccess.get_sha256(MATERIAL) == material_hash
		)

	_receipt["prefab_sha256"] = scene_hash
	_receipt["material_sha256"] = material_hash
	_receipt["prefab_uid"] = ResourceUID.id_to_text(ResourceLoader.get_resource_uid(PREFAB))
	_receipt["material_uid"] = ResourceUID.id_to_text(ResourceLoader.get_resource_uid(MATERIAL))


## Verify the external artwork material and imported mipmapped texture contract.
func _check_material(material: StandardMaterial3D) -> void:
	_expect(material.albedo_texture != null, "Missing artwork PNG dependency")
	if material.albedo_texture == null:
		return

	_expect(material.albedo_texture.get_size() == Vector2(512, 1024), "Artwork texture size")
	var image: Image = material.albedo_texture.get_image()
	_expect(image.has_mipmaps(), "Generated mipmaps")
	_expect(image.get_format() == Image.FORMAT_RGB8, "Lossless RGB8 artwork import")
	_receipt["texture_image_bytes_including_mips"] = image.get_data().size()
	_receipt["texture_image_format"] = image.get_format()
	var config := ConfigFile.new()
	var texture_path: String = material.albedo_texture.resource_path
	_expect(config.load(texture_path + ".import") == OK, "Texture import sidecar load")
	_expect(config.get_value("params", "compress/mode") == 0, "Lossless texture import")
	_expect(material.albedo_color == Color.WHITE, "No albedo colour multiplier")
	_expect(is_equal_approx(material.roughness, 0.94), "Matte paint roughness")
	_expect(material.metallic == 0 and not material.emission_enabled, "No metal or emission")
	_expect(
		material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED,
		"Opaque stepping artwork",
	)
	_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Single upward-facing artwork")
	_expect(not material.texture_repeat, "Clamp atlas UV edges")
	_expect(
		material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS,
		"Linear mipmap filtering"
	)


## Inspect actual imported resources and require an entirely collision-free linked wrapper.
func _inspect(instance: Node3D) -> void:
	_expect(instance.transform == Transform3D.IDENTITY, "Ground-centred wrapper pivot")
	var visuals: Node3D = instance.get_node("Visuals") as Node3D
	_expect(visuals.transform == Transform3D.IDENTITY, "Identity visual parent")
	var model: Node3D = instance.get_node("Visuals/Model") as Node3D
	_expect(model.scene_file_path == MODEL, "Linked GLB ancestry")
	_expect(model.transform == Transform3D.IDENTITY, "Identity model transform")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_expect(meshes.size() == 1, "One imported mesh")
	if meshes.size() != 1:
		return

	var mesh := meshes[0] as MeshInstance3D
	_expect(mesh.transform == Transform3D.IDENTITY, "Identity imported mesh transform")
	_expect(mesh.mesh.resource_path.begins_with(MODEL), "Mesh remains GLB resource")
	_expect(mesh.mesh.get_surface_count() == 1, "One material surface")
	_expect(mesh.material_override == null, "No mesh material override")
	_expect(mesh.get_surface_override_material(0) == null, "No editable child face override")
	var imported_material := mesh.mesh.surface_get_material(0)
	_expect(imported_material.resource_path == MATERIAL, "Import maps external artwork material")
	var bounds := mesh.get_aabb()
	_expect(
		bounds.position.distance_to(Vector3(-.95, .015, -2.65)) < BOUNDS_TOLERANCE_M,
		"Source/import AABB minimum"
	)
	_expect(bounds.size.distance_to(Vector3(1.9, 0, 5.3)) < BOUNDS_TOLERANCE_M, "AABB size")
	_expect(
		instance.find_children("*", "CollisionObject3D", true, false).is_empty(),
		"Flush artwork must not introduce terrain collision"
	)
	_receipt.merge({
		"mesh_count": meshes.size(),
		"surface_count": mesh.mesh.get_surface_count(),
		"aabb_min": [bounds.position.x, bounds.position.y, bounds.position.z],
		"aabb_size": [bounds.size.x, bounds.size.y, bounds.size.z],
		"external_material": imported_material.resource_path,
		"linked_identity_model": true,
		"collision_objects": 0,
		"material_overrides": 0,
	})


## Fail before runtime inspection if either owned resource omits serialized identities.
func _check_owned_identities() -> bool:
	for path: String in [PREFAB, MATERIAL]:
		_check_saved_identities(path)

	return _failures.is_empty()


## Load, optionally normalize, check all dependencies and write a fresh bounded receipt.
func _run() -> void:
	if not OS.get_cmdline_user_args().has("--normalize") and not _check_owned_identities():
		quit(1)
		return

	var version: Dictionary = Engine.get_version_info()
	_expect(version.string == "4.8-dev7 (official)", "Pinned engine version")
	_expect(str(version.hash).begins_with("c971f93e7"), "Pinned engine commit")
	var material := load(MATERIAL) as StandardMaterial3D
	_expect(material != null, "Material resource load")
	if material == null:
		quit(1)
		return

	_check_material(material)
	var normalize: bool = OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		_normalize(material)
		_finish(true)
		return

	_dependencies(PREFAB)
	var packed := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	_expect(packed is PackedScene, "Fresh prefab load")
	if not packed is PackedScene:
		quit(1)
		return

	var instance := (packed as PackedScene).instantiate() as Node3D
	_inspect(instance)
	instance.free()
	for path: String in [PREFAB, MODEL, MATERIAL]:
		var uid: int = ResourceLoader.get_resource_uid(path)
		_expect(uid != ResourceUID.INVALID_ID, "Registered resource UID: " + path)
		_receipt[path.get_file() + "_uid"] = ResourceUID.id_to_text(uid)

	var roundtrip: Dictionary = JSON.parse_string(
		FileAccess.get_file_as_string(SCRATCH + "roundtrip.json")
	)
	_expect(roundtrip.get("ok", false), "Roundtrip receipt passes")
	_expect(roundtrip["prefab_sha256"] == FileAccess.get_sha256(PREFAB), "Final scene bytes")
	_expect(roundtrip["material_sha256"] == FileAccess.get_sha256(MATERIAL), "Final material bytes")
	_expect(roundtrip["prefab_uid"] == _receipt[PREFAB.get_file() + "_uid"], "Stable scene UID")
	_expect(
		roundtrip["material_uid"] == _receipt[MATERIAL.get_file() + "_uid"],
		"Stable material UID",
	)
	_receipt["roundtrip"] = roundtrip
	_finish(false)


## Verify every imported dependency resolves through its registered saved UID.
func _dependencies(path: String) -> void:
	_expect(ResourceLoader.load(path) != null, "Resource loads: " + path)
	var uid: int = ResourceLoader.get_resource_uid(path)
	_expect(uid != ResourceUID.INVALID_ID, "Resource UID: " + path)
	_expect(ResourceUID.has_id(uid), "Registered UID: " + path)
	_expect(ResourceUID.get_id_path(uid) == path, "UID resolves: " + path)
	for dependency: String in ResourceLoader.get_dependencies(path):
		_dependencies(dependency.split("::")[-1])


## Write bounded normalization or final check evidence and return a failing exit on any error.
func _finish(normalize: bool) -> void:
	_receipt["engine"] = Engine.get_version_info().string
	_receipt["engine_hash"] = Engine.get_version_info().hash
	_receipt["texture_size"] = [512, 1024]
	_receipt["mipmaps"] = true
	_receipt["failures"] = _failures
	_receipt["ok"] = _failures.is_empty()
	var name: String = "roundtrip.json" if normalize else "prefab-check.json"
	var file := FileAccess.open(SCRATCH + name, FileAccess.WRITE)
	file.store_string(JSON.stringify(_receipt, "	") + "
")
	file.close()
	print("MOTIF_PREFAB_CHECK ", JSON.stringify(_receipt))
	quit(0 if _failures.is_empty() else 1)
