class_name S17PedestrianAdapter
extends RefCounted
## Exposes S10's selected graph-kinematic motion as one integrated-tick seam.

const MOTION: String = "graph_kinematic"
const BENCHMARK_SCENE: PackedScene = preload("res://tests/fixtures/s10/benchmark.tscn")

var _population: S10Population = S10Population.new()
var _fixture: Node3D
var _graph: Dictionary = {}


## Admits current S06 graph data and creates S10's unchanged 64-slot population.
func begin(fixture: Node3D, seed: int) -> Array[String]:
	_fixture = fixture
	_graph = _graph_input(fixture.get_node("City") as S06City)
	var failures: Array[String] = S10Population.graph_errors(_graph)
	if not failures.is_empty():
		return failures

	# S10 exposes only a monolithic run API; S17 calls its unchanged per-tick units.
	_population._reset(_fixture, _graph, seed)
	_population._spawn_initial_population()
	return []


## Advances S10's normal-play events and graph-kinematic population once.
func step(tick: int) -> void:
	_population._tick(tick, MOTION, false)


## Clears only S10 legality counters while retaining warmed population and event state.
func begin_measurement() -> void:
	_population._metrics.off_sidewalk_ticks = 0
	_population._metrics.road_outside_crossing_ticks = 0


## Returns one complete S11 movement row for every live or retained S10 slot.
func snapshot_rows(first_id: int) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for agent: Dictionary in _population._agents:
		var position: Vector3 = Vector3.ZERO
		if is_instance_valid(agent.body):
			position = (agent.body as S10Pedestrian).global_position
		var phase: int = 1 if agent.alive else 2
		rows.append({
			"id": first_id + rows.size(), "generation": 1, "kind": 1,
			"phase": phase, "flags": 0, "x": position.x,
			"z": position.z, "vx": 0.0, "vz": 0.0, "yaw": 0.0,
		})
	return rows


## Reports bounded live/dead and graph-legality outcomes from the unchanged S10 owner.
func receipt() -> Dictionary:
	var live: int = 0
	for agent: Dictionary in _population._agents:
		if agent.alive:
			live += 1
	return {
		"slots": _population._agents.size(),
		"live": live,
		"retained_dead": _population._dead_presentations.size(),
		"off_sidewalk_agent_ticks": _population._metrics.off_sidewalk_ticks,
		"road_outside_crossing_agent_ticks": _population._metrics.road_outside_crossing_ticks,
	}


## Frees the population's runtime instances without touching the saved fixture.
func finish() -> void:
	_population._dispose()


## Compares the adapter with direct unchanged S10 per-tick calls on two saved instances.
static func equivalence(  # gdstyle:ignore=quality/max-local-variables
		parent: Node, seed: int, ticks: int) -> Dictionary:
	var adapter_fixture: Node3D = BENCHMARK_SCENE.instantiate() as Node3D
	var source_fixture: Node3D = BENCHMARK_SCENE.instantiate() as Node3D
	parent.add_child(adapter_fixture)
	parent.add_child(source_fixture)
	var adapter: S17PedestrianAdapter = S17PedestrianAdapter.new()
	var failures: Array[String] = adapter.begin(adapter_fixture, seed)
	var graph: Dictionary = _graph_input(source_fixture.get_node("City") as S06City)
	var source: S10Population = S10Population.new()
	source._reset(source_fixture, graph, seed)
	source._spawn_initial_population()
	for tick: int in ticks:
		adapter.step(tick)
		source._tick(tick, MOTION, false)

	var maximum_position_error_m: float = 0.0
	for index: int in source._agents.size():
		var expected: Vector3 = (source._agents[index].body as S10Pedestrian).global_position
		var actual: Vector3 = (
			adapter._population._agents[index].body as S10Pedestrian).global_position
		maximum_position_error_m = maxf(maximum_position_error_m,
			actual.distance_to(expected))
	var metrics_match: bool = adapter._population._metrics == source._metrics
	var result: Dictionary = {
		"ok": failures.is_empty() and maximum_position_error_m <= 0.000001 and metrics_match,
		"ticks": ticks,
		"maximum_position_error_m": maximum_position_error_m,
		"metrics_match": metrics_match,
	}
	adapter.finish()
	source._dispose()
	adapter_fixture.free()
	source_fixture.free()
	return result


## Builds S10's graph admission input from unchanged S06 public APIs.
static func _graph_input(city: S06City) -> Dictionary:
	# Adapted line-for-line from tests/fixtures/s10/benchmark.gd at lane base 4abc07d.
	var full: Dictionary = city.route("FOOT", &"s06/foot/west", &"s06/foot/east")
	var west: Dictionary = city.route(
		"FOOT", &"s06/foot/west", &"s06/foot/cross_west")
	var crossing: Dictionary = city.route(
		"FOOT", &"s06/foot/cross_west", &"s06/foot/cross_east")
	var east: Dictionary = city.route(
		"FOOT", &"s06/foot/cross_east", &"s06/foot/east")
	var map: Dictionary = city.map_data()
	for result: Dictionary in [full, west, crossing, east, map]:
		if result.code != "OK":
			return {}
	var full_points: PackedVector3Array = full.world_points_m
	var crossing_points: PackedVector3Array = crossing.world_points_m
	return {
		"route_points": full_points,
		"link_ids": full.link_ids,
		"crossing_range": Vector2i(
			_nearest_route_index(full_points, crossing_points[0]),
			_nearest_route_index(full_points, crossing_points[-1])),
		"legal_regions": [
			{ "kind": "SIDEWALK", "points": west.world_points_m },
			{ "kind": "CROSSING", "points": crossing.world_points_m },
			{ "kind": "SIDEWALK", "points": east.world_points_m },
		],
		"roads": map.road_polylines_m,
	}


## Resolves one semantic endpoint back to the admitted full S06 route.
static func _nearest_route_index(points: PackedVector3Array, target: Vector3) -> int:
	var nearest_index: int = 0
	var nearest_distance: float = INF
	for index: int in points.size():
		var distance: float = points[index].distance_squared_to(target)
		if distance < nearest_distance:
			nearest_index = index
			nearest_distance = distance
	return nearest_index
