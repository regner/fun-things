class_name S05Damage  # gdstyle:ignore=quality/max-class-variables
extends Node
## Sole bounded owner; explicit finite counters retain the experiment work receipts.

signal changed(cut: Dictionary)
signal exploded(event: Dictionary)

const MAX_CARS: int = 12
const MAX_SHOOTERS: int = 4
const MAX_INTEGER: int = 2_147_483_647
const SHOT_WINDOW: int = 16
const ROOT_WORK_PER_TICK: int = 4
const TARGET_WORK_PER_TICK: int = 4
const MAX_HEALTH: int = 100
const DAMAGE: int = 100
const RADIUS_M: float = 4.1
const CHAIN_DELAY_TICKS: int = 6
const WRECK_TICKS: int = 300
const CAR_ID_START: int = 1001
const OCCUPANT_SENTINEL: int = 9001

var authoritative: bool = false
var session_id: String = ""
var tick: int = 0
var revision: int = 1
var next_event: int = 0
var bodies: Array[S05Car] = []
var rows: Array[Dictionary] = []
var shooters: Dictionary = {}
var jobs: Array[Dictionary] = []
var roots_this_tick: int = 0
var target_peak: int = 0
var root_peak: int = 0
var queue_peak: int = 0
var cache_peak: int = 0
var total_visits: int = 0
var damage_outcomes: int = 0
var occupant_deaths: int = 0
var completed: Array[Dictionary] = []


## Injects saved bodies once; this owner never builds hierarchy or placement.
func bind_bodies(saved_bodies: Array[S05Car]) -> void:
	assert(saved_bodies.size() > 0 and saved_bodies.size() <= MAX_CARS)
	bodies = saved_bodies


## Creates one finite fixture session with all chain capacity reserved up front.
func begin(host: bool, session: String) -> void:
	clear()
	authoritative = host
	session_id = session
	for index: int in bodies.size():
		rows.append({"id": CAR_ID_START + index, "generation": 1, "health": MAX_HEALTH,
			"life": 1, "collision": 1, "phase": "LIVE", "deadline": 0,
			"occupant": OCCUPANT_SENTINEL if index == 0 else 0,
			"occupant_alive": index == 0, "seat": index == 0, "explosions": 0})
		bodies[index].apply_life(host, "LIVE")


## Reserves immutable shooter identity and a retirement watermark until session end.
func register_shooter(entity: int, generation: int) -> bool:
	if not authoritative or entity <= 0 or generation != 1:
		return false

	if shooters.has(entity):
		return shooters[entity].generation == generation and shooters[entity].active

	if shooters.size() >= MAX_SHOOTERS:
		return false

	shooters[entity] = { "generation": generation, "sequence": 0, "active": true }
	return true


## Removes control while retaining the monotonic rejection floor for departed shooters.
func retire_shooter(entity: int) -> void:
	if shooters.has(entity):
		shooters[entity].active = false


## Resolves a host-committed shot exactly once; rejected work spends no identity.
func resolve_shot(shot: Dictionary, target: int) -> String:  # gdstyle:ignore=quality/max-returns
	if not authoritative:
		return "NOT_AUTHORITY"
	if not _shot_valid(shot) or target < CAR_ID_START or target >= CAR_ID_START + rows.size():
		return "INVALID"
	if shot.session != session_id or shot.match != 1:
		return "STALE_CONTEXT"
	if not shooters.has(shot.shooter):
		return "STALE_SHOOTER"

	var shooter: Dictionary = shooters[shot.shooter]
	if shot.generation != shooter.generation or not shooter.active:
		return "STALE_SHOOTER"
	if shot.sequence <= shooter.sequence:
		return "DUPLICATE"
	if shot.sequence > shooter.sequence + SHOT_WINDOW:
		return "WINDOW"
	if roots_this_tick >= ROOT_WORK_PER_TICK or next_event > MAX_INTEGER - MAX_CARS - 1:
		return "STATE_LIMIT"

	# Every car has one reserved chain slot; only nonterminal cars schedule it.
	roots_this_tick += 1
	root_peak = maxi(root_peak, roots_this_tick)
	shooter.sequence = shot.sequence
	next_event += 1
	_damage(target - CAR_ID_START)
	return "OK"


## Checks exact primitive committed ShotId fields before indexing or mutation.
func _shot_valid(shot: Dictionary) -> bool:
	if shot.size() != 5 or not shot.get("session") is String:
		return false

	for field: String in ["match", "shooter", "generation", "sequence"]:
		if not shot.get(field) is int or shot[field] <= 0 or shot[field] > MAX_INTEGER:
			return false

	return shot.session.length() == 32


## Commits health, occupant release and body collision before emitting owner state.
func _damage(index: int) -> void:
	var row: Dictionary = rows[index]
	if row.phase != "LIVE":
		return

	row.health = maxi(0, int(row.health) - DAMAGE)
	damage_outcomes += 1
	if row.health == 0:
		row.phase = "WRECK"
		row.life += 1
		row.collision += 1
		row.deadline = tick + WRECK_TICKS
		if row.occupant_alive:
			row.occupant_alive = false
			row.seat = false
			occupant_deaths += 1

		bodies[index].apply_life(authoritative, row.phase)
		next_event += 1
		jobs.append({"sequence": next_event, "car": row.id, "due": tick + CHAIN_DELAY_TICKS,
			"cursor": 0, "visited": []})
		queue_peak = maxi(queue_peak, jobs.size())
		assert(jobs.size() <= bodies.size())

	revision += 1
	changed.emit(cut())


## Runs finite target work in due/EventId order and retires only completed caches.
func advance() -> void:
	if not authoritative or rows.is_empty():
		return

	tick += 1
	roots_this_tick = 0
	jobs.sort_custom(_earlier)
	var work: int = 0
	while work < TARGET_WORK_PER_TICK and not jobs.is_empty() and jobs[0].due <= tick:
		var job: Dictionary = jobs[0]
		var index: int = job.cursor
		job.visited.append(rows[index].id)
		cache_peak = maxi(cache_peak, job.visited.size())
		job.cursor += 1
		work += 1
		total_visits += 1
		var source: S05Car = bodies[int(job.car) - CAR_ID_START]
		if bodies[index].global_position.distance_to(source.global_position) <= RADIUS_M:
			_damage(index)

		if job.cursor == rows.size():
			_complete(job)
			jobs.pop_front()

	target_peak = maxi(target_peak, work)
	_retire_wrecks()


## Orders bounded pending jobs without retiring older still-active target caches.
func _earlier(first: Dictionary, second: Dictionary) -> bool:
	return first.due < second.due or (first.due == second.due \
		and first.sequence < second.sequence)


## Records completion and emits one live blast after all authoritative targets finish.
func _complete(job: Dictionary) -> void:
	var row: Dictionary = rows[int(job.car) - CAR_ID_START]
	row.explosions += 1
	revision += 1
	completed.append({"sequence": job.sequence, "due": job.due, "tick": tick,
		"car": job.car, "visits": job.visited.size()})
	assert(completed.size() <= MAX_CARS)
	changed.emit(cut())
	exploded.emit({"session": session_id, "match": 1, "sequence": job.sequence,
		"required": revision, "tick": tick, "car": job.car})


## Clears expired collision only after its reserved authoritative blast completes.
func _retire_wrecks() -> void:
	for index: int in rows.size():
		var row: Dictionary = rows[index]
		if row.phase != "WRECK" or row.deadline > tick or row.explosions != 1:
			continue

		row.phase = "RETIRED"
		row.life += 1
		row.collision += 1
		bodies[index].apply_life(authoritative, "RETIRED")
		revision += 1
		changed.emit(cut())


## Captures current bounded state without damage history or historical live effects.
func cut() -> Dictionary:
	return {"session": session_id, "match": 1, "revision": revision,
		"tick": tick, "rows": rows.duplicate(true)}


## Preflights the entire fixed-car cut before any replica lifecycle or collision mutation.
func valid_cut(data: Dictionary) -> bool:
	if data.size() != 5 or data.get("session") != session_id or data.get("match") != 1:
		return false

	for field: String in ["revision", "tick"]:
		if not _integer(data.get(field), 0):
			return false

	var incoming: Variant = data.get("rows")
	if not incoming is Array or incoming.size() != bodies.size() or data.revision <= 0:
		return false

	for index: int in incoming.size():
		if not _row_valid(incoming[index], index):
			return false

	return true


## Validates fixed identity and coherent life/health/seat/collision/retention dependencies.
func _row_valid(row: Variant, index: int) -> bool:
	if not row is Dictionary or row.size() != 11:
		return false

	for field: String in ["id", "generation", "health", "life", "collision", "deadline",
		"occupant", "explosions"]:
		if not _integer(row.get(field), 0):
			return false

	if row.id != CAR_ID_START + index or row.generation != 1:
		return false
	if not row.get("occupant_alive") is bool or not row.get("seat") is bool:
		return false
	if row.occupant != (OCCUPANT_SENTINEL if index == 0 else 0):
		return false

	var phase: Variant = row.get("phase")
	var live: bool = phase == "LIVE"
	var retired: bool = phase == "RETIRED"
	return phase in ["LIVE", "WRECK", "RETIRED"] and row.health == (MAX_HEALTH if live else 0) \
		and row.life == (1 if live else (3 if retired else 2)) and row.collision == row.life \
		and row.occupant_alive == (index == 0 and live) and row.seat == row.occupant_alive \
		and row.explosions >= 0 and row.explosions <= (0 if live else 1) \
		and (not retired or row.explosions == 1) \
		and (row.deadline == 0 if live else row.deadline > 0)


## Accepts bounded integral JSON numbers without coercing malformed floats into IDs.
func _integer(value: Variant, minimum: int) -> bool:
	return (value is int or value is float) and is_finite(float(value)) \
		and value >= minimum and value <= MAX_INTEGER and float(value) == int(value)


## Applies only a validated newer current cut; replicas never enqueue authoritative work.
func apply_cut(data: Dictionary, hydrate: bool = false) -> bool:
	if authoritative or not valid_cut(data) or (not hydrate and data.revision <= revision):
		return false

	rows.clear()
	for index: int in data.rows.size():
		var row: Dictionary = data.rows[index].duplicate(true)
		for field: String in ["id", "generation", "health", "life", "collision", "deadline",
			"occupant", "explosions"]:
			row[field] = int(row[field])

		rows.append(row)
		bodies[index].apply_life(false, row.phase)

	revision = int(data.revision)
	tick = int(data.tick)
	return true


## Clears finite session work and passive bodies without changing saved placement.
func clear() -> void:
	for body: S05Car in bodies:
		body.apply_life(false, "RETIRED")

	authoritative = false
	session_id = ""
	tick = 0
	revision = 1
	next_event = 0
	rows.clear()
	shooters.clear()
	jobs.clear()
	completed.clear()
	roots_this_tick = 0
	target_peak = 0
	root_peak = 0
	queue_peak = 0
	cache_peak = 0
	total_visits = 0
	damage_outcomes = 0
	occupant_deaths = 0
