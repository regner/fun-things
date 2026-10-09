class_name S02Fixture
extends Node3D
## Orders standalone input, motion and query; fixture-only, without network or combat state.

@export var manual_mode: bool = false

@onready var actor: S02ActorMotion = $Actor
@onready var input_collector: S02DesktopInput = $Input
@onready var aim: S02AimProbe = $Aim
@onready var rig: S02CameraRig = $CameraRig
@onready var _overlay: S02ProbeOverlay = get_node("UI/Overlay")
@onready var _status: Label = get_node("UI/Status")


## Binds presentation, mouse projection and cancellation after saved children are ready.
func _ready() -> void:
	rig.bind(actor)
	input_collector.bind_aim(rig.camera(), actor)
	_overlay.bind(rig.camera(), actor)
	aim.fired.connect(_overlay.show_shot)
	input_collector.suspended.connect(_on_suspended)


## Collects intent before the single motion/query step, then updates diagnostic UI.
func _physics_process(delta: float) -> void:
	if not manual_mode:
		var command: Dictionary = input_collector.sample()
		step_command(command, delta)

	_update_status()


## Displays owner state; camera() returns a cached reference, not a tree lookup.
func _update_status() -> void:
	var hit_name: String = str(aim.last_hit.name) if is_instance_valid(aim.last_hit) else "none"
	_status.text = "S02 desktop experiment | %.0f m / %.0f° | shots %d | hit %s\n%s" % [
		rig.camera().position.y, rig.camera().fov, aim.shot_count, hit_name,
		"INPUT SUSPENDED — release controls, then resume" if (
			input_collector.menu_open or not input_collector.active
		) else "WASD or arrows move • Mouse aims • Left click / Space fires • Esc suspends",
	]


## Provides one command-shaped simulation entrypoint for standalone and later replay callers.
func step_command(command: Dictionary, delta: float) -> void:
	actor.step(command.move, command.aim_yaw, delta)
	aim.step(actor, command.fire, delta)


## Clears both continuous movement and transient firing before the next physics tick.
func _on_suspended() -> void:
	actor.neutralize()
	aim.clear()
