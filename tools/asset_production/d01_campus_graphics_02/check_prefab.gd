extends "res://tools/asset_production/d06_commercial_graphics_03/check_prefab.gd"
## Check the campus face-only override using existing hierarchy and roundtrip helpers.

const CAMPUS_PREFAB := "res://scenes/prefabs/environment/d01_campus_graphics_02.tscn"
const CAMPUS_MATERIAL := "res://art/materials/environment/d01_campus_graphics_02/entry_panel.tres"
const CAMPUS_TEXTURE := (
	"res://art/textures/environment/d01_campus_graphics_02/entry_panel_albedo.png"
)
const BOARD_PREFAB := "res://scenes/prefabs/environment/city_sign_supports_02.tscn"
const BOARD_MODEL := "res://art/models/environment/city_sign_supports_02/city_sign_supports_02.glb"
const CAMPUS_RECEIPT := "C:/tmp/ft/assets/d01_campus_graphics_02/prefab.json"


## Load and compare all dependencies, optionally proving two stable save/reload cycles.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var material := load(CAMPUS_MATERIAL) as StandardMaterial3D
	_check_material(material, "entry_panel")
	if not normalize:
		_check_registered_dependencies()
	var hashes: Array[String] = []
	var material_hashes: Array[String] = []
	if normalize:
		assert(Engine.is_editor_hint(), "UID-preserving saves require --editor")
		assert(ResourceSaver.save(material, CAMPUS_MATERIAL) == OK)
		_roundtrip(CAMPUS_PREFAB)
		hashes.append(FileAccess.get_sha256(CAMPUS_PREFAB))
		material_hashes.append(FileAccess.get_sha256(CAMPUS_MATERIAL))
		for cycle: int in range(2):
			material = _reload_and_save_material()
			_roundtrip(CAMPUS_PREFAB)
			hashes.append(FileAccess.get_sha256(CAMPUS_PREFAB))
			material_hashes.append(FileAccess.get_sha256(CAMPUS_MATERIAL))
			assert(hashes[0] == hashes[cycle + 1], "Saved identities changed")
			assert(material_hashes[0] == material_hashes[cycle + 1], "Material changed")

	var instance := (load(CAMPUS_PREFAB) as PackedScene).instantiate()
	var reference := (load(BOARD_PREFAB) as PackedScene).instantiate()
	_compare_hierarchy(instance, reference)
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(instance.transform == Transform3D.IDENTITY)
	assert(model.transform == Transform3D.IDENTITY and model.scene_file_path == BOARD_MODEL)
	var receipt := _inspect_model(model, reference.get_node("Visuals/Model"), material)
	_check_collision(instance, reference)
	receipt.merge({
		"engine": Engine.get_version_info().string,
		"prefab": CAMPUS_PREFAB, "base_prefab": BOARD_PREFAB, "model": BOARD_MODEL,
		"prefab_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(CAMPUS_PREFAB)),
		"material_uid": ResourceUID.id_to_text(ResourceLoader.get_resource_uid(CAMPUS_MATERIAL)),
		"identity_transforms": true, "hierarchy_and_imported_meshes_unchanged": true,
		"inherited_collision_unchanged": true, "texture_size": [1440, 390],
		"mipmaps": true, "filter": "linear_mipmap", "repeat": false,
		"stable_roundtrips": 2 if normalize else 0, "roundtrip_sha256": hashes,
		"material_roundtrip_sha256": material_hashes, "status": "PASS",
	})
	var file := FileAccess.open(CAMPUS_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	instance.free()
	reference.free()
	print("CAMPUS_PREFAB_PASS: face-only override, linked meshes, inherited collision")
	quit()


## Reload and save the actual material resource rather than only resaving an in-memory object.
func _reload_and_save_material() -> StandardMaterial3D:
	var material := ResourceLoader.load(
		CAMPUS_MATERIAL, "StandardMaterial3D", ResourceLoader.CACHE_MODE_REPLACE
	) as StandardMaterial3D
	_check_material(material, "entry_panel")
	assert(ResourceSaver.save(material, CAMPUS_MATERIAL) == OK)
	return material


## Reject stale UIDs instead of accepting the engine's fallback to text dependency paths.
func _check_registered_dependencies() -> void:
	for dependency: String in [CAMPUS_PREFAB, CAMPUS_MATERIAL, CAMPUS_TEXTURE, BOARD_MODEL]:
		var uid := ResourceLoader.get_resource_uid(dependency)
		assert(ResourceUID.has_id(uid) and ResourceUID.get_id_path(uid) == dependency)


## Require an opaque, neutral-multiplier, clamped sRGB artwork texture with imported mipmaps.
func _check_material(material: StandardMaterial3D, _variant: String) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.resource_path == CAMPUS_TEXTURE)
	assert(material.albedo_texture.get_size() == Vector2(1440, 390))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE and is_equal_approx(material.roughness, 0.65))
	assert(material.uv1_scale == Vector3.ONE and material.uv1_offset == Vector3.ZERO)


## Inspect each linked mesh/surface and permit only the named artwork-face slot override.
func _inspect_model(model: Node3D, reference: Node, material: Material) -> Dictionary:
	var shared_root := model.get_node("CitySignSupports02") as Node3D
	var meshes := 0
	var surfaces := 0
	var overrides := 0
	var bounds := AABB()
	for child: Node in shared_root.get_children():
		assert(child is MeshInstance3D)
		var mesh := child as MeshInstance3D
		var original := reference.get_node(NodePath("CitySignSupports02/" + mesh.name))
		assert(mesh.mesh == (original as MeshInstance3D).mesh)
		assert(mesh.material_override == null)
		for surface: int in range(mesh.mesh.get_surface_count()):
			var override := mesh.get_surface_override_material(surface)
			if override != null:
				overrides += 1
				assert(mesh.name == "CitySignSupports02_ArtworkCarrier" and surface == 0)
				assert(mesh.mesh.surface_get_material(surface).resource_name == "sign_face")
				assert(override == material)
		bounds = mesh.get_aabb() if meshes == 0 else bounds.merge(mesh.get_aabb())
		meshes += 1
		surfaces += mesh.mesh.get_surface_count()
	assert(meshes == 2 and surfaces == 5 and overrides == 1)
	assert(bounds.position.is_equal_approx(Vector3(-0.8, 0, -0.2)))
	assert(bounds.size.is_equal_approx(Vector3(1.6, 1.35, 0.4)))
	return {
		"meshes": meshes, "surfaces": surfaces, "face_only_overrides": overrides,
		"aabb_min": [-0.8, 0, -0.2], "aabb_max": [0.8, 1.35, 0.2],
	}


## Preserve the carrier-owned box collider exactly; artwork cannot alter gameplay clearance.
func _check_collision(instance: Node, reference: Node) -> void:
	assert(instance.find_children("*", "CollisionObject3D", true, false).size() == 1)
	var body := instance.get_node("Collision/Body") as StaticBody3D
	var original := reference.get_node("Collision/Body") as StaticBody3D
	assert(body.collision_layer == 1 and body.collision_mask == 0)
	assert(body.collision_layer == original.collision_layer)
	assert(body.collision_mask == original.collision_mask)
	var shape := body.get_node("Shape") as CollisionShape3D
	assert(shape.shape == (original.get_node("Shape") as CollisionShape3D).shape)
	assert(not shape.disabled and shape.position == Vector3(0, 0.675, 0))
	assert((shape.shape as BoxShape3D).size == Vector3(1.6, 1.35, 0.4))
