class_name VehiclePresentation
extends Node3D
## Drives imported wheel steering and spin from VehicleMotion telemetry only.

const MAX_STEER_ANGLE_RAD: float = 0.45
const WHEEL_RADIUS_M: float = 0.32
const FRONT_STEER_NAMES: Array[StringName] = [
	&"SteerFrontLeft",
	&"SteerFrontRight",
]
const SPIN_NAMES: Array[StringName] = [
	&"SpinFrontLeft",
	&"SpinFrontRight",
	&"SpinRearLeft",
	&"SpinRearRight",
]
const ENTRY_PRESENTATION_SECONDS: float = 0.3
const DOOR_OPEN_ANGLE_RAD: float = 0.85

var _front_steer_nodes: Array[Node3D] = []
var _spin_nodes: Array[Node3D] = []
var _door_hinges: Dictionary[StringName, Node3D] = {}
var _door_closed_yaws: Dictionary[StringName, float] = {}
var _door_tween: Tween


## Resolves the stable source-authored wheel names once after the imported model is ready.
func _ready() -> void:
	for wheel_name: StringName in FRONT_STEER_NAMES:
		var wheel: Node = find_child(String(wheel_name), true, false)
		if wheel is Node3D:
			_front_steer_nodes.append(wheel as Node3D)
	for spin_name: StringName in SPIN_NAMES:
		var spin: Node = find_child(String(spin_name), true, false)
		if spin is Node3D:
			_spin_nodes.append(spin as Node3D)
	for side: StringName in [&"Left", &"Right"]:
		var hinge: Node = find_child("HingeFront%s" % side, true, false)
		if hinge is Node3D:
			_door_hinges[side] = hinge as Node3D
			_door_closed_yaws[side] = (hinge as Node3D).rotation.y


## Applies steering and travelled-distance spin without querying gameplay collision.
func apply_motion(motion_state: Dictionary, delta_seconds: float) -> void:
	var steer: float = float(motion_state.steer)
	for wheel: Node3D in _front_steer_nodes:
		wheel.rotation.y = -steer * MAX_STEER_ANGLE_RAD

	var spin_delta: float = (
		-float(motion_state.forward_speed_mps) * delta_seconds / WHEEL_RADIUS_M
	)
	for spin: Node3D in _spin_nodes:
		spin.rotation.x = wrapf(spin.rotation.x + spin_delta, -PI, PI)


## Plays the authored front-door hinge without transferring gameplay ownership.
func play_entry(side: StringName) -> bool:
	var hinge: Node3D = _door_hinges.get(side)
	if hinge == null:
		return false
	if _door_tween != null and _door_tween.is_valid():
		_door_tween.kill()
	for door_side: StringName in _door_hinges:
		_door_hinges[door_side].rotation.y = _door_closed_yaws[door_side]
	var closed_yaw: float = _door_closed_yaws[side]
	var direction: float = 1.0 if side == &"Left" else -1.0
	_door_tween = create_tween()
	_door_tween.tween_property(
		hinge,
		"rotation:y",
		closed_yaw + direction * DOOR_OPEN_ANGLE_RAD,
		ENTRY_PRESENTATION_SECONDS * 0.5,
	)
	_door_tween.tween_property(
		hinge,
		"rotation:y",
		closed_yaw,
		ENTRY_PRESENTATION_SECONDS * 0.5,
	)
	return true


## Reports whether both imported entry hinges required by interaction resolved.
func has_complete_entry_rig() -> bool:
	return _door_hinges.size() == 2


## Reports whether all imported wheel controls required by the presentation contract resolved.
func has_complete_wheel_rig() -> bool:
	return (
		_front_steer_nodes.size() == FRONT_STEER_NAMES.size()
		and _spin_nodes.size() == SPIN_NAMES.size()
	)
