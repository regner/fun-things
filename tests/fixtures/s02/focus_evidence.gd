extends Node
## Exercises real window minimize/focus notifications with injected held keyboard events.

enum Stage {
	START,
	READY,
	HELD,
	MINIMIZED,
	RESTORED,
	DONE,
}

const SAMPLE_INTERVAL_SECONDS: float = 0.1
const DEADLINE_SECONDS: float = 7.0
const INITIAL_FOCUS_DEADLINE_SECONDS: float = 3.0
const PRESS_AT_SECONDS: float = 1.0
const MINIMIZE_AT_SECONDS: float = 1.5
const RESTORE_AT_SECONDS: float = 3.0
const CHECK_AT_SECONDS: float = 4.0
const FOCUS_GATE_ARGUMENT: String = "--focus-gate="

var _elapsed: float = 0.0
var _waiting_elapsed: float = 0.0
var _sample_remaining: float = 0.0
var _stage: Stage = Stage.START
var _saw_focus_loss: bool = false
var _held_seen: bool = false
var _lost_position: Vector3
var _lost_shots: int = 0
var _focus_gate: String = ""
var _failures: Array[String] = []

@onready var _fixture: S02Fixture = $Fixture
@onready var _window: Window = get_window()


## Requests foreground and waits for the runner's independently observed native-focus gate.
func _ready() -> void:
	_window.title = "S02 OS Focus Evidence"
	_focus_gate = _focus_gate_path()
	_window.show()
	_window.grab_focus()
	_emit_stage("await_initial_native_focus")


## Drives bounded OS transitions only after independently confirmed initial native focus.
func _process(delta: float) -> void:
	_waiting_elapsed += delta
	_sample_remaining -= delta
	if not is_instance_valid(_fixture) or not _fixture.is_node_ready():
		return

	if _stage == Stage.START:
		if not _focus_gate.is_empty() and FileAccess.file_exists(_focus_gate):
			_elapsed = 0.0
			_waiting_elapsed = 0.0
			_emit_stage("initial_native_focus_established")
			_stage = Stage.READY
		elif _waiting_elapsed >= INITIAL_FOCUS_DEADLINE_SECONDS:
			_failures.append("initial native focus not established")
			_finish()
		return

	_elapsed += delta
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
		_emit_stage("focus_out")

	if _sample_remaining <= 0.0:
		_record_sample()

	if _elapsed >= DEADLINE_SECONDS:
		_finish()


## Performs window transitions; cancellation must come from the OS signal, not a test call.
func _drive_window() -> void:
	if _stage == Stage.READY and _elapsed >= PRESS_AT_SECONDS:
		if not _require_focus_gate(false):
			return
		_emit_stage("press")
		_key(KEY_W, true)
		_key(KEY_SPACE, true)
		_stage = Stage.HELD
	elif _stage == Stage.HELD and _elapsed >= MINIMIZE_AT_SECONDS:
		if not _require_focus_gate(true):
			return
		_emit_stage("minimize")
		_window.mode = Window.MODE_MINIMIZED
		_stage = Stage.MINIMIZED
	elif _stage == Stage.MINIMIZED and _elapsed >= RESTORE_AT_SECONDS:
		_check_suspended()
		_key(KEY_W, false)
		_key(KEY_SPACE, false)
		_window.mode = Window.MODE_WINDOWED
		_window.grab_focus()
		_emit_stage("restore")
		_stage = Stage.RESTORED
	elif _stage == Stage.RESTORED and _elapsed >= CHECK_AT_SECONDS:
		_check_restored()
		_emit_stage("check")
		_stage = Stage.DONE


## Verifies restored focus remains neutral until a fresh physical input event.
func _check_restored() -> void:
	if not _window.has_focus():
		_failures.append("restoring window did not regain native focus")
	if _fixture.input_collector.sample().move != 0.0:
		_failures.append("restoring window resumed stale movement")
	if _fixture.input_collector.sample().fire:
		_failures.append("restoring window resumed stale fire")


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


## Emits process-clock stage markers so the runner uses the fixture's actual timeline.
func _emit_stage(stage_name: String) -> void:
	print("S02_FOCUS_STAGE ", JSON.stringify({
		"stage": stage_name,
		"process_ms": Time.get_ticks_msec(),
		"fixture_time": _elapsed,
		"native_focus": _window.has_focus(),
		"mode": _window.mode,
	}))


## Reports the bounded result once and exits without changing the saved fixture.
func _finish() -> void:
	if _stage == Stage.DONE and _elapsed < DEADLINE_SECONDS:
		return

	_stage = Stage.DONE
	_emit_stage("result")
	print("S02_FOCUS_RESULT ", JSON.stringify({
		"failures": _failures, "os_focus_loss": _saw_focus_loss,
	}))
	_fixture.queue_free()
	get_tree().quit(0 if _failures.is_empty() else 1)


## Stops before an input/window transition when independently observed foreground is lost.
func _require_focus_gate(release_keys: bool) -> bool:
	if _focus_gate_present():
		return true
	if release_keys:
		_key(KEY_W, false)
		_key(KEY_SPACE, false)
	_failures.append("initial native focus not established")
	_finish()
	return false


## Reports whether the runner still observes sustained child foreground ownership.
func _focus_gate_present() -> bool:
	return not _focus_gate.is_empty() and FileAccess.file_exists(_focus_gate)


## Reads the external gate path supplied after Godot's user-argument separator.
func _focus_gate_path() -> String:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with(FOCUS_GATE_ARGUMENT):
			return argument.trim_prefix(FOCUS_GATE_ARGUMENT)
	return ""


## Injects held keys; focus loss itself comes from the real desktop window transition.
func _key(code: Key, pressed: bool) -> void:
	var event: InputEventKey = InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = pressed
	_window.push_input(event)
