extends SceneTree
## Verify the inherited support, face-only override and two UID-preserving save roundtrips.

const PREFAB := "res://scenes/prefabs/environment/d07_retail_graphics_02.tscn"
const SUPPORT := "res://scenes/prefabs/environment/d07_sign_island_02.tscn"
const MATERIAL := "res://art/materials/environment/d07_retail_graphics_02/sign_island_face.tres"
const MODEL := "res://art/models/environment/d07_sign_island_02/d07_sign_island_02.glb"
const RECEIPT := "C:/tmp/ft/assets/d07_retail_graphics_02/prefab.json"


## Defer checks until the scene tree is initialized.
func _initialize() -> void:
	_run.call_deferred()


## Normalize only owned resources and prove the saved result against unchanged hardware.
func _run() -> void:
	var material := load(MATERIAL) as StandardMaterial3D
	_check_material(material)
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	if normalize:
		_normalize(material)

	var packed := load(PREFAB) as PackedScene
	assert(packed.get_state().get_base_scene_state().get_path() == SUPPORT)
	var instance := packed.instantiate() as Node3D
	var reference := (load(SUPPORT) as PackedScene).instantiate() as Node3D
	assert(instance.transform == Transform3D.IDENTITY)
	_check_tree(instance, reference)
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == MODEL)
	_check_mesh(model.get_node("D07SignIsland02/D07SignIsland02_Mesh") as MeshInstance3D)
	_check_collision(instance)
	var receipt := {
		"engine": Engine.get_version_info().string,
		"prefab": PREFAB,
		"inherited_support": SUPPORT,
		"linked_model": MODEL,
		"identity_model_transform": true,
		"imported_mesh_resources_unchanged": true,
		"collision_inherited_unchanged": true,
		"collision_bodies": 1,
		"collision_boxes": 2,
		"meshes": 1,
		"surfaces": 4,
		"face_only_overrides": 1,
		"front_uv_vertices": 4,
		"aabb_min": [-2.2, 0.0, -0.4],
		"aabb_max": [2.2, 2.6, 0.4],
		"texture_size": [1920, 920],
		"filter": "linear_mipmap",
		"repeat": false,
		"status": "PASS",
	}
	if normalize:
		receipt["two_roundtrips_byte_identical"] = true
		receipt["prefab_sha256"] = FileAccess.get_sha256(PREFAB)
		receipt["prefab_uid"] = ResourceUID.id_to_text(ResourceLoader.get_resource_uid(PREFAB))

	_write_receipt(receipt)
	instance.free()
	reference.free()
	print("SIGN_FACE_PREFAB_PASS: inherited collision, one face override, UVs, stable identities")
	quit()


## Persist the bounded inspection results for the log-checked final receipt writer.
func _write_receipt(receipt: Dictionary) -> void:
	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()


## Stabilize owned resources, then require two unchanged complete-file roundtrips.
func _normalize(material: StandardMaterial3D) -> void:
	assert(Engine.is_editor_hint(), "Use --editor for UID-preserving saves")
	assert(ResourceSaver.save(material, MATERIAL) == OK)
	_roundtrip()
	var first := FileAccess.get_file_as_bytes(PREFAB)
	_roundtrip()
	assert(first == FileAccess.get_file_as_bytes(PREFAB), "First stable roundtrip drift")
	_roundtrip()
	assert(first == FileAccess.get_file_as_bytes(PREFAB), "Second stable roundtrip drift")


## Require opaque, clamped albedo, physical roughness and no illumination behavior.
func _check_material(material: StandardMaterial3D) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE)
	assert(is_equal_approx(material.roughness, 0.56) and material.metallic == 0.0)
	assert(material.albedo_texture.get_size() == Vector2(1920, 920))
	assert(material.albedo_texture.get_image().has_mipmaps())


## Reject any extra/missing nodes, changed transforms, localized meshes or colliders.
func _check_tree(node: Node, reference: Node) -> void:
	assert(node.get_class() == reference.get_class())
	assert(node.get_child_count() == reference.get_child_count())
	if node is Node3D:
		assert((node as Node3D).transform == (reference as Node3D).transform)
	if node is MeshInstance3D:
		assert((node as MeshInstance3D).mesh == (reference as MeshInstance3D).mesh)
	if node is CollisionShape3D:
		assert((node as CollisionShape3D).shape == (reference as CollisionShape3D).shape)
		assert(not (node as CollisionShape3D).disabled)
	for index: int in range(node.get_child_count()):
		var child := node.get_child(index)
		var original := reference.get_child(index)
		assert(child.name == original.name)
		_check_tree(child, original)


## Independently check the front's UV orientation and all unaffected material surfaces.
func _check_mesh(mesh: MeshInstance3D) -> void:
	assert(mesh.material_override == null and mesh.mesh.get_surface_count() == 4)
	assert(mesh.get_aabb().position.is_equal_approx(Vector3(-2.2, 0.0, -0.4)))
	assert(mesh.get_aabb().size.is_equal_approx(Vector3(4.4, 2.6, 0.8)))
	for surface: int in range(4):
		var override := mesh.get_surface_override_material(surface)
		if surface == 0:
			assert(override != null and override.resource_path == MATERIAL)
			assert(mesh.mesh.surface_get_material(0).resource_name == "sign_island_artwork_face")
		else:
			assert(override == null)

	var arrays := mesh.mesh.surface_get_arrays(0)
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
	assert(vertices.size() == 4 and arrays[Mesh.ARRAY_INDEX].size() == 6)
	for index: int in range(4):
		assert(is_equal_approx(vertices[index].z, -0.29))
		assert(is_equal_approx(uvs[index].x, 0.0 if vertices[index].x > 0 else 1.0))
		assert(is_equal_approx(uvs[index].y, 1.0 if vertices[index].y < 1 else 0.0))


## Confirm that the freestanding artwork retains exactly the support owner's blockers.
func _check_collision(instance: Node3D) -> void:
	assert(instance.find_children("*", "CollisionObject3D", true, false).size() == 1)
	assert(instance.find_children("*", "CollisionShape3D", true, false).size() == 2)
	var body := instance.get_node("Collision/Body") as StaticBody3D
	assert(body.collision_layer == 1 and body.collision_mask == 0)
	var foot := body.get_node("Foot") as CollisionShape3D
	var casing := body.get_node("Casing") as CollisionShape3D
	assert((foot.shape as BoxShape3D).size.is_equal_approx(Vector3(4.4, 0.24, 0.8)))
	assert(foot.position.is_equal_approx(Vector3(0, 0.12, 0)))
	assert((casing.shape as BoxShape3D).size.is_equal_approx(Vector3(4.2, 2.36, 0.6)))
	assert(casing.position.is_equal_approx(Vector3(0, 1.42, 0)))


## Pack and save only the owned inherited scene, retaining its external support ancestry.
func _roundtrip() -> void:
	var packed := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_REPLACE)
	assert(packed != null)
	var instance := (packed as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, PREFAB) == OK)
	instance.free()
