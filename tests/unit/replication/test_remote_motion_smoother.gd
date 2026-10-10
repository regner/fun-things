extends GutTest
## Verifies tunable remote extrapolation, hold, authority blending, and invalidation.


## Extrapolates for the configured window and then holds the bounded display pose.
func test_extrapolates_then_holds_after_bound() -> void:
	var smoother := RemoteMotionSmoother.new(125, 100)
	assert_true(smoother.push(_state(Vector3.ZERO, Vector3(4.0, 0.0, 0.0)), 1000))

	var extrapolated: Dictionary = smoother.sample(1100)
	var held: Dictionary = smoother.sample(1400)
	assert_almost_eq(float(extrapolated.position.x), 0.4, 0.001)
	assert_almost_eq(float(held.position.x), 0.5, 0.001)


## Starts a new authority blend at the already displayed pose without a receipt snap.
func test_new_authority_blends_continuously_from_current_display() -> void:
	var smoother := RemoteMotionSmoother.new(125, 100)
	smoother.push(_state(Vector3.ZERO, Vector3(2.0, 0.0, 0.0)), 0)
	var before: Dictionary = smoother.sample(125)
	assert_true(smoother.push(_state(Vector3(0.1, 0.0, 0.0), Vector3(2.0, 0.0, 0.0)), 125))
	var at_receipt: Dictionary = smoother.sample(125)
	var blended: Dictionary = smoother.sample(175)

	assert_eq(at_receipt.position, before.position)
	assert_lt(float(blended.position.x), float(at_receipt.position.x))
	assert_gt(float(blended.position.x), 0.19)


## Clears extrapolated history when an entity generation dependency changes.
func test_generation_change_clears_remote_history() -> void:
	var smoother := RemoteMotionSmoother.new()
	assert_true(smoother.update_context(7, 1, 1, 1, 1))
	smoother.push(_state(Vector3.ONE, Vector3.RIGHT), 0)
	assert_false(smoother.sample(10).is_empty())

	assert_true(smoother.update_context(7, 2, 1, 1, 1))
	assert_true(smoother.sample(10).is_empty())


## Builds one complete finite authoritative presentation sample.
func _state(position: Vector3, velocity: Vector3, yaw: float = 0.0) -> Dictionary:
	return {
		"position": position,
		"velocity": velocity,
		"aim_yaw": yaw,
	}
