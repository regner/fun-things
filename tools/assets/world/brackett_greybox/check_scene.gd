extends SceneTree
## Checks saved greybox imports, replacement identities and provisional physics queries.

const BASE: String = "res://scenes/world/brackett_greybox/"
const OUTPUT_DIRECTORY: String = "user://brackett_greybox/review/"
const OUTPUT: String = OUTPUT_DIRECTORY + "scene_checks.json"
const BOUNDS_TOLERANCE_M: float = 0.01


## Starts the finite checks after scene-tree initialization.
func _initialize() -> void:
	_check.call_deferred()


## Measures actual imported bounds and exercises saved World collision through physics APIs.
func _check() -> void:
	var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(
		"res://tools/assets/world/brackett_greybox/editor_input.json"))
	var measurements: Array[Dictionary] = []
	for asset: Dictionary in spec.kit:
		measurements.append(_check_asset(asset))
	var packed: PackedScene = load(BASE + "city.tscn")
	var city: Node3D = packed.instantiate()
	root.add_child(city)
	await physics_frame
	await physics_frame
	var count: int = _placement_count(city)
	assert(count == 290)
	var space: PhysicsDirectSpaceState3D = city.get_world_3d().direct_space_state
	var queries: Array[Dictionary] = []
	queries.append(_ray(space, "harbour basin stays open", Vector2(350, 480), false))
	queries.append(_ray(space, "harbour mouth remains open", Vector2(350, 630), false))
	queries.append(_ray(space, "single bridge is solid", Vector2(350, 590), true))
	queries.append(_ray(space, "downtown avenue junction", Vector2(735, 245), true))
	queries.append(_ray(space, "western housing street", Vector2(230, 250), true))
	queries.append(_ray(space, "working coast", Vector2(1140, 440), true))
	queries.append(_ray(space, "southern retail street", Vector2(705, 530), true))
	queries.append(_ray(space, "north sea is not traversable ground", Vector2(650, 50), false))
	DirAccess.make_dir_recursive_absolute(OUTPUT_DIRECTORY)
	var file: FileAccess = FileAccess.open(OUTPUT, FileAccess.WRITE)
	file.store_string(JSON.stringify({"engine": Engine.get_version_info(),
		"buildings": count, "distinct_placement_ids": count, "imported_bounds": measurements,
		"physics_rays": queries, "scope": "asset queries; actor/vehicle/network pending"}, "\t"))
	print("BRACKETT_SCENE_CHECKS ", count, " buildings; ", measurements.size(), " imports; 8 rays")
	quit()


## Confirms each saved building retains a unique district-scoped replacement identity.
func _placement_count(city: Node3D) -> int:
	var ids: Dictionary = {}
	for index: int in range(1, 10):
		var district: Node = city.get_node("Sectors/District%02d" % index)
		assert(district.get("district_id") == index)
		for building: Node in district.get_node("Geometry").get_children():
			var identity: String = str(building.get("world_id"))
			assert(not identity.is_empty() and not ids.has(identity), identity)
			ids[identity] = true
			assert(building.get_node("Visuals/Model").scene_file_path.ends_with(".glb"))
	return ids.size()


## Checks metre scale, ground datum and unit-root transforms against independent dimensions.
func _check_asset(asset: Dictionary) -> Dictionary:
	var packed: PackedScene = load(BASE + "prefabs/" + asset.asset_id + ".tscn")
	var instance: Node3D = packed.instantiate()
	assert(instance.transform == Transform3D.IDENTITY)
	var model: Node3D = instance.get_node("Visuals/Model")
	assert(model.transform == Transform3D.IDENTITY)
	var bounds: AABB = _bounds(model)
	var expected: Vector3 = Vector3(asset.width, asset.height, asset.depth)
	assert(bounds.size.distance_to(expected) < BOUNDS_TOLERANCE_M, str(asset.asset_id))
	assert(absf(bounds.position.y) < BOUNDS_TOLERANCE_M)
	var result: Dictionary = {"asset_id": asset.asset_id, "aabb": str(bounds),
		"expected_size": str(expected), "linked_import": model.scene_file_path}
	instance.free()
	return result


## Unions source mesh bounds in model-local space; source exports have no nested transforms.
func _bounds(model: Node3D) -> AABB:
	var bounds: AABB
	var first: bool = true
	for node: Node in model.get_children():
		if node is MeshInstance3D:
			var box: AABB = node.transform * node.get_aabb()
			bounds = box if first else bounds.merge(box)
			first = false
	assert(not first)
	return bounds


## Queries the saved collision surface at a named independent map landmark.
func _ray(space: PhysicsDirectSpaceState3D, label: String, map: Vector2,
		expected: bool) -> Dictionary:
	var point: Vector3 = Vector3(map.x - 630, 0, map.y - 355)
	var ray: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(
		point + Vector3.UP * 1.0, point - Vector3.UP * 3.0, 1)
	var hit: Dictionary = space.intersect_ray(ray)
	assert((not hit.is_empty()) == expected, label)
	return {"case": label, "hit": not hit.is_empty(), "expected": expected,
		"map_coordinate": str(map), "position": str(hit.get("position", "none"))}
