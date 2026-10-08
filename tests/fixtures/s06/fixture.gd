class_name S06Fixture
extends Node3D
## Saved standalone host composition; commands call unchanged S02/S04 body APIs.

signal route_finished(case_name: String, samples: Array[Dictionary], timed_out: bool)

const FOOT_LAYER: int = 2
const FOOT_MASK: int = 3
const FOOT_LIMIT_TICKS: int = 1200
const CAR_LIMIT_TICKS: int = 1800

@export var authoritative: bool = true

var controller: S06Controller = S06Controller.new()
var active_body: CharacterBody3D
var active_kind: String = ""
var active_case: String = ""
var ticks: int = 0
var samples: Array[Dictionary] = []

@onready var _minimap: S06Minimap = $Ui/Minimap


## Configures passive roles before child entry, including bodies without their own callbacks.
func _enter_tree() -> void:
	($CarWest as S04Kinematic).configure(false)
	($CarEast as S04Kinematic).configure(false)
	($Person as S02ActorMotion).collision_layer = 0
	($Person as S02ActorMotion).collision_mask = 0


## Installs validated shared minimap data after saved child placement is available.
func _ready() -> void:
	_minimap.bind_city($City as S06City)


## Advances exactly one authoritative body step per actual physics callback.
func _physics_process(delta: float) -> void:
	if active_body == null:
		return

	var command: Dictionary = controller.intent(active_body.motion_state(), active_kind)
	if command.done:
		_finish(false)
		return

	if active_kind == "FOOT":
		(active_body as S02ActorMotion).step(command.move, command.turn, delta)
	else:
		(active_body as S04Kinematic).step(command.drive, delta)

	ticks += 1
	var state: Dictionary = active_body.motion_state()
	var contacts: Array[String] = []
	for index: int in active_body.get_slide_collision_count():
		var contact: KinematicCollision3D = active_body.get_slide_collision(index)
		contacts.append(str(contact.get_collider().name))
	samples.append({ "tick": ticks, "delta": delta,
		"position": [state.position.x, state.position.y, state.position.z],
		"yaw": state.yaw, "speed": state.velocity.length(), "contacts": contacts })
	_minimap.set_marker(state.position)
	var limit: int = FOOT_LIMIT_TICKS if active_kind == "FOOT" else CAR_LIMIT_TICKS
	if ticks >= limit:
		_finish(true)


## Clears producers on teardown without leaving pending callbacks or held commands.
func _exit_tree() -> void:
	stop_route()


## Admits one host-controlled route with no concurrent junction competitors in this spike.
func start_route(case_name: String) -> String:
	stop_route()
	if not authoritative:
		return "NOT_OWNER"

	var from_id: StringName
	var to_id: StringName
	if case_name == "foot":
		active_body = $Person
		active_kind = "FOOT"
		from_id = &"s06/foot/west"
		to_id = &"s06/foot/east"
	elif case_name == "east_to_north":
		active_body = $CarWest
		active_kind = "TRAFFIC"
		from_id = &"s06/lane/west"
		to_id = &"s06/lane/north"
	elif case_name == "west_to_south":
		active_body = $CarEast
		active_kind = "TRAFFIC"
		from_id = &"s06/lane/east"
		to_id = &"s06/lane/south"
	else:
		return "NO_ROUTE"

	var code: String = controller.bind_route($City, active_kind, from_id, to_id, true)
	if code != "OK":
		active_body = null
		return code

	if active_body is S04Kinematic:
		active_body.configure(true)
	else:
		active_body.collision_layer = FOOT_LAYER
		active_body.collision_mask = FOOT_MASK
	active_case = case_name
	ticks = 0
	samples.clear()
	return "OK"


## Returns current public body state for independent outcome assertions.
func body_state(case_name: String) -> Dictionary:
	var body: CharacterBody3D = $Person
	if case_name == "east_to_north":
		body = $CarWest
	elif case_name == "west_to_south":
		body = $CarEast
	return body.motion_state()


## Cancels producers and neutralizes bodies before ownership/lifetime changes.
func stop_route() -> void:
	controller.clear()
	if active_body != null:
		active_body.neutralize()
		if active_body is S04Kinematic:
			active_body.configure(false)
		else:
			active_body.collision_layer = 0
			active_body.collision_mask = 0

	active_body = null
	active_kind = ""
	active_case = ""


## Publishes complete stopped motion and retained trajectory before cancelling the binding.
func _finish(timed_out: bool) -> void:
	var case_name: String = active_case
	var completed: Array[Dictionary] = samples.duplicate(true)
	stop_route()
	route_finished.emit(case_name, completed, timed_out)
