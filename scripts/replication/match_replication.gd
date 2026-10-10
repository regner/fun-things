class_name MatchReplication  # gdstyle:ignore=format/max-line-length,quality/max-file-length,quality/max-class-variables,quality/max-public-methods
extends Node
## Coordinates Match-local authoritative players, admission, input, and latest-state replication.

signal input_granted(participant_id: int)
signal input_recovered(participant_id: int)
signal movement_applied(participant_id: int)
signal vehicle_action_resolved(result: Dictionary)

const PLAYER_SCENE: PackedScene = preload("res://scenes/entities/player.tscn")
const INITIAL_MATCH_REVISION: int = 1
const MOVEMENT_INTERVAL_TICKS: int = 3
const SPAWN_COLLISION_MASK: int = 7
const PLAYER_CLEARANCE_RADIUS_M: float = 0.45
const PLAYER_CLEARANCE_HEIGHT_M: float = 2.0
const INPUT_RATE_PER_SECOND: float = 60.0
const INPUT_BURST: float = 8.0
const MAX_VEHICLE_ACTION_ENVELOPE_BYTES: int = 4_096
const VEHICLE_ENTRY_PRESENTATION_TICKS: int = 18
const RESET_ADMISSION_TIMEOUT_MSEC: int = 15_000
const PHASE_MAPPED: StringName = &"mapped"
const ENTITY_KIND_PLAYER: int = 1
const PHASE_LIVE: int = 1
const PHASE_REMOVED: int = 3
const MOVEMENT_FLAG_GROUNDED: int = 1 << 0

@export_range(100, 150, 1) var remote_extrapolation_msec: int = 125
@export_range(1, 250, 1) var remote_authority_blend_msec: int = 150

var _codec := MeasuredReplicationCodec.new()
var _identities := PeerIdentityRegistry.new()
var _transport: ReplicationTransport
var _admission: ReplicationAdmission
var _assembler := BaselineAssembler.new()
var _store: ReplicaStateStore
var _input_authority := FootInputAuthority.new()
var _vehicle_replicator: VehicleReplicator
var _vehicle_interaction: VehicleInteraction
var _context: Dictionary = {
	"session_id": "",
	"local_participant_id": 0,
	"is_host": false,
	"clock": Callable(),
	"command_rejections": {},
}
var _configured: bool = false
var _client: Dictionary = {
	"baseline_installed": false,
	"grant_received": false,
	"input_open": false,
	"local_input_enabled": true,
	"input_epoch": 1,
	"input_recovery_pending": false,
	"last_recovery_correction_metres": 0.0,
	"last_command_packet": PackedByteArray(),
	"prediction": FootPrediction.new(),
	"remote_smoothers": {},
	"vehicle_transfer_revision_by_participant": {},
}
var _sequence: Dictionary = {
	"physics_tick": 0,
	"movement_sequence": 0,
	"baseline_id": 0,
	"durable_revision": 0,
	"match_revision": INITIAL_MATCH_REVISION,
}
var _actors_by_participant: Dictionary[int, ActorMotion] = {}
var _replica_pose_generation_by_participant: Dictionary[int, int] = {}
var _peer_by_participant: Dictionary[int, int] = {}
var _waiting_admission_deadline_by_peer: Dictionary[int, int] = {}
var _spawn_reservations := SpawnReservations.new()
var _resetting: bool = false
var _standalone: bool = false
var _suppress_lifecycle_publish: bool = false
var _input_state_by_participant: Dictionary[int, Dictionary] = {}
var _admitted_peers: Dictionary[int, bool] = {}
var _player_identity: Dictionary = {
	"tracker": EntityGenerationTracker.new(),
	"binding_by_participant": {},
	"participant_by_entity": {},
	"spawn_slot_by_participant": {},
}

@onready var _lifecycle: PlayerLifecycle = get_node("../PlayerLifecycle") as PlayerLifecycle


## Remains inert in standalone Match composition until Boot supplies a network session.
func _ready() -> void:
	set_physics_process(false)


## Runs authoritative remote motion or client intent and latest-state presentation.
func _physics_process(delta: float) -> void:
	if not _configured:
		return

	_sequence.physics_tick += 1
	if _context.is_host:
		var now_msec: int = _now_msec()
		_admission.expire_attempts(now_msec)
		_expire_waiting_mapped_peers(now_msec)
		_lifecycle.step(_sequence.physics_tick)
		_vehicle_interaction.process_actions(_sequence.physics_tick)
		if _client.local_input_enabled:
			_sample_and_submit_local_vehicle_input(delta)
		_step_remote_players(delta)
		_vehicle_replicator.step_authority(delta, now_msec, _sequence.physics_tick)
		if _sequence.physics_tick % MOVEMENT_INTERVAL_TICKS == 0:
			_publish_movement()
	else:
		_lifecycle.step(_sequence.physics_tick)
		_update_client_presentation(delta)
		_follow_local_control_display()
		if _client.input_open and _client.local_input_enabled:
			_sample_predict_and_submit_local_input(delta)


## Installs one admitted network identity and starts the appropriate authority role.
func configure_network(
	session_id: String,
	local_participant_id: int,
	is_host: bool,
	clock: Callable = Callable(),
	transport: ReplicationTransport = null,
) -> bool:
	if not _configure_context(session_id, local_participant_id, is_host, clock, transport):
		return false

	if not _context.is_host:
		_store = ReplicaStateStore.new(_codec, _context.session_id, _match_revision())
		if not _lifecycle.configure_replica(local_participant_id):
			return false
		if not _vehicle_replicator.configure_replica(_runtime_entities()):
			return false
		_bind_hud_sources()
		_send_ready.call_deferred()
	else:
		if not _configure_authority(local_participant_id, clock):
			return false

	set_physics_process(true)
	return true


## Starts standalone through the same lifecycle, safe-spawn, and reset ownership.
func configure_standalone(local_participant_id: int = 1, clock: Callable = Callable()) -> bool:
	var session_id: String = ReplicationIdentity.create_session_id()
	if not _configure_context(session_id, local_participant_id, true, clock, null):
		return false

	_standalone = true
	if not _configure_authority(local_participant_id, clock):
		return false
	set_physics_process(true)
	return true


## Captures immutable process identity before any actors or network work begin.
func _configure_context(
	session_id: String,
	local_participant_id: int,
	is_host: bool,
	clock: Callable,
	transport: ReplicationTransport,
) -> bool:
	if (
		_configured
		or not ReplicationIdentity.is_valid_session_id(session_id)
		or local_participant_id <= 0
	):
		return false

	_context.session_id = session_id
	_context.local_participant_id = local_participant_id
	_context.is_host = is_host
	_context.clock = clock
	_configured = true
	_transport = transport if transport != null else SceneReplicationTransport.new(self)
	if _vehicle_replicator == null:
		_vehicle_replicator = VehicleReplicator.new()
	return true


## Registers the one vehicle replication owner before Match network configuration.
func register_vehicle_replicator(replicator: VehicleReplicator) -> bool:
	if _configured or replicator == null or _vehicle_replicator != null:
		return false
	_vehicle_replicator = replicator
	return true


## Configures host-only lifecycle collaborators and creates the retained local player.
func _configure_authority(local_participant_id: int, clock: Callable) -> bool:
	if not _identities.bind_peer(1, local_participant_id).ok:
		return false
	_create_admission(clock)
	if not _lifecycle.configure_authority(
		local_participant_id,
		_city_data().anchor_descriptors(WorldAnchor.KIND_PLAYER_SPAWN),
		_spawn_reservations,
		_is_spawn_blocked,
		_respawn_authoritative_player,
	):
		return false
	_lifecycle.transition.connect(_on_lifecycle_transition)
	var actor: ActorMotion = _spawn_authoritative_player(local_participant_id, true)
	if actor == null or not _local_rig().bind_actor(actor):
		return false
	var tracker: EntityGenerationTracker = _player_identity.tracker
	if not _vehicle_replicator.configure_authority(
		_runtime_entities(),
		_city_data().anchor_descriptors(WorldAnchor.KIND_PARKED_CAR),
		tracker,
	):
		return false
	_vehicle_interaction = VehicleInteraction.new()
	if not _vehicle_interaction.configure(
		_vehicle_replicator,
		actor_for_participant,
		lifecycle_view_for,
		_is_clearance_blocked,
		_match_revision(),
		_input_authority.can_rebind,
		_input_authority.rebind,
	):
		return false
	_input_authority.grant(local_participant_id)
	_vehicle_interaction.action_resolved.connect(_on_vehicle_action_resolved)
	_vehicle_interaction.transaction_committed.connect(_on_vehicle_transaction_committed)
	_bind_hud_sources()
	return true


## Rebuilds revision-scoped admission while retaining Session-owned peer identities.
func _create_admission(clock: Callable) -> void:
	_admission = ReplicationAdmission.new(
		_codec,
		_transport,
		_identities,
		_context.session_id,
		_match_revision(),
	)
	_admission.set_clock(clock)


## Mirrors one Session-owned host mapping before accepting replication requests from it.
func admit_peer(native_peer_id: int, participant_id: int) -> bool:
	if not _configured or not _context.is_host:
		return false
	if not _identities.bind_peer(native_peer_id, participant_id).get("ok", false):
		return false

	_peer_by_participant[participant_id] = native_peer_id
	if not _waiting_admission_deadline_by_peer.has(native_peer_id):
		_waiting_admission_deadline_by_peer[native_peer_id] = (
			_now_msec() + ReplicationAdmission.TOTAL_ATTEMPT_TIMEOUT_MSEC
		)
	return true


## Retires one disconnected mapping, actor, pending input, and admission state.
func remove_peer(native_peer_id: int, participant_id: int) -> void:
	if not _configured or not _context.is_host:
		return

	_admitted_peers.erase(native_peer_id)
	_peer_by_participant.erase(participant_id)
	_waiting_admission_deadline_by_peer.erase(native_peer_id)
	_input_authority.remove(participant_id)
	if _vehicle_interaction != null:
		_vehicle_interaction.release_for_lifecycle(participant_id, &"DISCONNECT")
	_input_state_by_participant.erase(participant_id)
	_player_identity.spawn_slot_by_participant.erase(participant_id)
	_admission.remove_peer(native_peer_id)
	var actor: ActorMotion = _actors_by_participant.get(participant_id)
	var bindings: Dictionary = _player_identity.binding_by_participant
	if actor == null and not bindings.has(participant_id):
		return
	if actor != null:
		_actors_by_participant.erase(participant_id)
		actor.queue_free()
	_sequence.durable_revision += 1
	_admission.publish_durable(
		_durable_event(2, PHASE_REMOVED, participant_id, _sequence.durable_revision)
	)
	_lifecycle.remove_player(participant_id)
	_retire_player_binding(participant_id)
	_admission.publish_lifecycle(_lifecycle.revision())
	_publish_lifecycle_state()


## Allows deterministic integration drivers to replace desktop collection, not authority.
func set_local_input_enabled(enabled: bool) -> void:
	_client.local_input_enabled = enabled
	if not enabled:
		var input: DesktopFootInput = _local_input()
		if input != null:
			input.set_focused(false)
	_local_rig().set_vehicle_input_enabled(enabled)


## Encodes and sends one envelope-fenced local intent without applying prediction.
func submit_local_command(command: FootCommand) -> bool:
	var encoded: Dictionary = _encode_local_command(command)
	if not encoded.get("ok", false):
		return false
	_send_local_command_packet(encoded.packet)
	return true


## Validates wire admission before atomically predicting and sending the same packet.
func predict_and_submit_local_command(command: FootCommand, delta_seconds: float) -> bool:
	var encoded: Dictionary = _encode_local_command(command)
	if not encoded.get("ok", false):
		return false
	if not _prediction_owner().predict(command, delta_seconds):
		return false

	_send_local_command_packet(encoded.packet)
	return true


## Predicts and submits one local drive command through the current vehicle EntityRef fence.
func predict_and_submit_local_vehicle_command(
	command: DriveCommand,
	delta_seconds: float,
) -> bool:
	if _context.is_host or not _client.input_open:
		return false
	var binding: Dictionary = _vehicle_replicator.binding_for_participant(
		_context.local_participant_id
	)
	if binding.is_empty():
		return false
	var encoded: Dictionary = DriveCommandCodec.encode(command, int(binding.input_epoch))
	if not encoded.get("ok", false):
		return false
	if not _vehicle_replicator.predict_local(command, delta_seconds):
		return false
	_submit_vehicle_command.rpc_id(
		1,
		{
			"session_id": _context.session_id,
			"match_revision": _match_revision(),
			"entity_id": binding.id,
			"generation": binding.generation,
			"packet": encoded.packet,
		},
	)
	return true


## Validates and queues one listen-server drive command through the authoritative queue.
func submit_host_local_vehicle_command(command: DriveCommand) -> bool:
	if not _configured or not _context.is_host:
		return false
	var participant_id: int = int(_context.local_participant_id)
	var binding: Dictionary = _vehicle_replicator.binding_for_participant(participant_id)
	if binding.is_empty() or not _lifecycle.is_alive(participant_id):
		return false
	var encoded: Dictionary = DriveCommandCodec.encode(command, int(binding.input_epoch))
	if not encoded.get("ok", false):
		return false
	var decoded: Dictionary = DriveCommandCodec.decode(encoded.packet)
	if not decoded.get("ok", false):
		return false
	return _vehicle_replicator.offer_command(
		participant_id, decoded, _now_msec()
	).get("accepted", false)


## Queues one authoritative entry request for deterministic accepted-tick resolution.
func request_vehicle_entry(
	participant_id: int,
	entity_id: int,
	action_sequence: int,
	accepted_tick: int = -1,
) -> Dictionary:
	if not _configured or not _context.is_host or _vehicle_interaction == null:
		return { "ok": false, "failure": &"NOT_AUTHORITY" }
	var player_ref: Dictionary = _lifecycle.entity_ref_for(participant_id)
	var descriptor: Dictionary = _vehicle_replicator.descriptor_for_entity(entity_id)
	if player_ref.is_empty() or descriptor.is_empty():
		return { "ok": false, "failure": &"STALE_ACTION_CONTEXT" }
	return _vehicle_interaction.enqueue_action(
		{
			"participant_id": participant_id,
			"player_ref": player_ref,
			"vehicle_ref": {
				"id": entity_id,
				"generation": int(descriptor.generation),
			},
			"match_revision": _match_revision(),
			"accepted_tick": (
				_sequence.physics_tick + VEHICLE_ENTRY_PRESENTATION_TICKS
				if accepted_tick < 0
				else accepted_tick
			),
			"action_sequence": action_sequence,
			"kind": VehicleInteraction.ACTION_ENTER,
		}
	)


## Queues one authoritative exit request through the same reliable action sequence.
func request_vehicle_exit(
	participant_id: int,
	action_sequence: int,
	accepted_tick: int = -1,
) -> Dictionary:
	if not _configured or not _context.is_host or _vehicle_interaction == null:
		return { "ok": false, "failure": &"NOT_AUTHORITY" }
	var player_ref: Dictionary = _lifecycle.entity_ref_for(participant_id)
	if player_ref.is_empty():
		return { "ok": false, "failure": &"STALE_ACTION_CONTEXT" }
	return _vehicle_interaction.enqueue_action(
		{
			"participant_id": participant_id,
			"player_ref": player_ref,
			"match_revision": _match_revision(),
			"accepted_tick": (
				_sequence.physics_tick + 1 if accepted_tick < 0 else accepted_tick
			),
			"action_sequence": action_sequence,
			"kind": VehicleInteraction.ACTION_EXIT,
		}
	)


## Sends one local host-confirmed entry intent and starts only its door presentation.
func request_local_vehicle_entry(entity_id: int, action_sequence: int) -> bool:
	if not _configured or action_sequence <= 0:
		return false
	var vehicle: VehicleMotion = _vehicle_replicator.vehicle_for_entity(entity_id)
	var actor: ActorMotion = actor_for_participant(_context.local_participant_id)
	if vehicle == null or actor == null:
		return false
	vehicle.play_entry_presentation(actor.global_position)
	if _context.is_host:
		return request_vehicle_entry(
			_context.local_participant_id, entity_id, action_sequence
		).get("ok", false)
	var player_ref: Dictionary = _lifecycle.entity_ref_for(_context.local_participant_id)
	var descriptor: Dictionary = _vehicle_replicator.descriptor_for_entity(entity_id)
	if player_ref.is_empty() or descriptor.is_empty():
		return false
	_request_vehicle_action.rpc_id(
		1,
		_build_vehicle_action_envelope(
			VehicleInteraction.ACTION_ENTER,
			action_sequence,
			player_ref,
			{
				"id": entity_id,
				"generation": int(descriptor.generation),
			},
		),
	)
	return true


## Sends one local exit intent without changing camera or control before acceptance.
func request_local_vehicle_exit(action_sequence: int) -> bool:
	if not _configured or action_sequence <= 0:
		return false
	if _context.is_host:
		return request_vehicle_exit(
			_context.local_participant_id, action_sequence
		).get("ok", false)
	var player_ref: Dictionary = _lifecycle.entity_ref_for(_context.local_participant_id)
	if player_ref.is_empty():
		return false
	_request_vehicle_action.rpc_id(
		1,
		_build_vehicle_action_envelope(
			VehicleInteraction.ACTION_EXIT,
			action_sequence,
			player_ref,
			{},
		),
	)
	return true


## Returns one current replicated vehicle body for focused acceptance drivers.
func vehicle_for_entity(entity_id: int) -> VehicleMotion:
	return _vehicle_replicator.vehicle_for_entity(entity_id)


## Returns bounded local car replay and correction diagnostics.
func vehicle_prediction_diagnostics() -> Dictionary:
	return _vehicle_replicator.prediction_diagnostics()


## Sends one exact pre-encoded command packet for alternate bounded input collectors.
func send_local_command_packet(packet: PackedByteArray) -> bool:
	if not _can_submit_local_packet(packet):
		return false
	_send_local_command_packet(packet)
	return true


## Builds one fixed packet only while the local lifecycle binding and epoch are current.
func _encode_local_command(command: FootCommand) -> Dictionary:
	if not _can_submit_local_packet(PackedByteArray()):
		return { "ok": false }
	return FootCommandCodec.encode(command, int(_client.input_epoch))


## Checks local state before prediction can mutate movement.
func _can_submit_local_packet(packet: PackedByteArray) -> bool:
	if (
		_context.is_host
		or not _client.input_open
		or _client.input_recovery_pending
		or not _vehicle_replicator.binding_for_participant(
			_context.local_participant_id
		).is_empty()
	):
		return false
	if not packet.is_empty() and packet.size() != FootCommandCodec.PACKET_BYTES:
		return false
	return not _player_identity.binding_by_participant.get(
		_context.local_participant_id, {}
	).is_empty()


## Sends one fixed packet through A2.4's current session, match, and EntityRef fence.
func _send_local_command_packet(packet: PackedByteArray) -> void:
	_client.last_command_packet = packet.duplicate()
	_submit_command.rpc_id(1, _command_envelope(packet))


## Wraps one packet in the sole lifecycle-owned command fence.
func _command_envelope(packet: PackedByteArray) -> Dictionary:
	var binding: Dictionary = _player_identity.binding_by_participant[
		_context.local_participant_id
	]
	return {
		"session_id": _context.session_id,
		"match_revision": _match_revision(),
		"entity_id": int(binding.id),
		"generation": int(binding.generation),
		"packet": packet,
	}


## Invalidates replay at life, generation, reset, control, or collision fences.
func update_client_prediction_context(
	entity_id: int,
	generation: int,
	life_revision: int,
	control_revision: int,
	collision_revision: int,
) -> bool:
	return _prediction_owner().update_context(
		entity_id, generation, life_revision, control_revision, collision_revision
	)


## Clears prediction, smoothing, and pending recovery at a non-incremental fence.
func invalidate_client_motion() -> void:
	_prediction_owner().invalidate()
	_vehicle_replicator.invalidate_motion()
	_client.input_recovery_pending = false
	_client.last_command_packet = PackedByteArray()
	for smoother: RemoteMotionSmoother in _remote_smoothers().values():
		smoother.clear()


## Returns one process-local actor for wiring checks and integration receipts.
func actor_for_participant(participant_id: int) -> ActorMotion:
	return _actors_by_participant.get(participant_id)


## Reports the number of complete player bodies currently materialized in Match.
func player_count() -> int:
	return _actors_by_participant.size()


## Reports a bounded command-boundary diagnostic count without exposing mutable state.
func command_rejection_count(code: StringName) -> int:
	var counts: Dictionary = _context.command_rejections
	return counts.get(code, 0)


## Exposes the read-only local lifecycle and authoritative roster presentation snapshot.
func lifecycle_view() -> Dictionary:
	return _lifecycle.view()


## Returns one immutable authoritative or hydrated participant lifecycle row.
func lifecycle_view_for(participant_id: int) -> Dictionary:
	return _lifecycle.player_view(participant_id)


## Reports the current match fence for reset and real-process acceptance checks.
func match_revision() -> int:
	return _match_revision()


## Dev/test-only lethal trigger standing in for the future Health owner callback.
func trigger_test_death(participant_id: int) -> bool:
	if not _configured or not _context.is_host or not OS.is_debug_build():
		return false
	return _commit_player_death(participant_id)


## Resets host/standalone state while retaining every admitted Session participant.
func request_match_reset(requester_participant_id: int) -> bool:
	if (
		not _configured
		or not _context.is_host
		or _resetting
		or requester_participant_id != int(_context.local_participant_id)
	):
		return false

	_resetting = true
	var now_msec: int = _now_msec()
	var reset_attempts: Array[Dictionary] = _take_reset_attempts(now_msec)
	_sequence.match_revision = _match_revision() + 1
	_sequence.durable_revision = 0
	_input_authority.clear()
	_vehicle_interaction.reset(_match_revision())
	_input_state_by_participant.clear()
	_admitted_peers.clear()
	var failed_peers: Array[int] = []
	for attempt: Dictionary in reset_attempts:
		var native_peer_id: int = int(attempt.native_peer_id)
		if not _transport.send_reset_begin(native_peer_id, _match_revision()):
			failed_peers.append(native_peer_id)
	for actor: ActorMotion in _actors_by_participant.values():
		actor.neutralize()
	_apply_dead_to_all_actors()
	_create_admission(_context.clock)
	var reset_result: Dictionary = _lifecycle.reset_players(_sequence.physics_tick)
	_apply_lifecycle_to_actors()
	failed_peers = _restart_reset_attempts(reset_attempts, failed_peers, now_msec)
	_resetting = false
	return reset_result.get("ok", false) and failed_peers.is_empty()


## Inventories active and mapped waiting peers without extending pending join deadlines.
func _take_reset_attempts(now_msec: int) -> Array[Dictionary]:
	var attempts: Array[Dictionary] = _admission.take_reset_attempts()
	var included_peers: Dictionary[int, bool] = {}
	for attempt: Dictionary in attempts:
		included_peers[int(attempt.native_peer_id)] = true
	for participant_id: int in _peer_by_participant:
		var native_peer_id: int = int(_peer_by_participant[participant_id])
		if included_peers.has(native_peer_id):
			continue
		var default_deadline: int = now_msec + ReplicationAdmission.TOTAL_ATTEMPT_TIMEOUT_MSEC
		var deadline_msec: int = int(
			_waiting_admission_deadline_by_peer.get(native_peer_id, default_deadline)
		)
		attempts.append(
			{
				"native_peer_id": native_peer_id,
				"participant_id": participant_id,
				"phase": PHASE_MAPPED,
				"attempt_deadline_msec": deadline_msec,
			}
		)
	return attempts


## Restarts reset-interrupted transfers while retaining mapped peers until readiness.
func _restart_reset_attempts(
	attempts: Array[Dictionary],
	failed_peers: Array[int],
	now_msec: int,
) -> Array[int]:
	for attempt: Dictionary in attempts:
		var native_peer_id: int = int(attempt.native_peer_id)
		if native_peer_id in failed_peers:
			abort_peer(native_peer_id, &"RESET_FAILED")
			continue
		if attempt.phase == PHASE_MAPPED:
			_waiting_admission_deadline_by_peer[native_peer_id] = int(
				attempt.attempt_deadline_msec
			)
			continue
		var deadline_msec: int = (
			int(attempt.attempt_deadline_msec)
			if attempt.phase != ReplicationAdmission.PHASE_ADMITTED
			else now_msec + RESET_ADMISSION_TIMEOUT_MSEC
		)
		var restarted: Dictionary = begin_admission_for_peer(native_peer_id, deadline_msec)
		if not restarted.get("ok", false):
			failed_peers.append(native_peer_id)
			abort_peer(native_peer_id, &"RESET_FAILED")
	return failed_peers


## Sends client readiness only after the saved Match RPC path exists locally.
func _send_ready() -> void:
	if not _configured or _context.is_host or multiplayer.multiplayer_peer == null:
		return

	_ready_for_baseline.rpc_id(1, _context.session_id, _match_revision())


## Starts baseline admission only for the sender identity supplied by SessionService.
@rpc("any_peer", "call_remote", "reliable", 0)
func _ready_for_baseline(session_id: String, match_revision: int) -> void:
	if not _context.is_host or session_id != _context.session_id:
		return
	var native_peer_id: int = multiplayer.get_remote_sender_id()
	if match_revision != _match_revision():
		if (
			_identities.resolve_sender(native_peer_id) > 0
			and _waiting_admission_deadline_by_peer.has(native_peer_id)
		):
			_transport.send_reset_begin(native_peer_id, _match_revision())
		return

	begin_admission_for_peer(native_peer_id)


## Starts one sender-derived admission after Session has installed its mapping.
func begin_admission_for_peer(  # gdstyle:ignore=quality/max-branches
	native_peer_id: int,
	preserved_attempt_deadline_msec: int = -1,
) -> Dictionary:
	if not _configured or not _context.is_host:
		return { "ok": false }
	var participant_id: int = _identities.resolve_sender(native_peer_id)
	if participant_id == 0:
		return { "ok": false }
	var attempt_deadline_msec: int = preserved_attempt_deadline_msec
	if attempt_deadline_msec < 0:
		attempt_deadline_msec = int(
			_waiting_admission_deadline_by_peer.get(native_peer_id, -1)
		)
	if attempt_deadline_msec >= 0 and attempt_deadline_msec <= _now_msec():
		abort_peer(native_peer_id, &"SYNC_TIMEOUT")
		return { "ok": false, "failure": { "code": &"SYNC_TIMEOUT" } }
	var retained_player: bool = _actors_by_participant.has(participant_id)
	if not retained_player:
		if _spawn_authoritative_player(participant_id, false) == null:
			abort_peer(native_peer_id, &"SPAWN_FAILED")
			return { "ok": false }
		_broadcast_bindings()
		_sequence.durable_revision += 1
		_admission.publish_durable(
			_durable_event(1, PHASE_LIVE, participant_id, _sequence.durable_revision)
		)
		_publish_lifecycle_state()
	elif not _vehicle_replicator.binding_for_participant(participant_id).is_empty():
		var rebound: Dictionary = _vehicle_interaction.rebind_commands(participant_id)
		if not rebound.get("ok", false):
			abort_peer(native_peer_id, &"CONTROL_REVISION_EXHAUSTED")
			return rebound

	_sequence.baseline_id += 1
	var options: Dictionary = { "lifecycle_revision": _lifecycle.revision() }
	if attempt_deadline_msec >= 0:
		options.attempt_deadline_msec = attempt_deadline_msec
	var started: Dictionary = _admission.start(
		native_peer_id,
		_sequence.baseline_id,
		_sequence.physics_tick,
		_capture_rows(),
		options,
	)
	started["baseline_id"] = _sequence.baseline_id
	if started.get("ok", false):
		_waiting_admission_deadline_by_peer.erase(native_peer_id)
	return started


## Advances one current peer from baseline transfer to reliable handoff.
func acknowledge_baseline_for_peer(native_peer_id: int, baseline_id: int) -> Dictionary:
	return _admission.acknowledge_baseline(native_peer_id, baseline_id)


## Opens one current peer only after its matching reliable handoff marker.
func acknowledge_handoff_for_peer(
	native_peer_id: int,
	baseline_id: int,
	commit_revision: int,
	lifecycle_revision: int,
) -> Dictionary:
	var result: Dictionary = _admission.acknowledge_handoff(
		native_peer_id,
		baseline_id,
		commit_revision,
		lifecycle_revision,
	)
	if result.get("admitted", false):
		var participant_id: int = _identities.resolve_sender(native_peer_id)
		_admitted_peers[native_peer_id] = true
		_waiting_admission_deadline_by_peer.erase(native_peer_id)
		_input_authority.grant(participant_id)
		_lifecycle.set_admitted(participant_id, true)
	return result


## Reports command admission for deterministic runtime lifecycle checks.
func admitted_participant(native_peer_id: int) -> int:
	return _admission.input_participant(native_peer_id)


## Accepts a baseline acknowledgement only from its native RPC sender.
@rpc("any_peer", "call_remote", "reliable", 0)
func _acknowledge_baseline(
	session_id: String,
	match_revision: int,
	baseline_id: int,
) -> void:
	if (
		_context.is_host
		and session_id == _context.session_id
		and match_revision == _match_revision()
	):
		acknowledge_baseline_for_peer(multiplayer.get_remote_sender_id(), baseline_id)


## Accepts a handoff acknowledgement only from its native RPC sender.
@rpc("any_peer", "call_remote", "reliable", 0)
func _acknowledge_handoff(
	session_id: String,
	match_revision: int,
	baseline_id: int,
	commit_revision: int,
	lifecycle_revision: int,
) -> void:
	if (
		_context.is_host
		and session_id == _context.session_id
		and match_revision == _match_revision()
	):
		acknowledge_handoff_for_peer(
			multiplayer.get_remote_sender_id(),
			baseline_id,
			commit_revision,
			lifecycle_revision,
		)


## Requests one bounded epoch transition through the same lifecycle-owned command fence.
@rpc("any_peer", "call_remote", "reliable", 0)
func _request_input_recovery(envelope: Dictionary) -> void:
	var admitted: Dictionary = _admit_input(envelope)
	if admitted.is_empty():
		return
	var decoded: Dictionary = FootCommandCodec.decode(admitted.packet)
	if not decoded.get("ok", false):
		return
	var next_epoch: int = _input_authority.recover(
		int(admitted.participant_id),
		int(decoded.input_epoch),
		admitted.packet,
		_now_msec(),
	)
	if next_epoch <= 0:
		return
	var binding: Dictionary = admitted.binding
	_receive_input_recovery.rpc_id(
		int(admitted.sender),
		{
			"session_id": _context.session_id,
			"match_revision": _match_revision(),
			"entity_id": int(binding.id),
			"generation": int(binding.generation),
			"input_epoch": next_epoch,
		},
	)


## Installs one host-authorized epoch only while its complete lifecycle fence is current.
@rpc("authority", "call_remote", "reliable", 0)
func _receive_input_recovery(envelope: Dictionary) -> void:
	if _context.is_host or not _client.input_recovery_pending or envelope.size() != 5:
		return
	var binding: Dictionary = _player_identity.binding_by_participant.get(
		_context.local_participant_id, {}
	)
	if (
		binding.is_empty()
		or envelope.get("session_id") != _context.session_id
		or envelope.get("match_revision") != _match_revision()
		or envelope.get("entity_id") != int(binding.id)
		or envelope.get("generation") != int(binding.generation)
		or envelope.get("input_epoch") is not int
	):
		return
	var input_epoch: int = int(envelope.input_epoch)
	if input_epoch <= int(_client.input_epoch) or input_epoch > FootCommandCodec.MAX_INPUT_EPOCH:
		return
	_client.input_epoch = input_epoch
	_client.input_recovery_pending = false
	_client.last_command_packet = PackedByteArray()
	_reset_local_command_sequence()
	_prediction_owner().invalidate()
	_update_local_prediction_context()
	input_recovered.emit(_context.local_participant_id)


## Validates the command envelope before offering its fixed packet to host input state.
@rpc("any_peer", "call_remote", "unreliable_ordered", 2)
func _submit_command(envelope: Dictionary) -> void:
	var admitted: Dictionary = _admit_input(envelope)
	if admitted.is_empty() or not _consume_input_rate(int(admitted.participant_id)):
		return
	var decoded: Dictionary = FootCommandCodec.decode(admitted.packet)
	if not decoded.get("ok", false):
		_record_command_rejection(decoded.failure.code)
		return
	var offered: Dictionary = _input_authority.offer(
		int(admitted.participant_id), decoded, _now_msec()
	)
	if offered.has("failure"):
		_record_command_rejection(offered.failure)


## Accepts one exact sender-derived vehicle action onto the reliable control stream.
@rpc("any_peer", "call_remote", "reliable", 0)
# Exact boundary validation intentionally rejects before each kind-specific field use.
# gdstyle:ignore=quality/max-function-length,quality/max-returns,quality/max-branches
func _request_vehicle_action(envelope: Dictionary) -> void:
	if (
		not _context.is_host
		or envelope.size() not in [6, 7]
		or var_to_bytes(envelope).size() > MAX_VEHICLE_ACTION_ENVELOPE_BYTES
	):
		return
	if (
		envelope.get("session_id") is not String
		or envelope.get("match_revision") is not int
		or envelope.get("player_id") is not int
		or envelope.get("player_generation") is not int
		or envelope.get("action_sequence") is not int
		or (envelope.get("kind") is not String and envelope.get("kind") is not StringName)
		or envelope.session_id != _context.session_id
		or int(envelope.match_revision) != _match_revision()
	):
		return
	var sender: int = multiplayer.get_remote_sender_id()
	var participant_id: int = _admission.input_participant(sender)
	var player_ref: Dictionary = _lifecycle.entity_ref_for(participant_id)
	if (
		participant_id == 0
		or int(player_ref.get("id", 0)) != int(envelope.player_id)
		or int(player_ref.get("generation", 0)) != int(envelope.player_generation)
	):
		return
	var kind := StringName(envelope.kind)
	var queued: Dictionary
	if kind == VehicleInteraction.ACTION_ENTER and envelope.size() == 7:
		if envelope.get("vehicle_ref") is not Dictionary:
			return
		var vehicle_ref: Dictionary = envelope.vehicle_ref
		if not ReplicationIdentity.is_valid_entity_ref(vehicle_ref):
			return
		var descriptor: Dictionary = _vehicle_replicator.descriptor_for_entity(
			int(vehicle_ref.id)
		)
		if int(descriptor.get("generation", 0)) != int(vehicle_ref.generation):
			return
		queued = request_vehicle_entry(
			participant_id,
			int(vehicle_ref.id),
			int(envelope.action_sequence),
		)
	elif kind == VehicleInteraction.ACTION_EXIT and envelope.size() == 6:
		queued = request_vehicle_exit(participant_id, int(envelope.action_sequence))
	else:
		return
	if queued.get("cached_result") is Dictionary:
		_send_vehicle_action_result(sender, participant_id, queued.cached_result)
		return
	if not queued.get("ok", false):
		_send_vehicle_action_result(sender, participant_id, {
			"action_sequence": int(envelope.action_sequence),
			"status": VehicleInteraction.STATUS_REJECTED,
			"failure": queued.get("failure", &"ACTION_REJECTED"),
		})


## Installs one bounded action result without deriving control from the result itself.
@rpc("authority", "call_remote", "reliable", 0)
func _receive_vehicle_action_result(envelope: Dictionary) -> void:
	if (
		_context.is_host
		or envelope.size() != 4
		or envelope.get("session_id") != _context.session_id
		or envelope.get("match_revision") != _match_revision()
		or envelope.get("participant_id") != _context.local_participant_id
		or envelope.get("result") is not Dictionary
	):
		return
	var result: Dictionary = envelope.result
	if (
		result.get("action_sequence") is not int
		or result.get("status") not in [
			VehicleInteraction.STATUS_APPLIED,
			VehicleInteraction.STATUS_REJECTED,
		]
	):
		return
	vehicle_action_resolved.emit(result.duplicate(true))


## Validates and queues one sender-owned vehicle packet on the held-input stream.
@rpc("any_peer", "call_remote", "unreliable_ordered", 2)
func _submit_vehicle_command(envelope: Dictionary) -> void:
	if (
		envelope.size() != 5
		or envelope.get("session_id") is not String
		or envelope.get("match_revision") is not int
		or envelope.get("entity_id") is not int
		or envelope.get("generation") is not int
		or envelope.get("packet") is not PackedByteArray
	):
		return
	if (
		not _context.is_host
		or envelope.session_id != _context.session_id
		or int(envelope.match_revision) != _match_revision()
	):
		return
	var packet: PackedByteArray = envelope.packet
	if packet.size() != DriveCommandCodec.PACKET_BYTES:
		_record_command_rejection(&"PACKET_SIZE")
		return
	var sender: int = multiplayer.get_remote_sender_id()
	var participant_id: int = _admission.input_participant(sender)
	var binding: Dictionary = _vehicle_replicator.binding_for_participant(participant_id)
	if (
		participant_id == 0
		or binding.is_empty()
		or int(envelope.entity_id) != int(binding.id)
		or int(envelope.generation) != int(binding.generation)
		or not _consume_input_rate(participant_id)
	):
		return
	var decoded: Dictionary = DriveCommandCodec.decode(packet)
	if not decoded.get("ok", false):
		_record_command_rejection(decoded.failure.code)
		return
	var offered: Dictionary = _vehicle_replicator.offer_command(
		participant_id, decoded, _now_msec()
	)
	if offered.has("failure"):
		_record_command_rejection(offered.failure)


## Resolves one exact current command envelope without decoding its bounded packet.
func _admit_input(envelope: Dictionary) -> Dictionary:  # gdstyle:ignore=quality/max-returns
	if (
		envelope.size() != 5
		or envelope.get("session_id") is not String
		or envelope.get("match_revision") is not int
		or envelope.get("entity_id") is not int
		or envelope.get("generation") is not int
		or envelope.get("packet") is not PackedByteArray
	):
		return {}
	if (
		not _context.is_host
		or envelope.session_id != _context.session_id
		or int(envelope.match_revision) != _match_revision()
	):
		return {}
	var packet: PackedByteArray = envelope.packet
	if packet.size() != FootCommandCodec.PACKET_BYTES:
		_record_command_rejection(&"PACKET_SIZE")
		return {}
	var sender: int = multiplayer.get_remote_sender_id()
	var participant_id: int = _admission.input_participant(sender)
	var binding: Dictionary = _player_identity.binding_by_participant.get(participant_id, {})
	if (
		participant_id == 0
		or not _lifecycle.is_alive(participant_id)
		or not _vehicle_replicator.binding_for_participant(participant_id).is_empty()
		or binding.is_empty()
		or int(envelope.entity_id) != int(binding.id)
		or int(envelope.generation) != int(binding.generation)
	):
		return {}
	return {
		"binding": binding,
		"packet": packet,
		"participant_id": participant_id,
		"sender": sender,
	}


## Installs reliable vehicle definitions and test control bindings before movement.
@rpc("authority", "call_remote", "reliable", 1)
func _receive_vehicle_descriptors(
	session_id: String,
	match_revision: int,
	descriptors: Array,
	transfers: Array,
) -> void:
	if (
		_context.is_host
		or session_id != _context.session_id
		or match_revision != _match_revision()
	):
		return
	if not _install_vehicle_transfer_rows(transfers):
		return
	var previous_binding: Dictionary = _vehicle_replicator.binding_for_participant(
		_context.local_participant_id
	)
	if _vehicle_replicator.install_descriptors(
		descriptors, _context.local_participant_id
	):
		var current_binding: Dictionary = _vehicle_replicator.binding_for_participant(
			_context.local_participant_id
		)
		if int(current_binding.get("control_revision", 0)) != int(
			previous_binding.get("control_revision", 0)
		):
			_local_rig().reset_vehicle_command_sequence()
		_sync_vehicle_occupancy_presentation()


## Installs exact transfer poses and fresh foot epochs before occupancy can reopen input.


# gdstyle:ignore=quality/max-returns,quality/max-function-length
func _install_vehicle_transfer_rows(
	transfers: Array,
) -> bool:
	if transfers.size() > PeerIdentityRegistry.MAX_PARTICIPANTS:
		return false
	for value: Variant in transfers:
		if value is not Dictionary:
			return false
		var row: Dictionary = value
		if (
			row.size() != 10
			or row.get("participant_id") is not int
			or row.get("player_id") is not int
			or row.get("generation") is not int
			or row.get("seated") is not bool
			or row.get("foot_input_epoch") is not int
			or row.get("x") is not float
			or row.get("y") is not float
			or row.get("z") is not float
			or row.get("yaw") is not float
			or row.get("transaction_revision") is not int
		):
			return false
		var participant_id: int = int(row.participant_id)
		var revision: int = int(row.transaction_revision)
		var revisions: Dictionary = _client.vehicle_transfer_revision_by_participant
		if participant_id <= 0 or revision < int(revisions.get(participant_id, -1)):
			continue
		revisions[participant_id] = revision
		var actor: ActorMotion = _actors_by_participant.get(participant_id)
		if actor != null:
			var ref: Dictionary = _lifecycle.entity_ref_for(participant_id)
			if (
				int(ref.get("id", 0)) == int(row.player_id)
				and int(ref.get("generation", 0)) == int(row.generation)
			):
				actor.global_position = Vector3(row.x, row.y, row.z)
				actor.rotation.y = float(row.yaw)
				actor.neutralize()
		if participant_id != int(_context.local_participant_id):
			continue
		var foot_input_epoch: int = int(row.foot_input_epoch)
		if (
			foot_input_epoch <= 0
			or foot_input_epoch > FootCommandCodec.MAX_INPUT_EPOCH
			or foot_input_epoch == int(_client.input_epoch)
		):
			continue
		_client.input_epoch = foot_input_epoch
		invalidate_client_motion()
		_reset_local_command_sequence()
	return true


## Installs Session-to-entity bindings before baseline or lifecycle rows reference them.
@rpc("authority", "call_remote", "reliable", 1)
func _receive_player_bindings(
	session_id: String,
	match_revision: int,
	bindings: Array,
) -> void:
	if (
		_context.is_host
		or session_id != _context.session_id
		or match_revision != _match_revision()
	):
		return
	if bindings.size() > PeerIdentityRegistry.MAX_PARTICIPANTS:
		return

	for value: Variant in bindings:
		if value is not Dictionary:
			return
		var binding: Dictionary = value
		if (
			binding.size() != 3
			or not binding.has("participant_id")
			or binding.participant_id is not int
			or int(binding.participant_id) <= 0
			or not ReplicationIdentity.has_valid_entity_ref_fields(binding)
		):
			return
	for value: Variant in bindings:
		var binding: Dictionary = value
		var participant_id: int = int(binding.participant_id)
		var previous: Dictionary = _player_identity.binding_by_participant.get(
			participant_id, {}
		)
		_player_identity.binding_by_participant[participant_id] = binding.duplicate()
		_player_identity.participant_by_entity[int(binding.id)] = participant_id
		if participant_id == _context.local_participant_id and (
			previous.is_empty()
			or int(previous.id) != int(binding.id)
			or int(previous.generation) != int(binding.generation)
		):
			_client.input_epoch = 1
			_client.input_recovery_pending = false
			_client.last_command_packet = PackedByteArray()
			_reset_local_command_sequence()
	_update_motion_contexts()


## Installs reliable lifecycle and authoritative roster state before baseline movement.
@rpc("authority", "call_remote", "reliable", 1)
func _receive_lifecycle_hydration(
	session_id: String,
	match_revision: int,
	revision: int,
	rows: Array,
) -> void:
	if (
		_context.is_host
		or session_id != _context.session_id
		or match_revision != _match_revision()
	):
		return
	var applied: bool = _lifecycle.apply_replica_rows(
		match_revision,
		revision,
		rows,
		_sequence.physics_tick,
	)
	if not applied:
		return

	_apply_lifecycle_to_actors()
	_update_motion_contexts()


## Invalidates old-match input, state, and callbacks before reset hydration begins.
@rpc("authority", "call_remote", "reliable", 1)
func _receive_reset_begin(session_id: String, match_revision: int) -> void:
	if (
		_context.is_host
		or session_id != _context.session_id
		or match_revision != _match_revision() + 1
	):
		return

	_sequence.match_revision = match_revision
	_client.baseline_installed = false
	_client.grant_received = false
	_client.input_open = false
	_client.input_epoch = 1
	invalidate_client_motion()
	_reset_local_command_sequence()
	_input_state_by_participant.clear()
	(_client.vehicle_transfer_revision_by_participant as Dictionary).clear()
	_player_identity.binding_by_participant.clear()
	_player_identity.participant_by_entity.clear()
	_replica_pose_generation_by_participant.clear()
	_store = ReplicaStateStore.new(_codec, _context.session_id, _match_revision())
	_apply_dead_to_all_actors()
	_local_rig().set_replica_input_enabled(false)
	call_deferred("_send_ready")


## Begins one bounded client baseline transaction from the authoritative host.
@rpc("authority", "call_remote", "reliable", 1)
func _receive_baseline_metadata(metadata: Dictionary) -> void:
	if (
		_context.is_host
		or _store == null
		or not _assembler.begin(_codec, metadata).get("ok", false)
	):
		return

	_sequence.baseline_id = int(metadata.baseline_id)


## Installs complete baseline rows before acknowledging or enabling local input.
@rpc("authority", "call_remote", "reliable", 1)
func _receive_baseline_chunk(packet: PackedByteArray) -> void:
	if _context.is_host or _sequence.baseline_id <= 0:
		return
	var received: Dictionary = _assembler.receive(
		_context.session_id, _match_revision(), _sequence.baseline_id, packet
	)
	if not received.get("ok", false) or not received.get("complete", false):
		return

	var baseline: Dictionary = _assembler.finish()
	if (
		not baseline.get("ok", false)
		or int(baseline.cut_lifecycle_revision) != _lifecycle.revision()
		or not _store.install_baseline(baseline).get("ok", false)
	):
		return
	_client.baseline_installed = true
	_materialize_baseline(baseline.rows)
	_acknowledge_baseline.rpc_id(
		1,
		_context.session_id,
		_match_revision(),
		_sequence.baseline_id,
	)


## Applies one reliable lifecycle transition before any dependent movement row.
@rpc("authority", "call_remote", "reliable", 1)
func _receive_durable(
	session_id: String,
	match_revision: int,
	packet: PackedByteArray,
) -> void:
	if (
		_context.is_host
		or not _client.baseline_installed
		or session_id != _context.session_id
		or match_revision != _match_revision()
	):
		return
	var decoded: Dictionary = _codec.decode_durable(packet)
	if not decoded.get("ok", false):
		return
	if not _store.apply_durable(session_id, match_revision, packet).get("ok", false):
		return
	var participant_id: int = int(
		_player_identity.participant_by_entity.get(int(decoded.id), 0)
	)
	if int(decoded.phase) == PHASE_REMOVED:
		_remove_replica(participant_id)
	elif int(decoded.phase) == 2:
		_set_actor_alive(participant_id, false)


## Acknowledges a reliable handoff marker only after all prior durable records applied.
@rpc("authority", "call_remote", "reliable", 1)
func _receive_handoff(
	session_id: String,
	match_revision: int,
	baseline_id: int,
	commit_revision: int,
	lifecycle_revision: int,
) -> void:
	if (
		_context.is_host
		or session_id != _context.session_id
		or match_revision != _match_revision()
		or not _client.baseline_installed
		or baseline_id != _sequence.baseline_id
		or _store.durable_revision() != commit_revision
		or _lifecycle.revision() != lifecycle_revision
	):
		return

	_acknowledge_handoff.rpc_id(
		1,
		_context.session_id,
		_match_revision(),
		baseline_id,
		commit_revision,
		lifecycle_revision,
	)


## Opens client intent only after baseline and reliable handoff completion.
@rpc("authority", "call_remote", "reliable", 1)
func _receive_grant(
	session_id: String,
	match_revision: int,
	baseline_id: int,
	commit_revision: int,
	lifecycle_revision: int,
) -> void:
	if (
		_context.is_host
		or session_id != _context.session_id
		or match_revision != _match_revision()
		or not _client.baseline_installed
		or baseline_id != _sequence.baseline_id
		or _store.durable_revision() != commit_revision
		or _lifecycle.revision() != lifecycle_revision
	):
		return

	_client.grant_received = true
	_client.input_open = (
		_lifecycle.is_alive(_context.local_participant_id)
		and _replica_has_current_pose(_context.local_participant_id)
	)
	_bind_client_input()
	input_granted.emit(_context.local_participant_id)


## Applies the newest host pose without client prediction or interpolation.
@rpc("authority", "call_remote", "unreliable_ordered", 3)
func _receive_movement(
	session_id: String,
	match_revision: int,
	packet: PackedByteArray,
	acknowledged_sequence: int,
) -> void:
	if (
		_context.is_host
		or not _client.baseline_installed
		or session_id != _context.session_id
		or match_revision != _match_revision()
	):
		return
	var decoded: Dictionary = _codec.decode_movement(packet)
	if not decoded.get("ok", false):
		return
	var applied: Dictionary = _store.apply_movement(session_id, match_revision, packet)
	if not applied.get("ok", false):
		return
	for entity_id: int in applied.get("applied_ids", []):
		_apply_replica_state(entity_id, acknowledged_sequence)


## Sends immutable baseline framing through reliable RPCs at the saved Match path.
func send_baseline_to_peer(
	native_peer_id: int,
	metadata: Dictionary,
	packets: Array[PackedByteArray],
) -> bool:
	if not _can_send_to_peer(native_peer_id):
		return false
	_receive_vehicle_descriptors.rpc_id(
		native_peer_id,
		_context.session_id,
		_match_revision(),
		_vehicle_replicator.descriptor_rows(),
		_vehicle_transfer_rows(),
	)
	_receive_player_bindings.rpc_id(
		native_peer_id,
		_context.session_id,
		_match_revision(),
		_binding_rows(),
	)
	_receive_lifecycle_hydration.rpc_id(
		native_peer_id,
		_context.session_id,
		_match_revision(),
		_lifecycle.revision(),
		_lifecycle.hydration_rows(_sequence.physics_tick),
	)
	_receive_baseline_metadata.rpc_id(native_peer_id, metadata)
	for packet: PackedByteArray in packets:
		_receive_baseline_chunk.rpc_id(native_peer_id, packet)
	return true


## Sends one reliable lifecycle record to one peer.
func send_durable_to_peer(native_peer_id: int, packet: PackedByteArray) -> bool:
	if not _can_send_to_peer(native_peer_id):
		return false
	_receive_durable.rpc_id(
		native_peer_id,
		_context.session_id,
		_match_revision(),
		packet,
	)
	return true


## Sends the current complete lifecycle snapshot for one admission marker.
func send_lifecycle_to_peer(native_peer_id: int, lifecycle_revision: int) -> bool:
	if not _can_send_to_peer(native_peer_id) or lifecycle_revision != _lifecycle.revision():
		return false
	_receive_vehicle_descriptors.rpc_id(
		native_peer_id,
		_context.session_id,
		_match_revision(),
		_vehicle_replicator.descriptor_rows(),
		_vehicle_transfer_rows(),
	)
	_receive_player_bindings.rpc_id(
		native_peer_id,
		_context.session_id,
		_match_revision(),
		_binding_rows(),
	)
	_receive_lifecycle_hydration.rpc_id(
		native_peer_id,
		_context.session_id,
		_match_revision(),
		lifecycle_revision,
		_lifecycle.hydration_rows(_sequence.physics_tick),
	)
	return true


## Sends one reliable handoff cut to one peer through both required revisions.
func send_handoff_to_peer(
	native_peer_id: int,
	baseline_id: int,
	commit_revision: int,
	lifecycle_revision: int,
) -> bool:
	if not _can_send_to_peer(native_peer_id):
		return false
	_receive_handoff.rpc_id(
		native_peer_id,
		_context.session_id,
		_match_revision(),
		baseline_id,
		commit_revision,
		lifecycle_revision,
	)
	return true


## Marks the peer admitted locally before opening its remote input gate.
func send_grant_to_peer(
	native_peer_id: int,
	baseline_id: int,
	commit_revision: int,
	lifecycle_revision: int,
) -> bool:
	if not _can_send_to_peer(native_peer_id):
		return false
	_receive_grant.rpc_id(
		native_peer_id,
		_context.session_id,
		_match_revision(),
		baseline_id,
		commit_revision,
		lifecycle_revision,
	)
	return true


## Sends one reset supersession before starting the replacement admission.
func send_reset_begin_to_peer(native_peer_id: int, match_revision: int) -> bool:
	if not _can_send_to_peer(native_peer_id) or match_revision != _match_revision():
		return false
	_receive_reset_begin.rpc_id(native_peer_id, _context.session_id, match_revision)
	return true


## Confirms one current network peer exists before reporting transport acceptance.
func _can_send_to_peer(native_peer_id: int) -> bool:
	return (
		native_peer_id > 0
		and multiplayer.multiplayer_peer != null
		and multiplayer.multiplayer_peer.get_connection_status()
		== MultiplayerPeer.CONNECTION_CONNECTED
	)


## Ends mapped peers that never start baseline before their original admission deadline.
func _expire_waiting_mapped_peers(now_msec: int) -> void:
	for native_peer_id: int in _waiting_admission_deadline_by_peer.keys():
		if now_msec < int(_waiting_admission_deadline_by_peer[native_peer_id]):
			continue
		abort_peer(native_peer_id, &"SYNC_TIMEOUT")


## Removes every failed provisional life before ending its native peer.
func abort_peer(native_peer_id: int, _failure_code: StringName) -> void:
	var participant_id: int = _identities.resolve_sender(native_peer_id)
	if participant_id > 0:
		remove_peer(native_peer_id, participant_id)
	else:
		_admitted_peers.erase(native_peer_id)
	if multiplayer is SceneMultiplayer:
		(multiplayer as SceneMultiplayer).disconnect_peer(native_peer_id)


## Spawns one host-owned body only after an atomic safe-anchor reservation.
func _spawn_authoritative_player(participant_id: int, admitted: bool) -> ActorMotion:
	if _actors_by_participant.has(participant_id):
		return _actors_by_participant[participant_id]
	var binding: Dictionary = _allocate_player_binding(participant_id)
	if binding.is_empty():
		return null
	var candidate: Dictionary = _reserve_spawn_candidate(participant_id)
	if candidate.is_empty():
		return null
	var actor: ActorMotion = _instantiate_authority_actor(participant_id, candidate.transform)
	_spawn_reservations.release(participant_id)
	if actor == null:
		return null
	_suppress_lifecycle_publish = true
	var registered: bool = _lifecycle.register_player(
		participant_id,
		{ "id": binding.id, "generation": binding.generation },
		admitted,
	)
	_suppress_lifecycle_publish = false
	if not registered:
		actor.queue_free()
		_actors_by_participant.erase(participant_id)
		return null
	return actor


## Advances generation and replaces the dead body at a lifecycle-selected safe anchor.
func _respawn_authoritative_player(
	participant_id: int,
	candidate: Dictionary,
) -> Dictionary:
	var bindings: Dictionary = _player_identity.binding_by_participant
	var previous: Dictionary = bindings.get(participant_id, {})
	if previous.is_empty():
		return { "ok": false }
	var tracker: EntityGenerationTracker = _player_identity.tracker
	var previous_ref: Dictionary = {
		"id": previous.id,
		"generation": previous.generation,
	}
	if tracker.is_current(previous_ref):
		tracker.retire(previous_ref)
	var reused: Dictionary = tracker.reuse(int(previous.id))
	if not reused.get("ok", false):
		return reused

	var entity_ref: Dictionary = reused.entity_ref
	var binding: Dictionary = {
		"participant_id": participant_id,
		"id": entity_ref.id,
		"generation": entity_ref.generation,
	}
	bindings[participant_id] = binding
	_player_identity.participant_by_entity[int(binding.id)] = participant_id
	var old_actor: ActorMotion = _actors_by_participant.get(participant_id)
	var actor: ActorMotion = _instantiate_authority_actor(participant_id, candidate.transform)
	if actor == null:
		return { "ok": false }
	if old_actor != null and old_actor != actor:
		old_actor.queue_free()
	if not _resetting:
		_broadcast_bindings()
		_sequence.durable_revision += 1
		_admission.publish_durable(
			_durable_event(1, PHASE_LIVE, participant_id, _sequence.durable_revision)
		)
	if participant_id == int(_context.local_participant_id):
		_local_rig().bind_actor(actor)
	return { "ok": true, "entity_ref": entity_ref }


## Instantiates one saved player scene at a committed authoritative spawn transform.
func _instantiate_authority_actor(
	participant_id: int,
	spawn_transform: Transform3D,
) -> ActorMotion:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	actor.name = "Player%d" % participant_id
	_runtime_entities().add_child(actor)
	actor.global_transform = spawn_transform
	_actors_by_participant[participant_id] = actor
	return actor


## Selects at most ten authored candidates while respecting queries and reservations.
func _reserve_spawn_candidate(participant_id: int) -> Dictionary:
	var candidates: Array[Dictionary] = _city_data().anchor_descriptors(
		WorldAnchor.KIND_PLAYER_SPAWN
	)
	var first_slot: int = _allocate_spawn_slot(participant_id)
	for offset: int in mini(PlayerLifecycle.MAX_CANDIDATES_PER_TICK, candidates.size()):
		var index: int = (maxi(1, first_slot) - 1 + offset) % candidates.size()
		var candidate: Dictionary = candidates[index]
		if _is_spawn_blocked(candidate, participant_id):
			continue
		if _spawn_reservations.reserve(
			participant_id,
			candidate.world_id,
			candidate.transform.origin,
			PLAYER_CLEARANCE_RADIUS_M,
		):
			_player_identity.spawn_slot_by_participant[participant_id] = index + 1
			return candidate
	return {}


## Queries the actual actor envelope against world, actor, vehicle, and reservation solids.
func _is_spawn_blocked(candidate: Dictionary, participant_id: int) -> bool:
	if _spawn_reservations.conflicts(
		candidate.transform.origin,
		PLAYER_CLEARANCE_RADIUS_M,
		participant_id,
	):
		return true
	if not is_inside_tree() or _runtime_entities().get_world_3d() == null:
		return false

	var shape := CapsuleShape3D.new()
	shape.radius = PLAYER_CLEARANCE_RADIUS_M
	shape.height = PLAYER_CLEARANCE_HEIGHT_M
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = candidate.transform.translated_local(
		Vector3.UP * PLAYER_CLEARANCE_HEIGHT_M * 0.5
	)
	query.collision_mask = SPAWN_COLLISION_MASK
	query.collide_with_areas = false
	query.collide_with_bodies = true
	var replacing: ActorMotion = _actors_by_participant.get(participant_id)
	if replacing != null:
		query.exclude = [replacing.get_rid()]
	return not (
		_runtime_entities()
		.get_world_3d()
		.direct_space_state
		.intersect_shape(query, 1)
		.is_empty()
	)


## Queries the shared actor envelope at one authored entry or exit transfer point.
func _is_clearance_blocked(
	candidate: Transform3D,
	participant_id: int,
	actor: ActorMotion,
	vehicle: VehicleMotion,
) -> bool:
	if _spawn_reservations.conflicts(
		candidate.origin, PLAYER_CLEARANCE_RADIUS_M, participant_id
	):
		return true
	if not is_inside_tree() or _runtime_entities().get_world_3d() == null:
		return false
	var shape := CapsuleShape3D.new()
	shape.radius = PLAYER_CLEARANCE_RADIUS_M
	shape.height = PLAYER_CLEARANCE_HEIGHT_M
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = candidate.translated_local(
		Vector3.UP * PLAYER_CLEARANCE_HEIGHT_M * 0.5
	)
	query.collision_mask = SPAWN_COLLISION_MASK
	query.collide_with_areas = false
	query.collide_with_bodies = true
	query.exclude = [actor.get_rid(), vehicle.get_rid()]
	return not (
		_runtime_entities()
		.get_world_3d()
		.direct_space_state
		.intersect_shape(query, 1)
		.is_empty()
	)


## Instantiates all baseline player rows before local input can be granted.
func _materialize_baseline(rows: Array[Dictionary]) -> void:
	for row: Dictionary in rows:
		if int(row.kind) == VehicleReplicator.ENTITY_KIND_VEHICLE:
			_apply_replica_state(int(row.id), 0)
			continue
		var participant_id: int = int(
			_player_identity.participant_by_entity.get(int(row.id), 0)
		)
		if participant_id == 0:
			continue
		var actor: ActorMotion = _actors_by_participant.get(participant_id)
		if actor == null:
			actor = _instantiate_replica(participant_id)
		_apply_replica_state(int(row.id), 0)
	_sync_vehicle_occupancy_presentation()


## Reconciles local prediction or feeds one passive remote presentation sample.
func _apply_replica_state(entity_id: int, acknowledged_sequence: int) -> void:
	var state: Dictionary = _store.entity_state(entity_id)
	if state.is_empty() or int(state.phase) == PHASE_REMOVED:
		return
	if int(state.kind) == VehicleReplicator.ENTITY_KIND_VEHICLE:
		var applied: bool = _vehicle_replicator.apply_replica_state(
			state,
			_context.local_participant_id,
			acknowledged_sequence,
			_now_msec(),
		)
		var binding: Dictionary = _vehicle_replicator.binding_for_participant(
			_context.local_participant_id
		)
		if applied and int(binding.get("id", 0)) == entity_id:
			movement_applied.emit(_context.local_participant_id)
		return
	var participant_id: int = int(_player_identity.participant_by_entity.get(entity_id, 0))
	if participant_id == 0:
		return
	var life_ref: Dictionary = _lifecycle.entity_ref_for(participant_id)
	if (
		life_ref.is_empty()
		or int(life_ref.id) != entity_id
		or int(life_ref.generation) != int(state.generation)
	):
		return
	var actor: ActorMotion = _actors_by_participant.get(participant_id)
	if actor == null:
		actor = _instantiate_replica(participant_id)
	var position := Vector3(float(state.x), float(state.y), float(state.z))
	var velocity := Vector3(float(state.vx), float(state.vy), float(state.vz))
	var alive: bool = _lifecycle.is_alive(participant_id)
	_replica_pose_generation_by_participant[participant_id] = int(state.generation)
	_set_actor_alive(participant_id, alive)
	if participant_id == _context.local_participant_id:
		_apply_local_replica_state(
			actor,
			participant_id,
			state,
			{ "position": position, "velocity": velocity, "alive": alive },
			acknowledged_sequence,
		)
		return
	_apply_remote_replica_state(actor, participant_id, state, position, velocity)


## Reconciles one current local row or installs it while input remains closed.
func _apply_local_replica_state(
	actor: ActorMotion,
	participant_id: int,
	state: Dictionary,
	motion: Dictionary,
	acknowledged_sequence: int,
) -> void:
	var driving: bool = not _vehicle_replicator.binding_for_participant(
		participant_id
	).is_empty()
	if bool(motion.alive) and _client.grant_received:
		_client.input_open = true
		if not driving:
			_bind_client_input()
	if _client.input_open and not driving:
		var reconciliation: Dictionary = _prediction_owner().reconcile_motion(
			motion.position,
			motion.velocity,
			float(state.yaw),
			(int(state.flags) & MOVEMENT_FLAG_GROUNDED) != 0,
			acknowledged_sequence,
		)
		if reconciliation.get("history_exhausted", false):
			_request_local_input_recovery(float(reconciliation.correction_metres))
	else:
		actor.global_position = motion.position
		actor.rotation.y = float(state.yaw)
		actor.velocity = motion.velocity
	movement_applied.emit(participant_id)


## Pushes one current remote row into bounded passive presentation smoothing.
func _apply_remote_replica_state(
	actor: ActorMotion,
	participant_id: int,
	state: Dictionary,
	position: Vector3,
	velocity: Vector3,
) -> void:
	actor.global_position = position
	actor.rotation.y = float(state.yaw)
	actor.velocity = velocity
	var presentation: PlayerMotionPresentation = actor.get_node_or_null(
		"PresentationAnchor"
	) as PlayerMotionPresentation
	if presentation != null:
		presentation.apply_motion(actor.velocity, actor.rotation.y)
	var smoother: RemoteMotionSmoother = RemoteMotionSmoother.resolve(
		_remote_smoothers(),
		participant_id,
		_player_identity.binding_by_participant.get(participant_id, {}),
		remote_extrapolation_msec,
		remote_authority_blend_msec,
	)
	var now_msec: int = _now_msec()
	smoother.push(
		{
			"position": position,
			"velocity": velocity,
			"aim_yaw": float(state.yaw),
		},
		now_msec,
	)
	RemoteMotionSmoother.apply_display(actor, smoother.sample(now_msec))


## Creates one non-simulating courier replica at its authored participant anchor.
func _instantiate_replica(participant_id: int) -> ActorMotion:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	actor.name = "Player%d" % participant_id
	_runtime_entities().add_child(actor)
	var spawn: Marker3D = _spawn_for_slot(1)
	if spawn != null:
		actor.global_position.y = spawn.global_position.y
	_actors_by_participant[participant_id] = actor
	_set_actor_alive(participant_id, false)
	return actor


## Removes one terminal replica while retaining its state-store tombstone.
func _remove_replica(participant_id: int) -> void:
	var actor: ActorMotion = _actors_by_participant.get(participant_id)
	if actor == null:
		return
	_actors_by_participant.erase(participant_id)
	_replica_pose_generation_by_participant.erase(participant_id)
	var smoother: RemoteMotionSmoother = _remote_smoothers().get(participant_id)
	if smoother != null:
		smoother.clear()
	_remote_smoothers().erase(participant_id)
	if participant_id == _context.local_participant_id:
		invalidate_client_motion()
	actor.queue_free()


## Increments only the fixed malformed-packet diagnostics with saturation.
func _record_command_rejection(code: StringName) -> void:
	if code not in [&"PACKET_SIZE", &"MALFORMED_COMMAND", &"COMMAND_OUT_OF_RANGE"]:
		return
	var counts: Dictionary = _context.command_rejections
	counts[code] = mini(counts.get(code, 0) + 1, 0x7fff_ffff)


## Consumes one bounded per-participant token before decoding remote intent.
func _consume_input_rate(participant_id: int) -> bool:
	var now_msec: int = _now_msec()
	var state: Dictionary = _input_state_by_participant.get(
		participant_id,
		{
			"initialized": false,
			"last_sequence": 0,
			"tokens": INPUT_BURST,
			"updated_msec": now_msec,
		},
	)
	var elapsed_msec: int = maxi(0, now_msec - int(state.updated_msec))
	state.tokens = minf(
		INPUT_BURST,
		float(state.tokens) + float(elapsed_msec) * INPUT_RATE_PER_SECOND / 1000.0,
	)
	state.updated_msec = now_msec
	_input_state_by_participant[participant_id] = state
	if float(state.tokens) < 1.0:
		return false

	state.tokens = float(state.tokens) - 1.0
	_input_state_by_participant[participant_id] = state
	return true


## Consumes one bounded queued frame per live remote participant.
func _step_remote_players(delta: float) -> void:
	var now_msec: int = _now_msec()
	for participant_id: int in _actors_by_participant:
		if participant_id == _context.local_participant_id:
			continue
		var actor: ActorMotion = _actors_by_participant[participant_id]
		if (
			not _lifecycle.is_alive(participant_id)
			or not _vehicle_replicator.binding_for_participant(participant_id).is_empty()
		):
			actor.neutralize()
			continue
		var queue: FootInputQueue = _input_authority.queue(participant_id)
		if queue == null:
			actor.neutralize()
			continue
		var decision: Dictionary = queue.consume(now_msec)
		var command: FootCommand = decision.command
		if command == null:
			actor.neutralize()
			continue
		actor.step(command, delta, ActorMotion.StepMode.AUTHORITY)


## Publishes one shared encoded latest-state packet set to every admitted peer.
func _publish_movement() -> void:
	if _admitted_peers.is_empty():
		return
	_sequence.movement_sequence = (_sequence.movement_sequence + 1) & 0xffff
	var encoded: Dictionary = _codec.encode_movement(
		_sequence.movement_sequence, _sequence.physics_tick, _capture_rows()
	)
	if not encoded.get("ok", false):
		return
	for native_peer_id: int in _admitted_peers.keys():
		var participant_id: int = _identities.resolve_sender(native_peer_id)
		var acknowledgement: int = _input_authority.acknowledgement(participant_id)
		if not _vehicle_replicator.binding_for_participant(participant_id).is_empty():
			acknowledgement = _vehicle_replicator.acknowledgement(participant_id)
		for packet: PackedByteArray in encoded.packets:
			_receive_movement.rpc_id(
				native_peer_id,
				_context.session_id,
				_match_revision(),
				packet,
				acknowledgement,
			)


## Captures every live host player exactly once for baseline or rate-bucket encode.
func _capture_rows() -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var participant_ids: Array[int] = _actors_by_participant.keys()
	participant_ids.sort()
	for participant_id: int in participant_ids:
		if not _lifecycle.is_alive(participant_id):
			continue
		var actor: ActorMotion = _actors_by_participant[participant_id]
		var binding: Dictionary = _player_identity.binding_by_participant.get(
			participant_id, {}
		)
		if binding.is_empty():
			continue
		var state: Dictionary = actor.motion_state()
		var position: Vector3 = state.position
		var velocity: Vector3 = state.velocity
		rows.append(
			{
				"id": binding.id,
				"generation": binding.generation,
				"kind": ENTITY_KIND_PLAYER,
				"phase": PHASE_LIVE,
				"flags": MOVEMENT_FLAG_GROUNDED if bool(state.grounded) else 0,
				"x": position.x,
				"y": position.y,
				"z": position.z,
				"vx": velocity.x,
				"vy": velocity.y,
				"vz": velocity.z,
				"yaw": actor.rotation.y,
			}
		)
	rows.append_array(_vehicle_replicator.capture_rows())
	return rows


## Builds one reliable player lifecycle event at the current physics tick.
func _durable_event(
	event_kind: int,
	phase: int,
	participant_id: int,
	revision: int,
) -> Dictionary:
	var binding: Dictionary = _player_identity.binding_by_participant[participant_id]
	return {
		"event_kind": event_kind,
		"phase": phase,
		"id": binding.id,
		"generation": binding.generation,
		"revision": revision,
		"tick": _sequence.physics_tick,
	}


## Allocates one EntityRef independently from the Session-owned participant identity.
func _allocate_player_binding(participant_id: int) -> Dictionary:
	var bindings: Dictionary = _player_identity.binding_by_participant
	if bindings.has(participant_id):
		return bindings[participant_id]
	var tracker: EntityGenerationTracker = _player_identity.tracker
	var allocated: Dictionary = tracker.allocate()
	if not allocated.get("ok", false):
		return {}

	var entity_ref: Dictionary = allocated.entity_ref
	var binding: Dictionary = {
		"participant_id": participant_id,
		"id": entity_ref.id,
		"generation": entity_ref.generation,
	}
	bindings[participant_id] = binding
	_player_identity.participant_by_entity[int(entity_ref.id)] = participant_id
	return binding


## Retires one host binding after its reliable removal event has been published.
func _retire_player_binding(participant_id: int) -> void:
	var bindings: Dictionary = _player_identity.binding_by_participant
	var binding: Dictionary = bindings.get(participant_id, {})
	if binding.is_empty():
		return
	var tracker: EntityGenerationTracker = _player_identity.tracker
	tracker.retire({ "id": binding.id, "generation": binding.generation })
	_player_identity.participant_by_entity.erase(int(binding.id))
	bindings.erase(participant_id)


## Returns bounded immutable binding rows for reliable delivery before state records.
func _binding_rows() -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for participant_id: int in _player_identity.binding_by_participant:
		rows.append(
			_player_identity.binding_by_participant[participant_id].duplicate()
		)
	return rows


## Captures exact player pose and foot epoch in the reliable seat-transfer transaction.
func _vehicle_transfer_rows() -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var participant_ids: Array[int] = _actors_by_participant.keys()
	participant_ids.sort()
	for participant_id: int in participant_ids:
		var actor: ActorMotion = _actors_by_participant[participant_id]
		var player_ref: Dictionary = _lifecycle.entity_ref_for(participant_id)
		if actor == null or player_ref.is_empty():
			continue
		rows.append(
			{
				"participant_id": participant_id,
				"player_id": int(player_ref.id),
				"generation": int(player_ref.generation),
				"seated": not _vehicle_replicator.binding_for_participant(
					participant_id
				).is_empty(),
				"foot_input_epoch": _input_authority.input_epoch(participant_id),
				"x": actor.global_position.x,
				"y": actor.global_position.y,
				"z": actor.global_position.z,
				"yaw": actor.rotation.y,
				"transaction_revision": _vehicle_interaction.transaction_revision(),
			}
		)
	return rows


## Publishes new binding dependencies before their reliable spawn event.
func _broadcast_bindings() -> void:
	var rows: Array[Dictionary] = _binding_rows()
	for native_peer_id: int in _admitted_peers:
		_receive_player_bindings.rpc_id(
			native_peer_id,
			_context.session_id,
			_match_revision(),
			rows,
		)


## Publishes committed seat/control transactions before dependent movement acknowledgement.
func _broadcast_vehicle_descriptors() -> void:
	var rows: Array[Dictionary] = _vehicle_replicator.descriptor_rows()
	var transfers: Array[Dictionary] = _vehicle_transfer_rows()
	for native_peer_id: int in _admitted_peers:
		_receive_vehicle_descriptors.rpc_id(
			native_peer_id,
			_context.session_id,
			_match_revision(),
			rows,
			transfers,
		)


## Publishes an accepted transaction and applies local camera/HUD ownership afterward.
func _on_vehicle_transaction_committed(
	participant_id: int,
	_result: Dictionary,
) -> void:
	if participant_id == int(_context.local_participant_id):
		_local_rig().reset_vehicle_command_sequence()
	_broadcast_vehicle_descriptors()
	_sync_vehicle_occupancy_presentation()


## Routes one processed action result back to its sender without installing gameplay state.
func _on_vehicle_action_resolved(participant_id: int, result: Dictionary) -> void:
	if participant_id == int(_context.local_participant_id):
		vehicle_action_resolved.emit(result.duplicate(true))
		return
	var native_peer_id: int = int(_peer_by_participant.get(participant_id, 0))
	if native_peer_id > 0:
		_send_vehicle_action_result(native_peer_id, participant_id, result)


## Sends one bounded result on control stream zero; descriptors remain the state writer.
func _send_vehicle_action_result(
	native_peer_id: int,
	participant_id: int,
	result: Dictionary,
) -> void:
	if not _can_send_to_peer(native_peer_id):
		return
	_receive_vehicle_action_result.rpc_id(
		native_peer_id,
		{
			"session_id": _context.session_id,
			"match_revision": _match_revision(),
			"participant_id": participant_id,
			"result": result.duplicate(true),
		},
	)


## Builds one exact action envelope without accepting participant identity from the client.
func _build_vehicle_action_envelope(
	kind: StringName,
	action_sequence: int,
	player_ref: Dictionary,
	vehicle_ref: Dictionary,
) -> Dictionary:
	var envelope: Dictionary = {
		"session_id": _context.session_id,
		"match_revision": _match_revision(),
		"player_id": int(player_ref.id),
		"player_generation": int(player_ref.generation),
		"action_sequence": action_sequence,
		"kind": kind,
	}
	if kind == VehicleInteraction.ACTION_ENTER:
		envelope.vehicle_ref = vehicle_ref.duplicate()
	return envelope


## Applies seat visibility and acceptance-only local camera/input ownership together.
func _sync_vehicle_occupancy_presentation() -> void:
	for participant_id: int in _actors_by_participant:
		var actor: ActorMotion = _actors_by_participant[participant_id]
		var binding: Dictionary = _vehicle_replicator.binding_for_participant(participant_id)
		var seated: bool = not binding.is_empty()
		actor.collision_layer = 0 if seated else (2 if _lifecycle.is_alive(participant_id) else 0)
		actor.collision_mask = 0 if seated else (1 if _lifecycle.is_alive(participant_id) else 0)
		var presentation: Node3D = actor.get_node_or_null("PresentationAnchor") as Node3D
		if presentation != null:
			presentation.visible = not seated and _lifecycle.is_alive(participant_id)
		if participant_id != int(_context.local_participant_id):
			continue
		if seated:
			var vehicle: VehicleMotion = _vehicle_replicator.vehicle_for_entity(int(binding.id))
			_local_rig().bind_vehicle(vehicle)
			_local_rig().set_vehicle_input_enabled(
				_client.local_input_enabled and _lifecycle.is_alive(participant_id)
			)
		elif _context.is_host:
			_local_rig().bind_actor(actor)
			_local_rig().set_actor_control_enabled(_lifecycle.is_alive(participant_id))
		else:
			_bind_client_input()


## Clears old-life input before publishing one complete lifecycle transition.
func _on_lifecycle_transition(participant_id: int, state: Dictionary) -> void:
	if not _context.is_host:
		return
	_input_authority.remove(participant_id)
	_input_state_by_participant.erase(participant_id)
	var actor: ActorMotion = _actors_by_participant.get(participant_id)
	if actor != null:
		actor.neutralize()
	if bool(state.get("alive", false)) and bool(state.get("admitted", false)):
		_input_authority.grant(participant_id)
	if _resetting or _suppress_lifecycle_publish:
		return
	_admission.publish_lifecycle(_lifecycle.revision())
	_publish_lifecycle_state()
	_apply_lifecycle_to_actors()


## Sends one complete lifecycle snapshot over the ordered reliable state stream.
func _publish_lifecycle_state() -> void:
	for native_peer_id: int in _admitted_peers:
		_transport.send_lifecycle(native_peer_id, _lifecycle.revision())


## Commits death ordering before notifying lifecycle and presentation observers.
func _commit_player_death(participant_id: int) -> bool:
	if not _lifecycle.is_alive(participant_id):
		return false
	var actor: ActorMotion = _actors_by_participant.get(participant_id)
	if actor == null:
		return false

	_input_authority.remove(participant_id)
	_input_state_by_participant.erase(participant_id)
	if _vehicle_interaction != null:
		var released: Dictionary = _vehicle_interaction.release_for_lifecycle(
			participant_id, &"DEATH"
		)
		if not released.get("ok", false):
			return false
	actor.neutralize()
	_set_actor_alive(participant_id, false)
	_sequence.durable_revision += 1
	var published: Dictionary = _admission.publish_durable(
		_durable_event(3, 2, participant_id, _sequence.durable_revision)
	)
	if not published.get("ok", false):
		_sequence.durable_revision -= 1
		_set_actor_alive(participant_id, true)
		return false
	return _lifecycle.mark_dead(participant_id, _sequence.physics_tick)


## Applies life-owned collision, visibility, input, and HUD gates without deriving state.
func _apply_lifecycle_to_actors() -> void:
	for participant_id: int in _actors_by_participant:
		var alive: bool = _lifecycle.is_alive(participant_id)
		if not _context.is_host:
			alive = alive and _replica_has_current_pose(participant_id)
		_set_actor_alive(participant_id, alive)


## Disables every retained old body before reset spawn selection begins.
func _apply_dead_to_all_actors() -> void:
	for participant_id: int in _actors_by_participant:
		_set_actor_alive(participant_id, false)


## Reports whether a replica has received a pose for its current lifecycle generation.
func _replica_has_current_pose(participant_id: int) -> bool:
	var entity_ref: Dictionary = _lifecycle.entity_ref_for(participant_id)
	return (
		not entity_ref.is_empty()
		and int(_replica_pose_generation_by_participant.get(participant_id, 0))
		== int(entity_ref.generation)
	)


## Applies one committed alive/dead presentation and collision state atomically.
func _set_actor_alive(participant_id: int, alive: bool) -> void:
	var actor: ActorMotion = _actors_by_participant.get(participant_id)
	if actor == null:
		return
	actor.collision_layer = 2 if alive else 0
	actor.collision_mask = 1 if alive else 0
	var presentation: Node3D = actor.get_node_or_null("PresentationAnchor") as Node3D
	if presentation != null:
		presentation.visible = alive
	if participant_id != int(_context.local_participant_id):
		return
	var seated: bool = (
		_vehicle_replicator != null
		and not _vehicle_replicator.binding_for_participant(participant_id).is_empty()
	)
	if _context.is_host:
		_local_rig().set_actor_control_enabled(alive and not seated)
	else:
		_client.input_open = alive and bool(_client.grant_received)
		_local_rig().set_replica_input_enabled(_client.input_open)


## Binds PlayerLifecycle as both the life owner and joined-client roster authority.
func _bind_hud_sources() -> void:
	_local_rig().bind_lifecycle(_lifecycle)
	_local_rig().bind_authoritative_roster(_lifecycle)


## Returns the dynamic revision fence advanced by coherent match reset.
func _match_revision() -> int:
	return int(_sequence.match_revision)


## Returns saved CityData without reaching into authored world descendants.
func _city_data() -> CityData:
	return get_node("../CityData") as CityData


## Assigns the first free authored spawn slot for this match-local participant lifetime.
func _allocate_spawn_slot(participant_id: int) -> int:
	var slots: Dictionary = _player_identity.spawn_slot_by_participant
	if slots.has(participant_id):
		return slots[participant_id]
	for slot: int in range(1, _player_spawns().get_child_count() + 1):
		if slot not in slots.values():
			slots[participant_id] = slot
			return slot
	return 0


## Resolves one positive one-based slot into the saved PlayerSpawns collection.
func _spawn_for_slot(spawn_slot: int) -> Marker3D:
	if spawn_slot <= 0 or spawn_slot > _player_spawns().get_child_count():
		return null
	return _player_spawns().get_child(spawn_slot - 1) as Marker3D


## Follows the accepted control body without deriving ownership from movement state.
func _follow_local_control_display() -> void:
	var participant_id: int = int(_context.local_participant_id)
	var binding: Dictionary = _vehicle_replicator.binding_for_participant(participant_id)
	if not binding.is_empty():
		_local_rig().follow_vehicle_display(
			_vehicle_replicator.vehicle_for_entity(int(binding.id))
		)
		return
	_local_rig().follow_actor_display(actor_for_participant(participant_id))


## Samples, predicts, and submits exactly one local frame per fixed physics tick.
func _sample_predict_and_submit_local_input(delta_seconds: float) -> void:
	if _sample_and_submit_local_vehicle_input(delta_seconds):
		return
	var input: DesktopFootInput = _local_input()
	if input == null:
		return
	var command: FootCommand = input.sample(_sequence.physics_tick)
	predict_and_submit_local_command(command, delta_seconds)


## Routes saved desktop drive intent through client prediction or the host-local queue.
func _sample_and_submit_local_vehicle_input(delta_seconds: float) -> bool:
	var participant_id: int = int(_context.local_participant_id)
	if _vehicle_replicator.binding_for_participant(participant_id).is_empty():
		return false
	var command: DriveCommand = _local_rig().sample_vehicle_command()
	if command == null:
		return true
	if _context.is_host:
		submit_host_local_vehicle_command(command)
	else:
		predict_and_submit_local_vehicle_command(command, delta_seconds)
	return true


## Updates local correction decay and each passive remote presentation.
func _update_client_presentation(delta_seconds: float) -> void:
	_prediction_owner().tick_visual(delta_seconds)
	var now_msec: int = _now_msec()
	_vehicle_replicator.tick_presentation(delta_seconds, now_msec)
	for participant_id: int in _remote_smoothers():
		var actor: ActorMotion = _actors_by_participant.get(participant_id)
		var smoother: RemoteMotionSmoother = _remote_smoothers()[participant_id]
		RemoteMotionSmoother.apply_display(actor, smoother.sample(now_msec))


## Returns the client-local prediction owner retained inside bounded client state.
func _prediction_owner() -> FootPrediction:
	return _client.prediction as FootPrediction


## Returns participant-keyed remote presentation owners.
func _remote_smoothers() -> Dictionary:
	return _client.remote_smoothers as Dictionary


## Requests one host-authorized reset after bounded replay history exhaustion.
func _request_local_input_recovery(correction_metres: float) -> void:
	if (
		_context.is_host
		or _client.input_recovery_pending
		or (_client.last_command_packet as PackedByteArray).size()
		!= FootCommandCodec.PACKET_BYTES
	):
		return
	_client.input_recovery_pending = true
	_client.last_recovery_correction_metres = correction_metres
	_request_input_recovery.rpc_id(
		1, _command_envelope((_client.last_command_packet as PackedByteArray).duplicate())
	)


## Restarts only the authored collector sequence after a valid lifecycle or epoch fence.
func _reset_local_command_sequence() -> void:
	var input: DesktopFootInput = _local_input()
	if input != null:
		input.reset_sequence()


## Applies current lifecycle dependencies to local replay and remote smoothing owners.
func _update_motion_contexts() -> void:
	var life_revision: int = _lifecycle.revision()
	for participant_id: int in _player_identity.binding_by_participant:
		var binding: Dictionary = _player_identity.binding_by_participant[participant_id]
		if participant_id == _context.local_participant_id:
			update_client_prediction_context(
				int(binding.id), int(binding.generation), life_revision, 1, 1
			)
			continue
		var smoother: RemoteMotionSmoother = RemoteMotionSmoother.resolve(
			_remote_smoothers(),
			participant_id,
			binding,
			remote_extrapolation_msec,
			remote_authority_blend_msec,
		)
		smoother.update_context(
			int(binding.id), int(binding.generation), life_revision, 1, 1
		)


## Binds aim collection only after the local baseline actor and grant exist.
func _bind_client_input() -> void:
	var actor: ActorMotion = _actors_by_participant.get(_context.local_participant_id)
	var input: DesktopFootInput = _local_input()
	var camera: Camera3D = _local_rig().get_node_or_null("CameraAnchor/Camera3D") as Camera3D
	if actor == null or input == null or camera == null:
		return
	if not _local_rig().bind_replica_actor(actor):
		return
	input.bind_aim(camera, actor)
	_prediction_owner().bind_actor(actor)
	_update_local_prediction_context()
	_local_rig().set_replica_input_enabled(
		_client.input_open and _client.local_input_enabled
	)
	_local_rig().follow_actor_display(actor)


## Refreshes local replay dependencies from authoritative binding and lifecycle state.
func _update_local_prediction_context() -> void:
	var binding: Dictionary = _player_identity.binding_by_participant.get(
		_context.local_participant_id, {}
	)
	if binding.is_empty():
		return
	update_client_prediction_context(
		int(binding.id), int(binding.generation), _lifecycle.revision(), 1, 1
	)


## Reads the injected monotonic clock or the engine clock in production.
func _now_msec() -> int:
	var clock: Callable = _context.clock
	return int(clock.call()) if clock.is_valid() else Time.get_ticks_msec()


## Returns the Match runtime entity container authored beside this replication root.
func _runtime_entities() -> Node3D:
	return get_node("../RuntimeEntities") as Node3D


## Returns the stable authored player spawn collection without changing its contents.
func _player_spawns() -> Node3D:
	return get_node("../Anchors/PlayerSpawns") as Node3D


## Returns the saved local rig while preserving its standalone public behavior.
func _local_rig() -> LocalRig:
	return get_node("../LocalRig") as LocalRig


## Returns the saved desktop collector without changing LocalRig standalone behavior.
func _local_input() -> DesktopFootInput:
	return _local_rig().get_node_or_null("Input") as DesktopFootInput
