class_name HostTickCoordinator
extends RefCounted
## Orders current host pedestrian decisions before shared ActorMotion steps and profiles both.

const SECTION_PEDESTRIAN_DECISIONS: StringName = &"pedestrian_decisions"
const SECTION_ACTOR_MOTION: StringName = &"actor_motion"

var _profiler: HostTickProfiler
var _pedestrian_core: PedestrianCore
var _pedestrian_agent_ids: PackedInt64Array = PackedInt64Array()
var _pedestrian_actors: Array[ActorMotion] = []
var _player_actors: Array[ActorMotion] = []
var _last_failure: String = ""


## Installs optional report-only instrumentation and its current production sections.
func configure(profiler: HostTickProfiler = null) -> bool:
	_profiler = profiler
	if _profiler == null:
		return true
	if not _profiler.register_section(SECTION_PEDESTRIAN_DECISIONS):
		return false
	if not _profiler.register_section(SECTION_ACTOR_MOTION):
		return false
	return true


## Binds stable pedestrian identities and actors without taking ownership of their state.
func bind_pedestrians(
	pedestrian_core: PedestrianCore,
	pedestrian_agent_ids: PackedInt64Array,
	pedestrian_actors: Array[ActorMotion],
) -> bool:
	if pedestrian_core == null or pedestrian_agent_ids.size() != pedestrian_actors.size():
		return false
	if pedestrian_actors.has(null):
		return false

	_pedestrian_core = pedestrian_core
	_pedestrian_agent_ids = pedestrian_agent_ids.duplicate()
	_pedestrian_actors = pedestrian_actors.duplicate()
	return true


## Binds current player actors whose commands are supplied for each host tick.
func bind_players(player_actors: Array[ActorMotion]) -> bool:
	if player_actors.has(null):
		return false

	_player_actors = player_actors.duplicate()
	return true


## Runs one ordered host tick through existing owner APIs without becoming a state writer.
func step(
	host_tick: int,
	delta_seconds: float,
	player_commands: Array[FootCommand],
) -> bool:
	_last_failure = ""
	if host_tick < 0 or _pedestrian_core == null:
		_last_failure = "invalid host tick or unbound pedestrian core"
		return false
	if _player_actors.size() != player_commands.size():
		_last_failure = "player command cardinality mismatch"
		return false

	var profiling: bool = _profiler != null and _profiler.is_enabled()
	if profiling:
		_profiler.begin_tick()
		_profiler.begin_section(SECTION_PEDESTRIAN_DECISIONS)
	var pedestrian_commands: Array[FootCommand] = _pedestrian_core.step(host_tick)
	if profiling:
		_profiler.end_section(SECTION_PEDESTRIAN_DECISIONS)
	if pedestrian_commands.size() != _pedestrian_actors.size():
		_last_failure = "pedestrian command cardinality mismatch"
		if profiling:
			_profiler.end_tick()
		return false

	if profiling:
		_profiler.begin_section(SECTION_ACTOR_MOTION)
	var stepped: bool = _step_actors(delta_seconds, pedestrian_commands, player_commands)
	if profiling:
		_profiler.end_section(SECTION_ACTOR_MOTION)
		_profiler.end_tick()
	return stepped


## Returns a stable explanation only when the most recent host tick was rejected.
func last_failure() -> String:
	return _last_failure


## Applies actor-owned motion, then feeds observed pedestrian poses back to the AI owner.
func _step_actors(
	delta_seconds: float,
	pedestrian_commands: Array[FootCommand],
	player_commands: Array[FootCommand],
) -> bool:
	var stepped: bool = true
	for slot: int in _pedestrian_actors.size():
		var actor: ActorMotion = _pedestrian_actors[slot]
		var command: FootCommand = pedestrian_commands[slot]
		if not actor.step(command, delta_seconds, ActorMotion.StepMode.AUTHORITY):
			_last_failure = _describe_pedestrian_rejection(slot, command, delta_seconds)
			stepped = false
		var pose: Vector3 = actor.global_position
		if not _pedestrian_core.sync_position(
			_pedestrian_agent_ids[slot], Vector2(pose.x, pose.z)
		):
			_last_failure = "pedestrian pose handoff rejected slot %d" % slot
			stepped = false
	for slot: int in _player_actors.size():
		var actor: ActorMotion = _player_actors[slot]
		if not actor.step(
			player_commands[slot], delta_seconds, ActorMotion.StepMode.AUTHORITY
		):
			_last_failure = "player ActorMotion rejected slot %d" % slot
			stepped = false
	return stepped


## Describes an unexpected motion rejection without adding work to successful ticks.
func _describe_pedestrian_rejection(
	slot: int,
	command: FootCommand,
	delta_seconds: float,
) -> String:
	return "pedestrian ActorMotion rejected slot %d valid=%s move=%s aim=%s delta=%s" % [
		slot,
		command != null and command.is_valid(),
		command.move if command != null else Vector2.ZERO,
		command.aim_yaw if command != null else 0.0,
		delta_seconds,
	]
