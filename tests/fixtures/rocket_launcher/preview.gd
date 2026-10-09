class_name DockThumperPreview
extends Node3D
## Asset-local camera inspection only; no projectile simulation or gameplay state.

const PREVIEW_MAX_FPS: int = 60


## Caps this preview and enables synchronized presentation in its private window.
func _ready() -> void:
	Engine.max_fps = PREVIEW_MAX_FPS
	if DisplayServer.get_name() != "headless":
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)


## Switches among authored cameras without changing asset placement.
func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return

	match event.physical_keycode:
		KEY_1:
			%GameCamera.make_current()
		KEY_2:
			%DetailCamera.make_current()
		KEY_3:
			%RocketCamera.make_current()
		KEY_ESCAPE:
			get_tree().quit()
