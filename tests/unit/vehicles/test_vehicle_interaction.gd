extends GutTest
## Verifies the complete authoritative seat transaction and lifecycle matrix.

const PLAYER_SCENE: PackedScene = preload("res://scenes/entities/player.tscn")
const FIXED_DELTA: float = 1.0 / 60.0

var _runtime: Node3D
var _replicator: VehicleReplicator
var _interaction: VehicleInteraction
var _actors: Dictionary[int, ActorMotion] = { }
var _states: Dictionary[int, Dictionary] = { }
var _exit_blocked: bool = false


## Commits entry only after host acceptance and leaves an out-of-range rejection snap-free.
func test_host_confirmed_entry_accepts_without_mutating_rejection() -> void:
	await _configure([1])
	var descriptor: Dictionary = _descriptor(0)
	var actor: ActorMotion = _actors[1]
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(int(descriptor.id))
	actor.global_position = _entry_position(vehicle)
	var before_rejection: Transform3D = actor.global_transform
	actor.global_position += Vector3(20.0, 0.0, 0.0)

	var rejected: Dictionary = _interaction.try_enter(
		1, _player_ref(1), _vehicle_ref(descriptor), _context(), 1
	)
	assert_eq(rejected.status, VehicleInteraction.STATUS_REJECTED)
	assert_eq(rejected.failure, &"ENTRY_OUT_OF_RANGE")
	assert_eq(actor.global_transform, before_rejection.translated(Vector3(20.0, 0.0, 0.0)))
	assert_true(_replicator.binding_for_participant(1).is_empty())

	actor.global_position = _entry_position(vehicle)
	var applied: Dictionary = _interaction.try_enter(
		1, _player_ref(1), _vehicle_ref(descriptor), _context(), 2
	)
	assert_eq(applied.status, VehicleInteraction.STATUS_APPLIED)
	assert_eq(int(_replicator.binding_for_participant(1).id), int(descriptor.id))
	assert_eq(actor.collision_layer, 0)
	assert_false((actor.get_node("PresentationAnchor") as Node3D).visible)
	var driver_seat: Marker3D = vehicle.get_node("Sockets/DriverSeat") as Marker3D
	assert_eq(actor.global_transform, driver_seat.global_transform)


## Rejects a blocked chosen entry without changing body, presentation, or occupancy.
func test_blocked_entry_is_atomic() -> void:
	await _configure([1])
	var descriptor: Dictionary = _descriptor(0)
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(int(descriptor.id))
	var actor: ActorMotion = _actors[1]
	actor.global_position = _entry_position(vehicle)
	var before_transform: Transform3D = actor.global_transform
	var before_layer: int = actor.collision_layer
	var before_mask: int = actor.collision_mask
	var presentation: Node3D = actor.get_node("PresentationAnchor") as Node3D
	_exit_blocked = true

	var rejected: Dictionary = _interaction.try_enter(
		1, _player_ref(1), _vehicle_ref(descriptor), _context(), 1
	)
	assert_eq(rejected.failure, &"ENTRY_BLOCKED")
	assert_eq(actor.global_transform, before_transform)
	assert_eq(actor.collision_layer, before_layer)
	assert_eq(actor.collision_mask, before_mask)
	assert_true(presentation.visible)
	assert_true(_replicator.binding_for_participant(1).is_empty())
	assert_eq(_replicator.driver_for_entity(int(descriptor.id)), 0)
	_exit_blocked = false


## Sorts reversed same-tick requests by participant so exactly one claimant wins.
func test_same_tick_claim_has_one_deterministic_winner() -> void:
	await _configure([1, 2])
	var descriptor: Dictionary = _descriptor(0)
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(int(descriptor.id))
	_actors[1].global_position = _entry_position(vehicle)
	_actors[2].global_position = _entry_position(vehicle)
	assert_true(_interaction.enqueue_action(_entry_request(2, descriptor, 1, 20)).ok)
	assert_true(_interaction.enqueue_action(_entry_request(1, descriptor, 1, 20)).ok)

	var resolved: Array[Dictionary] = _interaction.process_actions(20)
	assert_eq(resolved.size(), 2)
	assert_eq(resolved[0].participant_id, 1)
	assert_eq(resolved[0].result.status, VehicleInteraction.STATUS_APPLIED)
	assert_eq(resolved[1].participant_id, 2)
	assert_eq(resolved[1].result.failure, &"SEAT_OCCUPIED")
	assert_eq(_replicator.driver_for_entity(int(descriptor.id)), 1)
	var duplicate: Dictionary = _interaction.enqueue_action(_entry_request(1, descriptor, 1, 20))
	assert_eq(duplicate.cached_result, resolved[0].result)
	assert_eq(_replicator.driver_for_entity(int(descriptor.id)), 1)


## Gives each participant an independent queue and resolves at most four each tick.
func test_action_queue_is_participant_scoped_rate_limited_and_fair() -> void:
	await _configure([1, 2])
	var descriptor: Dictionary = _descriptor(0)
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(int(descriptor.id))
	_actors[1].global_position = _entry_position(vehicle)
	_actors[2].global_position = _entry_position(vehicle)
	for sequence: int in range(1, 9):
		assert_true(_interaction.enqueue_action(_entry_request(1, descriptor, sequence, 20)).ok)
		assert_true(_interaction.enqueue_action(_entry_request(2, descriptor, sequence, 20)).ok)

	var first_tick: Array[Dictionary] = _interaction.process_actions(20)
	assert_eq(first_tick.size(), 8)
	assert_eq(
		first_tick.filter(func(row: Dictionary) -> bool: return row.participant_id == 1).size(),
		4,
	)
	assert_eq(
		first_tick.filter(func(row: Dictionary) -> bool: return row.participant_id == 2).size(),
		4,
	)
	assert_eq(_interaction.process_actions(20).size(), 8)

	var next_sequence: int = 9
	while next_sequence <= 32:
		var queued: Dictionary = _interaction.enqueue_action(
			_entry_request(1, descriptor, next_sequence, 20)
		)
		if queued.ok:
			_interaction.process_actions(20)
		next_sequence += 1
	assert_eq(
		_interaction.enqueue_action(_entry_request(1, descriptor, 33, 20)).failure,
		&"RATE_LIMIT",
	)
	assert_true(_interaction.enqueue_action(_entry_request(1, descriptor, 33, 80)).ok)


## Retains the full seat transaction for moving and blocked exits, then uses left first.
func test_exit_moving_and_blocked_are_atomic_before_clear_exit() -> void:
	await _configure([1])
	var descriptor: Dictionary = _descriptor(0)
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(int(descriptor.id))
	_actors[1].global_position = _entry_position(vehicle)
	assert_eq(
		_interaction.try_enter(1, _player_ref(1), _vehicle_ref(descriptor), _context(), 1).status,
		VehicleInteraction.STATUS_APPLIED,
	)
	var binding_before: Dictionary = _replicator.binding_for_participant(1)
	vehicle.velocity = Vector3(0.5, 0.0, 0.0)
	var moving: Dictionary = _interaction.try_exit(1, _player_ref(1), _context(), 2)
	assert_eq(moving.failure, &"EXIT_MOVING")
	assert_eq(_replicator.binding_for_participant(1), binding_before)

	vehicle.velocity = Vector3.ZERO
	_exit_blocked = true
	var blocked: Dictionary = _interaction.try_exit(1, _player_ref(1), _context(), 3)
	assert_eq(blocked.failure, &"EXIT_BLOCKED")
	assert_eq(_replicator.binding_for_participant(1), binding_before)
	assert_eq(_actors[1].collision_layer, 0)

	_exit_blocked = false
	var exited: Dictionary = _interaction.try_exit(1, _player_ref(1), _context(), 4)
	assert_eq(exited.status, VehicleInteraction.STATUS_APPLIED)
	assert_true(_replicator.binding_for_participant(1).is_empty())
	assert_eq(_actors[1].collision_layer, 2)
	assert_eq(
		_actors[1].global_transform,
		(vehicle.get_node("Sockets/ExitLeft") as Marker3D).global_transform,
	)


## Rebinds seated resync without reseating, then death releases and coasts the car.
func test_resync_preserves_seat_and_driver_death_coasts() -> void:
	await _configure([1])
	var descriptor: Dictionary = _descriptor(0)
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(int(descriptor.id))
	_actors[1].global_position = _entry_position(vehicle)
	assert_eq(
		_interaction.try_enter(1, _player_ref(1), _vehicle_ref(descriptor), _context(), 1).status,
		VehicleInteraction.STATUS_APPLIED,
	)
	var before: Dictionary = _replicator.binding_for_participant(1)
	var rebound: Dictionary = _interaction.rebind_commands(1)
	assert_true(rebound.ok)
	var after: Dictionary = _replicator.binding_for_participant(1)
	assert_eq(after.id, before.id)
	assert_gt(int(after.control_revision), int(before.control_revision))

	vehicle.velocity = Vector3(4.0, 0.0, 0.0)
	var released: Dictionary = _interaction.release_for_lifecycle(1, &"DEATH")
	assert_true(released.ok)
	assert_true(_replicator.binding_for_participant(1).is_empty())
	assert_true(_replicator._coasting_entity_ids.has(int(descriptor.id)))
	var previous_speed: float = vehicle.velocity.length()
	_replicator.step_authority(FIXED_DELTA, 16, 1)
	assert_lt(vehicle.velocity.length(), previous_speed)


## Releases lifecycle ownership at epoch saturation without wrapping or retaining a driver.
func test_disconnect_releases_final_epoch_and_permanently_retires_assignment() -> void:
	await _configure([1])
	var descriptor: Dictionary = _descriptor(0)
	var entity_id: int = int(descriptor.id)
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(entity_id)
	_actors[1].global_position = _entry_position(vehicle)
	assert_eq(
		_interaction.try_enter(1, _player_ref(1), _vehicle_ref(descriptor), _context(), 1).status,
		VehicleInteraction.STATUS_APPLIED,
	)
	var record: Dictionary = _replicator._records_by_id[entity_id]
	record.descriptor.control_revision = DriveCommandCodec.MAX_INPUT_EPOCH

	var released: Dictionary = _interaction.release_for_lifecycle(1, &"DISCONNECT")
	assert_true(released.ok)
	assert_true(_replicator.binding_for_participant(1).is_empty())
	assert_eq(
		int(_replicator.descriptor_for_entity(entity_id).control_revision),
		DriveCommandCodec.MAX_INPUT_EPOCH,
	)
	assert_false(_replicator.can_assign_driver(1, entity_id))


## Fences old-match work on reset and clears a terminal vehicle's occupant once.
func test_reset_and_destruction_clear_control_without_stale_replay() -> void:
	await _configure([1])
	var descriptor: Dictionary = _descriptor(0)
	var vehicle: VehicleMotion = _replicator.vehicle_for_entity(int(descriptor.id))
	_actors[1].global_position = _entry_position(vehicle)
	assert_eq(
		_interaction.try_enter(1, _player_ref(1), _vehicle_ref(descriptor), _context(), 1).status,
		VehicleInteraction.STATUS_APPLIED,
	)
	var destroyed: Dictionary = _interaction.release_for_destruction(int(descriptor.id))
	assert_true(destroyed.ok)
	assert_true(_replicator.binding_for_participant(1).is_empty())
	assert_eq(vehicle.velocity, Vector3.ZERO)

	assert_true(_interaction.enqueue_action(_entry_request(1, descriptor, 2, 30)).ok)
	assert_true(_interaction.reset(2))
	assert_true(_interaction.process_actions(30).is_empty())
	var stale: Dictionary = (
		_interaction
		. try_enter(
			1,
			_player_ref(1),
			_vehicle_ref(descriptor),
			{ "match_revision": 1 },
			3,
		)
	)
	assert_eq(stale.failure, &"STALE_ACTION_CONTEXT")


## Builds production vehicle instances and injected lifecycle collaborators for one case.
func _configure(participant_ids: Array[int]) -> void:
	_runtime = Node3D.new()
	add_child_autofree(_runtime)
	_replicator = VehicleReplicator.new()
	var anchors: Array[Dictionary] = [
		{
			"world_id": &"brackett/test/parked_car_latch_01",
			"transform": Transform3D.IDENTITY,
		},
	]
	assert_true(
		(
			_replicator
			. configure_authority(
				_runtime,
				anchors,
				EntityGenerationTracker.new(),
			)
		)
	)
	for participant_id: int in participant_ids:
		var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
		actor.name = "Player%d" % participant_id
		_runtime.add_child(actor)
		_actors[participant_id] = actor
		_states[participant_id] = {
			"entity_ref": { "id": participant_id + 100, "generation": 1 },
			"alive": true,
		}
	_interaction = VehicleInteraction.new()
	assert_true(
		(
			_interaction
			. configure(
				_replicator,
				_player_lookup,
				_player_state_lookup,
				_exit_blocked_query,
				1,
			)
		)
	)
	await get_tree().process_frame


## Returns the test-owned actor through the same injected production seam Match uses.
func _player_lookup(participant_id: int) -> ActorMotion:
	return _actors.get(participant_id)


## Returns immutable lifecycle state for generation/alive transaction fences.
func _player_state_lookup(participant_id: int) -> Dictionary:
	return (_states.get(participant_id, { }) as Dictionary).duplicate(true)


## Supplies deterministic blocked/clear outcomes without replacing interaction logic.
func _exit_blocked_query(
	_transform: Transform3D,
	_participant_id: int,
	_actor: ActorMotion,
	_vehicle: VehicleMotion,
) -> bool:
	return _exit_blocked


## Returns one sorted immutable descriptor from the production replication owner.
func _descriptor(index: int) -> Dictionary:
	return _replicator.descriptor_rows()[index]


## Builds the exact current player EntityRef expected by VehicleInteraction.
func _player_ref(participant_id: int) -> Dictionary:
	return (_states[participant_id].entity_ref as Dictionary).duplicate()


## Builds one vehicle generation fence from a current descriptor.
func _vehicle_ref(descriptor: Dictionary) -> Dictionary:
	return { "id": int(descriptor.id), "generation": int(descriptor.generation) }


## Returns the active MatchRevision fence for direct transaction tests.
func _context() -> Dictionary:
	return { "match_revision": 1 }


## Places a player at an authored entry socket inside the production range check.
func _entry_position(vehicle: VehicleMotion) -> Vector3:
	return (vehicle.get_node("Sockets/EntryLeft") as Marker3D).global_position


## Builds one complete queued entry request for same-tick ordering and reset tests.
func _entry_request(
	participant_id: int,
	descriptor: Dictionary,
	action_sequence: int,
	accepted_tick: int,
) -> Dictionary:
	return {
		"participant_id": participant_id,
		"player_ref": _player_ref(participant_id),
		"vehicle_ref": _vehicle_ref(descriptor),
		"match_revision": 1,
		"accepted_tick": accepted_tick,
		"action_sequence": action_sequence,
		"kind": VehicleInteraction.ACTION_ENTER,
	}
