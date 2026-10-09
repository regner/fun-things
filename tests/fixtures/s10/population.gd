class_name S10Population
extends RefCounted
## Deterministic host-owned pedestrian AI experiment over the saved S06 foot corridor.

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
const SEPARATION_RADIUS_M: float = 1.2
const SIDEWALK_MIN_Z_M: float = 4.9
const SIDEWALK_MAX_Z_M: float = 8.1
const ROUTE_MIN_X_M: float = -20.0
const ROUTE_MAX_X_M: float = 20.0
const CROSSING_EDGE_X_M: float = 6.5
const CROSSING_CAR_CLEARANCE_M: float = 5.0
const CAR_HALF_WIDTH_M: float = 0.9
const CAR_HALF_LENGTH_M: float = 1.7
const GRID_CELL_M: float = 1.5
const FOOT_METRIC_TOLERANCE_M: float = 0.001
const MOTION_GRAPH: String = "graph_kinematic"
const MOTION_CHARACTER: String = "character_body"

var _fixture: Dictionary = {}
var _agents: Array[Dictionary] = []
var _dead_presentations: Array[S10Pedestrian] = []
var _replenishments: Array[Dictionary] = []
var _events: Array[Dictionary] = []
var _timings_usec: Array[int] = []
var _flee_latencies_ticks: Array[int] = []
var _stuck_ids: Dictionary = {}
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()
var _next_identity: int = 1
var _next_event: int = 1
var _metrics: Dictionary = {}


## Runs one ten-minute seed with identical AI and one selected movement implementation.
func run_case(root: Node3D, seed: int, motion: String, storm: bool) -> Dictionary:
	_reset(root, seed)
	_spawn_initial_population()
	for tick: int in SIMULATION_TICKS:
		var started_usec: int = Time.get_ticks_usec()
		_step(tick, motion, storm)
		_timings_usec.append(Time.get_ticks_usec() - started_usec)
		if tick % OVERLAP_SAMPLE_INTERVAL_TICKS == 0:
			_sample_overlaps()
		if tick > 0 and tick % STUCK_WINDOW_TICKS == 0:
			_sample_stuck(tick)

	var result: Dictionary = _result(seed, motion, storm)
	_dispose()
	return result


## Clears per-case state while retaining the saved fixture as the composition owner.
func _reset(root: Node3D, seed: int) -> void:
	_fixture = {
		"population": root.get_node("Population") as Node3D,
		"dead": root.get_node("DeadPresentations") as Node3D,
		"car": root.get_node("CrossingCar") as AnimatableBody3D,
	}
	_rng.seed = seed
	_agents.clear()
	_dead_presentations.clear()
	_replenishments.clear()
	_events.clear()
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


## Creates 64 saved capsule instances in four legal lanes along the S06 foot route.
func _spawn_initial_population() -> void:
	for index: int in POPULATION_COUNT:
		var column: int = index / 4
		var lane: int = index % 4
		var x: float = -18.75 + float(column) * 2.5
		var z: float = 5.0 + float(lane)
		var direction: float = 1.0 if lane % 2 == 0 else -1.0
		_agents.append(_new_agent(Vector3(x, 0.001, z), direction, index))


## Builds one host-owned AI slot around an instance of the saved capsule scene.
func _new_agent(position: Vector3, direction: float, phase: int) -> Dictionary:
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
		"phase": phase % PERCEPTION_INTERVAL_TICKS,
		"panic_until": -1,
		"threat_position": Vector2.ZERO,
		"last_event": 0,
		"checkpoint": position,
		"checkpoint_tick": 0,
	}


## Advances event injection, perception, steering, motion, lifecycle and bounded metrics.
func _step(tick: int, motion: String, storm: bool) -> void:
	_inject_events(tick, storm)
	_expire_events(tick)
	_replenish(tick)
	var car_z: float = -20.0 + fmod(float(tick) * 8.0 / TICKS_PER_SECOND, 40.0)
	(_fixture.car as AnimatableBody3D).position.z = car_z
	var grid: Dictionary = _build_grid()
	for index: int in _agents.size():
		var agent: Dictionary = _agents[index]
		if not agent.alive:
			continue

		_perceive(agent, tick)
		var position: Vector3 = (agent.body as S10Pedestrian).global_position
		var velocity: Vector2 = _desired_velocity(agent, position, car_z, tick)
		velocity += _separation(index, position, grid)
		var speed_limit: float = FLEE_SPEED_MPS if tick < agent.panic_until else WALK_SPEED_MPS
		velocity = velocity.limit_length(speed_limit)
		var next: Vector3 = _constrain(position + Vector3(velocity.x, 0.0, velocity.y) /
			TICKS_PER_SECOND, agent)
		_move(agent.body as S10Pedestrian, next - position, motion)
		_measure_position(agent)
		if _car_overlaps(next, car_z):
			_kill(index, tick, "car")

	_update_live_bounds()


## Injects localized normal threats or a repeated all-population flee storm.
func _inject_events(tick: int, storm: bool) -> void:
	if storm and tick % STORM_EVENT_INTERVAL_TICKS == 0:
		_add_event(tick, Vector2(0.0, 6.5), 100.0, "gunfire")
	elif not storm and tick % NORMAL_EVENT_INTERVAL_TICKS == 0:
		var event_x: float = _rng.randf_range(-12.0, 12.0)
		_add_event(tick, Vector2(event_x, 6.5), 12.0, "gunfire")

	if not storm and tick > 0 and tick % BLAST_INTERVAL_TICKS == 0:
		var blast_position: Vector2 = Vector2(_rng.randf_range(-8.0, 8.0), 6.5)
		_add_event(tick, blast_position, 16.0, "blast")
		_kill_nearest(blast_position, tick, 4)


## Adds a short-lived threat so staggered perception reacts within one AI interval.
func _add_event(tick: int, position: Vector2, radius_m: float, kind: String) -> void:
	_events.append({
		"id": _next_event,
		"tick": tick,
		"expires": tick + EVENT_LIFETIME_TICKS,
		"position": position,
		"radius": radius_m,
		"kind": kind,
	})
	_next_event += 1


## Removes threats after every stagger phase had exactly one opportunity to observe them.
func _expire_events(tick: int) -> void:
	for index: int in range(_events.size() - 1, -1, -1):
		if tick >= int(_events[index].expires):
			_events.remove_at(index)


## Applies bounded 10 Hz perception while preserving 60 Hz movement for every live slot.
func _perceive(agent: Dictionary, tick: int) -> void:
	if tick % PERCEPTION_INTERVAL_TICKS != int(agent.phase):
		return

	var position: Vector3 = (agent.body as S10Pedestrian).global_position
	var point: Vector2 = Vector2(position.x, position.z)
	for event: Dictionary in _events:
		if int(event.id) <= int(agent.last_event):
			continue
		if point.distance_to(event.position) > float(event.radius):
			continue

		agent.last_event = event.id
		agent.panic_until = tick + PANIC_TICKS
		agent.threat_position = event.position
		_flee_latencies_ticks.append(tick - int(event.tick))


## Combines route wandering, crossing-gap waits and direction-away flee behavior.
func _desired_velocity(agent: Dictionary, position: Vector3, car_z: float,
		tick: int) -> Vector2:
	var direction: float = float(agent.direction)
	var velocity: Vector2 = Vector2(direction * WALK_SPEED_MPS, 0.0)
	var approaching_crossing: bool = absf(position.x) >= CROSSING_EDGE_X_M and (
		absf(position.x + direction * 0.5) < absf(position.x))
	if approaching_crossing and absf(car_z - 6.5) < CROSSING_CAR_CLEARANCE_M:
		velocity = Vector2.ZERO
		_metrics.crossing_wait_ticks += 1
	if tick < int(agent.panic_until):
		var away: Vector2 = Vector2(position.x, position.z) - agent.threat_position
		if away.length_squared() < 0.01:
			away = Vector2(direction, 0.0)
		velocity = (Vector2(direction, 0.0) * 0.35 + away.normalized()).normalized() * (
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


## Keeps every live capsule inside the authored foot corridor and reverses at endpoints.
func _constrain(position: Vector3, agent: Dictionary) -> Vector3:
	if position.x <= ROUTE_MIN_X_M or position.x >= ROUTE_MAX_X_M:
		agent.direction = -float(agent.direction)
	position.x = clampf(position.x, ROUTE_MIN_X_M, ROUTE_MAX_X_M)
	position.z = clampf(position.z, SIDEWALK_MIN_Z_M, SIDEWALK_MAX_Z_M)
	position.y = 0.001
	return position


## Selects direct graph motion or actual CharacterBody3D collision motion.
func _move(body: S10Pedestrian, displacement: Vector3, motion: String) -> void:
	if motion == MOTION_CHARACTER:
		body.advance_character(displacement)
	else:
		body.advance_graph(displacement)


## Retains a bounded corpse and schedules one edge replenishment for a killed slot.
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


## Replenishes killed slots after a bounded delay at alternating out-of-view route edges.
func _replenish(tick: int) -> void:
	for index: int in range(_replenishments.size() - 1, -1, -1):
		var request: Dictionary = _replenishments[index]
		if tick < int(request.due):
			continue

		var slot: int = request.slot
		var from_west: bool = _next_identity % 2 == 0
		var x: float = ROUTE_MIN_X_M if from_west else ROUTE_MAX_X_M
		var z: float = 5.0 + float(_next_identity % 4)
		var direction: float = 1.0 if from_west else -1.0
		_agents[slot] = _new_agent(Vector3(x, 0.001, z), direction, _next_identity)
		_replenishments.remove_at(index)
		_metrics.replacements += 1


## Detects rectangular car contact independently of either movement implementation.
func _car_overlaps(position: Vector3, car_z: float) -> bool:
	return absf(position.x) < CAR_HALF_WIDTH_M + AGENT_RADIUS_M and (
		absf(position.z - car_z) < CAR_HALF_LENGTH_M + AGENT_RADIUS_M)


## Counts any illegal foot-corridor or road-outside-crossing occupancy.
func _measure_position(agent: Dictionary) -> void:
	var position: Vector3 = (agent.body as S10Pedestrian).global_position
	if position.x < ROUTE_MIN_X_M - FOOT_METRIC_TOLERANCE_M or (
		position.x > ROUTE_MAX_X_M + FOOT_METRIC_TOLERANCE_M) or (
		position.z < SIDEWALK_MIN_Z_M - FOOT_METRIC_TOLERANCE_M) or (
		position.z > SIDEWALK_MAX_Z_M + FOOT_METRIC_TOLERANCE_M):
		_metrics.off_sidewalk_ticks += 1
	var in_road: bool = position.z > -4.5 and position.z < 4.5
	if in_road and absf(position.x) > CROSSING_EDGE_X_M:
		_metrics.road_outside_crossing_ticks += 1


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


## Records identities that failed to make 0.25 m progress over a four-second window.
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


## Produces compact timing and correctness evidence without retaining 36,000 raw samples.
func _result(seed: int, motion: String, storm: bool) -> Dictionary:
	var live: int = 0
	for agent: Dictionary in _agents:
		if agent.alive:
			live += 1
	var failures: Array[String] = []
	if live != POPULATION_COUNT:
		failures.append("end live population was not 64")
	if int(_metrics.max_dead) > DEAD_RETENTION_CAP:
		failures.append("dead presentation cap exceeded")
	if int(_metrics.off_sidewalk_ticks) > 0 or int(_metrics.road_outside_crossing_ticks) > 0:
		failures.append("pedestrian left the legal foot corridor")
	if not _flee_latencies_ticks.is_empty() and _percentile(_flee_latencies_ticks, 1.0) > 5:
		failures.append("flee reaction exceeded the six-phase perception bound")

	return {
		"seed": seed,
		"scenario": "flee_storm" if storm else "normal",
		"motion": motion,
		"ticks": SIMULATION_TICKS,
		"simulated_seconds": 600,
		"ai_movement_ms": _timing_summary(),
		"metrics": {
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
			"flee_reactions": _flee_latencies_ticks.size(),
			"flee_latency_ms": _latency_summary(),
		},
		"failures": failures,
	}


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
