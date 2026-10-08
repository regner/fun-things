class_name S05Presentation
extends Node
## Reserves presentation for every explosion possible in the finite fixture.

const MAX_SLOTS: int = S05Damage.MAX_CARS
const LIFETIME_TICKS: int = 120

var session_id: String = ""
var watermark: int = 0
var slots: Array[int] = []
var accepted: int = 0
var dropped: int = 0
var peak: int = 0


## Binds a fresh session without replaying historical explosion events.
func begin(session: String) -> void:
	clear()
	session_id = session


## Advances cosmetic lifetime without deciding or canceling authoritative work.
func advance(tick: int) -> void:
	while not slots.is_empty() and slots[0] <= tick:
		slots.pop_front()


## Consumes ordered live EventIds once only after their current-state dependency.
func consume(event: Dictionary, revision: int, tick: int) -> bool:
	if event.size() != 6 or event.get("session") != session_id or event.get("match") != 1:
		return false

	for field: String in ["sequence", "required", "tick", "car"]:
		if not event.get(field) is int or event[field] < 0:
			return false

	if event.sequence <= watermark or event.required > revision:
		return false

	watermark = event.sequence
	advance(tick)
	if slots.size() < MAX_SLOTS:
		slots.append(tick + LIFETIME_TICKS)
		accepted += 1
		peak = maxi(peak, slots.size())
	else:
		dropped += 1

	return true


## Clears all session event history and outstanding cosmetic reservations.
func clear() -> void:
	session_id = ""
	watermark = 0
	slots.clear()
	accepted = 0
	dropped = 0
	peak = 0
