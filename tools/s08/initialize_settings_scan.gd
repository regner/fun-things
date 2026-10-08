@tool
extends SceneTree
## Distinct ROOT-granted preparation: persist opt-out, finish first scan, then defer quit.

const OPT_OUT: String = "mcp_toolkit/performance/keep_editor_responsive_unfocused"

var _filesystem: EditorFileSystem
var _receipt: Dictionary = {}
var _finishing: bool = false


## Register completion observation before the initial editor scan starts.
func _initialize() -> void:
	_prepare.call_deferred()


## Persist through supported APIs and observe the real filesystem completion signal.
func _prepare() -> void:
	var settings: EditorSettings = EditorInterface.get_editor_settings()
	_filesystem = EditorInterface.get_resource_filesystem()
	var expected: String = OS.get_environment("XDG_CONFIG_HOME")
	expected += "/godot/editor_settings-4.8.tres"
	if settings == null or _filesystem == null or settings.resource_path != expected:
		print("S08_SETTINGS " + JSON.stringify({ "ok": false, "failure": "private editor context" }))
		quit(1)
		return

	_filesystem.filesystem_changed.connect(_scan_completed)
	settings.set_setting(OPT_OUT, false)
	var error: Error = ResourceSaver.save(settings, expected)
	var saved: EditorSettings = ResourceLoader.load(
		expected, "EditorSettings", ResourceLoader.CACHE_MODE_REPLACE
	) as EditorSettings
	var ok: bool = error == OK and saved != null and saved.has_setting(OPT_OUT)
	if ok:
		ok = (typeof(saved.get_setting(OPT_OUT)) == TYPE_BOOL
			and saved.get_setting(OPT_OUT) == false)

	_receipt = {
		"ok": ok, "path": expected, "key": OPT_OUT, "value": false, "save_error": error,
		"editor_hint": Engine.is_editor_hint(), "pid": OS.get_process_id(),
		"initial_scanning": _filesystem.is_scanning(),
		"initial_importing": _filesystem.is_importing(),
	}
	print("S08_PREP_INITIAL " + JSON.stringify(_receipt))
	if not ok:
		quit(1)


## Accept the signal only after the engine has joined the scan thread and cleared first_scan.
func _scan_completed() -> void:
	print("S08_PREP_SCAN " + JSON.stringify({
		"scanning": _filesystem.is_scanning(), "importing": _filesystem.is_importing(),
		"filesystem_present": _filesystem.get_filesystem() != null,
	}))
	if (_finishing or _filesystem.is_scanning() or _filesystem.is_importing()
			or _filesystem.get_filesystem() == null):
		return

	_finishing = true
	_finish.call_deferred()


## Leave the completion callback, recheck idle after the next frame, then request normal quit.
func _finish() -> void:
	await process_frame
	if _filesystem.is_scanning() or _filesystem.is_importing():
		_finishing = false
		return

	_receipt.scanning = _filesystem.is_scanning()
	_receipt.importing = _filesystem.is_importing()
	_receipt.filesystem_path = _filesystem.get_filesystem().get_path()
	_receipt.completion_signal = true
	_receipt.shutdown = "deferred SceneTree.quit after process_frame and idle recheck"
	print("S08_SETTINGS " + JSON.stringify(_receipt))
	quit(0 if _receipt.ok else 1)
