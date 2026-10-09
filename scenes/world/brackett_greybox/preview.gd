extends Node3D
## Asset-local camera selector; saved scenes own all visible geometry and placement.


## Bounds the review window's frame rate without changing shared project settings.
func _ready() -> void:
	Engine.max_fps = 60
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)


## Selects an authored review camera using the visible number-key legend.
func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return

	var camera_name: String = ""
	if event.keycode == KEY_0:
		camera_name = "Overview"
	elif event.keycode == KEY_TAB:
		camera_name = "Plan"
	elif event.keycode >= KEY_1 and event.keycode <= KEY_9:
		camera_name = "District%02d" % (event.keycode - KEY_0)

	if not camera_name.is_empty():
		var camera: Camera3D = get_node("Cameras/" + camera_name)
		camera.make_current()
