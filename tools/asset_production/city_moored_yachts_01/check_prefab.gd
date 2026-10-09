extends SceneTree

const PREFAB := "res://scenes/prefabs/environment/city_moored_yachts_01.tscn"
const MODEL := "res://art/models/environment/city_moored_yachts_01/city_moored_yachts_01.glb"
const EVIDENCE := "res://docs/assets/production/city_moored_yachts_01-evidence/validation.json"
const PLAYER := preload("res://scenes/entities/player.tscn")
const STEP_COUNT := 120

var _movement_results: Array[Dictionary] = []


## Normalize saved resources with the pinned headless editor, never a live editor session.
func _initialize() -> void:
	create_timer(60).timeout.connect(_deadline)
	if Engine.is_editor_hint():
		call_deferred("_wait_for_editor")
	else:
		call_deferred("_check")


## Await the CLI editor's filesystem registration before checking new imports and UIDs.
func _wait_for_editor() -> void:
	await create_timer(3).timeout
	while EditorInterface.get_resource_filesystem().is_scanning():
		await process_frame  # gdstyle:ignore=quality/await-in-loop

	_check()


## Fail closed if an asynchronous assertion interrupts the checks.
func _deadline() -> void:
	push_error("Yacht prefab validation did not finish within 60 seconds")
	quit(1)


## Validate linked geometry, physical queries, production motion and scene roundtrip.
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
		await _check_motion()
		# An interrupted asynchronous child must never produce a successful receipt.
		assert(_movement_results.size() == 6)
		for index in range(3):
			assert(_movement_results[index].end == _movement_results[index + 3].end)
		instance.free()

	assert(ResourceLoader.get_resource_uid(PREFAB) != ResourceUID.INVALID_ID)
	assert(ResourceLoader.get_resource_uid(MODEL) != ResourceUID.INVALID_ID)
	_write_report()
	print("PASS: yacht prefab checks; editor=", Engine.is_editor_hint(),
		"; completed ActorMotion cases=", _movement_results.size())
	quit(0)


## Inspect imported ancestry, identity transforms and independent visual bounds.
func _check_model(instance: Node3D) -> bool:
	var model := instance.get_node("Visuals/Model") as Node3D
	assert(instance.transform == Transform3D.IDENTITY)
	assert(model.scene_file_path == MODEL and model.transform == Transform3D.IDENTITY)
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	assert(meshes.size() == 1)
	var mesh := meshes[0] as MeshInstance3D
	assert(mesh.transform == Transform3D.IDENTITY and mesh.mesh.resource_path.begins_with(MODEL))
	assert(mesh.mesh.get_surface_count() == 7)
	assert(mesh.get_aabb().position.distance_to(Vector3(-1.9, -1.0, -6.212152)) < 0.001)
	assert(mesh.get_aabb().size.distance_to(Vector3(3.8, 4.1, 12.412152)) < 0.001)
	for index in range(7):
		var material := mesh.mesh.surface_get_material(index) as StandardMaterial3D
		assert(material != null)
		assert(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED)
		assert(material.cull_mode == BaseMaterial3D.CULL_BACK)

	return true


## Require only the three deliberately conservative above-water static blocking boxes.
func _check_collision(instance: Node3D) -> bool:
	var body := instance.get_node("Collision/Body") as StaticBody3D
	assert(body.collision_layer == 1 and body.collision_mask == 0)
	assert(body.get_child_count() == 3)
	var sizes := [Vector3(3.6, 1.25, 9.5), Vector3(2.5, 1.45, 2.92), Vector3(2.7, 1.45, 4.75)]
	var positions := [Vector3(0, 0.625, 1.45), Vector3(0, 0.725, -4.76), Vector3(0, 1.975, 0.2)]
	for index in range(3):
		var node := body.get_child(index) as CollisionShape3D
		var shape := node.shape as BoxShape3D
		assert(shape != null and shape.size.is_equal_approx(sizes[index]))
		assert(node.position.is_equal_approx(positions[index]))
		assert(not node.disabled)

	return true


## Exercise shot-like rays and a swept projectile sphere through the actual world API.
func _check_queries(instance: Node3D) -> bool:
	var space := instance.get_world_3d().direct_space_state
	var body := instance.get_node("Collision/Body")
	for height in [0.6, 2.0]:
		var hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(
			Vector3(4, height, 0), Vector3(-4, height, 0), 1
		))
		assert(not hit.is_empty() and hit.collider == body)

	for points in [
		[Vector3(4, 3.2, 0), Vector3(-4, 3.2, 0)],
		[Vector3(4, -0.5, 0), Vector3(-4, -0.5, 0)],
		[Vector3(4, 2.2, -4.5), Vector3(-4, 2.2, -4.5)],
		[Vector3(2.1, 0.6, -8), Vector3(2.1, 0.6, 8)],
	]:
		var ray := PhysicsRayQueryParameters3D.create(points[0], points[1], 1)
		assert(space.intersect_ray(ray).is_empty())

	var projectile := SphereShape3D.new()
	projectile.radius = 0.10
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = projectile
	query.collision_mask = 1
	query.transform.origin = Vector3(4, 0.6, 0)
	query.motion = Vector3(-8, 0, 0)
	var fractions := space.cast_motion(query)
	assert(fractions[0] > 0.24 and fractions[0] < 0.28)
	return true


## Replay identical held commands in authority and prediction modes using the saved player.
func _check_motion() -> void:
	await _check_mode(ActorMotion.StepMode.AUTHORITY)
	await _check_mode(ActorMotion.StepMode.REPLAY)


## Run the same bounded contact and bypass scenarios for one simulation mode.
func _check_mode(mode: ActorMotion.StepMode) -> void:
	await _move_case("hull_stop", Vector3(4, 0.55, 0), Vector2.LEFT, mode)
	await _move_case("bow_stop", Vector3(0, 0.55, -9), Vector2.DOWN, mode)
	await _move_case("clear_bypass", Vector3(4, 0.55, 7.5), Vector2.LEFT, mode)


## Assert contact and clear travel against fixed independent expectations, without boarding.
func _move_case(label: String, start: Vector3, move: Vector2, mode: ActorMotion.StepMode) -> void:
	var actor := PLAYER.instantiate() as ActorMotion
	assert(actor != null)
	actor.position = start
	root.add_child(actor)
	var fixed_delta := 1.0 / float(Engine.physics_ticks_per_second)
	for tick in range(STEP_COUNT):
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		# One fresh intent per test tick matches the production immutable-command contract.
		var command := FootCommand.new(  # gdstyle:ignore=quality/allocation-in-loop
			tick + 1, tick, move, 0.0, false, false
		)
		assert(actor.step(command, fixed_delta, mode))

	var end := actor.global_position
	match label:
		"hull_stop":
			assert(end.x > 2.14 and end.x < 2.17)
		"bow_stop":
			assert(end.z > -6.59 and end.z < -6.55)
		"clear_bypass":
			assert(absf(end.x + 6.0) < 0.005)

	assert(absf(end.y - 0.55) < 0.001)
	_movement_results.append({ "case": label, "mode": mode, "end": [end.x, end.y, end.z] })
	actor.free()


## Save, reopen and resave while preserving the imported model and normalized identities.
func _roundtrip(instance: Node3D) -> bool:
	var saved := PackedScene.new()
	assert(saved.pack(instance) == OK)
	assert(ResourceSaver.save(saved, PREFAB) == OK)
	instance.free()
	var normalized := FileAccess.get_file_as_bytes(PREFAB)
	var reopened := ResourceLoader.load(PREFAB, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	var second := (reopened as PackedScene).instantiate() as Node3D
	assert(_check_model(second))
	assert(_check_collision(second))
	saved = PackedScene.new()
	assert(saved.pack(second) == OK)
	assert(ResourceSaver.save(saved, PREFAB) == OK)
	second.free()
	assert(normalized == FileAccess.get_file_as_bytes(PREFAB))
	return true


## Extend the source receipt with bounded physics evidence, not world or transport acceptance.
func _write_report() -> void:
	var report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(EVIDENCE))
	var engine: Dictionary = report.get("godot", {})
	engine.merge({
		"version": Engine.get_version_info().string,
		"linked_model_identity": true,
		"meshes": 1,
		"surfaces": 7,
		"bounds_match": true,
		"dependency_uids_resolve": true,
		"collision": { "boxes": 3, "layer": 1, "mask": 0, "waterline_base_m": 0 },
		"queries": { "hull_and_cabin_rays_blocked": true, "projectile_sweep_blocked": true,
			"overhead_underwater_bow_rail_and_side_clear": true },
		"scope": "Saved player ActorMotion authority/replay; no transport or weapons-system proof",
	}, true)
	if Engine.is_editor_hint():
		engine["save_reload_byte_stable"] = true
	else:
		engine["production_actor_motion"] = _movement_results
		engine["authority_replay_endpoints_identical"] = true

	report["godot"] = engine
	var output := FileAccess.open(EVIDENCE, FileAccess.WRITE)
	output.store_string(JSON.stringify(report, "  ") + "\n")
	output.close()
