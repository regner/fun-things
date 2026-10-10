extends SceneTree
## Inspect the saved artwork-only override; --normalize also resaves owned resources.

const PREFAB := "res://scenes/prefabs/environment/d05_civic_graphics_01.tscn"
const MATERIAL := "res://art/materials/environment/d05_civic_graphics_01/hall_fascia.tres"
const MODEL := "res://art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb"
const PREVIEW := "res://scenes/prefabs/environment/d05_civic_graphics_01_hall_preview.tscn"
const RECEIPT := "C:/tmp/ft/assets/d05_civic_graphics_01/prefab.json"


## Defer validation until the scene tree has completed startup.
func _initialize() -> void:
	_run.call_deferred()


## Check dependencies and linked geometry, optionally normalizing only owned resources.
func _run() -> void:
	var material := load(MATERIAL) as StandardMaterial3D
	_check_material(material)
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var roundtrip_hashes := _normalize(material) if normalize else {}

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
	receipt["mounting"] = _check_mounting()
	receipt["resource_uids"] = _resource_uids()
	assert(receipt["resource_uids"].size() == 4, "Incomplete UID validation")
	receipt["prefab_sha256"] = FileAccess.get_sha256(PREFAB)
	receipt["preview_sha256"] = FileAccess.get_sha256(PREVIEW)
	if normalize:
		receipt["two_roundtrips_byte_identical"] = true
		receipt["roundtrip_sha256"] = roundtrip_hashes

	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	instance.free()
	print("HALL_PREFAB_PASS: linked meshes, face-only override, bounds, dependencies")
	quit()


## Stabilize new resources, then prove two full byte-identical save/reload cycles.
func _normalize(material: StandardMaterial3D) -> Dictionary:
	assert(Engine.is_editor_hint(), "Use --editor for UID-preserving resource saves")
	assert(ResourceSaver.save(material, MATERIAL) == OK)
	var hashes := {}
	for path: String in [PREFAB, PREVIEW]:
		_roundtrip(path)
		var baseline := FileAccess.get_file_as_bytes(path)
		hashes[path] = [FileAccess.get_sha256(path)]
		for cycle: int in range(2):
			_roundtrip(path)
			assert(baseline == FileAccess.get_file_as_bytes(path), "Scene IDs changed")
			hashes[path].append(FileAccess.get_sha256(path))
	return hashes


## Require a clamped opaque albedo with no hidden illumination or texture multiplier.
func _check_material(material: StandardMaterial3D) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE)
	assert(material.albedo_texture.get_size() == Vector2(2000, 400))
	assert(material.albedo_texture.get_image().has_mipmaps())


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
func _roundtrip(path: String) -> void:
	var packed := ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_REPLACE)
	assert(packed != null)
	var instance := (packed as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, path) == OK)
	instance.free()


## Measure the above-head mount without adding collision or changing the hall prefab.
func _check_mounting() -> Dictionary:
	var preview := (load(PREVIEW) as PackedScene).instantiate()
	var hall := preview.get_node("Hall") as Node3D
	var canopy := preview.get_node("Canopy") as Node3D
	var fascia := preview.get_node("Fascia") as Node3D
	assert(hall.transform == Transform3D.IDENTITY)
	assert(canopy.position.is_equal_approx(Vector3(0, 3.85, -9)))
	assert(fascia.position.is_equal_approx(Vector3(0, 4.95, -9)))
	assert(fascia.basis == Basis.IDENTITY and canopy.basis == Basis.IDENTITY)
	var canopy_mesh := canopy.find_children("*", "MeshInstance3D", true, false)[0]
	var canopy_top: float = canopy_mesh.get_aabb().end.y + canopy.position.y
	var fascia_bottom := fascia.position.y - 0.4
	assert(is_equal_approx(canopy_top, 4.25))
	assert(is_equal_approx(fascia_bottom - canopy_top, 0.3))
	assert(fascia_bottom > 2.5)
	assert(preview.find_children("*", "CollisionShape3D", true, false).size() == 3)
	assert(preview.find_children("*", "CollisionObject3D", true, false).size() == 1)
	preview.free()
	return { "position": [0, 4.95, -9], "canopy_gap_m": 0.3, "existing_colliders": 3 }


## Resolve all owned resource UIDs and ensure the imported dependency remains addressable.
func _resource_uids() -> Dictionary:
	var result := {}
	for path: String in [PREFAB, PREVIEW, MATERIAL, MODEL]:
		var resource_uid := ResourceLoader.get_resource_uid(path)
		assert(resource_uid != ResourceUID.INVALID_ID)
		# Newly saved editor UIDs enter the registry on the following filesystem scan.
		# The separate post-import runtime invocation must resolve them through the cache.
		if not Engine.is_editor_hint():
			assert(ResourceUID.has_id(resource_uid))
			assert(ResourceUID.get_id_path(resource_uid) == path)
		result[path] = ResourceUID.id_to_text(resource_uid)
	return result
