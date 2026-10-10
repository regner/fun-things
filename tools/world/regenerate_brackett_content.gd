extends SceneTree
## Regenerates the Brackett content manifest from the saved Match and prints its signature.
##
## Run headless from the checkout root:
## godot --headless --path . --script res://tools/world/regenerate_brackett_content.gd
## Copy the printed signature into `scenes/match/match.tscn` `content_signature` when it changes.

const MATCH_SCENE_PATH: String = "res://scenes/match/match.tscn"
const CITY_DATA_PATH: NodePath = ^"CityData"
const EXIT_FAILURE: int = 1


## Defers the run until the scene tree is initialized.
func _initialize() -> void:
	_run.call_deferred()


## Writes the canonical manifest, then reports the signature the saved Match must carry.
func _run() -> void:
	var packed: PackedScene = load(MATCH_SCENE_PATH) as PackedScene
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
			"BRACKETT_CONTENT_MANIFEST_FAILED (missing dependency or more than %d rows)"
			% CityData.MAX_MANIFEST_RESOURCES
		)
		return

	# Freeing the Match frees CityData, so keep the path for the failure message.
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

	var rows: int = (manifest.resources as Array).size()
	print("BRACKETT_CONTENT_MANIFEST_ROWS %d of %d" % [rows, CityData.MAX_MANIFEST_RESOURCES])
	print("BRACKETT_CONTENT_SIGNATURE ", signature)
	print("BRACKETT_CONTENT_SAVED_SIGNATURE_MATCHES ", signature == saved_signature)
	quit()


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
