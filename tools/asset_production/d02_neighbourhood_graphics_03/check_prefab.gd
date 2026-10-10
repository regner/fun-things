extends "res://tools/asset_production/d02_neighbourhood_graphics_01/check_prefab.gd"
## Verify face-only artwork on the unchanged fascia, preserving saved identities.

const CORNER_BASE := "res://scenes/prefabs/environment/city_shop_fittings_02.tscn"
const CORNER_MODEL := (
	"res://art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb"
)
const CORNER_NID := "d02_neighbourhood_graphics_03"
const CORNER_PREFAB := "res://scenes/prefabs/environment/" + CORNER_NID + ".tscn"
const CORNER_MATERIAL := "res://art/materials/environment/" + CORNER_NID + "/corner_cupboard.tres"
const CORNER_TEXTURE := (
	"res://art/textures/environment/" + CORNER_NID + "/corner_cupboard_albedo.png"
)
const CORNER_RECEIPT := "C:/tmp/ft/assets/" + CORNER_NID + "/prefab.json"


## Defer resource inspection until the tree has initialized.
func _initialize() -> void:
	_run.call_deferred()


## Check the actual dependency chain, optionally normalizing only owned resources.
func _run() -> void:
	var material := load(CORNER_MATERIAL) as StandardMaterial3D
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.resource_path == CORNER_TEXTURE)
	assert(material.albedo_texture.get_size() == Vector2(2000, 400))
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
		assert(ResourceSaver.save(material, CORNER_MATERIAL) == OK)
		_roundtrip()
		# Initial normalization establishes new IDs; the following two cycles must retain them.
		var initial := FileAccess.get_file_as_bytes(CORNER_PREFAB)
		for cycle: int in range(2):
			_roundtrip()
			assert(initial == FileAccess.get_file_as_bytes(CORNER_PREFAB), "Saved identity drift")
			roundtrips.append(FileAccess.get_sha256(CORNER_PREFAB))

	var instance := (load(CORNER_PREFAB) as PackedScene).instantiate()
	var reference := (load(CORNER_BASE) as PackedScene).instantiate()
	assert(instance.transform == Transform3D.IDENTITY)
	_compare_hierarchy(instance, reference)
	assert(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == CORNER_MODEL)
	var result := _inspect_model(model, reference.get_node("Visuals/Model"), material)
	result.merge({
		"status": "PASS", "engine": Engine.get_version_info().string,
		"prefab": CORNER_PREFAB, "prefab_sha256": FileAccess.get_sha256(CORNER_PREFAB),
		"two_stable_roundtrip_sha256": roundtrips,
		"mipmaps_present": true, "texture_dimensions": [2000, 400],
		"identity_model_transform": true, "hierarchy_and_geometry_unchanged": true,
		"collision": "None; mounted decorative face inherits facade-owned blocking",
	})
	var file := FileAccess.open(CORNER_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(result, "\t") + "\n")
	file.close()
	instance.free()
	reference.free()
	print("CORNER_PREFAB_PASS: shared geometry, face-only override, stable identities")
	quit()


## Check every surface and measured bounds, allowing only fascia_artwork_face to be replaced.
func _inspect_model(model: Node3D, reference: Node, material: Material) -> Dictionary:
	var meshes := 0
	var surfaces := 0
	var overrides := 0
	var bounds := AABB()
	for child: Node in model.get_node("city_shop_fittings_02").get_children():
		assert(child is MeshInstance3D)
		var mesh := child as MeshInstance3D
		var original := reference.get_node(NodePath("city_shop_fittings_02/" + mesh.name))
		assert(mesh.mesh == (original as MeshInstance3D).mesh)
		assert(mesh.material_override == null)
		for surface: int in range(mesh.mesh.get_surface_count()):
			var override := mesh.get_surface_override_material(surface)
			if override != null:
				overrides += 1
				assert(mesh.name == "fascia_artwork_carrier" and surface == 0)
				var original_material := mesh.mesh.surface_get_material(surface)
				assert(original_material.resource_name == "fascia_artwork_face")
				assert(override == material)
		bounds = mesh.get_aabb() if meshes == 0 else bounds.merge(mesh.get_aabb())
		meshes += 1
		surfaces += mesh.mesh.get_surface_count()
	assert(meshes == 7 and surfaces == 8 and overrides == 1)
	assert(bounds.position.is_equal_approx(Vector3(-1.6, -0.4, -0.14)))
	assert(bounds.size.is_equal_approx(Vector3(3.2, 0.8, 0.14)))
	return {
		"meshes": meshes, "surfaces": surfaces, "face_only_overrides": overrides,
		"aabb_min": [-1.6, -0.4, -0.14], "aabb_max": [1.6, 0.4, 0],
	}


## Pack and save only the artwork variant, retaining its inherited linked scene.
func _roundtrip() -> void:
	var packed := ResourceLoader.load(
		CORNER_PREFAB,
		"PackedScene",
		ResourceLoader.CACHE_MODE_REPLACE,
	)
	assert(packed != null)
	var instance := (packed as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, CORNER_PREFAB) == OK)
	instance.free()
