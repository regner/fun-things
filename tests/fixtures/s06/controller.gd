class_name S06Controller
extends RefCounted
## Host intent producer for one admitted saved route; never writes a body transform.

const LOOKAHEAD_M: float = 2.0
const ARRIVAL_M: float = 0.3
const TRAFFIC_SPEED_MPS: float = 3.5
const FOOT_TURN_GAIN: float = 4.0
const THROTTLE_GAIN_PER_MPS: float = 2.0
const FOOT_ALIGN_RAD: float = 0.05
const NEAREST_WINDOW: int = 32

var points: PackedVector3Array = []
var index: int = 0
var enabled: bool = false


## Admits a current CityData route to a host controller, rejecting passive/stale use.
func bind_route(city: S06City, kind: String, from_id: StringName,
		to_id: StringName, host: bool) -> String:
	clear()
	if not host:
		return "NOT_OWNER"

	var result: Dictionary = city.route(kind, from_id, to_id)
	if result.code != "OK":
		return result.code

	points = result.world_points_m
	enabled = points.size() >= 2
	return "OK" if enabled else "NO_ROUTE"


## Generates facing-relative intent using current public body state and saved route points.
func intent(state: Dictionary, kind: String) -> Dictionary:
	if not enabled:
		return { "done": true }

	var position: Vector3 = state.position
	if position.distance_to(points[-1]) <= ARRIVAL_M:
		clear()
		return { "done": true }

	var nearest: float = INF
	for candidate: int in range(index, mini(index + NEAREST_WINDOW, points.size())):
		var distance: float = position.distance_to(points[candidate])
		if distance < nearest:
			nearest = distance
			index = candidate

	var target_index: int = index
	var lookahead: float = 0.0
	while target_index + 1 < points.size() and lookahead < LOOKAHEAD_M:
		lookahead += points[target_index].distance_to(points[target_index + 1])
		target_index += 1

	var direction: Vector3 = points[target_index] - position
	var desired: float = atan2(-direction.x, -direction.z)
	var error: float = wrapf(desired - float(state.yaw), -PI, PI)
	if kind == "FOOT":
		return { "done": false, "move": 1.0 if absf(error) < FOOT_ALIGN_RAD else 0.0,
			"turn": clampf(-error * FOOT_TURN_GAIN, -1.0, 1.0) }

	return _car_intent(state, direction, error)


## Converts lookahead error to bounded steering/throttle through the shared handling scale.
func _car_intent(state: Dictionary, direction: Vector3, error: float) -> Dictionary:
	var speed: float = state.velocity.length()
	var yaw_rate: float = 2.0 * speed * sin(error) / maxf(direction.length(), ARRIVAL_M)
	var steer_scale: float = S04DriveRules.TURN_RAD_PER_SECOND * clampf(
		speed / S04DriveRules.FULL_STEER_SPEED_MPS, 0.0, 1.0)
	var steer: float = -yaw_rate / maxf(steer_scale, ARRIVAL_M)
	return { "done": false, "drive": {
		"throttle": clampf((TRAFFIC_SPEED_MPS - speed) * THROTTLE_GAIN_PER_MPS, 0.0, 1.0),
		"steer": clampf(steer, -1.0, 1.0), "brake": 0.0, "handbrake": false } }


## Cancels the bounded route before controller teardown or ownership transfer.
func clear() -> void:
	enabled = false
	points = []
	index = 0
