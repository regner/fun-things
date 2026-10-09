class_name SessionTransport
extends Node
## Provider-neutral transport boundary owned by one Boot-composed session provider.

signal peer_ready(operation_id: int, peer: MultiplayerPeer)
signal connected(operation_id: int, connection_token: int, native_peer_id: int)
signal disconnected(
	operation_id: int,
	connection_token: int,
	native_peer_id: int,
	failure: Dictionary,
)
signal failed(operation_id: int, failure: Dictionary)
signal closed(operation_id: int, result: Dictionary)

const REUSE_SAFE: StringName = &"SAFE"
const REUSE_UNAVAILABLE: StringName = &"UNAVAILABLE"


## Returns the stable provider identifier registered with SessionService.
func provider_id() -> StringName:
	return &""


## Reports whether this transport can accept a new operation.
func is_available() -> bool:
	return false


## Describes the fixed logical stream profile implemented by the transport.
func capabilities() -> Dictionary:
	return { "available": false, "streams": [] }


## Parses provider-owned endpoint text into an opaque current-generation target.
func parse_endpoint(_address: String, _port: int) -> Dictionary:
	return _failure(&"INVALID_ENDPOINT")


## Confirms that a callback token belongs to the adapter's current native generation.
func is_current_connection_token(
	_operation_id: int,
	_connection_token: int,
	_native_peer_id: int,
) -> bool:
	return false


## Opens a host endpoint for one correlated session operation.
func open_host(_operation_id: int, _options: Dictionary) -> Dictionary:
	return _failure(&"SERVICE_UNAVAILABLE")


## Opens a client endpoint from an opaque adapter-owned target.
func open_client(_operation_id: int, _target: Dictionary) -> Dictionary:
	return _failure(&"SERVICE_UNAVAILABLE")


## Invalidates targets and releases local resources for one close operation.
func close(_operation_id: int) -> Dictionary:
	return _success()


## Releases a peer produced by an obsolete provider callback.
func dispose_obsolete(_operation_id: int, peer: MultiplayerPeer) -> void:
	peer.close()


## Builds a successful synchronous adapter result.
func _success() -> Dictionary:
	return { "ok": true }


## Builds a rejected synchronous adapter result without accepting an operation.
func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code, "retryable": true } }
