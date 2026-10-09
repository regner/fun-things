extends Node
## Real-project entrypoint and bounded exported-build smoke observer.

const SMOKE_ARGUMENT: String = "--s08-x-export-smoke"
const INTERSECTION_PATH: String = "res://tests/fixtures/s06/intersection.tscn"
const SMOKE_FRAMES: int = 30

var _smoke_frames_remaining: int = 0
var _smoke_failures: Array[String] = []

@onready var _intersection: Node = $Intersection


## Verifies export-only exclusions after the saved intersection enters the scene tree.
func _ready() -> void:
	if OS.has_feature("editor"):
		return

	_check(get_tree().root.get_node_or_null("MCPRuntimeServer") == null,
		"MCP runtime autoload node is absent")
	_check(not ProjectSettings.has_setting("autoload/MCPRuntimeServer"),
		"MCP runtime autoload setting is absent")
	_check(not ClassDB.class_exists("Steam"), "GodotSteam class is absent")
	_check(not Engine.has_singleton("Steam"), "GodotSteam singleton is absent")
	_check(_intersection.scene_file_path == INTERSECTION_PATH,
		"saved S06 intersection is instanced")
	print("S08-X " + JSON.stringify({
		"event": "boot",
		"ok": _smoke_failures.is_empty(),
		"failures": _smoke_failures,
		"intersection": _intersection.scene_file_path,
		"max_fps": Engine.max_fps,
	}))
	if SMOKE_ARGUMENT not in OS.get_cmdline_user_args():
		return

	Engine.max_fps = 60
	_smoke_frames_remaining = SMOKE_FRAMES
	set_process(true)


## Ends the bounded smoke after rendered frames have exercised the real main scene.
func _process(_delta: float) -> void:
	if _smoke_frames_remaining <= 0:
		set_process(false)
		return

	_smoke_frames_remaining -= 1
	if _smoke_frames_remaining > 0:
		return

	print("S08-X " + JSON.stringify({
		"event": "smoke_complete",
		"ok": _smoke_failures.is_empty(),
		"frames": SMOKE_FRAMES,
		"max_fps": Engine.max_fps,
		"window_size": get_window().size,
	}))
	get_tree().quit(0 if _smoke_failures.is_empty() else 1)


## Records one independently named export contract without release-disabled assertions.
func _check(condition: bool, contract: String) -> void:
	if not condition:
		_smoke_failures.append(contract)
