class_name LocalSettings
extends Node
## Owns validated device-local presentation settings and their durable user-file lifecycle.

signal changed(snapshot: Dictionary)
signal save_completed(error: Error)

const SCHEMA_VERSION: int = 1
const DEFAULT_PATH: String = "user://local_settings.cfg"
const BUS_MASTER: StringName = &"Master"
const BUS_MUSIC: StringName = &"Music"
const BUS_SFX: StringName = &"SFX"
const AUDIO_BUSES: Array[StringName] = [BUS_MASTER, BUS_MUSIC, BUS_SFX]
const WINDOW_MODE_WINDOWED: StringName = &"windowed"
const WINDOW_MODE_FULLSCREEN: StringName = &"fullscreen"
const FPS_CAP_30: int = 30
const FPS_CAP_60: int = 60
const FPS_CAPS: Array[int] = [FPS_CAP_30, FPS_CAP_60]
const MIN_LINEAR_VOLUME: float = 0.001
const DEFAULT_MASTER_VOLUME: float = 1.0
const DEFAULT_MUSIC_VOLUME: float = 0.8
const DEFAULT_SFX_VOLUME: float = 0.8

var last_backup_path: String = ""
var last_load_recovered: bool = false
var last_save_error: Error = OK
var _storage_path: String = DEFAULT_PATH
var _master_volume: float = DEFAULT_MASTER_VOLUME
var _music_volume: float = DEFAULT_MUSIC_VOLUME
var _sfx_volume: float = DEFAULT_SFX_VOLUME
var _master_muted: bool = false
var _music_muted: bool = false
var _sfx_muted: bool = false
var _window_mode: StringName = WINDOW_MODE_WINDOWED
var _vsync_enabled: bool = true
var _fps_cap: int = FPS_CAP_60


## Loads validated settings, recovering a corrupt file to a backup before using defaults.
func load_settings(path: String = "") -> Error:
	_storage_path = _resolved_path(path)
	last_backup_path = ""
	last_load_recovered = false
	_set_defaults()
	var config := ConfigFile.new()
	var load_error: Error = config.load(_storage_path)
	if load_error == ERR_FILE_NOT_FOUND:
		apply()
		changed.emit(snapshot())
		return OK
	if load_error != OK:
		return _recover_corrupt()

	var values: Dictionary = _validated_values(config)
	if values.is_empty():
		return _recover_corrupt()

	_assign_values(values)
	apply()
	changed.emit(snapshot())
	return OK


## Atomically replaces the settings file after a complete temporary write.
func save_settings(path: String = "") -> Error:
	_storage_path = _resolved_path(path)
	var temporary_path: String = _storage_path + ".tmp"
	_remove_if_present(temporary_path)
	var save_error: Error = _build_config().save(temporary_path)
	if save_error == OK:
		save_error = _replace_from_temporary(temporary_path)
	if save_error != OK:
		_remove_if_present(temporary_path)

	last_save_error = save_error
	save_completed.emit(save_error)
	return save_error


## Applies a live audio preview for one owned top-level preference bus.
func preview_audio(bus_name: StringName, linear_volume: float, muted: bool) -> bool:
	if bus_name not in AUDIO_BUSES or not is_finite(linear_volume):
		return false

	var bounded_volume: float = clampf(linear_volume, MIN_LINEAR_VOLUME, 1.0)
	match bus_name:
		BUS_MASTER:
			_master_volume = bounded_volume
			_master_muted = muted
		BUS_MUSIC:
			_music_volume = bounded_volume
			_music_muted = muted
		BUS_SFX:
			_sfx_volume = bounded_volume
			_sfx_muted = muted
	var applied: bool = _apply_audio_bus(bus_name, bounded_volume, muted)
	changed.emit(snapshot())
	return applied


## Applies display preferences while retaining a finite cap even when VSync is disabled.
func preview_display(window_mode: StringName, vsync_enabled: bool, fps_cap: int) -> bool:
	if window_mode not in [WINDOW_MODE_WINDOWED, WINDOW_MODE_FULLSCREEN]:
		return false
	if fps_cap not in FPS_CAPS:
		return false

	_window_mode = window_mode
	_vsync_enabled = vsync_enabled
	_fps_cap = fps_cap
	_apply_display()
	changed.emit(snapshot())
	return true


## Restores and applies safe presentation defaults without touching gameplay state.
func restore_defaults() -> void:
	_set_defaults()
	apply()
	changed.emit(snapshot())


## Applies a previously validated snapshot, used to cancel a live settings preview.
func apply_snapshot(values: Dictionary) -> bool:
	if not _snapshot_is_valid(values):
		return false

	_assign_values(values)
	apply()
	changed.emit(snapshot())
	return true


## Applies all current values to presentation-only engine services.
func apply() -> bool:
	var audio_applied := true
	audio_applied = (_apply_audio_bus(BUS_MASTER, _master_volume, _master_muted) and audio_applied)
	audio_applied = (_apply_audio_bus(BUS_MUSIC, _music_volume, _music_muted) and audio_applied)
	audio_applied = _apply_audio_bus(BUS_SFX, _sfx_volume, _sfx_muted) and audio_applied
	_apply_display()
	return audio_applied


## Returns a detached serializable view for UI and restart checks.
func snapshot() -> Dictionary:
	return {
		"schema_version": SCHEMA_VERSION,
		"master_volume": _master_volume,
		"music_volume": _music_volume,
		"sfx_volume": _sfx_volume,
		"master_muted": _master_muted,
		"music_muted": _music_muted,
		"sfx_muted": _sfx_muted,
		"window_mode": _window_mode,
		"vsync_enabled": _vsync_enabled,
		"fps_cap": _fps_cap,
	}


## Resolves an optional test-injected path without changing the production default.
func _resolved_path(path: String) -> String:
	return _storage_path if path.is_empty() else path


## Restores in-memory values without performing presentation side effects.
func _set_defaults() -> void:
	_master_volume = DEFAULT_MASTER_VOLUME
	_music_volume = DEFAULT_MUSIC_VOLUME
	_sfx_volume = DEFAULT_SFX_VOLUME
	_master_muted = false
	_music_muted = false
	_sfx_muted = false
	_window_mode = WINDOW_MODE_WINDOWED
	_vsync_enabled = true
	_fps_cap = FPS_CAP_60


## Extracts all known values or rejects the file as one corrupt transaction.
func _validated_values(config: ConfigFile) -> Dictionary:
	if not config.has_section_key("meta", "schema_version"):
		return {}
	var schema: Variant = config.get_value("meta", "schema_version")
	if not schema is int or schema != SCHEMA_VERSION:
		return {}

	var values: Dictionary = {
		"schema_version": SCHEMA_VERSION,
		"master_volume": config.get_value("audio", "master_volume", DEFAULT_MASTER_VOLUME),
		"music_volume": config.get_value("audio", "music_volume", DEFAULT_MUSIC_VOLUME),
		"sfx_volume": config.get_value("audio", "sfx_volume", DEFAULT_SFX_VOLUME),
		"master_muted": config.get_value("audio", "master_muted", false),
		"music_muted": config.get_value("audio", "music_muted", false),
		"sfx_muted": config.get_value("audio", "sfx_muted", false),
		"window_mode": config.get_value("display", "window_mode", WINDOW_MODE_WINDOWED),
		"vsync_enabled": config.get_value("display", "vsync_enabled", true),
		"fps_cap": config.get_value("display", "fps_cap", FPS_CAP_60),
	}
	if not _snapshot_is_valid(values, false):
		return {}

	values.master_volume = clampf(float(values.master_volume), MIN_LINEAR_VOLUME, 1.0)
	values.music_volume = clampf(float(values.music_volume), MIN_LINEAR_VOLUME, 1.0)
	values.sfx_volume = clampf(float(values.sfx_volume), MIN_LINEAR_VOLUME, 1.0)
	values.window_mode = StringName(values.window_mode)
	return values


## Checks exact persisted types and finite values before any state mutation.
func _snapshot_is_valid(values: Dictionary, require_bounded_levels: bool = true) -> bool:
	for key: String in ["master_volume", "music_volume", "sfx_volume"]:
		var level: Variant = values.get(key)
		if not (level is float or level is int) or not is_finite(float(level)):
			return false
		if require_bounded_levels and (float(level) < MIN_LINEAR_VOLUME or float(level) > 1.0):
			return false
	for key: String in ["master_muted", "music_muted", "sfx_muted", "vsync_enabled"]:
		if not values.get(key) is bool:
			return false

	var mode_value: Variant = values.get("window_mode")
	if not (mode_value is String or mode_value is StringName):
		return false
	var mode := StringName(mode_value)
	if mode not in [WINDOW_MODE_WINDOWED, WINDOW_MODE_FULLSCREEN]:
		return false
	var fps_cap: Variant = values.get("fps_cap")
	return fps_cap is int and fps_cap in FPS_CAPS


## Installs a complete validated value set into the sole local state owner.
func _assign_values(values: Dictionary) -> void:
	_master_volume = float(values.master_volume)
	_music_volume = float(values.music_volume)
	_sfx_volume = float(values.sfx_volume)
	_master_muted = bool(values.master_muted)
	_music_muted = bool(values.music_muted)
	_sfx_muted = bool(values.sfx_muted)
	_window_mode = StringName(values.window_mode)
	_vsync_enabled = bool(values.vsync_enabled)
	_fps_cap = int(values.fps_cap)


## Builds the complete schema so partial writes never become valid settings.
func _build_config() -> ConfigFile:
	var config := ConfigFile.new()
	config.set_value("meta", "schema_version", SCHEMA_VERSION)
	config.set_value("audio", "master_volume", _master_volume)
	config.set_value("audio", "music_volume", _music_volume)
	config.set_value("audio", "sfx_volume", _sfx_volume)
	config.set_value("audio", "master_muted", _master_muted)
	config.set_value("audio", "music_muted", _music_muted)
	config.set_value("audio", "sfx_muted", _sfx_muted)
	config.set_value("display", "window_mode", _window_mode)
	config.set_value("display", "vsync_enabled", _vsync_enabled)
	config.set_value("display", "fps_cap", _fps_cap)
	return config


## Applies one owned bus and leaves A3.2 category routing and duck effects untouched.
func _apply_audio_bus(bus_name: StringName, linear_volume: float, muted: bool) -> bool:
	var bus_index: int = AudioServer.get_bus_index(bus_name)
	if bus_index < 0:
		return false

	AudioServer.set_bus_volume_db(bus_index, linear_to_db(linear_volume))
	AudioServer.set_bus_mute(bus_index, muted)
	return true


## Applies only local window presentation and a mandatory safe frame cap.
func _apply_display() -> void:
	Engine.max_fps = _fps_cap
	var vsync_mode := (
		DisplayServer.VSYNC_ENABLED if _vsync_enabled else DisplayServer.VSYNC_DISABLED
	)
	DisplayServer.window_set_vsync_mode(vsync_mode)
	var mode := (
		DisplayServer.WINDOW_MODE_FULLSCREEN
		if _window_mode == WINDOW_MODE_FULLSCREEN
		else DisplayServer.WINDOW_MODE_WINDOWED
	)
	DisplayServer.window_set_mode(mode)


## Moves a corrupt file aside before applying defaults as the recovered state.
func _recover_corrupt() -> Error:
	last_load_recovered = true
	var backup_suffix := "%d-%d" % [
		int(Time.get_unix_time_from_system() * 1000.0),
		Time.get_ticks_usec(),
	]
	last_backup_path = _storage_path + ".corrupt-" + backup_suffix
	var backup_error: Error = _rename(_storage_path, last_backup_path)
	apply()
	changed.emit(snapshot())
	if backup_error != OK:
		last_backup_path = ""
		return backup_error
	return OK


## Commits the complete temporary file while retaining the prior file for rollback.
func _replace_from_temporary(temporary_path: String) -> Error:
	var previous_path: String = _storage_path + ".previous"
	_remove_if_present(previous_path)
	var had_previous: bool = FileAccess.file_exists(_storage_path)
	if had_previous:
		var preserve_error: Error = _rename(_storage_path, previous_path)
		if preserve_error != OK:
			return preserve_error

	var replace_error: Error = _rename(temporary_path, _storage_path)
	if replace_error != OK:
		if had_previous:
			_rename(previous_path, _storage_path)
		return replace_error

	_remove_if_present(previous_path)
	return OK


## Renames through absolute paths so user and injected paths share one transaction path.
func _rename(source_path: String, destination_path: String) -> Error:
	return (
		DirAccess
		. rename_absolute(
			ProjectSettings.globalize_path(source_path),
			ProjectSettings.globalize_path(destination_path),
		)
	)


## Removes stale transaction files without treating absence as an error.
func _remove_if_present(path: String) -> void:
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
