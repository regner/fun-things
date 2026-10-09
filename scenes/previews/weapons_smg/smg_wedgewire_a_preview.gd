class_name SmgWedgewirePreview
extends Node3D
## Asset-local camera selection only; saved scenes own every visible node/transform.

const PREVIEW_MAX_FPS: int = 60


## Bounds local preview frame rate without changing project settings.
func _ready() -> void:
	Engine.max_fps = PREVIEW_MAX_FPS
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)


## Selects authored review cameras without changing model placement or gameplay.
func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.is_pressed() or event.is_echo():
		return

	var key_event: InputEventKey = event as InputEventKey
	match key_event.physical_keycode:
		KEY_O:
			($OverviewCamera as Camera3D).make_current()
		KEY_G:
			($GameCamera as Camera3D).make_current()
		KEY_S:
			($SideCamera as Camera3D).make_current()
