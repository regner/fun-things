class_name FootInputAuthority
extends RefCounted
## Owns host command queues, input epochs, and bounded sequence recovery.

var _queues: Dictionary[int, FootInputQueue] = {}
var _epoch_by_participant: Dictionary[int, int] = {}


## Opens one admitted participant at sequence one and input epoch one.
func grant(participant_id: int) -> void:
	var queue: FootInputQueue = _queues.get(participant_id)
	if queue == null:
		queue = FootInputQueue.new()
		_queues[participant_id] = queue
	else:
		queue.clear()
	_epoch_by_participant[participant_id] = 1


## Removes all retained input state for one departing participant.
func remove(participant_id: int) -> void:
	_queues.erase(participant_id)
	_epoch_by_participant.erase(participant_id)


## Offers one decoded command only when its recovery epoch matches authority.
func offer(participant_id: int, decoded: Dictionary, receipt_msec: int) -> Dictionary:
	var queue: FootInputQueue = _queues.get(participant_id)
	if (
		queue == null
		or int(decoded.input_epoch) != int(_epoch_by_participant.get(participant_id, 0))
	):
		return { "accepted": false, "failure": &"STALE_COMMAND_CONTEXT" }
	var command: FootCommand = decoded.command
	return { "accepted": queue.offer(command, receipt_msec) }


## Idempotently authorizes one participant-local epoch reset.
func recover(participant_id: int, requested_epoch: int) -> int:
	var queue: FootInputQueue = _queues.get(participant_id)
	if queue == null:
		return 0
	var current_epoch: int = int(_epoch_by_participant.get(participant_id, 0))
	if requested_epoch == current_epoch:
		current_epoch = (current_epoch % FootCommandCodec.MAX_INPUT_EPOCH) + 1
		_epoch_by_participant[participant_id] = current_epoch
		queue.clear()
	return current_epoch


## Returns the current queue after command-envelope admission.
func queue(participant_id: int) -> FootInputQueue:
	return _queues.get(participant_id)


## Reports one consumed-or-superseded watermark for diagnostics and replication.
func acknowledgement(participant_id: int) -> int:
	var input_queue: FootInputQueue = _queues.get(participant_id)
	return 0 if input_queue == null else input_queue.acknowledgement()
