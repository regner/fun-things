extends SceneTree
## Audit two saved wrap variants against the unchanged drum prefab and cylinder collision.

const NID := "d06_commercial_graphics_03"
const VARIANTS := ["last_call", "small_prices"]
const BASE := "res://scenes/prefabs/environment/d06_poster_drum_01.tscn"
const MODEL := "res://art/models/environment/d06_poster_drum_01/d06_poster_drum_01.glb"
const RECEIPT := "C:/tmp/ft/assets/d06_commercial_graphics_03/prefab.json"


## Wait for tree startup before inspecting resource dependencies.
func _initialize() -> void:
	_run.call_deferred()


## Check both variants, recording normalization only when explicitly requested.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var variants: Array[Dictionary] = []
	for variant: String in VARIANTS:
		variants.append(_check_variant(variant, normalize))

	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify({
		"engine": Engine.get_version_info().string,
		"variants": variants,
		"status": "PASS",
	}, "\t") + "\n")
	file.close()
	print("POSTER_WRAP_PREFABS_PASS: linked geometry, wrap-only overrides, inherited collision")
	quit()


## Load dependencies and prove each wrapper preserves the base visual and collision hierarchy.
func _check_variant(variant: String, normalize: bool) -> Dictionary:
	var prefab := "res://scenes/prefabs/environment/%s_%s.tscn" % [NID, variant]
	var material_path := "res://art/materials/environment/%s/%s.tres" % [NID, variant]
	var material := load(material_path) as StandardMaterial3D
	_check_material(material, variant)
	if normalize:
		assert(Engine.is_editor_hint(), "UID-preserving saves require --editor")
		assert(ResourceSaver.save(material, material_path) == OK)
		_roundtrip(prefab)
		var first := FileAccess.get_file_as_bytes(prefab)
		_roundtrip(prefab)
		assert(first == FileAccess.get_file_as_bytes(prefab), "Scene IDs changed on resave")

	var instance := (load(prefab) as PackedScene).instantiate()
	var reference := (load(BASE) as PackedScene).instantiate()
	assert(instance.transform == Transform3D.IDENTITY)
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == MODEL)
	_compare_hierarchy(instance, reference)
	var receipt := _inspect_model(model, reference.get_node("Visuals/Model"), material)
	_check_collision(instance, reference)
	receipt.merge({
		"prefab": prefab, "material": material_path, "texture_size": [2400, 1000],
		"identity_model_transform": true, "imported_mesh_resources_unchanged": true,
		"inherited_collision_unchanged": true, "second_roundtrip_byte_identical": normalize,
	})
	instance.free()
	reference.free()
	return receipt


## Reject added nodes, moved children or class changes anywhere in the inherited hierarchy.
func _compare_hierarchy(node: Node, reference: Node) -> void:
	assert(node.get_class() == reference.get_class())
	assert(node.get_child_count() == reference.get_child_count())
	if node is Node3D:
		assert((node as Node3D).transform == (reference as Node3D).transform)

	for index: int in range(node.get_child_count()):
		assert(node.get_child(index).name == reference.get_child(index).name)
		_compare_hierarchy(node.get_child(index), reference.get_child(index))


## Require opaque, clamped, mipmapped artwork without illumination or colour multiplication.
func _check_material(material: StandardMaterial3D, variant: String) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.get_size() == Vector2(2400, 1000))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.albedo_texture.resource_path == (
		"res://art/textures/environment/%s/%s_albedo.png" % [NID, variant]
	))
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE and is_equal_approx(material.roughness, 0.7))


## Compare every imported surface, permitting only the body's intended wrap slot to differ.
func _inspect_model(model: Node3D, reference: Node, material: Material) -> Dictionary:
	var root := model.get_node("D06PosterDrum01") as Node3D
	var meshes := 0
	var surfaces := 0
	var overrides := 0
	var bounds := AABB()
	for child: Node in root.get_children():
		assert(child is MeshInstance3D)
		var mesh := child as MeshInstance3D
		var original := reference.get_node(NodePath("D06PosterDrum01/" + mesh.name))
		assert(mesh.mesh == (original as MeshInstance3D).mesh)
		assert(mesh.material_override == null)
		for surface: int in range(mesh.mesh.get_surface_count()):
			var override := mesh.get_surface_override_material(surface)
			if override != null:
				overrides += 1
				assert(mesh.name == "D06PosterDrum01_Body" and surface == 1)
				assert(mesh.mesh.surface_get_material(surface).resource_name == "poster_wrap")
				assert(override == material)
		bounds = mesh.get_aabb() if meshes == 0 else bounds.merge(mesh.get_aabb())
		meshes += 1
		surfaces += mesh.mesh.get_surface_count()
	assert(meshes == 2 and surfaces == 3 and overrides == 1)
	assert(bounds.position.is_equal_approx(Vector3(-0.45, 0, -0.45)))
	assert(bounds.size.is_equal_approx(Vector3(0.9, 1.45, 0.9)))
	return {
		"meshes": meshes, "surfaces": surfaces, "wrap_only_overrides": overrides,
		"aabb_min": [-0.45, 0, -0.45], "aabb_max": [0.45, 1.45, 0.45],
	}


## Protect the exact inherited static cylinder rather than inventing graphics-owned physics.
func _check_collision(instance: Node, reference: Node) -> void:
	assert(instance.find_children("*", "CollisionObject3D", true, false).size() == 1)
	var body := instance.get_node("Collision/Body") as StaticBody3D
	var original := reference.get_node("Collision/Body") as StaticBody3D
	assert(body.collision_layer == 1 and body.collision_mask == 0)
	assert(body.collision_layer == original.collision_layer)
	assert(body.collision_mask == original.collision_mask)
	var shape := body.get_node("Shape") as CollisionShape3D
	assert(shape.shape == (original.get_node("Shape") as CollisionShape3D).shape)
	assert(not shape.disabled and shape.position == Vector3(0, 0.725, 0))
	var cylinder := shape.shape as CylinderShape3D
	assert(is_equal_approx(cylinder.radius, 0.45) and is_equal_approx(cylinder.height, 1.45))


## Save only the owned variant, retaining inherited base and linked model resources.
func _roundtrip(prefab: String) -> void:
	var packed := ResourceLoader.load(prefab, "PackedScene", ResourceLoader.CACHE_MODE_REPLACE)
	assert(packed != null)
	var instance := (packed as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, prefab) == OK)
	instance.free()
