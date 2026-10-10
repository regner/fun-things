extends GutTest
## Verifies the opt-in Brackett signature writer against disposable scene copies.

const RegenerateBrackettContent := preload("res://tools/world/regenerate_brackett_content.gd")
const TEMP_DIRECTORY: String = "user://regenerate_brackett_content_test"
const FIXTURE_PATH: String = TEMP_DIRECTORY + "/fixture.tscn"
const COPY_PATH: String = TEMP_DIRECTORY + "/match_copy.tscn"
const CURRENT_SIGNATURE: String = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
const STALE_SIGNATURE: String = "0000000000000000000000000000000000000000000000000000000000000000"


## Removes every disposable scene copy after each signature-writer case.
func after_each() -> void:
	for path: String in [COPY_PATH, FIXTURE_PATH]:
		if FileAccess.file_exists(path):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	var directory: String = ProjectSettings.globalize_path(TEMP_DIRECTORY)
	if DirAccess.dir_exists_absolute(directory):
		DirAccess.remove_absolute(directory)


## Replaces one stale value without changing any surrounding scene text.
func test_rewrites_stale_signature_in_temporary_copy() -> void:
	var source: String = _scene_source('content_signature = "%s"' % STALE_SIGNATURE)
	_make_scene_copy(source)

	var result: Dictionary = RegenerateBrackettContent.rewrite_content_signature(
		COPY_PATH, CURRENT_SIGNATURE
	)

	assert_true(result.ok, str(result.get("error", "")))
	assert_eq(
		FileAccess.get_file_as_string(COPY_PATH),
		_scene_source('content_signature = "%s"' % CURRENT_SIGNATURE),
	)


## Leaves an already-current signature copy byte-for-byte unchanged.
func test_current_signature_is_a_no_op() -> void:
	var source: String = _scene_source('content_signature = "%s"' % CURRENT_SIGNATURE)
	_make_scene_copy(source)

	var result: Dictionary = RegenerateBrackettContent.rewrite_content_signature(
		COPY_PATH, CURRENT_SIGNATURE
	)

	assert_true(result.ok, str(result.get("error", "")))
	assert_eq(FileAccess.get_file_as_string(COPY_PATH), source)


## Rejects a scene copy with no signature property and does not alter it.
func test_rejects_missing_signature_line() -> void:
	var source: String = _scene_source("content_revision = 1")
	_make_scene_copy(source)

	var result: Dictionary = RegenerateBrackettContent.rewrite_content_signature(
		COPY_PATH, CURRENT_SIGNATURE
	)

	assert_false(result.ok)
	assert_eq(result.error, "BRACKETT_CONTENT_SIGNATURE_LINE_COUNT 0")
	assert_eq(FileAccess.get_file_as_string(COPY_PATH), source)


## Rejects a scene copy with duplicate signature properties and does not alter it.
func test_rejects_duplicated_signature_line() -> void:
	var source: String = _scene_source(
		'content_signature = "%s"\ncontent_signature = "%s"' % [STALE_SIGNATURE, CURRENT_SIGNATURE]
	)
	_make_scene_copy(source)

	var result: Dictionary = RegenerateBrackettContent.rewrite_content_signature(
		COPY_PATH, CURRENT_SIGNATURE
	)

	assert_false(result.ok)
	assert_eq(result.error, "BRACKETT_CONTENT_SIGNATURE_LINE_COUNT 2")
	assert_eq(FileAccess.get_file_as_string(COPY_PATH), source)


## Wraps one property block in enough scene text to detect collateral rewrites.
func _scene_source(properties: String) -> String:
	return (
		"[gd_scene format=3]\n\n"
		+ '[node name="Match" type="Node3D"]\n'
		+ properties
		+ '\nmetadata/example = "preserved"\n'
	)


## Writes a fixture and copies it to the disposable path used by the production helper.
func _make_scene_copy(source: String) -> void:
	var directory: String = ProjectSettings.globalize_path(TEMP_DIRECTORY)
	assert_eq(DirAccess.make_dir_recursive_absolute(directory), OK)
	var fixture: FileAccess = FileAccess.open(FIXTURE_PATH, FileAccess.WRITE)
	assert_not_null(fixture)
	assert_true(fixture.store_string(source))
	fixture.close()
	assert_eq(
		(
			DirAccess
			. copy_absolute(
				ProjectSettings.globalize_path(FIXTURE_PATH),
				ProjectSettings.globalize_path(COPY_PATH),
			)
		),
		OK,
	)
