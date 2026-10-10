extends GutTest
## Verifies Brackett road presets, JSON seeding, stable identities, and graph validation.

const BRACKETT_SOURCE: RoadSourceCatalog = preload(
	"res://resources/world/roads/brackett_road_source.tres"
)
const GREYBOX_PLAN_PATH: String = (
	"res://art/source/models/brackett_greybox/authoring_plan.json"
)


## Proves the five class presets preserve the accepted carriageway and walk allocations.
func test_brackett_presets_and_route_specs_match_the_greybox_source() -> void:
	assert_true(BRACKETT_SOURCE.validate_source().ok)
	assert_eq(BRACKETT_SOURCE.source_revision, 1)
	assert_eq(BRACKETT_SOURCE.addon_version, "0.9.4")
	assert_eq(BRACKETT_SOURCE.presets.size(), 5)
	assert_eq(BRACKETT_SOURCE.sections.size(), 50)
	var expected: Dictionary[StringName, Array] = {
		&"avenue": [4, 3.5, 5.0, 13.9],
		&"street": [2, 4.5, 4.0, 11.1],
		&"local": [2, 3.5, 2.5, 8.3],
		&"freight": [2, 5.0, 2.0, 8.3],
		&"service": [1, 4.5, 1.5, 5.6],
	}
	var class_counts: Dictionary[StringName, int] = {}
	for preset: RoadTypePreset in BRACKETT_SOURCE.presets:
		var row: Array = expected[preset.preset_id]
		assert_eq(preset.lane_directions.size(), row[0])
		assert_almost_eq(preset.lane_width_m, row[1], 0.001)
		assert_almost_eq(preset.sidewalk_width_left_m, row[2], 0.001)
		assert_almost_eq(preset.speed_limit_mps, row[3], 0.001)
	for spec: RoadSectionSpec in BRACKETT_SOURCE.sections:
		class_counts[spec.preset.preset_id] = class_counts.get(spec.preset.preset_id, 0) + 1
		assert_true(String(spec.road_id).begins_with("brackett/roads/"))
		assert_true(String(spec.section_id).ends_with("/section_01"))
	assert_eq(
		class_counts,
		{ &"avenue": 2, &"freight": 4, &"local": 24, &"service": 1, &"street": 19 },
	)
	var invalid_digest: RoadSourceCatalog = BRACKETT_SOURCE.duplicate(true)
	invalid_digest.bootstrap_source_sha256 = "z".repeat(64)
	assert_false(invalid_digest.validate_source().ok)


## Proves JSON bootstrap retains all 50 identities and applies the documented map origin.
func test_json_bootstrap_requires_explicit_service_direction_and_bridge_profile() -> void:
	var unresolved: Dictionary = RoadJsonBootstrap.load_plan(
		GREYBOX_PLAN_PATH, BRACKETT_SOURCE, {}, &"harbour_bridge"
	)
	assert_false(unresolved.ok)
	assert_true(_errors_contain(unresolved.errors, "explicit one-way direction"))
	var service: RoadSectionSpec = BRACKETT_SOURCE.section_for_source_route(
		"Workshop service link"
	)
	var choices: Dictionary = {
		service.road_id: RoadSectionSpec.TravelDirection.FORWARD,
	}
	var wrong_bridge: Dictionary = RoadJsonBootstrap.load_plan(
		GREYBOX_PLAN_PATH, BRACKETT_SOURCE, choices, &"standard"
	)
	assert_false(wrong_bridge.ok)
	assert_true(_errors_contain(wrong_bridge.errors, "structural profile"))

	var result: Dictionary = RoadJsonBootstrap.load_plan(
		GREYBOX_PLAN_PATH, BRACKETT_SOURCE, choices, &"harbour_bridge"
	)
	assert_true(result.ok)
	assert_eq(result.routes.size(), 50)
	assert_eq(result.routes[0].road_id, &"brackett/roads/north_coast")
	assert_eq(result.routes[0].point_ids[0], &"brackett/roads/north_coast/point_0001")
	assert_eq(result.routes[0].points_world[0], Vector3(-505.0, 0.0, -170.0))


## Proves applying a preset changes addon fields but never the authored spline transform.
func test_adapter_applies_preset_and_rejects_drift() -> void:
	var fixture: Dictionary = _two_point_fixture(_single_section_catalog())
	var adapter: RoadNetworkAdapter = fixture.adapter
	var first: RoadPoint = fixture.first
	var second: RoadPoint = fixture.second
	var first_transform: Transform3D = first.transform
	assert_true(adapter.apply_section_to_point(first).ok)
	assert_true(adapter.apply_section_to_point(second).ok)
	assert_eq(first.transform, first_transform)
	assert_true(adapter.validate_network(fixture.root).ok)

	second.lane_width += 0.25
	var rejected: Dictionary = adapter.validate_network(fixture.root)
	assert_false(rejected.ok)
	assert_true(_errors_contain(rejected.errors, "lane width drifted"))


## Proves a connected class change is accepted only at an explicit stable boundary.
func test_class_transition_requires_target_section_identity() -> void:
	var catalog: RoadSourceCatalog = _transition_catalog()
	var root := Node.new()
	add_child_autofree(root)
	var adapter := RoadNetworkAdapter.new()
	adapter.source_catalog = catalog
	root.add_child(adapter)
	var container := RoadContainer.new()
	container.set_meta(RoadNetworkAdapter.META_CONTAINER_ID, &"brackett/containers/test")
	root.add_child(container)
	var points: Array[RoadPoint] = []
	for index: int in 4:
		var spec: RoadSectionSpec = catalog.sections[0 if index < 2 else 1]
		var point: RoadPoint = _point(spec, index + 1)
		container.add_child(point)
		point.container = container
		points.append(point)
	for index: int in 3:
		points[index].next_pt_init = points[index].get_path_to(points[index + 1])
		points[index + 1].prior_pt_init = points[index + 1].get_path_to(points[index])
	_mark_dead_end(points[0])
	_mark_dead_end(points[3])
	for point: RoadPoint in points:
		assert_true(adapter.apply_section_to_point(point).ok)

	var missing: Dictionary = adapter.validate_network(root)
	assert_false(missing.ok)
	assert_true(_errors_contain(missing.errors, "without an explicit section transition"))
	points[1].set_meta(
		RoadNetworkAdapter.META_TRANSITION_SECTION_ID, catalog.sections[1].section_id
	)
	assert_true(adapter.validate_network(root).ok)


## Proves procedural junction identity and branches stay inside one RoadContainer.
func test_procedural_junction_requires_stable_identity_and_same_container() -> void:
	var catalog: RoadSourceCatalog = _single_section_catalog()
	var junction_spec := RoadJunctionSpec.new()
	junction_spec.junction_id = &"brackett/junctions/test"
	catalog.junctions.append(junction_spec)
	var fixture: Dictionary = _two_point_fixture(catalog)
	var container: RoadContainer = fixture.first.get_parent()
	var intersection := RoadIntersection.new()
	intersection.name = "Junction"
	intersection.set_meta(RoadNetworkAdapter.META_JUNCTION_ID, junction_spec.junction_id)
	container.add_child(intersection)
	intersection.container = container
	fixture.first.next_pt_init = fixture.first.get_path_to(intersection)
	fixture.second.prior_pt_init = fixture.second.get_path_to(intersection)
	intersection.edge_points = [fixture.first, fixture.second]
	assert_true(fixture.adapter.apply_section_to_point(fixture.first).ok)
	assert_true(fixture.adapter.apply_section_to_point(fixture.second).ok)
	assert_true(fixture.adapter.validate_network(fixture.root).ok)

	var other := RoadContainer.new()
	other.set_meta(RoadNetworkAdapter.META_CONTAINER_ID, &"brackett/containers/other")
	fixture.root.add_child(other)
	container.remove_child(fixture.second)
	other.add_child(fixture.second)
	fixture.second.container = other
	var rejected: Dictionary = fixture.adapter.validate_network(fixture.root)
	assert_false(rejected.ok)
	assert_true(_errors_contain(rejected.errors, "branch outside its RoadContainer"))


## Proves reciprocal addon edges also require explicit interface-point metadata.
func test_cross_container_edge_requires_two_marked_interface_points() -> void:
	var preset := _preset(&"street", 4.5)
	var first_spec := _section(
		&"brackett/roads/first", &"brackett/roads/first/section_01", preset
	)
	var second_spec := _section(
		&"brackett/roads/second", &"brackett/roads/second/section_01", preset
	)
	var catalog: RoadSourceCatalog = _catalog([preset], [first_spec, second_spec])
	var root := Node.new()
	add_child_autofree(root)
	var adapter := RoadNetworkAdapter.new()
	adapter.source_catalog = catalog
	root.add_child(adapter)
	var first_container := _container(&"brackett/containers/first")
	var second_container := _container(&"brackett/containers/second")
	root.add_child(first_container)
	root.add_child(second_container)
	var points: Array[RoadPoint] = _cross_container_points(first_spec, second_spec)
	for point: RoadPoint in points.slice(0, 2):
		first_container.add_child(point)
		point.container = first_container
	for point: RoadPoint in points.slice(2):
		second_container.add_child(point)
		point.container = second_container
	points[0].next_pt_init = points[0].get_path_to(points[1])
	points[1].prior_pt_init = points[1].get_path_to(points[0])
	points[2].next_pt_init = points[2].get_path_to(points[3])
	points[3].prior_pt_init = points[3].get_path_to(points[2])
	_mark_dead_end(points[0])
	_mark_dead_end(points[3])
	_connect_container_edges(first_container, points[1], second_container, points[2])
	_connect_container_edges(second_container, points[2], first_container, points[1])
	first_container.edge_rp_local_dirs[0] = RoadPoint.PointInit.NEXT
	first_container.edge_rp_target_dirs[0] = RoadPoint.PointInit.PRIOR
	second_container.edge_rp_local_dirs[0] = RoadPoint.PointInit.PRIOR
	second_container.edge_rp_target_dirs[0] = RoadPoint.PointInit.NEXT
	for point: RoadPoint in points:
		assert_true(adapter.apply_section_to_point(point).ok)

	var unmarked: Dictionary = adapter.validate_network(root)
	assert_false(unmarked.ok)
	assert_true(_errors_contain(unmarked.errors, "interface RoadPoint"))
	points[1].set_meta(RoadNetworkAdapter.META_INTERFACE, true)
	points[2].set_meta(RoadNetworkAdapter.META_INTERFACE, true)
	assert_true(adapter.validate_network(root).ok)


## Returns whether any normalized validation message contains the expected fragment.
func _errors_contain(errors: Array, fragment: String) -> bool:
	for error: String in errors:
		if fragment in error:
			return true
	return false


## Builds one valid preset and section catalog for focused adapter tests.
func _single_section_catalog() -> RoadSourceCatalog:
	var preset := _preset(&"street", 4.5)
	var section := _section(
		&"brackett/roads/test", &"brackett/roads/test/section_01", preset
	)
	return _catalog([preset], [section])


## Builds two classes so transition validation cannot pass by comparing equal presets.
func _transition_catalog() -> RoadSourceCatalog:
	var street := _preset(&"street", 4.5)
	var local := _preset(&"local", 3.5)
	var first := _section(
		&"brackett/roads/test", &"brackett/roads/test/section_01", street
	)
	var second := _section(
		&"brackett/roads/test", &"brackett/roads/test/section_02", local
	)
	return _catalog([street, local], [first, second])


## Builds one valid semantic catalog with the supplied owned records.
func _catalog(
	presets: Array[RoadTypePreset], sections: Array[RoadSectionSpec]
) -> RoadSourceCatalog:
	var catalog := RoadSourceCatalog.new()
	catalog.district_id = &"brackett"
	catalog.bootstrap_source_sha256 = "a".repeat(64)
	catalog.presets = presets
	catalog.sections = sections
	return catalog


## Builds one minimum valid road-class preset.
func _preset(preset_id: StringName, lane_width_m: float) -> RoadTypePreset:
	var preset := RoadTypePreset.new()
	preset.preset_id = preset_id
	preset.lane_directions = [RoadPoint.LaneDir.REVERSE, RoadPoint.LaneDir.FORWARD]
	preset.lane_width_m = lane_width_m
	return preset


## Builds one stable section identity using an owned preset.
func _section(
	road_id: StringName, section_id: StringName, preset: RoadTypePreset
) -> RoadSectionSpec:
	var section := RoadSectionSpec.new()
	section.road_id = road_id
	section.section_id = section_id
	section.source_route_name = String(section_id)
	section.preset = preset
	return section


## Builds a two-point reciprocal addon graph with explicit stable endpoint identities.
func _two_point_fixture(catalog: RoadSourceCatalog) -> Dictionary:
	var root := Node.new()
	add_child_autofree(root)
	var adapter := RoadNetworkAdapter.new()
	adapter.source_catalog = catalog
	root.add_child(adapter)
	var container := RoadContainer.new()
	container.set_meta(RoadNetworkAdapter.META_CONTAINER_ID, &"brackett/containers/test")
	root.add_child(container)
	var first: RoadPoint = _point(catalog.sections[0], 1)
	var second: RoadPoint = _point(catalog.sections[0], 2)
	container.add_child(first)
	container.add_child(second)
	first.container = container
	second.container = container
	first.next_pt_init = first.get_path_to(second)
	second.prior_pt_init = second.get_path_to(first)
	_mark_dead_end(first)
	_mark_dead_end(second)
	return {
		"root": root,
		"adapter": adapter,
		"first": first,
		"second": second,
	}


## Builds two section pairs with colocated interface endpoints.
func _cross_container_points(
	first_spec: RoadSectionSpec, second_spec: RoadSectionSpec
) -> Array[RoadPoint]:
	var points: Array[RoadPoint] = [
		_point(first_spec, 1),
		_point(first_spec, 2),
		_point(second_spec, 1),
		_point(second_spec, 2),
	]
	points[2].position = points[1].position
	points[3].position = points[2].position + Vector3(20.0, 0.0, 0.0)
	return points


## Builds one container carrying a stable project-owned identity.
func _container(container_id: StringName) -> RoadContainer:
	var container := RoadContainer.new()
	container.set_meta(RoadNetworkAdapter.META_CONTAINER_ID, container_id)
	return container


## Stores one cross-container edge before assigning its endpoint directions.
func _connect_container_edges(
	local_container: RoadContainer,
	local_point: RoadPoint,
	target_container: RoadContainer,
	target_point: RoadPoint,
) -> void:
	local_container.edge_containers = [local_container.get_path_to(target_container)]
	local_container.edge_rp_locals = [local_container.get_path_to(local_point)]
	local_container.edge_rp_targets = [target_container.get_path_to(target_point)]
	local_container.edge_rp_local_dirs = [RoadPoint.PointInit.NEITHER]
	local_container.edge_rp_target_dirs = [RoadPoint.PointInit.NEITHER]


## Builds one addon point carrying only project-owned identity metadata.
func _point(spec: RoadSectionSpec, index: int) -> RoadPoint:
	var point := RoadPoint.new()
	point.name = "Point%02d" % index
	point.position = Vector3(index * 20.0, 0.0, 0.0)
	point.set_meta(RoadNetworkAdapter.META_ROAD_ID, spec.road_id)
	point.set_meta(RoadNetworkAdapter.META_SECTION_ID, spec.section_id)
	point.set_meta(
		RoadNetworkAdapter.META_POINT_ID,
		StringName("%s/point_%04d" % [spec.road_id, index]),
	)
	return point


## Marks one outer point as an intentional terminus for its missing connection.
func _mark_dead_end(point: RoadPoint) -> void:
	point.terminated = true
	point.set_meta(RoadNetworkAdapter.META_DEAD_END, true)
