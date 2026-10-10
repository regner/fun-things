class_name SettingsMenu
extends Control
## Presents device-local settings through an explicitly injected LocalSettings owner.

signal closed

var _settings: LocalSettings
var _opening_snapshot: Dictionary = {}

@onready var _master_volume: HSlider = %MasterVolume
@onready var _music_volume: HSlider = %MusicVolume
@onready var _sfx_volume: HSlider = %SFXVolume
@onready var _master_mute: CheckButton = %MasterMute
@onready var _music_mute: CheckButton = %MusicMute
@onready var _sfx_mute: CheckButton = %SFXMute
@onready var _window_mode: OptionButton = %WindowMode
@onready var _vsync: CheckButton = %VSync
@onready var _fps_cap: OptionButton = %FPSCap
@onready var _feedback: Label = %Feedback
@onready var _save_button: Button = %SaveButton


## Populates fixed display choices while remaining hidden until configured and opened.
func _ready() -> void:
	_window_mode.add_item("Windowed")
	_window_mode.set_item_metadata(0, LocalSettings.WINDOW_MODE_WINDOWED)
	_window_mode.add_item("Fullscreen")
	_window_mode.set_item_metadata(1, LocalSettings.WINDOW_MODE_FULLSCREEN)
	_fps_cap.add_item("30 FPS")
	_fps_cap.set_item_metadata(0, LocalSettings.FPS_CAP_30)
	_fps_cap.add_item("60 FPS")
	_fps_cap.set_item_metadata(1, LocalSettings.FPS_CAP_60)
	visible = false


## Handles Escape without intercepting gameplay while the settings view is hidden.
func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		cancel()


## Injects the process-lifetime owner without depending on Boot's internal node paths.
func configure(settings: LocalSettings) -> bool:
	if settings == null:
		return false
	_settings = settings
	return true


## Opens with current values and focuses the first keyboard-adjustable control.
func open() -> bool:
	if _settings == null:
		return false

	_opening_snapshot = _settings.snapshot()
	_sync_controls(_opening_snapshot)
	_feedback.text = _settings.last_recovery_warning
	visible = true
	_master_volume.grab_focus()
	return true


## Cancels live preview by restoring the complete opening snapshot.
func cancel() -> void:
	if _settings != null and not _opening_snapshot.is_empty():
		_settings.apply_snapshot(_opening_snapshot)
	visible = false
	closed.emit()


## Previews Master gain and mute together from authored controls.
func _on_master_changed(_value: float = 0.0) -> void:
	_preview_audio(LocalSettings.BUS_MASTER, _master_volume, _master_mute)


## Previews Music gain and mute together from authored controls.
func _on_music_changed(_value: float = 0.0) -> void:
	_preview_audio(LocalSettings.BUS_MUSIC, _music_volume, _music_mute)


## Previews SFX gain and mute together from authored controls.
func _on_sfx_changed(_value: float = 0.0) -> void:
	_preview_audio(LocalSettings.BUS_SFX, _sfx_volume, _sfx_mute)


## Previews the selected window, VSync, and finite frame-cap combination.
func _on_display_changed(_value: Variant = null) -> void:
	if _settings == null:
		return

	var mode := StringName(_window_mode.get_selected_metadata())
	var cap: int = int(_fps_cap.get_selected_metadata())
	_settings.preview_display(mode, _vsync.button_pressed, cap)


## Persists the current preview and closes only after the atomic replacement succeeds.
func _on_save_pressed() -> void:
	if _settings == null:
		_feedback.text = "Settings are unavailable."
		return

	var save_error: Error = _settings.save_settings()
	if save_error != OK:
		_feedback.text = "Could not save settings. Your previous file was kept."
		_save_button.grab_focus()
		return

	_opening_snapshot = _settings.snapshot()
	visible = false
	closed.emit()


## Restores defaults as a live preview that still requires an explicit save.
func _on_defaults_pressed() -> void:
	if _settings == null:
		return

	_settings.restore_defaults()
	_sync_controls(_settings.snapshot())
	_feedback.text = "Defaults previewed. Save to keep them."


## Routes the authored back button through the same rollback contract as Escape.
func _on_back_pressed() -> void:
	cancel()


## Applies one slider/check pair without giving the UI ownership of audio state.
func _preview_audio(
	bus_name: StringName,
	slider: HSlider,
	mute: CheckButton,
) -> void:
	if _settings != null:
		_settings.preview_audio(bus_name, slider.value, mute.button_pressed)


## Mirrors one detached state view without saving or recursively previewing it.
func _sync_controls(values: Dictionary) -> void:
	_master_volume.set_value_no_signal(float(values.master_volume))
	_music_volume.set_value_no_signal(float(values.music_volume))
	_sfx_volume.set_value_no_signal(float(values.sfx_volume))
	_master_mute.set_pressed_no_signal(bool(values.master_muted))
	_music_mute.set_pressed_no_signal(bool(values.music_muted))
	_sfx_mute.set_pressed_no_signal(bool(values.sfx_muted))
	_select_metadata(_window_mode, values.window_mode)
	_vsync.set_pressed_no_signal(bool(values.vsync_enabled))
	_select_metadata(_fps_cap, values.fps_cap)


## Selects a fixed authored option by its stable setting value.
func _select_metadata(control: OptionButton, expected: Variant) -> void:
	for index: int in control.item_count:
		if control.get_item_metadata(index) == expected:
			control.select(index)
			return
