extends SceneTree
## Measure imported run cadence and contact drift through the production presentation API.

const ACTOR: PackedScene = preload("res://scenes/prefabs/player_character/coral_courier.tscn")
const SPEED_MPS: float = 5.0
const STANCE_INTERVALS: int = 4


## Wait until the tree can initialize the source-linked visual wrapper.
func _initialize() -> void:
	_measure.call_deferred()


## Report all directional rates and independent world-space foot velocity residuals.
func _measure() -> void:
	var actor: PlayerCharacterVisual = ACTOR.instantiate() as PlayerCharacterVisual
	root.add_child(actor)
	var directions: Dictionary[StringName, Vector3] = {
		&"run": Vector3.FORWARD, &"run_back": Vector3.BACK,
		&"run_left": Vector3.LEFT, &"run_right": Vector3.RIGHT,
	}
	var report: Dictionary = {}
	for clip: StringName in directions:
		assert(actor.play_layered(clip, &"pistol_hold", SPEED_MPS))
		report[clip] = _measure_contact(actor, directions[clip])
	print("RUN_MEASUREMENTS ", JSON.stringify(report))
	actor.free()
	quit()


## Measure the four baked support intervals independently of the calibration endpoints.
func _measure_contact(actor: PlayerCharacterVisual, direction: Vector3) -> Dictionary:
	var lower: AnimationPlayer = actor.get_node("LowerBodyPlayer") as AnimationPlayer
	var skeleton: Skeleton3D = actor.get_skeleton()
	var foot: int = skeleton.find_bone(&"foot_r")
	var animation: Animation = lower.get_animation(lower.current_animation)
	var stance: Vector2 = animation.get_meta(&"stance_right_seconds")
	var seconds: float = (stance.y - stance.x) / STANCE_INTERVALS / lower.speed_scale
	var maximum_drift: float = 0.0
	lower.seek(stance.x, true)
	var start: Vector3 = skeleton.get_bone_global_pose(foot).origin
	var previous: Vector3 = start
	for interval: int in range(1, STANCE_INTERVALS + 1):
		lower.seek(lerpf(stance.x, stance.y, float(interval) / STANCE_INTERVALS), true)
		var current: Vector3 = skeleton.get_bone_global_pose(foot).origin
		maximum_drift = maxf(
			maximum_drift, (direction * SPEED_MPS + (current - previous) / seconds).length()
		)
		previous = current
	assert(lower.speed_scale >= 0.85 and lower.speed_scale <= 1.2)
	assert(maximum_drift < 0.05)
	return {
		"cycle_seconds": animation.length,
		"stance_seconds": stance.y - stance.x,
		"contact_travel_m": start.distance_to(previous),
		"derived_playback_rate_at_5_mps": lower.speed_scale,
		"maximum_baked_stance_world_velocity_mps": maximum_drift,
	}
