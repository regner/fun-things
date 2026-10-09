extends GutTest
## Verifies Courier clip routing and the read-only presentation boundary.

const FIXED_DELTA: float = 1.0 / 60.0
const PLAYER_SCENE: PackedScene = preload("res://scenes/entities/player.tscn")


## Selects five-metre run direction from world velocity relative to independent facing.
func test_layered_clip_selection_uses_relative_velocity() -> void:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	add_child_autofree(actor)
	await get_tree().process_frame
	var presentation: PlayerMotionPresentation = actor.get_node(
		"PresentationAnchor"
	) as PlayerMotionPresentation
	var lower: AnimationPlayer = actor.get_node(
		"PresentationAnchor/Visuals/Model/LowerBodyPlayer"
	) as AnimationPlayer
	var upper: AnimationPlayer = actor.get_node(
		"PresentationAnchor/Visuals/Model/UpperBodyPlayer"
	) as AnimationPlayer

	presentation.apply_motion(Vector3.RIGHT * 5.0, 0.0)
	assert_eq(lower.current_animation, &"run_right")
	assert_eq(upper.current_animation, &"pistol_hold")
	assert_true(is_equal_approx(lower.speed_scale, 1.0))

	presentation.apply_motion(Vector3.RIGHT * 5.0, -PI * 0.5)
	assert_eq(lower.current_animation, &"run")
	presentation.apply_motion(Vector3.ZERO, -PI * 0.5)
	assert_eq(lower.current_animation, &"idle")


## Retains the full-body death pose until presentation is explicitly returned alive.
func test_idle_and_death_states_use_delivered_clips() -> void:
	var actor: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	add_child_autofree(actor)
	await get_tree().process_frame
	var presentation: PlayerMotionPresentation = actor.get_node(
		"PresentationAnchor"
	) as PlayerMotionPresentation
	var full_body: AnimationPlayer = actor.get_node(
		"PresentationAnchor/Visuals/Model/AnimationPlayer"
	) as AnimationPlayer
	var lower: AnimationPlayer = actor.get_node(
		"PresentationAnchor/Visuals/Model/LowerBodyPlayer"
	) as AnimationPlayer

	presentation.apply_motion(Vector3.ZERO, 0.0)
	assert_eq(lower.current_animation, &"idle")
	presentation.set_dead(true)
	assert_eq(full_body.current_animation, &"player/death")
	presentation.apply_motion(Vector3.RIGHT * 5.0, 0.0)
	assert_eq(full_body.current_animation, &"player/death")
	presentation.set_dead(false)
	assert_eq(lower.current_animation, &"run_right")


## Produces identical motion when the optional presentation subtree is removed.
func test_presentation_removal_does_not_change_motion_state() -> void:
	var presented: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	var unpresented: ActorMotion = PLAYER_SCENE.instantiate() as ActorMotion
	var removed_presentation: Node = unpresented.get_node("PresentationAnchor")
	unpresented.remove_child(removed_presentation)
	removed_presentation.free()
	add_child_autofree(presented)
	add_child_autofree(unpresented)
	await get_tree().physics_frame
	var commands: Array[FootCommand] = [
		FootCommand.new(1, 1, Vector2.RIGHT, -PI * 0.5, false, false),
		FootCommand.new(2, 2, Vector2(0.0, -1.0), 0.4, false, false),
		FootCommand.new(3, 3, Vector2.ZERO, -1.2, false, false),
	]

	for command: FootCommand in commands:
		assert_true(presented.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))
		assert_true(unpresented.step(command, FIXED_DELTA, ActorMotion.StepMode.AUTHORITY))

	assert_eq(presented.motion_state(), unpresented.motion_state())
