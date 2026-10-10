extends "res://tools/asset_production/d08_repair_graphics_01/check_prefab.gd"
## Reuse hierarchy/roundtrip helpers, checking only this face on the unchanged fascia.

const WORDMARK_PREFAB := "res://scenes/prefabs/environment/d04_corporate_graphics_03.tscn"
const WORDMARK_MATERIAL := (
	"res://art/materials/environment/d04_corporate_graphics_03/entry_wordmark.tres"
)
const WORDMARK_TEXTURE := (
	"res://art/textures/environment/d04_corporate_graphics_03/entry_wordmark_albedo.png"
)
const FASCIA_PREFAB := "res://scenes/prefabs/environment/city_shop_fittings_02.tscn"
const FASCIA_MODEL := "res://art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb"
const WORDMARK_SCRATCH := "C:/tmp/ft/assets/d04_corporate_graphics_03/"
const CHECK_DEADLINE_SECONDS := 30.0


## Fail closed when an assertion aborts a deferred resource check.
func _initialize() -> void:
	create_timer(CHECK_DEADLINE_SECONDS).timeout.connect(_wordmark_deadline)
	_run.call_deferred()


## Bound checks without producing a false successful receipt after an assertion failure.
func _wordmark_deadline() -> void:
	push_error("Entry wordmark checks did not complete")
	quit(1)


## Save only this artwork, verifying linked resources and two stable identity roundtrips.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var material := load(WORDMARK_MATERIAL) as StandardMaterial3D
	_check_material(material, "entry_wordmark")
	if normalize:
		_normalize_repair(WORDMARK_PREFAB, WORDMARK_MATERIAL, material)

	var instance := (load(WORDMARK_PREFAB) as PackedScene).instantiate()
	var reference := (load(FASCIA_PREFAB) as PackedScene).instantiate()
	_compare_hierarchy(instance, reference)
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(instance.transform == Transform3D.IDENTITY)
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == FASCIA_MODEL)
	assert(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var receipt := _inspect_model(model, reference.get_node("Visuals/Model"), material)
	receipt.merge({
		"status": "PASS", "engine": Engine.get_version_info().string,
		"base_prefab": FASCIA_PREFAB, "linked_model": FASCIA_MODEL,
		"hierarchy_and_mesh_resources_unchanged": true, "no_collision": true,
		"identity_transforms": true, "texture_size": [2000, 400], "imported_mipmaps": true,
		"byte_stable_scene_material_roundtrips": 2 if normalize else 0,
		"prefab_sha256": FileAccess.get_sha256(WORDMARK_PREFAB),
		"material_sha256": FileAccess.get_sha256(WORDMARK_MATERIAL),
		"prefab_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(WORDMARK_PREFAB)),
		"material_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(WORDMARK_MATERIAL)),
		"model_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(FASCIA_MODEL)),
	})
	var filename := "normalization.json" if normalize else "prefab.json"
	var file := FileAccess.open(WORDMARK_SCRATCH + filename, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	instance.free()
	reference.free()
	print("WORDMARK_PREFAB_PASS: unchanged fascia, front-only override, mipmaps, stable UIDs")
	quit()


## Require the family-matched opaque clamped face without illumination or UV distortion.
func _check_material(material: StandardMaterial3D, _variant: String) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.resource_path == WORDMARK_TEXTURE)
	assert(material.albedo_texture.get_size() == Vector2(2000, 400))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE and is_equal_approx(material.roughness, 0.56))
	assert(is_zero_approx(material.metallic))
	assert(material.uv1_scale == Vector3.ONE and material.uv1_offset == Vector3.ZERO)


## Measure the actual linked fascia and reject mesh copies or any extra material override.
func _inspect_model(model: Node3D, reference: Node, material: Material) -> Dictionary:
	var shared_root := model.get_node("city_shop_fittings_02") as Node3D
	var meshes := 0
	var surfaces := 0
	var overrides := 0
	var bounds := AABB()
	for child: Node in shared_root.get_children():
		assert(child is MeshInstance3D)
		var mesh := child as MeshInstance3D
		var original := reference.get_node(NodePath("city_shop_fittings_02/" + mesh.name))
		assert(mesh.mesh == (original as MeshInstance3D).mesh)
		assert(mesh.material_override == null)
		overrides += _check_face(mesh, material)
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


## Permit only surface zero on the carrier, preserving frame, trim, back and side materials.
func _check_face(mesh: MeshInstance3D, material: Material) -> int:
	var overrides := 0
	for surface: int in range(mesh.mesh.get_surface_count()):
		var override := mesh.get_surface_override_material(surface)
		if override != null:
			overrides += 1
			assert(mesh.name == "fascia_artwork_carrier" and surface == 0)
			assert(mesh.mesh.surface_get_material(surface).resource_name == "fascia_artwork_face")
			assert(override == material)

	return overrides
