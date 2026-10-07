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
@onready var _buildings: Array[S02BuildingView] = [
	$WestCorner, $EastCorner, $NearTower, $TallTower,
]


## Binds presentation and cancellation after all saved children are ready.
func _ready() -> void:
	rig.bind(actor)
	_overlay.bind(rig.camera(), actor)
	aim.fired.connect(_overlay.show_shot)
	input_collector.suspended.connect(_on_suspended)


## Updates only local building materials after the follow camera has advanced.
func _process(_delta: float) -> void:
	for building: S02BuildingView in _buildings:
		building.protect_actor(rig.camera(), actor.global_position)


## Collects intent before the single motion/query step, then updates diagnostic UI.
func _physics_process(delta: float) -> void:
	if not manual_mode:
		var command: Dictionary = input_collector.sample()
		step_intent(command.move, command.turn, command.fire, delta)

	_update_status()


## Displays owner state; camera() returns a cached reference, not a tree lookup.
func _update_status() -> void:
	var hit_name: String = str(aim.last_hit.name) if is_instance_valid(aim.last_hit) else "none"
	_status.text = "S02 desktop experiment | %.0f m / %.0f° | shots %d | hit %s\n%s" % [
		rig.camera().position.y, rig.camera().fov, aim.shot_count, hit_name,
		"INPUT SUSPENDED — release controls, then resume" if (
			input_collector.menu_open or not input_collector.active
		) else "W/S or ↑/↓ forward/back • A/D or ←/→ turn • Space fire • Esc suspend",
	]


## Provides the shared standalone simulation entrypoint for input and outcome checks.
func step_intent(move_axis: float, turn_axis: float, firing: bool, delta: float) -> void:
	actor.step(move_axis, turn_axis, delta)
	aim.step(actor, firing, delta)


## Clears both continuous movement and transient firing before the next physics tick.
func _on_suspended() -> void:
	actor.neutralize()
	aim.clear()
