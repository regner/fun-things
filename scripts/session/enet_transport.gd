class_name ENetTransport
extends SessionTransport
## Owns ENet endpoint parsing, native peer lifecycle, and connection facts.

const PROVIDER_ID: StringName = &"enet"
const CHANNEL_COUNT: int = 4
const MAX_ADDRESS_BYTES: int = 255
const MAX_HOST_LABEL_BYTES: int = 63
const REJECTION_SLOT_COUNT: int = 1

var _adapter_generation: int = 1
var _operation_id: int = 0
var _peer: ENetMultiplayerPeer
var _role: StringName = &""
var _host_capacity: int = 0
var _workaround_applied: bool = false
var _next_connection_sequence: int = 1
var _token_by_peer: Dictionary[int, int] = {}


## Connects process-lifetime multiplayer callbacks before a peer is published.
func _ready() -> void:
	multiplayer.connected_to_server.connect(_on_connected_to_server)
	multiplayer.connection_failed.connect(_on_connection_failed)
	multiplayer.server_disconnected.connect(_on_server_disconnected)
	multiplayer.peer_connected.connect(_on_peer_connected)
	multiplayer.peer_disconnected.connect(_on_peer_disconnected)


## Returns the fixed initial-game provider identifier.
func provider_id() -> StringName:
	return PROVIDER_ID


## Reports whether no native endpoint is currently owned.
func is_available() -> bool:
	return _peer == null


## Describes ENet's required four logical streams and payload ceilings.
func capabilities() -> Dictionary:
	return {
		"available": is_available(),
		"identity_assurance": &"NONE",
		"max_receive_packet_bytes": 16 * 1024,
		"route_diagnostics_available": false,
		"streams": [
			_stream(0, &"RELIABLE_ORDERED", &"DURABLE", 4096),
			_stream(1, &"RELIABLE_ORDERED", &"DURABLE", 16 * 1024),
			_stream(2, &"UNRELIABLE_ORDERED", &"REPLACEABLE_LOSSY", 1200),
			_stream(3, &"UNRELIABLE_ORDERED", &"REPLACEABLE_LOSSY", 1200),
		],
	}


## Parses a bounded IP address or DNS hostname into an adapter-generation target.
func parse_endpoint(address: String, port: int) -> Dictionary:
	var normalized: String = address.strip_edges().to_lower()
	if port < 1 or port > 65_535 or not _valid_address(normalized):
		return _failure(&"INVALID_ENDPOINT")

	return {
		"ok": true,
		"target": {
			"provider_id": PROVIDER_ID,
			"adapter_generation": _adapter_generation,
			"kind": &"TRANSPORT_READY",
			"local_handle": { "address": normalized, "port": port },
		},
	}


## Confirms callback identity against the active operation and adapter generation.
func is_current_connection_token(
	operation_id: int,
	connection_token: int,
	native_peer_id: int,
) -> bool:
	return (
		_peer != null
		and operation_id == _operation_id
		and connection_token == _token_by_peer.get(native_peer_id, -1)
	)


## Opens a bounded listen endpoint and applies the pinned-engine workaround first.
func open_host(operation_id: int, options: Dictionary) -> Dictionary:
	if not is_available():
		return _failure(&"BUSY")

	var port: Variant = options.get("port")
	var capacity: Variant = options.get("capacity")
	var bind_address: Variant = options.get("bind_address", "*")
	if (
		port is not int
		or port < 1
		or port > 65_535
		or capacity is not int
		or capacity < 1
		or capacity > 4
		or bind_address is not String
	):
		return _failure(&"INVALID_REQUEST")

	var candidate := ENetMultiplayerPeer.new()
	candidate.set_bind_ip(bind_address)
	# One bounded rejection slot lets SessionService return FULL explicitly.
	var max_native_clients: int = capacity - 1 + REJECTION_SLOT_COUNT
	var error: Error = candidate.create_server(port, max_native_clients, CHANNEL_COUNT)
	if error != OK:
		candidate.close()
		return _failure(&"SERVICE_UNAVAILABLE")

	# Godot c971 passes max_channels as incoming bandwidth during create_server.
	candidate.host.bandwidth_limit(0, 0)
	_workaround_applied = true
	_operation_id = operation_id
	_role = &"HOST"
	_host_capacity = capacity
	_peer = candidate
	peer_ready.emit(operation_id, candidate)
	return _success()


## Opens a client endpoint only from a current target created by this adapter.
func open_client(operation_id: int, target: Dictionary) -> Dictionary:
	if not is_available():
		return _failure(&"BUSY")
	if target.get("adapter_generation", -1) != _adapter_generation:
		return _failure(&"TARGET_EXPIRED")

	var handle: Variant = target.get("local_handle")
	if handle is not Dictionary:
		return _failure(&"INVALID_ENDPOINT")

	var address: Variant = handle.get("address")
	var port: Variant = handle.get("port")
	if (
		address is not String
		or port is not int
		or port < 1
		or port > 65_535
		or not _valid_address(address)
	):
		return _failure(&"INVALID_ENDPOINT")

	var candidate := ENetMultiplayerPeer.new()
	var error: Error = candidate.create_client(address, port, CHANNEL_COUNT)
	if error != OK:
		candidate.close()
		return _failure(&"CONNECT_FAILED")

	_operation_id = operation_id
	_role = &"CLIENT"
	_host_capacity = 0
	_workaround_applied = false
	_peer = candidate
	peer_ready.emit(operation_id, candidate)
	return _success()


## Releases native resources, expires old targets, and reports safe local reuse.
func close(operation_id: int) -> Dictionary:
	_adapter_generation += 1
	_next_connection_sequence = 1
	_operation_id = 0
	_role = &""
	_host_capacity = 0
	_workaround_applied = false
	_token_by_peer.clear()
	if _peer != null:
		_peer.close()
		_peer = null

	_emit_closed.call_deferred(operation_id)
	return _success()


## Releases an obsolete peer without changing the current adapter generation.
func dispose_obsolete(_operation_id: int, peer: MultiplayerPeer) -> void:
	peer.close()


## Reports whether the server workaround preceded publication for test evidence.
func bandwidth_workaround_applied() -> bool:
	return _workaround_applied


## Emits the client connection with a generation-scoped opaque token.
func _on_connected_to_server() -> void:
	if _peer == null or _role != &"CLIENT":
		return

	var connection_token: int = _allocate_connection_token(1)
	connected.emit(_operation_id, connection_token, 1)


## Normalizes a refused or unreachable native client attempt.
func _on_connection_failed() -> void:
	if _peer == null or _role != &"CLIENT":
		return

	failed.emit(_operation_id, _failure_record(&"CONNECT_FAILED", true))


## Ends a client session when its authoritative host disappears.
func _on_server_disconnected() -> void:
	if _peer == null or _role != &"CLIENT":
		return

	var connection_token: int = _token_by_peer.get(1, -1)
	disconnected.emit(
		_operation_id,
		connection_token,
		1,
		_failure_record(&"HOST_LOST", true),
	)
	_token_by_peer.erase(1)


## Publishes one host-observed native peer without assigning gameplay identity.
func _on_peer_connected(peer_id: int) -> void:
	if _peer == null or _role != &"HOST":
		return

	var connection_token: int = _allocate_connection_token(peer_id)
	connected.emit(_operation_id, connection_token, peer_id)


## Publishes host-side peer loss so SessionService can release its reservation.
func _on_peer_disconnected(peer_id: int) -> void:
	if _peer == null or _role != &"HOST":
		return

	var connection_token: int = _token_by_peer.get(peer_id, -1)
	disconnected.emit(
		_operation_id,
		connection_token,
		peer_id,
		_failure_record(&"CONNECT_FAILED", true),
	)
	_token_by_peer.erase(peer_id)


## Defers close completion so SessionService finishes its synchronous close call first.
func _emit_closed(operation_id: int) -> void:
	closed.emit(operation_id, { "reuse_status": REUSE_SAFE })


## Allocates a token that cannot alias peer-ID reuse or another adapter generation.
func _allocate_connection_token(peer_id: int) -> int:
	var connection_token: int = (_adapter_generation << 32) | _next_connection_sequence
	_next_connection_sequence += 1
	_token_by_peer[peer_id] = connection_token
	return connection_token


## Validates bounded IP and DNS text without resolving or allocating native work.
func _valid_address(address: String) -> bool:
	if address.is_empty() or address.to_utf8_buffer().size() > MAX_ADDRESS_BYTES:
		return false
	if address.is_valid_ip_address():
		return true

	# FQDN trailing dots are rejected so every accepted target has one canonical spelling.
	var labels: PackedStringArray = address.split(".", true)
	if labels.is_empty():
		return false
	for label: String in labels:
		if not _valid_host_label(label):
			return false

	return true


## Accepts one DNS label with alphanumeric ends and internal hyphens only.
func _valid_host_label(label: String) -> bool:
	if (
		label.is_empty()
		or label.to_utf8_buffer().size() > MAX_HOST_LABEL_BYTES
		or label.begins_with("-")
		or label.ends_with("-")
	):
		return false

	for character: String in label:
		var code: int = character.unicode_at(0)
		var is_digit: bool = code >= 48 and code <= 57
		var is_lower: bool = code >= 97 and code <= 122
		if not is_digit and not is_lower and character != "-":
			return false

	return true


## Builds one normalized local transport failure.
func _failure_record(code: StringName, retryable: bool) -> Dictionary:
	return { "code": code, "retryable": retryable }


## Builds one fixed logical stream capability row.
func _stream(
	channel: int,
	delivery: StringName,
	queue_policy: StringName,
	max_payload_bytes: int,
) -> Dictionary:
	return {
		"channel": channel,
		"delivery": delivery,
		"queue_policy": queue_policy,
		"max_logical_payload_bytes": max_payload_bytes,
	}
