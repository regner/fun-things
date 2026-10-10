extends GutTest
## Verifies HUD owner bindings, read-only presentation, and supported-resolution layout.

const HUD_SCENE: PackedScene = preload("res://scenes/ui/hud.tscn")
const SUPPORTED_SIZES: Array[Vector2i] = [
	Vector2i(1280, 720),
	Vector2i(1920, 1080),
	Vector2i(2560, 1440),
	Vector2i(1280, 800),
]


## Rebinding disconnects the prior session owner and owner teardown hides stale data.
func test_session_binding_rebinding_and_owner_freed() -> void:
	var hud: Hud = await _add_hud()
	var first := FakeHudSource.new()
	var second := FakeHudSource.new()
	add_child_autofree(first)
	add_child_autofree(second)
	first.snapshot = _session_view(&"HOST", 2)
	second.snapshot = _session_view(&"JOIN", 3, "Good 42 ms")

	assert_true(hud.bind_session(first))
	assert_eq(_label(hud, "SessionCard/Content/SessionMode").text, "HOST")
	assert_true(hud.bind_session(second))
	assert_eq(_label(hud, "SessionCard/Content/SessionMode").text, "CLIENT")
	assert_eq(_label(hud, "SessionCard/Content/SessionDetail").text, "3 PLAYERS")
	assert_eq(_label(hud, "SessionCard/Content/ConnectionQuality").text, "GOOD 42 MS")

	first.publish(_session_view(&"STANDALONE", 1))
	assert_eq(_label(hud, "SessionCard/Content/SessionMode").text, "CLIENT")
	second.queue_free()
	await get_tree().process_frame
	assert_false(hud.get_node("SessionCard").visible)


## Controlled-player and lifecycle owners update only their presentation and clear on teardown.
func test_player_and_lifecycle_binding_clear_stale_state() -> void:
	var hud: Hud = await _add_hud()
	var player := FakeHudSource.new()
	var lifecycle := FakeHudSource.new()
	add_child_autofree(player)
	add_child_autofree(lifecycle)
	lifecycle.snapshot = { "alive": false, "respawn_seconds": 2.4 }

	assert_true(hud.bind_player(player))
	assert_eq(_label(hud, "PlayerCard/Content/PlayerState").text, "ACTIVE")
	player.publish_alive(false)
	assert_eq(_label(hud, "PlayerCard/Content/PlayerState").text, "DOWN")
	player.publish_alive(true)
	assert_true(hud.bind_lifecycle(lifecycle))
	assert_eq(_label(hud, "PlayerCard/Content/PlayerState").text, "DOWN")
	assert_true(hud.get_node("RespawnSlot").visible)
	assert_eq(_label(hud, "RespawnSlot/Content/RespawnValue").text, "2.4")

	lifecycle.publish({ "alive": true })
	assert_eq(_label(hud, "PlayerCard/Content/PlayerState").text, "ACTIVE")
	assert_false(hud.get_node("RespawnSlot").visible)
	lifecycle.publish({ "alive": false, "respawn_seconds": 1.2 })
	lifecycle.queue_free()
	await get_tree().process_frame
	assert_eq(_label(hud, "PlayerCard/Content/PlayerState").text, "ACTIVE")
	assert_false(hud.get_node("RespawnSlot").visible)
	player.queue_free()
	await get_tree().process_frame
	assert_false(hud.get_node("PlayerCard").visible)


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
	var player := FakeHudSource.new()
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
	var roster: Array[Dictionary] = []
	for participant_id: int in range(1, peer_count + 1):
		roster.append({ "participant_id": participant_id })
	return {
		"operation_kind": kind,
		"roster": roster,
		"connection_quality": quality,
	}


## Resolves a label while keeping individual expectations concise.
func _label(hud: Hud, path: NodePath) -> Label:
	return hud.get_node(path) as Label


## Checks each side independently so the failure reports the offending rectangle.
func _assert_rect_on_screen(rect: Rect2, viewport_size: Vector2i) -> void:
	assert_gte(rect.position.x, 0.0)
	assert_gte(rect.position.y, 0.0)
	assert_lte(rect.end.x, float(viewport_size.x))
	assert_lte(rect.end.y, float(viewport_size.y))
