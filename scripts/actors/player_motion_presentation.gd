class_name PlayerMotionPresentation
extends Node3D
## Selects Coral Courier locomotion clips from motion state without writing simulation.

const MOVING_SPEED_EPSILON: float = 0.05

var _current_clip: StringName = &""

@onready var _visual: PlayerCharacterVisual = $Visuals/Model as PlayerCharacterVisual


## Updates the full-body locomotion clip relative to the actor's independent facing.
func apply_motion(world_velocity: Vector3, facing_yaw: float) -> void:
	var clip: StringName = _locomotion_clip(world_velocity, facing_yaw)
	if clip == _current_clip:
		return

	if _visual.play_clip(clip):
		_current_clip = clip


## Maps planar movement into the nearest authored forward/back/left/right clip.
func _locomotion_clip(world_velocity: Vector3, facing_yaw: float) -> StringName:
	var planar := Vector3(world_velocity.x, 0.0, world_velocity.z)
	if planar.length() <= MOVING_SPEED_EPSILON:
		return &"idle"

	var local_velocity: Vector3 = Basis(Vector3.UP, facing_yaw).inverse() * planar
	if absf(local_velocity.x) > absf(local_velocity.z):
		return &"run_right" if local_velocity.x > 0.0 else &"run_left"
	return &"run_back" if local_velocity.z > 0.0 else &"run"
