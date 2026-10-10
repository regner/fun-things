extends SceneTree

const PREFAB := "res://scenes/prefabs/environment/city_sign_supports_02.tscn"
const MODEL := "res://art/models/environment/city_sign_supports_02/city_sign_supports_02.glb"
const PLAYER := "res://scenes/entities/player.tscn"
const MOTION_TICKS := 60
const CHECK_DEADLINE_SECONDS := 30.0
const EDITOR_SETTLE_SECONDS := 3.0
const EVIDENCE := "res://docs/assets/production/city_sign_supports_02-evidence/validation.json"

var _movement_results: Dictionary = {}


## Normalize resources in editor mode; exercise production scripts in a runtime process.
func _initialize() -> void:
	create_timer(CHECK_DEADLINE_SECONDS).timeout.connect(_deadline)
	if Engine.is_editor_hint():
		call_deferred("_wait_for_editor")
	else:
		call_deferred("_check")


## Let editor startup finish before saving resources and requesting a clean exit.
func _wait_for_editor() -> void:
	await create_timer(EDITOR_SETTLE_SECONDS).timeout
	# Initial scan completion does not reliably emit filesystem_changed in CLI editor mode.
	while EditorInterface.get_resource_filesystem().is_scanning():
		await process_frame  # gdstyle:ignore=quality/await-in-loop

	_check()


## Fail closed if an assertion interrupts the asynchronous check.
func _deadline() -> void:
	push_error("Low panel validation did not complete within 30 seconds")
	quit(1)


## Check the complete prefab and retain its bounded engine evidence.
func _check() -> void:
	var packed := load(PREFAB) as PackedScene
	assert(packed != null)
	var instance := packed.instantiate() as Node3D
	root.add_child(instance)
	assert(_check_model(instance))
	assert(_check_collision(instance))
	await physics_frame
	await physics_frame
	assert(_check_queries(instance))
	if Engine.is_editor_hint():
		assert(_roundtrip(instance))
	else:
		assert(await _check_movement())
		instance.free()

	assert(ResourceLoader.get_resource_uid(PREFAB) != ResourceUID.INVALID_ID)
	assert(ResourceLoader.get_resource_uid(MODEL) != ResourceUID.INVALID_ID)
	_write_report()
	print("PASS: linked prefab, bounds, collision rays, UIDs and stable save/reload")
	quit(0)


## Verify that the saved visual is an unchanged imported model with the approved bounds.
func _check_model(instance: Node3D) -> bool:
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

	assert(surfaces == 5)
	assert(bounds.position.distance_to(Vector3(-0.8, 0, -0.2)) < 0.001)
	assert(bounds.size.distance_to(Vector3(1.6, 1.35, 0.4)) < 0.001)
	return true


## Verify the separate, simple static-world collision envelope and ground datum.
func _check_collision(instance: Node3D) -> bool:
	var body := instance.get_node("Collision/Body") as StaticBody3D
	var shape_node := body.get_node("Shape") as CollisionShape3D
	var box := shape_node.shape as BoxShape3D
	assert(body.collision_layer == 1 and body.collision_mask == 0)
	assert(box.size.is_equal_approx(Vector3(1.6, 1.35, 0.4)))
	assert(shape_node.position.is_equal_approx(Vector3(0, 0.675, 0)))
	return true


## Exercise actual physics rays for the solid center, clear side, and clear overhead.
func _check_queries(instance: Node3D) -> bool:
	var space := instance.get_world_3d().direct_space_state
	var hit := space.intersect_ray(
		PhysicsRayQueryParameters3D.create(Vector3(0, 0.7, 2), Vector3(0, 0.7, -2), 1)
	)
	assert(not hit.is_empty() and hit.collider == instance.get_node("Collision/Body"))
	var clear := space.intersect_ray(
		PhysicsRayQueryParameters3D.create(Vector3(0.9, 0.7, 2), Vector3(0.9, 0.7, -2), 1)
	)
	assert(clear.is_empty())
	var above := space.intersect_ray(
		PhysicsRayQueryParameters3D.create(Vector3(0, 1.6, 2), Vector3(0, 1.6, -2), 1)
	)
	assert(above.is_empty())
	return true


## Exercise the production player's shape and motion API in authority and replay modes.
func _check_movement() -> bool:
	var player_scene := load(PLAYER) as PackedScene
	var actor := player_scene.instantiate() as ActorMotion
	root.add_child(actor)
	var shape := (actor.get_node("Collision") as CollisionShape3D).shape as CapsuleShape3D
	assert(is_equal_approx(shape.radius, 0.35) and is_equal_approx(shape.height, 1.8))
	var authority_stop := await _walk(actor, 0.0, ActorMotion.StepMode.AUTHORITY)
	assert(authority_stop.z > 0.54 and authority_stop.z < 0.57)
	var replay_stop := await _walk(actor, 0.0, ActorMotion.StepMode.REPLAY)
	assert(authority_stop.distance_to(replay_stop) < 0.001)
	var bypass := await _walk(actor, 1.3, ActorMotion.StepMode.AUTHORITY)
	assert(bypass.distance_to(Vector3(1.3, 0, -3)) < 0.001)
	_movement_results = {
		"authority_stop_z_m": authority_stop.z,
		"replay_stop_z_m": replay_stop.z,
		"bypass_end_z_m": bypass.z,
		"authority_replay_equivalent": true,
		"capsule_radius_m": 0.35,
		"capsule_height_m": 1.8,
		"ticks_per_case": MOTION_TICKS,
	}
	actor.free()
	return true


## Feed valid fixed-step foot commands while preserving independent endpoint assertions.
func _walk(actor: ActorMotion, x: float, mode: ActorMotion.StepMode) -> Vector3:
	actor.position = Vector3(x, 0, 2)
	actor.neutralize()
	await physics_frame
	var command := FootCommand.new(1, 0, Vector2(0, -1), 0.0, false, false)
	for _tick in range(MOTION_TICKS):
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		assert(actor.step(command, 1.0 / float(Engine.physics_ticks_per_second), mode))

	return actor.global_position


## Pack, save, reopen, and resave without losing the imported instance or identities.
func _roundtrip(instance: Node3D) -> bool:
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, PREFAB) == OK)
	instance.free()
	var normalized := FileAccess.get_file_as_bytes(PREFAB)
	var reopened := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	assert(reopened is PackedScene)
	var second := reopened.instantiate() as Node3D
	assert(_check_model(second))
	assert(_check_collision(second))
	saved = PackedScene.new()
	assert(saved.pack(second) == OK)
	assert(ResourceSaver.save(saved, PREFAB) == OK)
	second.free()
	assert(normalized == FileAccess.get_file_as_bytes(PREFAB))
	return true


## Add engine results to the source/export measurements without claiming gameplay acceptance.
func _write_report() -> void:
	var report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(EVIDENCE))
	var prior: Dictionary = report.get("godot", {})
	var stable: bool = Engine.is_editor_hint() or prior.get("save_reload_byte_stable", false)
	if _movement_results.is_empty():
		_movement_results = prior.get("production_actor_motion", {})

	report["godot"] = {
		"version": Engine.get_version_info().string,
		"linked_model_identity": true,
		"mesh_count": 2,
		"surfaces": 5,
		"bounds_match": true,
		"save_reload_byte_stable": stable,
		"dependency_uids_resolve": true,
		"collision": { "size_m": [1.6, 1.35, 0.4], "layer": 1, "mask": 0 },
		"production_actor_motion": _movement_results,
		"ray_queries": { "center_hit": true, "side_clear": true, "above_clear": true },
	}
	var output := FileAccess.open(EVIDENCE, FileAccess.WRITE)
	output.store_string(JSON.stringify(report, "  ") + "\n")
	output.close()
