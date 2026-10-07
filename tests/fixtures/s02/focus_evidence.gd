extends Node
## Exercises real window minimize/focus notifications with injected held keyboard events.

enum Stage {
	START,
	HELD,
	MINIMIZED,
	RESTORED,
	DONE,
}

const SAMPLE_INTERVAL_SECONDS: float = 0.1
const DEADLINE_SECONDS: float = 7.0
const PRESS_AT_SECONDS: float = 1.0
const MINIMIZE_AT_SECONDS: float = 1.5
const RESTORE_AT_SECONDS: float = 3.0
const CHECK_AT_SECONDS: float = 4.0

var _elapsed: float = 0.0
var _sample_remaining: float = 0.0
var _stage: Stage = Stage.START
var _saw_focus_loss: bool = false
var _held_seen: bool = false
var _lost_position: Vector3
var _lost_shots: int = 0
var _failures: Array[String] = []

@onready var _fixture: S02Fixture = $Fixture
@onready var _window: Window = get_window()


## Names the owned native window without constructing the saved fixture hierarchy.
func _ready() -> void:
	_window.title = "S02 OS Focus Evidence"


## Drives bounded OS transitions and observes the ordinary input owner.
func _process(delta: float) -> void:
	_elapsed += delta
	_sample_remaining -= delta
	if not is_instance_valid(_fixture) or not _fixture.is_node_ready():
		return

	_drive_window()
	if _stage == Stage.HELD and _fixture.actor.velocity.length() > 0.0:
		_held_seen = true

	if (
		_stage == Stage.MINIMIZED and _held_seen and not _window.has_focus()
		and not _fixture.input_collector.active and not _saw_focus_loss
	):
		_saw_focus_loss = true
		_lost_position = _fixture.actor.position
		_lost_shots = _fixture.aim.shot_count

	if _sample_remaining <= 0.0:
		_record_sample()

	if _elapsed >= DEADLINE_SECONDS:
		print("S02_FOCUS_RESULT ", JSON.stringify({
			"failures": _failures, "os_focus_loss": _saw_focus_loss,
		}))
		_fixture.queue_free()
		get_tree().quit(0 if _failures.is_empty() else 1)

	return


## Performs window transitions; cancellation must come from the OS signal, not a test call.
func _drive_window() -> void:
	if _stage == Stage.START and _elapsed >= PRESS_AT_SECONDS:
		_window.show()
		_window.grab_focus()
		_key(KEY_W, true)
		_key(KEY_SPACE, true)
		_stage = Stage.HELD
	elif _stage == Stage.HELD and _elapsed >= MINIMIZE_AT_SECONDS:
		_window.mode = Window.MODE_MINIMIZED
		_stage = Stage.MINIMIZED
	elif _stage == Stage.MINIMIZED and _elapsed >= RESTORE_AT_SECONDS:
		_check_suspended()
		_key(KEY_W, false)
		_key(KEY_SPACE, false)
		_window.mode = Window.MODE_WINDOWED
		_window.grab_focus()
		_stage = Stage.RESTORED
	elif _stage == Stage.RESTORED and _elapsed >= CHECK_AT_SECONDS:
		if not _window.has_focus():
			_failures.append("restoring window did not regain native focus")
		if _fixture.input_collector.sample().move != 0.0:
			_failures.append("restoring window resumed stale input")
		_stage = Stage.DONE


## Verifies actual focus loss froze movement and shot production.
func _check_suspended() -> void:
	if not _held_seen:
		_failures.append("held movement was never observed before minimize")
	if not _saw_focus_loss:
		_failures.append("OS minimize did not deliver focus loss")
	elif _fixture.actor.position.distance_to(_lost_position) > 0.01:
		_failures.append("movement continued after OS focus loss")
	elif _fixture.aim.shot_count != _lost_shots:
		_failures.append("firing continued after OS focus loss")


## Retains native-window and input-owner observations for independent review.
func _record_sample() -> void:
	_sample_remaining = SAMPLE_INTERVAL_SECONDS
	print("S02_FOCUS ", JSON.stringify({
		"time": _elapsed, "focused": _fixture.input_collector.active,
		"visible": _window.visible, "native_focus": _window.has_focus(), "mode": _window.mode,
		"command": _fixture.input_collector.sample(),
		"position": str(_fixture.actor.position), "shots": _fixture.aim.shot_count,
	}))


## Injects held keys; focus loss itself comes from the real desktop window transition.
func _key(code: Key, pressed: bool) -> void:
	var event: InputEventKey = InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = pressed
	_window.push_input(event)
