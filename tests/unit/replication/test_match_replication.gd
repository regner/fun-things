extends GutTest
## Verifies saved Match composition and host player wiring without changing standalone ownership.

const MATCH_SCENE: PackedScene = preload("res://scenes/match/match.tscn")
const BASELINE_STALL_PEER: int = 22
const HANDOFF_STALL_PEER: int = 23
const ADMITTED_PEER: int = 24

var _now_msec: int = 0
var _timeout_replication: MatchReplication


## Keeps replication outside authored content roots and spawns host at the first anchor.
func test_saved_replication_root_configures_host_player_and_local_rig() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var replication: MatchReplication = match.get_node("Replication") as MatchReplication
	var rig: LocalRig = match.get_node("LocalRig") as LocalRig
	var spawn: Marker3D = match.get_node("Anchors/PlayerSpawns/Spawn01") as Marker3D

	assert_eq(replication.get_parent(), match)
	assert_false(replication.is_ancestor_of(match.get_node("World")))
	assert_false(replication.is_ancestor_of(match.get_node("Anchors")))
	assert_true(
		replication.configure_network(ReplicationIdentity.create_session_id(), 1, true)
	)
	var actor: ActorMotion = replication.actor_for_participant(1)
	assert_not_null(actor)
	assert_eq(replication.player_count(), 1)
	assert_eq(rig.controlled_actor(), actor)
	assert_almost_eq(actor.global_position.x, spawn.global_position.x, 0.001)
	assert_not_null(actor.get_node_or_null("PresentationAnchor/Visuals/Model"))


## Dev death, timed respawn, and reset each advance the entity generation fence.
func test_lifecycle_respawn_and_reset_retain_local_player_with_fresh_generations() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var replication: MatchReplication = match.get_node("Replication") as MatchReplication
	assert_true(replication.configure_standalone())
	var first_ref: Dictionary = replication.lifecycle_view().entity_ref

	assert_true(replication.trigger_test_death(1))
	assert_false(replication.lifecycle_view().alive)
	for _tick: int in PlayerLifecycle.RESPAWN_DELAY_TICKS:
		replication._physics_process(1.0 / 60.0)
	var respawn_ref: Dictionary = replication.lifecycle_view().entity_ref
	assert_true(replication.lifecycle_view().alive)
	assert_eq(respawn_ref.id, first_ref.id)
	assert_eq(respawn_ref.generation, first_ref.generation + 1)

	assert_true(replication.request_match_reset(1))
	var reset_ref: Dictionary = replication.lifecycle_view().entity_ref
	assert_eq(replication.match_revision(), 2)
	assert_true(replication.lifecycle_view().alive)
	assert_eq(reset_ref.id, first_ref.id)
	assert_eq(reset_ref.generation, respawn_ref.generation + 1)
	assert_eq(replication.lifecycle_view().roster.size(), 1)


## Saved Match binds PlayerLifecycle into both HUD lifecycle and roster seams.
func test_match_lifecycle_binding_drives_dead_hud_countdown() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var replication: MatchReplication = match.get_node("Replication") as MatchReplication
	var hud: Hud = match.get_node("LocalRig/UI/HUD") as Hud
	assert_true(replication.configure_standalone())
	assert_true(replication.trigger_test_death(1))

	assert_eq((hud.get_node("PlayerCard/Content/PlayerState") as Label).text, "DOWN")
	assert_true(hud.get_node("RespawnSlot").visible)
	assert_eq((hud.get_node("RespawnSlot/Content/RespawnValue") as Label).text, "3.0")
	assert_eq((hud.get_node("SessionCard/Content/SessionDetail") as Label).text, "")


## Mirrors a Session-owned remote sender without allocating another participant identity.
func test_host_accepts_current_session_peer_mapping_once() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var replication: MatchReplication = match.get_node("Replication") as MatchReplication
	assert_true(
		replication.configure_network(ReplicationIdentity.create_session_id(), 1, true)
	)

	assert_true(replication.admit_peer(42, 2))
	assert_true(replication.admit_peer(42, 2))
	assert_false(replication.admit_peer(42, 3))


## Services baseline and handoff deadlines without stopping admitted peers or host simulation.
func test_host_physics_expires_stalled_admissions_with_injected_clock() -> void:
	var transport: FakeReplicationTransport = _start_timeout_scenario()

	_now_msec = ReplicationAdmission.HANDOFF_TIMEOUT_MSEC
	_timeout_replication._physics_process(1.0 / 60.0)
	assert_eq(_timeout_replication.admitted_participant(HANDOFF_STALL_PEER), 0)
	assert_eq(_timeout_replication.admitted_participant(BASELINE_STALL_PEER), 0)
	assert_eq(_timeout_replication.admitted_participant(ADMITTED_PEER), 4)
	assert_eq(_timeout_replication.player_count(), 3)
	assert_not_null(_timeout_replication.actor_for_participant(2))
	assert_null(_timeout_replication.actor_for_participant(3))

	_now_msec = ReplicationAdmission.BASELINE_TIMEOUT_MSEC
	_timeout_replication._physics_process(1.0 / 60.0)
	assert_eq(_timeout_replication.admitted_participant(BASELINE_STALL_PEER), 0)
	assert_eq(_timeout_replication.admitted_participant(ADMITTED_PEER), 4)
	assert_eq(_timeout_replication.player_count(), 2)
	assert_null(_timeout_replication.actor_for_participant(2))
	assert_not_null(_timeout_replication.actor_for_participant(1))
	assert_not_null(_timeout_replication.actor_for_participant(4))
	assert_true(_has_abort(transport, BASELINE_STALL_PEER))
	assert_true(_has_abort(transport, HANDOFF_STALL_PEER))
	assert_false(_has_abort(transport, ADMITTED_PEER))


## Protects the four logical streams assigned by the replication contract.
func test_rpc_channels_match_control_state_input_and_movement_streams() -> void:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	var replication: MatchReplication = match.get_node("Replication") as MatchReplication
	var config: Dictionary = replication.get_script().get_rpc_config()

	assert_eq(int(config[&"_ready_for_baseline"].channel), 0)
	assert_eq(int(config[&"_acknowledge_baseline"].channel), 0)
	assert_eq(int(config[&"_acknowledge_handoff"].channel), 0)
	for method: StringName in [
		&"_receive_player_bindings",
		&"_receive_lifecycle_hydration",
		&"_receive_reset_begin",
		&"_receive_baseline_metadata",
		&"_receive_baseline_chunk",
		&"_receive_durable",
		&"_receive_handoff",
		&"_receive_grant",
	]:
		assert_eq(int(config[method].channel), 1, str(method))
	assert_eq(int(config[&"_submit_command"].channel), 2)
	assert_eq(int(config[&"_receive_movement"].channel), 3)


## Creates baseline-stalled, handoff-stalled and fully admitted runtime peers.
func _start_timeout_scenario() -> FakeReplicationTransport:
	var match: Node3D = MATCH_SCENE.instantiate() as Node3D
	add_child_autofree(match)
	_timeout_replication = match.get_node("Replication") as MatchReplication
	var transport := FakeReplicationTransport.new()
	transport.abort_callback = _remove_timed_out_peer
	assert_true(
		_timeout_replication.configure_network(
			ReplicationIdentity.create_session_id(), 1, true, _clock_msec, transport
		)
	)
	assert_true(_timeout_replication.admit_peer(BASELINE_STALL_PEER, 2))
	assert_true(_timeout_replication.admit_peer(HANDOFF_STALL_PEER, 3))
	assert_true(_timeout_replication.admit_peer(ADMITTED_PEER, 4))
	var baseline_stall: Dictionary = _timeout_replication.begin_admission_for_peer(
		BASELINE_STALL_PEER
	)
	var handoff_stall: Dictionary = _timeout_replication.begin_admission_for_peer(
		HANDOFF_STALL_PEER
	)
	var handoff: Dictionary = _timeout_replication.acknowledge_baseline_for_peer(
		HANDOFF_STALL_PEER, int(handoff_stall.baseline_id)
	)
	var admitted: Dictionary = _timeout_replication.begin_admission_for_peer(ADMITTED_PEER)
	var marker: Dictionary = _timeout_replication.acknowledge_baseline_for_peer(
		ADMITTED_PEER, int(admitted.baseline_id)
	)
	var grant: Dictionary = _timeout_replication.acknowledge_handoff_for_peer(
		ADMITTED_PEER, int(admitted.baseline_id), int(marker.commit_revision)
	)
	assert_true(grant.admitted)
	assert_true(baseline_stall.ok)
	assert_true(handoff.ok)
	assert_eq(_timeout_replication.player_count(), 4)
	return transport


## Returns deterministic monotonic time for runtime admission servicing.
func _clock_msec() -> int:
	return _now_msec


## Mirrors SessionService disconnect cleanup after a timeout transport abort.
func _remove_timed_out_peer(native_peer_id: int) -> void:
	_timeout_replication.remove_peer(native_peer_id, native_peer_id - 20)


## Reports one peer-local abort recorded by the fake runtime transport.
func _has_abort(transport: FakeReplicationTransport, native_peer_id: int) -> bool:
	for event: Dictionary in transport.events:
		if event.kind == &"abort" and int(event.peer) == native_peer_id:
			return true
	return false
