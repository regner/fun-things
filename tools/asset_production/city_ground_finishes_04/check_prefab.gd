extends SceneTree
## Check the imported material/swatch, save stable IDs, and probe its continuous top datum.

const PREFAB := "res://scenes/prefabs/environment/city_ground_finishes_04.tscn"
const MODEL := "res://art/models/environment/city_ground_finishes_04/city_ground_finishes_04.glb"
const MATERIAL := "res://art/materials/environment/city_ground_finishes_04/short_grass.tres"
const RECEIPT := "C:/tmp/ft/assets/city_ground_finishes_04/prefab.json"
const EDITOR_SETTLE_SECONDS := 5.0

var _material_checked := false
var _physics_checked := false


## Defer checks until the resource loader and scene tree are initialized.
func _initialize() -> void:
	_run.call_deferred()


## Check the independent material contract, linked mesh, collider and save/reload stability.
func _run() -> void:
	if Engine.is_editor_hint():
		await create_timer(EDITOR_SETTLE_SECONDS).timeout
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame  # gdstyle:ignore=quality/await-in-loop

	var material := load(MATERIAL) as StandardMaterial3D
	_check_material(material)
	if not _material_checked:
		quit(1)
		return

	var normalize := OS.get_cmdline_user_args().has("--normalize")
	if normalize and not _normalize(material):
		quit(1)
		return

	var instance := (load(PREFAB) as PackedScene).instantiate()
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == MODEL)
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	assert(meshes.size() == 1)
	var mesh := meshes[0] as MeshInstance3D
	assert(mesh.transform == Transform3D.IDENTITY)
	assert(mesh.mesh.get_surface_count() == 1 and mesh.material_override == null)
	assert(mesh.mesh.surface_get_material(0) == material, "External import remap missing")
	assert(mesh.get_aabb().position.is_equal_approx(Vector3(-2, -0.08, -2)))
	assert(mesh.get_aabb().size.is_equal_approx(Vector3(4, 0.08, 4)))
	var shape := instance.get_node("Collision/SwatchBody/Shape") as CollisionShape3D
	assert((shape.shape as BoxShape3D).size.is_equal_approx(Vector3(4, 0.08, 4)))
	assert(shape.position.is_equal_approx(Vector3(0, -0.04, 0)))
	root.add_child(instance)
	await physics_frame
	await physics_frame
	_check_physics(instance)
	if not _physics_checked:
		quit(1)
		return

	_write_receipt(normalize)
	instance.free()
	print("GRASS_PREFAB_PASS: linked mesh, external material, stable scene, floor datum")
	quit()


## Write a bounded receipt; callers must also reject any diagnostics in the engine log.
func _write_receipt(normalize: bool) -> void:
	var receipt := {
		"status": "PASS",
		"engine": Engine.get_version_info().string,
		"identity_linked_model": MODEL,
		"external_material": MATERIAL,
		"mesh_count": 1,
		"surface_count": 1,
		"aabb_min": [-2, -0.08, -2],
		"aabb_max": [2, 0, 2],
		"texture_size": [512, 512],
		"texture_mipmaps": true,
		"uv_unit_metres": 4,
		"floor_ray_hits": 5,
		"outside_ray_clear": true,
		"normalization_requested": normalize,
		"second_roundtrip_byte_identical": normalize,
	}
	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()


## Keep the portable material opaque, repeating, mipmapped, matte and displacement-free.
func _check_material(material: StandardMaterial3D) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.get_size() == Vector2(512, 512))
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(material.texture_repeat and material.albedo_color == Color.WHITE)
	assert(material.uv1_scale == Vector3.ONE)
	assert(is_equal_approx(material.roughness, 0.96) and material.metallic == 0.0)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(not material.emission_enabled and not material.normal_enabled)
	assert(not material.heightmap_enabled)
	var settings := ConfigFile.new()
	assert(settings.load(material.albedo_texture.resource_path + ".import") == OK)
	assert(settings.get_value("params", "mipmaps/generate") == true)
	_material_checked = true


## Probe the one continuous sample collider, not production actor movement or road collision.
func _check_physics(instance: Node3D) -> void:
	var space := instance.get_world_3d().direct_space_state
	for point: Vector2 in [Vector2.ZERO, Vector2(-1.9, -1.9), Vector2(1.9, -1.9),
			Vector2(-1.9, 1.9), Vector2(1.9, 1.9)]:
		var query := PhysicsRayQueryParameters3D.create(
			Vector3(point.x, 1, point.y), Vector3(point.x, -1, point.y), 1)
		var hit := space.intersect_ray(query)
		assert(not hit.is_empty() and absf(hit.position.y) < 0.0001)
		assert(hit.normal.is_equal_approx(Vector3.UP))
	var outside := PhysicsRayQueryParameters3D.create(Vector3(3, 1, 0), Vector3(3, -1, 0), 1)
	assert(space.intersect_ray(outside).is_empty())
	_physics_checked = true


## Resave the material and require two complete, byte-stable wrapper roundtrips.
func _normalize(material: StandardMaterial3D) -> bool:
	assert(Engine.is_editor_hint(), "Normalize through the headless editor")
	assert(ResourceSaver.save(material, MATERIAL) == OK)
	if not _roundtrip():
		return false

	var first := FileAccess.get_file_as_bytes(PREFAB)
	if not _roundtrip():
		return false

	assert(first == FileAccess.get_file_as_bytes(PREFAB), "Scene IDs changed on resave")
	return true


## Normalize only this new wrapper while preserving the imported, noneditable model instance.
func _roundtrip() -> bool:
	var packed := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_REPLACE)
	assert(packed != null)
	var instance := (packed as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, PREFAB) == OK)
	instance.free()
	return true
