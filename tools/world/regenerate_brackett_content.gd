extends SceneTree
## Regenerates the Brackett content manifest from the saved Match and prints its signature.
##
## Run headless from the checkout root. Add `-- --write-signature` to update the Match after
## regenerating the manifest; without that opt-in argument, the tool remains read-only for Match.

const MATCH_SCENE_PATH: String = "res://scenes/match/match.tscn"
const CITY_DATA_PATH: NodePath = ^"CityData"
const WRITE_SIGNATURE_ARGUMENT: String = "--write-signature"
const SIGNATURE_LINE_PATTERN: String = '(?m)^content_signature = "[^\r\n]*"\r?$'
const EXIT_FAILURE: int = 1


## Preflights the opt-in write target, then defers work until the tree is initialized.
func _initialize() -> void:
	if WRITE_SIGNATURE_ARGUMENT in OS.get_cmdline_user_args():
		var count: int = _content_signature_line_count(MATCH_SCENE_PATH)
		if count != 1:
			_fail.bind("BRACKETT_CONTENT_SIGNATURE_LINE_COUNT %d" % count).call_deferred()
			return
	_run.call_deferred()


## Writes the manifest, optionally updates Match, then reports the verified saved signature.
func _run() -> void:
	var packed: PackedScene = _load_match_scene()
	if packed == null:
		_fail("BRACKETT_CONTENT_MATCH_LOAD_FAILED")
		return

	# Anchor descriptors hash global transforms, so the Match must be inside the tree.
	var match_root: Node = packed.instantiate()
	root.add_child(match_root)
	var city_data: CityData = match_root.get_node_or_null(CITY_DATA_PATH) as CityData
	if city_data == null:
		match_root.free()
		_fail("BRACKETT_CONTENT_CITY_DATA_MISSING")
		return

	var manifest: Dictionary = city_data.build_content_manifest()
	if manifest.is_empty():
		match_root.free()
		_fail(
			(
				"BRACKETT_CONTENT_MANIFEST_FAILED (missing dependency or more than %d rows)"
				% CityData.MAX_MANIFEST_RESOURCES
			)
		)
		return

	# Freeing the Match frees CityData, so keep values needed after releasing the scene file.
	var manifest_path: String = city_data.content_manifest_path
	if not _write_manifest(manifest_path, manifest):
		match_root.free()
		_fail("BRACKETT_CONTENT_MANIFEST_WRITE_FAILED " + manifest_path)
		return

	var signature: String = city_data.calculate_content_signature()
	var saved_signature: String = city_data.content_signature
	match_root.free()
	if signature.is_empty():
		_fail("BRACKETT_CONTENT_SIGNATURE_FAILED")
		return

	if WRITE_SIGNATURE_ARGUMENT in OS.get_cmdline_user_args():
		var checked: Dictionary = _write_and_recheck_signature(signature)
		if not checked.ok:
			_fail(checked.error)
			return
		signature = checked.signature
		saved_signature = checked.saved_signature

	_report_result_and_quit(manifest, signature, saved_signature)


## Prints the canonical result markers consumed by world-content lanes, then exits successfully.
func _report_result_and_quit(
	manifest: Dictionary, signature: String, saved_signature: String
) -> void:
	var rows: int = (manifest.resources as Array).size()
	print("BRACKETT_CONTENT_MANIFEST_ROWS %d of %d" % [rows, CityData.MAX_MANIFEST_RESOURCES])
	print("BRACKETT_CONTENT_SIGNATURE ", signature)
	print("BRACKETT_CONTENT_SAVED_SIGNATURE_MATCHES ", signature == saved_signature)
	quit()


## Writes one signature line and returns values freshly recomputed from the reloaded Match.
func _write_and_recheck_signature(signature: String) -> Dictionary:
	var write_result: Dictionary = rewrite_content_signature(MATCH_SCENE_PATH, signature)
	if not write_result.ok:
		return write_result

	var checked: Dictionary = _recheck_saved_signature()
	if not checked.ok:
		return checked
	if checked.signature != checked.saved_signature:
		return {
			"ok": false,
			"error": "BRACKETT_CONTENT_SAVED_SIGNATURE_MISMATCH_AFTER_WRITE",
		}
	return checked


## Counts exact content-signature property lines without loading a potentially invalid scene.
static func _content_signature_line_count(path: String) -> int:
	var content: String = FileAccess.get_file_as_string(path)
	var pattern := RegEx.create_from_string(SIGNATURE_LINE_PATTERN)
	return pattern.search_all(content).size()


## Replaces the sole exact content-signature property line while preserving all other bytes.
static func rewrite_content_signature(path: String, signature: String) -> Dictionary:
	var content: String = FileAccess.get_file_as_string(path)
	var pattern := RegEx.create_from_string(SIGNATURE_LINE_PATTERN)
	var matches: Array[RegExMatch] = pattern.search_all(content)
	if matches.size() != 1:
		return {
			"ok": false,
			"error": "BRACKETT_CONTENT_SIGNATURE_LINE_COUNT %d" % matches.size(),
		}

	var matched: RegExMatch = matches[0]
	var ending: String = "\r" if matched.get_string().ends_with("\r") else ""
	var replacement: String = 'content_signature = "%s"%s' % [signature, ending]
	var updated: String = (
		content.substr(0, matched.get_start()) + replacement + content.substr(matched.get_end())
	)
	var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return { "ok": false, "error": "BRACKETT_CONTENT_SIGNATURE_WRITE_FAILED " + path }
	var stored: bool = file.store_string(updated)
	file.close()
	if not stored:
		return { "ok": false, "error": "BRACKETT_CONTENT_SIGNATURE_WRITE_FAILED " + path }
	return { "ok": true }


## Loads Match without returning an earlier cached value after a signature rewrite.
func _load_match_scene() -> PackedScene:
	return (
		ResourceLoader.load(MATCH_SCENE_PATH, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
		as PackedScene
	)


## Reloads Match after writing and recomputes both sides of the saved-signature comparison.
func _recheck_saved_signature() -> Dictionary:
	var packed: PackedScene = _load_match_scene()
	if packed == null:
		return { "ok": false, "error": "BRACKETT_CONTENT_MATCH_RELOAD_FAILED" }
	var match_root: Node = packed.instantiate()
	root.add_child(match_root)
	var city_data: CityData = match_root.get_node_or_null(CITY_DATA_PATH) as CityData
	if city_data == null:
		match_root.free()
		return { "ok": false, "error": "BRACKETT_CONTENT_CITY_DATA_MISSING_AFTER_WRITE" }

	var signature: String = city_data.calculate_content_signature()
	var saved_signature: String = city_data.content_signature
	match_root.free()
	if signature.is_empty():
		return { "ok": false, "error": "BRACKETT_CONTENT_SIGNATURE_RECHECK_FAILED" }
	return { "ok": true, "signature": signature, "saved_signature": saved_signature }


## Stores the manifest in the canonical sorted, tab-indented, LF-terminated form.
func _write_manifest(path: String, manifest: Dictionary) -> bool:
	var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return false
	var stored: bool = file.store_string(JSON.stringify(manifest, "\t") + "\n")
	file.close()
	return stored


## Reports a failure and exits non-zero instead of leaving a stale manifest unnoticed.
func _fail(message: String) -> void:
	push_error(message)
	quit(EXIT_FAILURE)
