extends "res://tools/asset_production/d06_commercial_graphics_04/check_prefab.gd"
## Reuse the accepted wall-panel hierarchy/mesh audit for this parking face only.

const PARKING_PREFAB := "res://scenes/prefabs/environment/d07_retail_graphics_03.tscn"
const PARKING_MATERIAL := "res://art/materials/environment/d07_retail_graphics_03/parking_zone.tres"
const PARKING_TEXTURE := (
	"res://art/textures/environment/d07_retail_graphics_03/parking_zone_albedo.png"
)
const PARKING_RECEIPT := "C:/tmp/ft/assets/d07_retail_graphics_03/prefab.json"
# Existing hardware import quantizes UVs; tolerate <0.062 texel, not orientation drift.
const IMPORTED_UV_TOLERANCE := 0.00005


## Inspect the saved artwork and shared geometry; only --normalize saves owned resources.
func _run() -> void:
	var material := load(PARKING_MATERIAL) as StandardMaterial3D
	_check_material(material, "parking_zone")
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		_normalize_parking(material)

	var instance := (load(PARKING_PREFAB) as PackedScene).instantiate()
	var reference := (load(WALL_PREFAB) as PackedScene).instantiate()
	_compare_hierarchy(instance, reference)
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(instance.transform == Transform3D.IDENTITY)
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == WALL_MODEL)
	assert(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var receipt := _inspect_model(model, reference.get_node("Visuals/Model"), material)
	receipt["imported_uv_max_error"] = _check_parking_uv(model)
	receipt.merge({
		"engine": Engine.get_version_info().string,
		"prefab": PARKING_PREFAB, "base_prefab": WALL_PREFAB, "linked_model": WALL_MODEL,
		"identity_model_transform": true, "hierarchy_and_mesh_resources_unchanged": true,
		"no_collision": true, "texture_size": [1220, 820], "imported_mipmaps": true,
		"front_uv_vertices": 36, "two_roundtrips_byte_identical": normalize,
		"prefab_sha256": FileAccess.get_sha256(PARKING_PREFAB),
		"prefab_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(PARKING_PREFAB)),
		"status": "PASS",
	})
	var file := FileAccess.open(PARKING_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	instance.free()
	reference.free()
	print("PARKING_PREFAB_PASS: linked hardware, one face override, UVs, no collision")
	quit()


## Normalize once, then prove two further saves preserve every byte, identity and UID.
func _normalize_parking(material: StandardMaterial3D) -> void:
	assert(Engine.is_editor_hint(), "UID-preserving saves require --editor")
	assert(ResourceSaver.save(material, PARKING_MATERIAL) == OK)
	_roundtrip(PARKING_PREFAB)
	var first := FileAccess.get_file_as_bytes(PARKING_PREFAB)
	for pass_index: int in range(2):
		_roundtrip(PARKING_PREFAB)
		assert(first == FileAccess.get_file_as_bytes(PARKING_PREFAB),
			"Parking scene bytes/IDs changed on roundtrip %d" % pass_index)


## Require opaque clamped albedo with actual mipmaps and no illumination or UV correction.
func _check_material(material: StandardMaterial3D, _variant: String) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.resource_path == PARKING_TEXTURE)
	assert(material.albedo_texture.get_size() == Vector2(1220, 820))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE and is_equal_approx(material.roughness, 0.56))
	assert(is_zero_approx(material.metallic))
	assert(material.uv1_scale == Vector3.ONE and material.uv1_offset == Vector3.ZERO)


## Check the actual rounded face vertices so the parking P and zone read unmirrored.
func _check_parking_uv(model: Node3D) -> float:
	var mesh := model.get_node("CitySignSupports01/artwork_carrier") as MeshInstance3D
	var arrays := mesh.mesh.surface_get_arrays(0)
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
	assert(vertices.size() == 36 and uvs.size() == 36)
	var max_error := 0.0
	for index: int in range(vertices.size()):
		assert(absf(vertices[index].z + 0.088) < 0.000001)
		max_error = maxf(max_error, absf(uvs[index].x - (0.5 - vertices[index].x / 1.22)))
		max_error = maxf(max_error, absf(uvs[index].y - (0.5 - vertices[index].y / 0.82)))
	assert(max_error < IMPORTED_UV_TOLERANCE)
	return max_error
