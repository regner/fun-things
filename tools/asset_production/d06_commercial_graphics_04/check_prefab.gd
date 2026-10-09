extends "res://tools/asset_production/d06_commercial_graphics_03/check_prefab.gd"
## Reuse family hierarchy/roundtrip helpers; audit only the rightward passage panel.

const PASSAGE_PREFAB := "res://scenes/prefabs/environment/d06_commercial_graphics_04.tscn"
const PASSAGE_MATERIAL := "res://art/materials/environment/d06_commercial_graphics_04/passage.tres"
const PASSAGE_TEXTURE := (
	"res://art/textures/environment/d06_commercial_graphics_04/passage_albedo.png"
)
const WALL_PREFAB := "res://scenes/prefabs/environment/city_sign_supports_01.tscn"
const WALL_MODEL := "res://art/models/environment/city_sign_supports_01/city_sign_supports_01.glb"
const PASSAGE_RECEIPT := "C:/tmp/ft/assets/d06_commercial_graphics_04/prefab.json"


## Check one passage face, saving only its own resources when explicitly requested.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var material := load(PASSAGE_MATERIAL) as StandardMaterial3D
	_check_material(material, "passage")
	if normalize:
		assert(Engine.is_editor_hint(), "UID-preserving saves require --editor")
		assert(ResourceSaver.save(material, PASSAGE_MATERIAL) == OK)
		_roundtrip(PASSAGE_PREFAB)
		var first := FileAccess.get_file_as_bytes(PASSAGE_PREFAB)
		_roundtrip(PASSAGE_PREFAB)
		assert(first == FileAccess.get_file_as_bytes(PASSAGE_PREFAB), "Scene IDs changed on resave")

	var instance := (load(PASSAGE_PREFAB) as PackedScene).instantiate()
	var reference := (load(WALL_PREFAB) as PackedScene).instantiate()
	_compare_hierarchy(instance, reference)
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(instance.transform == Transform3D.IDENTITY)
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == WALL_MODEL)
	assert(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var receipt := _inspect_model(model, reference.get_node("Visuals/Model"), material)
	receipt.merge({
		"engine": Engine.get_version_info().string,
		"prefab": PASSAGE_PREFAB, "base_prefab": WALL_PREFAB, "linked_model": WALL_MODEL,
		"identity_model_transform": true, "hierarchy_and_mesh_resources_unchanged": true,
		"no_collision": true, "texture_size": [1220, 820], "imported_mipmaps": true,
		"second_roundtrip_byte_identical": normalize, "status": "PASS",
	})
	var file := FileAccess.open(PASSAGE_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	instance.free()
	reference.free()
	print("PASSAGE_PREFAB_PASS: linked meshes, face-only override, inherited bounds, dependencies")
	quit()


## Require opaque clamped albedo with real imported mipmaps, not emission or mirrored UVs.
func _check_material(material: StandardMaterial3D, _variant: String) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.resource_path == PASSAGE_TEXTURE)
	assert(material.albedo_texture.get_size() == Vector2(1220, 820))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE and is_equal_approx(material.roughness, 0.56))
	assert(material.uv1_scale == Vector3.ONE and material.uv1_offset == Vector3.ZERO)


## Check all imported surfaces, accepting only the named front-face slot override.
func _inspect_model(model: Node3D, reference: Node, material: Material) -> Dictionary:
	var root := model.get_node("CitySignSupports01") as Node3D
	var meshes := 0
	var surfaces := 0
	var overrides := 0
	var bounds := AABB()
	for child: Node in root.get_children():
		assert(child is MeshInstance3D)
		var mesh := child as MeshInstance3D
		var original := reference.get_node(NodePath("CitySignSupports01/" + mesh.name))
		assert(mesh.mesh == (original as MeshInstance3D).mesh)
		assert(mesh.material_override == null)
		overrides += _check_face(mesh, material)
		bounds = mesh.get_aabb() if meshes == 0 else bounds.merge(mesh.get_aabb())
		meshes += 1
		surfaces += mesh.mesh.get_surface_count()
	assert(meshes == 12 and surfaces == 13 and overrides == 1)
	assert(bounds.position.is_equal_approx(Vector3(-0.7, -0.5, -0.1)))
	assert(bounds.size.is_equal_approx(Vector3(1.4, 1.0, 0.1)))
	return {
		"meshes": meshes, "surfaces": surfaces, "face_only_overrides": overrides,
		"aabb_min": [-0.7, -0.5, -0.1], "aabb_max": [0.7, 0.5, 0],
	}


## Preserve all hardware materials, including carrier sides and rear.
func _check_face(mesh: MeshInstance3D, material: Material) -> int:
	var overrides := 0
	for surface: int in range(mesh.mesh.get_surface_count()):
		var override := mesh.get_surface_override_material(surface)
		if override != null:
			overrides += 1
			assert(mesh.name == "artwork_carrier" and surface == 0)
			assert(mesh.mesh.surface_get_material(surface).resource_name == "sign_face")
			assert(override == material)
	return overrides
