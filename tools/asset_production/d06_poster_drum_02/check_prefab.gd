extends SceneTree

const PREFAB := "res://scenes/prefabs/environment/d06_poster_drum_02.tscn"
const MODEL := "res://art/models/environment/d06_poster_drum_02/d06_poster_drum_02.glb"
const EVIDENCE := "res://docs/assets/production/d06_poster_drum_02-evidence/validation.json"


## Run with --headless --editor so ResourceSaver retains scene and dependency UIDs.
func _initialize() -> void:
	assert(Engine.is_editor_hint())
	create_timer(30).timeout.connect(_deadline)
	call_deferred("_wait_for_editor")


## Let editor startup finish before saving resources and requesting a clean exit.
func _wait_for_editor() -> void:
	await create_timer(3).timeout
	# Initial scan completion does not reliably emit filesystem_changed in CLI editor mode.
	while EditorInterface.get_resource_filesystem().is_scanning():
		await process_frame  # gdstyle:ignore=quality/await-in-loop

	_check()


## Fail closed if an assertion interrupts the asynchronous check.
func _deadline() -> void:
	push_error("Poster drum validation did not complete within 30 seconds")
	quit(1)


## Check the complete prefab and retain its bounded engine evidence.
func _check() -> void:
	var packed := load(PREFAB) as PackedScene
	assert(packed != null)
	var instance := packed.instantiate() as Node3D
	root.add_child(instance)
	_check_model(instance)
	_check_collision(instance)
	await physics_frame
	await physics_frame
	_check_queries(instance)
	_roundtrip(instance)
	assert(ResourceLoader.get_resource_uid(PREFAB) != ResourceUID.INVALID_ID)
	assert(ResourceLoader.get_resource_uid(MODEL) != ResourceUID.INVALID_ID)
	_write_report()
	print("PASS: linked prefab, bounds, collision rays, UIDs and stable save/reload")
	quit(0)


## Verify that the saved visual is an unchanged imported model with the approved bounds.
func _check_model(instance: Node3D) -> void:
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(model.scene_file_path == MODEL)
	assert(model.transform == Transform3D.IDENTITY)
	assert(instance.transform == Transform3D.IDENTITY)
	var bounds := AABB()
	var first := true
	var surfaces := 0
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	assert(meshes.size() == 2)
	for child: MeshInstance3D in meshes:
		assert(child.transform == Transform3D.IDENTITY)
		assert(child.mesh.resource_path.begins_with(MODEL))
		var mesh_bounds := child.get_aabb()
		bounds = mesh_bounds if first else bounds.merge(mesh_bounds)
		first = false
		surfaces += child.mesh.get_surface_count()

	assert(surfaces == 4)
	assert(bounds.position.distance_to(Vector3(-0.45, 0, -0.45)) < 0.001)
	assert(bounds.size.distance_to(Vector3(0.9, 1.53, 0.9)) < 0.001)


## Verify the separate, simple static-world collision envelope and ground datum.
func _check_collision(instance: Node3D) -> void:
	var body := instance.get_node("Collision/Body") as StaticBody3D
	var shape_node := body.get_node("Shape") as CollisionShape3D
	var cylinder := shape_node.shape as CylinderShape3D
	assert(body.collision_layer == 1 and body.collision_mask == 0)
	assert(is_equal_approx(cylinder.radius, 0.45))
	assert(is_equal_approx(cylinder.height, 1.53))
	assert(shape_node.position.is_equal_approx(Vector3(0, 0.765, 0)))


## Exercise actual physics rays for the solid center, clear side, and clear overhead.
func _check_queries(instance: Node3D) -> void:
	var space := instance.get_world_3d().direct_space_state
	var hit := space.intersect_ray(
		PhysicsRayQueryParameters3D.create(Vector3(0, 0.7, 2), Vector3(0, 0.7, -2), 1)
	)
	assert(not hit.is_empty() and hit.collider == instance.get_node("Collision/Body"))
	var cap_hit := space.intersect_ray(
		PhysicsRayQueryParameters3D.create(Vector3(0, 1.49, 2), Vector3(0, 1.49, -2), 1)
	)
	assert(not cap_hit.is_empty() and cap_hit.collider == instance.get_node("Collision/Body"))
	var clear := space.intersect_ray(
		PhysicsRayQueryParameters3D.create(Vector3(0.6, 0.7, 2), Vector3(0.6, 0.7, -2), 1)
	)
	assert(clear.is_empty())
	var above := space.intersect_ray(
		PhysicsRayQueryParameters3D.create(Vector3(0, 1.6, 2), Vector3(0, 1.6, -2), 1)
	)
	assert(above.is_empty())


## Pack, save, reopen, and resave without losing the imported instance or identities.
func _roundtrip(instance: Node3D) -> void:
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, PREFAB) == OK)
	instance.free()
	var normalized := FileAccess.get_file_as_bytes(PREFAB)
	var reopened := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	assert(reopened is PackedScene)
	var second := reopened.instantiate() as Node3D
	_check_model(second)
	_check_collision(second)
	saved = PackedScene.new()
	assert(saved.pack(second) == OK)
	assert(ResourceSaver.save(saved, PREFAB) == OK)
	second.free()
	assert(normalized == FileAccess.get_file_as_bytes(PREFAB))


## Add engine results to the source/export measurements without claiming gameplay acceptance.
func _write_report() -> void:
	var report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(EVIDENCE))
	report["godot"] = {
		"version": Engine.get_version_info().string,
		"linked_model_identity": true,
		"mesh_count": 2,
		"surfaces": 4,
		"bounds_match": true,
		"save_reload_byte_stable": true,
		"dependency_uids_resolve": true,
		"collision": { "radius_m": 0.45, "height_m": 1.53, "layer": 1, "mask": 0 },
		"ray_queries": {
			"center_hit": true, "cap_hit": true, "side_clear": true, "above_clear": true,
		},
	}
	var output := FileAccess.open(EVIDENCE, FileAccess.WRITE)
	output.store_string(JSON.stringify(report, "  ") + "\n")
	output.close()
