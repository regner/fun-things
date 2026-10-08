extends SceneTree  # gdstyle:ignore=quality/max-class-variables
## Fresh-session S05 comparator scheduler; owns only trial timing and fixture lifetime.

const FIXTURE: String = "res://tests/fixtures/s05_effect/burst.tscn"
const CAMERA: String = "res://tests/fixtures/s05_draw/camera.tscn"
const MAX_TRIALS: int = 20
const MAX_INITIAL_DELAY_SECONDS: float = 15.0
const MAX_SPACING_SECONDS: float = 30.0
const CHAIN_DEADLINE_TICKS: int = 180
const DRAW_DEADLINE_MS: int = 5000
const EXPECTED_POSITIONS: Array[Vector3] = [
	Vector3(0, 0.001, 0),
	Vector3(4, 0.001, 0),
	Vector3(8, 0.001, 0),
	Vector3(12, 0.001, 0),
	Vector3(0, 0.001, 4),
	Vector3(4, 0.001, 4),
	Vector3(8, 0.001, 4),
	Vector3(12, 0.001, 4),
	Vector3(0, 0.001, 8),
	Vector3(4, 0.001, 8),
	Vector3(8, 0.001, 8),
	Vector3(12, 0.001, 8),
]

var failures: Array[String] = []
var trials: int = 20
var initial_delay_seconds: float = 15.0
var spacing_seconds: float = 30.0
var started_usec: int = 0
var trial_rows: Array[Dictionary] = []
var stream: FileAccess
var graphical: bool = false
var draw_serial: int = 0
var active_match: S05Match
var active_trial: int = 0
var active_draw: Dictionary = {}
var previous_intent: Dictionary = {}
var previous_event: Dictionary = {}
var previous_callback: Callable
var previous_instance_ids: Array[int] = []


## Defers argument validation and execution until the SceneTree can own saved fixtures.
func _initialize() -> void:
	_run.call_deferred()


## Parses a bounded parameterized schedule and executes every trial without fixture reuse.
func _run() -> void:
	if not _parse_arguments():
		_write_result()
		quit(2)
		return

	stream = FileAccess.open("res://trials.jsonl", FileAccess.WRITE)
	if stream == null:
		_fail("trial stream unavailable")
		_write_result()
		quit(2)
		return

	graphical = DisplayServer.get_name() != "headless"
	if graphical:
		var camera_scene: PackedScene = load(CAMERA) as PackedScene
		var observation: Node3D = camera_scene.instantiate() as Node3D
		root.add_child(observation)
		(observation.get_node("Camera3D") as Camera3D).make_current()
		RenderingServer.frame_post_draw.connect(_post_draw)

	started_usec = Time.get_ticks_usec()
	for ordinal: int in trials:
		await _wait_for_schedule(initial_delay_seconds + spacing_seconds * ordinal)  # gdstyle:ignore=format/max-line-length,quality/await-in-loop
		await _run_trial(ordinal + 1)  # gdstyle:ignore=quality/await-in-loop
		if not failures.is_empty():
			break

	stream.close()
	_write_result()
	quit(0 if failures.is_empty() and trial_rows.size() == trials else 1)


## Accepts only finite C0 schedule values within the measured-card envelope.
func _parse_arguments() -> bool:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--trials="):
			trials = int(argument.trim_prefix("--trials="))
		elif argument.begins_with("--initial-delay="):
			initial_delay_seconds = float(argument.trim_prefix("--initial-delay="))
		elif argument.begins_with("--spacing="):
			spacing_seconds = float(argument.trim_prefix("--spacing="))
		else:
			_fail("unknown argument: " + argument)

	return (
		failures.is_empty()
		and trials > 0
		and trials <= MAX_TRIALS
		and is_finite(initial_delay_seconds)
		and initial_delay_seconds >= 0.0
		and initial_delay_seconds <= MAX_INITIAL_DELAY_SECONDS
		and is_finite(spacing_seconds)
		and spacing_seconds >= 0.0
		and spacing_seconds <= MAX_SPACING_SECONDS
	)


## Waits against the run's monotonic origin so trial loading is outside chain timing.
func _wait_for_schedule(target_seconds: float) -> void:
	while _elapsed_seconds() < target_seconds:
		await create_timer(minf(target_seconds - _elapsed_seconds(), 0.05)).timeout  # gdstyle:ignore=format/max-line-length,quality/await-in-loop


## Loads, admits, fires, checks, clears and observes retirement for one fresh session.
func _run_trial(ordinal: int) -> void:  # gdstyle:ignore=format/max-line-length,quality/max-function-length,quality/max-local-variables
	var scheduled_seconds: float = initial_delay_seconds + spacing_seconds * (ordinal - 1)
	var load_start_usec: int = Time.get_ticks_usec()
	var packed: PackedScene = load(FIXTURE) as PackedScene
	if packed == null:
		_fail("saved effect fixture unavailable")
		return

	var fixture: Node = packed.instantiate()
	# The inherited proof is a test coordinator. This driver replaces only that coordinator.
	fixture.set_script(null)
	var state: S05Match = fixture.get_node("View/Match") as S05Match
	var session_id: String = Crypto.new().generate_random_bytes(16).hex_encode()
	state.authoritative = true
	state.session_id = session_id
	root.add_child(fixture)
	await process_frame
	var ready_usec: int = Time.get_ticks_usec()
	active_match = state
	active_trial = ordinal
	active_draw = {}

	var instance_ids: Array[int] = [fixture.get_instance_id()]
	for body: S05Car in state.damage.bodies:
		instance_ids.append(body.get_instance_id())

	var start_valid: bool = _saved_start_valid(state)
	var identities_fresh: bool = _identities_fresh(instance_ids)
	var first_draw_seconds: Variant = null
	if graphical:
		var before_draw: int = draw_serial
		var draw_start_usec: int = Time.get_ticks_usec()
		if await _wait_for_draw(before_draw):
			first_draw_seconds = (Time.get_ticks_usec() - draw_start_usec) / 1000000.0
		else:
			_fail("trial %d first draw deadline" % ordinal)

	var participant: int = ordinal
	var entity: int = state.prepare_initial(participant)
	state.admit(participant)
	var stale_shot_rejected: bool = (
		previous_intent.is_empty()
		or state.submit_fire(participant, previous_intent) == "STALE_CONTEXT"
	)
	var stale_event_rejected: bool = (
		previous_event.is_empty()
		or not state.effects.consume(previous_event, state.damage.revision, state.damage.tick)
	)
	var stale_callback_retired: bool = (
		previous_callback.is_null() or not previous_callback.is_valid()
	)
	var held_velocity_zero: bool = _held_velocity_zero(state, participant)
	var intent: Dictionary = {
		"context": state.context(participant),
		"sequence": 1,
		"fire": true,
	}
	var chain_start_usec: int = Time.get_ticks_usec()
	var chain_start_tick: int = state.damage.tick
	var admission: String = state.submit_fire(participant, intent)
	while admission == "OK" and not _settled(state):
		await physics_frame  # gdstyle:ignore=quality/await-in-loop
		if state.damage.tick - chain_start_tick > CHAIN_DEADLINE_TICKS:
			_fail("trial %d chain deadline" % ordinal)
			break

	var chain_end_usec: int = Time.get_ticks_usec()
	var outcomes_valid: bool = admission == "OK" and _outcomes_valid(state)
	var damage_outcomes: int = state.damage.damage_outcomes
	var total_visits: int = state.damage.total_visits
	var target_peak: int = state.damage.target_peak
	var completed_count: int = state.damage.completed.size()
	var effects_accepted: int = state.effects.accepted
	var effects_dropped: int = state.effects.dropped
	var drawn: bool = false
	if graphical and outcomes_valid:
		drawn = await _wait_for_burst_draw(ordinal)
		if not drawn:
			_fail("trial %d burst draw deadline" % ordinal)

	var events: Array[Dictionary] = []
	for completed: Dictionary in state.damage.completed:
		(
			events
			. append(
				{
					"session": session_id,
					"match": 1,
					"sequence": completed.sequence,
					"required": state.damage.revision,
					"tick": completed.tick,
					"car": completed.car,
				}
			)
		)

	var reset_start_usec: int = Time.get_ticks_usec()
	state.rollback(participant)
	state.effects.clear()
	var producer_stopped: bool = (
		not state.damage.shooters[entity].active and not state.bindings.has(participant)
	)
	var local_effects_cleared: bool = (
		state.effects.slots.is_empty()
		and (state.effects as S05SavedPresentation).visible_count() == 0
	)
	var no_live_job: bool = state.damage.jobs.is_empty()
	previous_callback = Callable(state.effects, "advance_cosmetic")
	previous_intent = intent.duplicate(true)
	previous_event = events[-1].duplicate(true) if not events.is_empty() else {}
	previous_instance_ids = instance_ids.duplicate()
	state.clear()
	fixture.queue_free()
	await process_frame
	var retired_usec: int = Time.get_ticks_usec()
	var fixture_freed: bool = not is_instance_valid(fixture)
	var callback_retired: bool = not previous_callback.is_valid()
	active_match = null
	active_trial = 0

	var row: Dictionary = {
		"trial": ordinal,
		"session": session_id,
		"scheduled_seconds": scheduled_seconds,
		"actual_start_seconds": (load_start_usec - started_usec) / 1000000.0,
		"loading_seconds": (ready_usec - load_start_usec) / 1000000.0,
		"first_draw_seconds": first_draw_seconds,
		"chain_seconds": (chain_end_usec - chain_start_usec) / 1000000.0,
		"reset_seconds": (retired_usec - reset_start_usec) / 1000000.0,
		"admission": admission,
		"start_valid": start_valid,
		"identities_fresh": identities_fresh,
		"stale_shot_rejected": stale_shot_rejected,
		"stale_event_rejected": stale_event_rejected,
		"stale_callback_retired": stale_callback_retired and callback_retired,
		"held_velocity_zero": held_velocity_zero,
		"outcomes_valid": outcomes_valid,
		"producer_stopped": producer_stopped,
		"local_effects_cleared": local_effects_cleared,
		"no_live_job": no_live_job,
		"fixture_freed": fixture_freed,
		"drawn": drawn,
		"draw": active_draw,
		"damage": damage_outcomes,
		"visits": total_visits,
		"target_peak": target_peak,
		"completed": completed_count,
		"effects_accepted": effects_accepted,
		"effects_dropped": effects_dropped,
	}
	trial_rows.append(row)
	stream.store_line(JSON.stringify(row))
	stream.flush()
	if not _trial_valid(row):
		_fail("trial %d lifecycle criteria" % ordinal)


## Checks literal saved placement, passive pre-tree roles and neutral body state.
func _saved_start_valid(state: S05Match) -> bool:
	if state.damage.bodies.size() != EXPECTED_POSITIONS.size():
		return false

	for index: int in state.damage.bodies.size():
		var body: S05Car = state.damage.bodies[index]
		if not body.global_position.is_equal_approx(EXPECTED_POSITIONS[index]):
			return false
		if body.velocity != Vector3.ZERO or body.simulation_enabled:
			return false
		if body.collision_layer != 0 or body.collision_mask != 0:
			return false

	return true


## Rejects accidental reuse of the root or any saved body object across trials.
func _identities_fresh(instance_ids: Array[int]) -> bool:
	for identity: int in instance_ids:
		if identity in previous_instance_ids:
			return false

	return true


## Reads held intent and every body velocity without becoming another movement writer.
func _held_velocity_zero(state: S05Match, participant: int) -> bool:
	if not state.bindings.has(participant) or state.bindings[participant].held != 0.0:
		return false

	for body: S05Car in state.damage.bodies:
		if body.velocity != Vector3.ZERO:
			return false

	return true


## Recognizes completion only from the twelve public current rows.
func _settled(state: S05Match) -> bool:
	if state.damage.rows.size() != 12:
		return false

	for row: Dictionary in state.damage.rows:
		if row.explosions != 1:
			return false

	return true


## Checks literal/API outcomes without duplicating radius or damage calculations.
func _outcomes_valid(state: S05Match) -> bool:
	if state.damage.rows.size() != 12 or state.damage.completed.size() != 12:
		return false

	for row: Dictionary in state.damage.rows:
		if row.health != 0 or row.phase != "WRECK" or row.explosions != 1:
			return false
	for completed: Dictionary in state.damage.completed:
		if completed.visits != 12:
			return false

	var presentation: S05SavedPresentation = state.effects as S05SavedPresentation
	return (
		state.damage.damage_outcomes == 12
		and state.damage.total_visits == 144
		and state.damage.target_peak == 4
		and state.damage.jobs.is_empty()
		and presentation.accepted == 8
		and presentation.dropped == 4
		and presentation.visible_count() == 8
		and presentation.visual_peak == 8
	)


## Waits for one genuine post-draw callback after the current fixture became ready.
func _wait_for_draw(previous: int) -> bool:
	var deadline: int = Time.get_ticks_msec() + DRAW_DEADLINE_MS
	while draw_serial <= previous and Time.get_ticks_msec() < deadline:
		await process_frame  # gdstyle:ignore=quality/await-in-loop

	return draw_serial > previous


## Waits until a post-draw callback captures all eight accepted saved effect slots.
func _wait_for_burst_draw(ordinal: int) -> bool:
	var deadline: int = Time.get_ticks_msec() + DRAW_DEADLINE_MS
	while active_draw.is_empty() and Time.get_ticks_msec() < deadline:
		await process_frame  # gdstyle:ignore=quality/await-in-loop

	return (
		not active_draw.is_empty()
		and active_draw.trial == ordinal
		and active_draw.visible == 8
		and active_draw.visible_in_tree == 8
		and active_draw.dropped == 4
		and active_draw.png.save_error == OK
	)


## Captures saved-slot visibility and viewport pixels only from completed automatic draws.
func _post_draw() -> void:
	draw_serial += 1
	if active_match == null or active_trial <= 0 or not active_draw.is_empty():
		return

	var presentation: S05SavedPresentation = active_match.effects as S05SavedPresentation
	if presentation.visible_count() != 8 or presentation.dropped != 4:
		return

	var visible_in_tree: int = 0
	var mesh_nodes: int = 0
	for slot: Node3D in presentation.get_node("Slots").get_children():
		if slot.is_visible_in_tree():
			visible_in_tree += 1
		mesh_nodes += slot.find_children("*", "MeshInstance3D", true, false).size()

	var image: Image = root.get_texture().get_image()
	var path: String = "res://trial-%02d-burst.png" % active_trial
	var error: Error = image.save_png(path)
	active_draw = {
		"trial": active_trial,
		"callback": draw_serial,
		"render_index": Engine.get_frames_drawn(),
		"visible": presentation.visible_count(),
		"visible_in_tree": visible_in_tree,
		"mesh_nodes": mesh_nodes,
		"dropped": presentation.dropped,
		"can_draw": DisplayServer.window_can_draw(),
		"camera_scene": CAMERA,
		"png":
		{
			"path": path,
			"width": image.get_width(),
			"height": image.get_height(),
			"save_error": error,
			"sha256": FileAccess.get_sha256(path) if error == OK else "",
		},
	}


## Applies all independent lifecycle booleans to each retained trial receipt.
func _trial_valid(row: Dictionary) -> bool:
	for field: String in [
		"start_valid",
		"identities_fresh",
		"stale_shot_rejected",
		"stale_event_rejected",
		"stale_callback_retired",
		"held_velocity_zero",
		"outcomes_valid",
		"producer_stopped",
		"local_effects_cleared",
		"no_live_job",
		"fixture_freed",
	]:
		if row[field] != true:
			return false

	return not graphical or row.drawn == true


## Retains the first failure while permitting deterministic cleanup and result writing.
func _fail(message: String) -> void:
	if message not in failures:
		failures.append(message)


## Writes one bounded aggregate with lifecycle costs separate from chain cost.
func _write_result() -> void:
	var result: Dictionary = {
		"ok": failures.is_empty() and trial_rows.size() == trials,
		"failures": failures,
		"trials_requested": trials,
		"trials_completed": trial_rows.size(),
		"initial_delay_seconds": initial_delay_seconds,
		"spacing_seconds": spacing_seconds,
		"elapsed_seconds": _elapsed_seconds(),
		"graphical": graphical,
		"engine": Engine.get_version_info(),
		"scope": "standalone comparator correctness; no ENet or capacity measurement",
	}
	var file: FileAccess = FileAccess.open("res://result.json", FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify(result, "\t") + "\n")
		file.close()
	print("S07_COMPARATOR_RESULT ", JSON.stringify(result))


## Returns monotonic elapsed time, including scheduled idle and lifecycle phases.
func _elapsed_seconds() -> float:
	if started_usec == 0:
		return 0.0

	return (Time.get_ticks_usec() - started_usec) / 1000000.0
