class_name S02ProbeOverlay
extends Control
## Diagnostic aim trace and local marker; no 3D draw geometry or gameplay decisions.

const TRACE_SECONDS: float = 0.12
const MARKER_RADIUS_PX: float = 11.0
const MARKER_COLOR: Color = Color("#F6F1DC")
const HIT_COLOR: Color = Color("#FFC05A")

var _camera: Camera3D
var _actor: S02ActorMotion
var _start: Vector3
var _end: Vector3
var _trace_remaining: float = 0.0


## Expires the one bounded trace and schedules current-camera debug drawing.
func _process(delta: float) -> void:
	_trace_remaining = maxf(0.0, _trace_remaining - delta)
	queue_redraw()


## Draws an explicit diagnostic marker and shot result over the actual camera.
func _draw() -> void:
	if not is_instance_valid(_camera) or not is_instance_valid(_actor):
		return

	var point: Vector2 = _camera.unproject_position(_actor.global_position)
	draw_arc(point, MARKER_RADIUS_PX, 0.3, 2.8, 20, MARKER_COLOR, 1.5, true)
	draw_arc(point, MARKER_RADIUS_PX, 3.5, 5.9, 20, MARKER_COLOR, 1.5, true)
	if _trace_remaining > 0.0:
		var endpoint: Vector2 = _camera.unproject_position(_end)
		draw_line(_camera.unproject_position(_start), endpoint, HIT_COLOR, 2.0, true)
		draw_circle(endpoint, 3.0, HIT_COLOR)


## Receives presentation dependencies from the enclosing fixture coordinator.
func bind(camera_node: Camera3D, actor: S02ActorMotion) -> void:
	_camera = camera_node
	_actor = actor


## Displays the probe's resolved endpoint without performing another hit query.
func show_shot(origin: Vector3, endpoint: Vector3, _hit: Node) -> void:
	_start = origin
	_end = endpoint
	_trace_remaining = TRACE_SECONDS
