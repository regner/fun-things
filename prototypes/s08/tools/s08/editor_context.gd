@tool
extends SceneTree
## Read-only actual editor startup context; does not alter settings or authored nodes.

const OPT_OUT: String = "mcp_toolkit/performance/keep_editor_responsive_unfocused"


## Observe after the normal editor singleton has been constructed.
func _initialize() -> void:
	_observe.call_deferred()


## Bind actual project/process/version and live private EditorSettings before authentication.
func _observe() -> void:
	var settings: EditorSettings = EditorInterface.get_editor_settings()
	print("S08_EDITOR_CONTEXT " + JSON.stringify({
		"editor_hint": Engine.is_editor_hint(), "pid": OS.get_process_id(),
		"project": ProjectSettings.globalize_path("res://"), "version": Engine.get_version_info(),
		"boost": settings.get_setting(OPT_OUT), "settings_path": settings.resource_path,
	}))
