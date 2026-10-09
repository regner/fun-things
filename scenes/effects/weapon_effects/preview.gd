extends Node3D
## Bounded asset-local playback; positions and visible geometry belong to saved scenes.

const CYCLE_SECONDS: float = 3.2
const TRAIL_EMIT_SECONDS: float = 0.8
const PREVIEW_SECONDS: float = 24.0
const PREVIEW_FPS: int = 60

var _elapsed_seconds: float = 0.0
var _cycle_seconds: float = 0.0
var _trail_stopped: bool = false
var _paused: bool = false

@onready var muzzle: Node3D = $Muzzle
@onready var impact: Node3D = $Hit
@onready var trail: Node3D = $TrailAnchor/Trail
@onready var explosion: Node3D = $Explosion
@onready var overlap: Node3D = $Overlap


## Play the saved assembly at a capped rate; command-line evidence capture remains optional.
func _ready() -> void:
	Engine.max_fps = PREVIEW_FPS
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	_play_cycle()
	if "--effects-capture" in OS.get_cmdline_user_args():
		_capture_frames()


## Bound automatic playback and test a stopped trail without assigning projectile motion.
func _process(delta: float) -> void:
	if _paused:
		return

	_elapsed_seconds += delta
	_cycle_seconds += delta
	if not _trail_stopped and _cycle_seconds >= TRAIL_EMIT_SECONDS:
		trail.stop_emission()
		_trail_stopped = true

	if _elapsed_seconds >= PREVIEW_SECONDS:
		set_playback(false)
		print("WEAPON_EFFECTS_PREVIEW_BOUNDED_STOP")
		return

	if _cycle_seconds >= CYCLE_SECONDS:
		_play_cycle()


## Provide simple preview-only controls without modifying project-wide input settings.
func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return

	if event.keycode == KEY_SPACE:
		set_playback(_paused)
	elif event.keycode == KEY_R:
		restart_playback()
	elif event.keycode == KEY_ESCAPE:
		set_playback(false)


## Restart the bounded preview explicitly after it settles.
func restart_playback() -> void:
	_elapsed_seconds = 0.0
	_paused = false
	_play_cycle()


## Stop future cycles and clear the owned roots, or restart the preview.
func set_playback(playing: bool) -> void:
	_paused = not playing
	if playing:
		restart_playback()
		return

	for effect: Node3D in [muzzle, impact, trail, explosion]:
		effect.clear()

	for effect: Node3D in overlap.get_children():
		effect.clear()


## Restart only the review fixtures; accepted-event allocation belongs to the integrator.
func _play_cycle() -> void:
	_cycle_seconds = 0.0
	_trail_stopped = false
	for effect: Node3D in [muzzle, impact, trail, explosion]:
		effect.clear()
		effect.play()

	for effect: Node3D in overlap.get_children():
		effect.clear()
		effect.play()

	print("WEAPON_EFFECTS_PREVIEW_CYCLE")


## Capture the actual saved camera in a bounded standalone process and then exit normally.
func _capture_frames() -> void:
	var window: Window = get_window()
	window.size = Vector2i(1280, 800)
	window.position = Vector2i(40, 40)
	window.mode = Window.MODE_WINDOWED
	# Warm the real particle pipelines, then restart before measuring frame age.
	await get_tree().create_timer(1.0).timeout
	restart_playback()
	DirAccess.make_dir_recursive_absolute("user://screenshots/")
	var previous_seconds: float = 0.0
	for stage: Array in [
		["ignite", 0.016],
		["peak", 0.12],
		["break", 0.32],
		["smoke", 0.70],
		["settle", 1.35],
		["clear", 1.65],
	]:
		await get_tree().create_timer(stage[1] - previous_seconds).timeout
		await RenderingServer.frame_post_draw
		var image: Image = get_viewport().get_texture().get_image()
		assert(image.get_size() == Vector2i(1280, 800))
		assert(image.save_png("user://screenshots/weapon_effects_a_" + stage[0] + ".png") == OK)
		print("WEAPON_EFFECTS_CAPTURE ", stage[0], " ", image.get_size(), " age=", _cycle_seconds)
		previous_seconds = stage[1]

	get_tree().quit()
