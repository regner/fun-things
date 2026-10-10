extends GutTest
## Verifies lifecycle deadlines, bounded blocked search, generation advance, and reset hydration.

var _blocked_world_ids: Dictionary[StringName, bool] = {}
var _generation_by_participant: Dictionary[int, int] = {}
var _spawn_calls: int = 0


## Commits death immediately and respawns only on the exact three-second due tick.
func test_death_waits_three_seconds_then_advances_generation() -> void:
	var lifecycle: PlayerLifecycle = _configured_lifecycle()
	assert_true(lifecycle.register_player(1, { "id": 7, "generation": 1 }, true))
	_generation_by_participant[1] = 1

	assert_true(lifecycle.mark_dead(1, 20))
	assert_false(lifecycle.view().alive)
	assert_eq(lifecycle.view().respawn_seconds, 3.0)
	lifecycle.step(20 + PlayerLifecycle.RESPAWN_DELAY_TICKS - 1)
	assert_false(lifecycle.view().alive)
	assert_eq(_spawn_calls, 0)

	lifecycle.step(20 + PlayerLifecycle.RESPAWN_DELAY_TICKS)
	assert_true(lifecycle.view().alive)
	assert_eq(lifecycle.entity_ref_for(1).generation, 2)
	assert_eq(_spawn_calls, 1)


## Searches alternate anchors and reports bounded failure without overlapping spawn.
func test_blocked_search_uses_alternate_then_stops_after_deadline() -> void:
	var lifecycle: PlayerLifecycle = _configured_lifecycle()
	assert_true(lifecycle.register_player(1, { "id": 7, "generation": 1 }, true))
	_generation_by_participant[1] = 1
	_blocked_world_ids[&"spawn/a"] = true
	assert_true(lifecycle.mark_dead(1, 0))

	lifecycle.step(PlayerLifecycle.RESPAWN_DELAY_TICKS)
	assert_true(lifecycle.view().alive)
	assert_eq(_spawn_calls, 1)

	assert_true(lifecycle.mark_dead(1, PlayerLifecycle.RESPAWN_DELAY_TICKS + 1))
	_blocked_world_ids[&"spawn/b"] = true
	var deadline: int = (
		PlayerLifecycle.RESPAWN_DELAY_TICKS
		+ 1
		+ PlayerLifecycle.RESPAWN_DELAY_TICKS
		+ PlayerLifecycle.SEARCH_DEADLINE_TICKS
	)
	lifecycle.step(deadline)
	assert_false(lifecycle.view().alive)
	assert_eq(lifecycle.view().spawn_failure, &"SPAWN_BLOCKED")
	assert_eq(_spawn_calls, 1)


## Reset retains admitted roster rows while replacing every life with a fresh generation.
func test_reset_rehydrates_retained_admitted_players() -> void:
	var lifecycle: PlayerLifecycle = _configured_lifecycle()
	assert_true(lifecycle.register_player(1, { "id": 7, "generation": 1 }, true))
	assert_true(lifecycle.register_player(2, { "id": 8, "generation": 3 }, true))
	_generation_by_participant[1] = 1
	_generation_by_participant[2] = 3

	var result: Dictionary = lifecycle.reset_players(400)
	assert_true(result.ok)
	assert_true(lifecycle.is_alive(1))
	assert_true(lifecycle.is_alive(2))
	assert_eq(lifecycle.entity_ref_for(1).generation, 2)
	assert_eq(lifecycle.entity_ref_for(2).generation, 4)
	assert_eq(lifecycle.view().roster.size(), 2)
	assert_eq(_spawn_calls, 2)


## Creates two deterministic candidates with injected blockers and generation callback.
func _configured_lifecycle() -> PlayerLifecycle:
	_blocked_world_ids.clear()
	_generation_by_participant.clear()
	_spawn_calls = 0
	var lifecycle := PlayerLifecycle.new()
	add_child_autofree(lifecycle)
	var candidates: Array[Dictionary] = [
		{
			"world_id": &"spawn/a",
			"transform": Transform3D(Basis.IDENTITY, Vector3.ZERO),
		},
		{
			"world_id": &"spawn/b",
			"transform": Transform3D(Basis.IDENTITY, Vector3(3.0, 0.0, 0.0)),
		},
	]
	assert_true(
		lifecycle.configure_authority(
			1,
			candidates,
			SpawnReservations.new(),
			_is_blocked,
			_spawn,
		)
	)
	return lifecycle


## Returns the deterministic blocked state for one authored candidate.
func _is_blocked(candidate: Dictionary, _participant_id: int) -> bool:
	return _blocked_world_ids.has(candidate.world_id)


## Advances the participant generation exactly once for every accepted safe spawn.
func _spawn(participant_id: int, _candidate: Dictionary) -> Dictionary:
	_spawn_calls += 1
	var generation: int = _generation_by_participant.get(participant_id, 0) + 1
	_generation_by_participant[participant_id] = generation
	return {
		"ok": true,
		"entity_ref": { "id": participant_id + 6, "generation": generation },
	}
