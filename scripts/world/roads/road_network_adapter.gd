@tool
class_name RoadNetworkAdapter
extends Node
## Applies project road semantics to addon nodes and validates stable source connections.

const META_CONTAINER_ID: StringName = &"road_container_id"
const META_ROAD_ID: StringName = &"road_id"
const META_SECTION_ID: StringName = &"road_section_id"
const META_POINT_ID: StringName = &"road_point_id"
const META_JUNCTION_ID: StringName = &"road_junction_id"
const META_INTERFACE: StringName = &"road_interface_point"
const META_DEAD_END: StringName = &"road_dead_end"
const META_TRANSITION_SECTION_ID: StringName = &"road_transition_section_id"
const FLOAT_TOLERANCE: float = 0.0001

@export var source_catalog: RoadSourceCatalog


## Returns the world-integrator-owned road revision consumed by later derivation stages.
func source_identity() -> Dictionary:
	if source_catalog == null:
		return {}
	return {
		"district_id": source_catalog.district_id,
		"source_revision": source_catalog.source_revision,
		"derivation_schema_revision": source_catalog.derivation_schema_revision,
		"addon_version": source_catalog.addon_version,
	}


## Applies one section's lane and width values without altering point curves or transforms.
func apply_section_to_point(point: RoadPoint) -> Dictionary:
	var spec: RoadSectionSpec = _section_for_point(point)
	if spec == null or not spec.is_valid():
		return _failure("point does not resolve to a valid road section")
	var directions: Array[RoadPoint.LaneDir] = spec.expected_lane_directions()
	if directions.is_empty():
		return _failure("section requires an explicit one-way direction")
	point.traffic_dir = directions
	point.lane_width = spec.expected_lane_width_m()
	point.shoulder_width_l = spec.expected_shoulder_left_m()
	point.shoulder_width_r = spec.expected_shoulder_right_m()
	point.gutter_profile = spec.expected_gutter_profile_m()
	return { "ok": true }


## Validates catalog ownership, stable IDs, preset agreement, and all addon connections.
func validate_network(root: Node) -> Dictionary:
	var errors: Array[String] = []
	if source_catalog == null:
		return _failure("source_catalog is not assigned")
	var source_result: Dictionary = source_catalog.validate_source()
	if not source_result.ok:
		return source_result
	var containers: Array[RoadContainer] = []
	_collect_containers(root, containers)
	_validate_containers(containers, errors)
	_validate_complete_sections(containers, errors)
	return { "ok": errors.is_empty(), "errors": errors }


## Recursively gathers addon containers without depending on generated child names.
func _collect_containers(node: Node, output: Array[RoadContainer]) -> void:
	if node is RoadContainer:
		output.append(node as RoadContainer)
	for child: Node in node.get_children():
		_collect_containers(child, output)


## Validates unique container identities and delegates contained source checks.
func _validate_containers(
	containers: Array[RoadContainer], errors: Array[String]
) -> void:
	var container_ids: Dictionary[StringName, bool] = {}
	var point_ids: Dictionary[StringName, bool] = {}
	var junction_ids: Dictionary[StringName, bool] = {}
	for container: RoadContainer in containers:
		var container_id: StringName = StringName(container.get_meta(META_CONTAINER_ID, &""))
		_add_unique_id(container_id, "container", container_ids, errors)
		_validate_edge_storage(container, errors)
		for child: Node in container.get_children():
			if child is RoadPoint:
				_validate_point(child as RoadPoint, point_ids, errors)
			elif child is RoadIntersection:
				_validate_junction(child as RoadIntersection, junction_ids, errors)


## Ensures every catalog section owns at least two source points in the live graph.
func _validate_complete_sections(
	containers: Array[RoadContainer], errors: Array[String]
) -> void:
	var counts: Dictionary[StringName, int] = {}
	for container: RoadContainer in containers:
		for child: Node in container.get_children():
			if child is RoadPoint:
				var section_id := StringName(child.get_meta(META_SECTION_ID, &""))
				counts[section_id] = counts.get(section_id, 0) + 1
	for spec: RoadSectionSpec in source_catalog.sections:
		if counts.get(spec.section_id, 0) < 2:
			errors.append("section %s has fewer than two RoadPoints" % spec.section_id)


## Checks one point's identities, preset values, and prior/next relationships.
func _validate_point(
	point: RoadPoint,
	point_ids: Dictionary[StringName, bool],
	errors: Array[String],
) -> void:
	var point_id: StringName = StringName(point.get_meta(META_POINT_ID, &""))
	_add_unique_id(point_id, "point", point_ids, errors)
	var spec: RoadSectionSpec = _section_for_point(point)
	if spec == null:
		errors.append("point %s references an unknown section" % point_id)
		return
	if StringName(point.get_meta(META_ROAD_ID, &"")) != spec.road_id:
		errors.append("point %s road_id disagrees with its section" % point_id)
	_validate_point_preset(point, spec, point_id, errors)
	_validate_point_direction(point, point.prior_pt_init, false, errors)
	_validate_point_direction(point, point.next_pt_init, true, errors)


## Rejects any addon point value that drifted from the preset or declared override.
func _validate_point_preset(
	point: RoadPoint,
	spec: RoadSectionSpec,
	point_id: StringName,
	errors: Array[String],
) -> void:
	if point.traffic_dir != spec.expected_lane_directions():
		errors.append("point %s lane directions drifted from its section" % point_id)
	if not is_equal_approx(point.lane_width, spec.expected_lane_width_m()):
		errors.append("point %s lane width drifted from its section" % point_id)
	if not is_equal_approx(point.shoulder_width_l, spec.expected_shoulder_left_m()):
		errors.append("point %s left shoulder drifted from its section" % point_id)
	if not is_equal_approx(point.shoulder_width_r, spec.expected_shoulder_right_m()):
		errors.append("point %s right shoulder drifted from its section" % point_id)
	if not point.gutter_profile.is_equal_approx(spec.expected_gutter_profile_m()):
		errors.append("point %s gutter profile drifted from its section" % point_id)


## Checks one local connection, an explicit external interface, or a declared dead end.
func _validate_point_direction(
	point: RoadPoint,
	path: NodePath,
	is_next: bool,
	errors: Array[String],
) -> void:
	var spec: RoadSectionSpec = _section_for_point(point)
	var point_id := StringName(point.get_meta(META_POINT_ID, &""))
	var target: RoadGraphNode = null
	if path:
		target = point.get_node_or_null(path) as RoadGraphNode
	if target == null:
		if _has_external_edge(point, is_next):
			return
		if point.terminated and bool(point.get_meta(META_DEAD_END, false)):
			return
		errors.append("point %s has an unvalidated open connection" % point_id)
		return
	if target is RoadIntersection:
		_validate_intersection_connection(point, target as RoadIntersection, point_id, errors)
		return
	if not target is RoadPoint:
		errors.append("point %s connects to an unsupported graph node" % point_id)
		return
	_validate_point_connection(point, target as RoadPoint, is_next, errors)


## Checks reciprocal point links and explicit section-class transition markers.
func _validate_point_connection(
	point: RoadPoint,
	target: RoadPoint,
	is_next: bool,
	errors: Array[String],
) -> void:
	var spec: RoadSectionSpec = _section_for_point(point)
	var point_id := StringName(point.get_meta(META_POINT_ID, &""))
	if not _points_are_reciprocal(point, target):
		errors.append("point %s connection is not reciprocal" % point_id)
	var target_spec: RoadSectionSpec = _section_for_point(target)
	if target_spec == null:
		errors.append("point %s connects to an unknown section" % point_id)
		return
	if target_spec.section_id == spec.section_id:
		return
	if not is_next:
		return
	var transition_id := StringName(point.get_meta(META_TRANSITION_SECTION_ID, &""))
	if transition_id != target_spec.section_id:
		errors.append("point %s changes class without an explicit section transition" % point_id)


## Checks that a procedural junction and every branch remain in one RoadContainer.
func _validate_intersection_connection(
	point: RoadPoint,
	intersection: RoadIntersection,
	point_id: StringName,
	errors: Array[String],
) -> void:
	if point.get_parent() != intersection.get_parent():
		errors.append("point %s crosses containers to a procedural intersection" % point_id)
	if point not in intersection.edge_points:
		errors.append("point %s intersection branch is not reciprocal" % point_id)


## Validates one stable junction identity, catalog spec, and same-container branches.
func _validate_junction(
	intersection: RoadIntersection,
	junction_ids: Dictionary[StringName, bool],
	errors: Array[String],
) -> void:
	var junction_id := StringName(intersection.get_meta(META_JUNCTION_ID, &""))
	_add_unique_id(junction_id, "junction", junction_ids, errors)
	if source_catalog.junction(junction_id) == null:
		errors.append("junction %s has no catalog spec" % junction_id)
	for point: RoadPoint in intersection.edge_points:
		if point == null or point.get_parent() != intersection.get_parent():
			errors.append("junction %s has a branch outside its RoadContainer" % junction_id)


## Validates parallel edge arrays, addon reciprocity, and explicit interface-point seams.
func _validate_edge_storage(container: RoadContainer, errors: Array[String]) -> void:
	var size: int = container.edge_rp_locals.size()
	if (
		container.edge_containers.size() != size
		or container.edge_rp_targets.size() != size
		or container.edge_rp_target_dirs.size() != size
		or container.edge_rp_local_dirs.size() != size
	):
		errors.append("container %s has mismatched edge arrays" % container.name)
		return
	if not container.validate_edges(false):
		errors.append("container %s has invalid addon edge connections" % container.name)
	for index: int in size:
		if container.edge_containers[index] == ^"":
			continue
		_validate_interface_entry(container, index, errors)


## Enforces the documented interface-RoadPoint workaround for cross-container seams.
func _validate_interface_entry(
	container: RoadContainer, index: int, errors: Array[String]
) -> void:
	var point: RoadPoint = container.get_node_or_null(container.edge_rp_locals[index]) as RoadPoint
	var target_container: RoadContainer = container.get_node_or_null(
		container.edge_containers[index]
	) as RoadContainer
	var target: RoadPoint = null
	if target_container != null:
		target = target_container.get_node_or_null(container.edge_rp_targets[index]) as RoadPoint
	if point == null or target == null:
		return
	if not point.get_meta(META_INTERFACE, false) or not target.get_meta(META_INTERFACE, false):
		errors.append("cross-container connection does not use interface RoadPoints")
	if point.global_position.distance_to(target.global_position) > FLOAT_TOLERANCE:
		errors.append("cross-container interface RoadPoints do not share a position")
	if point.traffic_dir != target.traffic_dir or not is_equal_approx(
		point.lane_width, target.lane_width
	):
		errors.append("cross-container interface RoadPoints disagree on lane shape")
	if not _has_reciprocal_edge_entry(container, index, target_container, target):
		errors.append("cross-container interface entry is not reciprocal")


## Finds the target container's exact reverse edge record.
func _has_reciprocal_edge_entry(
	container: RoadContainer,
	index: int,
	target_container: RoadContainer,
	target: RoadPoint,
) -> bool:
	for target_index: int in target_container.edge_rp_locals.size():
		if (
			target_index >= target_container.edge_containers.size()
			or target_index >= target_container.edge_rp_targets.size()
			or target_index >= target_container.edge_rp_target_dirs.size()
			or target_index >= target_container.edge_rp_local_dirs.size()
		):
			continue
		var candidate: Node = target_container.get_node_or_null(
			target_container.edge_rp_locals[target_index]
		)
		if candidate != target:
			continue
		if target_container.get_node_or_null(
			target_container.edge_containers[target_index]
		) != container:
			continue
		var local_point: Node = container.get_node_or_null(container.edge_rp_locals[index])
		if (
			local_point == null
			or target_container.edge_rp_targets[target_index]
			!= container.get_path_to(local_point)
		):
			continue
		if (
			target_container.edge_rp_local_dirs[target_index]
			!= container.edge_rp_target_dirs[index]
			or target_container.edge_rp_target_dirs[target_index]
			!= container.edge_rp_local_dirs[index]
		):
			continue
		return true
	return false


## Reports whether this missing local direction is a populated addon external edge.
func _has_external_edge(point: RoadPoint, is_next: bool) -> bool:
	var container: RoadContainer = point.get_parent() as RoadContainer
	if container == null:
		return false
	var direction: int = RoadPoint.PointInit.NEXT if is_next else RoadPoint.PointInit.PRIOR
	for index: int in container.edge_rp_locals.size():
		if container.get_node_or_null(container.edge_rp_locals[index]) != point:
			continue
		if container.edge_rp_local_dirs[index] != direction:
			continue
		return container.edge_containers[index] != ^""
	return false


## Resolves one point's semantic section from stable metadata only.
func _section_for_point(point: RoadPoint) -> RoadSectionSpec:
	if source_catalog == null or point == null:
		return null
	var section_id := StringName(point.get_meta(META_SECTION_ID, &""))
	return source_catalog.section(section_id)


## Checks that either target direction points back to the source point.
func _points_are_reciprocal(point: RoadPoint, target: RoadPoint) -> bool:
	return (
		target.get_node_or_null(target.prior_pt_init) == point
		or target.get_node_or_null(target.next_pt_init) == point
	)


## Adds a bounded nonempty identity or records its exact duplicate.
func _add_unique_id(
	value: StringName,
	label: String,
	seen: Dictionary[StringName, bool],
	errors: Array[String],
) -> void:
	var byte_count: int = String(value).to_utf8_buffer().size()
	if byte_count == 0 or byte_count > RoadSourceCatalog.MAX_ID_BYTES:
		errors.append("%s identity is missing or exceeds 128 UTF-8 bytes" % label)
	elif seen.has(value):
		errors.append("duplicate %s identity: %s" % [label, value])
	seen[value] = true


## Creates a normalized validation failure.
func _failure(message: String) -> Dictionary:
	return { "ok": false, "errors": [message] }
