extends Node3D
## Asset-only clip and camera inspection; no player movement, combat or network behavior.

const FRAME_CAP: int = 60
const CLIPS: Array[StringName] = [
	&"idle", &"walk", &"run", &"walk_back", &"walk_left", &"walk_right",
	&"run_back", &"run_left", &"run_right", &"pistol_hold", &"pistol_walk",
	&"pistol_run", &"pistol_fire", &"pistol_reload", &"smg_hold", &"smg_walk",
	&"smg_run", &"smg_fire", &"smg_reload", &"launcher_hold", &"launcher_walk",
	&"launcher_run", &"launcher_fire", &"death",
]

var _clip_index: int = 0


## Start the saved preview at a capped frame rate and display its inspection controls.
func _ready() -> void:
	Engine.max_fps = FRAME_CAP
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	_show_clip()


## Cycle presentation clips or select one of the two authored cameras.
func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	if event.keycode == KEY_RIGHT:
		_clip_index = (_clip_index + 1) % CLIPS.size()
	elif event.keycode == KEY_LEFT:
		_clip_index = posmod(_clip_index - 1, CLIPS.size())
	elif event.keycode == KEY_TAB:
		if $GameCamera.current:
			$Camera.make_current()
		else:
			$GameCamera.make_current()
	else:
		return
	_show_clip()
	get_viewport().set_input_as_handled()


## Apply the selected clip through the reusable visual's public API.
func _show_clip() -> void:
	$Courier.play_clip(CLIPS[_clip_index])
	$ReviewOverlay/Caption.text = "Coral Courier • %s\n← / → clip    Tab camera\n%s" % [
		CLIPS[_clip_index], "47 m / 42° / north up" if $GameCamera.current else "Close review",
	]
