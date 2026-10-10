extends "res://tools/asset_production/d09_storage_03/check.gd"
## Check linked crate arrangements; reuse family save/dependency and ActorMotion helpers read-only.

const CRATE := "res://scenes/prefabs/environment/d09_storage_04_crate.tscn"
const PAIR := "res://scenes/prefabs/environment/d09_storage_04_pair.tscn"
const TRIO := "res://scenes/prefabs/environment/d09_storage_04.tscn"
const CRATE_FIXTURE := "res://tools/asset_production/d09_storage_04/check_scene.tscn"
const CRATE_EVIDENCE := "res://docs/assets/production/d09_storage_04-evidence/validation.json"
const CRATE_MODEL := "res://art/models/environment/d09_storage_04/d09_storage_04.glb"
const CRATE_BOUNDS := AABB(Vector3(-.7, 0, -.7), Vector3(1.4, 1.05, 1.4))


## Normalize all owned scenes, inspect linked components and exercise saved collision variants.
func _run() -> void:
	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if "--normalize" in OS.get_cmdline_user_args():
		for path: String in [CRATE, PAIR, TRIO, CRATE_FIXTURE]:
			var before: String = FileAccess.get_sha256(path)
			_save_scene(path)
			var first: String = FileAccess.get_sha256(path)
			_save_scene(path)
			_require(first == FileAccess.get_sha256(path), "First roundtrip drift: " + path)
			_save_scene(path)
			_require(first == FileAccess.get_sha256(path), "Second roundtrip drift: " + path)
			if "--verify-stable" in OS.get_cmdline_user_args():
				_require(before == first, "Fresh-process identity drift: " + path)
		_report["save_reload_byte_stable"] = true
		_report["stable_roundtrips"] = 2
		_report["fresh_process_roundtrip_byte_stable"] = (
			"--verify-stable" in OS.get_cmdline_user_args()
		)

	_check_dependencies(CRATE_FIXTURE)
	_check_model()
	_require(_report.has("variants"), "Variant checks incomplete")
	await _check_physics()
	_require(_report.has("physics"), "Physics checks incomplete")
	if _failed:
		quit(1)
		return

	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CRATE_EVIDENCE))
	if data.has("godot") and not _report.has("save_reload_byte_stable"):
		for key: String in [
			"save_reload_byte_stable", "stable_roundtrips", "fresh_process_roundtrip_byte_stable",
		]:
			_report[key] = data["godot"].get(key, false)
	_report["engine"] = Engine.get_version_info()["string"]
	data["godot"] = _report
	var file: FileAccess = FileAccess.open(CRATE_EVIDENCE, FileAccess.WRITE)
	file.store_string(JSON.stringify(data, "\t") + "\n")
	file.close()
	print("D09_STORAGE_04_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Assert one source-backed mesh and solid envelope, then exact saved arrangement translations.
func _check_model() -> void:
	var packed: PackedScene = load(CRATE)
	var crate: Node3D = packed.instantiate()
	_check_crate(crate)
	crate.free()
	_check_arrangement(PAIR, [Vector3(-.74, 0, 0), Vector3(.74, 0, 0)],
		AABB(Vector3(-1.44, 0, -.7), Vector3(2.88, 1.05, 1.4)))
	_check_arrangement(TRIO, [Vector3(-.74, 0, 0), Vector3(.74, 0, 0), Vector3(-.74, 1.05, 0)],
		AABB(Vector3(-1.44, 0, -.7), Vector3(2.88, 2.1, 1.4)))
	_report["variants"] = {
		"crate": { "meshes": 1, "surfaces": 4, "boxes": 1, "size_m": [1.4, 1.05, 1.4] },
		"pair": { "meshes": 2, "surfaces": 8, "boxes": 2, "size_m": [2.88, 1.05, 1.4] },
		"trio": { "meshes": 3, "surfaces": 12, "boxes": 3, "size_m": [2.88, 2.1, 1.4] },
	}


## Inspect each reused component's ancestry, geometry, material state and deliberate collider.
func _check_crate(crate: Node3D) -> AABB:
	var model: Node3D = crate.get_node("Visuals/Model")
	_require(model.transform == Transform3D.IDENTITY, "Corrective model transform")
	_require(model.scene_file_path == CRATE_MODEL, "Unlinked GLB")
	var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	_require(meshes.size() == 1, "Crate mesh count")
	var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
	_require(mesh.visible and model.visible, "Imported render visibility")
	var bounds: AABB = mesh.transform * mesh.mesh.get_aabb()
	_require(bounds.position.distance_to(CRATE_BOUNDS.position) < .001, "Crate minimum")
	_require(bounds.size.distance_to(CRATE_BOUNDS.size) < .001, "Crate size")
	_require(mesh.mesh.get_surface_count() == 4, "Crate surface count")
	for surface: int in mesh.mesh.get_surface_count():
		var material: BaseMaterial3D = mesh.mesh.surface_get_material(surface)
		_require(material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED, "Transparency")
		_require(material.cull_mode == BaseMaterial3D.CULL_BACK, "Two-sided geometry")
	_require(crate.find_children("*", "CollisionObject3D", true, false).size() == 1,
		"One static collider per crate")
	var body: StaticBody3D = crate.get_node("Collision/Body")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Static-world filtering")
	_require(body.get_child_count() == 1, "One box per crate")
	_check_box(body.get_node("Shell"), Vector3(1.4, 1.05, 1.4), Vector3(0, .525, 0))
	return bounds


## Confirm saved prefab reuse and compound silhouette without filling the stepped upper notch.
func _check_arrangement(path: String, positions: Array[Vector3], expected: AABB) -> void:
	var packed: PackedScene = load(path)
	var group: Node3D = packed.instantiate()
	_require(group.transform == Transform3D.IDENTITY, "Group root correction")
	_require(group.get_child_count() == positions.size(), "Unexpected arrangement members")
	var bounds: AABB
	for index: int in positions.size():
		var crate: Node3D = group.get_child(index)
		_require(crate.scene_file_path == CRATE, "Arrangement duplicated crate geometry")
		_require(crate.position.is_equal_approx(positions[index]), "Changed crate position")
		_require(crate.basis == Basis.IDENTITY, "Changed crate rotation/scale")
		var local: AABB = crate.transform * _check_crate(crate)
		bounds = local if index == 0 else bounds.merge(local)
	_require(bounds.position.distance_to(expected.position) < .001, "Arrangement minimum")
	_require(bounds.size.distance_to(expected.size) < .001, "Arrangement bounds")
	group.free()


## Check face corners, retained seam/notch voids, car casts and authority/replay contact routes.
func _check_physics() -> void:
	var packed: PackedScene = load(CRATE_FIXTURE)
	var fixture: Node3D = packed.instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	for x: float in [-1.4, -.74, 1.4, 4.6, 5.26, 7.4, 11.34, 12.0, 12.66]:
		_require(_ray_blocked(space, x, .5), "Missing front/corner solid")
	for x: float in [0.0, 6.0]:
		_require(not _ray_blocked(space, x, .5), "Invisible blocker in 0.08 m seam")
	_require(_ray_blocked(space, -.74, 1.5), "Missing upper crate collider")
	_require(not _ray_blocked(space, .74, 1.5), "Invisible upper-right notch blocker")
	_require(not _ray_blocked(space, 0, 2.2), "Above-trio obstruction")
	_require(not _ray_blocked(space, 6, 1.2), "Above-pair obstruction")
	_require(not _ray_blocked(space, 12, 1.2), "Above-crate obstruction")
	var cars: Dictionary = _check_car_envelope(space)
	var results: Array[Dictionary] = []
	for index: int in 3:
		var contact_x: float = [-.74, 5.26, 12.0][index]
		var bypass_x: float = [1.94, 7.94, 13.2][index]
		results.append(await _check_actor_routes(fixture.get_node("Actor"), contact_x, bypass_x))
	# The narrow visual gap stays a gap for rays but must not admit an actor capsule.
	var seam: Vector3 = await _walk(fixture.get_node("Actor"), 0, ActorMotion.StepMode.AUTHORITY)
	_require(seam.z < -1.04 and seam.z > -1.08, "Actor penetrated narrow crate seam")
	_report["physics"] = {
		"nine_front_corner_rays_blocked": true, "seam_rays_clear": true,
		"stepped_notch_and_overhead_clear": true, "upper_crate_blocked": true,
		"actor_capsule_radius_m": .35, "actor_capsule_height_m": 1.8,
		"ticks_per_case_per_mode": WALK_TICKS, "authority_replay_equal": true,
		"variants": results, "seam_actor_stop_m": [seam.x, seam.y, seam.z],
		"vehicle_driving_network_transport_and_placement": "not tested",
	}
	_report["physics"].merge(cars)
	fixture.free()


## Query a known front plane independently of the render mesh.
func _ray_blocked(space: PhysicsDirectSpaceState3D, x: float, height: float) -> bool:
	var query := PhysicsRayQueryParameters3D.create(
		Vector3(x, height, -8),
		Vector3(x, height, 8),
		1,
	)
	var hit: Dictionary = space.intersect_ray(query)
	if hit.is_empty():
		return false
	_require(absf(hit["position"].z + .7) < .001, "Incorrect crate front plane")
	return true


## Compare production movement on a clear route and contact plane for both simulation modes.
func _check_actor_routes(actor: ActorMotion, contact_x: float, bypass_x: float) -> Dictionary:
	var contacts: Array[Vector3] = []
	var bypasses: Array[Vector3] = []
	for mode: ActorMotion.StepMode in [ActorMotion.StepMode.AUTHORITY, ActorMotion.StepMode.REPLAY]:
		contacts.append(await _walk(actor, contact_x, mode))
		bypasses.append(await _walk(actor, bypass_x, mode))
	_require(contacts[0].z <= -1.05 and contacts[0].z >= -1.08, "Crate contact plane/gap")
	_require(bypasses[0].distance_to(Vector3(bypass_x, 0, 8)) < .015, "Crate bypass blocked")
	_require(contacts[0].is_equal_approx(contacts[1]), "Contact authority/replay mismatch")
	_require(bypasses[0].is_equal_approx(bypasses[1]), "Bypass authority/replay mismatch")
	return {
		"contact_stop_m": [contacts[0].x, contacts[0].y, contacts[0].z],
		"bypass_end_m": [bypasses[0].x, bypasses[0].y, bypasses[0].z],
	}


## Cast a provisional car-sized box against all variants and through clear apron offsets.
func _check_car_envelope(space: PhysicsDirectSpaceState3D) -> Dictionary:
	var shape := BoxShape3D.new()
	shape.size = Vector3(1.8, 1.5, 4.4)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.collision_mask = 1
	query.motion = Vector3(0, 0, 20)
	var blocked: Array[float] = []
	var bypass: Array[float] = []
	for x: float in [0.0, 6.0, 12.0]:
		query.transform.origin = Vector3(x, .85, -10)
		var result: PackedFloat32Array = space.cast_motion(query)
		_require(result[0] > .35 and result[0] < .36, "Car cast missed crate front")
		blocked.append(result[0])
		query.transform.origin.x = x + 2.5
		result = space.cast_motion(query)
		_require(result[0] == 1.0, "Car bypass blocked")
		bypass.append(result[0])
	return {
		"car_box_dimensions_m": [1.8, 1.5, 4.4],
		"car_front_cast_safe_fractions": blocked, "car_bypass_safe_fractions": bypass,
	}
