class_name S09TrafficSimulation
extends RefCounted
## Deterministic host traffic prototype that emits only shared S04 drive commands.

const PHYSICS_HZ: int = 60
const STEP_SECONDS: float = 1.0 / PHYSICS_HZ
const MAX_TRAFFIC: int = 32
const DESIRED_SPEED_MPS: float = 6.0
const LOOKAHEAD_POINTS: int = 10
const NEAREST_BACK_POINTS: int = 8
const NEAREST_FORWARD_POINTS: int = 32
const BLOCK_LOOKAHEAD_M: float = 14.0
const BLOCK_WAIT_TICKS: int = 120
const REVERSE_TICKS: int = 30
const SAFE_GAP_BASE_M: float = 6.0
const SAFE_GAP_SECONDS: float = 1.0
const COLLISION_DISTANCE_M: float = 1.7
const GRIDLOCK_TICKS: int = 240
const PROGRESS_DISTANCE_M: float = 0.25

var _topology: S09Topology
var _routes: Dictionary = {}
var _cars: Array[Dictionary] = []
var _intersection_owner: int = -1
var _intersection_entered: bool = false
var _collision_pairs: Dictionary = {}
var _collision_count: int = 0
var _collision_details: Dictionary = { "same_family": 0, "cross_family": 0 }
var _collision_events: Array[Dictionary] = []
var _deadlock_count: int = 0
var _gridlock_ticks: int = 0
var _stuck_events: int = 0
var _recoveries: Array[float] = []
var _lane_tick_errors: Array[float] = []
var _drive_rule_steps: int = 0


## Admits one valid saved topology before any host simulation work.
func configure(topology: S09Topology) -> String:
	_topology = topology
	_routes.clear()
	if topology == null or topology.validate_content() != "OK":
		return "CONTENT_INVALID"
	for route_id: StringName in [
		&"s09/horizontal", &"s09/horizontal_detour",
		&"s09/vertical", &"s09/vertical_detour", &"s09/outer",
	]:
		var points: PackedVector3Array = topology.route_points(route_id)
		if points.is_empty():
			return "CONTENT_INVALID"
		_routes[route_id] = points

	return "OK"


## Runs a bounded ten-minute-style host case and returns measurements through one public API.
func run(population: int, seed: int, ticks: int) -> Dictionary:
	if _topology == null or population <= 0 or population > MAX_TRAFFIC or ticks <= 0:
		return { "code": "INVALID_ARGUMENT" }
	_reset_case()
	_spawn(population, seed)
	var timings_usec: Array[int] = []
	for tick: int in ticks:
		var started_usec: int = Time.get_ticks_usec()
		_step(tick)
		timings_usec.append(Time.get_ticks_usec() - started_usec)

	var timing_ms: Array[float] = []
	for elapsed_usec: int in timings_usec:
		timing_ms.append(float(elapsed_usec) / 1000.0)
	return {
		"code": "OK", "population": population, "seed": seed, "ticks": ticks,
		"simulated_seconds": float(ticks) / PHYSICS_HZ,
		"ai_tick_ms": _distribution(timing_ms),
		"ai_tick_usec_samples": timings_usec,
		"ai_collisions": _collision_count, "collision_details": _collision_details,
		"collision_events": _collision_events, "deadlocks": _deadlock_count,
		"stuck_events": _stuck_events,
		"stuck_recovery_seconds": _distribution(_recoveries),
		"stuck_recovery_samples_seconds": _recoveries,
		"lane_error_m": _distribution(_lane_tick_errors),
		"final_states": _final_states(),
		"drive_rule_steps": _drive_rule_steps,
		"expected_drive_rule_steps": population * ticks,
	}


## Clears all mutable case state so seeds and population rows are independent.
func _reset_case() -> void:
	_cars.clear()
	_intersection_owner = -1
	_intersection_entered = false
	_collision_pairs.clear()
	_collision_count = 0
	_collision_details = { "same_family": 0, "cross_family": 0 }
	_collision_events.clear()
	_deadlock_count = 0
	_gridlock_ticks = 0
	_stuck_events = 0
	_recoveries.clear()
	_lane_tick_errors.clear()
	_drive_rule_steps = 0


## Creates a bounded, seeded distribution on the two authored base loops.
func _spawn(population: int, seed: int) -> void:
	var random: RandomNumberGenerator = RandomNumberGenerator.new()
	random.seed = seed
	var route_counts: Dictionary = {
		&"s09/horizontal": 0, &"s09/vertical": 0, &"s09/outer": 0,
	}
	for car_id: int in population:
		var route_id: StringName = _spawn_route(car_id)
		route_counts[route_id] += 1
	var placed: Dictionary = {
		&"s09/horizontal": 0, &"s09/vertical": 0, &"s09/outer": 0,
	}
	for car_id: int in population:
		var route_id: StringName = _spawn_route(car_id)
		var points: PackedVector3Array = _routes[route_id]
		var ordinal: int = placed[route_id]
		placed[route_id] = ordinal + 1
		var index: int = int(float(ordinal) * points.size() / route_counts[route_id])
		index = (index + random.randi_range(0, 2)) % points.size()
		for blockage: Dictionary in _topology.blockages():
			if blockage.route_id == route_id and points[index].distance_to(blockage.position) < 8.0:
				index = (index + 24) % points.size()
		var next: Vector3 = points[(index + 1) % points.size()]
		var direction: Vector3 = next - points[index]
		_cars.append({
			"id": car_id, "route_id": route_id, "family": _route_family(route_id),
			"position": points[index],
			"yaw": atan2(-direction.x, -direction.z), "velocity": Vector3.ZERO,
			"route_index": index, "recovery_state": "driving", "blocked_tick": -1,
			"reverse_until_tick": -1, "progress_origin": points[index],
			"progress_tick": 0,
		})


## Assigns most cars to the nonconflicting outer loop while retaining both blocked approaches.
func _spawn_route(car_id: int) -> StringName:
	if car_id % 8 == 0:
		return &"s09/horizontal"
	if car_id % 8 == 1:
		return &"s09/vertical"
	return &"s09/outer"


## Applies reservation, following, blockage recovery and shared handling once for every car.
func _step(tick: int) -> void:
	_update_intersection_reservation()
	var maximum_lane_error: float = 0.0
	for car: Dictionary in _cars:
		var points: PackedVector3Array = _routes[car.route_id]
		var nearest: Dictionary = _nearest(points, car.position, car.route_index)
		car.route_index = nearest.index
		maximum_lane_error = maxf(maximum_lane_error, nearest.distance)
		var command: Dictionary = _drive_command(car, points, tick)
		var next: Dictionary = S04DriveRules.advance(car.velocity, car.yaw, command,
			STEP_SECONDS)
		car.yaw = wrapf(car.yaw + float(next.yaw_rate) * STEP_SECONDS, -PI, PI)
		car.velocity = next.velocity
		car.position += car.velocity * STEP_SECONDS
		_drive_rule_steps += 1
		_update_stuck(car, tick)
	_lane_tick_errors.append(maximum_lane_error)
	_update_collisions()
	_update_gridlock()


## Produces throttle, steer, brake and handbrake without bypassing the handling owner.
func _drive_command(car: Dictionary, points: PackedVector3Array, tick: int) -> Dictionary:
	var recovery: Dictionary = _recovery_command(car, tick)
	if not recovery.is_empty():
		return recovery
	if _must_yield_intersection(car) or _must_follow(car):
		return { "throttle": 0.0, "steer": 0.0, "brake": 1.0, "handbrake": false }

	var target_index: int = (int(car.route_index) + LOOKAHEAD_POINTS) % points.size()
	var direction: Vector3 = points[target_index] - car.position
	var desired_yaw: float = atan2(-direction.x, -direction.z)
	var error: float = wrapf(desired_yaw - float(car.yaw), -PI, PI)
	var speed: float = car.velocity.length()
	var yaw_rate: float = 2.0 * speed * sin(error) / maxf(direction.length(), 0.3)
	var steer_scale: float = S04DriveRules.TURN_RAD_PER_SECOND * clampf(
		speed / S04DriveRules.FULL_STEER_SPEED_MPS, 0.0, 1.0)
	var steer: float = -error if speed < 0.5 else -yaw_rate / maxf(steer_scale, 0.3)
	return {
		"throttle": clampf((DESIRED_SPEED_MPS - speed) * 0.6, 0.0, 1.0),
		"steer": clampf(steer, -1.0, 1.0), "brake": 0.0, "handbrake": false,
	}


## Waits, reverses briefly, then selects only the authored alternate around an obstruction.
func _recovery_command(car: Dictionary, tick: int) -> Dictionary:
	if car.recovery_state == "waiting":
		if tick - int(car.blocked_tick) >= BLOCK_WAIT_TICKS:
			car.recovery_state = "reversing"
			car.reverse_until_tick = tick + REVERSE_TICKS
		return { "throttle": 0.0, "steer": 0.0, "brake": 1.0, "handbrake": false }
	if car.recovery_state == "reversing":
		if tick < int(car.reverse_until_tick):
			return { "throttle": -0.5, "steer": 0.0, "brake": 0.0, "handbrake": false }
		var replacement: StringName = _topology.replacement_route(car.route_id)
		if replacement == &"":
			return { "throttle": 0.0, "steer": 0.0, "brake": 1.0, "handbrake": false }
		car.route_id = replacement
		var nearest: Dictionary = _nearest(_routes[replacement], car.position, 0, true)
		car.route_index = nearest.index
		car.recovery_state = "driving"
		_recoveries.append(float(tick - int(car.blocked_tick)) / PHYSICS_HZ)

	if not str(car.route_id).ends_with("_detour"):
		for blockage: Dictionary in _topology.blockages():
			if blockage.route_id != car.route_id:
				continue
			var offset: Vector3 = blockage.position - car.position
			var forward: Vector3 = Vector3(-sin(car.yaw), 0.0, -cos(car.yaw))
			if offset.length() <= BLOCK_LOOKAHEAD_M and forward.dot(offset) > 0.0:
				car.recovery_state = "waiting"
				car.blocked_tick = tick
				return { "throttle": 0.0, "steer": 0.0, "brake": 1.0,
					"handbrake": false }

	return {}


## Stops an approaching car unless it owns the bounded central conflict zone.
func _must_yield_intersection(car: Dictionary) -> bool:
	var distance: float = car.position.distance_to(_topology.intersection_center())
	return distance < 12.0 and _intersection_owner != int(car.id)


## Uses a speed-sensitive same-lane gap without changing another car's state.
func _must_follow(car: Dictionary) -> bool:
	var forward: Vector3 = Vector3(-sin(car.yaw), 0.0, -cos(car.yaw))
	var safe_gap: float = SAFE_GAP_BASE_M + car.velocity.length() * SAFE_GAP_SECONDS
	for other: Dictionary in _cars:
		if other.id == car.id or other.family != car.family:
			continue
		var offset: Vector3 = other.position - car.position
		if offset.length() < safe_gap and forward.dot(offset) > 0.0:
			return true

	return false


## Grants the intersection to the nearest stable car ID and releases after its exit.
func _update_intersection_reservation() -> void:
	var center: Vector3 = _topology.intersection_center()
	if _intersection_owner >= 0:
		var owner: Dictionary = _cars[_intersection_owner]
		var distance: float = owner.position.distance_to(center)
		if distance < 4.0:
			_intersection_entered = true
		if _intersection_entered and distance > 14.0:
			_intersection_owner = -1
			_intersection_entered = false
		else:
			return

	var candidate_id: int = -1
	var candidate_distance: float = INF
	for car: Dictionary in _cars:
		var distance: float = car.position.distance_to(center)
		if distance <= 14.0 and (distance < candidate_distance or (
			is_equal_approx(distance, candidate_distance) and int(car.id) < candidate_id)):
			candidate_id = car.id
			candidate_distance = distance
	_intersection_owner = candidate_id


## Tracks failure to make progress separately from expected short reservation waits.
func _update_stuck(car: Dictionary, tick: int) -> void:
	if car.position.distance_to(car.progress_origin) >= PROGRESS_DISTANCE_M:
		car.progress_origin = car.position
		car.progress_tick = tick
	elif tick - int(car.progress_tick) == GRIDLOCK_TICKS:
		_stuck_events += 1


## Counts new close-contact episodes between AI cars without double-counting held overlap.
func _update_collisions() -> void:
	var current: Dictionary = {}
	for left_index: int in _cars.size():
		for right_index: int in range(left_index + 1, _cars.size()):
			var left: Dictionary = _cars[left_index]
			var right: Dictionary = _cars[right_index]
			if left.position.distance_to(right.position) >= COLLISION_DISTANCE_M:
				continue
			var key: String = "%d:%d" % [left.id, right.id]
			current[key] = true
			if not _collision_pairs.has(key):
				_record_collision(left, right)
	_collision_pairs = current


## Retains one collision episode and a bounded diagnostic position sample.
func _record_collision(left: Dictionary, right: Dictionary) -> void:
	_collision_count += 1
	var category: String = "same_family" if left.family == right.family else "cross_family"
	_collision_details[category] += 1
	if _collision_events.size() < 32:
		_collision_events.append({ "left": left.id, "right": right.id,
			"position": (left.position + right.position) * 0.5,
			"distance_m": left.position.distance_to(right.position),
			"category": category })


## Groups a base lane and its authored detour for car-following admission.
func _route_family(route_id: StringName) -> String:
	return str(route_id).trim_prefix("s09/").trim_suffix("_detour")


## Counts a gridlock only when the complete moving population remains stopped for four seconds.
func _update_gridlock() -> void:
	var moving: bool = false
	for car: Dictionary in _cars:
		if car.velocity.length() >= 0.2:
			moving = true
			break
	if moving:
		_gridlock_ticks = 0
		return

	_gridlock_ticks += 1
	if _gridlock_ticks == GRIDLOCK_TICKS:
		_deadlock_count += 1


## Finds the closest route sample in a bounded moving window or one explicit full rebind.
func _nearest(points: PackedVector3Array, position: Vector3, former_index: int,
		full_search: bool = false) -> Dictionary:
	var best_index: int = 0 if full_search else former_index
	var best_distance: float = INF
	var start: int = 0 if full_search else -NEAREST_BACK_POINTS
	var finish: int = points.size() if full_search else NEAREST_FORWARD_POINTS
	for offset: int in range(start, finish):
		var candidate: int = offset if full_search else (former_index + offset) % points.size()
		if candidate < 0:
			candidate += points.size()
		var distance: float = position.distance_to(points[candidate])
		if distance < best_distance:
			best_distance = distance
			best_index = candidate

	return { "index": best_index, "distance": best_distance }


## Retains compact terminal state to diagnose gridlock and recovery without pose histories.
func _final_states() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for car: Dictionary in _cars:
		result.append({ "id": car.id, "route_id": car.route_id,
			"position": car.position, "speed_mps": car.velocity.length(),
			"route_index": car.route_index, "recovery_state": car.recovery_state })
	return result


## Reports nearest-rank median/p95/p99/worst while retaining zero-sample cases honestly.
func _distribution(values: Array[float]) -> Dictionary:
	if values.is_empty():
		return { "count": 0 }
	var ordered: Array[float] = values.duplicate()
	ordered.sort()
	return {
		"count": ordered.size(), "median": _percentile(ordered, 0.5),
		"p95": _percentile(ordered, 0.95), "p99": _percentile(ordered, 0.99),
		"worst": ordered[-1],
	}


## Selects one nearest-rank percentile from an already sorted finite sample.
func _percentile(ordered: Array[float], fraction: float) -> float:
	return ordered[clampi(ceili(fraction * ordered.size()) - 1, 0, ordered.size() - 1)]
