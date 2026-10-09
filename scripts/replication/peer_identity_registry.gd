class_name PeerIdentityRegistry
extends RefCounted
## Mirrors Session-owned peer mappings and resolves remote identity from native senders.

const MAX_PARTICIPANTS: int = 4

var _participant_by_peer: Dictionary[int, int] = {}
var _retired_participants: Dictionary[int, bool] = {}


## Binds one Session-allocated participant to its current native sender.
func bind_peer(native_peer_id: int, participant_id: int) -> Dictionary:
	if native_peer_id <= 0 or participant_id <= 0:
		return _failure(&"INVALID_SENDER")
	if _retired_participants.has(participant_id):
		return _failure(&"STALE_PARTICIPANT")
	if _participant_by_peer.has(native_peer_id):
		return (
			{ "ok": true, "existing": true }
			if int(_participant_by_peer[native_peer_id]) == participant_id
			else _failure(&"IDENTITY_CONFLICT")
		)
	if participant_id in _participant_by_peer.values():
		return _failure(&"IDENTITY_CONFLICT")
	if _participant_by_peer.size() >= MAX_PARTICIPANTS:
		return _failure(&"FULL")

	_participant_by_peer[native_peer_id] = participant_id
	return { "ok": true, "existing": false }


## Resolves only the native sender captured at the receive callback.
func resolve_sender(native_peer_id: int) -> int:
	return _participant_by_peer.get(native_peer_id, 0)


## Retires a mapping so peer-ID reuse cannot inherit its old participant.
func remove_peer(native_peer_id: int) -> void:
	if _participant_by_peer.has(native_peer_id):
		_retired_participants[_participant_by_peer[native_peer_id]] = true
	_participant_by_peer.erase(native_peer_id)


## Clears current mappings while retaining retired participant fences for this session.
func clear_connections() -> void:
	for participant_id: int in _participant_by_peer.values():
		_retired_participants[participant_id] = true
	_participant_by_peer.clear()


## Reports the bounded number of currently mapped peers.
func size() -> int:
	return _participant_by_peer.size()


## Returns a normalized local failure without exposing a claimed payload identity.
func _failure(code: StringName) -> Dictionary:
	return { "ok": false, "failure": { "code": code } }
