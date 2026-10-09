extends GutTest
## Verifies production audio limits, deterministic stealing, and clean teardown.

const FIXTURE_SCENE: PackedScene = preload("res://tests/unit/audio/audio_voice_test.tscn")

var _fixture: Node3D
var _service: AudioVoiceService
var _emitters: Array[StateAudioEmitter3D] = []


## Instantiates the saved voice-policy composition for each test.
func before_each() -> void:
	_fixture = FIXTURE_SCENE.instantiate() as Node3D
	add_child_autofree(_fixture)
	_service = _fixture.get_node("VoiceService") as AudioVoiceService
	_emitters.clear()
	for child: Node in _fixture.get_children():
		var emitter := child as StateAudioEmitter3D
		if emitter != null:
			_emitters.append(emitter)
	assert_eq(_emitters.size(), 10)
	assert_true(_service.set_listener_position(Vector3.ZERO))


## Keeps S14's accepted engine, weapon, and explosion categories at fixed limits.
func test_category_limits_are_explicit_and_enforced() -> void:
	assert_eq(_service.voice_limit(AudioVoiceService.CATEGORY_ENGINES), 8)
	assert_eq(_service.voice_limit(AudioVoiceService.CATEGORY_WEAPONS), 6)
	assert_eq(_service.voice_limit(AudioVoiceService.CATEGORY_EXPLOSIONS), 8)
	_activate_emitters(_emitters, AudioVoiceService.CATEGORY_ENGINES)

	assert_eq(_service.active_voice_count(AudioVoiceService.CATEGORY_ENGINES), 8)
	assert_eq(_service.waiting_voice_count(AudioVoiceService.CATEGORY_ENGINES), 2)
	assert_true(_emitters[7].is_voice_granted())
	assert_false(_emitters[8].is_voice_granted())
	assert_eq(_service.telemetry().dropped_requests, 0)


## Steals the farthest equal-priority weapon voice for a nearer presentation source.
func test_nearer_equal_priority_voice_steals_farthest() -> void:
	var initial: Array[StateAudioEmitter3D] = []
	for index in range(4, 10):
		initial.append(_emitters[index])
	_activate_emitters(initial, AudioVoiceService.CATEGORY_WEAPONS)
	assert_true(
		_activate_emitter(_emitters[0], AudioVoiceService.CATEGORY_WEAPONS, 0)
	)

	assert_true(_emitters[0].is_voice_granted())
	assert_false(_emitters[9].is_voice_granted())
	assert_eq(_service.active_voice_count(AudioVoiceService.CATEGORY_WEAPONS), 6)
	assert_eq(_service.telemetry().stolen_voices, 1)


## Lets explicit presentation importance outrank distance without increasing the cap.
func test_higher_priority_voice_steals_a_nearer_voice() -> void:
	var initial: Array[StateAudioEmitter3D] = []
	for index in 6:
		initial.append(_emitters[index])
	_activate_emitters(initial, AudioVoiceService.CATEGORY_WEAPONS)
	assert_true(
		_activate_emitter(_emitters[9], AudioVoiceService.CATEGORY_WEAPONS, 1)
	)

	assert_true(_emitters[9].is_voice_granted())
	assert_false(_emitters[5].is_voice_granted())
	assert_eq(_service.active_voice_count(AudioVoiceService.CATEGORY_WEAPONS), 6)


## Drops a lower-ranked one-shot instead of replaying it after a voice becomes free.
func test_rejected_one_shot_does_not_wait_for_late_playback() -> void:
	for index in 6:
		assert_true(
			_activate_emitter(_emitters[index], AudioVoiceService.CATEGORY_WEAPONS, 1)
		)
	assert_true(
		_activate_emitter(_emitters[9], AudioVoiceService.CATEGORY_WEAPONS, 0)
	)
	assert_false(_emitters[9].is_voice_granted())
	assert_eq(_service.waiting_voice_count(AudioVoiceService.CATEGORY_WEAPONS), 0)
	assert_eq(_service.telemetry().dropped_requests, 1)

	assert_true(_emitters[0].apply_state(false))

	assert_false(_emitters[9].is_voice_granted())
	assert_eq(_service.active_voice_count(AudioVoiceService.CATEGORY_WEAPONS), 5)


## Promotes the next preferred waiting source when an emitter despawns.
func test_emitter_teardown_releases_and_promotes_waiting_voice() -> void:
	_activate_emitters(_emitters, AudioVoiceService.CATEGORY_ENGINES)
	assert_false(_emitters[8].is_voice_granted())

	_emitters[0].queue_free()
	await get_tree().process_frame

	assert_true(_emitters[8].is_voice_granted())
	assert_eq(_service.active_voice_count(AudioVoiceService.CATEGORY_ENGINES), 8)
	assert_eq(_service.waiting_voice_count(AudioVoiceService.CATEGORY_ENGINES), 1)


## Revokes and stops every selected player before the voice owner is removed.
func test_service_teardown_stops_all_managed_emitters() -> void:
	_activate_emitters(_emitters, AudioVoiceService.CATEGORY_ENGINES)
	assert_true(_emitters[0].is_voice_granted())

	_service.queue_free()
	await get_tree().process_frame

	assert_false(is_instance_valid(_service))
	for emitter: StateAudioEmitter3D in _emitters:
		assert_false(emitter.is_voice_granted())
		assert_false(emitter.is_audio_playing())


## Confirms default production routing exists at neutral levels before settings land.
func test_default_bus_layout_has_expected_routes_and_levels() -> void:
	var expected_routes: Dictionary[StringName, StringName] = {
		&"Music": &"Master",
		&"SFX": &"Master",
		&"Engines": &"SFX",
		&"Weapons": &"SFX",
		&"Explosions": &"SFX",
		&"UI": &"SFX",
		&"Ambience": &"Music",
	}
	var master_index := AudioServer.get_bus_index(&"Master")
	assert_gte(master_index, 0)
	assert_true(is_zero_approx(AudioServer.get_bus_volume_db(master_index)))
	assert_eq(AudioServer.get_bus_effect_count(master_index), 1)
	var limiter := AudioServer.get_bus_effect(master_index, 0) as AudioEffectLimiter
	assert_not_null(limiter)
	assert_true(is_equal_approx(limiter.ceiling_db, -1.0))
	for bus_name: StringName in expected_routes:
		var bus_index := AudioServer.get_bus_index(bus_name)
		assert_gte(bus_index, 0)
		assert_true(is_zero_approx(AudioServer.get_bus_volume_db(bus_index)))
		assert_eq(AudioServer.get_bus_send(bus_index), expected_routes[bus_name])


## Activates a list through only the emitter's presentation-state API.
func _activate_emitters(
	emitters: Array[StateAudioEmitter3D],
	category: StringName,
) -> void:
	for emitter: StateAudioEmitter3D in emitters:
		_activate_emitter(emitter, category, 0)


## Configures and activates one saved emitter with its placeholder stream.
func _activate_emitter(
	emitter: StateAudioEmitter3D,
	category: StringName,
	priority: int,
) -> bool:
	if not emitter.configure_voice(_service, category, priority):
		return false
	return emitter.apply_state(true, emitter.stream, 1.0)
