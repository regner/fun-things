class_name StateAudioEmitter3D
extends Node3D
## Presents externally owned state through one bounded spatial audio voice.

@export var category: StringName = AudioVoiceService.CATEGORY_ENGINES
@export_range(-100, 100, 1) var priority := 0
@export var stream: AudioStream

var _voice_service: AudioVoiceService
var _desired_active := false
var _voice_granted := false
var _request_submitted := false
var _pitch_scale := 1.0

@onready var _player: AudioStreamPlayer3D = %Player


## Applies the saved stream and any state received before tree entry.
func _ready() -> void:
	_player.stream = stream
	_player.pitch_scale = _pitch_scale
	_player.bus = category
	_sync_voice_request()


## Releases the owned voice before despawn, reset, or scene teardown completes.
func _exit_tree() -> void:
	_desired_active = false
	_request_submitted = false
	if _voice_service != null and is_instance_valid(_voice_service):
		_voice_service.release_voice(self)
	set_voice_granted(false)
	_voice_service = null


## Injects the presentation voice owner and this emitter's fixed category policy.
func configure_voice(
	voice_service: AudioVoiceService,
	voice_category: StringName,
	voice_priority: int = 0,
) -> bool:
	if voice_service == null or voice_service.voice_limit(voice_category) == 0:
		return false

	if _voice_service != null and _desired_active:
		_voice_service.release_voice(self)
	_request_submitted = false
	_voice_service = voice_service
	category = voice_category
	priority = voice_priority
	if is_node_ready():
		_player.bus = category
	_sync_voice_request()
	return true


## Consumes presentation state without deciding the gameplay event or outcome.
func apply_state(
	active: bool,
	state_stream: AudioStream = null,
	state_pitch_scale: float = 1.0,
) -> bool:
	if not is_finite(state_pitch_scale) or state_pitch_scale <= 0.0:
		return false
	if state_stream != null:
		stream = state_stream
	if active and stream == null:
		return false

	if active != _desired_active:
		_request_submitted = false
	_desired_active = active
	_pitch_scale = state_pitch_scale
	if is_node_ready():
		_player.stream = stream
		_player.pitch_scale = _pitch_scale
	_sync_voice_request()
	return true


## Exposes whether the voice policy currently selected this emitter.
func is_voice_granted() -> bool:
	return _voice_granted


## Exposes actual player state for lifecycle checks and presentation diagnostics.
func is_audio_playing() -> bool:
	return is_node_ready() and _player.playing


## Applies the voice owner's grant without changing desired presentation state.
func set_voice_granted(granted: bool) -> void:
	_voice_granted = granted and _desired_active
	if not is_node_ready():
		return

	if _voice_granted:
		if not _player.playing:
			_player.play()
	else:
		_player.stop()


## Mirrors desired state into the injected voice policy when ready.
func _sync_voice_request() -> void:
	if not is_node_ready() or _voice_service == null or not is_instance_valid(_voice_service):
		return
	if _desired_active:
		if _request_submitted:
			set_voice_granted(_voice_granted)
			return
		_request_submitted = true
		var granted := _voice_service.request_voice(self, category, priority)
		set_voice_granted(granted)
	else:
		_request_submitted = false
		_voice_service.release_voice(self)
