extends GutTest
## Verifies compact pedestrian decisions and the isolated FootCommand adapter.

var _navigation: SyntheticPopulationNavigation
var _reservations: CrossingReservations
var _core: PedestrianCore


## Creates one configured host-only core per test.
func before_each() -> void:
	_navigation = SyntheticPopulationNavigation.new()
	_reservations = CrossingReservations.new()
	assert_true(_reservations.configure(_navigation))
	_core = PedestrianCore.new()
	assert_true(_core.configure(_navigation, _reservations))


## Emits the production A2.1 command type with every field in its admitted range.
func test_foot_command_adapter_shape_and_ranges() -> void:
	var start_node: int = _navigation.grid_node(0, 0)
	assert_true(_core.add_agent(1, start_node, _navigation.node_position(start_node)))
	var commands: Array[FootCommand] = _core.step(1)
	assert_eq(commands.size(), 1)
	var command: FootCommand = commands[0]
	assert_not_null(command)
	assert_true(command.is_valid())
	assert_eq(command.client_tick, 1)
	assert_eq(command.sequence, 1)
	assert_true(command.move.is_finite())
	assert_lte(command.move.length(), 1.0)
	assert_true(is_finite(command.aim_yaw))
	assert_false(command.fire_held)
	assert_false(command.alt_held)


## Staggers all six decision phases while every identity emits 60 Hz intent.
func test_decisions_are_staggered_and_threat_reactions_are_bounded() -> void:
	for agent_id: int in range(1, 7):
		var start_node: int = _navigation.grid_node(agent_id - 1, 0)
		assert_true(
			_core.add_agent(agent_id, start_node, _navigation.node_position(start_node))
		)
	assert_true(
		_core.publish_threat(
			Vector2(18.0, 0.0),
			100.0,
			PedestrianCore.ThreatKind.GUNFIRE,
			0,
		)
	)

	for host_tick: int in PedestrianCore.DECISION_INTERVAL_TICKS:
		var commands: Array[FootCommand] = _core.step(host_tick)
		assert_eq(commands.size(), 6)
		for slot: int in commands.size():
			var position: Vector2 = _navigation.node_position(slot)
			_core.sync_position(slot + 1, position)

	for agent_id: int in range(1, 7):
		assert_eq(_core.decision_count(agent_id), 1)
		assert_between(
			_core.last_reaction_tick(agent_id),
			0,
			PedestrianCore.DECISION_INTERVAL_TICKS - 1,
		)


## Accepts only the declared threat kinds and rejects unknown enum values.
func test_threat_kind_validation() -> void:
	for kind: PedestrianCore.ThreatKind in [
		PedestrianCore.ThreatKind.GUNFIRE,
		PedestrianCore.ThreatKind.BLAST,
		PedestrianCore.ThreatKind.VEHICLE,
	]:
		assert_true(_core.publish_threat(Vector2.ZERO, 1.0, kind, 0))

	for invalid_kind: PedestrianCore.ThreatKind in [-1, 99]:
		assert_false(_core.publish_threat(Vector2.ZERO, 1.0, invalid_kind, 0))


## Considers a relevant eighth threat despite seven earlier irrelevant records.
func test_relevant_threat_at_scan_capacity_reacts_within_bound() -> void:
	var start_node: int = _navigation.grid_node(0, 0)
	var start: Vector2 = _navigation.node_position(start_node)
	assert_true(_core.add_agent(1, start_node, start))
	for index: int in PedestrianCore.MAX_THREATS_PER_DECISION - 1:
		assert_true(
			_core.publish_threat(
				Vector2(1000.0 + index, 1000.0),
				1.0,
				PedestrianCore.ThreatKind.VEHICLE,
				0,
				PedestrianCore.THREAT_LIFETIME_CAP_TICKS,
			)
		)
	assert_true(
		_core.publish_threat(
			start,
			1.0,
			PedestrianCore.ThreatKind.GUNFIRE,
			0,
			PedestrianCore.THREAT_LIFETIME_CAP_TICKS,
		)
	)

	for host_tick: int in PedestrianCore.DECISION_INTERVAL_TICKS:
		_core.step(host_tick)
	assert_between(
		_core.last_reaction_tick(1),
		0,
		PedestrianCore.DECISION_INTERVAL_TICKS - 1,
	)


## Receives two simultaneously relevant threats during the same bounded decision.
func test_simultaneously_relevant_threats_are_both_received() -> void:
	var start_node: int = _navigation.grid_node(0, 0)
	var start: Vector2 = _navigation.node_position(start_node)
	assert_true(_core.add_agent(1, start_node, start))
	assert_true(
		_core.publish_threat(
			start + Vector2.LEFT,
			2.0,
			PedestrianCore.ThreatKind.GUNFIRE,
			0,
		)
	)
	var first_threat_id: int = _core.latest_threat_id()
	assert_true(
		_core.publish_threat(
			start + Vector2.RIGHT,
			2.0,
			PedestrianCore.ThreatKind.BLAST,
			0,
		)
	)
	var second_threat_id: int = _core.latest_threat_id()

	for host_tick: int in PedestrianCore.DECISION_INTERVAL_TICKS:
		_core.step(host_tick)
	assert_between(
		_core.reaction_tick(1, first_threat_id),
		0,
		PedestrianCore.DECISION_INTERVAL_TICKS - 1,
	)
	assert_eq(
		_core.reaction_tick(1, second_threat_id),
		_core.reaction_tick(1, first_threat_id),
	)
	assert_eq(_core.last_reaction_threat_id(1), second_threat_id)


## Rejects the relevant ninth record when eight long-lived threats fill the live cap.
func test_relevant_ninth_threat_is_rejected_at_live_cap() -> void:
	var start_node: int = _navigation.grid_node(0, 0)
	var start: Vector2 = _navigation.node_position(start_node)
	assert_true(_core.add_agent(1, start_node, start))
	for index: int in PedestrianCore.MAX_THREATS:
		assert_true(
			_core.publish_threat(
				Vector2(1000.0 + index, 1000.0),
				1.0,
				PedestrianCore.ThreatKind.VEHICLE,
				0,
				PedestrianCore.THREAT_LIFETIME_CAP_TICKS,
			)
		)
	assert_false(
		_core.publish_threat(
			start,
			1.0,
			PedestrianCore.ThreatKind.BLAST,
			0,
			PedestrianCore.THREAT_LIFETIME_CAP_TICKS,
		)
	)


## Frees capacity before admission when existing records expire at this exact tick.
func test_publication_expires_records_before_live_cap_check() -> void:
	for index: int in PedestrianCore.MAX_THREATS:
		assert_true(
			_core.publish_threat(
				Vector2(1000.0 + index, 1000.0),
				1.0,
				PedestrianCore.ThreatKind.VEHICLE,
				0,
				PedestrianCore.DECISION_INTERVAL_TICKS,
			)
		)
	assert_true(
		_core.publish_threat(
			Vector2.ZERO,
			1.0,
			PedestrianCore.ThreatKind.GUNFIRE,
			PedestrianCore.DECISION_INTERVAL_TICKS,
		)
	)
	assert_eq(_core.latest_threat_id(), PedestrianCore.MAX_THREATS + 1)


## Preserves a live receipt while short-lived threat slots repeatedly churn.
func test_receipts_remain_bounded_during_threat_churn() -> void:
	var start_node: int = _navigation.grid_node(0, 0)
	var start: Vector2 = _navigation.node_position(start_node)
	assert_true(_core.add_agent(1, start_node, start))
	assert_true(
		_core.publish_threat(
			start,
			1.0,
			PedestrianCore.ThreatKind.BLAST,
			0,
			PedestrianCore.THREAT_LIFETIME_CAP_TICKS,
		)
	)
	var long_threat_id: int = _core.latest_threat_id()
	for _short_index: int in PedestrianCore.MAX_THREATS - 1:
		assert_true(
			_core.publish_threat(
				start,
				1.0,
				PedestrianCore.ThreatKind.GUNFIRE,
				0,
				PedestrianCore.DECISION_INTERVAL_TICKS,
			)
		)
	for host_tick: int in PedestrianCore.DECISION_INTERVAL_TICKS:
		_core.step(host_tick)
	var original_receipt_tick: int = _core.reaction_tick(1, long_threat_id)
	assert_between(
		original_receipt_tick,
		0,
		PedestrianCore.DECISION_INTERVAL_TICKS - 1,
	)
	assert_eq(_core.reaction_receipt_count(1), PedestrianCore.MAX_THREATS)

	for cycle: int in range(1, 5):
		var publish_tick: int = cycle * PedestrianCore.DECISION_INTERVAL_TICKS
		for _short_index: int in PedestrianCore.MAX_THREATS - 1:
			assert_true(
				_core.publish_threat(
					start,
					1.0,
					PedestrianCore.ThreatKind.GUNFIRE,
					publish_tick,
					PedestrianCore.DECISION_INTERVAL_TICKS,
				)
			)
		assert_eq(_core.reaction_receipt_count(1), 1)
		_core.step(publish_tick)
		_core.step(publish_tick + 1)
		assert_eq(_core.reaction_tick(1, long_threat_id), original_receipt_tick)
		assert_eq(_core.reaction_receipt_count(1), PedestrianCore.MAX_THREATS)
