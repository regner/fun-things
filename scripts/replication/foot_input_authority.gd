class_name FootInputAuthority
extends RefCounted
## Owns host command queues, input epochs, and bounded sequence recovery.

const RECOVERY_COOLDOWN_MSEC: int = 1_000

var _queues: Dictionary[int, FootInputQueue] = {}
var _epoch_by_participant: Dictionary[int, int] = {}
var _recovery_authorized: Dictionary[int, bool] = {}
var _last_recovery_attempt_msec: Dictionary[int, int] = {}


## Opens one admitted participant at sequence one and input epoch one.
func grant(participant_id: int) -> void:
	var queue: FootInputQueue = _queues.get(participant_id)
	if queue == null:
		queue = FootInputQueue.new()
		_queues[participant_id] = queue
	else:
		queue.clear()
	_epoch_by_participant[participant_id] = 1
	_recovery_authorized[participant_id] = false
	_last_recovery_attempt_msec[participant_id] = -RECOVERY_COOLDOWN_MSEC


## Reports whether a seat transfer can advance one admitted participant without wrapping.
func can_rebind(participant_id: int) -> bool:
	return (
		_queues.has(participant_id)
		and int(_epoch_by_participant.get(participant_id, 0))
		< FootCommandCodec.MAX_INPUT_EPOCH
	)


## Advances one seat-transfer epoch and clears all pre-transfer held foot intent.
func rebind(participant_id: int) -> int:
	if not can_rebind(participant_id):
		return 0
	var epoch: int = int(_epoch_by_participant[participant_id]) + 1
	_epoch_by_participant[participant_id] = epoch
	_recovery_authorized[participant_id] = false
	var queue: FootInputQueue = _queues[participant_id]
	queue.clear()
	return epoch


## Returns the current command epoch for reliable control-transfer hydration.
func input_epoch(participant_id: int) -> int:
	return int(_epoch_by_participant.get(participant_id, 0))


## Removes all retained input state for one departing participant.
func remove(participant_id: int) -> void:
	_queues.erase(participant_id)
	_epoch_by_participant.erase(participant_id)
	_recovery_authorized.erase(participant_id)
	_last_recovery_attempt_msec.erase(participant_id)


## Clears every queue and recovery fence at an authoritative match reset.
func clear() -> void:
	_queues.clear()
	_epoch_by_participant.clear()
	_recovery_authorized.clear()
	_last_recovery_attempt_msec.clear()


## Offers one decoded command and records host evidence when its sequence is out of window.
func offer(participant_id: int, decoded: Dictionary, receipt_msec: int) -> Dictionary:
	var queue: FootInputQueue = _queues.get(participant_id)
	if (
		queue == null
		or int(decoded.input_epoch) != int(_epoch_by_participant.get(participant_id, 0))
	):
		return { "accepted": false, "failure": &"STALE_COMMAND_CONTEXT" }
	var command: FootCommand = decoded.command
	if queue.sequence_exceeds_freshness_window(command.sequence):
		_recovery_authorized[participant_id] = true
		return { "accepted": false, "failure": &"SEQUENCE_WINDOW" }
	return { "accepted": queue.offer(command, receipt_msec) }


## Advances one proven epoch subject to a request cooldown and a no-wrap bound.
func recover(
	participant_id: int,
	requested_epoch: int,
	probe_packet: PackedByteArray,
	now_msec: int,
) -> int:
	var queue: FootInputQueue = _queues.get(participant_id)
	if queue == null or now_msec < 0:
		return 0
	var current_epoch: int = int(_epoch_by_participant.get(participant_id, 0))
	var last_attempt_msec: int = int(
		_last_recovery_attempt_msec.get(participant_id, -RECOVERY_COOLDOWN_MSEC)
	)
	if (
		requested_epoch != current_epoch
		or now_msec - last_attempt_msec < RECOVERY_COOLDOWN_MSEC
		or current_epoch >= FootCommandCodec.MAX_INPUT_EPOCH
	):
		return 0
	_last_recovery_attempt_msec[participant_id] = now_msec
	if probe_packet.size() != FootCommandCodec.PACKET_BYTES:
		return 0
	var decoded: Dictionary = FootCommandCodec.decode(probe_packet)
	if not decoded.get("ok", false) or int(decoded.input_epoch) != current_epoch:
		return 0
	var probe: FootCommand = decoded.command
	if (
		not bool(_recovery_authorized.get(participant_id, false))
		and not queue.sequence_exceeds_freshness_window(probe.sequence)
	):
		return 0

	current_epoch += 1
	_epoch_by_participant[participant_id] = current_epoch
	_recovery_authorized[participant_id] = false
	queue.clear()
	return current_epoch


## Returns the current queue after command-envelope admission.
func queue(participant_id: int) -> FootInputQueue:
	return _queues.get(participant_id)


## Reports one consumed-or-superseded watermark for diagnostics and replication.
func acknowledgement(participant_id: int) -> int:
	var input_queue: FootInputQueue = _queues.get(participant_id)
	return 0 if input_queue == null else input_queue.acknowledgement()
