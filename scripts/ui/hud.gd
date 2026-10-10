class_name Hud
extends Control
## Presents injected session, controlled-player, and lifecycle state without owning gameplay.

const SESSION_STANDALONE: StringName = &"STANDALONE"
const SESSION_HOST: StringName = &"HOST"
const SESSION_JOIN: StringName = &"JOIN"

var _session_source: Node
var _player_source: Node
var _lifecycle_source: Node

@onready var _session_card: PanelContainer = %SessionCard
@onready var _session_mode: Label = %SessionMode
@onready var _session_detail: Label = %SessionDetail
@onready var _connection_quality: Label = %ConnectionQuality
@onready var _player_card: PanelContainer = %PlayerCard
@onready var _player_state: Label = %PlayerState
@onready var _respawn_slot: PanelContainer = %RespawnSlot
@onready var _respawn_value: Label = %RespawnValue


## Disconnects injected owners while they are still valid during HUD teardown.
func _exit_tree() -> void:
	unbind_session()
	unbind_player()
	unbind_lifecycle()


## Binds a read-only source exposing changed(Dictionary) and view() session contracts.
func bind_session(source: Node) -> bool:
	if not _is_view_source(source):
		return false
	if _session_source == source:
		_present_session(_source_view(source))
		return true

	unbind_session()
	_session_source = source
	_session_source.connect(&"changed", _on_session_changed)
	_session_source.tree_exiting.connect(_on_session_source_exiting.bind(source))
	_present_session(_source_view(source))
	return true


## Clears session presentation without changing the session owner.
func unbind_session() -> void:
	_disconnect_source(_session_source, &"changed", _on_session_changed)
	_disconnect_exiting(_session_source, _on_session_source_exiting.bind(_session_source))
	_session_source = null
	if is_instance_valid(_session_card):
		_session_card.visible = false


## Binds the controlled player and observes alive_changed(bool) when the owner provides it.
func bind_player(source: Node) -> bool:
	if source == null or not is_instance_valid(source) or not source.is_inside_tree():
		return false
	if _player_source == source:
		_present_player(_read_player_alive(source))
		return true

	unbind_player()
	_player_source = source
	if source.has_signal(&"alive_changed"):
		source.connect(&"alive_changed", _on_player_alive_changed)
	source.tree_exiting.connect(_on_player_source_exiting.bind(source))
	_present_player(_read_player_alive(source))
	return true


## Clears controlled-player presentation without changing or retaining that player.
func unbind_player() -> void:
	_disconnect_source(_player_source, &"alive_changed", _on_player_alive_changed)
	_disconnect_exiting(_player_source, _on_player_source_exiting.bind(_player_source))
	_player_source = null
	if is_instance_valid(_player_card):
		_player_card.visible = false


## Binds a lifecycle source exposing changed(Dictionary) and view() presentation contracts.
func bind_lifecycle(source: Node) -> bool:
	if not _is_view_source(source):
		return false
	if _lifecycle_source == source:
		_present_lifecycle(_source_view(source))
		return true

	unbind_lifecycle()
	_lifecycle_source = source
	_lifecycle_source.connect(&"changed", _on_lifecycle_changed)
	_lifecycle_source.tree_exiting.connect(_on_lifecycle_source_exiting.bind(source))
	_present_lifecycle(_source_view(source))
	return true


## Clears lifecycle presentation and hides its future respawn-countdown slot.
func unbind_lifecycle() -> void:
	_disconnect_source(_lifecycle_source, &"changed", _on_lifecycle_changed)
	_disconnect_exiting(
		_lifecycle_source,
		_on_lifecycle_source_exiting.bind(_lifecycle_source),
	)
	_lifecycle_source = null
	if is_instance_valid(_respawn_slot):
		_respawn_slot.visible = false
	if is_instance_valid(_player_source) and is_instance_valid(_player_card):
		_present_player(_read_player_alive(_player_source))


## Returns whether the four future B-row and C4.2 authored slots remain unpopulated.
func future_slots_are_empty() -> bool:
	return (
		not %HealthSlot.visible
		and not %AmmoSlot.visible
		and not %VehicleSlot.visible
		and not %MinimapSlot.visible
	)


## Applies an immutable session snapshot from the currently bound source only.
func _on_session_changed(view: Dictionary) -> void:
	if not is_instance_valid(_session_source):
		return

	_present_session(view.duplicate(true))


## Removes session data when its owner begins leaving the tree.
func _on_session_source_exiting(source: Node) -> void:
	if source == _session_source:
		unbind_session()


## Applies controlled-player life state emitted by its owner.
func _on_player_alive_changed(alive: bool) -> void:
	if is_instance_valid(_player_source):
		_present_player(alive)


## Removes player data when its owner begins leaving the tree.
func _on_player_source_exiting(source: Node) -> void:
	if source == _player_source:
		unbind_player()


## Applies an immutable lifecycle snapshot from the currently bound source only.
func _on_lifecycle_changed(view: Dictionary) -> void:
	if not is_instance_valid(_lifecycle_source):
		return

	_present_lifecycle(view.duplicate(true))


## Removes lifecycle data when its owner begins leaving the tree.
func _on_lifecycle_source_exiting(source: Node) -> void:
	if source == _lifecycle_source:
		unbind_lifecycle()


## Renders mode, admitted peer count, and optional owner-supplied connection quality.
func _present_session(view: Dictionary) -> void:
	var operation_kind: StringName = view.get("operation_kind", &"")
	var roster: Array = view.get("roster", [])
	var peer_count: int = roster.size()
	_session_mode.text = _session_mode_text(operation_kind)
	_session_detail.text = "%d %s" % [peer_count, "PLAYER" if peer_count == 1 else "PLAYERS"]
	var quality: String = String(view.get("connection_quality", "")).strip_edges()
	_connection_quality.visible = not quality.is_empty()
	_connection_quality.text = quality.to_upper()
	_session_card.visible = not _session_mode.text.is_empty()


## Renders only the controlled player's owner-reported life state.
func _present_player(alive: bool) -> void:
	_player_state.text = "ACTIVE" if alive else "DOWN"
	_player_state.modulate = Color("f6f1dc") if alive else Color("ff7262")
	_player_card.visible = true


## Renders owner-supplied death state and countdown, hiding absent countdown data.
func _present_lifecycle(view: Dictionary) -> void:
	if view.has("alive") and view.alive is bool:
		_present_player(view.alive)
	if not view.has("respawn_seconds"):
		_respawn_slot.visible = false
		return

	var seconds_value: Variant = view.respawn_seconds
	if not (seconds_value is int or seconds_value is float) or float(seconds_value) < 0.0:
		_respawn_slot.visible = false
		return

	_respawn_value.text = "%.1f" % float(seconds_value)
	_respawn_slot.visible = true


## Maps the session owner's operation kind to concise HUD copy without deriving state.
func _session_mode_text(operation_kind: StringName) -> String:
	match operation_kind:
		SESSION_STANDALONE:
			return "SOLO"
		SESSION_HOST:
			return "HOST"
		SESSION_JOIN:
			return "CLIENT"
		_:
			return ""


## Reads optional player life state without requiring ActorMotion to own lifecycle rules.
func _read_player_alive(source: Node) -> bool:
	if source.has_method(&"is_alive"):
		var result: Variant = source.call(&"is_alive")
		if result is bool:
			return result
	return true


## Validates the small read-only source protocol used by session and lifecycle owners.
func _is_view_source(source: Node) -> bool:
	return (
		source != null
		and is_instance_valid(source)
		and source.is_inside_tree()
		and source.has_signal(&"changed")
		and source.has_method(&"view")
	)


## Copies an owner snapshot before presentation so the HUD cannot mutate owner storage.
func _source_view(source: Node) -> Dictionary:
	var value: Variant = source.call(&"view")
	return (value as Dictionary).duplicate(true) if value is Dictionary else {}


## Disconnects an optional owner signal without assuming that owner still exists.
func _disconnect_source(source: Node, signal_name: StringName, callback: Callable) -> void:
	if (
		is_instance_valid(source)
		and source.has_signal(signal_name)
		and source.is_connected(signal_name, callback)
	):
		source.disconnect(signal_name, callback)


## Disconnects a bound tree-exit callback while its owner remains valid.
func _disconnect_exiting(source: Node, callback: Callable) -> void:
	if is_instance_valid(source) and source.tree_exiting.is_connected(callback):
		source.tree_exiting.disconnect(callback)
