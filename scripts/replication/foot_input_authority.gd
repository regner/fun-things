class_name FootInputAuthority
extends RefCounted
## Owns generation-fenced host queues, input epochs, and bounded sequence recovery.

var _queues: Dictionary[int, FootInputQueue] = {}
var _epoch_by_participant: Dictionary[int, int] = {}
var _generation_by_participant: Dictionary[int, int] = {}


## Opens one admitted generation at sequence one and input epoch one.
func grant(participant_id: int, generation: int) -> void:
	var queue: FootInputQueue = _queues.get(participant_id)
	if queue == null:
		queue = FootInputQueue.new()
		_queues[participant_id] = queue
	else:
		queue.clear()
	_epoch_by_participant[participant_id] = 1
	_generation_by_participant[participant_id] = generation


## Removes all retained input state for one departing participant.
func remove(participant_id: int) -> void:
	_queues.erase(participant_id)
	_epoch_by_participant.erase(participant_id)
	_generation_by_participant.erase(participant_id)


## Clears queued old-life intent whenever the authoritative generation advances.
func synchronize(participant_id: int, generation: int) -> bool:
	if generation <= 0:
		return false
	if int(_generation_by_participant.get(participant_id, 0)) == generation:
		return true
	grant(participant_id, generation)
	return true


## Offers one decoded command only when its generation and epoch match authority.
func offer(
	participant_id: int,
	generation: int,
	decoded: Dictionary,
	receipt_msec: int,
) -> Dictionary:
	if not synchronize(participant_id, generation):
		return { "accepted": false, "failure": &"STALE_COMMAND_CONTEXT" }
	if (
		int(decoded.generation) != generation
		or int(decoded.input_epoch) != int(_epoch_by_participant.get(participant_id, 0))
	):
		return { "accepted": false, "failure": &"STALE_COMMAND_CONTEXT" }
	var command: FootCommand = decoded.command
	var queue: FootInputQueue = _queues[participant_id]
	return { "accepted": queue.offer(command, receipt_msec) }


## Idempotently authorizes one participant-local epoch reset for the current generation.
func recover(participant_id: int, generation: int, requested_epoch: int) -> int:
	if not synchronize(participant_id, generation):
		return 0
	var current_epoch: int = int(_epoch_by_participant.get(participant_id, 0))
	if requested_epoch == current_epoch:
		current_epoch = (current_epoch % FootCommandCodec.MAX_INPUT_EPOCH) + 1
		_epoch_by_participant[participant_id] = current_epoch
		(_queues[participant_id] as FootInputQueue).clear()
	return current_epoch


## Returns the current queue after synchronization by the lifecycle owner.
func queue(participant_id: int) -> FootInputQueue:
	return _queues.get(participant_id)


## Reports one consumed-or-superseded watermark for diagnostics and replication.
func acknowledgement(participant_id: int) -> int:
	var input_queue: FootInputQueue = _queues.get(participant_id)
	return 0 if input_queue == null else input_queue.acknowledgement()
