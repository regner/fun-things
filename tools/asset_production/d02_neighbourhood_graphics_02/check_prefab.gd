extends "res://tools/asset_production/d02_neighbourhood_graphics_01/check_prefab.gd"
## Verify face-only artwork on the unchanged wall panel, preserving saved identities.

const PARKING_NID := "d02_neighbourhood_graphics_02"
const PARKING_PREFAB := "res://scenes/prefabs/environment/" + PARKING_NID + ".tscn"
const PARKING_MATERIAL := "res://art/materials/environment/" + PARKING_NID + "/parking_request.tres"
const PARKING_TEXTURE := (
	"res://art/textures/environment/" + PARKING_NID + "/parking_request_albedo.png"
)
const PARKING_RECEIPT := "C:/tmp/ft/assets/" + PARKING_NID + "/prefab.json"


## Defer resource inspection until the tree has initialized.
func _initialize() -> void:
	_run.call_deferred()


## Check the actual dependency chain, optionally normalizing only owned resources.
func _run() -> void:
	var material := load(PARKING_MATERIAL) as StandardMaterial3D
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.resource_path == PARKING_TEXTURE)
	assert(material.albedo_texture.get_size() == Vector2(1220, 820))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE and is_equal_approx(material.roughness, 0.8))
	assert(is_zero_approx(material.metallic))
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var roundtrips: Array[String] = []
	if normalize:
		assert(Engine.is_editor_hint())
		assert(ResourceSaver.save(material, PARKING_MATERIAL) == OK)
		_roundtrip()
		# Initial normalization establishes new IDs; the following two cycles must retain them.
		var initial := FileAccess.get_file_as_bytes(PARKING_PREFAB)
		for cycle: int in range(2):
			_roundtrip()
			assert(initial == FileAccess.get_file_as_bytes(PARKING_PREFAB), "Saved identity drift")
			roundtrips.append(FileAccess.get_sha256(PARKING_PREFAB))

	var instance := (load(PARKING_PREFAB) as PackedScene).instantiate()
	var reference := (load(BASE) as PackedScene).instantiate()
	assert(instance.transform == Transform3D.IDENTITY)
	_compare_hierarchy(instance, reference)
	assert(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == MODEL)
	var result := _inspect_model(model, reference.get_node("Visuals/Model"), material)
	result.merge({
		"status": "PASS", "engine": Engine.get_version_info().string,
		"prefab": PARKING_PREFAB, "prefab_sha256": FileAccess.get_sha256(PARKING_PREFAB),
		"two_stable_roundtrip_sha256": roundtrips,
		"mipmaps_present": true, "texture_dimensions": [1220, 820],
		"identity_model_transform": true, "hierarchy_and_geometry_unchanged": true,
		"collision": "None; mounted decorative face inherits facade-owned blocking",
	})
	var file := FileAccess.open(PARKING_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(result, "\t") + "\n")
	file.close()
	instance.free()
	reference.free()
	print("PARKING_PREFAB_PASS: shared geometry, face-only override, stable identities")
	quit()


## Pack and save only the artwork variant, retaining its inherited linked scene.
func _roundtrip() -> void:
	var packed := ResourceLoader.load(
		PARKING_PREFAB,
		"PackedScene",
		ResourceLoader.CACHE_MODE_REPLACE,
	)
	assert(packed != null)
	var instance := (packed as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, PARKING_PREFAB) == OK)
	instance.free()
