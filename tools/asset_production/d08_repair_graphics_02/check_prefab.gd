extends "res://tools/asset_production/d08_repair_graphics_01/check_prefab.gd"
## Verify depot face overrides, unchanged low-panel hardware and inherited static collision.

const DEPOT_ID := "d08_repair_graphics_02"
const DEPOT_VARIANTS := ["depot_right", "depot_right_patched"]
const DEPOT_RECEIPT := "C:/tmp/ft/assets/d08_repair_graphics_02/prefab.json"
const LOW_PREFAB := "res://scenes/prefabs/environment/city_sign_supports_02.tscn"
const LOW_MODEL := "res://art/models/environment/city_sign_supports_02/city_sign_supports_02.glb"
const CHECK_DEADLINE_SECONDS := 45.0


## Fail closed if an assertion prevents a complete receipt.
func _initialize() -> void:
	create_timer(CHECK_DEADLINE_SECONDS).timeout.connect(_deadline)
	_run.call_deferred()


## Reject incomplete checks rather than hanging or leaving a success exit code.
func _deadline() -> void:
	push_error("Depot artwork check did not complete")
	quit(1)


## Normalize only the two owned appearances and audit each saved instance.
func _run() -> void:
	var normalize := OS.get_cmdline_user_args().has("--normalize")
	var receipts: Array[Dictionary] = []
	for variant: String in DEPOT_VARIANTS:
		receipts.append(await _check_depot(variant, normalize))

	var file := FileAccess.open(DEPOT_RECEIPT, FileAccess.WRITE)
	file.store_string(JSON.stringify({
		"engine": Engine.get_version_info().string,
		"variants": receipts,
		"status": "PASS",
	}, "\t") + "\n")
	file.close()
	print("DEPOT_PREFABS_PASS: face-only overrides, inherited box, rays, mipmaps, stable UIDs")
	quit()


## Retain every imported mesh, transform and collision resource from the shared prefab.
func _check_depot(variant: String, normalize: bool) -> Dictionary:
	var suffix := "" if variant == "depot_right" else "_patched"
	var prefab := "res://scenes/prefabs/environment/%s%s.tscn" % [DEPOT_ID, suffix]
	var material_path := "res://art/materials/environment/%s/%s.tres" % [DEPOT_ID, variant]
	var material := load(material_path) as StandardMaterial3D
	_check_material(material, variant)
	if normalize:
		_normalize_repair(prefab, material_path, material)

	var instance := (load(prefab) as PackedScene).instantiate()
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
		"prefab": prefab, "material": material_path, "texture_size": [1440, 390],
		"linked_model": LOW_MODEL, "base_prefab": LOW_PREFAB,
		"identity_transforms": true, "hierarchy_and_mesh_resources_unchanged": true,
		"imported_mipmaps": true, "inherited_collision_unchanged": true,
		"ray_queries": { "center_blocked": true, "side_clear": true, "overhead_clear": true },
		"byte_stable_scene_material_roundtrips": 2 if normalize else 0,
		"prefab_sha256": FileAccess.get_sha256(prefab),
		"material_sha256": FileAccess.get_sha256(material_path),
	})
	instance.free()
	reference.free()
	return receipt


## Require the family's non-emissive, opaque, clamped paint with actual imported mipmaps.
func _check_material(material: StandardMaterial3D, variant: String) -> void:
	var texture := "res://art/textures/environment/%s/%s_albedo.png" % [DEPOT_ID, variant]
	assert(material != null and material.albedo_texture != null)
	assert(material.albedo_texture.resource_path == texture)
	assert(material.albedo_texture.get_size() == Vector2(1440, 390))
	assert(material.albedo_texture.get_image().has_mipmaps())
	assert(material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
	assert(not material.texture_repeat and not material.emission_enabled)
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(material.cull_mode == BaseMaterial3D.CULL_BACK)
	assert(material.albedo_color == Color.WHITE and is_equal_approx(material.roughness, 0.82))
	assert(is_zero_approx(material.metallic))
	assert(material.uv1_scale == Vector3.ONE and material.uv1_offset == Vector3.ZERO)


## Compare both imported meshes and all five surfaces against the source-linked reference.
func _inspect_model(model: Node3D, reference: Node, material: Material) -> Dictionary:
	var meshes := 0
	var surfaces := 0
	var overrides := 0
	var bounds := AABB()
	for child: Node in model.get_node("CitySignSupports02").get_children():
		assert(child is MeshInstance3D)
		var mesh := child as MeshInstance3D
		var original := reference.get_node(NodePath("CitySignSupports02/" + mesh.name))
		assert(mesh.mesh == (original as MeshInstance3D).mesh)
		assert(mesh.material_override == null)
		overrides += _check_face(mesh, material)
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


## Restrict artwork to the front slot while retaining hardware, rear and side materials.
func _check_face(mesh: MeshInstance3D, material: Material) -> int:
	var overrides := 0
	for surface: int in range(mesh.mesh.get_surface_count()):
		var override := mesh.get_surface_override_material(surface)
		if override != null:
			overrides += 1
			assert(mesh.name == "CitySignSupports02_ArtworkCarrier" and surface == 0)
			assert(mesh.mesh.surface_get_material(surface).resource_name == "sign_face")
			assert(override == material)

	return overrides


## Preserve the approved full box, including its intentional solid under-panel gap.
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
	assert((shape.shape as BoxShape3D).size.is_equal_approx(Vector3(1.6, 1.35, 0.4)))


## Exercise the actual saved variant's blocking centre and clear side/overhead rays.
func _check_queries(instance: Node3D) -> bool:
	var space := instance.get_world_3d().direct_space_state
	var hit := space.intersect_ray(
		PhysicsRayQueryParameters3D.create(Vector3(0, 0.7, 2), Vector3(0, 0.7, -2), 1)
	)
	assert(not hit.is_empty() and hit.collider == instance.get_node("Collision/Body"))
	assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(
		Vector3(0.9, 0.7, 2), Vector3(0.9, 0.7, -2), 1
	)).is_empty())
	assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(
		Vector3(0, 1.6, 2), Vector3(0, 1.6, -2), 1
	)).is_empty())
	return true
