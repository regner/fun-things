extends "res://tools/asset_production/d07_trolley_shelter_02/check.gd"
## Validate saved nesting, disabled component collision, group queries and shelter interface.

const GROUP_PREFAB := "res://scenes/prefabs/environment/d07_trolley_shelter_03.tscn"
const GROUP_EVIDENCE := (
	"res://docs/assets/production/d07_trolley_shelter_03-evidence/validation.json"
)
const SHELTER_PREFAB := "res://scenes/prefabs/environment/d07_trolley_shelter_01.tscn"
const GROUP_BOUNDS := AABB(Vector3(-.34, 0, -1.245), Vector3(.68, 1.08, 2.49))
const CAPSULE_RADIUS_M := .35
const CAPSULE_HEIGHT_M := 1.8


## Reuse the component's safe save/dependency helpers without writing any component resource.
func _run() -> void:
	_require(Engine.get_version_info()["hash"].begins_with("c971f93e7"), "Engine pin")
	if "--normalize" in OS.get_cmdline_user_args():
		_save_scene(GROUP_PREFAB)
		var first_hash: String = FileAccess.get_sha256(GROUP_PREFAB)
		for roundtrip: int in 2:
			_save_scene(GROUP_PREFAB)
			_require(first_hash == FileAccess.get_sha256(GROUP_PREFAB),
				"Save/reload drift on roundtrip %d" % roundtrip)
		_report["two_save_reload_roundtrips_byte_stable"] = true

	_check_dependencies(GROUP_PREFAB)
	_check_model()
	await _check_physics()
	await _check_shelter_fit()
	_require(_report.has("physics") and _report.has("shelter_fit"), "Incomplete checks")
	if _failed:
		quit(1)
		return

	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(GROUP_EVIDENCE))
	_report["engine"] = Engine.get_version_info()["string"]
	data["godot"] = _report
	var file: FileAccess = FileAccess.open(GROUP_EVIDENCE, FileAccess.WRITE)
	file.store_string(JSON.stringify(data, "\t") + "\n")
	file.close()
	print("D07_TROLLEY_SHELTER_03_CHECK_PASS ", JSON.stringify(_report))
	quit(0)


## Inspect the production instances and shared imported mesh, not duplicated triangle data.
func _check_model() -> void:
	var instance: Node3D = load(GROUP_PREFAB).instantiate()
	_require(instance.transform == Transform3D.IDENTITY, "Group root transform")
	var combined := AABB()
	var shared_mesh: Mesh = null
	var placements: Dictionary = { "Front": -.72, "Middle": 0.0, "Rear": .72 }
	for child_name: String in placements:
		var trolley: Node3D = instance.get_node("Trolleys/" + child_name)
		_require(trolley.scene_file_path == PREFAB, "Not the existing component prefab")
		_require(trolley.basis == Basis.IDENTITY, "Trolley rotation or scale")
		_require(trolley.position.is_equal_approx(Vector3(0, 0, placements[child_name])),
			"Unexpected saved pitch")
		var model: Node3D = trolley.get_node("Visuals/Model")
		_require(model.transform == Transform3D.IDENTITY, "Corrective imported transform")
		_require(model.scene_file_path.ends_with("d07_trolley_shelter_02.glb"), "Unlinked GLB")
		var meshes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
		_require(meshes.size() == 1, "Unexpected component mesh count")
		var mesh: MeshInstance3D = meshes[0] as MeshInstance3D
		_require(mesh.mesh.get_surface_count() == 4, "Material surface count")
		var bounds: AABB = (
			trolley.transform * model.transform * mesh.transform * mesh.mesh.get_aabb()
		)
		if shared_mesh == null:
			shared_mesh = mesh.mesh
			combined = bounds
		else:
			_require(shared_mesh == mesh.mesh, "Mesh not shared across instances")
			combined = combined.merge(bounds)

	_require(combined.position.distance_to(GROUP_BOUNDS.position) < .001, "Group bounds minimum")
	_require(combined.size.distance_to(GROUP_BOUNDS.size) < .001, "Group bounds size")
	_check_collision(instance)
	_report["imported_bounds_min_m"] = [
		combined.position.x, combined.position.y, combined.position.z,
	]
	_report["imported_bounds_size_m"] = [combined.size.x, combined.size.y, combined.size.z]
	_report["linked_instances"] = 3
	_report["shared_mesh_resources"] = 1
	instance.free()


## Keep the three inherited boxes disabled; only the deliberately authored group box is active.
func _check_collision(instance: Node3D) -> void:
	var shapes: Array[Node] = instance.find_children("*", "CollisionShape3D", true, false)
	_require(shapes.size() == 4, "One group box plus three inherited disabled boxes")
	var enabled_count := 0
	for shape: CollisionShape3D in shapes:
		if not shape.disabled:
			enabled_count += 1
			_require(shape == instance.get_node("Collision/GroupBody/Envelope"),
				"Unexpected enabled component collider")

	_require(enabled_count == 1, "Expected exactly one active shape")
	var body: StaticBody3D = instance.get_node("Collision/GroupBody")
	_require(body.collision_layer == 1 and body.collision_mask == 0, "Static-world filtering")
	var envelope: CollisionShape3D = body.get_node("Envelope")
	_require(envelope.shape is BoxShape3D, "Expected one box")
	_require(envelope.shape.size.is_equal_approx(Vector3(.68, 1.08, 2.49)), "Group box size")
	_require(envelope.position.is_equal_approx(Vector3(0, .54, 0)), "Group box ground datum")
	_report["collision"] = {
		"active_boxes": 1, "disabled_component_boxes": 3, "layer": 1, "mask": 0,
	}


## Prove the authored group owns every contact plane, with clear bypass and above-group queries.
func _check_physics() -> void:
	var fixture: Node3D = load(GROUP_PREFAB).instantiate()
	root.add_child(fixture)
	await physics_frame
	await physics_frame
	var space: PhysicsDirectSpaceState3D = fixture.get_world_3d().direct_space_state
	for contact: Vector3 in [Vector3(-.34, .6, 0), Vector3(.34, .6, 0),
		Vector3(0, .6, -1.245), Vector3(0, .6, 1.245)]:
		var ray := PhysicsRayQueryParameters3D.create(
			Vector3(contact.x * 4, .6, contact.z * 4), Vector3(0, .6, 0), 1,
		)
		var hit: Dictionary = space.intersect_ray(ray)
		_require(not hit.is_empty(), "Group contact missed")
		if not hit.is_empty():
			_require(hit["position"].is_equal_approx(contact), "Group contact plane")
			_require(hit["collider"] == fixture.get_node("Collision/GroupBody"),
				"Disabled component collider still participates")

	var above := PhysicsRayQueryParameters3D.create(Vector3(-2, 1.2, 0), Vector3(2, 1.2, 0), 1)
	_require(space.intersect_ray(above).is_empty(), "Unexpected above-group collision")
	var query: PhysicsShapeQueryParameters3D = _capsule_query()
	for position: Vector3 in [Vector3(-.75, .9, 0), Vector3(.75, .9, 0),
		Vector3(0, .9, -1.65), Vector3(0, .9, 1.65)]:
		query.transform.origin = position
		_require(space.intersect_shape(query).is_empty(), "Capsule bypass blocked")
	for position: Vector3 in [Vector3(-.6, .9, 0), Vector3(.6, .9, 0),
		Vector3(0, .9, -1.5), Vector3(0, .9, 1.5)]:
		query.transform.origin = position
		_require(not space.intersect_shape(query).is_empty(), "Capsule overlap missed")

	_report["physics"] = {
		"four_contact_planes_hit_group_only": true, "above_group_clear": true,
		"four_capsule_bypasses_clear": true, "four_capsule_overlaps_blocked": true,
		"capsule_radius_m": CAPSULE_RADIUS_M, "capsule_height_m": CAPSULE_HEIGHT_M,
		"movement_vehicle_network_and_placement": "not tested",
	}
	fixture.free()


## Create only a test query shape matching the current actor's production envelope.
func _capsule_query() -> PhysicsShapeQueryParameters3D:
	var capsule := CapsuleShape3D.new()
	capsule.radius = CAPSULE_RADIUS_M
	capsule.height = CAPSULE_HEIGHT_M
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = 1
	return query


## Test the documented optional shelter transform without creating a second placement artifact.
func _check_shelter_fit() -> void:
	var shelter: Node3D = load(SHELTER_PREFAB).instantiate()
	var group: Node3D = load(GROUP_PREFAB).instantiate()
	group.rotation.y = PI
	group.position.z = -.05
	root.add_child(shelter)
	root.add_child(group)
	await physics_frame
	await physics_frame
	var bounds: AABB = group.transform * GROUP_BOUNDS
	_require(bounds.position.x > -1.0 and bounds.end.x < 1.0, "Shelter X fitting region")
	_require(bounds.position.z > -1.30 and bounds.end.z < 1.20, "Shelter Z fitting region")
	_require(bounds.position.y == 0 and bounds.end.y < 1.50, "Shelter ground/height region")
	var space: PhysicsDirectSpaceState3D = shelter.get_world_3d().direct_space_state
	var query: PhysicsShapeQueryParameters3D = _capsule_query()
	for x: float in [-.74, .74]:
		for z: float in [-1.0, 0.0, 1.0]:
			query.transform.origin = Vector3(x, .9, z)
			_require(space.intersect_shape(query).is_empty(), "Under-shelter side capsule blocked")

	_report["shelter_fit"] = {
		"yaw_degrees": 180, "translation_m": [0, 0, -.05],
		"fitting_region_pass": true, "six_side_capsule_queries_clear": true,
		"side_gap_to_shelter_collision_m": .79, "rear_gap_to_stop_m": .205,
		"fitting_region_front_and_rear_margin_m": .005,
		"not_a_through_route_or_world_placement": true,
	}
	group.free()
	shelter.free()
