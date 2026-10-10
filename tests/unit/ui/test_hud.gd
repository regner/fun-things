extends GutTest
## Verifies HUD owner bindings, read-only presentation, and supported-resolution layout.

const HUD_SCENE: PackedScene = preload("res://scenes/ui/hud.tscn")
const SUPPORTED_SIZES: Array[Vector2i] = [
	Vector2i(1280, 720),
	Vector2i(1920, 1080),
	Vector2i(2560, 1440),
	Vector2i(1280, 800),
]


## Rebinding disconnects prior owners and JOIN waits for an authoritative roster source.
func test_session_and_authoritative_roster_binding_lifecycle() -> void:
	var hud: Hud = await _add_hud()
	var host := FakeHudSource.new()
	var client := FakeHudSource.new()
	var authoritative_roster := FakeHudSource.new()
	add_child_autofree(host)
	add_child_autofree(client)
	add_child_autofree(authoritative_roster)
	host.snapshot = _session_view(&"HOST", 2)
	client.snapshot = _session_view(&"JOIN", 3, "Good 42 ms")
	authoritative_roster.snapshot = _roster_view(3)

	assert_true(hud.bind_session(host))
	assert_eq(_label(hud, "SessionCard/Content/SessionMode").text, "HOST")
	assert_eq(_label(hud, "SessionCard/Content/SessionDetail").text, "2 PLAYERS")
	assert_true(hud.bind_session(client))
	assert_eq(_label(hud, "SessionCard/Content/SessionMode").text, "CLIENT")
	assert_false(hud.get_node("SessionCard/Content/SessionDetail").visible)
	assert_eq(_label(hud, "SessionCard/Content/ConnectionQuality").text, "GOOD 42 MS")
	assert_true(hud.bind_authoritative_roster(authoritative_roster))
	assert_eq(_label(hud, "SessionCard/Content/SessionDetail").text, "3 PLAYERS")

	host.publish(_session_view(&"STANDALONE", 1))
	authoritative_roster.publish(_roster_view(4))
	assert_eq(_label(hud, "SessionCard/Content/SessionMode").text, "CLIENT")
	assert_eq(_label(hud, "SessionCard/Content/SessionDetail").text, "4 PLAYERS")
	authoritative_roster.queue_free()
	await get_tree().process_frame
	assert_false(hud.get_node("SessionCard/Content/SessionDetail").visible)
	client.queue_free()
	await get_tree().process_frame
	assert_false(hud.get_node("SessionCard").visible)


## An actual joining SessionService cannot expose its local-only roster as a peer count.
func test_joined_session_service_suppresses_non_authoritative_peer_count() -> void:
	var hud: Hud = await _add_hud()
	var service := SessionService.new()
	var transport := FakeSessionTransport.new()
	transport.auto_ready = false
	add_child_autofree(service)
	add_child_autofree(transport)
	assert_true(service.register_transport(transport).ok)
	var target: Dictionary = {
		"provider_id": &"fake",
		"adapter_generation": 1,
		"kind": &"TRANSPORT_READY",
		"local_handle": 44,
	}
	var join_result: Dictionary = service.join(target)
	assert_true(join_result.ok)
	assert_eq(service.view().operation_kind, SessionService.OPERATION_JOIN)

	assert_true(hud.bind_session(service))
	assert_eq(_label(hud, "SessionCard/Content/SessionMode").text, "CLIENT")
	assert_false(hud.get_node("SessionCard/Content/SessionDetail").visible)
	transport.emit_peer(join_result.operation_id)
	await get_tree().process_frame
	assert_eq(service.view().phase, SessionService.PHASE_CONNECTING)
	assert_false(hud.get_node("SessionCard/Content/SessionDetail").visible)


## PlayerLifecycle alone owns life text despite an actor signal, and dead teardown hides it.
func test_lifecycle_is_sole_life_writer_and_dead_removal_hides_row() -> void:
	var hud: Hud = await _add_hud()
	var actor := ActorMotion.new()
	actor.add_user_signal(&"alive_changed", [{ "name": "alive", "type": TYPE_BOOL }])
	var lifecycle := FakeHudSource.new()
	add_child_autofree(actor)
	add_child_autofree(lifecycle)
	lifecycle.snapshot = { "alive": false, "respawn_seconds": 2.4 }

	assert_true(hud.bind_player(actor))
	assert_false(hud.get_node("PlayerCard").visible)
	assert_true(hud.bind_lifecycle(lifecycle))
	assert_eq(_label(hud, "PlayerCard/Content/PlayerState").text, "DOWN")
	assert_true(hud.get_node("RespawnSlot").visible)
	assert_eq(_label(hud, "RespawnSlot/Content/RespawnValue").text, "2.4")

	actor.emit_signal(&"alive_changed", true)
	assert_eq(_label(hud, "PlayerCard/Content/PlayerState").text, "DOWN")
	lifecycle.publish({ "alive": true })
	assert_eq(_label(hud, "PlayerCard/Content/PlayerState").text, "ACTIVE")
	assert_false(hud.get_node("RespawnSlot").visible)
	lifecycle.publish({ "alive": false, "respawn_seconds": 1.2 })
	lifecycle.queue_free()
	await get_tree().process_frame
	assert_false(hud.get_node("PlayerCard").visible)
	assert_eq(_label(hud, "PlayerCard/Content/PlayerState").text, "")
	assert_false(hud.get_node("RespawnSlot").visible)
	assert_eq(_label(hud, "RespawnSlot/Content/RespawnValue").text, "")


## Owner snapshots stay unchanged and no gameplay mutation API is called during presentation.
func test_hud_reads_without_writing_owner_state() -> void:
	var hud: Hud = await _add_hud()
	var session := FakeHudSource.new()
	add_child_autofree(session)
	var expected: Dictionary = _session_view(&"STANDALONE", 1)
	session.snapshot = expected.duplicate(true)

	assert_true(hud.bind_session(session))
	assert_eq(_label(hud, "SessionCard/Content/SessionMode").text, "SOLO")
	assert_eq(_label(hud, "SessionCard/Content/SessionDetail").text, "1 PLAYER")
	assert_false(hud.get_node("SessionCard/Content/ConnectionQuality").visible)
	assert_gt(session.read_count, 0)
	assert_eq(session.write_count, 0)
	assert_eq(session.snapshot, expected)
	assert_true(hud.future_slots_are_empty())
	assert_false(hud.get_node("PlayerCard/Content/HealthSlot").visible)
	assert_false(hud.get_node("PlayerCard/Content/AmmoSlot").visible)
	assert_false(hud.get_node("PlayerCard/Content/VehicleSlot").visible)
	assert_false(hud.get_node("MinimapSlot").visible)


## Visible HUD cards stay on-screen and disjoint at every supported viewport size.
func test_supported_resolution_layout_has_no_overlap_or_offscreen_cards() -> void:
	for viewport_size: Vector2i in SUPPORTED_SIZES:
		await _assert_supported_layout(viewport_size)  # gdstyle:ignore=quality/await-in-loop


## Builds one HUD under the active test viewport and waits for authored bindings.
func _add_hud() -> Hud:
	var hud: Hud = HUD_SCENE.instantiate() as Hud
	add_child_autofree(hud)
	await get_tree().process_frame
	return hud


## Builds and checks one authored HUD layout at an exact supported viewport size.
func _assert_supported_layout(viewport_size: Vector2i) -> void:
	var viewport := SubViewport.new()
	viewport.size = viewport_size
	viewport.disable_3d = true
	add_child_autofree(viewport)
	var hud: Hud = HUD_SCENE.instantiate() as Hud
	var session := FakeHudSource.new()
	var player := ActorMotion.new()
	var lifecycle := FakeHudSource.new()
	viewport.add_child(session)
	viewport.add_child(player)
	viewport.add_child(lifecycle)
	viewport.add_child(hud)
	await get_tree().process_frame
	session.snapshot = _session_view(&"HOST", 4, "Good 42 ms")
	lifecycle.snapshot = { "alive": false, "respawn_seconds": 2.8 }
	assert_true(hud.bind_session(session))
	assert_true(hud.bind_player(player))
	assert_true(hud.bind_lifecycle(lifecycle))
	await get_tree().process_frame

	var panels: Array[PanelContainer] = [
		hud.get_node("SessionCard") as PanelContainer,
		hud.get_node("PlayerCard") as PanelContainer,
		hud.get_node("RespawnSlot") as PanelContainer,
		hud.get_node("ControlsCard") as PanelContainer,
	]
	for panel: PanelContainer in panels:
		_assert_rect_on_screen(panel.get_global_rect(), viewport_size)
	_assert_no_overlaps(panels, viewport_size)

	viewport.queue_free()
	await get_tree().process_frame


## Checks every visible card pair without nesting that concern into scene setup.
func _assert_no_overlaps(panels: Array[PanelContainer], viewport_size: Vector2i) -> void:
	for left_index: int in range(panels.size()):
		for right_index: int in range(left_index + 1, panels.size()):
			assert_false(
				panels[left_index].get_global_rect().intersects(
					panels[right_index].get_global_rect()
				),
				(
					"%s and %s overlap at %s"
					% [panels[left_index].name, panels[right_index].name, viewport_size]
				),
			)


## Creates an owner-shaped session view with stable admitted roster rows.
func _session_view(kind: StringName, peer_count: int, quality: String = "") -> Dictionary:
	var result: Dictionary = _roster_view(peer_count)
	result["operation_kind"] = kind
	result["connection_quality"] = quality
	return result


## Creates a roster-owner view with stable admitted participant rows.
func _roster_view(peer_count: int) -> Dictionary:
	var roster: Array[Dictionary] = []
	for participant_id: int in range(1, peer_count + 1):
		roster.append({ "participant_id": participant_id, "phase": &"ADMITTED" })
	return { "roster": roster }


## Resolves a label while keeping individual expectations concise.
func _label(hud: Hud, path: NodePath) -> Label:
	return hud.get_node(path) as Label


## Checks each side independently so the failure reports the offending rectangle.
func _assert_rect_on_screen(rect: Rect2, viewport_size: Vector2i) -> void:
	assert_gte(rect.position.x, 0.0)
	assert_gte(rect.position.y, 0.0)
	assert_lte(rect.end.x, float(viewport_size.x))
	assert_lte(rect.end.y, float(viewport_size.y))
