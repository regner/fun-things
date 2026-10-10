extends Node
## Exercises production baseline assembly and state application over separate ENet processes.

const KIND_BASELINE_METADATA: int = 1
const KIND_BASELINE_CHUNK: int = 2
const KIND_BASELINE_ACK: int = 3
const KIND_DURABLE: int = 4
const KIND_HANDOFF: int = 5
const KIND_HANDOFF_ACK: int = 6
const KIND_GRANT: int = 7
const KIND_MOVEMENT: int = 8
const KIND_RESULT: int = 9
const KIND_READY: int = 10
const SESSION_ID: String = "0123456789abcdef0123456789abcdef"
const MATCH_REVISION: int = 1
const BASELINE_ID: int = 17
const DEADLINE_MSEC: int = 10_000
const MAX_HARNESS_PACKET_BYTES: int = 16 * 1024

var _role: String
var _port: int
var _peer: ENetMultiplayerPeer
var _codec := MeasuredReplicationCodec.new()
var _assembler := BaselineAssembler.new()
var _store := ReplicaStateStore.new(_codec, SESSION_ID, MATCH_REVISION)
var _started_msec: int
var _baseline_sent: bool = false
var _ready_sent: bool = false
var _baseline_metadata: Dictionary = {}
var _baseline_installed: bool = false
var _handoff_applied: bool = false
var _grant_received: bool = false
var _result_sent: bool = false


## Opens one bounded test endpoint from explicit process arguments.
func _ready() -> void:
	Engine.max_fps = 60
	var arguments: Dictionary = _parse_arguments(OS.get_cmdline_user_args())
	_role = arguments.get("role", "")
	_port = int(arguments.get("port", 0))
	_started_msec = Time.get_ticks_msec()
	_peer = ENetMultiplayerPeer.new()
	var error: Error
	if _role == "host":
		error = _peer.create_server(_port, 1, 4)
		if error == OK:
			_peer.host.bandwidth_limit(0, 0)
	elif _role == "client":
		error = _peer.create_client("127.0.0.1", _port, 4)
	else:
		_finish(false, "invalid role")
		return
	if error != OK:
		_finish(false, "open failed")


## Polls only this process's peer and enforces one wall-clock deadline.
func _process(_delta: float) -> void:
	if Time.get_ticks_msec() - _started_msec >= DEADLINE_MSEC:
		_finish(false, "deadline")
		return

	if _peer.get_connection_status() == MultiplayerPeer.CONNECTION_DISCONNECTED:
		_finish(_role == "client" and _result_sent, "host closed after result")
		return
	_peer.poll()
	if (
		_role == "client"
		and not _ready_sent
		and _peer.get_connection_status() == MultiplayerPeer.CONNECTION_CONNECTED
	):
		_ready_sent = true
		_send(1, KIND_READY, PackedByteArray())
	while _peer.get_available_packet_count() > 0:
		var sender: int = _peer.get_packet_peer()
		var packet: PackedByteArray = _peer.get_packet()
		_receive(sender, packet)


## Sends the immutable current state before accepting either acknowledgement.
func _send_baseline(client_peer_id: int) -> void:
	var encoded: Dictionary = _codec.encode_movement(
		BASELINE_ID,
		10,
		[_row(1, 1, 1, 0.0), _row(2, 1, 1, 5.0)],
	)
	if not encoded.ok:
		_finish(false, "baseline encode")
		return

	var packets: Array[PackedByteArray] = encoded.packets
	_baseline_metadata = _metadata(packets, 2)
	_send(client_peer_id, KIND_BASELINE_METADATA, var_to_bytes(_baseline_metadata))
	for packet: PackedByteArray in packets:
		_send(client_peer_id, KIND_BASELINE_CHUNK, packet)
	_baseline_sent = true
	print("M1-A2.2 host baseline_sent")


## Dispatches the finite integration protocol without creating another gameplay codec.
func _receive(sender: int, packet: PackedByteArray) -> void:
	if packet.is_empty() or packet.size() > MAX_HARNESS_PACKET_BYTES:
		_finish(false, "packet bound")
		return

	var kind: int = packet[0]
	var payload: PackedByteArray = packet.slice(1)
	if _role == "host":
		_receive_host(sender, kind, payload)
	else:
		_receive_client(kind, payload)


## Advances host handoff only after each explicit client acknowledgement.
func _receive_host(sender: int, kind: int, payload: PackedByteArray) -> void:
	if kind == KIND_READY and not _baseline_sent:
		_send_baseline(sender)
	elif kind == KIND_BASELINE_ACK:
		var durable: Dictionary = _codec.encode_durable(
			{
				"event_kind": 3,
				"phase": 2,
				"id": 1,
				"generation": 1,
				"revision": 1,
				"tick": 11,
			}
		)
		_send(sender, KIND_DURABLE, durable.packet)
		_send(sender, KIND_HANDOFF, _u32_payload(1))
	elif kind == KIND_HANDOFF_ACK:
		_send(sender, KIND_GRANT, _u32_payload(1))
		var movement: Dictionary = _codec.encode_movement(
			18,
			12,
			[_row(1, 1, 2, 25.0)],
		)
		_send(sender, KIND_MOVEMENT, movement.packets[0])
	elif kind == KIND_RESULT:
		print("M1-A2.2 host current_state_applied")
		_finish(payload.get_string_from_utf8() == "ok", "client result")


## Dispatches client receive work by transfer phase to keep each boundary bounded.
func _receive_client(kind: int, payload: PackedByteArray) -> void:
	if kind in [KIND_BASELINE_METADATA, KIND_BASELINE_CHUNK]:
		_receive_client_baseline(kind, payload)
	elif kind in [KIND_DURABLE, KIND_HANDOFF]:
		_receive_client_handoff(kind, payload)
	elif kind in [KIND_GRANT, KIND_MOVEMENT]:
		_receive_client_live(kind, payload)


## Installs only a complete checksum-validated baseline before acknowledging it.
func _receive_client_baseline(kind: int, payload: PackedByteArray) -> void:
	if kind == KIND_BASELINE_METADATA:
		# Variant framing exists only in this bounded harness; production codecs stay fixed.
		var value: Variant = bytes_to_var(payload)
		if value is not Dictionary or not _assembler.begin(_codec, value).ok:
			_finish(false, "metadata")
		return
	if kind != KIND_BASELINE_CHUNK:
		_finish(false, "baseline dispatch")
		return

	var received: Dictionary = _assembler.receive(SESSION_ID, 1, BASELINE_ID, payload)
	if not received.ok:
		_finish(false, "baseline chunk")
	elif received.complete:
		var baseline: Dictionary = _assembler.finish()
		if not baseline.ok or not _store.install_baseline(baseline).ok:
			_finish(false, "baseline install")
			return
		_baseline_installed = true
		_send(1, KIND_BASELINE_ACK, PackedByteArray())


## Applies the ordered durable journal before acknowledging its handoff marker.
func _receive_client_handoff(kind: int, payload: PackedByteArray) -> void:
	if kind == KIND_DURABLE:
		if not _baseline_installed or not _store.apply_durable(SESSION_ID, 1, payload).ok:
			_finish(false, "durable apply")
		return
	if kind != KIND_HANDOFF:
		_finish(false, "handoff dispatch")
		return

	if _store.durable_revision() != int(payload.decode_u32(0)):
		_finish(false, "handoff revision")
		return
	_handoff_applied = true
	_send(1, KIND_HANDOFF_ACK, PackedByteArray())


## Opens the live gate from grant and verifies one fresh movement application.
func _receive_client_live(kind: int, payload: PackedByteArray) -> void:
	if kind == KIND_GRANT:
		_grant_received = (
			_handoff_applied and _store.durable_revision() == int(payload.decode_u32(0))
		)
		return

	var applied: Dictionary = _store.apply_movement(SESSION_ID, 1, payload)
	var state: Dictionary = _store.entity_state(1)
	var ok: bool = (
		_grant_received
		and applied.ok
		and applied.applied == 1
		and state.phase == 2
		and absf(float(state.x) - 25.00435) <= 0.011
	)
	print("M1-A2.2 client baseline=%s durable=%s movement=%s" % [
		_baseline_installed,
		state.phase == 2,
		applied.get("applied", 0),
	])
	_send(1, KIND_RESULT, ("ok" if ok else "failed").to_utf8_buffer())
	_result_sent = ok
	if not ok:
		_finish(false, "state mismatch")


## Sends one harness-framed packet on reliable channel 1 to the selected peer.
func _send(target_peer: int, kind: int, payload: PackedByteArray) -> void:
	var packet := PackedByteArray([kind])
	packet.append_array(payload)
	_peer.set_target_peer(target_peer)
	_peer.set_transfer_channel(1)
	_peer.set_transfer_mode(MultiplayerPeer.TRANSFER_MODE_RELIABLE)
	if _peer.put_packet(packet) != OK:
		_finish(false, "send failed")


## Builds validated baseline metadata from the exact packet bytes sent by the host.
func _metadata(packets: Array[PackedByteArray], row_count: int) -> Dictionary:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	var total_bytes: int = 0
	for packet: PackedByteArray in packets:
		context.update(packet)
		total_bytes += packet.size()
	return {
		"session_id": SESSION_ID,
		"match_revision": MATCH_REVISION,
		"baseline_id": BASELINE_ID,
		"cut_tick": 10,
		"cut_durable_revision": 0,
		"chunk_count": packets.size(),
		"total_bytes": total_bytes,
		"row_count": row_count,
		"checksum": context.finish().hex_encode(),
	}


## Builds one complete measured row for current-state and fresh movement messages.
func _row(entity_id: int, generation: int, phase: int, x: float) -> Dictionary:
	return {
		"id": entity_id,
		"generation": generation,
		"kind": 1,
		"phase": phase,
		"flags": 0,
		"x": x,
		"z": 200.0,
		"vx": 1.0,
		"vz": 0.0,
		"yaw": 0.0,
	}


## Encodes one little-endian harness control value with a fixed four-byte bound.
func _u32_payload(value: int) -> PackedByteArray:
	var payload := PackedByteArray()
	payload.resize(4)
	payload.encode_u32(0, value)
	return payload


## Parses only the two explicit key-value fields accepted by this harness.
func _parse_arguments(arguments: PackedStringArray) -> Dictionary:
	var result: Dictionary = {}
	for argument: String in arguments:
		if argument.begins_with("--role="):
			result.role = argument.trim_prefix("--role=")
		elif argument.begins_with("--port="):
			result.port = argument.trim_prefix("--port=")
	return result


## Closes only this process's peer and exits truthfully after a structured receipt.
func _finish(ok: bool, detail: String) -> void:
	if _peer != null:
		_peer.close()
	print("M1-A2.2 RESULT " + JSON.stringify({ "role": _role, "ok": ok, "detail": detail }))
	get_tree().quit(0 if ok else 1)
