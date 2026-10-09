class_name S17TrafficAdapter
extends RefCounted
## Exposes S09's existing host simulation as one callable integrated-tick seam.

const MOVING_CARS: int = 24
const PARKED_CARS: int = 8

var _simulation: S09TrafficSimulation = S09TrafficSimulation.new()


## Admits the unchanged saved S09 topology and creates the seeded 24-car population.
func begin(topology: S09Topology, seed: int) -> String:
	var result: String = _simulation.configure(topology)
	if result != "OK":
		return result

	# S09 exposes only a monolithic run API; S17 calls its unchanged per-tick units.
	_simulation._reset_case()
	_simulation._spawn(MOVING_CARS, seed)
	return "OK"


## Advances the unchanged S09 controller and S04 drive rule exactly once.
func step(tick: int) -> void:
	_simulation._step(tick)


## Returns 24 moving rows plus eight no-controller parked rows for S11 encoding.
func snapshot_rows(first_id: int) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for car: Dictionary in _simulation._cars:
		rows.append(_row(first_id + rows.size(), car.position, car.velocity, car.yaw, 2))
	for parked_index: int in PARKED_CARS:
		var position: Vector3 = Vector3(-28.0 + parked_index * 4.0, 0.0, 28.0)
		rows.append(_row(first_id + rows.size(), position, Vector3.ZERO, 0.0, 2))
	return rows


## Reports the unchanged source owner's step count and terminal safety outcomes.
func receipt() -> Dictionary:
	return {
		"moving_cars": _simulation._cars.size(),
		"parked_cars": PARKED_CARS,
		"drive_rule_steps": _simulation._drive_rule_steps,
		"collisions": _simulation._collision_count,
		"gridlock": _simulation._gridlock_receipt(),
	}


## Proves the adapter reaches the same seeded states as S09's public run API.
static func equivalence(topology: S09Topology, seed: int, ticks: int) -> Dictionary:
	var source: S09TrafficSimulation = S09TrafficSimulation.new()
	var source_admission: String = source.configure(topology)
	var expected: Dictionary = source.run(MOVING_CARS, seed, ticks)
	var adapter: S17TrafficAdapter = S17TrafficAdapter.new()
	var adapter_admission: String = adapter.begin(topology, seed)
	for tick: int in ticks:
		adapter.step(tick)

	var maximum_position_error_m: float = 0.0
	var actual_states: Array[Dictionary] = adapter._simulation._final_states()
	var expected_states: Array = expected.get("final_states", [])
	if actual_states.size() == expected_states.size():
		for index: int in actual_states.size():
			maximum_position_error_m = maxf(maximum_position_error_m,
				(actual_states[index].position as Vector3).distance_to(
					expected_states[index].position))
	return {
		"ok": source_admission == "OK" and adapter_admission == "OK" and (
			expected.get("code") == "OK") and maximum_position_error_m <= 0.000001 and (
			adapter._simulation._drive_rule_steps == expected.get("drive_rule_steps")),
		"ticks": ticks,
		"maximum_position_error_m": maximum_position_error_m,
		"source_drive_rule_steps": expected.get("drive_rule_steps", -1),
		"adapter_drive_rule_steps": adapter._simulation._drive_rule_steps,
	}


## Builds one complete S11 movement row without changing codec ownership.
static func _row(entity_id: int, position: Vector3, velocity: Vector3, yaw: float,
		kind: int) -> Dictionary:
	return {
		"id": entity_id, "generation": 1, "kind": kind, "phase": 1, "flags": 0,
		"x": position.x, "z": position.z, "vx": velocity.x, "vz": velocity.z,
		"yaw": yaw,
	}
