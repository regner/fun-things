class_name S14VoiceManager
extends Node3D
## Bounds fixture audio voices while keeping authoritative presentation requests separate.

const ENGINE_CAP := 8
const EXPLOSION_CAP := 8
const WEAPON_CAP := 6
const ENGINE_MAX_SPEED_MPS := 30.0
const ENGINE_IDLE_PITCH := 0.75
const ENGINE_MAX_PITCH := 1.55
const EXPLOSION_DUCK_DB := -8.0
const WEAPON_DUCK_DB := -4.0
const DUCK_DURATION_MSEC := 280

var _listener: AudioListener3D
var _duck_deadline_msec := 0
var _engine_base_db := 0.0
var _weapon_base_db := 0.0
var _accepted_explosions := 0
var _dropped_explosions := 0
var _accepted_weapon_shots := 0
var _dropped_weapon_shots := 0

@onready var _engine_voices: Node3D = %EngineVoices
@onready var _explosion_voices: Node3D = %ExplosionVoices
@onready var _weapon_voices: Node3D = %WeaponVoices


## Injects the listener used for nearest-engine priority and validates saved pools.
func configure(listener: AudioListener3D) -> bool:
	_listener = listener
	_engine_base_db = _bus_volume(&"Engines")
	_weapon_base_db = _bus_volume(&"Weapons")
	return (
		_engine_voices.get_child_count() == 32
		and _explosion_voices.get_child_count() == EXPLOSION_CAP
		and _weapon_voices.get_child_count() == WEAPON_CAP
	)


## Activates only the nearest engine voices and maps speed to a bounded pitch range.
func set_engine_speeds(speeds_mps: PackedFloat32Array) -> void:
	var ranked: Array[AudioStreamPlayer3D] = []
	for child: Node in _engine_voices.get_children():
		var voice := child as AudioStreamPlayer3D
		if voice != null:
			ranked.append(voice)
	ranked.sort_custom(_is_voice_nearer)

	for index in ranked.size():
		var voice := ranked[index]
		if index < ENGINE_CAP:
			var speed := speeds_mps[index % speeds_mps.size()]
			voice.pitch_scale = lerpf(
				ENGINE_IDLE_PITCH,
				ENGINE_MAX_PITCH,
				clampf(speed / ENGINE_MAX_SPEED_MPS, 0.0, 1.0),
			)
			if not voice.playing:
				voice.play()
		else:
			voice.stop()


## Requests one explosion sound, dropping audio only when its category pool is full.
func request_explosion(position: Vector3) -> bool:
	var voice := _first_available_voice(_explosion_voices)
	if voice == null:
		_dropped_explosions += 1
		return false

	voice.global_position = position
	voice.play()
	_accepted_explosions += 1
	_begin_explosion_duck()
	return true


## Requests one SMG sound, dropping audio only when its category pool is full.
func request_weapon_shot(position: Vector3) -> bool:
	var voice := _first_available_voice(_weapon_voices)
	if voice == null:
		_dropped_weapon_shots += 1
		return false

	voice.global_position = position
	voice.play()
	_accepted_weapon_shots += 1
	return true


## Restores ducked categories after the latest explosion's bounded readability window.
func update_duck(now_msec: int) -> void:
	if _duck_deadline_msec == 0 or now_msec < _duck_deadline_msec:
		return

	_set_bus_volume(&"Engines", _engine_base_db)
	_set_bus_volume(&"Weapons", _weapon_base_db)
	_duck_deadline_msec = 0


## Reports logical and currently playing voice counts through the public fixture API.
func report() -> Dictionary:
	return {
		"caps":
		{
			"engines": ENGINE_CAP,
			"explosions": EXPLOSION_CAP,
			"weapons": WEAPON_CAP,
		},
		"active":
		{
			"engines": _active_count(_engine_voices),
			"explosions": _active_count(_explosion_voices),
			"weapons": _active_count(_weapon_voices),
		},
		"requests":
		{
			"explosions_accepted": _accepted_explosions,
			"explosions_dropped": _dropped_explosions,
			"weapon_accepted": _accepted_weapon_shots,
			"weapon_dropped": _dropped_weapon_shots,
		},
		"ducking_active": _duck_deadline_msec > 0,
	}


## Stops every managed voice and restores altered bus levels during teardown.
func stop_all() -> void:
	for pool: Node3D in [_engine_voices, _explosion_voices, _weapon_voices]:
		for child: Node in pool.get_children():
			var voice := child as AudioStreamPlayer3D
			if voice != null:
				voice.stop()
	_set_bus_volume(&"Engines", _engine_base_db)
	_set_bus_volume(&"Weapons", _weapon_base_db)
	_duck_deadline_msec = 0


## Orders engine sources by ground-relative listener distance.
func _is_voice_nearer(left: AudioStreamPlayer3D, right: AudioStreamPlayer3D) -> bool:
	return (
		left.global_position.distance_squared_to(_listener.global_position)
		< right.global_position.distance_squared_to(_listener.global_position)
	)


## Finds a free saved player without creating runtime nodes.
func _first_available_voice(pool: Node3D) -> AudioStreamPlayer3D:
	for child: Node in pool.get_children():
		var voice := child as AudioStreamPlayer3D
		if voice != null and not voice.playing:
			return voice
	return null


## Counts currently playing saved players in one category.
func _active_count(pool: Node3D) -> int:
	var count := 0
	for child: Node in pool.get_children():
		var voice := child as AudioStreamPlayer3D
		if voice != null and voice.playing:
			count += 1
	return count


## Starts or extends category ducking for explosion readability.
func _begin_explosion_duck() -> void:
	_set_bus_volume(&"Engines", _engine_base_db + EXPLOSION_DUCK_DB)
	_set_bus_volume(&"Weapons", _weapon_base_db + WEAPON_DUCK_DB)
	_duck_deadline_msec = Time.get_ticks_msec() + DUCK_DURATION_MSEC


## Returns the current bus volume, falling back safely when a bus is absent.
func _bus_volume(bus_name: StringName) -> float:
	var index := AudioServer.get_bus_index(bus_name)
	if index < 0:
		return 0.0
	return AudioServer.get_bus_volume_db(index)


## Sets a bus volume when the fixture layout contains the named bus.
func _set_bus_volume(bus_name: StringName, volume_db: float) -> void:
	var index := AudioServer.get_bus_index(bus_name)
	if index >= 0:
		AudioServer.set_bus_volume_db(index, volume_db)
