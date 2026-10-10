extends SceneTree
## Validate the linked panel, external face remap and normalized saved identities.

const PREFAB := "res://scenes/prefabs/environment/d04_corporate_graphics_01.tscn"
const MODEL := (
	"res://art/models/environment/d04_corporate_graphics_01/" + "d04_corporate_graphics_01.glb"
)
const MATERIAL := "res://art/materials/environment/d04_corporate_graphics_01/tomorrow.tres"
const SCRATCH := "C:/tmp/ft/assets/d04_corporate_graphics_01/"


## Defer until resource initialization finishes.
func _initialize() -> void:
	_run.call_deferred()


## Normalize only owned resources when requested, then inspect the production prefab.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var material := load(MATERIAL) as StandardMaterial3D
	_check_material(material)
	if normalize:
		assert(Engine.is_editor_hint())
		assert(ResourceSaver.save(material, MATERIAL) == OK)
		_roundtrip()
		var initial := FileAccess.get_file_as_bytes(PREFAB)
		for cycle: int in range(2):
			_roundtrip()
			assert(initial == FileAccess.get_file_as_bytes(PREFAB), "Saved identities changed")

	var instance := (load(PREFAB) as PackedScene).instantiate()
	assert(instance.transform == Transform3D.IDENTITY)
	assert(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == MODEL)
	var receipt := _inspect_meshes(model)
	receipt.merge({
		"status": "PASS",
		"engine": Engine.get_version_info().string,
		"no_collision": true,
		"identity_model_transform": true,
		"prefab_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(PREFAB)),
		"model_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(MODEL)),
		"material_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(MATERIAL)),
		"stable_roundtrips": 2 if normalize else 0,
	})
	var filename := "normalization.json" if normalize else "prefab.json"
	var file := FileAccess.open(SCRATCH + filename, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	instance.free()
	print("CORPORATE_PREFAB_PASS: linked source, face remap, bounds and dependencies")
	quit()


## Require an opaque clamped white-multiplied albedo with mipmaps and no emission.
func _check_material(material: StandardMaterial3D) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.get_size() == Vector2(1608, 1128))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE)


## Inspect actual imported resources and prove only the front uses the artwork material.
func _inspect_meshes(model: Node3D) -> Dictionary:
	var source_root := model.get_node("D04CorporateGraphics01") as Node3D
	assert(source_root.transform == Transform3D.IDENTITY)
	var bounds := AABB()
	var mesh_count := 0
	var surfaces := 0
	var artwork_surfaces := 0
	for child: Node in source_root.get_children():
		assert(child is MeshInstance3D)
		var mesh := child as MeshInstance3D
		assert(mesh.transform == Transform3D.IDENTITY and mesh.material_override == null)
		assert(mesh.mesh.resource_path.begins_with(MODEL + "::"))
		bounds = mesh.get_aabb() if mesh_count == 0 else bounds.merge(mesh.get_aabb())
		mesh_count += 1
		for surface: int in range(mesh.mesh.get_surface_count()):
			assert(mesh.get_surface_override_material(surface) == null)
			var mat := mesh.mesh.surface_get_material(surface)
			assert(mat != null)
			if mat.resource_path == MATERIAL:
				assert(mesh.name == "D04CorporateGraphics01_ArtworkCarrier" and surface == 0)
				artwork_surfaces += 1
			surfaces += 1
	assert(mesh_count == 2 and surfaces == 5 and artwork_surfaces == 1)
	assert(bounds.position.is_equal_approx(Vector3(-2.8, -2, -0.14)))
	assert(bounds.size.is_equal_approx(Vector3(5.6, 4, 0.14)))
	return { "meshes": mesh_count, "surfaces": surfaces, "artwork_surfaces": artwork_surfaces }


## Pack and save the wrapper while preserving the linked model and generated identities.
func _roundtrip() -> void:
	var packed := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_REPLACE)
	var instance := (packed as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, PREFAB) == OK)
	instance.free()
