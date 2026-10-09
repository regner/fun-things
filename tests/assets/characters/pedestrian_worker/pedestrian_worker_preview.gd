class_name PedestrianWorkerPreview
extends Node3D
## Bounded asset-only playback; no AI, spawning, movement simulation or network authority.

const PREVIEW_SECONDS: float = 20.0


## Cap the standalone review and leave death in its retained final pose.
func _ready() -> void:
	Engine.max_fps = 60
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	$Workers/Death.animation_player().seek(1.6, true)
	$Workers/Death.animation_player().pause()
	if "--worker-overview" in OS.get_cmdline_user_args():
		$OverviewCamera.make_current()
		$ReviewLabels/Context.text = (
			"OFF-SHIFT WORKER / ASSET OVERVIEW\n" +
			"Left to right: death · run · walk · idle\n" +
			"Separate game-camera capture: 47 m · 42° · north-up"
		)
	get_tree().create_timer(PREVIEW_SECONDS).timeout.connect(_finish_preview)


## End the bounded preview without changing the main project launch scene.
func _finish_preview() -> void:
	get_tree().quit()
