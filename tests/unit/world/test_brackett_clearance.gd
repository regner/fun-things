extends GutTest
## Gates Brackett sector placements: corridors, placement gaps, district bounds and anchors.
##
## Every C2.2a district lane runs this gate before landing. Report mode writes a per-site
## clearance and prefab-fit report when `BRACKETT_CLEARANCE_REPORT` names an output JSON path;
## `BRACKETT_CLEARANCE_CANDIDATES` names an optional fit-candidate JSON (see
## `tools/world/district_02_fit_candidates.json`) and `BRACKETT_CLEARANCE_BASE` an optional
## earlier report whose `world_ids` replace the frozen authoring placements as identity base.

const Footprints := preload("res://tests/unit/world/brackett_footprints.gd")
const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")
const AUTHORING_INPUT_PATH: String = "res://tools/assets/world/brackett_greybox/editor_input.json"
const PREFAB_DIRECTORY: String = "res://scenes/prefabs/environment/"
## Godot XZ = authoring map XY + this offset (`map_origin_godot` in the greybox prepare.py).
const AUTHORING_MAP_ORIGIN := Vector2(-630.0, -355.0)
const DISTRICT_COUNT: int = 9
const ROAD_MATERIAL: String = "grey_road"
const WALK_MATERIAL: String = "grey_walk"
const MAX_SURFACE_OVERLAP_M2: float = 0.01
const MAX_DISTRICT_SPILL_M2: float = 0.01
const MIN_PLACEMENT_GAP_M: float = 1.0
## Collision entirely above this soffit may span corridors (footbridge decks over carriageways).
const COLLISION_SOFFIT_CLEARANCE_M: float = 5.5
## Visual parts reaching below these heights must stay off the matching corridor surface.
const ROAD_VISUAL_CLEARANCE_M: float = 4.5
const WALK_VISUAL_CLEARANCE_M: float = 2.5
const ROAD_AREA_TOLERANCE: float = 0.005
const SPAWN_CAPSULE_RADIUS_M: float = 0.35
const SPAWN_CAPSULE_HEIGHT_M: float = 1.8
const PARKED_CAR_BOX_SIZE_M := Vector3(1.8, 1.5, 3.4)
const ANCHOR_QUERY_MAX_RESULTS: int = 32
const PHYSICS_SETTLE_FRAMES: int = 3
const MAX_LISTED_VIOLATIONS: int = 20
const REPORT_SEARCH_RADIUS_M: float = 40.0
const MAX_FIT_CANDIDATES_PER_SITE: int = 8
const FIT_SNAP_M: float = 0.01
## Yaw steps relative to the road-facing yaw, in plan order: facing, opposite, perpendiculars.
const FIT_YAW_STEPS_DEG: Array[float] = [0.0, 180.0, 90.0, 270.0]
const REPORT_PATH_ENV: String = "BRACKETT_CLEARANCE_REPORT"
const CANDIDATES_PATH_ENV: String = "BRACKETT_CLEARANCE_CANDIDATES"
const BASE_REPORT_ENV: String = "BRACKETT_CLEARANCE_BASE"
const REPORT_SCHEMA: int = 1

var _match: Node3D
var _authoring: Dictionary = {}
var _road := Footprints.PolygonIndex.new()
var _walk := Footprints.PolygonIndex.new()
var _sites: Array[Site] = []
var _district_nodes: Dictionary[int, Node3D] = {}
var _district_polygons: Dictionary[int, PackedVector2Array] = {}
var _footprints: Array[Footprints.Footprint] = []
var _collision_index := Footprints.PolygonIndex.new()
var _collision_footprints: Array[Footprints.Footprint] = []
var _scan_failures := PackedStringArray()


## Instantiates the saved Match once and extracts surfaces, districts and footprints.
func before_all() -> void:
	_authoring = JSON.parse_string(FileAccess.get_file_as_string(AUTHORING_INPUT_PATH))
	for district: Dictionary in _authoring.districts:
		var polygon := PackedVector2Array()
		for point: Array in district.points:
			polygon.append(Vector2(point[0], point[1]) + AUTHORING_MAP_ORIGIN)
		_district_polygons[int(district.id)] = polygon

	_match = MATCH_SCENE.instantiate() as Node3D
	add_child(_match)
	var sectors: Node = _match.get_node("World/Sectors")
	for sector: Node in sectors.get_children():
		if int(sector.get("district_id")) > 0:
			_scan_district(sector as Node3D)
		else:
			_scan_ground(sector as Node3D)

	for footprint: Footprints.Footprint in _footprints:
		if footprint.is_collision and footprint.is_placement:
			_collision_index.add(footprint.polygon)
			_collision_footprints.append(footprint)


## Frees the shared Match instance.
func after_all() -> void:
	_match.free()


## Proves surfaces come from the saved ground meshes and match the frozen authoring areas.
func test_saved_ground_meshes_supply_road_and_walk_surfaces() -> void:
	assert_gt(_road.polygons.size(), 0, "road triangles come from grey_road surfaces")
	assert_gt(_walk.polygons.size(), 0, "walk triangles come from grey_walk surfaces")
	var road_area: float = 0.0
	for triangle: PackedVector2Array in _road.polygons:
		road_area += Footprints.polygon_area(triangle)
	var authored_area: float = float(_authoring.summary.road_area_m2)
	assert_almost_eq(road_area, authored_area, authored_area * ROAD_AREA_TOLERANCE)
	assert_eq(_district_nodes.size(), DISTRICT_COUNT, "every district sector is scanned")
	assert_eq(_district_polygons.size(), DISTRICT_COUNT, "every district has a bound")
	_assert_no_violations(_scan_failures, "supported sector collision shapes")


## Proves building identities stay unique and scoped to the district that saves them.
func test_world_ids_are_unique_and_district_scoped() -> void:
	var violations := PackedStringArray()
	var seen: Dictionary[String, bool] = {}
	for site: Site in _sites:
		if seen.has(site.world_id):
			violations.append("duplicate world_id " + site.world_id)
		seen[site.world_id] = true
		var prefix: String = "brackett/district_%02d/" % site.district_id
		if not site.world_id.begins_with(prefix) or site.world_id.length() == prefix.length():
			violations.append("%s is not scoped to %s" % [site.world_id, prefix])
	assert_gt(_sites.size(), 0, "placements are found below District*/Geometry")
	_assert_no_violations(violations, "unique district-scoped world_ids")


## Proves no collision below the corridor soffit covers saved road or walk surface.
func test_collision_stays_off_road_and_walk_corridors() -> void:
	var collision: Array[Footprints.Footprint] = Footprints.of_kind(_footprints, true)
	assert_gt(collision.size(), 0)
	_assert_no_violations(_corridor_failures(collision), "collision clear of corridors")


## Proves low visual parts stay off the carriageway and the walk below canopy height.
func test_low_visual_parts_stay_off_road_and_walk_corridors() -> void:
	var visuals: Array[Footprints.Footprint] = Footprints.of_kind(_footprints, false)
	assert_gt(visuals.size(), 0)
	_assert_no_violations(_corridor_failures(visuals), "low visuals clear of corridors")


## Proves different placements keep the minimum collision gap; attached parts share one id.
func test_placements_keep_minimum_collision_gap() -> void:
	_assert_no_violations(_all_gap_failures(), "minimum placement collision gap")


## Proves every collision and visual footprint stays inside its district polygon.
func test_sector_footprints_stay_inside_district_bounds() -> void:
	_assert_no_violations(_district_failures(_footprints), "district containment")


## Proves saved spawn capsules and parked-car boxes do not intersect sector collision.
func test_spawn_and_parked_car_anchors_stay_clear_of_building_collision() -> void:
	for _frame: int in range(PHYSICS_SETTLE_FRAMES):
		await get_tree().physics_frame  # gdstyle:ignore=quality/await-in-loop
	var city_data: CityData = _match.get_node("CityData") as CityData
	var anchors: Array[Dictionary] = city_data.anchor_descriptors(WorldAnchor.KIND_PLAYER_SPAWN)
	anchors.append_array(city_data.anchor_descriptors(WorldAnchor.KIND_PARKED_CAR))
	assert_gt(anchors.size(), 0, "saved anchors are published")

	var violations := PackedStringArray()
	for descriptor: Dictionary in anchors:
		var hits: PackedStringArray = _anchor_hits(descriptor.kind, descriptor.transform)
		if not hits.is_empty():
			violations.append("%s intersects %s" % [descriptor.world_id, ", ".join(hits)])
	_assert_no_violations(violations, "anchor clearance")

	# The query must detect a building, or a clear result would prove nothing.
	var probe := Transform3D(Basis.IDENTITY, _sites[0].node.global_position)
	assert_false(
		_anchor_hits(WorldAnchor.KIND_PLAYER_SPAWN, probe).is_empty(),
		"a capsule inside a building is reported",
	)


## Proves each check rejects a constructed violation instead of passing vacuously.
func test_checks_reject_constructed_violations() -> void:
	var on_road: Footprints.Footprint = _square_footprint(
		Footprints.polygon_centroid(_road.polygons[0]),
		1.0,
	)
	assert_false(_corridor_failures([on_road]).is_empty(), "collision on a road fails")

	var site: Site = _sites[0]
	var neighbour: Footprints.Footprint = Footprints.shifted_copy(
		_site_collision(site)[0],
		_nearest_gap_shift(site),
	)
	neighbour.owner_id = site.world_id + "_constructed"
	assert_false(_gap_failures(neighbour, neighbour.owner_id).is_empty(), "0.5 m gap fails")

	var outside: Footprints.Footprint = _square_footprint(Vector2(10_000.0, 10_000.0), 1.0)
	outside.district_id = 1
	assert_false(_district_failures([outside]).is_empty(), "footprint outside its district fails")


## Builds the per-site clearance report and writes it when report mode is requested.
func test_clearance_report_covers_every_site() -> void:
	var candidates: Dictionary = _load_fit_candidates()
	var report: Dictionary = _build_report(candidates)
	assert_eq((report.sites as Array).size(), _sites.size(), "every site is reported")
	assert_eq((report.world_ids as Array).size(), _sites.size())
	assert_false(report.has("candidate_error"), str(report.get("candidate_error", "")))

	var report_path: String = OS.get_environment(REPORT_PATH_ENV)
	if not report_path.is_empty():
		var file: FileAccess = FileAccess.open(report_path, FileAccess.WRITE)
		assert_not_null(file, "report path opens for writing")
		if file != null:
			file.store_string(JSON.stringify(report, "\t") + "\n")
			file.close()
			gut.p("Brackett clearance report: " + report_path)


## Collects road and walk triangles from one saved ground sector by surface material.
func _scan_ground(sector: Node3D) -> void:
	for node: Node in sector.find_children("*", "MeshInstance3D", true, false):
		var mesh_instance: MeshInstance3D = node as MeshInstance3D
		var mesh: Mesh = mesh_instance.mesh
		for surface: int in mesh.get_surface_count():
			var material: Material = mesh_instance.get_active_material(surface)
			var material_name: String = material.resource_name if material != null else ""
			if material_name == ROAD_MATERIAL:
				_add_surface_triangles(mesh, surface, mesh_instance.global_transform, _road)
			elif material_name == WALK_MATERIAL:
				_add_surface_triangles(mesh, surface, mesh_instance.global_transform, _walk)


## Projects one indexed or unindexed mesh surface into XZ triangles.
func _add_surface_triangles(
	mesh: Mesh, surface: int, transform: Transform3D, index: Footprints.PolygonIndex
) -> void:
	var arrays: Array = mesh.surface_get_arrays(surface)
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var indices := PackedInt32Array(range(vertices.size()))
	if arrays[Mesh.ARRAY_INDEX] != null:
		indices = arrays[Mesh.ARRAY_INDEX]
	for corner: int in range(0, indices.size() - 2, 3):
		var triangle := PackedVector2Array()
		for offset: int in 3:
			var point: Vector3 = transform * vertices[indices[corner + offset]]
			triangle.append(Vector2(point.x, point.z))
		if Footprints.polygon_area(triangle) > 0.0:
			index.add(triangle)


## Records one district's placements under Geometry and any other sector content as dressing.
func _scan_district(district: Node3D) -> void:
	var district_id: int = int(district.get("district_id"))
	_district_nodes[district_id] = district
	for child: Node in district.get_children():
		if child.name == &"Geometry":
			for placement: Node in child.get_children():
				_scan_site(placement as Node3D, district_id)
		elif child is Node3D:
			var dressing: Array[Footprints.Footprint] = Footprints.collect_footprints(
				child, (child as Node3D).global_transform, _scan_failures
			)
			_assign_owner(dressing, "dressing:" + str(district.get_path_to(child)), district_id)
			_footprints.append_array(dressing)


## Records one placement's identity and its collision and visual footprints.
func _scan_site(placement: Node3D, district_id: int) -> void:
	var site := Site.new()
	site.node = placement
	site.world_id = String(placement.get("world_id"))
	site.asset_id = String(placement.get("asset_id"))
	site.district_id = district_id
	site.footprints = Footprints.collect_footprints(
		placement,
		placement.global_transform,
		_scan_failures,
	)
	_assign_owner(site.footprints, site.world_id, district_id)
	for footprint: Footprints.Footprint in site.footprints:
		footprint.is_placement = true
	_sites.append(site)
	_footprints.append_array(site.footprints)


## Labels footprints with the identity and district that own them.
func _assign_owner(
	footprints: Array[Footprints.Footprint],
	owner_id: String,
	district_id: int,
) -> void:
	for footprint: Footprints.Footprint in footprints:
		footprint.owner_id = owner_id
		footprint.district_id = district_id


## Lists corridor violations: low collision on road or walk, low visuals by height band.
func _corridor_failures(footprints: Array) -> PackedStringArray:
	var failures := PackedStringArray()
	for footprint: Footprints.Footprint in footprints:
		var road_limit: float = COLLISION_SOFFIT_CLEARANCE_M
		var walk_limit: float = COLLISION_SOFFIT_CLEARANCE_M
		if not footprint.is_collision:
			road_limit = ROAD_VISUAL_CLEARANCE_M
			walk_limit = WALK_VISUAL_CLEARANCE_M
		if footprint.bottom_m < road_limit:
			_append_overlap(failures, footprint, _road, "road")
		if footprint.bottom_m < walk_limit:
			_append_overlap(failures, footprint, _walk, "walk")
	return failures


## Appends one failure when a footprint covers more than the allowed surface area.
func _append_overlap(
	failures: PackedStringArray,
	footprint: Footprints.Footprint,
	surface: Footprints.PolygonIndex,
	label: String,
) -> void:
	var area: float = Footprints.overlap_area(footprint.polygon, surface)
	if area > MAX_SURFACE_OVERLAP_M2:
		failures.append(
			"%s %s %s covers %.3f m2 of %s" % [
				footprint.owner_id,
				"collision" if footprint.is_collision else "visual",
				footprint.source,
				area,
				label,
			]
		)


## Lists each placement pair closer than the minimum collision gap once.
func _all_gap_failures() -> PackedStringArray:
	var failures := PackedStringArray()
	for footprint: Footprints.Footprint in _collision_footprints:
		for failure: String in _gap_failures(footprint, footprint.owner_id):
			# Each pair is found from both sides; keep the ordered report.
			if footprint.owner_id < failure.get_slice(" ", 0):
				failures.append(failure)
	return failures


## Lists placements whose collision is closer than the minimum gap to one footprint.
func _gap_failures(footprint: Footprints.Footprint, own_id: String) -> PackedStringArray:
	var failures := PackedStringArray()
	var area: Rect2 = footprint.bounds.grow(MIN_PLACEMENT_GAP_M)
	for index: int in _collision_index.query(area):
		var other: Footprints.Footprint = _collision_footprints[index]
		if other.owner_id == own_id or not other.bounds.intersects(area):
			continue
		var gap: float = Footprints.polygon_distance(footprint.polygon, other.polygon)
		if gap < MIN_PLACEMENT_GAP_M:
			failures.append("%s is %.2f m from %s" % [other.owner_id, gap, own_id])
	return failures


## Lists footprints that spill outside their district polygon.
func _district_failures(footprints: Array) -> PackedStringArray:
	var failures := PackedStringArray()
	for footprint: Footprints.Footprint in footprints:
		var bound: PackedVector2Array = _district_polygons.get(footprint.district_id)
		var spill: float = Footprints.outside_area(footprint.polygon, bound)
		if spill > MAX_DISTRICT_SPILL_M2:
			failures.append(
				"%s %s spills %.3f m2 outside district %02d"
				% [footprint.owner_id, footprint.source, spill, footprint.district_id]
			)
	return failures


## Returns sector collision objects intersecting one anchor's envelope.
func _anchor_hits(kind: StringName, anchor: Transform3D) -> PackedStringArray:
	var query := PhysicsShapeQueryParameters3D.new()
	if kind == WorldAnchor.KIND_PARKED_CAR:
		var box := BoxShape3D.new()
		box.size = PARKED_CAR_BOX_SIZE_M
		query.shape = box
		query.transform = anchor.translated_local(Vector3.UP * PARKED_CAR_BOX_SIZE_M.y * 0.5)
	else:
		var capsule := CapsuleShape3D.new()
		capsule.radius = SPAWN_CAPSULE_RADIUS_M
		capsule.height = SPAWN_CAPSULE_HEIGHT_M
		query.shape = capsule
		query.transform = anchor.translated_local(Vector3.UP * SPAWN_CAPSULE_HEIGHT_M * 0.5)

	var space: PhysicsDirectSpaceState3D = _match.get_world_3d().direct_space_state
	var hits := PackedStringArray()
	for hit: Dictionary in space.intersect_shape(query, ANCHOR_QUERY_MAX_RESULTS):
		var collider: Node = hit.collider as Node
		if collider != null and _is_sector_content(collider):
			hits.append(str(_match.get_path_to(collider)))
	return hits


## Reports whether a node belongs to a district sector rather than ground or runtime actors.
func _is_sector_content(node: Node) -> bool:
	for district: Node3D in _district_nodes.values():
		if district.is_ancestor_of(node):
			return true
	return false


## Builds the identity, anchor and per-site clearance report, with fits when requested.
func _build_report(candidates: Dictionary) -> Dictionary:
	var world_ids: Array[String] = []
	for site: Site in _sites:
		world_ids.append(site.world_id)
	world_ids.sort()

	var prefab_cache: Dictionary[String, Array] = {}
	var site_rows: Array[Dictionary] = []
	for site: Site in _sites:
		var row: Dictionary = _site_report(site)
		var choices: Array = _site_candidates(site, candidates)
		if not choices.is_empty():
			row.fit = _fit_report(site, choices, prefab_cache)
		site_rows.append(row)

	var report: Dictionary = {
		"schema": REPORT_SCHEMA,
		"engine": Engine.get_version_info().string,
		"identity": _identity_report(world_ids),
		"world_ids": world_ids,
		"checks": _check_report(),
		"sites": site_rows,
	}
	if candidates.has("error"):
		report.candidate_error = candidates.error
	return report


## Returns every current check failure so a lane can review a failing state in one file.
func _check_report() -> Dictionary:
	return {
		"scan": _scan_failures,
		"corridors": _corridor_failures(_footprints),
		"placement_gaps": _all_gap_failures(),
		"district_bounds": _district_failures(_footprints),
	}


## Compares current world_ids with an earlier report, or with the frozen authoring placements.
func _identity_report(world_ids: Array[String]) -> Dictionary:
	var base_source: String = OS.get_environment(BASE_REPORT_ENV)
	var base_ids: Array = []
	if base_source.is_empty():
		base_source = AUTHORING_INPUT_PATH
		for placement: Dictionary in _authoring.placements:
			base_ids.append(String(placement.world_id))
	else:
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(base_source))
		base_ids = parsed.get("world_ids", []) if parsed is Dictionary else []

	var current: Dictionary[String, bool] = {}
	for world_id: String in world_ids:
		current[world_id] = true
	var base: Dictionary[String, bool] = {}
	for world_id: Variant in base_ids:
		base[String(world_id)] = true
	var added: Array = world_ids.filter(func(id: String) -> bool: return not base.has(id))
	var retired: Array = base.keys().filter(func(id: String) -> bool: return not current.has(id))
	retired.sort()
	return {
		"base": base_source,
		"count": world_ids.size(),
		"base_count": base.size(),
		"added": added,
		"retired": retired,
	}


## Reports one site's transform and its current clearance margins.
func _site_report(site: Site) -> Dictionary:
	var collision: Array[Footprints.Footprint] = _site_collision(site)
	return {
		"world_id": site.world_id,
		"asset_id": site.asset_id,
		"district_id": site.district_id,
		"position": [
			snappedf(site.node.global_position.x, FIT_SNAP_M),
			snappedf(site.node.global_position.z, FIT_SNAP_M),
		],
		"yaw_degrees": snappedf(rad_to_deg(site.node.global_basis.get_euler().y), FIT_SNAP_M),
		"front_axis": _front_axis_name(_front_axis(site)),
		"margins_m": {
			"road": _surface_margin(collision, _road),
			"walk": _surface_margin(collision, _walk),
			"placement": _placement_margin(collision, site.world_id),
			"district_edge": _district_margin(collision, site.district_id),
		},
	}


## Returns the nearest corridor distance, capped at the report search radius.
func _surface_margin(
	collision: Array[Footprints.Footprint],
	surface: Footprints.PolygonIndex,
) -> float:
	var margin: float = REPORT_SEARCH_RADIUS_M
	for footprint: Footprints.Footprint in collision:
		for index: int in surface.query(footprint.bounds.grow(REPORT_SEARCH_RADIUS_M)):
			margin = minf(
				margin,
				Footprints.polygon_distance(footprint.polygon, surface.polygons[index]),
			)
	return snappedf(margin, FIT_SNAP_M)


## Returns the nearest other placement's collision distance, capped at the search radius.
func _placement_margin(collision: Array[Footprints.Footprint], own_id: String) -> float:
	var margin: float = REPORT_SEARCH_RADIUS_M
	for footprint: Footprints.Footprint in collision:
		for index: int in _collision_index.query(footprint.bounds.grow(REPORT_SEARCH_RADIUS_M)):
			var other: Footprints.Footprint = _collision_footprints[index]
			if other.owner_id != own_id:
				margin = minf(margin, Footprints.polygon_distance(footprint.polygon, other.polygon))
	return snappedf(margin, FIT_SNAP_M)


## Returns the nearest district-boundary distance of a site's collision.
func _district_margin(collision: Array[Footprints.Footprint], district_id: int) -> float:
	var margin: float = INF
	for footprint: Footprints.Footprint in collision:
		margin = minf(
			margin, Footprints.boundary_distance(footprint.polygon, _district_polygons[district_id])
		)
	return snappedf(margin, FIT_SNAP_M) if margin != INF else 0.0


## Loads the optional fit-candidate file; returns an `error` entry instead of failing late.
func _load_fit_candidates() -> Dictionary:
	var path: String = OS.get_environment(CANDIDATES_PATH_ENV)
	if path.is_empty():
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		return { "error": "fit candidates are not a JSON object: " + path }
	var candidates: Dictionary = parsed
	if candidates.get("schema") != float(REPORT_SCHEMA):
		return { "error": "fit candidates need schema %d: %s" % [REPORT_SCHEMA, path] }
	var pattern := RegEx.create_from_string("^[a-z0-9_]+$")
	for group: String in ["by_asset", "by_world_id"]:
		for prefab_ids: Variant in (candidates.get(group, {}) as Dictionary).values():
			if (not prefab_ids is Array
					or (prefab_ids as Array).size() > MAX_FIT_CANDIDATES_PER_SITE):
				return { "error": "%s entries must be arrays of at most %d ids" % [
					group, MAX_FIT_CANDIDATES_PER_SITE,
				] }
			for prefab_id: Variant in prefab_ids:
				var id: String = str(prefab_id)
				if pattern.search(id) == null or not ResourceLoader.exists(_prefab_path(id)):
					return { "error": "unknown production prefab id: " + id }
	return candidates


## Returns the ordered candidate prefab ids for one site, honouring the district filter.
func _site_candidates(site: Site, candidates: Dictionary) -> Array:
	if candidates.is_empty() or candidates.has("error"):
		return []
	var districts: Array = candidates.get("districts", [])
	if not districts.is_empty() and not districts.has(float(site.district_id)):
		return []
	var by_world_id: Dictionary = candidates.get("by_world_id", {})
	if by_world_id.has(site.world_id):
		return by_world_id[site.world_id]
	return (candidates.get("by_asset", {}) as Dictionary).get(site.asset_id, [])


## Evaluates each candidate prefab at road-facing-first yaws and two offset modes.
func _fit_report(site: Site, prefab_ids: Array, cache: Dictionary[String, Array]) -> Dictionary:
	var greybox_local: Rect2 = _local_bounds(site, _site_collision(site))
	var front: Vector2 = _front_axis(site)
	var facing: float = _facing_yaw(front)
	var options: Array[Dictionary] = []
	var suggestion: Dictionary = {}
	for prefab_id: String in prefab_ids:
		if not cache.has(prefab_id):
			cache[prefab_id] = _prefab_footprints(prefab_id)
		if cache[prefab_id].is_empty():
			var failure: String = "no footprints or an unsupported collision shape"
			options.append({ "prefab": prefab_id, "fits": false, "failures": [failure] })
			continue
		for step: float in FIT_YAW_STEPS_DEG:
			var yaw: float = fposmod(facing + step, 360.0)
			for road_face: bool in [true, false]:
				var option: Dictionary = _fit_option(prefab_id, cache[prefab_id], yaw, facing)
				option.offset_mode = "road_face" if road_face else "centred"
				_place_option(option, site, greybox_local, front, road_face)
				options.append(option)
				if suggestion.is_empty() and option.fits:
					suggestion = option
	return { "suggestion": suggestion, "options": options }


## Creates one fit option record with the prefab's local footprints rotated by yaw.
func _fit_option(
	prefab_id: String, local: Array, yaw_degrees: float, facing_yaw: float
) -> Dictionary:
	var rotation := Transform3D(Footprints.quarter_turn_basis(yaw_degrees), Vector3.ZERO)
	var rotated: Array[Footprints.Footprint] = []
	for footprint: Footprints.Footprint in local:
		rotated.append(Footprints.transformed_copy(footprint, rotation))
	return {
		"prefab": prefab_id,
		"yaw_degrees": yaw_degrees,
		"facing_road": is_equal_approx(yaw_degrees, facing_yaw),
		"rotated": rotated,
	}


## Offsets a rotated option inside the greybox site frame, then runs every placement check.
func _place_option(
	option: Dictionary, site: Site, greybox: Rect2, front: Vector2, road_face: bool
) -> void:
	var rotated: Array[Footprints.Footprint] = option.rotated
	option.erase("rotated")
	var collision: Array[Footprints.Footprint] = Footprints.of_kind(rotated, true)
	var prefab: Rect2 = Footprints.union_bounds(collision if not collision.is_empty() else rotated)
	var offset: Vector2 = greybox.get_center() - prefab.get_center()
	if road_face and front.x != 0.0:
		offset.x = (greybox.end.x - prefab.end.x) if front.x > 0.0 else (
			greybox.position.x - prefab.position.x
		)
	elif road_face:
		offset.y = (greybox.end.y - prefab.end.y) if front.y > 0.0 else (
			greybox.position.y - prefab.position.y
		)
	var offset_x: float = snappedf(offset.x, FIT_SNAP_M)
	var offset_z: float = snappedf(offset.y, FIT_SNAP_M)
	offset = Vector2(offset_x, offset_z)
	var child := Transform3D(
		Footprints.quarter_turn_basis(option.yaw_degrees), Vector3(offset_x, 0.0, offset_z)
	)
	var placed: Array[Footprints.Footprint] = []
	for footprint: Footprints.Footprint in rotated:
		var world: Footprints.Footprint = Footprints.transformed_copy(
			footprint,
			site.node.global_transform,
		)
		_shift_in_site(world, site, offset)
		world.owner_id = site.world_id
		world.district_id = site.district_id
		placed.append(world)
	var failures: PackedStringArray = _corridor_failures(placed)
	failures.append_array(_district_failures(placed))
	for footprint: Footprints.Footprint in Footprints.of_kind(placed, true):
		failures.append_array(_gap_failures(footprint, site.world_id))
	option.offset_xz = [offset_x, offset_z]
	option.asset_child_transform = var_to_str(child)
	option.fits = failures.is_empty()
	option.failures = failures.slice(0, MAX_LISTED_VIOLATIONS)


## Moves a world footprint by a site-local XZ offset.
func _shift_in_site(footprint: Footprints.Footprint, site: Site, offset: Vector2) -> void:
	var basis: Basis = site.node.global_basis
	var world_offset: Vector3 = basis.x * offset.x + basis.z * offset.y
	var shifted: Footprints.Footprint = Footprints.shifted_copy(
		footprint,
		Vector2(world_offset.x, world_offset.z),
	)
	footprint.polygon = shifted.polygon
	footprint.bounds = shifted.bounds


## Measures a production prefab in its own root frame; unsupported shapes yield no footprints.
func _prefab_footprints(prefab_id: String) -> Array:
	var packed: PackedScene = load(_prefab_path(prefab_id)) as PackedScene
	var instance: Node = packed.instantiate()
	var failures := PackedStringArray()
	var footprints: Array[Footprints.Footprint] = Footprints.collect_footprints(
		instance, Transform3D.IDENTITY, failures
	)
	instance.free()
	return footprints if failures.is_empty() else []


## Returns the conventional saved path of a production environment prefab.
func _prefab_path(prefab_id: String) -> String:
	return PREFAB_DIRECTORY + prefab_id + ".tscn"


## Returns the site-local XZ bounds of world footprints.
func _local_bounds(site: Site, footprints: Array[Footprints.Footprint]) -> Rect2:
	var to_local: Transform3D = site.node.global_transform.affine_inverse()
	var local: Array[Footprints.Footprint] = []
	for footprint: Footprints.Footprint in footprints:
		local.append(Footprints.transformed_copy(footprint, to_local))
	return Footprints.union_bounds(local)


## Returns the site-local axis (+-X or +-Z) pointing to the nearest carriageway.
func _front_axis(site: Site) -> Vector2:
	var origin: Vector3 = site.node.global_position
	var centre := Vector2(origin.x, origin.z)
	var nearest: Vector2 = centre + Vector2(0.0, -1.0)
	var best: float = INF
	var search := Rect2(centre, Vector2.ZERO).grow(REPORT_SEARCH_RADIUS_M * 2.0)
	for index: int in _road.query(search):
		var triangle: PackedVector2Array = _road.polygons[index]
		for corner: int in 3:
			var point: Vector2 = Geometry2D.get_closest_point_to_segment(
				centre, triangle[corner], triangle[(corner + 1) % 3]
			)
			if point.distance_squared_to(centre) < best:
				best = point.distance_squared_to(centre)
				nearest = point
	var local: Vector3 = site.node.global_basis.inverse() * Vector3(
		nearest.x - centre.x, 0.0, nearest.y - centre.y
	)
	if absf(local.x) > absf(local.z):
		return Vector2(signf(local.x), 0.0)
	return Vector2(0.0, signf(local.z) if local.z != 0.0 else -1.0)


## Returns the prefab yaw whose front (-Z) points along a site-local axis.
func _facing_yaw(front: Vector2) -> float:
	if front.y < 0.0:
		return 0.0
	if front.y > 0.0:
		return 180.0
	return 90.0 if front.x < 0.0 else 270.0


## Names a site-local axis for report readers.
func _front_axis_name(front: Vector2) -> String:
	if front.x != 0.0:
		return "+X" if front.x > 0.0 else "-X"
	return "+Z" if front.y > 0.0 else "-Z"


## Returns a site's collision footprints.
func _site_collision(site: Site) -> Array[Footprints.Footprint]:
	return Footprints.of_kind(site.footprints, true)


## Builds a ground-level collision square used by constructed-violation proofs.
func _square_footprint(centre: Vector2, half_size: float) -> Footprints.Footprint:
	var half := Vector3(half_size, 1.0, half_size)
	var points: PackedVector3Array = Footprints.box_points(-half, half)
	var world := Transform3D(Basis.IDENTITY, Vector3(centre.x, 0.0, centre.y))
	var footprint: Footprints.Footprint = Footprints.make_footprint(
		points, world, true, "constructed"
	)
	footprint.owner_id = "constructed"
	footprint.is_placement = true
	return footprint


## Returns a shift that leaves a copy of the site's first box 0.5 m beyond its +X face.
func _nearest_gap_shift(site: Site) -> Vector2:
	var footprint: Footprints.Footprint = _site_collision(site)[0]
	var axis: Vector3 = site.node.global_basis.x
	var width: float = 0.0
	for point: Vector2 in footprint.polygon:
		var along: float = (point - footprint.bounds.get_center()).dot(Vector2(axis.x, axis.z))
		width = maxf(width, along * 2.0)
	var shift: float = width + MIN_PLACEMENT_GAP_M * 0.5
	return Vector2(axis.x, axis.z) * shift


## Fails with a bounded list of violations so large regressions stay readable.
func _assert_no_violations(violations: PackedStringArray, label: String) -> void:
	var listed: String = "\n".join(violations.slice(0, MAX_LISTED_VIOLATIONS))
	assert_eq(violations.size(), 0, "%s: %d violations\n%s" % [label, violations.size(), listed])


## One saved building placement and the footprints of everything below it.
class Site:
	var world_id: String
	var asset_id: String
	var district_id: int
	var node: Node3D
	var footprints: Array[Footprints.Footprint] = []
