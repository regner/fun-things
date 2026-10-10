extends GutTest
## Verifies validated local settings, recovery, atomic persistence, preview, and UI access.

const SETTINGS_SCENE: PackedScene = preload("res://scenes/ui/settings_menu.tscn")
const MAIN_MENU_SCENE: PackedScene = preload("res://scenes/ui/main_menu.tscn")
const FAILING_ROLLBACK_SETTINGS: GDScript = preload(
	"res://tests/unit/settings/fixtures/failing_rollback_settings.gd"
)

var _paths_to_remove: Array[String] = []


## Restores process-global presentation services and removes each test's user files.
func after_each() -> void:
	for bus_name: StringName in LocalSettings.AUDIO_BUSES:
		var bus_index: int = AudioServer.get_bus_index(bus_name)
		AudioServer.set_bus_volume_db(bus_index, 0.0)
		AudioServer.set_bus_mute(bus_index, false)
	Engine.max_fps = 0
	for path: String in _paths_to_remove:
		_remove_path(path)
	_paths_to_remove.clear()


## Applies explicit safe defaults when no prior file exists.
func test_missing_file_uses_defaults_and_applies_them() -> void:
	var path: String = _test_path("defaults")
	var settings := _new_settings()

	assert_eq(settings.load_settings(path), OK)
	assert_eq(settings.snapshot().master_volume, 1.0)
	assert_eq(settings.snapshot().music_volume, 1.0)
	assert_eq(settings.snapshot().sfx_volume, 1.0)
	assert_eq(LocalSettings.DEFAULT_PATH, "user://settings.cfg")
	assert_eq(settings.snapshot().window_mode, LocalSettings.WINDOW_MODE_WINDOWED)
	assert_true(settings.snapshot().vsync_enabled)
	assert_eq(Engine.max_fps, LocalSettings.FPS_CAP_60)
	assert_false(settings.last_load_recovered)


## Clamps finite persisted gains while retaining exact mute and display values.
func test_load_validates_and_clamps_persisted_values() -> void:
	var path: String = _test_path("clamp")
	var config := ConfigFile.new()
	config.set_value("meta", "schema_version", LocalSettings.SCHEMA_VERSION)
	config.set_value("audio", "master_volume", 5.0)
	config.set_value("audio", "music_volume", -2.0)
	config.set_value("audio", "sfx_volume", 0.35)
	config.set_value("audio", "master_muted", true)
	config.set_value("audio", "music_muted", false)
	config.set_value("audio", "sfx_muted", true)
	config.set_value("display", "window_mode", LocalSettings.WINDOW_MODE_WINDOWED)
	config.set_value("display", "vsync_enabled", false)
	config.set_value("display", "fps_cap", LocalSettings.FPS_CAP_30)
	assert_eq(config.save(path), OK)
	var settings := _new_settings()

	assert_eq(settings.load_settings(path), OK)
	var loaded: Dictionary = settings.snapshot()
	assert_eq(loaded.master_volume, 1.0)
	assert_eq(loaded.music_volume, 0.0)
	assert_eq(loaded.sfx_volume, 0.35)
	assert_true(loaded.master_muted)
	assert_true(loaded.sfx_muted)
	assert_false(loaded.vsync_enabled)
	assert_eq(Engine.max_fps, LocalSettings.FPS_CAP_30)


## Moves malformed data aside and recovers the complete safe default transaction.
func test_corrupt_file_is_backed_up_before_default_recovery() -> void:
	var path: String = _test_path("corrupt")
	var file := FileAccess.open(path, FileAccess.WRITE)
	assert_not_null(file)
	file.store_string("not a ConfigFile")
	file.close()
	var settings := _new_settings()

	assert_eq(settings.load_settings(path), OK)
	assert_true(settings.last_load_recovered)
	assert_false(settings.last_backup_path.is_empty())
	_paths_to_remove.append(settings.last_backup_path)
	assert_true(FileAccess.file_exists(settings.last_backup_path))
	assert_false(FileAccess.file_exists(path))
	assert_eq(settings.snapshot().music_volume, LocalSettings.DEFAULT_MUSIC_VOLUME)
	assert_eq(settings.last_recovery_warning, LocalSettings.CORRUPT_RECOVERY_WARNING)

	var menu: SettingsMenu = SETTINGS_SCENE.instantiate()
	assert_true(menu.configure(settings))
	add_child_autofree(menu)
	await get_tree().process_frame
	assert_true(menu.open())
	assert_eq(menu.get_node("%Feedback").text, LocalSettings.CORRUPT_RECOVERY_WARNING)


## Treats wrong known-value types as one corrupt transaction rather than partial state.
func test_invalid_types_recover_whole_file_instead_of_partially_loading() -> void:
	var path: String = _test_path("types")
	var config := ConfigFile.new()
	config.set_value("meta", "schema_version", LocalSettings.SCHEMA_VERSION)
	config.set_value("audio", "master_volume", "loud")
	config.set_value("audio", "master_muted", 1)
	assert_eq(config.save(path), OK)
	var settings := _new_settings()

	assert_eq(settings.load_settings(path), OK)
	_paths_to_remove.append(settings.last_backup_path)
	assert_true(settings.last_load_recovered)
	assert_eq(settings.snapshot().master_volume, LocalSettings.DEFAULT_MASTER_VOLUME)
	assert_false(settings.snapshot().master_muted)


## Replaces an existing file through a temporary and survives a fresh owner restart.
func test_atomic_save_replaces_existing_file_and_restarts_cleanly() -> void:
	var path: String = _test_path("restart")
	var settings := _new_settings()
	assert_eq(settings.load_settings(path), OK)
	assert_eq(settings.save_settings(), OK)
	assert_true(settings.preview_audio(LocalSettings.BUS_MUSIC, 0.42, true))
	assert_true(
		(
			settings
			. preview_display(
				LocalSettings.WINDOW_MODE_WINDOWED,
				false,
				LocalSettings.FPS_CAP_30,
			)
		)
	)
	assert_eq(settings.save_settings(), OK)

	var restarted := _new_settings()
	assert_eq(restarted.load_settings(path), OK)
	assert_eq(restarted.snapshot(), settings.snapshot())
	assert_false(FileAccess.file_exists(path + ".tmp"))
	assert_false(FileAccess.file_exists(path + ".previous"))


## Restores a preserved last-good file when promotion never established a destination.
func test_restart_restores_previous_when_destination_is_absent() -> void:
	var path: String = _test_path("previous_only")
	_write_settings(path + ".previous", 0.31)
	var settings := _new_settings()

	assert_eq(settings.load_settings(path), OK)
	assert_eq(settings.snapshot().music_volume, 0.31)
	assert_true(FileAccess.file_exists(path))
	assert_false(FileAccess.file_exists(path + ".previous"))
	assert_eq(settings.last_recovery_warning, LocalSettings.TRANSACTION_RECOVERY_WARNING)
	_assert_restart_value(path, 0.31)


## Rejects an uncommitted temporary candidate while restoring the preserved destination.
func test_restart_prefers_previous_over_temporary_when_destination_is_absent() -> void:
	var path: String = _test_path("previous_and_tmp")
	_write_settings(path + ".previous", 0.32)
	_write_settings(path + ".tmp", 0.82)
	var settings := _new_settings()

	assert_eq(settings.load_settings(path), OK)
	assert_eq(settings.snapshot().music_volume, 0.32)
	assert_false(FileAccess.file_exists(path + ".previous"))
	assert_false(FileAccess.file_exists(path + ".tmp"))
	_assert_restart_value(path, 0.32)


## Keeps the committed destination when a crash leaves an unpromoted temporary file.
func test_restart_discards_temporary_when_valid_destination_exists() -> void:
	var path: String = _test_path("destination_and_tmp")
	_write_settings(path, 0.33)
	_write_settings(path + ".tmp", 0.83)
	var settings := _new_settings()

	assert_eq(settings.load_settings(path), OK)
	assert_eq(settings.snapshot().music_volume, 0.33)
	assert_false(FileAccess.file_exists(path + ".tmp"))
	_assert_restart_value(path, 0.33)


## Validates the promoted destination before deleting the preserved prior generation.
func test_restart_keeps_valid_promoted_destination_and_removes_previous() -> void:
	var path: String = _test_path("destination_and_previous")
	_write_settings(path, 0.84)
	_write_settings(path + ".previous", 0.34)
	var settings := _new_settings()

	assert_eq(settings.load_settings(path), OK)
	assert_eq(settings.snapshot().music_volume, 0.84)
	assert_false(FileAccess.file_exists(path + ".previous"))
	_assert_restart_value(path, 0.84)


## Restores the prior generation when an invalid destination survived promotion.
func test_restart_replaces_invalid_destination_with_valid_previous() -> void:
	var path: String = _test_path("invalid_destination")
	var invalid_file := FileAccess.open(path, FileAccess.WRITE)
	assert_not_null(invalid_file)
	invalid_file.store_string("invalid promoted settings")
	invalid_file.close()
	_write_settings(path + ".previous", 0.35)
	var settings := _new_settings()

	assert_eq(settings.load_settings(path), OK)
	_paths_to_remove.append(settings.last_backup_path)
	assert_eq(settings.snapshot().music_volume, 0.35)
	assert_true(FileAccess.file_exists(settings.last_backup_path))
	assert_eq(settings.last_recovery_warning, LocalSettings.CORRUPT_RECOVERY_WARNING)
	assert_false(FileAccess.file_exists(path + ".previous"))
	_assert_restart_value(path, 0.35)


## Discards a temporary-only first-save artifact because it was never committed.
func test_restart_discards_temporary_when_no_committed_file_exists() -> void:
	var path: String = _test_path("tmp_only")
	_write_settings(path + ".tmp", 0.86)
	var settings := _new_settings()

	assert_eq(settings.load_settings(path), OK)
	assert_eq(settings.snapshot().music_volume, 1.0)
	assert_false(FileAccess.file_exists(path))
	assert_false(FileAccess.file_exists(path + ".tmp"))
	assert_eq(settings.last_recovery_warning, LocalSettings.TRANSACTION_RECOVERY_WARNING)


## Propagates a rollback rename failure and leaves the prior generation recoverable.
func test_save_reports_rollback_failure_without_losing_previous() -> void:
	var path: String = _test_path("rollback_failure")
	_write_settings(path, 0.36)
	var settings: LocalSettings = FAILING_ROLLBACK_SETTINGS.new()
	add_child_autofree(settings)
	assert_eq(settings.load_settings(path), OK)
	assert_true(settings.preview_audio(LocalSettings.BUS_MUSIC, 0.87, false))

	assert_eq(settings.save_settings(), ERR_CANT_OPEN)
	assert_eq(settings.last_save_error, ERR_CANT_OPEN)
	assert_false(FileAccess.file_exists(path))
	assert_true(FileAccess.file_exists(path + ".previous"))
	_assert_restart_value(path, 0.36)


## Reports an unwritable temporary path without creating a partial destination.
func test_save_failure_is_reported_and_cleans_temporary_file() -> void:
	var directory: String = "user://m1_d5_missing_" + str(Time.get_ticks_usec())
	var path: String = directory + "/settings.cfg"
	_paths_to_remove.append(path)
	_paths_to_remove.append(path + ".tmp")
	var settings := _new_settings()
	assert_eq(settings.load_settings(path), OK)
	var observed_error: Array[Error] = []
	settings.save_completed.connect(func(error: Error) -> void: observed_error.append(error))

	var save_error: Error = settings.save_settings()

	assert_ne(save_error, OK)
	assert_eq(settings.last_save_error, save_error)
	assert_eq(observed_error, [save_error])
	assert_false(FileAccess.file_exists(path))
	assert_false(FileAccess.file_exists(path + ".tmp"))


## Changes bus state immediately without changing A3.2's child routing or effects.
func test_audio_preview_is_live_and_limited_to_owned_buses() -> void:
	var settings := _new_settings()
	var music_index: int = AudioServer.get_bus_index(LocalSettings.BUS_MUSIC)
	var original_send: StringName = AudioServer.get_bus_send(music_index)
	var original_effect_count: int = AudioServer.get_bus_effect_count(music_index)

	assert_true(settings.preview_audio(LocalSettings.BUS_MUSIC, 0.25, true))

	assert_true(is_equal_approx(AudioServer.get_bus_volume_db(music_index), linear_to_db(0.25)))
	assert_true(AudioServer.is_bus_mute(music_index))
	assert_eq(AudioServer.get_bus_send(music_index), original_send)
	assert_eq(AudioServer.get_bus_effect_count(music_index), original_effect_count)
	assert_false(settings.preview_audio(&"Weapons", 0.5, false))


## Opens the saved settings scene with injected state and restores preview on cancel.
func test_settings_scene_is_keyboard_focused_and_cancel_restores_preview() -> void:
	var settings := _new_settings()
	var menu: SettingsMenu = SETTINGS_SCENE.instantiate()
	assert_true(menu.configure(settings))
	add_child_autofree(menu)
	await get_tree().process_frame
	assert_true(menu.open())
	await get_tree().process_frame
	var master_slider: HSlider = menu.get_node("%MasterVolume")
	master_slider.value = 0.5
	master_slider.value_changed.emit(master_slider.value)
	assert_true(is_equal_approx(settings.snapshot().master_volume, master_slider.value))
	assert_eq(get_viewport().gui_get_focus_owner(), master_slider)

	menu.cancel()

	assert_false(menu.visible)
	assert_true(is_equal_approx(settings.snapshot().master_volume, 1.0))


## Keeps the menu open with actionable feedback when its atomic save cannot start.
func test_settings_scene_reports_save_failure_without_discarding_preview() -> void:
	var directory: String = "user://m1_d5_ui_missing_" + str(Time.get_ticks_usec())
	var path: String = directory + "/settings.cfg"
	var settings := _new_settings()
	assert_eq(settings.load_settings(path), OK)
	var menu: SettingsMenu = SETTINGS_SCENE.instantiate()
	assert_true(menu.configure(settings))
	add_child_autofree(menu)
	await get_tree().process_frame
	assert_true(menu.open())

	var save_button: Button = menu.get_node("%SaveButton")
	save_button.pressed.emit()

	assert_true(menu.visible)
	assert_string_contains(menu.get_node("%Feedback").text, "Could not save")
	assert_eq(get_viewport().gui_get_focus_owner(), save_button)


## Exposes the Settings entry as navigation intent without owning the service or screen.
func test_main_menu_settings_entry_emits_request() -> void:
	var main_menu: MainMenu = MAIN_MENU_SCENE.instantiate()
	add_child_autofree(main_menu)
	var requests: Array[bool] = []
	main_menu.settings_requested.connect(func() -> void: requests.append(true))
	var button: Button = main_menu.get_node("%SettingsButton")

	button.pressed.emit()

	assert_eq(requests, [true])


## Creates a tree-owned settings node through the production public API.
func _new_settings() -> LocalSettings:
	var settings := LocalSettings.new()
	add_child_autofree(settings)
	return settings


## Allocates one isolated user path and tracks transaction siblings for cleanup.
func _test_path(label: String) -> String:
	var path: String = "user://m1_d5_%s_%d.cfg" % [label, Time.get_ticks_usec()]
	_paths_to_remove.append(path)
	_paths_to_remove.append(path + ".tmp")
	_paths_to_remove.append(path + ".previous")
	return path


## Writes one complete production schema to construct a specific transaction generation.
func _write_settings(path: String, music_volume: float) -> void:
	var config := ConfigFile.new()
	config.set_value("meta", "schema_version", LocalSettings.SCHEMA_VERSION)
	config.set_value("audio", "master_volume", 1.0)
	config.set_value("audio", "music_volume", music_volume)
	config.set_value("audio", "sfx_volume", 1.0)
	config.set_value("audio", "master_muted", false)
	config.set_value("audio", "music_muted", true)
	config.set_value("audio", "sfx_muted", false)
	config.set_value("display", "window_mode", LocalSettings.WINDOW_MODE_WINDOWED)
	config.set_value("display", "vsync_enabled", true)
	config.set_value("display", "fps_cap", LocalSettings.FPS_CAP_60)
	assert_eq(config.save(path), OK)


## Proves a second process-local owner sees the recovered committed generation.
func _assert_restart_value(path: String, expected_music_volume: float) -> void:
	var restarted := _new_settings()
	assert_eq(restarted.load_settings(path), OK)
	assert_eq(restarted.snapshot().music_volume, expected_music_volume)
	assert_true(restarted.snapshot().music_muted)


## Removes one user file when it exists.
func _remove_path(path: String) -> void:
	if not path.is_empty() and FileAccess.file_exists(path):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
