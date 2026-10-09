class_name PeerIdentityRegistry
extends RefCounted
## Allocates session-scoped participants and resolves remote identity from native senders.

const MAX_PARTICIPANTS: int = 4

var _next_participant_id: int = 1
var _participant_by_peer: Dictionary[int, int] = {}


## Admits one native peer with a fresh participant identity owned by this registry.
func admit_peer(native_peer_id: int) -> Dictionary:
	if native_peer_id <= 0:
		return _failure(&"INVALID_SENDER")
	if _participant_by_peer.has(native_peer_id):
		return {
			"ok": true,
			"participant_id": _participant_by_peer[native_peer_id],
			"existing": true,
		}
	if _participant_by_peer.size() >= MAX_PARTICIPANTS:
		return _failure(&"FULL")

	var participant_id: int = _next_participant_id
	_next_participant_id += 1
	_participant_by_peer[native_peer_id] = participant_id
	return { "ok": true, "participant_id": participant_id, "existing": false }


## Resolves only the native sender captured at the receive callback.
func resolve_sender(native_peer_id: int) -> int:
	return _participant_by_peer.get(native_peer_id, 0)


## Retires a mapping so native peer-ID reuse cannot inherit admission.
func remove_peer(native_peer_id: int) -> void:
	_participant_by_peer.erase(native_peer_id)


## Clears mappings while keeping participant allocation monotonic for this session.
func clear_connections() -> void:
	_participant_by_peer.clear()


## Reports the bounded number of currently mapped peers.
func size() -> int:
	return _participant_by_peer.size()


## Returns a normalized local failure without exposing a claimed payload identity.
func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
