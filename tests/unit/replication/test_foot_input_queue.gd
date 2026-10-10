extends GutTest
## Verifies ordered bounded host input selection, watermark timing, and expiry.


## Keeps receipt separate from the consumed-or-superseded acknowledgement watermark.
func test_receipt_does_not_acknowledge_until_authority_consumes() -> void:
	var queue := FootInputQueue.new()
	assert_true(queue.offer(_command(1, 10), 100))
	assert_eq(queue.acknowledgement(), 0)

	var decision: Dictionary = queue.consume(100)
	assert_eq((decision.command as FootCommand).sequence, 1)
	assert_eq(decision.acknowledgement, 1)
	assert_eq(queue.acknowledgement(), 1)


## Supersedes old distance lag and still consumes only one selected frame this tick.
func test_distance_bound_selects_oldest_frame_within_three_ticks_of_newest() -> void:
	var queue := FootInputQueue.new()
	for sequence: int in range(1, 7):
		assert_true(queue.offer(_command(sequence, sequence + 20), 0))

	var decision: Dictionary = queue.consume(1)
	assert_eq((decision.command as FootCommand).sequence, 3)
	assert_true(decision.superseded)
	assert_eq(decision.acknowledgement, 3)
	assert_eq(queue.size(), 3)


## Retains at most eight pending frames independently from the freshness window.
func test_queue_capacity_rejects_ninth_frame_without_acknowledging_it() -> void:
	var queue := FootInputQueue.new()
	for sequence: int in range(1, FootInputQueue.MAX_QUEUED_FRAMES + 1):
		assert_true(queue.offer(_command(sequence, sequence), 0))

	assert_false(queue.offer(_command(9, 9), 0))
	assert_eq(queue.size(), FootInputQueue.MAX_QUEUED_FRAMES)
	assert_eq(queue.acknowledgement(), 0)


## Expires all pending held intent to neutral on the first post-boundary host step.
func test_expiry_supersedes_pending_frames_and_advances_watermark() -> void:
	var queue := FootInputQueue.new()
	assert_true(queue.offer(_command(1, 1, Vector2.RIGHT), 10))
	assert_true(queue.offer(_command(2, 2, Vector2.RIGHT), 10))

	var before: Dictionary = queue.consume(10 + FootInputQueue.HELD_EXPIRY_MSEC)
	assert_not_null(before.command)
	assert_eq(before.acknowledgement, 1)
	var expired: Dictionary = queue.consume(11 + FootInputQueue.HELD_EXPIRY_MSEC)
	assert_null(expired.command)
	assert_true(expired.expired)
	assert_eq(expired.acknowledgement, 2)
	assert_eq(queue.size(), 0)


## Rejects inconsistent sequence-to-client-tick numbering and freshness jumps.
func test_numbering_and_freshness_window_are_bounded() -> void:
	var queue := FootInputQueue.new()
	assert_true(queue.offer(_command(1, 41), 0))
	assert_false(queue.offer(_command(2, 43), 0))
	assert_false(queue.offer(_command(FootInputQueue.SEQUENCE_FRESHNESS_WINDOW + 1, 161), 0))


## Recovers sequence one after an authorized epoch reset clears an exceeded window.
func test_clear_recovers_after_sequence_freshness_window_is_exceeded() -> void:
	var queue := FootInputQueue.new()
	var outside: int = FootInputQueue.SEQUENCE_FRESHNESS_WINDOW + 1
	assert_true(queue.sequence_exceeds_freshness_window(outside))
	assert_false(queue.offer(_command(outside, outside), 0))

	queue.clear()
	assert_true(queue.offer(_command(1, 1, Vector2.RIGHT), 1))
	var recovered: Dictionary = queue.consume(1)
	assert_eq((recovered.command as FootCommand).sequence, 1)
	assert_eq(recovered.acknowledgement, 1)


## Creates one complete immutable command for queue contract cases.
func _command(
	sequence: int,
	client_tick: int,
	move: Vector2 = Vector2.ZERO,
) -> FootCommand:
	return FootCommand.new(sequence, client_tick, move, 0.0, false, false)
