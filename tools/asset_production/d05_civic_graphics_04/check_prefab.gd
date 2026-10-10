extends "res://tools/asset_production/d05_civic_graphics_01/check_prefab.gd"
## Reuse the hall's geometry/material/roundtrip checks for three inherited shop fascias.

const SHOP_VARIANTS := ["tide_tea", "quay_pantry", "hem_repairs"]
const SHOP_BASE := "res://scenes/prefabs/environment/city_shop_fittings_02.tscn"
const SHOP_RECEIPT := "C:/tmp/ft/assets/d05_civic_graphics_04/prefab.json"
const SHOP_MATERIAL_DIR := "res://art/materials/environment/d05_civic_graphics_04/"
const SHOP_TEXTURE_DIR := "res://art/textures/environment/d05_civic_graphics_04/"
const SHOP_PREFAB_PREFIX := "res://scenes/prefabs/environment/d05_civic_graphics_04_"

var _current_material: String


## Inspect every saved variant, keeping the inherited startup and shared geometry audit.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var receipt := { "engine": Engine.get_version_info().string, "variants": {}, "status": "PASS" }
	for variant: String in SHOP_VARIANTS:
		receipt["variants"][variant] = _check_variant(variant, normalize)

	var file := FileAccess.open(SHOP_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	print("SHOPS_PREFAB_PASS: three face-only variants, unchanged geometry and stable IDs")
	quit()


## Check inherited identity, UV orientation, materials and all five dependency UIDs.
func _check_variant(variant: String, normalize: bool) -> Dictionary:
	_current_material = SHOP_MATERIAL_DIR + variant + ".tres"
	var path := SHOP_PREFAB_PREFIX + variant + ".tscn"
	var texture_path := SHOP_TEXTURE_DIR + variant + "_albedo.png"
	var material := load(_current_material) as StandardMaterial3D
	_check_material(material)
	assert(is_equal_approx(material.roughness, 0.56) and is_zero_approx(material.metallic))
	assert(material.albedo_texture.resource_path == texture_path)
	var hashes := _normalize_shop(path, material) if normalize else []
	var instance := (load(path) as PackedScene).instantiate()
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == MODEL)
	assert(instance.transform == Transform3D.IDENTITY)
	assert(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var result := _inspect_model(model)
	result["imported_uv"] = _check_uv(model)
	result["prefab"] = path
	result["prefab_sha256"] = FileAccess.get_sha256(path)
	result["no_collision"] = true
	result["resource_uids"] = _shop_uids([path, SHOP_BASE, MODEL, _current_material, texture_path])
	result["texture_size"] = [2000, 400]
	result["filter"] = "linear_mipmap"
	result["repeat"] = false
	result["emission"] = false
	if normalize:
		result["roundtrip_sha256"] = hashes

	instance.free()
	return result


## Normalize new resources once, then prove two full save/reload byte-stable cycles.
func _normalize_shop(path: String, material: StandardMaterial3D) -> Array:
	assert(Engine.is_editor_hint())
	assert(ResourceSaver.save(material, _current_material) == OK)
	_roundtrip(path)
	var baseline := FileAccess.get_file_as_bytes(path)
	var hashes := [FileAccess.get_sha256(path)]
	for cycle: int in range(2):
		_roundtrip(path)
		assert(baseline == FileAccess.get_file_as_bytes(path), "Scene IDs changed")
		hashes.append(FileAccess.get_sha256(path))

	return hashes


## Require exactly the intended tenant material on face slot zero and no hardware overrides.
func _check_mesh(mesh: MeshInstance3D, original: MeshInstance3D) -> int:
	assert(mesh.transform == original.transform and mesh.transform == Transform3D.IDENTITY)
	assert(mesh.mesh == original.mesh and mesh.material_override == null)
	var overrides := 0
	for surface: int in range(mesh.mesh.get_surface_count()):
		var override := mesh.get_surface_override_material(surface)
		if override != null:
			overrides += 1
			assert(mesh.name == "fascia_artwork_carrier" and surface == 0)
			assert(mesh.mesh.surface_get_material(surface).resource_name == "fascia_artwork_face")
			assert(override.resource_path == _current_material)

	return overrides


## Independently verify imported artwork coordinates remain upright and unmirrored.
func _check_uv(model: Node3D) -> Dictionary:
	var mesh := model.get_node("city_shop_fittings_02/fascia_artwork_carrier") as MeshInstance3D
	var arrays := mesh.mesh.surface_get_arrays(0)
	var positions: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var uv: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
	var max_error := 0.0
	for index: int in range(positions.size()):
		var point := positions[index]
		assert(absf(point.z + 0.128) < 0.00001)
		var expected := Vector2((1.5 - point.x) / 3.0, (0.3 - point.y) / 0.6)
		max_error = maxf(max_error, uv[index].distance_to(expected))

	assert(positions.size() == 28 and max_error < 0.00005)
	return { "face_vertices": positions.size(), "maximum_uv_error": max_error }


## Resolve saved identities after import; editor saves defer registry resolution to runtime.
func _shop_uids(paths: Array) -> Dictionary:
	var result := {}
	for path: String in paths:
		var resource_uid := ResourceLoader.get_resource_uid(path)
		assert(resource_uid != ResourceUID.INVALID_ID)
		if not Engine.is_editor_hint():
			assert(ResourceUID.has_id(resource_uid))
			assert(ResourceUID.get_id_path(resource_uid) == path)

		result[path] = ResourceUID.id_to_text(resource_uid)
	return result
