extends Node3D
## Runs the production foot command and ActorMotion on a source-linked flat ground sector.

const SMOKE_ARGUMENT: String = "--foot-harness-smoke"
const SMOKE_TICKS: int = 6

var _client_tick: int = 0
var _smoke: bool = false
var _start_position: Vector3

@onready var _actor: ActorMotion = $Player as ActorMotion
@onready var _input: DesktopFootInput = $DesktopFootInput as DesktopFootInput
@onready var _camera_rig: Node3D = $CameraRig
@onready var _camera: Camera3D = $CameraRig/Camera3D as Camera3D


## Binds authored harness nodes and enforces a 60 FPS development safety cap.
func _ready() -> void:
	Engine.max_fps = 60
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	_input.bind_aim(_camera, _actor)
	_smoke = SMOKE_ARGUMENT in OS.get_cmdline_user_args()
	if _smoke:
		_input.set_focused(true)
	_start_position = _actor.global_position


## Samples standalone desktop intent and applies exactly one shared authority step.
func _physics_process(delta: float) -> void:
	_client_tick += 1
	_camera_rig.global_position.x = _actor.global_position.x
	_camera_rig.global_position.z = _actor.global_position.z
	var command: FootCommand = _input.sample(_client_tick)
	if _smoke:
		command = FootCommand.new(
			_client_tick, _client_tick, Vector2.RIGHT, -PI * 0.5, false, false
		)
	_actor.step(command, delta, ActorMotion.StepMode.AUTHORITY)

	if _smoke and _client_tick >= SMOKE_TICKS:
		_finish_smoke()


## Exits the bounded headless smoke with a nonzero result on missing movement.
func _finish_smoke() -> void:
	var travelled: float = _actor.global_position.distance_to(_start_position)
	if travelled <= 0.2:
		push_error("FOOT_HARNESS_SMOKE failed: ActorMotion did not move")
		get_tree().quit(1)
		return

	print("FOOT_HARNESS_SMOKE PASS distance=%.3f" % travelled)
	get_tree().quit(0)
