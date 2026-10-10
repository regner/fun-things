class_name Hud
extends Control
## Presents injected session, controlled-player, and lifecycle state without owning gameplay.

const SESSION_STANDALONE: StringName = &"STANDALONE"
const SESSION_HOST: StringName = &"HOST"
const SESSION_JOIN: StringName = &"JOIN"

var _session_source: Node
var _authoritative_roster_source: Node
var _player_source: Node
var _lifecycle_source: Node
var _session_operation_kind: StringName = &""

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
	unbind_authoritative_roster()
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
	_session_operation_kind = &""
	if is_instance_valid(_session_card):
		_session_card.visible = false


## Binds the future A2.2/A2.4 authoritative replicated roster used by joined clients.
func bind_authoritative_roster(source: Node) -> bool:
	if not _is_view_source(source):
		return false
	if _authoritative_roster_source == source:
		_present_authoritative_roster(_source_view(source))
		return true

	unbind_authoritative_roster()
	_authoritative_roster_source = source
	_authoritative_roster_source.connect(&"changed", _on_authoritative_roster_changed)
	_authoritative_roster_source.tree_exiting.connect(
		_on_authoritative_roster_source_exiting.bind(source)
	)
	_present_authoritative_roster(_source_view(source))
	return true


## Removes the joined-client roster count instead of falling back to SessionService's local row.
func unbind_authoritative_roster() -> void:
	_disconnect_source(
		_authoritative_roster_source,
		&"changed",
		_on_authoritative_roster_changed,
	)
	_disconnect_exiting(
		_authoritative_roster_source,
		_on_authoritative_roster_source_exiting.bind(_authoritative_roster_source),
	)
	_authoritative_roster_source = null
	if is_instance_valid(_session_detail) and _session_operation_kind == SESSION_JOIN:
		_hide_session_detail()


## Binds the controlled actor only as an entity-presence source, never a life-state owner.
func bind_player(source: Node) -> bool:
	if source == null or not is_instance_valid(source) or not source.is_inside_tree():
		return false
	if _player_source == source:
		_present_lifecycle_if_ready()
		return true

	unbind_player()
	_player_source = source
	_player_source.tree_exiting.connect(_on_player_source_exiting.bind(source))
	_present_lifecycle_if_ready()
	return true


## Clears controlled-player presence and all lifecycle-owned presentation.
func unbind_player() -> void:
	_disconnect_exiting(_player_source, _on_player_source_exiting.bind(_player_source))
	_player_source = null
	_hide_lifecycle()


## Binds PlayerLifecycle as the sole alive/dead and respawn presentation source.
func bind_lifecycle(source: Node) -> bool:
	if not _is_view_source(source):
		return false
	if _lifecycle_source == source:
		_present_lifecycle_if_ready()
		return true

	unbind_lifecycle()
	_lifecycle_source = source
	_lifecycle_source.connect(&"changed", _on_lifecycle_changed)
	_lifecycle_source.tree_exiting.connect(_on_lifecycle_source_exiting.bind(source))
	_present_lifecycle_if_ready()
	return true


## Clears every lifecycle-owned value without inventing a fallback actor state.
func unbind_lifecycle() -> void:
	_disconnect_source(_lifecycle_source, &"changed", _on_lifecycle_changed)
	_disconnect_exiting(
		_lifecycle_source,
		_on_lifecycle_source_exiting.bind(_lifecycle_source),
	)
	_lifecycle_source = null
	_hide_lifecycle()


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


## Applies an immutable authoritative roster snapshot from the currently bound source only.
func _on_authoritative_roster_changed(view: Dictionary) -> void:
	if not is_instance_valid(_authoritative_roster_source):
		return

	_present_authoritative_roster(view.duplicate(true))


## Removes joined-client roster presentation when its authoritative owner leaves.
func _on_authoritative_roster_source_exiting(source: Node) -> void:
	if source == _authoritative_roster_source:
		unbind_authoritative_roster()


## Removes player presence when its actor begins leaving the tree.
func _on_player_source_exiting(source: Node) -> void:
	if source == _player_source:
		unbind_player()


## Applies an immutable lifecycle snapshot from the currently bound source only.
func _on_lifecycle_changed(view: Dictionary) -> void:
	if not is_instance_valid(_lifecycle_source):
		return
	if not is_instance_valid(_player_source):
		_hide_lifecycle()
		return

	_present_lifecycle(view.duplicate(true))


## Removes lifecycle data when its owner begins leaving the tree.
func _on_lifecycle_source_exiting(source: Node) -> void:
	if source == _lifecycle_source:
		unbind_lifecycle()


## Renders mode, an authoritative admitted count when available, and optional quality.
func _present_session(view: Dictionary) -> void:
	_session_operation_kind = view.get("operation_kind", &"")
	_session_mode.text = _session_mode_text(_session_operation_kind)
	_present_session_detail(view)
	var quality: String = String(view.get("connection_quality", "")).strip_edges()
	_connection_quality.visible = not quality.is_empty()
	_connection_quality.text = quality.to_upper()
	_session_card.visible = not _session_mode.text.is_empty()


## Selects the authoritative peer-count owner for the current operation kind.
func _present_session_detail(session_view: Dictionary) -> void:
	if _session_operation_kind == SESSION_JOIN:
		if is_instance_valid(_authoritative_roster_source):
			_present_authoritative_roster(_source_view(_authoritative_roster_source))
		else:
			_hide_session_detail()
		return

	_present_peer_count(session_view)


## Accepts joined-client counts only from the separately injected replicated roster owner.
func _present_authoritative_roster(view: Dictionary) -> void:
	if _session_operation_kind != SESSION_JOIN:
		return

	_present_peer_count(view)


## Renders an owner-supplied admitted roster without deriving or padding membership.
func _present_peer_count(view: Dictionary) -> void:
	var roster_value: Variant = view.get("roster")
	if not roster_value is Array:
		_hide_session_detail()
		return

	var peer_count: int = (roster_value as Array).size()
	_session_detail.text = "%d %s" % [peer_count, "PLAYER" if peer_count == 1 else "PLAYERS"]
	_session_detail.visible = true


## Hides absent or non-authoritative peer-count data and clears its stale copy.
func _hide_session_detail() -> void:
	_session_detail.text = ""
	_session_detail.visible = false


## Renders the lifecycle snapshot only when both required owners are present.
func _present_lifecycle_if_ready() -> void:
	if not is_instance_valid(_player_source) or not is_instance_valid(_lifecycle_source):
		_hide_lifecycle()
		return

	_present_lifecycle(_source_view(_lifecycle_source))


## Renders PlayerLifecycle-owned death state and an optional dead-state countdown.
func _present_lifecycle(view: Dictionary) -> void:
	var alive_value: Variant = view.get("alive")
	if not alive_value is bool:
		_hide_lifecycle()
		return

	var alive: bool = alive_value
	_player_state.text = "ACTIVE" if alive else "DOWN"
	_player_state.modulate = Color("f6f1dc") if alive else Color("ff7262")
	_player_card.visible = true
	if alive or not view.has("respawn_seconds"):
		_respawn_slot.visible = false
		return

	var seconds_value: Variant = view.respawn_seconds
	if not (seconds_value is int or seconds_value is float) or float(seconds_value) < 0.0:
		_respawn_slot.visible = false
		return

	_respawn_value.text = "%.1f" % float(seconds_value)
	_respawn_slot.visible = true


## Hides and clears lifecycle-owned rows whenever their full source chain is absent.
func _hide_lifecycle() -> void:
	if is_instance_valid(_player_card):
		_player_card.visible = false
	if is_instance_valid(_player_state):
		_player_state.text = ""
	if is_instance_valid(_respawn_slot):
		_respawn_slot.visible = false
	if is_instance_valid(_respawn_value):
		_respawn_value.text = ""


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


## Validates the small read-only source protocol used by presentation owners.
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
