extends Node3D
## Saved rocket-and-trail presentation moved only for the bounded visual stress fixture.

const TRAVEL_SPAN_METERS: float = 36.0
const SPEED_METERS_PER_SECOND: float = 12.0

var _start: Vector3
var _direction: Vector3 = Vector3.RIGHT


## Captures authored placement and assigns one of four cardinal stress lanes.
func configure_lane(index: int) -> void:
	_start = position
	_direction = [Vector3.RIGHT, Vector3.BACK, Vector3.LEFT, Vector3.FORWARD][index % 4]
	$Trail.emitting = true


## Advances presentation and wraps it without producing gameplay collision or damage.
func advance(delta: float) -> void:
	position += _direction * SPEED_METERS_PER_SECOND * delta
	if position.distance_to(_start) >= TRAVEL_SPAN_METERS:
		position = _start
