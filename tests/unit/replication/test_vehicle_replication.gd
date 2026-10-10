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
func test_test_driver_seam_steps_one_authoritative_vehicle() -> void:
	var replication: MatchReplication = _add_match_replication()
	assert_true(replication.configure_standalone())
	var assignment: Dictionary = replication.assign_vehicle_driver_for_testing(1)
	assert_true(assignment.ok)
	var entity_id: int = int(assignment.entity_ref.id)
	var vehicle: VehicleMotion = replication.vehicle_for_entity(entity_id)
	var start: Vector3 = vehicle.global_position
	for tick: int in range(1, 31):
		# The held-input contract numbers one immutable frame per client physics tick.
		# gdstyle:ignore=quality/allocation-in-loop
		var command := DriveCommand.new(tick, tick, 1.0, 0.5, 0.0, false)
		var encoded: Dictionary = DriveCommandCodec.encode(
			command,
			VehicleReplicator.INPUT_EPOCH,
		)
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
	assert_true(replication.assign_vehicle_driver_for_testing(2).ok)
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


## Keeps drive intent on channel two and descriptors on ordered reliable state.
func test_vehicle_rpcs_use_existing_match_replication_streams() -> void:
	var replication: MatchReplication = _add_match_replication()
	var config: Dictionary = replication.get_script().get_rpc_config()
	assert_eq(int(config[&"_submit_vehicle_command"].channel), 2)
	assert_eq(int(config[&"_receive_vehicle_descriptors"].channel), 1)


## Instantiates saved Match and returns its sole replication writer.
func _add_match_replication() -> MatchReplication:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	return match.get_node("Replication") as MatchReplication
