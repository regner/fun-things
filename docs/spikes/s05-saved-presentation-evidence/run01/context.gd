@tool
extends SceneTree
## Reports actual private editor context and initializes only the granted setting.

const BOOST: String = "mcp_toolkit/performance/keep_editor_responsive_unfocused"


## Waits until the editor singleton has been constructed by normal startup.
func _initialize() -> void:
	call_deferred("_probe")


## Saves an engine-generated private settings resource or reads it before authentication.
func _probe() -> void:
	var settings: EditorSettings = EditorInterface.get_editor_settings()
	var initialize: bool = "--initialize" in OS.get_cmdline_user_args()
	var error: int = OK
	if initialize:
		settings.set_setting(BOOST, false)
		error = ResourceSaver.save(settings, settings.get_path())

	print("S05_CONTEXT " + JSON.stringify({"editor_hint": Engine.is_editor_hint(),
		"pid": OS.get_process_id(), "project": ProjectSettings.globalize_path("res://"),
		"version": Engine.get_version_info(), "boost": settings.get_setting(BOOST),
		"settings_path": settings.get_path(), "save_error": error}))
	if initialize:
		quit(error)
