class_name MatchReplication  # gdstyle:ignore=format/max-line-length,quality/max-file-length,quality/max-class-variables,quality/max-public-methods
extends Node
## Coordinates Match-local authoritative players, admission, input, and latest-state replication.

signal input_granted(participant_id: int)
signal movement_applied(participant_id: int)

const PLAYER_SCENE: PackedScene = preload("res://scenes/entities/player.tscn")
const INITIAL_MATCH_REVISION: int = 1
const MOVEMENT_INTERVAL_TICKS: int = 3
const SPAWN_COLLISION_MASK: int = 7
const PLAYER_CLEARANCE_RADIUS_M: float = 0.45
const PLAYER_CLEARANCE_HEIGHT_M: float = 2.0
const INPUT_INTERVAL_TICKS: int = 2
const INPUT_STALE_MSEC: int = 250
const INPUT_RATE_PER_SECOND: float = 60.0
const INPUT_BURST: float = 8.0
const MAX_SEQUENCE_ADVANCE: int = 120
const ENTITY_KIND_PLAYER: int = 1
const PHASE_LIVE: int = 1
const PHASE_REMOVED: int = 3

var _codec := MeasuredReplicationCodec.new()
var _identities := PeerIdentityRegistry.new()
var _transport: ReplicationTransport
var _admission: ReplicationAdmission
var _assembler := BaselineAssembler.new()
var _store: ReplicaStateStore
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
}
var _sequence: Dictionary = {
	"physics_tick": 0,
	"movement_sequence": 0,
	"baseline_id": 0,
	"durable_revision": 0,
	"match_revision": INITIAL_MATCH_REVISION,
}
var _actors_by_participant: Dictionary[int, ActorMotion] = {}
var _peer_by_participant: Dictionary[int, int] = {}
var _spawn_reservations := SpawnReservations.new()
var _resetting: bool = false
var _standalone: bool = false
var _suppress_lifecycle_publish: bool = false
var _latest_command_by_participant: Dictionary[int, Dictionary] = {}
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
		_admission.expire_attempts(_now_msec())
		_lifecycle.step(_sequence.physics_tick)
		_step_remote_players(delta)
		if _sequence.physics_tick % MOVEMENT_INTERVAL_TICKS == 0:
			_publish_movement()
	else:
		_lifecycle.step(_sequence.physics_tick)
		_follow_local_camera()
		if (
			_client.input_open
			and _client.local_input_enabled
			and _sequence.physics_tick % INPUT_INTERVAL_TICKS == 0
		):
			_sample_and_submit_local_input()


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
	return true


## Retires one disconnected mapping, actor, pending input, and admission state.
func remove_peer(native_peer_id: int, participant_id: int) -> void:
	if not _configured or not _context.is_host:
		return

	_admitted_peers.erase(native_peer_id)
	_peer_by_participant.erase(participant_id)
	_latest_command_by_participant.erase(participant_id)
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


## Allows deterministic integration drivers to replace desktop collection, not authority.
func set_local_input_enabled(enabled: bool) -> void:
	_client.local_input_enabled = enabled
	if not enabled:
		var input: DesktopFootInput = _local_input()
		if input != null:
			input.set_focused(false)


## Encodes and sends one local intent without applying it on the client.
func submit_local_command(command: FootCommand) -> bool:
	var encoded: Dictionary = FootCommandCodec.encode(command)
	if not encoded.get("ok", false):
		return false
	return send_local_command_packet(encoded.packet)


## Sends one exact command packet for alternate bounded input collectors.
func send_local_command_packet(packet: PackedByteArray) -> bool:
	if (
		_context.is_host
		or not _client.input_open
		or packet.size() != FootCommandCodec.PACKET_BYTES
	):
		return false

	var binding: Dictionary = _player_identity.binding_by_participant.get(
		_context.local_participant_id, {}
	)
	if binding.is_empty():
		return false
	_submit_command.rpc_id(
		1,
		{
			"session_id": _context.session_id,
			"match_revision": _match_revision(),
			"entity_id": int(binding.id),
			"generation": int(binding.generation),
			"packet": packet,
		},
	)
	return true


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
	var retained_peers: Dictionary[int, bool] = _admitted_peers.duplicate()
	_sequence.match_revision = _match_revision() + 1
	_sequence.durable_revision = 0
	_latest_command_by_participant.clear()
	_input_state_by_participant.clear()
	_admitted_peers.clear()
	for native_peer_id: int in retained_peers:
		_receive_reset_begin.rpc_id(
			native_peer_id,
			_context.session_id,
			_match_revision(),
		)
	_create_admission(_context.clock)
	var reset_result: Dictionary = _lifecycle.reset_players(_sequence.physics_tick)
	for native_peer_id: int in retained_peers:
		begin_admission_for_peer(native_peer_id)
	_resetting = false
	return reset_result.get("ok", false)


## Sends client readiness only after the saved Match RPC path exists locally.
func _send_ready() -> void:
	if not _configured or _context.is_host or multiplayer.multiplayer_peer == null:
		return

	_ready_for_baseline.rpc_id(1, _context.session_id, _match_revision())


## Starts baseline admission only for the sender identity supplied by SessionService.
@rpc("any_peer", "call_remote", "reliable", 0)
func _ready_for_baseline(session_id: String, match_revision: int) -> void:
	if (
		not _context.is_host
		or session_id != _context.session_id
		or match_revision != _match_revision()
	):
		return

	begin_admission_for_peer(multiplayer.get_remote_sender_id())


## Starts one sender-derived admission after Session has installed its mapping.
func begin_admission_for_peer(native_peer_id: int) -> Dictionary:
	if not _configured or not _context.is_host:
		return { "ok": false }
	var participant_id: int = _identities.resolve_sender(native_peer_id)
	if participant_id == 0:
		return { "ok": false }
	if not _actors_by_participant.has(participant_id):
		if _spawn_authoritative_player(participant_id, false) == null:
			abort_peer(native_peer_id, &"SPAWN_FAILED")
			return { "ok": false }
		_broadcast_bindings()
		_sequence.durable_revision += 1
		_admission.publish_durable(
			_durable_event(1, PHASE_LIVE, participant_id, _sequence.durable_revision)
		)
		_publish_lifecycle_state()

	_sequence.baseline_id += 1
	var started: Dictionary = _admission.start(
		native_peer_id,
		_sequence.baseline_id,
		_sequence.physics_tick,
		_capture_rows(),
	)
	started["baseline_id"] = _sequence.baseline_id
	return started


## Advances one current peer from baseline transfer to reliable handoff.
func acknowledge_baseline_for_peer(native_peer_id: int, baseline_id: int) -> Dictionary:
	return _admission.acknowledge_baseline(native_peer_id, baseline_id)


## Opens one current peer only after its matching reliable handoff marker.
func acknowledge_handoff_for_peer(
	native_peer_id: int,
	baseline_id: int,
	commit_revision: int,
) -> Dictionary:
	return _admission.acknowledge_handoff(
		native_peer_id, baseline_id, commit_revision
	)


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
) -> void:
	if (
		_context.is_host
		and session_id == _context.session_id
		and match_revision == _match_revision()
	):
		acknowledge_handoff_for_peer(
			multiplayer.get_remote_sender_id(), baseline_id, commit_revision
		)


## Validates sender admission and exact FootCommand shape before authority simulation.
@rpc("any_peer", "call_remote", "unreliable_ordered", 2)
func _submit_command(envelope: Dictionary) -> void:  # gdstyle:ignore=format/max-line-length,quality/max-function-length,quality/max-returns
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
	if packet.size() != FootCommandCodec.PACKET_BYTES:
		_record_command_rejection(&"PACKET_SIZE")
		return

	var sender: int = multiplayer.get_remote_sender_id()
	var participant_id: int = _admission.input_participant(sender)
	var binding: Dictionary = _player_identity.binding_by_participant.get(participant_id, {})
	if (
		participant_id == 0
		or not _lifecycle.is_alive(participant_id)
		or binding.is_empty()
		or int(envelope.entity_id) != int(binding.id)
		or int(envelope.generation) != int(binding.generation)
	):
		return
	if not _consume_input_rate(participant_id):
		return
	var decoded: Dictionary = FootCommandCodec.decode(packet)
	if not decoded.get("ok", false):
		_record_command_rejection(decoded.failure.code)
		return
	var command: FootCommand = decoded.command
	var input_state: Dictionary = _input_state_by_participant[participant_id]
	var previous_sequence: int = int(input_state.last_sequence)
	if bool(input_state.initialized) and (
		command.sequence <= previous_sequence
		or command.sequence > previous_sequence + MAX_SEQUENCE_ADVANCE
	):
		return

	input_state.initialized = true
	input_state.last_sequence = command.sequence
	_latest_command_by_participant[participant_id] = {
		"command": command,
		"received_msec": _now_msec(),
	}


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
		_player_identity.binding_by_participant[int(binding.participant_id)] = binding.duplicate()
		_player_identity.participant_by_entity[int(binding.id)] = int(binding.participant_id)


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
	_latest_command_by_participant.clear()
	_input_state_by_participant.clear()
	_player_identity.binding_by_participant.clear()
	_player_identity.participant_by_entity.clear()
	_store = ReplicaStateStore.new(_codec, _context.session_id, _match_revision())
	_local_rig().set_actor_control_enabled(false)


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
	if not baseline.get("ok", false) or not _store.install_baseline(baseline).get("ok", false):
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
) -> void:
	if (
		_context.is_host
		or session_id != _context.session_id
		or match_revision != _match_revision()
		or not _client.baseline_installed
		or baseline_id != _sequence.baseline_id
		or _store.durable_revision() != commit_revision
	):
		return

	_acknowledge_handoff.rpc_id(
		1,
		_context.session_id,
		_match_revision(),
		baseline_id,
		commit_revision,
	)


## Opens client intent only after baseline and reliable handoff completion.
@rpc("authority", "call_remote", "reliable", 1)
func _receive_grant(
	session_id: String,
	match_revision: int,
	baseline_id: int,
	commit_revision: int,
) -> void:
	if (
		_context.is_host
		or session_id != _context.session_id
		or match_revision != _match_revision()
		or not _client.baseline_installed
		or baseline_id != _sequence.baseline_id
		or _store.durable_revision() != commit_revision
	):
		return

	_client.grant_received = true
	_client.input_open = _lifecycle.is_alive(_context.local_participant_id)
	_bind_client_input()
	input_granted.emit(_context.local_participant_id)


## Applies the newest host pose without client prediction or interpolation.
@rpc("authority", "call_remote", "unreliable_ordered", 3)
func _receive_movement(
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
	var decoded: Dictionary = _codec.decode_movement(packet)
	if not decoded.get("ok", false):
		return
	var applied: Dictionary = _store.apply_movement(session_id, match_revision, packet)
	if not applied.get("ok", false):
		return
	for row: Dictionary in decoded.rows:
		_apply_replica_state(int(row.id))


## Sends immutable baseline framing through reliable RPCs at the saved Match path.
func send_baseline_to_peer(
	native_peer_id: int,
	metadata: Dictionary,
	packets: Array[PackedByteArray],
) -> bool:
	if not _can_send_to_peer(native_peer_id):
		return false
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


## Sends one reliable handoff cut to one peer.
func send_handoff_to_peer(
	native_peer_id: int,
	baseline_id: int,
	commit_revision: int,
) -> bool:
	if not _can_send_to_peer(native_peer_id):
		return false
	_receive_handoff.rpc_id(
		native_peer_id,
		_context.session_id,
		_match_revision(),
		baseline_id,
		commit_revision,
	)
	return true


## Marks the peer admitted locally before opening its remote input gate.
func send_grant_to_peer(
	native_peer_id: int,
	baseline_id: int,
	commit_revision: int,
) -> bool:
	if not _can_send_to_peer(native_peer_id):
		return false
	_receive_grant.rpc_id(
		native_peer_id,
		_context.session_id,
		_match_revision(),
		baseline_id,
		commit_revision,
	)
	_admitted_peers[native_peer_id] = true
	var participant_id: int = _identities.resolve_sender(native_peer_id)
	_lifecycle.set_admitted(participant_id, true)
	return true


## Confirms one current network peer exists before reporting transport acceptance.
func _can_send_to_peer(native_peer_id: int) -> bool:
	return (
		native_peer_id > 0
		and multiplayer.multiplayer_peer != null
		and multiplayer.multiplayer_peer.get_connection_status()
		== MultiplayerPeer.CONNECTION_CONNECTED
	)


## Removes timed-out provisional state before ending the failed native peer.
func abort_peer(native_peer_id: int, failure_code: StringName) -> void:
	var participant_id: int = _identities.resolve_sender(native_peer_id)
	if failure_code == &"SYNC_TIMEOUT" and participant_id > 0:
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


## Instantiates all baseline player rows before local input can be granted.
func _materialize_baseline(rows: Array[Dictionary]) -> void:
	for row: Dictionary in rows:
		var participant_id: int = int(
			_player_identity.participant_by_entity.get(int(row.id), 0)
		)
		if participant_id == 0:
			continue
		var actor: ActorMotion = _actors_by_participant.get(participant_id)
		if actor == null:
			actor = _instantiate_replica(participant_id)
		_apply_replica_state(int(row.id))


## Applies one store-owned latest pose and updates the delivered courier presentation.
func _apply_replica_state(entity_id: int) -> void:
	var participant_id: int = int(_player_identity.participant_by_entity.get(entity_id, 0))
	if participant_id == 0:
		return
	var state: Dictionary = _store.entity_state(entity_id)
	if state.is_empty() or int(state.phase) == PHASE_REMOVED:
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
	actor.global_position = Vector3(float(state.x), actor.global_position.y, float(state.z))
	actor.rotation.y = float(state.yaw)
	actor.velocity = Vector3(float(state.vx), 0.0, float(state.vz))
	var presentation: PlayerMotionPresentation = actor.get_node_or_null(
		"PresentationAnchor"
	) as PlayerMotionPresentation
	if presentation != null:
		presentation.apply_motion(actor.velocity, actor.rotation.y)
	_set_actor_alive(participant_id, _lifecycle.is_alive(participant_id))
	if participant_id == _context.local_participant_id:
		if _lifecycle.is_alive(participant_id) and _client.grant_received:
			_client.input_open = true
			_bind_client_input()
		movement_applied.emit(participant_id)


## Creates one non-simulating courier replica at its authored participant anchor.
func _instantiate_replica(participant_id: int) -> ActorMotion:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	actor.name = "Player%d" % participant_id
	_runtime_entities().add_child(actor)
	var spawn: Marker3D = _spawn_for_slot(1)
	if spawn != null:
		actor.global_position.y = spawn.global_position.y
	_actors_by_participant[participant_id] = actor
	return actor


## Removes one terminal replica while retaining its state-store tombstone.
func _remove_replica(participant_id: int) -> void:
	var actor: ActorMotion = _actors_by_participant.get(participant_id)
	if actor == null:
		return
	_actors_by_participant.erase(participant_id)
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


## Applies fresh admitted client commands and neutralizes expired held input.
func _step_remote_players(delta: float) -> void:
	var now_msec: int = _now_msec()
	for participant_id: int in _latest_command_by_participant.keys():
		var actor: ActorMotion = _actors_by_participant.get(participant_id)
		if actor == null or not _lifecycle.is_alive(participant_id):
			continue
		var latest: Dictionary = _latest_command_by_participant[participant_id]
		if now_msec - int(latest.received_msec) > INPUT_STALE_MSEC:
			actor.neutralize()
			continue
		actor.step(latest.command, delta, ActorMotion.StepMode.AUTHORITY)


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
		for packet: PackedByteArray in encoded.packets:
			_receive_movement.rpc_id(
				native_peer_id,
				_context.session_id,
				_match_revision(),
				packet,
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
				"flags": 0,
				"x": position.x,
				"z": position.z,
				"vx": velocity.x,
				"vz": velocity.z,
				"yaw": actor.rotation.y,
			}
		)
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


## Publishes reliable lifecycle/roster state after its durable dependency was committed.
func _on_lifecycle_transition(_participant_id: int, _state: Dictionary) -> void:
	if _resetting or _suppress_lifecycle_publish or not _context.is_host:
		return
	_publish_lifecycle_state()
	_apply_lifecycle_to_actors()


## Sends one complete lifecycle snapshot over the ordered reliable state stream.
func _publish_lifecycle_state() -> void:
	for native_peer_id: int in _admitted_peers:
		_receive_lifecycle_hydration.rpc_id(
			native_peer_id,
			_context.session_id,
			_match_revision(),
			_lifecycle.revision(),
			_lifecycle.hydration_rows(_sequence.physics_tick),
		)


## Commits death ordering before notifying lifecycle and presentation observers.
func _commit_player_death(participant_id: int) -> bool:
	if not _lifecycle.is_alive(participant_id):
		return false
	var actor: ActorMotion = _actors_by_participant.get(participant_id)
	if actor == null:
		return false

	_latest_command_by_participant.erase(participant_id)
	_input_state_by_participant.erase(participant_id)
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
		_set_actor_alive(participant_id, _lifecycle.is_alive(participant_id))


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
	if _context.is_host:
		_local_rig().set_actor_control_enabled(alive)
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


## Samples the authored desktop collector without applying client-side prediction.
func _sample_and_submit_local_input() -> void:
	var input: DesktopFootInput = _local_input()
	if input == null:
		return
	var command: FootCommand = input.sample(_sequence.physics_tick)
	submit_local_command(command)


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
	_local_rig().set_replica_input_enabled(
		_client.input_open and _client.local_input_enabled
	)
	_follow_local_camera()


## Keeps the authored camera centred while client prediction remains disabled.
func _follow_local_camera() -> void:
	var actor: ActorMotion = _actors_by_participant.get(_context.local_participant_id)
	var anchor: Node3D = _local_rig().get_node_or_null("CameraAnchor") as Node3D
	if actor != null and anchor != null:
		anchor.global_position = actor.global_position


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
