class_name ReplicationTransport
extends RefCounted
## Defines the narrow admission output seam implemented by network and fake transports.


## Sends immutable numbered baseline chunks and their validated transaction metadata.
func send_baseline(
	_native_peer_id: int,
	_metadata: Dictionary,
	_packets: Array[PackedByteArray],
) -> bool:
	return false


## Sends one reliable durable record on the same ordered state stream.
func send_durable(_native_peer_id: int, _packet: PackedByteArray) -> bool:
	return false


## Sends the newest complete lifecycle snapshot before its matching handoff marker.
func send_lifecycle(_native_peer_id: int, _lifecycle_revision: int) -> bool:
	return false


## Sends the reliable cut marker after journal and lifecycle state through both revisions.
func send_handoff(
	_native_peer_id: int,
	_baseline_id: int,
	_commit_revision: int,
	_lifecycle_revision: int,
) -> bool:
	return false


## Opens input only after the current durable and lifecycle handoff acknowledgement.
func send_grant(
	_native_peer_id: int,
	_baseline_id: int,
	_commit_revision: int,
	_lifecycle_revision: int,
) -> bool:
	return false


## Supersedes one old-match transfer before a reset baseline begins.
func send_reset_begin(_native_peer_id: int, _match_revision: int) -> bool:
	return false


## Ends one overflowing, timed-out, or malformed attempt without affecting other peers.
func abort_admission(_native_peer_id: int, _failure_code: StringName) -> void:
	pass
