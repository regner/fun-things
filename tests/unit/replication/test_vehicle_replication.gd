extends GutTest
## Verifies Match vehicle EntityRefs, baseline state, host stepping, and RPC stream ownership.

const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")
const FIXED_DELTA: float = 1.0 / 60.0


## Creates all authored parked cars with globally distinct Match EntityRefs.
func test_standalone_registers_authored_vehicle_rows_with_player_state() -> void:
	var replication: MatchReplication = _add_match_replication()
	assert_true(replication.configure_standalone())
	var rows: Array[Dictionary] = replication._capture_rows()
	assert_eq(rows.size(), 4)
	var ids: Dictionary[int, bool] = {}
	var vehicle_count: int = 0
	for row: Dictionary in rows:
		assert_false(ids.has(int(row.id)))
		ids[int(row.id)] = true
		if int(row.kind) == VehicleReplicator.ENTITY_KIND_VEHICLE:
			vehicle_count += 1
	assert_eq(vehicle_count, 3)
	assert_eq(replication._vehicle_replicator.descriptor_rows().size(), 3)


## Drives one assigned host car only through its bounded queue and shared motion step.
func test_interaction_approved_binding_steps_one_authoritative_vehicle() -> void:
	var replication: MatchReplication = _add_match_replication()
	assert_true(replication.configure_standalone())
	var assignment: Dictionary = _assign_driver(replication, 1)
	assert_true(assignment.ok)
	var entity_id: int = int(assignment.entity_ref.id)
	var input_epoch: int = int(assignment.input_epoch)
	var vehicle: VehicleMotion = replication.vehicle_for_entity(entity_id)
	var start: Vector3 = vehicle.global_position
	for tick: int in range(1, 31):
		# The held-input contract numbers one immutable frame per client physics tick.
		# gdstyle:ignore=quality/allocation-in-loop
		var command := DriveCommand.new(tick, tick, 1.0, 0.5, 0.0, false)
		var encoded: Dictionary = DriveCommandCodec.encode(command, input_epoch)
		assert_true(
			replication._vehicle_replicator.offer_command(
				1,
				DriveCommandCodec.decode(encoded.packet),
				tick * 16,
			).accepted
		)
		replication._vehicle_replicator.step_authority(FIXED_DELTA, tick * 16, tick)
	assert_gt(vehicle.global_position.distance_to(start), 0.25)
	assert_eq(replication._vehicle_replicator.acknowledgement(1), 30)


## Commits entry with a fresh foot epoch and clears pre-seat held intent atomically.
func test_entry_transaction_fences_host_foot_queue() -> void:
	var replication: MatchReplication = _add_match_replication()
	assert_true(replication.configure_standalone())
	var participant_id: int = 1
	var descriptor: Dictionary = replica_rows(replication)[0]
	var vehicle: VehicleMotion = replication.vehicle_for_entity(int(descriptor.id))
	var actor: ActorMotion = replication.actor_for_participant(participant_id)
	actor.global_position = (vehicle.get_node("Sockets/EntryLeft") as Marker3D).global_position
	var stale: Dictionary = FootCommandCodec.decode(
		FootCommandCodec.encode(
			FootCommand.new(1, 1, Vector2.RIGHT, 0.0, false, false),
			1,
		).packet
	)
	assert_true(replication._input_authority.offer(participant_id, stale, 0).accepted)
	assert_true(replication.request_vehicle_entry(participant_id, int(descriptor.id), 1, 1).ok)
	replication._vehicle_interaction.process_actions(1)

	assert_eq(replication._input_authority.input_epoch(participant_id), 2)
	assert_eq(replication._input_authority.queue(participant_id).size(), 0)
	assert_false(replication._input_authority.offer(participant_id, stale, 1).accepted)
	assert_false(replication._vehicle_replicator.binding_for_participant(participant_id).is_empty())


## Routes listen-server intent through codec validation and the held authority queue.
func test_listen_server_vehicle_input_uses_validated_host_queue() -> void:
	var replication: MatchReplication = _add_match_replication()
	assert_true(replication.configure_standalone())
	var assignment: Dictionary = _assign_driver(replication, 1)
	assert_true(assignment.ok)
	replication._sync_vehicle_occupancy_presentation()
	var vehicle: VehicleMotion = replication.vehicle_for_entity(int(assignment.entity_ref.id))
	var start: Vector3 = vehicle.global_position

	assert_true(
		replication.submit_host_local_vehicle_command(
			DriveCommand.new(1, 1, 1.0, 0.0, 0.0, false)
		)
	)
	assert_false(
		replication.submit_host_local_vehicle_command(
			DriveCommand.new(1, 2, 1.0, 0.0, 0.0, false)
		)
	)
	replication._vehicle_replicator.step_authority(FIXED_DELTA, 1, 1)
	assert_gt(vehicle.global_position.distance_to(start), 0.0)
	assert_eq(replication._vehicle_replicator.acknowledgement(1), 1)


## Rejects an old assignment packet after the same participant reacquires the EntityRef.
func test_reassignment_rejects_old_input_epoch() -> void:
	var replication: MatchReplication = _add_match_replication()
	assert_true(replication.configure_standalone())
	var first: Dictionary = _assign_driver(replication, 1)
	assert_true(first.ok)
	var entity_id: int = int(first.entity_ref.id)
	var stale: Dictionary = DriveCommandCodec.decode(
		DriveCommandCodec.encode(
			DriveCommand.new(1, 1, 1.0, 0.0, 0.0, false),
			first.input_epoch,
		).packet
	)

	replication._vehicle_replicator.commit_driver_release(1, false)
	var second: Dictionary = _assign_driver(replication, 1, entity_id)
	assert_true(second.ok)
	assert_gt(int(second.input_epoch), int(first.input_epoch))
	var refused: Dictionary = replication._vehicle_replicator.offer_command(1, stale, 10)
	assert_false(refused.accepted)
	assert_eq(refused.failure, &"STALE_COMMAND_CONTEXT")
	var current: Dictionary = DriveCommandCodec.decode(
		DriveCommandCodec.encode(
			DriveCommand.new(1, 1, 1.0, 0.0, 0.0, false), second.input_epoch
		).packet
	)
	assert_true(replication._vehicle_replicator.offer_command(1, current, 11).accepted)


## Exhausts the fixed assignment epoch without allowing it to wrap to an old value.
func test_assignment_input_epoch_saturates_without_wrapping() -> void:
	var replication: MatchReplication = _add_match_replication()
	assert_true(replication.configure_standalone())
	var entity_id: int = 0
	for _index: int in range(127):
		var assignment: Dictionary = _assign_driver(replication, 1, entity_id)
		assert_true(assignment.ok)
		entity_id = int(assignment.entity_ref.id)
		replication._vehicle_replicator.commit_driver_release(1, false)
	assert_eq(
		int(replication._vehicle_replicator.descriptor_rows()[0].control_revision),
		DriveCommandCodec.MAX_INPUT_EPOCH,
	)
	assert_false(_assign_driver(replication, 1, entity_id).ok)


## Keeps the caller's vehicle and queue when an unoccupied target epoch is exhausted.
func test_exhausted_unoccupied_target_does_not_release_caller() -> void:
	var replication: MatchReplication = _add_match_replication()
	assert_true(replication.configure_standalone())
	var rows: Array[Dictionary] = replica_rows(replication)
	var caller_vehicle_id: int = int(rows[0].id)
	var target_vehicle_id: int = int(rows[1].id)
	var assignment: Dictionary = _assign_driver(
		replication, 1, caller_vehicle_id
	)
	assert_true(assignment.ok)
	var caller_queue: VehicleInputQueue = (
		replication._vehicle_replicator._queues_by_participant[1]
	)
	_set_control_revision(replication, target_vehicle_id, DriveCommandCodec.MAX_INPUT_EPOCH)
	var descriptors_before: Array[Dictionary] = replica_rows(replication)
	var binding_before: Dictionary = replication._vehicle_replicator.binding_for_participant(1)

	assert_false(_assign_driver(replication, 1, target_vehicle_id).ok)
	assert_eq(replica_rows(replication), descriptors_before)
	assert_eq(replication._vehicle_replicator.binding_for_participant(1), binding_before)
	assert_same(replication._vehicle_replicator._queues_by_participant[1], caller_queue)


## Keeps both drivers and queues when an occupied target lacks two epoch revisions.
func test_exhausted_occupied_target_does_not_release_either_driver() -> void:
	var replication: MatchReplication = _add_match_replication()
	assert_true(replication.configure_standalone())
	var rows: Array[Dictionary] = replica_rows(replication)
	var caller_vehicle_id: int = int(rows[0].id)
	var target_vehicle_id: int = int(rows[1].id)
	assert_true(_assign_driver(replication, 1, caller_vehicle_id).ok)
	assert_true(_assign_driver(replication, 7, target_vehicle_id).ok)
	var caller_queue: VehicleInputQueue = (
		replication._vehicle_replicator._queues_by_participant[1]
	)
	var target_queue: VehicleInputQueue = (
		replication._vehicle_replicator._queues_by_participant[7]
	)
	_set_control_revision(
		replication, target_vehicle_id, DriveCommandCodec.MAX_INPUT_EPOCH - 1
	)
	var descriptors_before: Array[Dictionary] = replica_rows(replication)
	var caller_before: Dictionary = replication._vehicle_replicator.binding_for_participant(1)
	var target_before: Dictionary = replication._vehicle_replicator.binding_for_participant(7)

	assert_false(_assign_driver(replication, 1, target_vehicle_id).ok)
	assert_eq(replica_rows(replication), descriptors_before)
	assert_eq(replication._vehicle_replicator.binding_for_participant(1), caller_before)
	assert_eq(replication._vehicle_replicator.binding_for_participant(7), target_before)
	assert_same(replication._vehicle_replicator._queues_by_participant[1], caller_queue)
	assert_same(replication._vehicle_replicator._queues_by_participant[7], target_queue)


## Re-enables the same replica body after release, remote state, and reassignment.
func test_reassignment_rebinds_same_vehicle_after_remote_snapshot() -> void:
	var authority: MatchReplication = _add_match_replication()
	assert_true(authority.configure_standalone())
	var first: Dictionary = _assign_driver(authority, 7)
	assert_true(first.ok)
	var entity_id: int = int(first.entity_ref.id)
	var replica_root := Node3D.new()
	add_child_autofree(replica_root)
	var replica := VehicleReplicator.new()
	assert_true(replica.configure_replica(replica_root))
	assert_true(replica.install_descriptors(replica_rows(authority), 7))
	var vehicle: VehicleMotion = replica.vehicle_for_entity(entity_id)
	assert_true(vehicle.simulation_enabled)

	authority._vehicle_replicator.commit_driver_release(7, false)
	assert_true(replica.install_descriptors(replica_rows(authority), 7))
	assert_false(vehicle.simulation_enabled)
	var remote_state: Dictionary = _vehicle_state(authority, entity_id)
	assert_true(replica.apply_replica_state(remote_state, 7, 0, 10))
	assert_false(vehicle.simulation_enabled)

	assert_true(_assign_driver(authority, 7, entity_id).ok)
	assert_true(replica.install_descriptors(replica_rows(authority), 7))
	assert_same(replica.vehicle_for_entity(entity_id), vehicle)
	assert_true(vehicle.simulation_enabled)
	assert_true(replica.predict_local(DriveCommand.new(1, 1, 1.0, 0.0, 0.0, false), FIXED_DELTA))


## Installs a reliable exit pose and fresh foot fence before old prediction can replay.
func test_reliable_transfer_clears_foot_prediction_and_applies_exact_exit_pose() -> void:
	var replication: MatchReplication = _add_match_replication()
	assert_true(replication.configure_standalone())
	var actor: ActorMotion = replication.actor_for_participant(1)
	var prediction: FootPrediction = replication._prediction_owner()
	assert_true(prediction.bind_actor(actor))
	assert_true(
		prediction.predict(
			FootCommand.new(1, 1, Vector2.RIGHT, 0.0, false, false),
			FIXED_DELTA,
		)
	)
	assert_eq(prediction._history.size(), 1)
	var player_ref: Dictionary = replication._lifecycle.entity_ref_for(1)

	assert_true(
		replication._install_vehicle_transfer_rows(
			[
				{
					"participant_id": 1,
					"player_id": int(player_ref.id),
					"generation": int(player_ref.generation),
					"seated": false,
					"foot_input_epoch": 2,
					"x": 24.0,
					"y": 0.5,
					"z": -17.0,
					"yaw": 1.25,
					"transaction_revision": 1,
				},
			]
		)
	)
	assert_eq(prediction._history.size(), 0)
	assert_eq(int(replication._client.input_epoch), 2)
	assert_true(actor.global_position.is_equal_approx(Vector3(24.0, 0.5, -17.0)))
	assert_true(is_equal_approx(actor.rotation.y, 1.25))


## Includes current vehicle rows in the immutable late-join baseline transaction.
func test_late_join_baseline_contains_every_current_vehicle() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var replication: MatchReplication = match.get_node("Replication") as MatchReplication
	var transport := FakeReplicationTransport.new()
	assert_true(
		replication.configure_network(
			ReplicationIdentity.create_session_id(),
			1,
			true,
			Callable(),
			transport,
		)
	)
	assert_true(replication.admit_peer(22, 2))
	assert_true(_assign_driver(replication, 2).ok)
	assert_true(replication.begin_admission_for_peer(22).ok)
	var baseline_event: Dictionary = transport.events[0]
	assert_eq(baseline_event.kind, &"baseline")
	var vehicle_rows: int = 0
	for packet: PackedByteArray in baseline_event.packets:
		var decoded: Dictionary = replication._codec.decode_movement(packet)
		assert_true(decoded.ok)
		for row: Dictionary in decoded.rows:
			if int(row.kind) == VehicleReplicator.ENTITY_KIND_VEHICLE:
				vehicle_rows += 1
	assert_eq(vehicle_rows, 3)


## Keeps actions/results on control, descriptors on state, and drive intent on input streams.
func test_vehicle_rpcs_use_existing_match_replication_streams() -> void:
	var replication: MatchReplication = _add_match_replication()
	var config: Dictionary = replication.get_script().get_rpc_config()
	assert_eq(int(config[&"_request_vehicle_action"].channel), 0)
	assert_eq(int(config[&"_receive_vehicle_action_result"].channel), 0)
	assert_eq(int(config[&"_submit_vehicle_command"].channel), 2)
	assert_eq(int(config[&"_receive_vehicle_descriptors"].channel), 1)


## Applies an interaction-approved low-level binding for replication-focused tests.
func _assign_driver(
	authority: MatchReplication,
	participant_id: int,
	entity_id: int = 0,
) -> Dictionary:
	if entity_id == 0:
		var rows: Array[Dictionary] = replica_rows(authority)
		entity_id = int(rows[0].id)
	return authority._vehicle_replicator.commit_driver_assignment(
		participant_id, entity_id
	)


## Returns the authority's immutable descriptor table with static typing for tests.
func replica_rows(authority: MatchReplication) -> Array[Dictionary]:
	return authority._vehicle_replicator.descriptor_rows()


## Sets one authority descriptor revision to a boundary value for exhaustion tests.
func _set_control_revision(
	authority: MatchReplication, entity_id: int, revision: int
) -> void:
	var record: Dictionary = authority._vehicle_replicator._records_by_id[entity_id]
	var descriptor: Dictionary = record.descriptor
	descriptor.control_revision = revision


## Finds one current measured vehicle row for replica application.
func _vehicle_state(authority: MatchReplication, entity_id: int) -> Dictionary:
	for row: Dictionary in authority._vehicle_replicator.capture_rows():
		if int(row.id) == entity_id:
			return row
	return {}


## Instantiates saved Match and returns its sole replication writer.
func _add_match_replication() -> MatchReplication:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	return match.get_node("Replication") as MatchReplication
