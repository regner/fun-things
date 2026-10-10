extends GutTest
## Verifies the saved Boot composition reaches and persists its injected settings view.

const BOOT_SCENE: PackedScene = preload("res://scenes/boot/boot.tscn")


## Starts each Boot persistence proof without settings from an earlier test process.
func before_each() -> void:
	_remove_settings_files()


## Restores process-global presentation state and removes the persisted proof file.
func after_each() -> void:
	for bus_name: StringName in LocalSettings.AUDIO_BUSES:
		var bus_index: int = AudioServer.get_bus_index(bus_name)
		AudioServer.set_bus_volume_db(bus_index, 0.0)
		AudioServer.set_bus_mute(bus_index, false)
	Engine.max_fps = 0
	_remove_settings_files()


## Opens Settings from the running Boot, saves a change, and reloads it in a fresh Boot.
func test_boot_settings_is_reachable_and_persists_across_restart() -> void:
	var boot: Boot = BOOT_SCENE.instantiate()
	add_child_autofree(boot)
	await get_tree().process_frame
	var main_menu: MainMenu = boot.get_node("View/MainMenu")
	var settings_menu: SettingsMenu = boot.get_node("View/SettingsMenu")
	var local_settings: LocalSettings = boot.get_node("LocalSettings")

	main_menu.get_node("%SettingsButton").pressed.emit()

	assert_false(main_menu.visible)
	assert_true(settings_menu.visible)
	var music_slider: HSlider = settings_menu.get_node("%MusicVolume")
	music_slider.value = 0.47
	music_slider.value_changed.emit(music_slider.value)
	settings_menu.get_node("%SaveButton").pressed.emit()
	assert_false(settings_menu.visible)
	assert_true(main_menu.visible)
	assert_true(FileAccess.file_exists(LocalSettings.DEFAULT_PATH))
	assert_eq(local_settings.snapshot().music_volume, 0.47)

	boot.queue_free()
	await get_tree().process_frame
	var restarted_boot: Boot = BOOT_SCENE.instantiate()
	add_child_autofree(restarted_boot)
	await get_tree().process_frame
	var restarted_settings: LocalSettings = restarted_boot.get_node("LocalSettings")
	var restarted_menu: MainMenu = restarted_boot.get_node("View/MainMenu")
	var restarted_settings_menu: SettingsMenu = restarted_boot.get_node("View/SettingsMenu")

	assert_eq(restarted_settings.snapshot().music_volume, 0.47)
	restarted_menu.get_node("%SettingsButton").pressed.emit()
	assert_true(restarted_settings_menu.visible)
	assert_eq(restarted_settings_menu.get_node("%MusicVolume").value, 0.47)


## Removes the canonical file and each bounded transaction sibling when present.
func _remove_settings_files() -> void:
	for suffix: String in ["", ".tmp", ".previous"]:
		var path: String = LocalSettings.DEFAULT_PATH + suffix
		if FileAccess.file_exists(path):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
