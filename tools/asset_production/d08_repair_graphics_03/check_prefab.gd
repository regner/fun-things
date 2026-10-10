extends "res://tools/asset_production/d08_repair_graphics_01/check_prefab.gd"
## Audit service-warning faces with the family's existing wall-panel and stable-save helpers.

const WARNING_ID := "d08_repair_graphics_03"
const WARNING_VARIANTS := ["service_warning", "service_warning_patched"]
const WARNING_RECEIPT := "C:/tmp/ft/assets/d08_repair_graphics_03/prefab.json"


## Check only this record's appearances and optionally normalize their owned resources.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var receipts: Array[Dictionary] = []
	for variant: String in WARNING_VARIANTS:
		receipts.append(_check_warning(variant, normalize))

	var file := FileAccess.open(WARNING_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify({
		"engine": Engine.get_version_info().string,
		"variants": receipts,
		"status": "PASS",
	}, "\t") + "\n")
	file.close()
	print("WARNING_PREFABS_PASS: unchanged carrier, front-only overrides, mipmaps, stable UIDs")
	quit()


## Retain the base hierarchy, linked mesh resources, metre bounds and wall-only mounting.
func _check_warning(variant: String, normalize: bool) -> Dictionary:
	var suffix := "" if variant == "service_warning" else "_patched"
	var prefab := "res://scenes/prefabs/environment/%s%s.tscn" % [WARNING_ID, suffix]
	var material_path := "res://art/materials/environment/%s/%s.tres" % [WARNING_ID, variant]
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


## Require family paint values, opaque clamped UV0 and real imported mipmaps, never emission.
func _check_material(material: StandardMaterial3D, variant: String) -> void:
	var texture := "res://art/textures/environment/%s/%s_albedo.png" % [WARNING_ID, variant]
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
