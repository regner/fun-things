extends GutTest
## Verifies bounded ordered vehicle input, supersession, and expiry acknowledgements.


## Selects only one current command per host tick and bounds queued work.
func test_queue_supersedes_old_lag_without_extra_simulation_steps() -> void:
	var queue := VehicleInputQueue.new()
	for sequence: int in range(1, 7):
		assert_true(queue.offer(_command(sequence), 100))

	var decision: Dictionary = queue.consume(100)
	assert_eq(decision.command.sequence, 6)
	assert_true(decision.superseded)
	assert_eq(queue.acknowledgement(), 6)
	assert_eq(queue.size(), 0)

	decision = queue.consume(101)
	assert_eq(decision.command.sequence, 6)
	assert_false(decision.superseded)
	assert_eq(queue.acknowledgement(), 6)


## Reuses the newest consumed held intent between lossy packet arrivals.
func test_consumed_command_holds_until_expiry() -> void:
	var queue := VehicleInputQueue.new()
	assert_true(queue.offer(_command(1), 100))
	assert_eq(queue.consume(100).command.sequence, 1)

	var held: Dictionary = queue.consume(100 + VehicleInputQueue.HELD_EXPIRY_MSEC)
	assert_eq(held.command.sequence, 1)
	assert_false(held.expired)
	var expired: Dictionary = queue.consume(
		100 + VehicleInputQueue.HELD_EXPIRY_MSEC + 1
	)
	assert_null(expired.command)
	assert_true(expired.expired)
	assert_eq(expired.acknowledgement, 1)


## Acknowledges expired intent exactly when neutral control replaces it.
func test_expiry_neutralizes_and_acknowledges_latest_command() -> void:
	var queue := VehicleInputQueue.new()
	assert_true(queue.offer(_command(1), 100))
	var decision: Dictionary = queue.consume(
		100 + VehicleInputQueue.HELD_EXPIRY_MSEC + 1
	)
	assert_null(decision.command)
	assert_true(decision.expired)
	assert_eq(queue.acknowledgement(), 1)
	assert_eq(queue.size(), 0)


## Rejects duplicates, inconsistent ticks, queue overflow, and sequence-window jumps.
func test_offer_rejects_unbounded_or_inconsistent_work() -> void:
	var queue := VehicleInputQueue.new()
	assert_true(queue.offer(_command(1), 0))
	assert_false(queue.offer(_command(1), 0))
	assert_false(
		queue.offer(DriveCommand.new(2, 4, 1.0, 0.0, 0.0, false), 0)
	)
	assert_true(
		queue.sequence_exceeds_freshness_window(
			VehicleInputQueue.SEQUENCE_FRESHNESS_WINDOW + 1
		)
	)


## Builds one valid command with matching client and sequence clocks.
func _command(sequence: int) -> DriveCommand:
	return DriveCommand.new(sequence, sequence, 1.0, 0.0, 0.0, false)
