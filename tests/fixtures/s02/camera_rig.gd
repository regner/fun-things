class_name S02CameraRig
extends Node3D
## Fixed-yaw vertical perspective follow; visual state never changes world collision.

const MIN_CANDIDATE_FOV_DEGREES: float = 30.0
const MAX_CANDIDATE_FOV_DEGREES: float = 70.0

@export var follow_rate_per_second: float = 12.0

var _target: S02ActorMotion

@onready var _camera: Camera3D = $Camera3D


## Follows committed position without inheriting the actor's facing.
func _process(delta: float) -> void:
	if not is_instance_valid(_target):
		return

	global_position = global_position.lerp(
		_target.global_position, 1.0 - exp(-follow_rate_per_second * delta)
	)


## Binds a simulation owner and snaps only this local presentation anchor.
func bind(actor: S02ActorMotion) -> void:
	_target = actor
	global_position = actor.global_position


## Chooses an experiment FOV while preserving vertical projection and yaw.
func set_candidate_fov(degrees: float) -> void:
	_camera.fov = clampf(degrees, MIN_CANDIDATE_FOV_DEGREES, MAX_CANDIDATE_FOV_DEGREES)


## Exposes measured camera state and projection for evidence and overlays.
func camera() -> Camera3D:
	return _camera
