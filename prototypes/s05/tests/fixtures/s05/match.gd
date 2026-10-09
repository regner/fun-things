class_name S05Match
extends S03Match
## Reuses S03 marker admission; damage rows have one separate scoped owner.

@onready var damage: S05Damage = $Damage
@onready var effects: S05Presentation = $Presentation


## Establishes passive roles before any saved car descendant can run ready callbacks.
func _enter_tree() -> void:
	for body: S05Car in $Cars.get_children():
		body.configure(false)


## Injects saved cars and connects local live presentation through the match coordinator.
func _ready() -> void:
	var saved: Array[S05Car] = []
	for body: S05Car in $Cars.get_children():
		saved.append(body)

	damage.bind_bodies(saved)
	damage.exploded.connect(_present)


## Advances the same sole gameplay owner only on authoritative physics ticks.
func _physics_process(delta: float) -> void:
	super._physics_process(delta)
	if authoritative:
		damage.advance()
		effects.advance(damage.tick)


## Adds bounded lifetime shooter registration alongside inherited provisional markers.
func prepare_initial(participant: int) -> int:
	if damage.session_id.is_empty():
		damage.begin(authoritative, session_id)
		effects.begin(session_id)

	var entity: int = super.prepare_initial(participant)
	assert(damage.register_shooter(entity, 1), "S05 lifetime shooter capacity exhausted")
	return entity


## Extends the existing immutable S03 cut with current car/life state, never events.
func baseline(participant: int, baseline_id: int) -> Dictionary:
	var data: Dictionary = super.baseline(participant, baseline_id)
	data["cars"] = damage.cut()
	return data


## Preflights car dependencies before inherited marker mutation and disabled rig binding.
func apply_baseline(data: Dictionary) -> bool:
	if not data.get("cars") is Dictionary:
		return false

	damage.session_id = session_id
	if not damage.valid_cut(data.cars):
		return false

	var cars: Dictionary = data.cars.duplicate(true)
	if not super.apply_baseline(data):
		return false

	damage.begin(false, session_id)
	effects.begin(session_id)
	return damage.apply_cut(cars, true)


## Validates admitted sender-owned primitive fire intent before host-only shot resolution.
func submit_fire(participant: int, envelope: Variant) -> String:
	if not authoritative or not bindings.has(participant) or not bindings[participant].admitted:
		return "NOT_ADMITTED"
	if not envelope is Dictionary or envelope.size() != 3:
		return "INVALID"
	if not envelope.get("sequence") is int or envelope.get("fire") != true:
		return "INVALID"
	if not envelope.get("fire") is bool or not envelope.get("context") is Dictionary:
		return "INVALID"
	if envelope.context != context(participant):
		return "STALE_CONTEXT"

	var binding: Dictionary = bindings[participant]
	return damage.resolve_shot({"session": session_id, "match": 1, "shooter": binding.entity,
		"generation": binding.generation, "sequence": envelope.sequence}, S05Damage.CAR_ID_START)


## Applies only current reliable car rows; marker movement has no car lifecycle writer.
func apply_cars(cut: Dictionary) -> bool:
	return damage.apply_cut(cut)


## Consumes live events through the presentation owner after their durable car dependency.
func _present(event: Dictionary) -> void:
	effects.consume(event, damage.revision, damage.tick)


## Removes shooter control while preserving shot rejection history until session teardown.
func rollback(participant: int) -> void:
	if bindings.has(participant):
		damage.retire_shooter(bindings[participant].entity)

	super.rollback(participant)


## Clears scoped jobs/effects before the inherited session close becomes observable.
func clear() -> void:
	damage.clear()
	effects.clear()
	super.clear()
