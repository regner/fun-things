extends "res://tools/asset_production/d08_repair_graphics_02/check_prefab.gd"
## Reuse the shared low-panel hierarchy, face-slot, collision and query assertions.

const DIRECTORY_PREFAB := "res://scenes/prefabs/environment/d04_corporate_graphics_02.tscn"
const DIRECTORY_MATERIAL := (
	"res://art/materials/environment/d04_corporate_graphics_02/directory.tres"
)
const DIRECTORY_TEXTURE := (
	"res://art/textures/environment/d04_corporate_graphics_02/directory_albedo.png"
)
const DIRECTORY_SCRATCH := "C:/tmp/ft/assets/d04_corporate_graphics_02/"


## Bound assertion failures without writing a false successful receipt.
func _initialize() -> void:
	create_timer(CHECK_DEADLINE_SECONDS).timeout.connect(_directory_deadline)
	_run.call_deferred()


## Fail closed if an assertion aborts the deferred check.
func _directory_deadline() -> void:
	push_error("Directory artwork checks did not complete")
	quit(1)


## Save only this artwork variant and verify its unchanged hardware and collision.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var material := load(DIRECTORY_MATERIAL) as StandardMaterial3D
	_check_material(material, "directory")
	if normalize:
		_normalize_repair(DIRECTORY_PREFAB, DIRECTORY_MATERIAL, material)

	var instance := (load(DIRECTORY_PREFAB) as PackedScene).instantiate()
	var reference := (load(LOW_PREFAB) as PackedScene).instantiate()
	_compare_hierarchy(instance, reference)
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(instance.transform == Transform3D.IDENTITY)
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == LOW_MODEL)
	_check_collision(instance, reference)
	var receipt := _inspect_model(model, reference.get_node("Visuals/Model"), material)
	root.add_child(instance)
	await physics_frame
	await physics_frame
	assert(_check_queries(instance))
	receipt.merge({
		"status": "PASS", "engine": Engine.get_version_info().string,
		"base_prefab": LOW_PREFAB, "linked_model": LOW_MODEL,
		"hierarchy_mesh_resources_and_collision_unchanged": true,
		"identity_transforms": true, "texture_size": [1440, 390], "imported_mipmaps": true,
		"ray_queries": { "center_blocked": true, "side_clear": true, "overhead_clear": true },
		"byte_stable_scene_material_roundtrips": 2 if normalize else 0,
		"prefab_sha256": FileAccess.get_sha256(DIRECTORY_PREFAB),
		"material_sha256": FileAccess.get_sha256(DIRECTORY_MATERIAL),
		"prefab_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(DIRECTORY_PREFAB)),
		"material_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(DIRECTORY_MATERIAL)),
		"model_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(LOW_MODEL)),
	})
	var filename := "normalization.json" if normalize else "prefab.json"
	var file := FileAccess.open(DIRECTORY_SCRATCH + filename, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	instance.free()
	reference.free()
	print("DIRECTORY_PREFAB_PASS: face-only override, inherited box, rays, mipmaps, stable UIDs")
	quit()


## Require family-matched opaque, clamped artwork with white multiplication and no emission.
func _check_material(material: StandardMaterial3D, _variant: String) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.resource_path == DIRECTORY_TEXTURE)
	assert(material.albedo_texture.get_size() == Vector2(1440, 390))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE and is_equal_approx(material.roughness, 0.56))
	assert(is_zero_approx(material.metallic))
	assert(material.uv1_scale == Vector3.ONE and material.uv1_offset == Vector3.ZERO)
