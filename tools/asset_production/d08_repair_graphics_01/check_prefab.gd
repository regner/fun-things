extends "res://tools/asset_production/d06_commercial_graphics_04/check_prefab.gd"
## Audit only the two repair faces using the accepted wall-panel hierarchy/slot checks.

const REPAIR_ID := "d08_repair_graphics_01"
const REPAIR_VARIANTS := ["fixed_enough", "fixed_enough_patched"]
const REPAIR_RECEIPT := "C:/tmp/ft/assets/d08_repair_graphics_01/prefab.json"


## Normalize owned appearances and prove two byte-stable save/reload cycles per variant.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var receipts: Array[Dictionary] = []
	for variant: String in REPAIR_VARIANTS:
		receipts.append(_check_repair(variant, normalize))

	var file := FileAccess.open(REPAIR_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify({
		"engine": Engine.get_version_info().string,
		"variants": receipts,
		"status": "PASS",
	}, "\t") + "\n")
	file.close()
	print("REPAIR_PREFABS_PASS: inherited hardware, front-only overrides, mipmaps, stable UIDs")
	quit()


## Keep inherited mesh resources, transforms, face slots and decoration-only behavior intact.
func _check_repair(variant: String, normalize: bool) -> Dictionary:
	var suffix := "" if variant == "fixed_enough" else "_patched"
	var prefab := "res://scenes/prefabs/environment/%s%s.tscn" % [REPAIR_ID, suffix]
	var material_path := "res://art/materials/environment/%s/%s.tres" % [REPAIR_ID, variant]
	var material := load(material_path) as StandardMaterial3D
	_check_material(material, variant)
	if normalize:
		_normalize_repair(prefab, material_path, material)

	var instance := (load(prefab) as PackedScene).instantiate()
	var reference := (load(WALL_PREFAB) as PackedScene).instantiate()
	_compare_hierarchy(instance, reference)
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(instance.transform == Transform3D.IDENTITY)
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == WALL_MODEL)
	assert(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var receipt := _inspect_model(model, reference.get_node("Visuals/Model"), material)
	receipt.merge({
		"prefab": prefab, "material": material_path, "texture_size": [1220, 820],
		"linked_model": WALL_MODEL, "base_prefab": WALL_PREFAB,
		"identity_transforms": true, "hierarchy_and_mesh_resources_unchanged": true,
		"imported_mipmaps": true, "no_collision": true,
		"byte_stable_scene_material_roundtrips": 2 if normalize else 0,
		"prefab_sha256": FileAccess.get_sha256(prefab),
		"material_sha256": FileAccess.get_sha256(material_path),
	})
	instance.free()
	reference.free()
	return receipt


## Compare complete serialized files, including imported identities and dependency UIDs.
func _normalize_repair(prefab: String, material_path: String, material: Material) -> void:
	assert(Engine.is_editor_hint(), "UID-preserving saves require --editor")
	assert(ResourceSaver.save(material, material_path) == OK)
	_roundtrip(prefab)
	var baseline := FileAccess.get_file_as_bytes(prefab)
	var material_bytes := FileAccess.get_file_as_bytes(material_path)
	for cycle: int in range(2):
		_roundtrip(prefab)
		assert(baseline == FileAccess.get_file_as_bytes(prefab), "Scene IDs/UIDs changed")
		assert(ResourceSaver.save(material, material_path) == OK)
		assert(material_bytes == FileAccess.get_file_as_bytes(material_path))


## Verify the non-emissive sun-faded paint uses opaque clamped UV0 with real mipmaps.
func _check_material(material: StandardMaterial3D, variant: String) -> void:
	var texture := "res://art/textures/environment/%s/%s_albedo.png" % [REPAIR_ID, variant]
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.resource_path == texture)
	assert(material.albedo_texture.get_size() == Vector2(1220, 820))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE and is_equal_approx(material.roughness, 0.82))
	assert(is_zero_approx(material.metallic))
	assert(material.uv1_scale == Vector3.ONE and material.uv1_offset == Vector3.ZERO)
