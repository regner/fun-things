extends GutTest
## Verifies generation fences and host-authorized sequence-window recovery.


## Clears accepted old-life work before rejecting a delayed prior-generation command.
func test_generation_advance_clears_queue_and_rejects_delayed_input() -> void:
	var authority := FootInputAuthority.new()
	authority.grant(2, 1)
	assert_true(authority.offer(2, 1, _decoded(1, 1, 1), 0).accepted)
	assert_eq(authority.queue(2).size(), 1)

	assert_false(authority.offer(2, 2, _decoded(2, 1, 1), 1).accepted)
	assert_eq(authority.queue(2).size(), 0)
	assert_true(authority.offer(2, 2, _decoded(1, 2, 1), 2).accepted)
	assert_eq(authority.queue(2).consume(2).acknowledgement, 1)


## Advances an epoch only after overflow and resumes from sequence one.
func test_freshness_overflow_authorizes_bounded_epoch_recovery() -> void:
	var authority := FootInputAuthority.new()
	authority.grant(2, 1)
	var outside: int = FootInputQueue.SEQUENCE_FRESHNESS_WINDOW + 1
	assert_false(authority.offer(2, 1, _decoded(outside, 1, 1), 0).accepted)

	assert_eq(authority.recover(2, 1, 1), 2)
	assert_eq(authority.recover(2, 1, 1), 2)
	assert_true(authority.offer(2, 1, _decoded(1, 1, 2), 1).accepted)
	assert_eq(authority.queue(2).consume(1).acknowledgement, 1)


## Round-trips one command through the exact fixed input envelope.
func _decoded(sequence: int, generation: int, input_epoch: int) -> Dictionary:
	var encoded: Dictionary = FootCommandCodec.encode(
		FootCommand.new(sequence, sequence, Vector2.RIGHT, 0.0, false, false),
		generation,
		input_epoch,
	)
	assert_true(encoded.ok)
	return FootCommandCodec.decode(encoded.packet)
