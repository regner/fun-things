extends GutTest
## Verifies the coordinator brackets existing pedestrian and ActorMotion owner APIs.

var _clock_usec: int = 0


## Resets the deterministic timing clock before each coordinator contract test.
func before_each() -> void:
	_clock_usec = 0


## Steps pedestrian decisions before pedestrian and player motion in one timed tick.
func test_reports_owner_sections() -> void:  # gdstyle:ignore=quality/max-local-variables
	var navigation := SyntheticPopulationNavigation.new()
	var reservations := CrossingReservations.new()
	assert_true(reservations.configure(navigation))
	var core := PedestrianCore.new()
	assert_true(core.configure(navigation, reservations))
	var start_node: int = navigation.grid_node(0, 0)
	var start: Vector2 = navigation.node_position(start_node)
	assert_true(core.add_agent(41, start_node, start))

	var pedestrian := _add_actor(Vector3(start.x, 0.0, start.y))
	var player := _add_actor(Vector3(60.0, 0.0, 0.0))
	await get_tree().physics_frame
	var profiler := HostTickProfiler.new()
	assert_true(profiler.configure(8, Callable(self, "_next_clock_usec")))
	var coordinator := HostTickCoordinator.new()
	assert_true(coordinator.configure(profiler))
	var pedestrian_actors: Array[ActorMotion] = [pedestrian]
	var player_actors: Array[ActorMotion] = [player]
	assert_true(coordinator.bind_pedestrians(core, PackedInt64Array([41]), pedestrian_actors))
	assert_true(coordinator.bind_players(player_actors))
	profiler.set_enabled(true)
	var player_commands: Array[FootCommand] = [
		FootCommand.new(1, 1, Vector2.RIGHT, 0.0, false, false),
	]

	assert_true(
		coordinator.step(
			5,
			1.0 / float(Engine.physics_ticks_per_second),
			player_commands,
		)
	)
	var report: Dictionary = profiler.summary()
	assert_eq(report.sample_count, 1)
	assert_eq(report.sections.pedestrian_decisions.count, 1)
	assert_eq(report.sections.actor_motion.count, 1)
	assert_gt(player.global_position.x, 60.0)
	assert_eq(core.decision_count(41), 1)


## Rejects identity/actor cardinality mismatches before any owner or timer call.
func test_binding_rejects_mismatched_pedestrian_identities_without_timing() -> void:
	var navigation := SyntheticPopulationNavigation.new()
	var reservations := CrossingReservations.new()
	assert_true(reservations.configure(navigation))
	var core := PedestrianCore.new()
	assert_true(core.configure(navigation, reservations))
	var profiler := HostTickProfiler.new()
	assert_true(profiler.configure())
	var coordinator := HostTickCoordinator.new()
	assert_true(coordinator.configure(profiler))
	profiler.set_enabled(true)
	var no_actors: Array[ActorMotion] = []

	assert_false(coordinator.bind_pedestrians(core, PackedInt64Array([1]), no_actors))
	assert_eq(profiler.timer_read_count(), 0)


## Adds one floating ActorMotion node for production owner API execution.
func _add_actor(position: Vector3) -> ActorMotion:
	var actor := ActorMotion.new()
	actor.motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	actor.position = position
	add_child_autofree(actor)
	return actor


## Advances a deterministic microsecond clock by ten on every timer read.
func _next_clock_usec() -> int:
	var value: int = _clock_usec
	_clock_usec += 10
	return value
