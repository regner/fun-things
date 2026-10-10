class_name PlayerMotionPresentation
extends Node3D
## Selects Coral Courier animation from motion state without writing simulation.

const MOVING_SPEED_EPSILON_MPS: float = 0.05
const FULL_STRIDE_SPEED_MPS: float = 5.0
const IDLE_CLIP: StringName = &"idle"
const DEFAULT_UPPER_BODY_CLIP: StringName = &"pistol_hold"

var _dead: bool = false
var _latest_velocity: Vector3 = Vector3.ZERO
var _latest_facing_yaw: float = 0.0

@onready var _visual: PlayerCharacterVisual = $Visuals/Model as PlayerCharacterVisual


## Updates lower-body locomotion relative to the actor's independent facing.
func apply_motion(world_velocity: Vector3, facing_yaw: float) -> void:
	_latest_velocity = world_velocity
	_latest_facing_yaw = facing_yaw
	if _dead:
		return

	var planar_speed: float = Vector2(world_velocity.x, world_velocity.z).length()
	var clip: StringName = _locomotion_clip(world_velocity, facing_yaw)
	var playback_speed: float = 0.0 if clip == IDLE_CLIP else planar_speed
	_visual.play_layered(clip, DEFAULT_UPPER_BODY_CLIP, playback_speed)


## Selects or clears the retained full-body death pose without changing motion state.
func set_dead(dead: bool) -> void:
	if _dead == dead:
		return

	_dead = dead
	if dead:
		_visual.play_clip(&"death")
	else:
		apply_motion(_latest_velocity, _latest_facing_yaw)


## Maps planar movement into the nearest authored forward/back/left/right run clip.
func _locomotion_clip(world_velocity: Vector3, facing_yaw: float) -> StringName:
	var planar := Vector3(world_velocity.x, 0.0, world_velocity.z)
	if planar.length() <= MOVING_SPEED_EPSILON_MPS:
		return IDLE_CLIP

	var gait: String = (
		"run"
		if planar.length() >= FULL_STRIDE_SPEED_MPS - MOVING_SPEED_EPSILON_MPS
		else "walk"
	)
	var local_velocity: Vector3 = Basis(Vector3.UP, facing_yaw).inverse() * planar
	if absf(local_velocity.x) > absf(local_velocity.z):
		return StringName(gait + ("_right" if local_velocity.x > 0.0 else "_left"))
	return StringName(gait + ("_back" if local_velocity.z > 0.0 else ""))
