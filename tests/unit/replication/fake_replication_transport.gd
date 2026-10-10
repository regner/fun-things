class_name FakeReplicationTransport
extends ReplicationTransport
## Records admission output ordering without a native peer or alternate replication rules.

var events: Array[Dictionary] = []
var fail_next_send: bool = false
var fail_durable_peer: int = 0
var abort_callback: Callable


## Records baseline metadata and immutable chunks as one transport operation.
func send_baseline(
	native_peer_id: int,
	metadata: Dictionary,
	packets: Array[PackedByteArray],
) -> bool:
	if _consume_failure():
		return false

	events.append(
		{
			"kind": &"baseline",
			"peer": native_peer_id,
			"metadata": metadata.duplicate(true),
			"packets": packets.duplicate(true),
		}
	)
	return true


## Records one reliable durable packet.
func send_durable(native_peer_id: int, packet: PackedByteArray) -> bool:
	if native_peer_id == fail_durable_peer:
		fail_durable_peer = 0
		return false
	if _consume_failure():
		return false

	events.append({ "kind": &"durable", "peer": native_peer_id, "packet": packet.duplicate() })
	return true


## Records the reliable handoff marker after its journal.
func send_handoff(native_peer_id: int, baseline_id: int, commit_revision: int) -> bool:
	if _consume_failure():
		return false

	events.append(
		{
			"kind": &"handoff",
			"peer": native_peer_id,
			"baseline_id": baseline_id,
			"revision": commit_revision,
		}
	)
	return true


## Records the command grant that follows handoff acknowledgement.
func send_grant(native_peer_id: int, baseline_id: int, commit_revision: int) -> bool:
	if _consume_failure():
		return false

	events.append(
		{
			"kind": &"grant",
			"peer": native_peer_id,
			"baseline_id": baseline_id,
			"revision": commit_revision,
		}
	)
	return true


## Records one peer-local failure and no grant.
func abort_admission(native_peer_id: int, failure_code: StringName) -> void:
	events.append({ "kind": &"abort", "peer": native_peer_id, "code": failure_code })
	if abort_callback.is_valid():
		abort_callback.call(native_peer_id)


## Fails exactly one requested send to exercise bounded cleanup.
func _consume_failure() -> bool:
	if not fail_next_send:
		return false

	fail_next_send = false
	return true
