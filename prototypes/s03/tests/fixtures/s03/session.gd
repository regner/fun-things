class_name S03Session
extends Node

signal changed()
signal close_started(outcome: String)
signal completed(operation_id: int, outcome: String)

const PROTOCOL: int = 1
const CONTENT: String = "s03-tiny-v1"
const DEADLINE_MS: int = 15_000
const RESYNC_COOLDOWN_MS: int = 1000

var provider: S03Transport
var match_state: S03Match
var replication: S03Replication
var phase: String = "IDLE"
var operation_id: int = 0
var session_id: String = ""
var local_participant: int = 0
var roster: Dictionary = {}
var next_participant: int = 1
var deadline_ms: int = 0
var is_host: bool = false
var close_outcome: String = ""
var completed_operation: int = 0
var disconnected_count: int = 0


## Connect fixed multiplayer callbacks once for the process-lifetime endpoint.
func _ready() -> void:
	multiplayer.connected_to_server.connect(_connected)
	multiplayer.peer_disconnected.connect(_disconnected)
	multiplayer.server_disconnected.connect(_host_lost)
	multiplayer.connection_failed.connect(_connection_failed)


## Bound setup/hydration and per-participant loading without stopping the host.
func _process(_delta: float) -> void:
	var now: int = Time.get_ticks_msec()
	if phase not in ["IDLE", "ACTIVE"] and now > deadline_ms:
		if phase == "CLOSING":
			_closed(operation_id)
		else:
			_close("TIMEOUT")

	if not is_host or phase != "ACTIVE":
		return

	for peer_id: int in roster.keys():
		var row: Dictionary = roster[peer_id]
		if row.phase != "ADMITTED" and now > int(row.deadline):
			multiplayer.multiplayer_peer.disconnect_peer(peer_id)
			_disconnected(peer_id)


## Inject a replacement provider only after cleanup finishes.
func select_provider(candidate: S03Transport) -> bool:
	if phase != "IDLE":
		return false

	if provider != null:
		provider.peer_ready.disconnect(_peer_ready)
		provider.closed.disconnect(_closed)

	provider = candidate
	provider.peer_ready.connect(_peer_ready)
	provider.closed.connect(_closed)
	return true


## Begin a host operation; no Steam/platform initialization is required.
func host(port: int) -> int:
	if phase != "IDLE" or provider == null or port < 1 or port > 65_535:
		return 0

	_begin("STARTING")
	is_host = true
	var error: Error = provider.open_host(operation_id, port)
	if error != OK:
		_close("OPEN_FAILED")

	return operation_id


## Begin a join with an opaque adapter-owned target.
func join(target: Dictionary) -> int:
	if phase != "IDLE" or provider == null or target.is_empty():
		return 0

	_begin("CONNECTING")
	is_host = false
	var error: Error = provider.open_client(operation_id, target)
	if error != OK:
		_close("TARGET_EXPIRED")

	return operation_id


## Allocate a fresh local identity for each accepted operation.
func _begin(initial_phase: String) -> void:
	operation_id += 1
	phase = initial_phase
	deadline_ms = Time.get_ticks_msec() + DEADLINE_MS
	changed.emit()


## Attach only the active operation's native peer at existing fixed endpoints.
func _peer_ready(source_operation: int, candidate: MultiplayerPeer) -> void:
	if source_operation != operation_id or phase not in ["STARTING", "CONNECTING"]:
		if provider is S03FakeTransport:
			(provider as S03FakeTransport).dispose_obsolete(candidate)
		else:
			candidate.close()

		return

	multiplayer.multiplayer_peer = candidate
	if is_host:
		session_id = Crypto.new().generate_random_bytes(16).hex_encode()
		local_participant = 1
		match_state.authoritative = true
		match_state.session_id = session_id
		match_state.prepare_initial(local_participant)
		match_state.bind_local(local_participant)
		match_state.admit(local_participant)
		match_state.enable_local()
		phase = "ACTIVE"
		_finish(operation_id, "OK")
		changed.emit()


## Send compatibility before reserving gameplay state.
func _connected() -> void:
	if phase != "CONNECTING":
		return

	phase = "NEGOTIATING"
	_hello.rpc_id(1, operation_id, PROTOCOL, CONTENT)


## Validate compatibility and allocate a fresh sender-bound participant.
@rpc("any_peer", "call_remote", "reliable", 0)
func _hello(client_operation: int, protocol: int, content: String) -> void:
	if not is_host or phase != "ACTIVE" or protocol != PROTOCOL or content != CONTENT:
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	if client_operation <= 0 or roster.size() >= 3:
		return

	if not roster.has(peer_id):
		next_participant += 1
		roster[peer_id] = {"participant": next_participant, "operation": client_operation,
			"phase": "LOADING", "deadline": Time.get_ticks_msec() + DEADLINE_MS,
			"resync_ms": -RESYNC_COOLDOWN_MS}

	var row: Dictionary = roster[peer_id]
	if row.operation != client_operation:
		return

	_offer.rpc_id(peer_id, client_operation, session_id, row.participant)


## Load the already-authored match endpoint with replica simulation disabled.
@rpc("authority", "call_remote", "reliable", 0)
func _offer(client_operation: int, session: String, participant: int) -> void:
	if client_operation != operation_id or phase != "NEGOTIATING":
		return

	session_id = session
	local_participant = participant
	match_state.authoritative = false
	match_state.session_id = session
	phase = "SYNCHRONIZING"
	_world_ready.rpc_id(1, client_operation, session)


## Create a provisional life once, then start the bounded baseline.
@rpc("any_peer", "call_remote", "reliable", 0)
func _world_ready(client_operation: int, session: String) -> void:
	if not is_host or session != session_id:
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	if not roster.has(peer_id):
		return

	var row: Dictionary = roster[peer_id]
	if row.operation != client_operation or row.phase != "LOADING":
		return

	row.phase = "SYNCHRONIZING"
	match_state.prepare_initial(row.participant)
	replication.begin(peer_id, row.participant)


## Commit sender admission after the current reliable handoff.
func confirm_handoff(peer_id: int, baseline_id: int) -> void:
	if not roster.has(peer_id) or roster[peer_id].phase != "SYNCHRONIZING":
		return

	var row: Dictionary = roster[peer_id]
	row.phase = "ADMITTED"
	match_state.admit(row.participant)
	replication.grant(peer_id, row.participant, baseline_id)
	changed.emit()


## Mark the local operation active after authority grants admission.
func receive_admission() -> void:
	phase = "ACTIVE"
	_finish(operation_id, "OK")
	changed.emit()


## Resolve remote identity exclusively from the active native sender mapping.
func participant_for_peer(peer_id: int) -> int:
	if not roster.has(peer_id):
		return 0

	return int(roster[peer_id].participant)


## Request sequence recovery independently of the held-input window.
func request_resync() -> void:
	if phase != "ACTIVE":
		return

	phase = "SYNCHRONIZING"
	deadline_ms = Time.get_ticks_msec() + DEADLINE_MS
	match_state.rig.set_meta("input_enabled", false)
	_resync.rpc_id(1, session_id)


## Retain current gameplay state while issuing a fresh host-owned control revision.
@rpc("any_peer", "call_remote", "reliable", 0)
func _resync(session: String) -> void:
	if not is_host or session != session_id:
		return

	var peer_id: int = multiplayer.get_remote_sender_id()
	if not roster.has(peer_id):
		return

	var row: Dictionary = roster[peer_id]
	var now: int = Time.get_ticks_msec()
	if row.phase != "ADMITTED" or now - int(row.resync_ms) < RESYNC_COOLDOWN_MS:
		return

	row.resync_ms = now
	row.deadline = now + DEADLINE_MS
	row.phase = "SYNCHRONIZING"
	match_state.prepare_resync(row.participant)
	replication.begin(peer_id, row.participant)


## Cancel only the requested current attempt; cleanup is idempotent.
func cancel(requested_operation: int) -> void:
	if requested_operation != operation_id or phase in ["IDLE", "CLOSING"]:
		return

	_close("CANCELED")


## Leave through the same bounded asynchronous close path.
func leave() -> void:
	if phase not in ["IDLE", "CLOSING"]:
		if phase == "ACTIVE":
			operation_id += 1

		_close("LEFT")


## Invalidate producers before freeing match/transport resources.
func _close(outcome: String) -> void:
	phase = "CLOSING"
	close_outcome = outcome
	close_started.emit(outcome)
	deadline_ms = Time.get_ticks_msec() + DEADLINE_MS
	roster.clear()
	match_state.clear()
	replication.clear()
	multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()
	provider.close(operation_id)
	changed.emit()


## Return to idle only after adapter cleanup completes.
func _closed(source_operation: int) -> void:
	if source_operation != operation_id or phase != "CLOSING":
		return

	session_id = ""
	local_participant = 0
	phase = "IDLE"
	_finish(operation_id, close_outcome)
	changed.emit()


## Emit exactly one terminal completion per accepted operation.
func _finish(source_operation: int, outcome: String) -> void:
	if source_operation <= completed_operation:
		return

	completed_operation = source_operation
	completed.emit(source_operation, outcome)


## Release provisional entities, admission buffers and capacity on peer loss.
func _disconnected(peer_id: int) -> void:
	if not roster.has(peer_id):
		return

	match_state.rollback(roster[peer_id].participant)
	roster.erase(peer_id)
	replication.forget(peer_id)
	disconnected_count += 1
	changed.emit()


## End a listen-server client session on host loss.
func _host_lost() -> void:
	if phase not in ["IDLE", "CLOSING"]:
		_close("HOST_LOST")


## Fail a refused native connection through normal cleanup.
func _connection_failed() -> void:
	if phase not in ["IDLE", "CLOSING"]:
		_close("CONNECT_FAILED")
