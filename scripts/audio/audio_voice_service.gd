class_name AudioVoiceService
extends Node
## Owns bounded presentation-audio voice selection and deterministic stealing.

const CATEGORY_ENGINES: StringName = &"Engines"
const CATEGORY_WEAPONS: StringName = &"Weapons"
const CATEGORY_EXPLOSIONS: StringName = &"Explosions"
const ENGINE_VOICE_LIMIT := 8
const WEAPON_VOICE_LIMIT := 6
const EXPLOSION_VOICE_LIMIT := 8
const EXPLOSION_DUCK_DURATION_SECONDS := 0.28
const ENGINE_DUCK_DB := -8.0
const WEAPON_DUCK_DB := -4.0
const DUCK_EFFECT_NAME := &"Explosion Duck Gain"

var _listener_position := Vector3.ZERO
var _requests: Dictionary = {}
var _next_sequence := 1
var _dropped_requests := 0
var _stolen_voices := 0
var _duck_remaining_seconds := 0.0
var _shutting_down := false


## Keeps duck recovery dormant until a granted explosion starts it.
func _ready() -> void:
	set_process(false)


## Restores category gain after the bounded explosion readability window.
func _process(delta: float) -> void:
	_duck_remaining_seconds = maxf(_duck_remaining_seconds - delta, 0.0)
	if is_zero_approx(_duck_remaining_seconds):
		_restore_explosion_duck()


## Stops managed audio before this presentation owner leaves the tree.
func _exit_tree() -> void:
	stop_all()


## Updates the presentation listener position used by distance priority.
func set_listener_position(listener_position: Vector3) -> bool:
	if not listener_position.is_finite():
		return false

	_listener_position = listener_position
	_reconcile_all_categories()
	return true


## Requests or updates one desired presentation voice.
func request_voice(
	emitter: StateAudioEmitter3D,
	category: StringName,
	priority: int,
) -> bool:
	if _shutting_down or not is_instance_valid(emitter) or voice_limit(category) == 0:
		return false

	var emitter_id := emitter.get_instance_id()
	var is_new := not _requests.has(emitter_id)
	if is_new:
		_requests[emitter_id] = {
			"emitter": weakref(emitter),
			"category": category,
			"priority": priority,
			"sequence": _next_sequence,
			"granted": false,
		}
		_next_sequence += 1
	else:
		var existing: Dictionary = _requests[emitter_id]
		var previous_category: StringName = existing["category"]
		if previous_category != category and bool(existing["granted"]):
			emitter.set_voice_granted(false)
			existing["granted"] = false
		existing["category"] = category
		existing["priority"] = priority
		_requests[emitter_id] = existing
		if previous_category != category:
			_reconcile_category(previous_category)

	_reconcile_category(category)
	var request: Dictionary = _requests.get(emitter_id, {})
	var granted := not request.is_empty() and bool(request["granted"])
	if is_new and not granted and not _category_retains_waiting(category):
		_dropped_requests += 1
		_requests.erase(emitter_id)
	return granted


## Releases one emitter and promotes the next preferred waiting voice.
func release_voice(emitter: StateAudioEmitter3D) -> void:
	if not is_instance_valid(emitter):
		return

	var emitter_id := emitter.get_instance_id()
	if not _requests.has(emitter_id):
		emitter.set_voice_granted(false)
		return

	var request: Dictionary = _requests[emitter_id]
	var category: StringName = request["category"]
	_requests.erase(emitter_id)
	emitter.set_voice_granted(false)
	if not _shutting_down:
		_reconcile_category(category)


## Returns the fixed production limit for a managed category.
func voice_limit(category: StringName) -> int:
	match category:
		CATEGORY_ENGINES:
			return ENGINE_VOICE_LIMIT
		CATEGORY_WEAPONS:
			return WEAPON_VOICE_LIMIT
		CATEGORY_EXPLOSIONS:
			return EXPLOSION_VOICE_LIMIT
		_:
			return 0


## Reports currently granted voices for one managed category.
func active_voice_count(category: StringName) -> int:
	var count := 0
	for request: Dictionary in _requests.values():
		if request["category"] == category and bool(request["granted"]):
			count += 1
	return count


## Reports desired voices waiting behind a category limit.
func waiting_voice_count(category: StringName) -> int:
	var count := 0
	for request: Dictionary in _requests.values():
		if request["category"] == category and not bool(request["granted"]):
			count += 1
	return count


## Reports whether the bounded explosion readability duck is active.
func is_ducking_active() -> bool:
	return _duck_remaining_seconds > 0.0


## Returns bounded-policy telemetry without affecting gameplay or visual events.
func telemetry() -> Dictionary:
	return {
		"dropped_requests": _dropped_requests,
		"stolen_voices": _stolen_voices,
		"active_requests": _requests.size(),
	}


## Revokes every voice and prevents new requests during service teardown.
func stop_all() -> void:
	if _shutting_down:
		return

	_shutting_down = true
	for request: Dictionary in _requests.values():
		var emitter := _request_emitter(request)
		if emitter != null:
			emitter.set_voice_granted(false)
	_requests.clear()
	_restore_explosion_duck()


## Reconciles every managed category after listener movement.
func _reconcile_all_categories() -> void:
	_reconcile_category(CATEGORY_ENGINES)
	_reconcile_category(CATEGORY_WEAPONS)
	_reconcile_category(CATEGORY_EXPLOSIONS)


## Grants the preferred bounded set and revokes voices displaced by it.
func _reconcile_category(category: StringName) -> void:
	_remove_invalid_requests()
	var ranked: Array[Dictionary] = []
	for request: Dictionary in _requests.values():
		if request["category"] == category:
			ranked.append(request)
	ranked.sort_custom(_request_precedes)

	var limit := voice_limit(category)
	for index in ranked.size():
		var request := ranked[index]
		var should_grant := index < limit
		if bool(request["granted"]) == should_grant:
			continue

		var emitter := _request_emitter(request)
		if emitter == null:
			continue
		if not should_grant:
			_stolen_voices += 1
		request["granted"] = should_grant
		_requests[emitter.get_instance_id()] = request
		emitter.set_voice_granted(should_grant)
		if should_grant and category == CATEGORY_EXPLOSIONS:
			_begin_explosion_duck()
		if not should_grant and not _category_retains_waiting(category):
			_requests.erase(emitter.get_instance_id())


## Starts or extends category gain ducking without changing D5-owned bus levels.
func _begin_explosion_duck() -> void:
	_set_duck_effect(CATEGORY_ENGINES, ENGINE_DUCK_DB)
	_set_duck_effect(CATEGORY_WEAPONS, WEAPON_DUCK_DB)
	_duck_remaining_seconds = EXPLOSION_DUCK_DURATION_SECONDS
	set_process(true)


## Restores only service-owned gain effects on expiry or teardown.
func _restore_explosion_duck() -> void:
	_set_duck_effect(CATEGORY_ENGINES, 0.0)
	_set_duck_effect(CATEGORY_WEAPONS, 0.0)
	_duck_remaining_seconds = 0.0
	set_process(false)


## Changes the authored duck effect while leaving the bus's persisted base level intact.
func _set_duck_effect(bus_name: StringName, duck_db: float) -> void:
	var bus_index := AudioServer.get_bus_index(bus_name)
	if bus_index < 0:
		return
	for effect_index in AudioServer.get_bus_effect_count(bus_index):
		var effect := AudioServer.get_bus_effect(bus_index, effect_index)
		if effect is AudioEffectAmplify and effect.resource_name == DUCK_EFFECT_NAME:
			(effect as AudioEffectAmplify).volume_db = duck_db
			return


## Returns whether displaced continuous voices may wait for later promotion.
func _category_retains_waiting(category: StringName) -> bool:
	return category == CATEGORY_ENGINES


## Removes dead weak references without retaining despawned presentation emitters.
func _remove_invalid_requests() -> void:
	var invalid_ids: Array[int] = []
	for emitter_id: int in _requests:
		var request: Dictionary = _requests[emitter_id]
		if _request_emitter(request) == null:
			invalid_ids.append(emitter_id)
	for emitter_id: int in invalid_ids:
		_requests.erase(emitter_id)


## Orders by importance, then proximity, then newer request significance.
func _request_precedes(left: Dictionary, right: Dictionary) -> bool:
	var left_priority: int = left["priority"]
	var right_priority: int = right["priority"]
	if left_priority != right_priority:
		return left_priority > right_priority

	var left_distance := _request_distance_squared(left)
	var right_distance := _request_distance_squared(right)
	if not is_equal_approx(left_distance, right_distance):
		return left_distance < right_distance
	return int(left["sequence"]) > int(right["sequence"])


## Measures one valid emitter against the current presentation listener.
func _request_distance_squared(request: Dictionary) -> float:
	var emitter := _request_emitter(request)
	if emitter == null or not emitter.is_inside_tree():
		return INF
	return emitter.global_position.distance_squared_to(_listener_position)


## Resolves one weak emitter reference without extending its lifetime.
func _request_emitter(request: Dictionary) -> StateAudioEmitter3D:
	var emitter_reference: WeakRef = request["emitter"]
	var emitter := emitter_reference.get_ref() as StateAudioEmitter3D
	if not is_instance_valid(emitter):
		return null
	return emitter
