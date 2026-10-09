class_name MainMenu
extends Control
## Authored front-end navigation that emits session intent without owning session state.

signal standalone_requested()
signal host_requested(port: int)
signal join_requested(address: String, port: int)
signal quit_requested()

const DEFAULT_PORT: int = 24_900

@onready var _main_actions: VBoxContainer = %MainActions
@onready var _host_panel: PanelContainer = %HostPanel
@onready var _join_panel: PanelContainer = %JoinPanel
@onready var _host_port: SpinBox = %HostPort
@onready var _join_address: LineEdit = %JoinAddress
@onready var _join_port: SpinBox = %JoinPort
@onready var _feedback: Label = %Feedback
@onready var _solo_button: Button = %SoloButton


## Supplies deterministic defaults when the authored controls enter the tree.
func _ready() -> void:
	_host_port.value = DEFAULT_PORT
	_join_port.value = DEFAULT_PORT
	show_main()


## Restores the primary actions and initial keyboard focus.
func show_main() -> void:
	visible = true
	_main_actions.visible = true
	_host_panel.visible = false
	_join_panel.visible = false
	_feedback.text = ""
	_solo_button.grab_focus()


## Displays a synchronous request rejection without deciding recovery.
func show_feedback(message: String) -> void:
	_feedback.text = message


## Emits the standalone session intent.
func _on_solo_pressed() -> void:
	standalone_requested.emit()


## Opens the authored ENet host form.
func _on_host_pressed() -> void:
	_main_actions.visible = false
	_join_panel.visible = false
	_host_panel.visible = true
	_host_port.grab_focus()


## Opens the authored direct-address join form.
func _on_join_pressed() -> void:
	_main_actions.visible = false
	_host_panel.visible = false
	_join_panel.visible = true
	_join_address.grab_focus()


## Emits a host intent using the validated numeric form field.
func _on_create_host_pressed() -> void:
	host_requested.emit(int(_host_port.value))


## Emits direct endpoint text for the future ENet adapter parser.
func _on_connect_pressed() -> void:
	var address: String = _join_address.text.strip_edges()
	if address.is_empty():
		show_feedback("Enter the host address first.")
		_join_address.grab_focus()
		return

	join_requested.emit(address, int(_join_port.value))


## Returns from a secondary form to the primary actions.
func _on_back_pressed() -> void:
	show_main()


## Requests orderly process exit from the Boot coordinator.
func _on_quit_pressed() -> void:
	quit_requested.emit()
