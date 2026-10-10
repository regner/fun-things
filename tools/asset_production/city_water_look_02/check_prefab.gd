extends SceneTree
## Verify the linked water-study swatch, external PBR material and stable saved identities.

const PREFAB := "res://scenes/prefabs/environment/city_water_look_02.tscn"
const MATERIAL := "res://art/materials/environment/city_water_look_02/quiet_basin.tres"
const MODEL := "res://art/models/environment/city_water_look_02/city_water_look_02.glb"
const TEXTURES := "res://art/textures/environment/city_water_look_02/quiet_basin_"
const EDITOR_STARTUP_SECONDS := 3.0
const RECEIPT := "C:/tmp/ft/assets/city_water_look_02/prefab.json"

var _failed := false
var _observations: Dictionary = {}


## Defer until the engine has initialized its resource services.
func _initialize() -> void:
	_start.call_deferred()


## Wait for isolated editor startup so resource saves do not race its initial scan.
func _start() -> void:
	if Engine.is_editor_hint():
		await create_timer(EDITOR_STARTUP_SECONDS).timeout
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame  # gdstyle:ignore=quality/await-in-loop

	_run()


## Prepare owned import settings, or verify and optionally normalize the saved wrapper.
func _run() -> void:
	var version := Engine.get_version_info()
	_require(version.major == 4 and version.minor == 8 and version.status == "dev7")
	_require(str(version.hash).begins_with("c971f93e7"))
	if OS.get_cmdline_user_args().has("--prepare"):
		_prepare_imports()
		if _failed:
			quit(1)
			return

		print("WATER_IMPORT_SETTINGS_PASS: reimport before validating")
		quit()
		return

	var normalize := OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		_require(Engine.is_editor_hint(), "UID-preserving saves require --editor")
		_roundtrip()
		var first := FileAccess.get_file_as_bytes(PREFAB)
		_roundtrip()
		_require(first == FileAccess.get_file_as_bytes(PREFAB), "Unstable scene identities")

	var instance := (load(PREFAB) as PackedScene).instantiate()
	var model := instance.get_node("Visuals/Model") as Node3D
	_require(model.transform == Transform3D.IDENTITY and model.scene_file_path == MODEL)
	_require(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	_require(meshes.size() == 1)
	_check_mesh(meshes[0] as MeshInstance3D)
	if _failed:
		instance.free()
		quit(1)
		return

	instance.free()
	_write_receipt(normalize)


## Write the checked engine measurements after all helper checks have succeeded.
func _write_receipt(normalize: bool) -> void:
	var receipt := {
		"status": "PASS", "engine": Engine.get_version_info().string,
		"meshes": 1, "surfaces": 1, "vertices": 4, "triangles": 2,
		"aabb_min": [-8, 0, -8], "aabb_max": [8, 0, 8],
		"linked_model": MODEL, "external_material": MATERIAL,
		"identity_model_transform": true, "unit_up_normals_and_tangents": true,
		"no_collision_or_material_overrides": true, "texture_size": [512, 512],
		"normal_map": "OpenGL +Y, no inversion", "filter": "linear_mipmap_repeat",
		"normalized_second_roundtrip_byte_identical": normalize,
	}
	receipt.merge(_observations, true)
	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	print("WATER_PREFAB_PASS: linked geometry, external material, bounds, normals, UV tangents")
	quit()


## Require unchanged imported geometry, a planar 16m swatch and its material remap.
func _check_mesh(mesh: MeshInstance3D) -> void:
	_require(mesh.transform == Transform3D.IDENTITY)
	_require(mesh.mesh.get_surface_count() == 1 and mesh.material_override == null)
	_require(mesh.get_surface_override_material(0) == null)
	var reference := (load(MODEL) as PackedScene).instantiate()
	var original := reference.find_children("*", "MeshInstance3D", true, false)[0]
	_require(mesh.mesh == original.mesh, "Keep the original imported mesh resource")
	var material := mesh.mesh.surface_get_material(0) as StandardMaterial3D
	_check_material(material)
	var bounds := mesh.get_aabb()
	_require(bounds.position.distance_to(Vector3(-8, 0, -8)) <= 0.001)
	_require(bounds.size.distance_to(Vector3(16, 0, 16)) <= 0.001)
	_observations["aabb_min"] = [bounds.position.x, bounds.position.y, bounds.position.z]
	_observations["aabb_max"] = [bounds.end.x, bounds.end.y, bounds.end.z]
	_check_arrays(mesh.mesh.surface_get_arrays(0))
	reference.free()


## Inspect actual imported indices, up normals and generated tangent frames.
func _check_arrays(arrays: Array) -> void:
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
	var tangents: PackedFloat32Array = arrays[Mesh.ARRAY_TANGENT]
	var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
	_require(vertices.size() == 4 and indices.size() == 6 and tangents.size() == 16)
	for normal: Vector3 in normals:
		_require(normal.distance_to(Vector3.UP) < 0.0001)
	for index: int in range(4):
		var tangent := Vector3(tangents[index * 4], tangents[index * 4 + 1],
			tangents[index * 4 + 2])
		_require(is_equal_approx(tangent.length(), 1.0))


## Save deterministic material remapping and lossless mipmapped texture import settings.
func _prepare_imports() -> void:
	_require(Engine.is_editor_hint())
	var material := load(MATERIAL) as StandardMaterial3D
	_require(material != null)
	_require(ResourceSaver.save(material, MATERIAL) == OK)
	var config := ConfigFile.new()
	_require(config.load(MODEL + ".import") == OK)
	config.set_value("params", "_subresources", {
		"materials": {"quiet_basin": {
			"use_external/enabled": true, "use_external/path": MATERIAL,
		}},
	})
	_require(config.save(MODEL + ".import") == OK)
	for suffix: String in ["albedo", "normal"]:
		var path := TEXTURES + suffix + ".png.import"
		_require(config.load(path) == OK)
		config.set_value("params", "mipmaps/generate", true)
		config.set_value("params", "compress/mode", 0)
		config.set_value("params", "compress/normal_map", 1 if suffix == "normal" else 0)
		config.set_value("params", "detect_3d/compress_to", 0)
		_require(config.save(path) == OK)


## Require a quiet opaque water material with no simulation, emission or transparency.
func _check_material(material: StandardMaterial3D) -> void:
	_require(material != null and material.resource_path == MATERIAL)
	_require(material.albedo_color == Color.WHITE)
	_require(material.albedo_texture.get_size() == Vector2(512, 512))
	_require(material.normal_texture.get_size() == Vector2(512, 512))
	_require(material.normal_enabled and is_equal_approx(material.normal_scale, 1.0))
	_require(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	_require(material.texture_repeat and not material.emission_enabled)
	_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	_require(material.cull_mode == BaseMaterial3D.CULL_BACK)
	_require(is_equal_approx(material.roughness, 0.40))
	_require(is_equal_approx(material.metallic_specular, 0.25) and material.metallic == 0.0)
	var config := ConfigFile.new()
	for suffix: String in ["albedo", "normal"]:
		_require(config.load(TEXTURES + suffix + ".png.import") == OK)
		_require(config.get_value("params", "mipmaps/generate"))
		_require(not config.get_value("params", "process/normal_map_invert_y"))


## Pack and resave only the owned wrapper, preserving its linked imported instance.
func _roundtrip() -> void:
	var packed := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_REPLACE)
	var instance := (packed as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	_require(saved.pack(instance) == OK)
	_require(ResourceSaver.save(saved, PREFAB) == OK)
	instance.free()


## Keep helper failures fatal to the whole check rather than emitting a false PASS receipt.
func _require(condition: bool, message := "Water swatch contract failed") -> void:
	if not condition:
		_failed = true
		push_error(message)
