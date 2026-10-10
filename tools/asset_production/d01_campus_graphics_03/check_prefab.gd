extends "res://tools/asset_production/d01_campus_graphics_02/check_prefab.gd"
## Check all three route faces using the existing low-panel geometry/collision assertions.

const ROUTE_DIRECTORY := "res://art/materials/environment/d01_campus_graphics_03/"
const ROUTE_TEXTURES := "res://art/textures/environment/d01_campus_graphics_03/"
const ROUTE_PREFAB := "res://scenes/prefabs/environment/d01_campus_graphics_03"
const ROUTE_RECEIPT := "C:/tmp/ft/assets/d01_campus_graphics_03/prefab.json"


## Check each independently saved variant and collect its real resource roundtrip evidence.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var variants: Array[Dictionary] = []
	for variant: String in ["left", "ahead", "right"]:
		variants.append(_check_route(variant, normalize))
	var file := FileAccess.open(ROUTE_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify({
		"status": "PASS", "engine": Engine.get_version_info().string,
		"variants": variants, "stable_roundtrips": 2 if normalize else 0,
	}, "\t") + "\n")
	file.close()
	print("ROUTE_SET_PREFAB_PASS: three face-only variants, unchanged linked hardware/collision")
	quit()


## Verify a variant against the accepted support, retaining all original hierarchy and meshes.
func _check_route(variant: String, normalize: bool) -> Dictionary:
	var suffix := "" if variant == "ahead" else "_" + variant
	var prefab_path := ROUTE_PREFAB + suffix + ".tscn"
	var material_path := ROUTE_DIRECTORY + "route_" + variant + ".tres"
	var material := load(material_path) as StandardMaterial3D
	_check_material(material, variant)
	var receipt := _save_route(prefab_path, material_path, variant) if normalize else {}
	if not normalize:
		for dependency: String in [
			prefab_path, material_path, ROUTE_TEXTURES + "route_" + variant + "_albedo.png",
			BOARD_MODEL, BOARD_PREFAB,
		]:
			var uid := ResourceLoader.get_resource_uid(dependency)
			assert(ResourceUID.has_id(uid) and ResourceUID.get_id_path(uid) == dependency)
	var instance := (load(prefab_path) as PackedScene).instantiate()
	var reference := (load(BOARD_PREFAB) as PackedScene).instantiate()
	_compare_hierarchy(instance, reference)
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(instance.transform == Transform3D.IDENTITY)
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == BOARD_MODEL)
	receipt.merge(_inspect_model(model, reference.get_node("Visuals/Model"), material))
	_check_collision(instance, reference)
	receipt.merge({
		"variant": variant, "prefab": prefab_path, "material": material_path,
		"prefab_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(prefab_path)),
		"material_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(material_path)),
		"identity_transforms": true, "hierarchy_and_imported_meshes_unchanged": true,
		"inherited_collision_unchanged": true, "texture_size": [1440, 390],
	})
	instance.free()
	reference.free()
	return receipt


## Normalize once then reload and save twice, requiring stable bytes and serialized identities.
func _save_route(prefab_path: String, material_path: String, variant: String) -> Dictionary:
	assert(Engine.is_editor_hint(), "UID-preserving saves require --editor")
	var hashes: Array[String] = []
	var material_hashes: Array[String] = []
	for cycle: int in range(3):
		var material := ResourceLoader.load(
			material_path, "StandardMaterial3D", ResourceLoader.CACHE_MODE_REPLACE
		) as StandardMaterial3D
		_check_material(material, variant)
		assert(ResourceSaver.save(material, material_path) == OK)
		_roundtrip(prefab_path)
		hashes.append(FileAccess.get_sha256(prefab_path))
		material_hashes.append(FileAccess.get_sha256(material_path))
		assert(hashes[0] == hashes[cycle], "Scene identity drift")
		assert(material_hashes[0] == material_hashes[cycle], "Material identity drift")
	return { "roundtrip_sha256": hashes, "material_roundtrip_sha256": material_hashes }


## Require the correct opaque clamped mipmapped texture, never whole-mesh or UV overrides.
func _check_material(material: StandardMaterial3D, variant: String) -> void:
	assert(material != null and material.albedo_texture != null)
	var texture_path := ROUTE_TEXTURES + "route_" + variant + "_albedo.png"
	assert(material.albedo_texture.resource_path == texture_path)
	assert(material.albedo_texture.get_size() == Vector2(1440, 390))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE and is_equal_approx(material.roughness, 0.65))
	assert(material.uv1_scale == Vector3.ONE and material.uv1_offset == Vector3.ZERO)
