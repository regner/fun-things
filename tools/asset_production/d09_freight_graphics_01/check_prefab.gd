extends SceneTree
## Audit the actual saved linked fascia and its one authorized artwork-face override.

const PREFAB := "res://scenes/prefabs/environment/d09_freight_graphics_01.tscn"
const MODEL := "res://art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb"
const MATERIAL := "res://art/materials/environment/d09_freight_graphics_01/warehouse_fascia.tres"
const TEXTURE := (
	"res://art/textures/environment/d09_freight_graphics_01/warehouse_fascia_albedo.png"
)
const SCRATCH := "C:/tmp/ft/assets/d09_freight_graphics_01/"

var _failures: Array[String] = []
var _result: Dictionary = {}


## Run after the isolated headless SceneTree has initialized.
func _initialize() -> void:
	_run.call_deferred()


## Accumulate bounded failures and return a nonzero process exit at completion.
func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


## Preserve an inline saved UID, or allocate it once for an unsaved owned resource.
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


## Normalize only the owned material and wrapper, preserving linked imported geometry.
func _save_resources() -> void:
	var material_uid := _saved_uid(MATERIAL)
	var material := ResourceLoader.load(MATERIAL, "", ResourceLoader.CACHE_MODE_IGNORE)
	_expect(ResourceSaver.save(material, MATERIAL) == OK, "Material save")
	_expect(ResourceSaver.set_uid(MATERIAL, material_uid) == OK, "Material UID save")
	var scene_uid := _saved_uid(PREFAB)
	var source := ResourceLoader.load(
		PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE
	) as PackedScene
	if source == null:
		_expect(false, "Missing prefab during save")
		return

	var instance := source.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var packed := PackedScene.new()
	_expect(packed.pack(instance) == OK, "Prefab pack")
	_expect(ResourceSaver.save(packed, PREFAB) == OK, "Prefab save")
	_expect(ResourceSaver.set_uid(PREFAB, scene_uid) == OK, "Prefab UID save")
	instance.free()


## Prove two full save/reload cycles leave scene/material bytes and inline identities unchanged.
func _roundtrip() -> void:
	_save_resources()
	var scene_hash := FileAccess.get_sha256(PREFAB)
	var material_hash := FileAccess.get_sha256(MATERIAL)
	for cycle: int in range(2):
		_save_resources()
		_expect(FileAccess.get_sha256(PREFAB) == scene_hash, "Scene drift: " + str(cycle))
		_expect(FileAccess.get_sha256(MATERIAL) == material_hash, "Material drift: " + str(cycle))
	_result["stable_roundtrip_count"] = 2
	_result["scene_sha256"] = scene_hash
	_result["material_sha256"] = material_hash


## Check imported texture settings as well as material runtime properties.
func _check_material() -> void:
	var material := load(MATERIAL) as StandardMaterial3D
	_expect(material != null, "Missing material")
	if material == null:
		return

	_expect(material.albedo_texture != null, "Missing texture")
	_expect(material.albedo_texture.get_size() == Vector2(2000, 400), "Texture size")
	_expect(material.albedo_texture.resource_path == TEXTURE, "Texture dependency")
	_expect(material.albedo_color == Color.WHITE, "White texture multiplier")
	_expect(is_equal_approx(material.roughness, 0.62), "Roughness")
	_expect(material.metallic == 0.0 and not material.emission_enabled, "Non-emissive ink")
	_expect(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque ink")
	_expect(material.cull_mode == BaseMaterial3D.CULL_BACK, "Back culling")
	_expect(not material.texture_repeat, "Clamp texture")
	_expect(
		material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS,
		"Linear mipmapped filtering"
	)
	var config := ConfigFile.new()
	_expect(config.load(TEXTURE + ".import") == OK, "Texture sidecar load")
	_expect(config.get_value("params", "mipmaps/generate") == true, "Mipmaps enabled")
	_expect(config.get_value("params", "compress/mode") == 0, "Lossless compression")
	_expect(config.get_value("params", "detect_3d/compress_to") == 0, "No auto conversion")


## Compare every mesh/surface with an independent pristine GLB instance.
func _check_meshes(model: Node3D) -> void:
	var reference := (load(MODEL) as PackedScene).instantiate()
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	var surfaces := 0
	var overrides := 0
	var bounds := AABB()
	for index: int in range(meshes.size()):
		var mesh := meshes[index] as MeshInstance3D
		var original := reference.get_node(model.get_path_to(mesh)) as MeshInstance3D
		_expect(mesh.mesh == original.mesh, "Mesh must remain the imported resource")
		_expect(mesh.transform == Transform3D.IDENTITY, "Mesh transform")
		_expect(mesh.material_override == null, "No whole-object material override")
		bounds = mesh.get_aabb() if index == 0 else bounds.merge(mesh.get_aabb())
		for surface: int in range(mesh.mesh.get_surface_count()):
			surfaces += 1
			var override := mesh.get_surface_override_material(surface)
			if override == null:
				continue

			overrides += 1
			_expect(mesh.name == "fascia_artwork_carrier" and surface == 0, "Face-only slot")
			_expect(override.resource_path == MATERIAL, "Owned artwork material")
			_expect(
				mesh.mesh.surface_get_material(surface).resource_name == "fascia_artwork_face",
				"Original artwork slot name"
			)
	_expect(meshes.size() == 7 and surfaces == 8 and overrides == 1, "Mesh/surface counts")
	_expect(bounds.position.is_equal_approx(Vector3(-1.6, -0.4, -0.14)), "AABB minimum")
	_expect(bounds.size.is_equal_approx(Vector3(3.2, 0.8, 0.14)), "AABB dimensions")
	_result.merge({ "meshes": meshes.size(), "surfaces": surfaces, "face_overrides": overrides })
	reference.free()


## Check saved dependencies and emit either the normalization or fresh-process receipt.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		_roundtrip()

	_check_material()
	var packed := load(PREFAB) as PackedScene
	_expect(packed != null, "Prefab load")
	if packed != null:
		var instance := packed.instantiate()
		var model := instance.get_node("Visuals/Model") as Node3D
		_expect(model.scene_file_path == MODEL, "Linked GLB ancestry")
		_expect(model.transform == Transform3D.IDENTITY, "Identity Visuals/Model")
		_expect(
			(model.get_node("city_shop_fittings_02") as Node3D).transform == Transform3D.IDENTITY,
			"Identity shared export root"
		)
		_expect(
			instance.find_children("*", "CollisionObject3D", true, false).is_empty(),
			"No collision",
		)
		_check_meshes(model)
		instance.free()
	for path: String in [PREFAB, MATERIAL, MODEL, TEXTURE]:
		var uid := ResourceLoader.get_resource_uid(path)
		_expect(uid != ResourceUID.INVALID_ID, "Missing UID: " + path)
		_result[path] = ResourceUID.id_to_text(uid)
	_result["engine"] = Engine.get_version_info().string
	_result["failures"] = _failures
	_result["status"] = "PASS" if _failures.is_empty() else "FAIL"
	var output := SCRATCH + ("normalize.json" if normalize else "prefab.json")
	var file := FileAccess.open(output, FileAccess.WRITE)
	file.store_string(JSON.stringify(_result, "\t") + "\n")
	file.close()
	print("FREIGHT_PREFAB_", _result["status"], ": ", JSON.stringify(_result))
	quit(0 if _failures.is_empty() else 1)
