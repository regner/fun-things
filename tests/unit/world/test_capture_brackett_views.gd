extends GutTest
## Verifies the Brackett capture tool's output boundary and record-write failure reporting.

const CaptureViews := preload("res://tools/world/capture_brackett_views.gd")
const RECORD_DIRECTORY: String = "user://capture_brackett_views_test"


## Removes record fixtures so each case starts from an empty user directory.
func after_each() -> void:
	var directory: String = ProjectSettings.globalize_path(RECORD_DIRECTORY)
	var blocked: String = directory.path_join("capture.json")
	if DirAccess.dir_exists_absolute(blocked) or FileAccess.file_exists(blocked):
		DirAccess.remove_absolute(blocked)
	if DirAccess.dir_exists_absolute(directory):
		DirAccess.remove_absolute(directory)


## Proves resource schemes, relative paths and checkout paths are rejected as destinations.
func test_rejects_resource_relative_and_checkout_destinations() -> void:
	var project: String = _project_directory()
	var name: String = project.get_file()
	for rejected: String in [
		"res://review-captures",
		"user://review-captures",
		"review-captures",
		"../review-captures",
		project,
		project + "/review-captures",
		project.replace("/", "\\") + "\\review-captures",
		project.to_upper() + "/review-captures",
		project + "/../" + name + "/review-captures",
		project.get_base_dir() + "/elsewhere/../" + name + "/captures",
	]:
		assert_eq(CaptureViews.checked_output_directory(rejected), "", rejected)

	var rejected_arguments: Dictionary = CaptureViews.parse_arguments(
		PackedStringArray(["--views", "res://views.json", "--output", "res://review-captures"])
	)
	assert_true(rejected_arguments.has("error"))
	assert_false(DirAccess.dir_exists_absolute(project.path_join("review-captures")))


## Proves native destinations outside the checkout, including a sibling prefix, are accepted.
func test_accepts_native_destinations_outside_checkout() -> void:
	var project: String = _project_directory()
	var sibling: String = project + "_sibling/captures"
	assert_eq(CaptureViews.checked_output_directory(sibling), sibling)
	var outside: String = project.get_base_dir() + "/captures"
	assert_eq(CaptureViews.checked_output_directory(outside + "/"), outside)

	var arguments: Dictionary = CaptureViews.parse_arguments(
		PackedStringArray(["--views", "res://views.json", "--output", sibling])
	)
	assert_false(arguments.has("error"), str(arguments.get("error", "")))
	assert_eq(arguments.output, sibling)
	assert_true(CaptureViews.parse_arguments(PackedStringArray(["--output", sibling])).has("error"))


## Proves the capture record reports a blocked destination instead of claiming success.
func test_capture_record_write_reports_blocked_destination() -> void:
	var directory: String = ProjectSettings.globalize_path(RECORD_DIRECTORY)
	var record_path: String = directory.path_join("capture.json")
	assert_eq(DirAccess.make_dir_recursive_absolute(record_path), OK)
	assert_false(CaptureViews.write_capture_record(record_path, { "views": [] }))

	DirAccess.remove_absolute(record_path)
	assert_true(CaptureViews.write_capture_record(record_path, { "views": [] }))
	var written: Variant = JSON.parse_string(FileAccess.get_file_as_string(record_path))
	assert_eq(written, { "views": [] })


## Returns the checkout directory in normalized forward-slash form without a trailing slash.
func _project_directory() -> String:
	return ProjectSettings.globalize_path("res://").replace("\\", "/").trim_suffix("/")
