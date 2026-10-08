extends SceneTree
## Pre-auth initialization only; run in the explicitly owned addon-disabled editor project.

const OPT_OUT: String = "mcp_toolkit/performance/keep_editor_responsive_unfocused"


## Wait until the editor singleton has completed construction before persisting the opt-out.
func _initialize() -> void:
	_prepare.call_deferred()


## Save through the engine serializer and require an independent cache-replacing readback.
func _prepare() -> void:
	var settings: EditorSettings = EditorInterface.get_editor_settings()
	var expected: String = OS.get_environment("XDG_CONFIG_HOME")
	expected += "/godot/editor_settings-4.8.tres"
	if settings == null or settings.resource_path != expected:
		print("S08_SETTINGS " + JSON.stringify({
			"ok": false, "failure": "private settings path",
		}))
		quit(1)
		return

	settings.set_setting(OPT_OUT, false)
	var error: Error = ResourceSaver.save(settings, expected)
	var saved: EditorSettings = ResourceLoader.load(
		expected, "EditorSettings", ResourceLoader.CACHE_MODE_REPLACE
	) as EditorSettings
	var ok: bool = error == OK and saved != null and saved.has_setting(OPT_OUT)
	if ok:
		ok = (typeof(saved.get_setting(OPT_OUT)) == TYPE_BOOL
			and saved.get_setting(OPT_OUT) == false)

	print("S08_SETTINGS " + JSON.stringify({
		"ok": ok, "path": expected, "key": OPT_OUT, "value": false, "save_error": error,
		"editor_hint": Engine.is_editor_hint(), "pid": OS.get_process_id(),
	}))
	quit(0 if ok else 1)
