extends GutTest
## Verifies recovery-epoch evidence, rate bounds, and sequence recovery.


## Clears accepted prior-epoch work before rejecting delayed input from that epoch.
func test_epoch_advance_clears_queue_and_rejects_delayed_input() -> void:
	var authority := FootInputAuthority.new()
	authority.grant(2)
	assert_true(authority.offer(2, _decoded(1, 1), 0).accepted)
	assert_eq(authority.queue(2).size(), 1)
	assert_false(authority.offer(2, _decoded(_outside_sequence(), 1), 1).accepted)

	assert_eq(authority.recover(2, 1, _packet(_outside_sequence(), 1), 1), 2)
	assert_eq(authority.queue(2).size(), 0)
	assert_false(authority.offer(2, _decoded(2, 1), 2).accepted)
	assert_true(authority.offer(2, _decoded(1, 2), 3).accepted)
	assert_eq(authority.queue(2).consume(3).acknowledgement, 1)


## Advances seat-transfer control and rejects every delayed pre-transfer foot packet.
func test_seat_transfer_rebind_clears_held_input_and_advances_epoch() -> void:
	var authority := FootInputAuthority.new()
	authority.grant(2)
	var stale: Dictionary = _decoded(1, 1)
	assert_true(authority.offer(2, stale, 0).accepted)
	assert_true(authority.can_rebind(2))
	assert_eq(authority.rebind(2), 2)
	assert_eq(authority.input_epoch(2), 2)
	assert_eq(authority.queue(2).size(), 0)
	assert_false(authority.offer(2, stale, 1).accepted)
	assert_true(authority.offer(2, _decoded(1, 2), 2).accepted)


## Refuses recovery without host evidence and rate-limits an authorized request burst.
func test_recovery_requires_window_evidence_and_rate_limits_burst() -> void:
	var authority := FootInputAuthority.new()
	authority.grant(2)
	assert_eq(authority.recover(2, 1, _packet(1, 1), 0), 0)
	assert_false(authority.offer(2, _decoded(_outside_sequence(), 1), 1).accepted)
	var cooldown: int = FootInputAuthority.RECOVERY_COOLDOWN_MSEC
	assert_eq(authority.recover(2, 1, _packet(_outside_sequence(), 1), cooldown), 2)

	assert_false(authority.offer(2, _decoded(_outside_sequence(), 2), cooldown + 1).accepted)
	for _attempt: int in range(16):
		assert_eq(
			authority.recover(2, 2, _packet(_outside_sequence(), 2), cooldown * 2 - 1),
			0,
		)
	assert_eq(
		authority.recover(2, 2, _packet(_outside_sequence(), 2), cooldown * 2), 3
	)
	assert_eq(authority.recover(2, 2, _packet(_outside_sequence(), 2), cooldown * 2), 0)


## Saturates the finite wire epoch instead of accepting a wrapped prior epoch.
func test_recovery_epoch_never_wraps() -> void:
	var authority := FootInputAuthority.new()
	authority.grant(2)
	var current_epoch: int = 1
	var now_msec: int = 0
	while current_epoch < FootCommandCodec.MAX_INPUT_EPOCH:
		assert_false(
			authority.offer(2, _decoded(_outside_sequence(), current_epoch), now_msec).accepted
		)
		var next_epoch: int = authority.recover(
			2, current_epoch, _packet(_outside_sequence(), current_epoch), now_msec
		)
		assert_eq(next_epoch, current_epoch + 1)
		current_epoch = next_epoch
		now_msec += FootInputAuthority.RECOVERY_COOLDOWN_MSEC

	assert_false(
		authority.offer(2, _decoded(_outside_sequence(), current_epoch), now_msec).accepted
	)
	assert_eq(
		authority.recover(
			2, current_epoch, _packet(_outside_sequence(), current_epoch), now_msec
		),
		0,
	)
	assert_false(authority.offer(2, _decoded(1, 1), now_msec).accepted)


## Returns the first sequence that only epoch recovery can make admissible.
func _outside_sequence() -> int:
	return FootInputQueue.SEQUENCE_FRESHNESS_WINDOW + 1


## Round-trips one command through the exact fixed input packet.
func _decoded(sequence: int, input_epoch: int) -> Dictionary:
	return FootCommandCodec.decode(_packet(sequence, input_epoch))


## Encodes one fixed recovery probe without copying production admission logic.
func _packet(sequence: int, input_epoch: int) -> PackedByteArray:
	var encoded: Dictionary = FootCommandCodec.encode(
		FootCommand.new(sequence, sequence, Vector2.RIGHT, 0.0, false, false),
		input_epoch,
	)
	assert_true(encoded.ok)
	return encoded.packet
