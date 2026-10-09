extends "res://tools/asset_production/d06_commercial_graphics_01/check_prefab.gd"
## Reuse the family geometry audit while checking three separately saved face overrides.

const VARIANTS := ["loose_change", "second_helping", "side_b"]
const OUTPUT_RECEIPT := "C:/tmp/ft/assets/d06_commercial_graphics_02/prefab.json"

var _current_material: String


## Check each owned variant; never normalize or modify the inherited hall resources.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var variants: Array[Dictionary] = []
	for variant: String in VARIANTS:
		variants.append(_check_variant(variant, normalize))

	var file := FileAccess.open(OUTPUT_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify({
		"engine": Engine.get_version_info().string,
		"variants": variants,
		"status": "PASS",
	}, "\t") + "\n")
	file.close()
	print("SHOP_FASCIA_PREFABS_PASS: three linked face-only variants, bounds, dependencies")
	quit()


## Inspect one material and linked prefab, optionally proving two byte-stable saves.
func _check_variant(variant: String, normalize: bool) -> Dictionary:
	var prefab := "res://scenes/prefabs/environment/d06_commercial_graphics_02_%s.tscn" % variant
	_current_material = (
		"res://art/materials/environment/d06_commercial_graphics_02/%s.tres" % variant
	)
	var material := load(_current_material) as StandardMaterial3D
	_check_material(material)
	assert(material.albedo_texture.resource_path == (
		"res://art/textures/environment/d06_commercial_graphics_02/%s_albedo.png" % variant
	))
	if normalize:
		assert(Engine.is_editor_hint(), "Use --editor for UID-preserving saves")
		assert(ResourceSaver.save(material, _current_material) == OK)
		_roundtrip_variant(prefab)
		var first := FileAccess.get_file_as_bytes(prefab)
		_roundtrip_variant(prefab)
		assert(first == FileAccess.get_file_as_bytes(prefab), "Scene IDs changed on resave")

	var instance := (load(prefab) as PackedScene).instantiate()
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == MODEL)
	assert(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var receipt := _inspect_model(model)
	receipt.merge({
		"prefab": prefab,
		"material": _current_material,
		"texture_size": [2000, 400],
		"identity_model_transform": true,
		"imported_mesh_resources_unchanged": true,
		"no_collision": true,
		"second_roundtrip_byte_identical": normalize,
	})
	instance.free()
	return receipt


## Keep all imported resources untouched except the current tenant's front surface.
func _check_mesh(mesh: MeshInstance3D, original: MeshInstance3D) -> int:
	assert(mesh.transform == Transform3D.IDENTITY)
	assert(mesh.mesh == original.mesh, "Geometry must remain the imported resource")
	assert(mesh.material_override == null)
	var overrides := 0
	for surface: int in range(mesh.mesh.get_surface_count()):
		var override := mesh.get_surface_override_material(surface)
		if override != null:
			overrides += 1
			assert(mesh.name == "fascia_artwork_carrier" and surface == 0)
			assert(mesh.mesh.surface_get_material(surface).resource_name == "fascia_artwork_face")
			assert(override.resource_path == _current_material)
	return overrides


## Pack and resave only the passed owned variant, preserving the linked imported child.
func _roundtrip_variant(prefab: String) -> void:
	var packed := ResourceLoader.load(prefab, "PackedScene", ResourceLoader.CACHE_MODE_REPLACE)
	assert(packed != null)
	var instance := (packed as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, prefab) == OK)
	instance.free()
