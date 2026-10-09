class_name S14Settings
extends RefCounted
## Stores and applies the fixture's process-local audio preferences.

const SCHEMA_VERSION := 1
const BUS_MASTER := &"Master"
const BUS_MUSIC := &"Music"
const BUS_SFX := &"SFX"

var master_level := 1.0
var music_level := 0.8
var sfx_level := 0.8
var master_muted := false
var music_muted := false
var sfx_muted := false


## Saves the current settings to an injected local ConfigFile path.
func save(path: String) -> Error:
	var config := ConfigFile.new()
	config.set_value("meta", "schema_version", SCHEMA_VERSION)
	config.set_value("audio", "master_level", master_level)
	config.set_value("audio", "music_level", music_level)
	config.set_value("audio", "sfx_level", sfx_level)
	config.set_value("audio", "master_muted", master_muted)
	config.set_value("audio", "music_muted", music_muted)
	config.set_value("audio", "sfx_muted", sfx_muted)
	return config.save(path)


## Loads known values, retaining safe defaults for absent or malformed settings.
func load_settings(path: String) -> Error:
	var config := ConfigFile.new()
	var error := config.load(path)
	if error != OK:
		return error

	master_level = _read_level(config, "master_level", master_level)
	music_level = _read_level(config, "music_level", music_level)
	sfx_level = _read_level(config, "sfx_level", sfx_level)
	master_muted = _read_bool(config, "master_muted", master_muted)
	music_muted = _read_bool(config, "music_muted", music_muted)
	sfx_muted = _read_bool(config, "sfx_muted", sfx_muted)
	return OK


## Applies levels and mute state to the fixture-local bus layout.
func apply() -> bool:
	var mappings := [
		[BUS_MASTER, master_level, master_muted],
		[BUS_MUSIC, music_level, music_muted],
		[BUS_SFX, sfx_level, sfx_muted],
	]
	for mapping: Array in mappings:
		var bus_index := AudioServer.get_bus_index(mapping[0])
		if bus_index < 0:
			return false

		AudioServer.set_bus_volume_db(bus_index, linear_to_db(float(mapping[1])))
		AudioServer.set_bus_mute(bus_index, bool(mapping[2]))
	return true


## Returns serializable values for independent roundtrip assertions.
func snapshot() -> Dictionary:
	return {
		"schema_version": SCHEMA_VERSION,
		"master_level": master_level,
		"music_level": music_level,
		"sfx_level": sfx_level,
		"master_muted": master_muted,
		"music_muted": music_muted,
		"sfx_muted": sfx_muted,
	}


## Reads and bounds one linear gain from the audio section.
func _read_level(config: ConfigFile, key: String, fallback: float) -> float:
	var value: Variant = config.get_value("audio", key, fallback)
	if not (value is float or value is int):
		return fallback
	return clampf(float(value), 0.001, 1.0)


## Reads one mute only when its persisted value is actually boolean.
func _read_bool(config: ConfigFile, key: String, fallback: bool) -> bool:
	var value: Variant = config.get_value("audio", key, fallback)
	if not value is bool:
		return fallback
	return value
