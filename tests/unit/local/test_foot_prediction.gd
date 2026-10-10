extends GutTest
## Verifies bounded shared-rule foot prediction, reconciliation, and lifecycle clearing.

const PLAYER_SCENE: PackedScene = preload("res://scenes/entities/player.tscn")
const FIXED_DELTA: float = 1.0 / 60.0


## Restores authority and replays each unacknowledged command through ActorMotion.
func test_reconciliation_replays_unacknowledged_commands() -> void:
	var predicted: ActorMotion = _add_actor()
	var authority: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var prediction := FootPrediction.new()
	assert_true(prediction.bind_actor(predicted))
	prediction.update_context(5, 1, 1, 1, 1)

	for sequence: int in range(1, 4):
		var command: FootCommand = _command(sequence, Vector2.RIGHT)
		assert_true(prediction.predict(command, FIXED_DELTA))
		if sequence == 1:
			assert_true(authority.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
	var before: Dictionary = predicted.motion_state()
	var result: Dictionary = prediction.reconcile(authority.motion_state(), 1)

	assert_true(result.ok)
	assert_eq(result.replayed, 2)
	assert_eq(prediction.history_size(), 2)
	assert_almost_eq(predicted.global_position.x, float(before.position.x), 0.001)
	assert_eq(prediction.acknowledgement(), 1)
	assert_eq(prediction.last_authority_position(), authority.global_position)


## Tolerates the measured wire quantization without introducing a visual offset.
func test_quantization_error_does_not_start_visual_correction() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var prediction := FootPrediction.new()
	prediction.bind_actor(actor)
	prediction.update_context(7, 1, 1, 1, 1)
	prediction.predict(_command(1, Vector2.RIGHT), FIXED_DELTA)
	var authority: Dictionary = actor.motion_state()
	authority.position.x += 0.01

	var result: Dictionary = prediction.reconcile(authority, 1)
	var presentation: Node3D = actor.get_node("PresentationAnchor") as Node3D
	assert_true(result.ok)
	assert_lt(float(result.correction_metres), FootPrediction.WIRE_QUANTIZATION_TOLERANCE_METRES)
	assert_eq(presentation.transform, Transform3D.IDENTITY)


## Smooths bounded corrections on presentation while authority wins collision immediately.
func test_bounded_correction_preserves_then_decays_display_pose() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var prediction := FootPrediction.new()
	prediction.bind_actor(actor)
	prediction.update_context(8, 1, 1, 1, 1)
	prediction.predict(_command(1, Vector2.RIGHT), FIXED_DELTA)
	var displayed_before: Vector3 = (actor.get_node("PresentationAnchor") as Node3D).global_position
	var authority: Dictionary = actor.motion_state()
	authority.position.x -= 0.2

	var result: Dictionary = prediction.reconcile(authority, 1)
	var presentation: Node3D = actor.get_node("PresentationAnchor") as Node3D
	assert_true(result.ok)
	assert_almost_eq(float(result.correction_metres), 0.2, 0.001)
	assert_almost_eq(prediction.correction_p95_metres(), 0.2, 0.001)
	assert_almost_eq(presentation.global_position.x, displayed_before.x, 0.001)
	assert_almost_eq(actor.global_position.x, displayed_before.x - 0.2, 0.001)

	for _tick: int in range(7):
		prediction.tick_visual(FIXED_DELTA)
	assert_lt(presentation.global_position.distance_to(actor.global_position), 0.07)


## Snaps and clears replay when correction exceeds the documented large-error bound.
func test_large_correction_snaps_and_clears_history() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var prediction := FootPrediction.new()
	prediction.bind_actor(actor)
	prediction.update_context(9, 1, 1, 1, 1)
	prediction.predict(_command(1, Vector2.RIGHT), FIXED_DELTA)
	prediction.predict(_command(2, Vector2.RIGHT), FIXED_DELTA)
	var authority: Dictionary = actor.motion_state()
	authority.position.x -= FootPrediction.LARGE_CORRECTION_SNAP_METRES + 0.5

	var result: Dictionary = prediction.reconcile(authority, 1)
	assert_true(result.ok)
	assert_eq(prediction.history_size(), 0)
	assert_eq(
		(actor.get_node("PresentationAnchor") as Node3D).transform,
		Transform3D.IDENTITY,
	)


## Bounds history and reports an unreplayable prefix instead of inventing simulation.
func test_history_overflow_requires_authoritative_snap() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var prediction := FootPrediction.new()
	prediction.bind_actor(actor)
	prediction.update_context(10, 1, 1, 1, 1)
	for sequence: int in range(1, FootPrediction.HISTORY_CAPACITY + 2):
		assert_true(prediction.predict(_command(sequence, Vector2.RIGHT), FIXED_DELTA))

	assert_eq(prediction.history_size(), FootPrediction.HISTORY_CAPACITY)
	var authority: Dictionary = actor.motion_state()
	authority.position = Vector3.ZERO
	var result: Dictionary = prediction.reconcile(authority, 0)
	assert_true(result.ok)
	assert_true(result.history_exhausted)
	assert_eq(prediction.history_size(), 0)
	assert_eq(actor.global_position, Vector3.ZERO)


## Clears replay whenever generation, life, control, or collision context advances.
func test_generation_and_revision_changes_clear_history() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var prediction := FootPrediction.new()
	prediction.bind_actor(actor)
	prediction.update_context(11, 1, 1, 1, 1)
	prediction.predict(_command(1, Vector2.RIGHT), FIXED_DELTA)
	assert_eq(prediction.history_size(), 1)

	assert_true(prediction.update_context(11, 2, 1, 1, 1))
	assert_eq(prediction.history_size(), 0)
	prediction.predict(_command(1, Vector2.RIGHT), FIXED_DELTA)
	assert_true(prediction.update_context(11, 2, 2, 1, 1))
	assert_eq(prediction.history_size(), 0)


## Replays held action flags only through motion, which has no mutation or effect endpoint.
func test_replay_with_action_flags_changes_only_motion_state() -> void:
	var actor: ActorMotion = _add_actor()
	await get_tree().physics_frame
	var prediction := FootPrediction.new()
	prediction.bind_actor(actor)
	prediction.update_context(12, 1, 1, 1, 1)
	var command := FootCommand.new(1, 1, Vector2.RIGHT, 0.0, true, true)

	assert_true(prediction.predict(command, FIXED_DELTA))
	assert_gt(actor.global_position.x, 0.0)
	assert_eq(prediction.history_size(), 1)


## Instantiates the authored actor so correction uses the real presentation anchor.
func _add_actor() -> ActorMotion:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	add_child_autofree(actor)
	return actor


## Builds one complete deterministic movement-only command.
func _command(sequence: int, move: Vector2) -> FootCommand:
	return FootCommand.new(sequence, sequence, move, 0.0, false, false)
