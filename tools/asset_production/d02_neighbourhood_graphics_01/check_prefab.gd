extends SceneTree
## Verify face-only artwork on the unchanged wall panel, preserving saved identities.

const NID := "d02_neighbourhood_graphics_01"
const BASE := "res://scenes/prefabs/environment/city_sign_supports_01.tscn"
const MODEL := "res://art/models/environment/city_sign_supports_01/city_sign_supports_01.glb"
const PREFAB := "res://scenes/prefabs/environment/" + NID + ".tscn"
const MATERIAL := "res://art/materials/environment/" + NID + "/watch_notice.tres"
const TEXTURE := "res://art/textures/environment/" + NID + "/watch_notice_albedo.png"
const RECEIPT := "C:/tmp/ft/assets/" + NID + "/prefab.json"


## Defer resource inspection until the tree has initialized.
func _initialize() -> void:
	_run.call_deferred()


## Check the actual dependency chain, optionally normalizing only owned resources.
func _run() -> void:
	var material := load(MATERIAL) as StandardMaterial3D
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.resource_path == TEXTURE)
	assert(material.albedo_texture.get_size() == Vector2(1220, 820))
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
		assert(ResourceSaver.save(material, MATERIAL) == OK)
		_roundtrip()
		# Initial normalization establishes new IDs; the following two cycles must retain them.
		var initial := FileAccess.get_file_as_bytes(PREFAB)
		for cycle: int in range(2):
			_roundtrip()
			assert(initial == FileAccess.get_file_as_bytes(PREFAB), "Saved identity drift")
			roundtrips.append(FileAccess.get_sha256(PREFAB))

	var instance := (load(PREFAB) as PackedScene).instantiate()
	var reference := (load(BASE) as PackedScene).instantiate()
	assert(instance.transform == Transform3D.IDENTITY)
	_compare_hierarchy(instance, reference)
	assert(instance.find_children("*", "CollisionObject3D", true, false).is_empty())
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == MODEL)
	var result := _inspect_model(model, reference.get_node("Visuals/Model"), material)
	result.merge({
		"status": "PASS", "engine": Engine.get_version_info().string,
		"prefab": PREFAB, "prefab_sha256": FileAccess.get_sha256(PREFAB),
		"two_stable_roundtrip_sha256": roundtrips,
		"mipmaps_present": true, "texture_dimensions": [1220, 820],
		"identity_model_transform": true, "hierarchy_and_geometry_unchanged": true,
		"collision": "None; mounted decorative face inherits facade-owned blocking",
	})
	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(result, "\t") + "\n")
	file.close()
	instance.free()
	reference.free()
	print("WATCH_PREFAB_PASS: shared geometry, face-only override, stable identities")
	quit()


## Reject any extra node, moved child or class change against the original carrier.
func _compare_hierarchy(node: Node, reference: Node) -> void:
	assert(node.get_class() == reference.get_class())
	assert(node.get_child_count() == reference.get_child_count())
	if node is Node3D:
		assert((node as Node3D).transform == (reference as Node3D).transform)

	for index: int in range(node.get_child_count()):
		assert(node.get_child(index).name == reference.get_child(index).name)
		_compare_hierarchy(node.get_child(index), reference.get_child(index))


## Check every surface and measured bounds, allowing only sign_face to be replaced.
func _inspect_model(model: Node3D, reference: Node, material: Material) -> Dictionary:
	var meshes := 0
	var surfaces := 0
	var overrides := 0
	var bounds := AABB()
	for child: Node in model.get_node("CitySignSupports01").get_children():
		assert(child is MeshInstance3D)
		var mesh := child as MeshInstance3D
		var original := reference.get_node(NodePath("CitySignSupports01/" + mesh.name))
		assert(mesh.mesh == (original as MeshInstance3D).mesh)
		assert(mesh.material_override == null)
		for surface: int in range(mesh.mesh.get_surface_count()):
			var override := mesh.get_surface_override_material(surface)
			if override != null:
				overrides += 1
				assert(mesh.name == "artwork_carrier" and surface == 0)
				assert(mesh.mesh.surface_get_material(surface).resource_name == "sign_face")
				assert(override == material)
		bounds = mesh.get_aabb() if meshes == 0 else bounds.merge(mesh.get_aabb())
		meshes += 1
		surfaces += mesh.mesh.get_surface_count()
	assert(meshes == 12 and surfaces == 13 and overrides == 1)
	assert(bounds.position.is_equal_approx(Vector3(-0.7, -0.5, -0.1)))
	assert(bounds.size.is_equal_approx(Vector3(1.4, 1, 0.1)))
	return {
		"meshes": meshes, "surfaces": surfaces, "face_only_overrides": overrides,
		"aabb_min": [-0.7, -0.5, -0.1], "aabb_max": [0.7, 0.5, 0],
	}


## Pack and save only the artwork variant, retaining its inherited linked scene.
func _roundtrip() -> void:
	var packed := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_REPLACE)
	assert(packed != null)
	var instance := (packed as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, PREFAB) == OK)
	instance.free()
