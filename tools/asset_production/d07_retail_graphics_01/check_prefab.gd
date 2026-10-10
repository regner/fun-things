extends SceneTree
## Inspect the saved artwork-only override; --normalize also resaves owned resources.

const PREFAB := "res://scenes/prefabs/environment/d07_retail_graphics_01.tscn"
const MATERIAL := "res://art/materials/environment/d07_retail_graphics_01/retail_fascia.tres"
const MODEL := "res://art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb"
const RECEIPT := "C:/tmp/ft/assets/d07_retail_graphics_01/prefab.json"


## Defer validation until the scene tree has completed startup.
func _initialize() -> void:
	_run.call_deferred()


## Check dependencies and linked geometry, optionally normalizing only owned resources.
func _run() -> void:
	var material := load(MATERIAL) as StandardMaterial3D
	_check_material(material)
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		assert(Engine.is_editor_hint(), "Use --editor for UID-preserving resource saves")
		assert(ResourceSaver.save(material, MATERIAL) == OK)
		_roundtrip()
		var first := FileAccess.get_file_as_bytes(PREFAB)
		_roundtrip()
		assert(first == FileAccess.get_file_as_bytes(PREFAB), "Scene IDs changed on resave")
		_roundtrip()
		assert(first == FileAccess.get_file_as_bytes(PREFAB), "Second roundtrip changed IDs")

	var instance := (load(PREFAB) as PackedScene).instantiate()
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.transform == Transform3D.IDENTITY)
	assert(model.scene_file_path == MODEL)
	assert(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var receipt := _inspect_model(model)
	receipt.merge({
		"engine": Engine.get_version_info().string,
		"prefab": PREFAB,
		"linked_model": MODEL,
		"identity_model_transform": true,
		"imported_mesh_resources_unchanged": true,
		"no_collision": true,
		"texture_size": [2000, 400],
		"filter": "linear_mipmap",
		"repeat": false,
		"status": "PASS",
	})
	if normalize:
		receipt["two_roundtrips_byte_identical"] = true
		receipt["prefab_sha256"] = FileAccess.get_sha256(PREFAB)
		receipt["prefab_uid"] = ResourceUID.id_to_text(ResourceLoader.get_resource_uid(PREFAB))

	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	instance.free()
	print("RETAIL_PREFAB_PASS: linked meshes, face-only override, bounds, dependencies")
	quit()


## Require a clamped opaque albedo with no hidden illumination or texture multiplier.
func _check_material(material: StandardMaterial3D) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE)
	assert(material.albedo_texture.get_size() == Vector2(2000, 400))


## Compare every saved mesh and surface to an independent unmodified imported instance.
func _inspect_model(model: Node3D) -> Dictionary:
	var reference := (load(MODEL) as PackedScene).instantiate()
	var shared_root := model.get_node("city_shop_fittings_02") as Node3D
	assert(shared_root.transform == Transform3D.IDENTITY)
	var meshes := 0
	var surfaces := 0
	var overrides := 0
	var bounds := AABB()
	for child: Node in shared_root.get_children():
		assert(child is MeshInstance3D)
		var mesh := child as MeshInstance3D
		var original := reference.get_node(
			NodePath("city_shop_fittings_02/" + mesh.name)
		) as MeshInstance3D
		overrides += _check_mesh(mesh, original)
		bounds = mesh.get_aabb() if meshes == 0 else bounds.merge(mesh.get_aabb())
		meshes += 1
		surfaces += mesh.mesh.get_surface_count()
	assert(meshes == 7 and surfaces == 8 and overrides == 1)
	assert(bounds.position.is_equal_approx(Vector3(-1.6, -0.4, -0.14)))
	assert(bounds.size.is_equal_approx(Vector3(3.2, 0.8, 0.14)))
	reference.free()
	return {
		"meshes": meshes,
		"surfaces": surfaces,
		"face_only_overrides": overrides,
		"aabb_min": [-1.6, -0.4, -0.14],
		"aabb_max": [1.6, 0.4, 0.0],
	}


## Reject transformed/replaced geometry and any override beyond the intended front face.
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
			var original_material := mesh.mesh.surface_get_material(surface)
			assert(original_material.resource_name == "fascia_artwork_face")
			assert(override.resource_path == MATERIAL)
	return overrides


## Save only the owned wrapper while keeping its imported model linked.
func _roundtrip() -> void:
	var packed := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_REPLACE)
	assert(packed != null)
	var instance := (packed as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, PREFAB) == OK)
	instance.free()
