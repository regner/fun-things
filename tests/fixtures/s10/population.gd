class_name S10Population
extends RefCounted
## Deterministic host-owned pedestrian AI experiment over admitted S06 foot graph data.

const PEDESTRIAN_SCENE: PackedScene = preload("res://tests/fixtures/s10/pedestrian.tscn")
const POPULATION_COUNT: int = 64
const DEAD_RETENTION_CAP: int = 16
const TICKS_PER_SECOND: int = 60
const SIMULATION_TICKS: int = 10 * 60 * TICKS_PER_SECOND
const PERCEPTION_INTERVAL_TICKS: int = 6
const PANIC_TICKS: int = 5 * TICKS_PER_SECOND
const REPLENISH_DELAY_TICKS: int = 5 * TICKS_PER_SECOND
const STUCK_WINDOW_TICKS: int = 4 * TICKS_PER_SECOND
const EVENT_LIFETIME_TICKS: int = PERCEPTION_INTERVAL_TICKS
const NORMAL_EVENT_INTERVAL_TICKS: int = 20 * TICKS_PER_SECOND
const BLAST_INTERVAL_TICKS: int = 120 * TICKS_PER_SECOND
const STORM_EVENT_INTERVAL_TICKS: int = 5 * TICKS_PER_SECOND
const OVERLAP_SAMPLE_INTERVAL_TICKS: int = TICKS_PER_SECOND
const WALK_SPEED_MPS: float = 1.5
const FLEE_SPEED_MPS: float = 3.0
const AGENT_RADIUS_M: float = 0.38
const AUTHORED_FOOT_HALF_WIDTH_M: float = 2.0
const LEGAL_CENTER_HALF_WIDTH_M: float = AUTHORED_FOOT_HALF_WIDTH_M - AGENT_RADIUS_M
const MOTION_CENTER_HALF_WIDTH_M: float = 1.55
const SEPARATION_RADIUS_M: float = 1.2
const CROSSING_CAR_CLEARANCE_M: float = 5.0
const CAR_HALF_WIDTH_M: float = 0.9
const CAR_HALF_LENGTH_M: float = 1.7
const CAR_TRAVEL_HALF_LENGTH_M: float = 20.0
const GRID_CELL_M: float = 1.5
const FOOT_METRIC_TOLERANCE_M: float = 0.001
const ROUTE_LOOKAHEAD_POINTS: int = 8
const ROUTE_SEARCH_POINTS: int = 16
const MOTION_GRAPH: String = "graph_kinematic"
const MOTION_CHARACTER: String = "character_body"
const CROSSING_LINK_ID: StringName = &"s06/foot/crossing"

var _fixture: Dictionary = {}
var _graph: Dictionary = {}
var _agents: Array[Dictionary] = []
var _dead_presentations: Array[S10Pedestrian] = []
var _replenishments: Array[Dictionary] = []
var _events: Array[Dictionary] = []
var _event_expectations: Dictionary = {}
var _timings_usec: Array[int] = []
var _flee_latencies_ticks: Array[int] = []
var _stuck_ids: Dictionary = {}
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()
var _next_identity: int = 1
var _next_event: int = 1
var _metrics: Dictionary = {}


## Runs one ten-minute seed from admitted S06 route, legal-region and road geometry.
func run_case(root: Node3D, graph: Dictionary, seed: int, motion: String,
		storm: bool) -> Dictionary:
	_reset(root, graph, seed)
	_spawn_initial_population()
	for tick: int in SIMULATION_TICKS:
		var started_usec: int = Time.get_ticks_usec()
		_tick(tick, motion, storm)
		_timings_usec.append(Time.get_ticks_usec() - started_usec)
		if tick % OVERLAP_SAMPLE_INTERVAL_TICKS == 0:
			_sample_overlaps()
		if tick > 0 and tick % STUCK_WINDOW_TICKS == 0:
			_sample_stuck(tick)

	var result: Dictionary = _result(seed, motion, storm)
	_dispose()
	return result


## Rejects missing route semantics, crossing identity or independently supplied regions.
static func graph_errors(graph: Dictionary) -> Array[String]:  # gdstyle:ignore=quality/max-branches
	var failures: Array[String] = []
	if not graph.has_all([
		"route_points", "link_ids", "crossing_range", "legal_regions", "roads"]):
		return ["graph input omitted required S06 route or region fields"]
	if typeof(graph.route_points) != TYPE_PACKED_VECTOR3_ARRAY or graph.route_points.size() < 2:
		failures.append("S06 foot route needs at least two world points")
	if CROSSING_LINK_ID not in graph.link_ids:
		failures.append("S06 foot route omitted the authored crossing link")
	if typeof(graph.crossing_range) != TYPE_VECTOR2I or graph.crossing_range.x < 0 or (
		graph.crossing_range.y <= graph.crossing_range.x):
		failures.append("S06 crossing range was invalid")
	var route_points: PackedVector3Array = graph.route_points
	for point: Vector3 in route_points:
		if not point.is_finite():
			failures.append("S06 foot route contained a nonfinite point")
			break
	var crossing_regions: int = 0
	var previous_end: Vector3 = route_points[0] if not route_points.is_empty() else Vector3.ZERO
	for region: Dictionary in graph.legal_regions:
		if not region.has_all(["kind", "points"]):
			failures.append("legal region omitted kind or graph points")
			continue
		if typeof(region.points) != TYPE_PACKED_VECTOR3_ARRAY or region.points.size() < 2:
			failures.append("legal region needs at least two graph points")
			continue
		var points: PackedVector3Array = region.points
		if points[0].distance_to(previous_end) > FOOT_METRIC_TOLERANCE_M:
			failures.append("legal foot regions did not follow the admitted route continuously")
		previous_end = points[-1]
		if region.kind == "CROSSING":
			crossing_regions += 1
	if crossing_regions != 1:
		failures.append("graph input needs exactly one authored crossing region")
	if not route_points.is_empty() and previous_end.distance_to(route_points[-1]) > (
		FOOT_METRIC_TOLERANCE_M):
		failures.append("legal foot regions did not end at the admitted route destination")
	if graph.roads.is_empty():
		failures.append("S06 map roads are required for independent road occupancy")
	return failures


## Fails empty, partial or late threat receipts, including the zero-reaction regression.
static func reaction_failures(expectations: Dictionary,
		latencies_ticks: Array[int]) -> Array[String]:
	var failures: Array[String] = []
	if expectations.is_empty():
		failures.append("no threat events were injected")
	var expected_total: int = 0
	var observed_total: int = 0
	for event_id: Variant in expectations:
		var expectation: Dictionary = expectations[event_id]
		var expected: int = int(expectation.expected)
		var observed: int = int(expectation.observed)
		expected_total += expected
		observed_total += observed
		if expected <= 0:
			failures.append("threat event %s had no eligible reactions" % event_id)
		elif observed != expected:
			failures.append("threat event %s observed %d of %d reactions" % [
				event_id, observed, expected])
	if expected_total <= 0 or observed_total <= 0 or latencies_ticks.is_empty():
		failures.append("flee reactions were absent")
	elif latencies_ticks.max() >= PERCEPTION_INTERVAL_TICKS:
		failures.append("flee reaction exceeded the six-phase perception bound")
	return failures


## Clears per-case state while compiling graph-derived segments for bounded hot queries.
func _reset(root: Node3D, graph: Dictionary, seed: int) -> void:
	_fixture = {
		"population": root.get_node("Population") as Node3D,
		"dead": root.get_node("DeadPresentations") as Node3D,
		"car": root.get_node("CrossingCar") as AnimatableBody3D,
	}
	_graph = graph.duplicate(true)
	_graph.legal_segments = _compile_legal_segments(graph.legal_regions)
	_graph.road_segments = _compile_road_segments(graph.roads)
	_graph.crossing_center = _region_midpoint(graph.legal_regions, "CROSSING")
	_rng.seed = seed
	_agents.clear()
	_dead_presentations.clear()
	_replenishments.clear()
	_events.clear()
	_event_expectations.clear()
	_timings_usec.clear()
	_flee_latencies_ticks.clear()
	_stuck_ids.clear()
	_next_identity = 1
	_next_event = 1
	_metrics = {
		"min_live": POPULATION_COUNT,
		"max_live": POPULATION_COUNT,
		"max_dead": 0,
		"deaths": 0,
		"blast_deaths": 0,
		"car_hits": 0,
		"replacements": 0,
		"crossing_wait_ticks": 0,
		"off_sidewalk_ticks": 0,
		"road_outside_crossing_ticks": 0,
		"overlap_pair_samples": 0,
		"max_overlap_pairs": 0,
		"overlap_samples": 0,
	}


## Creates 64 capsule instances at graph-derived positions in four lateral lanes.
func _spawn_initial_population() -> void:
	var points: PackedVector3Array = _graph.route_points
	for index: int in POPULATION_COUNT:
		var column: int = index / 4
		var lane: int = index % 4
		var fraction: float = (float(column) + 0.5) / 16.0
		var route_index: int = clampi(roundi(fraction * float(points.size() - 1)),
			1, points.size() - 2)
		var lateral: float = -1.2 + float(lane) * 0.8
		var direction: int = 1 if lane % 2 == 0 else -1
		var position: Vector3 = _route_pose(route_index, lateral)
		_agents.append(_new_agent(position, route_index, direction, lateral, index))


## Builds one host-owned AI slot around an instance of the saved capsule scene.
func _new_agent(position: Vector3, route_index: int, direction: int, lateral: float,
		phase: int) -> Dictionary:
	var body: S10Pedestrian = PEDESTRIAN_SCENE.instantiate() as S10Pedestrian
	(_fixture.population as Node3D).add_child(body)
	body.install_position(position)
	var identity: int = _next_identity
	_next_identity += 1
	return {
		"id": identity,
		"body": body,
		"alive": true,
		"direction": direction,
		"route_index": route_index,
		"lateral": lateral,
		"phase": phase % PERCEPTION_INTERVAL_TICKS,
		"panic_until": -1,
		"threat_position": Vector2.ZERO,
		"last_event": 0,
		"checkpoint": position,
		"checkpoint_tick": 0,
	}


## Advances event injection, graph steering, motion, lifecycle and bounded metrics.
func _tick(tick: int, mode: String, flee: bool) -> void:
	_inject_events(tick, flee)
	_expire_events(tick)
	_replenish(tick)
	var crossing: Vector3 = _graph.crossing_center
	var car_z: float = crossing.z - CAR_TRAVEL_HALF_LENGTH_M + fmod(
		float(tick) * 8.0 / TICKS_PER_SECOND, CAR_TRAVEL_HALF_LENGTH_M * 2.0)
	var car_body: AnimatableBody3D = _fixture.car
	car_body.position.x = crossing.x
	car_body.position.z = car_z
	var grid: Dictionary = _build_grid()
	for index: int in _agents.size():
		_advance_agent(index, tick, mode, car_z, grid)

	_update_live_bounds()


## Advances one live slot from graph progress through the selected motion adapter.
func _advance_agent(index: int, tick: int, mode: String, car_z: float,
		grid: Dictionary) -> void:
	var agent: Dictionary = _agents[index]
	if not agent.alive:
		return

	_perceive(agent, tick)
	var body: S10Pedestrian = agent.body
	var position: Vector3 = body.global_position
	_update_route_index(agent, position)
	var velocity: Vector2 = _desired_velocity(agent, position, car_z, tick)
	velocity += _separation(index, position, grid)
	var speed_limit: float = FLEE_SPEED_MPS if tick < agent.panic_until else WALK_SPEED_MPS
	velocity = velocity.limit_length(speed_limit)
	var proposed: Vector3 = position + (
		Vector3(velocity.x, 0.0, velocity.y) / TICKS_PER_SECOND)
	var next: Vector3 = _constrain_to_route(proposed, agent)
	_move(body, next - position, mode)
	_measure_position(agent)
	if tick < SIMULATION_TICKS - REPLENISH_DELAY_TICKS and (
		_car_overlaps(body.global_position, car_z)):
		_kill(index, tick, "car")


## Injects graph-positioned normal threats or a repeated all-population flee storm.
func _inject_events(tick: int, storm: bool) -> void:
	var crossing: Vector3 = _graph.crossing_center
	if storm and tick % STORM_EVENT_INTERVAL_TICKS == 0:
		_add_event(tick, Vector2(crossing.x, crossing.z), 100.0, "gunfire")
		return
	if storm:
		return

	if tick > 0 and tick % BLAST_INTERVAL_TICKS == 0:
		var blast_position: Vector2 = _random_route_position()
		_kill_nearest(blast_position, tick, 4)
		_add_event(tick, blast_position, 16.0, "blast")
	if tick % NORMAL_EVENT_INTERVAL_TICKS == 0:
		_add_event(tick, _random_route_position(), 12.0, "gunfire")


## Selects a deterministic threat position from the admitted route instead of world constants.
func _random_route_position() -> Vector2:
	var points: PackedVector3Array = _graph.route_points
	var margin: int = mini(16, (points.size() - 1) / 4)
	var index: int = _rng.randi_range(margin, points.size() - 1 - margin)
	return Vector2(points[index].x, points[index].z)


## Adds a threat and independently records every currently eligible live reaction.
func _add_event(tick: int, position: Vector2, radius_m: float, kind: String) -> void:
	var identity: int = _next_event
	var targets: Dictionary = _eligible_reaction_ids(position, radius_m)
	_events.append({
		"id": identity,
		"tick": tick,
		"expires": tick + EVENT_LIFETIME_TICKS,
		"position": position,
		"radius": radius_m,
		"kind": kind,
		"targets": targets,
	})
	_event_expectations[identity] = {
		"kind": kind,
		"expected": targets.size(),
		"observed": 0,
	}
	_next_event += 1


## Captures stable target identities from live real positions at publication time.
func _eligible_reaction_ids(position: Vector2, radius_m: float) -> Dictionary:
	var targets: Dictionary = {}
	for agent: Dictionary in _agents:
		if not agent.alive:
			continue
		var body_position: Vector3 = (agent.body as S10Pedestrian).global_position
		if position.distance_to(Vector2(body_position.x, body_position.z)) <= radius_m:
			targets[agent.id] = true
	return targets


## Removes threats after every stagger phase had exactly one opportunity to observe them.
func _expire_events(tick: int) -> void:
	for index: int in range(_events.size() - 1, -1, -1):
		if tick >= int(_events[index].expires):
			_events.remove_at(index)


## Applies bounded 10 Hz perception while preserving 60 Hz movement for every live slot.
func _perceive(agent: Dictionary, tick: int) -> void:
	if tick % PERCEPTION_INTERVAL_TICKS != int(agent.phase):
		return

	for event: Dictionary in _events:
		if int(event.id) <= int(agent.last_event):
			continue
		if not (event.targets as Dictionary).has(agent.id):
			continue

		agent.last_event = event.id
		agent.panic_until = tick + PANIC_TICKS
		agent.threat_position = event.position
		_flee_latencies_ticks.append(tick - int(event.tick))
		var expectation: Dictionary = _event_expectations[event.id]
		expectation.observed = int(expectation.observed) + 1
		_event_expectations[event.id] = expectation


## Combines graph tangent following, crossing-gap waits and direction-away fleeing.
func _desired_velocity(agent: Dictionary, position: Vector3, car_z: float,
		tick: int) -> Vector2:
	var points: PackedVector3Array = _graph.route_points
	var direction: int = int(agent.direction)
	if int(agent.route_index) <= 1 and direction < 0:
		direction = 1
	elif int(agent.route_index) >= points.size() - 2 and direction > 0:
		direction = -1
	agent.direction = direction
	var target_index: int = clampi(int(agent.route_index) + direction * ROUTE_LOOKAHEAD_POINTS,
		0, points.size() - 1)
	var target: Vector3 = points[target_index]
	var route_direction: Vector2 = Vector2(target.x - position.x, target.z - position.z)
	if route_direction.length_squared() < 0.001:
		route_direction = _route_tangent(int(agent.route_index)) * float(direction)
	var velocity: Vector2 = route_direction.normalized() * WALK_SPEED_MPS
	var crossing_range: Vector2i = _graph.crossing_range
	var entering_crossing: bool = (
		direction > 0 and int(agent.route_index) < crossing_range.x and (
			target_index >= crossing_range.x)) or (
		direction < 0 and int(agent.route_index) > crossing_range.y and (
			target_index <= crossing_range.y))
	var crossing: Vector3 = _graph.crossing_center
	if entering_crossing and absf(car_z - crossing.z) < CROSSING_CAR_CLEARANCE_M:
		velocity = Vector2.ZERO
		_metrics.crossing_wait_ticks += 1
	if tick < int(agent.panic_until):
		var away: Vector2 = Vector2(position.x, position.z) - agent.threat_position
		if away.length_squared() < 0.01:
			away = _route_tangent(int(agent.route_index)) * float(direction)
		velocity = (route_direction.normalized() * 0.35 + away.normalized()).normalized() * (
			FLEE_SPEED_MPS)

	return velocity


## Builds a bounded local-neighbor grid used by both measured movement options.
func _build_grid() -> Dictionary:
	var grid: Dictionary = {}
	for index: int in _agents.size():
		var agent: Dictionary = _agents[index]
		if not agent.alive:
			continue

		var position: Vector3 = (agent.body as S10Pedestrian).global_position
		var key: Vector2i = _grid_key(position)
		if not grid.has(key):
			grid[key] = []
		(grid[key] as Array).append(index)

	return grid


## Returns simple bounded separation steering without delegating gameplay to engine RVO.
func _separation(index: int, position: Vector3, grid: Dictionary) -> Vector2:
	var steering: Vector2 = Vector2.ZERO
	var key: Vector2i = _grid_key(position)
	for offset_x: int in range(-1, 2):
		for offset_y: int in range(-1, 2):
			var bucket_key: Vector2i = key + Vector2i(offset_x, offset_y)
			if not grid.has(bucket_key):
				continue
			for other_index: int in grid[bucket_key]:
				if other_index == index:
					continue
				var other: Dictionary = _agents[other_index]
				var other_position: Vector3 = (other.body as S10Pedestrian).global_position
				var offset: Vector2 = Vector2(position.x - other_position.x,
					position.z - other_position.z)
				var distance: float = offset.length()
				if distance > 0.001 and distance < SEPARATION_RADIUS_M:
					steering += offset / distance * (SEPARATION_RADIUS_M - distance)

	return steering * 2.0


## Maps a world position to the fixed-size local separation grid.
func _grid_key(position: Vector3) -> Vector2i:
	return Vector2i(floori(position.x / GRID_CELL_M), floori(position.z / GRID_CELL_M))


## Updates graph progress from the nearest admitted route point in a bounded window.
func _update_route_index(agent: Dictionary, position: Vector3) -> void:
	var points: PackedVector3Array = _graph.route_points
	var current: int = int(agent.route_index)
	var first: int = maxi(0, current - ROUTE_SEARCH_POINTS)
	var last: int = mini(points.size() - 1, current + ROUTE_SEARCH_POINTS)
	var nearest_index: int = current
	var nearest_distance: float = INF
	for index: int in range(first, last + 1):
		var distance: float = position.distance_squared_to(points[index])
		if distance < nearest_distance:
			nearest_distance = distance
			nearest_index = index
	agent.route_index = nearest_index


## Projects proposed motion onto the admitted route corridor rather than fixed world bounds.
func _constrain_to_route(position: Vector3, agent: Dictionary) -> Vector3:
	var projection: Dictionary = _nearest_route_projection(position, int(agent.route_index))
	agent.route_index = projection.index
	var centre: Vector3 = projection.position
	var offset: Vector2 = Vector2(position.x - centre.x, position.z - centre.z)
	if offset.length() > MOTION_CENTER_HALF_WIDTH_M:
		offset = offset.normalized() * MOTION_CENTER_HALF_WIDTH_M
	return Vector3(centre.x + offset.x, 0.001, centre.z + offset.y)


## Finds the closest projection on graph segments around current progress with finite work.
func _nearest_route_projection(position: Vector3, route_index: int) -> Dictionary:
	var points: PackedVector3Array = _graph.route_points
	var first: int = maxi(0, route_index - ROUTE_SEARCH_POINTS)
	var point_2d: Vector2 = Vector2(position.x, position.z)
	var nearest: Vector2 = Vector2(points[route_index].x, points[route_index].z)
	var nearest_index: int = route_index
	var nearest_distance: float = INF
	for index: int in range(first,
			mini(points.size() - 2, route_index + ROUTE_SEARCH_POINTS) + 1):
		var start: Vector2 = Vector2(points[index].x, points[index].z)
		var finish: Vector2 = Vector2(points[index + 1].x, points[index + 1].z)
		var candidate: Vector2 = Geometry2D.get_closest_point_to_segment(
			point_2d, start, finish)
		var distance: float = point_2d.distance_squared_to(candidate)
		if distance < nearest_distance:
			nearest = candidate
			nearest_distance = distance
			nearest_index = index
	return { "position": Vector3(nearest.x, 0.001, nearest.y), "index": nearest_index }


## Produces a graph point offset along the local normal for authored initial lanes.
func _route_pose(route_index: int, lateral: float) -> Vector3:
	var point: Vector3 = (_graph.route_points as PackedVector3Array)[route_index]
	var tangent: Vector2 = _route_tangent(route_index)
	var normal: Vector2 = Vector2(-tangent.y, tangent.x)
	return Vector3(point.x + normal.x * lateral, 0.001, point.z + normal.y * lateral)


## Reads a normalized XZ tangent from neighboring admitted route samples.
func _route_tangent(route_index: int) -> Vector2:
	var points: PackedVector3Array = _graph.route_points
	var before: Vector3 = points[maxi(0, route_index - 1)]
	var after: Vector3 = points[mini(points.size() - 1, route_index + 1)]
	return Vector2(after.x - before.x, after.z - before.z).normalized()


## Selects direct graph motion or actual CharacterBody3D collision motion.
func _move(body: S10Pedestrian, displacement: Vector3, motion: String) -> void:
	if motion == MOTION_CHARACTER:
		body.advance_character(displacement)
	else:
		body.advance_graph(displacement)


## Retains a bounded corpse and schedules one graph-end replenishment for its slot.
func _kill(index: int, tick: int, cause: String) -> void:
	var agent: Dictionary = _agents[index]
	if not agent.alive:
		return

	agent.alive = false
	var body: S10Pedestrian = agent.body
	body.reparent(_fixture.dead as Node3D)
	body.retain_dead()
	_dead_presentations.append(body)
	while _dead_presentations.size() > DEAD_RETENTION_CAP:
		var retired: S10Pedestrian = _dead_presentations.pop_front()
		retired.free()
	_replenishments.append({ "slot": index, "due": tick + REPLENISH_DELAY_TICKS })
	_metrics.deaths += 1
	if cause == "blast":
		_metrics.blast_deaths += 1
	else:
		_metrics.car_hits += 1
	_metrics.max_dead = maxi(int(_metrics.max_dead), _dead_presentations.size())


## Kills at most a fixed number of nearest live pedestrians inside a blast radius.
func _kill_nearest(position: Vector2, tick: int, count: int) -> void:
	var candidates: Array[Dictionary] = []
	for index: int in _agents.size():
		var agent: Dictionary = _agents[index]
		if not agent.alive:
			continue

		var body_position: Vector3 = (agent.body as S10Pedestrian).global_position
		var distance: float = position.distance_to(Vector2(body_position.x, body_position.z))
		if distance <= 16.0:
			candidates.append({ "index": index, "distance": distance })
	candidates.sort_custom(_candidate_before)
	for candidate_index: int in mini(count, candidates.size()):
		_kill(int(candidates[candidate_index].index), tick, "blast")


## Orders blast candidates deterministically by distance then stable slot index.
func _candidate_before(left: Dictionary, right: Dictionary) -> bool:
	if left.distance == right.distance:
		return int(left.index) < int(right.index)
	return float(left.distance) < float(right.distance)


## Replenishes killed slots after a bounded delay at alternating graph endpoints.
func _replenish(tick: int) -> void:
	var points: PackedVector3Array = _graph.route_points
	for index: int in range(_replenishments.size() - 1, -1, -1):
		var request: Dictionary = _replenishments[index]
		if tick < int(request.due):
			continue

		var slot: int = request.slot
		var from_start: bool = _next_identity % 2 == 0
		var route_index: int = 0 if from_start else points.size() - 1
		var direction: int = 1 if from_start else -1
		var lane: int = _next_identity % 4
		var lateral: float = -1.2 + float(lane) * 0.8
		var position: Vector3 = _route_pose(route_index, lateral)
		_agents[slot] = _new_agent(position, route_index, direction, lateral, _next_identity)
		_replenishments.remove_at(index)
		_metrics.replacements += 1


## Detects rectangular car contact around the graph-derived crossing centre.
func _car_overlaps(position: Vector3, car_z: float) -> bool:
	var crossing: Vector3 = _graph.crossing_center
	return absf(position.x - crossing.x) < CAR_HALF_WIDTH_M + AGENT_RADIUS_M and (
		absf(position.z - car_z) < CAR_HALF_LENGTH_M + AGENT_RADIUS_M)


## Measures real body positions against independent graph regions and derived S06 roads.
func _measure_position(agent: Dictionary) -> void:
	var position: Vector3 = (agent.body as S10Pedestrian).global_position
	if not _is_legal_kind(position, ""):
		_metrics.off_sidewalk_ticks += 1
	if _overlaps_road(position) and not _is_legal_kind(position, "CROSSING"):
		_metrics.road_outside_crossing_ticks += 1


## Checks capsule-centre clearance against compiled authored foot-link segments.
func _is_legal_kind(position: Vector3, kind: String) -> bool:
	var point: Vector2 = Vector2(position.x, position.z)
	for segment: Dictionary in _graph.legal_segments:
		if not kind.is_empty() and segment.kind != kind:
			continue
		if _point_segment_distance(point, segment.start, segment.finish) <= (
			LEGAL_CENTER_HALF_WIDTH_M + FOOT_METRIC_TOLERANCE_M):
			return true
	return false


## Checks whether any part of the capsule footprint overlaps a derived S06 road strip.
func _overlaps_road(position: Vector3) -> bool:
	var point: Vector2 = Vector2(position.x, position.z)
	for segment: Dictionary in _graph.road_segments:
		if _point_segment_distance(point, segment.start, segment.finish) <= (
			float(segment.half_width) + AGENT_RADIUS_M):
			return true
	return false


## Compiles collinear legal polylines into bounded independent measurement segments.
func _compile_legal_segments(regions: Array) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for region: Dictionary in regions:
		for segment: Dictionary in _polyline_segments(region.points):
			segment.kind = region.kind
			result.append(segment)
	return result


## Compiles S06 map road polylines and their authored widths for occupancy checks.
func _compile_road_segments(roads: Array) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for road: Dictionary in roads:
		for segment: Dictionary in _polyline_segments(road.points):
			segment.half_width = float(road.width_m) * 0.5
			result.append(segment)
	return result


## Collapses consecutive collinear graph samples without replacing their world geometry.
func _polyline_segments(points: PackedVector3Array) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	var start: Vector2 = Vector2(points[0].x, points[0].z)
	var previous: Vector2 = start
	var direction: Vector2 = Vector2.ZERO
	for index: int in range(1, points.size()):
		var current: Vector2 = Vector2(points[index].x, points[index].z)
		var next_direction: Vector2 = (current - previous).normalized()
		if direction != Vector2.ZERO and direction.dot(next_direction) < 0.9999:
			result.append({ "start": start, "finish": previous })
			start = previous
		direction = next_direction
		previous = current
	result.append({ "start": start, "finish": previous })
	return result


## Finds the graph-derived midpoint of the single required semantic region.
func _region_midpoint(regions: Array, kind: String) -> Vector3:
	for region: Dictionary in regions:
		if region.kind == kind:
			var points: PackedVector3Array = region.points
			return points[points.size() / 2]
	return Vector3.ZERO


## Returns distance from one XZ point to an independently compiled graph segment.
func _point_segment_distance(point: Vector2, start: Vector2, finish: Vector2) -> float:
	return point.distance_to(Geometry2D.get_closest_point_to_segment(point, start, finish))


## Samples pair overlaps once per simulated second without contaminating timed work.
func _sample_overlaps() -> void:
	var pairs: int = 0
	for left_index: int in _agents.size():
		var left: Dictionary = _agents[left_index]
		if not left.alive:
			continue

		var left_position: Vector3 = (left.body as S10Pedestrian).global_position
		for right_index: int in range(left_index + 1, _agents.size()):
			var right: Dictionary = _agents[right_index]
			if not right.alive:
				continue

			var right_position: Vector3 = (right.body as S10Pedestrian).global_position
			if left_position.distance_to(right_position) < AGENT_RADIUS_M * 2.0:
				pairs += 1
	_metrics.overlap_pair_samples += pairs
	_metrics.max_overlap_pairs = maxi(int(_metrics.max_overlap_pairs), pairs)
	_metrics.overlap_samples += 1


## Records identities whose endpoint displacement is below 0.25 m over four seconds.
func _sample_stuck(tick: int) -> void:
	for agent: Dictionary in _agents:
		if not agent.alive:
			continue

		var position: Vector3 = (agent.body as S10Pedestrian).global_position
		if position.distance_to(agent.checkpoint) < 0.25:
			_stuck_ids[agent.id] = true
		agent.checkpoint = position
		agent.checkpoint_tick = tick


## Tracks bounded global live population after lifecycle work for the current tick.
func _update_live_bounds() -> void:
	var live: int = 0
	for agent: Dictionary in _agents:
		if agent.alive:
			live += 1
	_metrics.min_live = mini(int(_metrics.min_live), live)
	_metrics.max_live = maxi(int(_metrics.max_live), live)


## Produces compact timing, graph legality and reaction-completeness evidence.
func _result(seed: int, mode: String, flee: bool) -> Dictionary:
	var live: int = 0
	for agent: Dictionary in _agents:
		if agent.alive:
			live += 1
	var failures: Array[String] = reaction_failures(
		_event_expectations, _flee_latencies_ticks)
	failures.append_array(graph_errors(_graph))
	if live != POPULATION_COUNT:
		failures.append("end live population was not 64")
	if int(_metrics.max_dead) > DEAD_RETENTION_CAP:
		failures.append("dead presentation cap exceeded")
	if int(_metrics.off_sidewalk_ticks) > 0 or int(_metrics.road_outside_crossing_ticks) > 0:
		failures.append("pedestrian left the admitted S06 foot graph regions")
	if flee:
		for event_id: Variant in _event_expectations:
			if int(_event_expectations[event_id].expected) != POPULATION_COUNT:
				failures.append("storm event %s did not target all 64 live slots" % event_id)

	return {
		"seed": seed,
		"scenario": "flee_storm" if flee else "normal",
		"motion": mode,
		"ticks": SIMULATION_TICKS,
		"simulated_seconds": 600,
		"ai_movement_ms": _timing_summary(),
		"graph": {
			"link_ids": _graph.link_ids,
			"route_point_count": (_graph.route_points as PackedVector3Array).size(),
			"legal_segment_count": (_graph.legal_segments as Array).size(),
			"road_segment_count": (_graph.road_segments as Array).size(),
		},
		"metrics": _result_metrics(live),
		"failures": failures,
	}


## Collects lifecycle, legality, density and reaction outcomes for the compact receipt.
func _result_metrics(live: int) -> Dictionary:
	return {
		"end_live": live,
		"min_live": _metrics.min_live,
		"max_live": _metrics.max_live,
		"deaths": _metrics.deaths,
		"blast_deaths": _metrics.blast_deaths,
		"car_hits": _metrics.car_hits,
		"replacements": _metrics.replacements,
		"retained_dead": _dead_presentations.size(),
		"max_retained_dead": _metrics.max_dead,
		"off_sidewalk_agent_ticks": _metrics.off_sidewalk_ticks,
		"road_outside_crossing_agent_ticks": _metrics.road_outside_crossing_ticks,
		"stuck_entities": _stuck_ids.size(),
		"overlap_pair_samples": _metrics.overlap_pair_samples,
		"max_overlap_pairs": _metrics.max_overlap_pairs,
		"overlap_sample_count": _metrics.overlap_samples,
		"crossing_wait_agent_ticks": _metrics.crossing_wait_ticks,
		"threat_events": _event_expectations.size(),
		"expected_flee_reactions": _expected_reaction_total(),
		"flee_reactions": _flee_latencies_ticks.size(),
		"flee_latency_ms": _latency_summary(),
	}


## Totals independently captured event expectations for the compact receipt.
func _expected_reaction_total() -> int:
	var total: int = 0
	for event_id: Variant in _event_expectations:
		total += int(_event_expectations[event_id].expected)
	return total


## Summarizes per-tick AI plus movement wall-clock time in milliseconds.
func _timing_summary() -> Dictionary:
	_timings_usec.sort()
	var total: int = 0
	for value: int in _timings_usec:
		total += value
	return {
		"median": float(_percentile(_timings_usec, 0.5)) / 1000.0,
		"p95": float(_percentile(_timings_usec, 0.95)) / 1000.0,
		"p99": float(_percentile(_timings_usec, 0.99)) / 1000.0,
		"max": float(_percentile(_timings_usec, 1.0)) / 1000.0,
		"mean": float(total) / float(_timings_usec.size()) / 1000.0,
	}


## Converts staggered perception ticks to latency milliseconds.
func _latency_summary() -> Dictionary:
	if _flee_latencies_ticks.is_empty():
		return { "median": 0.0, "p95": 0.0, "max": 0.0 }

	_flee_latencies_ticks.sort()
	return {
		"median": float(_percentile(_flee_latencies_ticks, 0.5)) * 1000.0 /
			TICKS_PER_SECOND,
		"p95": float(_percentile(_flee_latencies_ticks, 0.95)) * 1000.0 /
			TICKS_PER_SECOND,
		"max": float(_percentile(_flee_latencies_ticks, 1.0)) * 1000.0 /
			TICKS_PER_SECOND,
	}


## Selects a nearest-rank percentile from an already sorted integer sample.
func _percentile(values: Array[int], fraction: float) -> int:
	var index: int = ceili(float(values.size()) * fraction) - 1
	return values[clampi(index, 0, values.size() - 1)]


## Frees only this case's owned bodies before the fixture instance is retired.
func _dispose() -> void:
	for agent: Dictionary in _agents:
		var body: S10Pedestrian = agent.body
		if is_instance_valid(body):
			body.free()
	for body: S10Pedestrian in _dead_presentations:
		if is_instance_valid(body):
			body.free()
	_agents.clear()
	_dead_presentations.clear()
