class_name MatchReplication
extends Node
## Coordinates Match-local authoritative players, admission, input, and latest-state replication.

signal input_granted(participant_id: int)
signal movement_applied(participant_id: int)

const PLAYER_SCENE: PackedScene = preload("res://scenes/entities/player.tscn")
const MATCH_REVISION: int = 1
const MOVEMENT_INTERVAL_TICKS: int = 3
const INPUT_INTERVAL_TICKS: int = 2
const INPUT_STALE_MSEC: int = 250
const ENTITY_KIND_PLAYER: int = 1
const PHASE_LIVE: int = 1
const PHASE_REMOVED: int = 3

var _codec := MeasuredReplicationCodec.new()
var _identities := PeerIdentityRegistry.new()
var _transport: SceneReplicationTransport
var _admission: ReplicationAdmission
var _assembler := BaselineAssembler.new()
var _store: ReplicaStateStore
var _context: Dictionary = {
	"session_id": "",
	"local_participant_id": 0,
	"is_host": false,
}
var _configured: bool = false
var _client: Dictionary = {
	"baseline_installed": false,
	"input_open": false,
	"local_input_enabled": true,
}
var _sequence: Dictionary = {
	"physics_tick": 0,
	"movement_sequence": 0,
	"baseline_id": 0,
	"durable_revision": 0,
}
var _actors_by_participant: Dictionary[int, ActorMotion] = {}
var _latest_command_by_participant: Dictionary[int, Dictionary] = {}
var _last_sequence_by_participant: Dictionary[int, int] = {}
var _admitted_peers: Dictionary[int, bool] = {}


## Remains inert in standalone Match composition until Boot supplies a network session.
func _ready() -> void:
	set_physics_process(false)


## Runs authoritative remote motion or client intent and latest-state presentation.
func _physics_process(delta: float) -> void:
	if not _configured:
		return

	_sequence.physics_tick += 1
	if _context.is_host:
		_step_remote_players(delta)
		if _sequence.physics_tick % MOVEMENT_INTERVAL_TICKS == 0:
			_publish_movement()
	else:
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
	_configured = true
	_transport = SceneReplicationTransport.new(self)
	if not _context.is_host:
		_store = ReplicaStateStore.new(_codec, _context.session_id, MATCH_REVISION)
		_send_ready.call_deferred()
	if _context.is_host:
		if not _identities.bind_peer(1, local_participant_id).ok:
			return false
		_admission = ReplicationAdmission.new(
			_codec,
			_transport,
			_identities,
			_context.session_id,
			MATCH_REVISION,
		)
		var actor: ActorMotion = _spawn_authoritative_player(local_participant_id)
		if actor == null or not _local_rig().bind_actor(actor):
			return false

	set_physics_process(true)
	return true


## Mirrors one Session-owned host mapping before accepting replication requests from it.
func admit_peer(native_peer_id: int, participant_id: int) -> bool:
	return (
		_configured
		and _context.is_host
		and _identities.bind_peer(native_peer_id, participant_id).get("ok", false)
	)


## Retires one disconnected mapping, actor, pending input, and admission state.
func remove_peer(native_peer_id: int, participant_id: int) -> void:
	if not _configured or not _context.is_host:
		return

	_admitted_peers.erase(native_peer_id)
	_latest_command_by_participant.erase(participant_id)
	_last_sequence_by_participant.erase(participant_id)
	_admission.remove_peer(native_peer_id)
	var actor: ActorMotion = _actors_by_participant.get(participant_id)
	if actor != null:
		_actors_by_participant.erase(participant_id)
		actor.queue_free()
	_sequence.durable_revision += 1
	_admission.publish_durable(
		_durable_event(2, PHASE_REMOVED, participant_id, _sequence.durable_revision)
	)


## Allows deterministic integration drivers to replace desktop collection, not authority.
func set_local_input_enabled(enabled: bool) -> void:
	_client.local_input_enabled = enabled
	if not enabled:
		var input: DesktopFootInput = _local_input()
		if input != null:
			input.set_focused(false)


## Sends one already-validated local intent to the host without applying it locally.
func submit_local_command(command: FootCommand) -> bool:
	if _context.is_host or not _client.input_open or command == null or not command.is_valid():
		return false

	var payload: Dictionary = {
		"sequence": command.sequence,
		"client_tick": command.client_tick,
		"move": command.move,
		"aim_yaw": command.aim_yaw,
		"fire_held": command.fire_held,
		"alt_held": command.alt_held,
	}
	_submit_command.rpc_id(1, _context.session_id, MATCH_REVISION, payload)
	return true


## Returns one process-local actor for wiring checks and integration receipts.
func actor_for_participant(participant_id: int) -> ActorMotion:
	return _actors_by_participant.get(participant_id)


## Reports the number of complete player bodies currently materialized in Match.
func player_count() -> int:
	return _actors_by_participant.size()


## Sends client readiness only after the saved Match RPC path exists locally.
func _send_ready() -> void:
	if not _configured or _context.is_host or multiplayer.multiplayer_peer == null:
		return

	_ready_for_baseline.rpc_id(1, _context.session_id, MATCH_REVISION)


## Starts baseline admission only for the sender identity supplied by SessionService.
@rpc("any_peer", "call_remote", "reliable", 0)
func _ready_for_baseline(session_id: String, match_revision: int) -> void:
	if (not _context.is_host
			or session_id != _context.session_id
			or match_revision != MATCH_REVISION):
		return

	var sender: int = multiplayer.get_remote_sender_id()
	var participant_id: int = _identities.resolve_sender(sender)
	if participant_id == 0:
		return
	if not _actors_by_participant.has(participant_id):
		if _spawn_authoritative_player(participant_id) == null:
			abort_peer(sender, &"SPAWN_FAILED")
			return
		_sequence.durable_revision += 1
		_admission.publish_durable(
			_durable_event(1, PHASE_LIVE, participant_id, _sequence.durable_revision)
		)

	_sequence.baseline_id += 1
	_admission.start(
		sender,
		_sequence.baseline_id,
		_sequence.physics_tick,
		_capture_rows(),
	)


## Accepts a baseline acknowledgement only from its native RPC sender.
@rpc("any_peer", "call_remote", "reliable", 0)
func _acknowledge_baseline(baseline_id: int) -> void:
	if _context.is_host:
		_admission.acknowledge_baseline(multiplayer.get_remote_sender_id(), baseline_id)


## Accepts a handoff acknowledgement only from its native RPC sender.
@rpc("any_peer", "call_remote", "reliable", 0)
func _acknowledge_handoff(baseline_id: int, commit_revision: int) -> void:
	if _context.is_host:
		_admission.acknowledge_handoff(
			multiplayer.get_remote_sender_id(), baseline_id, commit_revision
		)


## Validates sender admission and exact FootCommand shape before authority simulation.
@rpc("any_peer", "call_remote", "unreliable_ordered", 1)
func _submit_command(session_id: String, match_revision: int, payload: Dictionary) -> void:
	if (not _context.is_host
			or session_id != _context.session_id
			or match_revision != MATCH_REVISION):
		return

	var sender: int = multiplayer.get_remote_sender_id()
	var participant_id: int = _admission.input_participant(sender)
	if participant_id == 0:
		return
	var decoded: Dictionary = FootCommand.decode(payload)
	if not decoded.get("ok", false):
		return
	var command: FootCommand = decoded.command
	if command.sequence <= int(_last_sequence_by_participant.get(participant_id, 0)):
		return

	_last_sequence_by_participant[participant_id] = command.sequence
	_latest_command_by_participant[participant_id] = {
		"command": command,
		"received_msec": Time.get_ticks_msec(),
	}


## Begins one bounded client baseline transaction from the authoritative host.
@rpc("authority", "call_remote", "reliable", 0)
func _receive_baseline_metadata(metadata: Dictionary) -> void:
	if (
		_context.is_host
		or _store == null
		or not _assembler.begin(_codec, metadata).get("ok", false)
	):
		return

	_sequence.baseline_id = int(metadata.baseline_id)


## Installs complete baseline rows before acknowledging or enabling local input.
@rpc("authority", "call_remote", "reliable", 0)
func _receive_baseline_chunk(packet: PackedByteArray) -> void:
	if _context.is_host or _sequence.baseline_id <= 0:
		return
	var received: Dictionary = _assembler.receive(
		_context.session_id, MATCH_REVISION, _sequence.baseline_id, packet
	)
	if not received.get("ok", false) or not received.get("complete", false):
		return

	var baseline: Dictionary = _assembler.finish()
	if not baseline.get("ok", false) or not _store.install_baseline(baseline).get("ok", false):
		return
	_client.baseline_installed = true
	_materialize_baseline(baseline.rows)
	_acknowledge_baseline.rpc_id(1, _sequence.baseline_id)


## Applies one reliable lifecycle transition before any dependent movement row.
@rpc("authority", "call_remote", "reliable", 0)
func _receive_durable(packet: PackedByteArray) -> void:
	if _context.is_host or not _client.baseline_installed:
		return
	var decoded: Dictionary = _codec.decode_durable(packet)
	if not decoded.get("ok", false):
		return
	if not _store.apply_durable(_context.session_id, MATCH_REVISION, packet).get("ok", false):
		return
	if int(decoded.phase) == PHASE_REMOVED:
		_remove_replica(int(decoded.id))


## Acknowledges a reliable handoff marker only after all prior durable records applied.
@rpc("authority", "call_remote", "reliable", 0)
func _receive_handoff(baseline_id: int, commit_revision: int) -> void:
	if (
		_context.is_host
		or not _client.baseline_installed
		or baseline_id != _sequence.baseline_id
		or _store.durable_revision() != commit_revision
	):
		return

	_acknowledge_handoff.rpc_id(1, baseline_id, commit_revision)


## Opens client intent only after baseline and reliable handoff completion.
@rpc("authority", "call_remote", "reliable", 0)
func _receive_grant(baseline_id: int, commit_revision: int) -> void:
	if (
		_context.is_host
		or not _client.baseline_installed
		or baseline_id != _sequence.baseline_id
		or _store.durable_revision() != commit_revision
	):
		return

	_client.input_open = true
	_bind_client_input()
	input_granted.emit(_context.local_participant_id)


## Applies the newest host pose without client prediction or interpolation.
@rpc("authority", "call_remote", "unreliable_ordered", 2)
func _receive_movement(packet: PackedByteArray) -> void:
	if _context.is_host or not _client.baseline_installed:
		return
	var decoded: Dictionary = _codec.decode_movement(packet)
	if not decoded.get("ok", false):
		return
	var applied: Dictionary = _store.apply_movement(
		_context.session_id, MATCH_REVISION, packet
	)
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
	_receive_baseline_metadata.rpc_id(native_peer_id, metadata)
	for packet: PackedByteArray in packets:
		_receive_baseline_chunk.rpc_id(native_peer_id, packet)
	return true


## Sends one reliable lifecycle record to one peer.
func send_durable_to_peer(native_peer_id: int, packet: PackedByteArray) -> bool:
	if not _can_send_to_peer(native_peer_id):
		return false
	_receive_durable.rpc_id(native_peer_id, packet)
	return true


## Sends one reliable handoff cut to one peer.
func send_handoff_to_peer(
	native_peer_id: int,
	baseline_id: int,
	commit_revision: int,
) -> bool:
	if not _can_send_to_peer(native_peer_id):
		return false
	_receive_handoff.rpc_id(native_peer_id, baseline_id, commit_revision)
	return true


## Marks the peer admitted locally before opening its remote input gate.
func send_grant_to_peer(
	native_peer_id: int,
	baseline_id: int,
	commit_revision: int,
) -> bool:
	if not _can_send_to_peer(native_peer_id):
		return false
	_receive_grant.rpc_id(native_peer_id, baseline_id, commit_revision)
	_admitted_peers[native_peer_id] = true
	return true


## Confirms one current network peer exists before reporting transport acceptance.
func _can_send_to_peer(native_peer_id: int) -> bool:
	return (
		native_peer_id > 0
		and multiplayer.multiplayer_peer != null
		and multiplayer.multiplayer_peer.get_connection_status()
		== MultiplayerPeer.CONNECTION_CONNECTED
	)


## Ends one failed peer's replication admission through SceneMultiplayer.
func abort_peer(native_peer_id: int, _failure_code: StringName) -> void:
	_admitted_peers.erase(native_peer_id)
	if multiplayer is SceneMultiplayer:
		(multiplayer as SceneMultiplayer).disconnect_peer(native_peer_id)


## Spawns one host-owned body at its stable authored participant anchor.
func _spawn_authoritative_player(participant_id: int) -> ActorMotion:
	if _actors_by_participant.has(participant_id):
		return _actors_by_participant[participant_id]
	var spawn: Marker3D = _spawn_for_participant(participant_id)
	if spawn == null:
		return null
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	actor.name = "Player%d" % participant_id
	_runtime_entities().add_child(actor)
	actor.global_transform = spawn.global_transform
	_actors_by_participant[participant_id] = actor
	return actor


## Instantiates all baseline player rows before local input can be granted.
func _materialize_baseline(rows: Array[Dictionary]) -> void:
	for row: Dictionary in rows:
		var participant_id: int = int(row.id)
		var actor: ActorMotion = _actors_by_participant.get(participant_id)
		if actor == null:
			actor = _instantiate_replica(participant_id)
		_apply_replica_state(participant_id)


## Applies one store-owned latest pose and updates the delivered courier presentation.
func _apply_replica_state(participant_id: int) -> void:
	var state: Dictionary = _store.entity_state(participant_id)
	if state.is_empty() or int(state.phase) == PHASE_REMOVED:
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
	if participant_id == _context.local_participant_id:
		movement_applied.emit(participant_id)


## Creates one non-simulating courier replica at its authored participant anchor.
func _instantiate_replica(participant_id: int) -> ActorMotion:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	actor.name = "Player%d" % participant_id
	_runtime_entities().add_child(actor)
	var spawn: Marker3D = _spawn_for_participant(participant_id)
	if spawn != null:
		actor.global_transform = spawn.global_transform
	_actors_by_participant[participant_id] = actor
	return actor


## Removes one terminal replica while retaining its state-store tombstone.
func _remove_replica(participant_id: int) -> void:
	var actor: ActorMotion = _actors_by_participant.get(participant_id)
	if actor == null:
		return
	_actors_by_participant.erase(participant_id)
	actor.queue_free()


## Applies fresh admitted client commands and neutralizes expired held input.
func _step_remote_players(delta: float) -> void:
	var now_msec: int = Time.get_ticks_msec()
	for participant_id: int in _latest_command_by_participant.keys():
		var actor: ActorMotion = _actors_by_participant.get(participant_id)
		if actor == null:
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
			_receive_movement.rpc_id(native_peer_id, packet)


## Captures every live host player exactly once for baseline or rate-bucket encode.
func _capture_rows() -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var participant_ids: Array[int] = _actors_by_participant.keys()
	participant_ids.sort()
	for participant_id: int in participant_ids:
		var actor: ActorMotion = _actors_by_participant[participant_id]
		var state: Dictionary = actor.motion_state()
		var position: Vector3 = state.position
		var velocity: Vector3 = state.velocity
		rows.append(
			{
				"id": participant_id,
				"generation": 1,
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
	return {
		"event_kind": event_kind,
		"phase": phase,
		"id": participant_id,
		"generation": 1,
		"revision": revision,
		"tick": _sequence.physics_tick,
	}


## Maps participant identity deterministically onto one of four saved spawn anchors.
func _spawn_for_participant(participant_id: int) -> Marker3D:
	if participant_id <= 0 or participant_id > _player_spawns().get_child_count():
		return null
	return _player_spawns().get_child(participant_id - 1) as Marker3D


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
	input.bind_aim(camera, actor)
	input.set_focused(get_window().has_focus() and _client.local_input_enabled)
	_follow_local_camera()


## Keeps the authored camera centred while client prediction remains disabled.
func _follow_local_camera() -> void:
	var actor: ActorMotion = _actors_by_participant.get(_context.local_participant_id)
	var anchor: Node3D = _local_rig().get_node_or_null("CameraAnchor") as Node3D
	if actor != null and anchor != null:
		anchor.global_position = actor.global_position


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
