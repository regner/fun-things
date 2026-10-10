extends "res://tools/asset_production/d06_commercial_graphics_03/check_prefab.gd"
## Audit the civic noticeboard using existing hierarchy and resource-roundtrip helpers.

const NOTICEBOARD_PREFAB := "res://scenes/prefabs/environment/d05_civic_graphics_02.tscn"
const BOARD_PREFAB := "res://scenes/prefabs/environment/city_sign_supports_03.tscn"
const BOARD_MODEL := "res://art/models/environment/city_sign_supports_03/city_sign_supports_03.glb"
const NOTICEBOARD_MATERIAL := (
	"res://art/materials/environment/d05_civic_graphics_02/noticeboard.tres"
)
const NOTICEBOARD_TEXTURE := (
	"res://art/textures/environment/d05_civic_graphics_02/noticeboard_albedo.png"
)
const NOTICEBOARD_RECEIPT := "C:/tmp/ft/assets/d05_civic_graphics_02/prefab.json"
const IMPORTED_UV_TOLERANCE := 0.00005
const CHECK_DEADLINE_SECONDS := 30.0


## Fail closed when asynchronous assertions interrupt the audit.
func _initialize() -> void:
	create_timer(CHECK_DEADLINE_SECONDS).timeout.connect(_deadline)
	_run.call_deferred()


## Return failure instead of hanging or mistaking an assertion for a successful check.
func _deadline() -> void:
	push_error("Noticeboard audit did not finish")
	quit(1)


## Normalize only owned files; prove inherited hardware, material mapping and collider identity.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var roundtrip_hashes: Array[String] = []
	var material := load(NOTICEBOARD_MATERIAL) as StandardMaterial3D
	_check_material(material, "noticeboard")
	if normalize:
		assert(Engine.is_editor_hint())
		assert(ResourceSaver.save(material, NOTICEBOARD_MATERIAL) == OK)
		_roundtrip(NOTICEBOARD_PREFAB)
		var first := FileAccess.get_file_as_bytes(NOTICEBOARD_PREFAB)
		roundtrip_hashes.append(FileAccess.get_sha256(NOTICEBOARD_PREFAB))
		for pass_index: int in range(2):
			_roundtrip(NOTICEBOARD_PREFAB)
			assert(first == FileAccess.get_file_as_bytes(NOTICEBOARD_PREFAB),
				"Scene bytes/IDs changed on roundtrip %d" % pass_index)
			roundtrip_hashes.append(FileAccess.get_sha256(NOTICEBOARD_PREFAB))

	var instance := (load(NOTICEBOARD_PREFAB) as PackedScene).instantiate() as Node3D
	var reference := (load(BOARD_PREFAB) as PackedScene).instantiate()
	_compare_hierarchy(instance, reference)
	assert(instance.transform == Transform3D.IDENTITY)
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.scene_file_path == BOARD_MODEL and model.transform == Transform3D.IDENTITY)
	var receipt := _inspect_model(model, reference.get_node("Visuals/Model"), material)
	_check_collision(instance, reference)
	root.add_child(instance)
	await physics_frame
	await physics_frame
	_check_queries(instance)
	receipt.merge({
		"engine": Engine.get_version_info().string,
		"prefab": NOTICEBOARD_PREFAB, "base_prefab": BOARD_PREFAB, "linked_model": BOARD_MODEL,
		"roundtrip_sha256": roundtrip_hashes,
		"resource_uids": _check_resource_uids(),
		"hierarchy_meshes_and_collision_unchanged": true, "imported_mipmaps": true,
		"texture_size": [1640, 1040], "ray_center_blocked_side_and_above_clear": true,
		"prefab_sha256": FileAccess.get_sha256(NOTICEBOARD_PREFAB),
		"status": "PASS",
	})
	var file := FileAccess.open(NOTICEBOARD_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	instance.free()
	reference.free()
	print("NOTICEBOARD_PREFAB_PASS: linked hardware, face-only override, unchanged collider")
	quit()


## Require the exact opaque, clamped, mipmapped artwork with no UV correction or emission.
func _check_material(material: StandardMaterial3D, _variant: String) -> void:
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.resource_path == NOTICEBOARD_TEXTURE)
	assert(material.albedo_texture.get_size() == Vector2(1640, 1040))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE and is_equal_approx(material.roughness, 0.56))
	assert(is_zero_approx(material.metallic))
	assert(material.uv1_scale == Vector3.ONE and material.uv1_offset == Vector3.ZERO)


## Check every shared mesh/surface and allow exactly one front-face material override.
func _inspect_model(model: Node3D, reference: Node, material: Material) -> Dictionary:
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	assert(meshes.size() == 2)
	var bounds := AABB()
	var surfaces := 0
	var overrides := 0
	for child: MeshInstance3D in meshes:
		var original := reference.get_node(model.get_path_to(child)) as MeshInstance3D
		assert(child.mesh == original.mesh and child.material_override == null)
		bounds = child.get_aabb() if surfaces == 0 else bounds.merge(child.get_aabb())
		for surface: int in range(child.mesh.get_surface_count()):
			var override := child.get_surface_override_material(surface)
			if override != null:
				overrides += 1
				assert(child.name == "CitySignSupports03_ArtworkCarrier" and surface == 0)
				assert(child.mesh.surface_get_material(surface).resource_name == "sign_face")
				assert(override == material)

		surfaces += child.mesh.get_surface_count()

	assert(surfaces == 5 and overrides == 1)
	assert(bounds.position.distance_to(Vector3(-0.95, 0, -0.22)) < 0.001)
	assert(bounds.size.distance_to(Vector3(1.9, 2.1, 0.44)) < 0.001)
	return {
		"meshes": 2, "surfaces": surfaces, "face_only_overrides": overrides,
		"aabb_min": [-0.95, 0, -0.22], "aabb_max": [0.95, 2.1, 0.22],
		"imported_uv_max_error": _check_uv(model),
	}


## Verify imported UV orientation against the noticeboard carrier's physical face dimensions.
func _check_uv(model: Node3D) -> float:
	var face := model.get_node("CitySignSupports03/CitySignSupports03_ArtworkCarrier")
	var arrays := (face as MeshInstance3D).mesh.surface_get_arrays(0)
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
	assert(vertices.size() == 28 and uvs.size() == 28)
	var max_error := 0.0
	for index: int in range(vertices.size()):
		assert(absf(vertices[index].z + 0.071) < 0.00001)
		max_error = maxf(max_error, absf(uvs[index].x - (0.82 - vertices[index].x) / 1.64))
		max_error = maxf(max_error, absf(uvs[index].y - (1.94 - vertices[index].y) / 1.04))

	assert(max_error < IMPORTED_UV_TOLERANCE)
	return max_error


## Keep the existing full-envelope box, including its deliberate under-panel blocking.
func _check_collision(instance: Node, reference: Node) -> void:
	assert(instance.find_children("*", "CollisionObject3D", true, false).size() == 1)
	var body := instance.get_node("Collision/Body") as StaticBody3D
	assert(body.collision_layer == 1 and body.collision_mask == 0)
	var shape := body.get_node("Shape") as CollisionShape3D
	var original := reference.get_node("Collision/Body/Shape") as CollisionShape3D
	assert(shape.shape == original.shape and not shape.disabled)
	assert(shape.position.is_equal_approx(Vector3(0, 1.05, 0)))
	assert((shape.shape as BoxShape3D).size.is_equal_approx(Vector3(1.9, 2.1, 0.44)))


## Exercise the inherited solid centre and independent clear-side/above expectations.
func _check_queries(instance: Node3D) -> void:
	var space := instance.get_world_3d().direct_space_state
	var hit := space.intersect_ray(
		PhysicsRayQueryParameters3D.create(Vector3(0, 0.7, 2), Vector3(0, 0.7, -2), 1)
	)
	assert(not hit.is_empty() and hit.collider == instance.get_node("Collision/Body"))
	for point: Vector3 in [Vector3(1.05, 0.7, 2), Vector3(0, 2.3, 2)]:
		var clear := space.intersect_ray(
			PhysicsRayQueryParameters3D.create(point, point + Vector3(0, 0, -4), 1)
		)
		assert(clear.is_empty())


## Resolve saved dependency identities in fresh runtimes after the import scan.
func _check_resource_uids() -> Dictionary:
	var result := {}
	for path: String in [NOTICEBOARD_PREFAB, BOARD_PREFAB, BOARD_MODEL,
		NOTICEBOARD_MATERIAL, NOTICEBOARD_TEXTURE]:
		var resource_uid := ResourceLoader.get_resource_uid(path)
		assert(resource_uid != ResourceUID.INVALID_ID)
		if not Engine.is_editor_hint():
			assert(ResourceUID.has_id(resource_uid))
			assert(ResourceUID.get_id_path(resource_uid) == path)
		result[path] = ResourceUID.id_to_text(resource_uid)
	return result
