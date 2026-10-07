class_name S03RActor
extends S02ActorMotion
## Adds fixture-only replica presentation; inherited step remains the only movement rule.

const INTERPOLATION_MS: int = 100
const MAX_SAMPLES: int = 8

var remote_view: bool = false
var samples: Array[Dictionary] = []
var latest_sequence: int = 0

@onready var _anchor: Node3D = $PresentationAnchor


## Smooths only remote presentation behind receipt time; owned baseline displays latest authority.
func _process(_delta: float) -> void:
	if not remote_view or samples.size() < 2:
		_anchor.transform = Transform3D.IDENTITY
		return

	var target_ms: int = Time.get_ticks_msec() - INTERPOLATION_MS
	while samples.size() > 2 and int(samples[1].time) <= target_ms:
		samples.pop_front()

	var first: Dictionary = samples[0]
	var second: Dictionary = samples[1]
	var weight: float = clampf(float(target_ms - first.time) /
		maxf(1.0, float(second.time - first.time)), 0.0, 1.0)
	_anchor.global_transform = (first.transform as Transform3D).interpolate_with(
		second.transform, weight)


## Installs host physics pose without allowing replicas to simulate collision.
func install_pose(pose: Dictionary, receipt_ms: int) -> void:
	global_position = Vector3(pose.position[0], pose.position[1], pose.position[2])
	rotation.y = pose.yaw
	velocity = Vector3(pose.velocity[0], pose.velocity[1], pose.velocity[2])
	latest_sequence = int(pose.sequence)
	samples.append({ "time": receipt_ms, "transform": global_transform })
	if samples.size() > MAX_SAMPLES:
		samples.pop_front()


## Clears motion and interpolation before lifecycle observers can see a retired body.
func retire() -> void:
	neutralize()
	samples.clear()
	visible = false
	collision_layer = 0
	collision_mask = 0


## Exposes the actual rendered anchor pose separately from physics state.
func display_state() -> Dictionary:
	return { "position": _anchor.global_position, "yaw": _anchor.global_rotation.y }
