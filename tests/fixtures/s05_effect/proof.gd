class_name S05SavedProof
extends S05Proof
## Extends accepted finite ENet proof with literal saved-slot and cosmetic lifetime checks.


## Verifies cosmetic APIs before the unchanged admission and ENet proof begins.
func _ready() -> void:
	state = $View/Match as S05Match
	_effect_contract()
	_negative_guards()
	super._ready()


## Checks saved identity, saturation, fences and local expiry independently of damage.
func _effect_contract() -> void:
	var presentation: S05SavedPresentation = state.effects as S05SavedPresentation
	_check(presentation.receipt().instances == 8, "eight authored effect instances")
	for slot: Node3D in $View/Match/Presentation/Slots.get_children():
		_check(slot.scene_file_path == "res://tests/fixtures/s05_effect/explosion.tscn",
			"saved explosion ancestry")
		var model: Node3D = slot.get_node("Visuals/Model") as Node3D
		_check(model.scene_file_path == "res://art/models/spikes/s05_explosion_carrier.glb",
			"linked GLB ancestry")
		_check(model.transform == Transform3D.IDENTITY, "authored model datum preserved")

	presentation.begin(API_SESSION)
	for sequence: int in range(1, 13):
		_check(presentation.consume(_event(sequence), 1, 0), "new live event accepted")

	_check(presentation.accepted == 8 and presentation.dropped == 4,
		"literal eight reservations and four saturation drops")
	_check(presentation.visible_count() == 8, "eight saved nodes visible property")
	_event_fences(presentation)
	for tick: int in 119:
		presentation.advance_cosmetic()

	_check(presentation.visible_count() == 8, "visible before literal120 cosmetic ticks")
	presentation.advance_cosmetic()
	_check(presentation.visible_count() == 0 and presentation.slots.is_empty(),
		"local expiry at literal120 ticks without another host event")
	var retired_epoch: int = presentation.epoch
	presentation.begin(API_SESSION)
	_check(presentation.consume(_event(1), 1, 0), "new session cosmetic reservation")
	presentation.call("_release", 0, retired_epoch, 1)
	_check(presentation.visible_count() == 1, "obsolete epoch callback rejected")
	presentation.advance(120)
	_check(presentation.consume(_event(2), 1, 120), "slot reused after host deadline")
	presentation.call("_release", 0, presentation.epoch, 1)
	_check(presentation.visible_count() == 1, "obsolete slot generation callback rejected")
	presentation.clear()
	_check(presentation.visible_count() == 0 and presentation.slots.is_empty(),
		"clear hides authored slots and retires reservations")
	print("S05_EFFECT " + JSON.stringify({"event": "api", "instances": 8,
		"accepted": 8, "dropped": 4, "cleanup_ticks": 120, "ok": failures.is_empty()}))


## Exercises literal rejected events without allocating more slots or advancing history.
func _event_fences(presentation: S05SavedPresentation) -> void:
	var watermark_before: int = presentation.watermark
	_check(not presentation.consume(_event(12), 1, 0), "duplicate live fence")
	_check(not presentation.consume(_event(1), 1, 0), "stale sequence fence")
	var invalid: Dictionary = _event(13)
	invalid.required = 2
	_check(not presentation.consume(invalid, 1, 0), "future durable dependency fence")
	invalid = _event(13)
	invalid.session = "ffffffffffffffffffffffffffffffff"
	_check(not presentation.consume(invalid, 1, 0), "stale session fence")
	invalid = _event(13)
	invalid.generation = 2
	_check(not presentation.consume(invalid, 1, 0), "unsupported event generation rejected")
	_check(presentation.watermark == watermark_before and presentation.visible_count() == 8,
		"rejected events cannot allocate or advance history")


## Builds the accepted six-field live event shape for literal adapter expectations.
func _event(sequence: int) -> Dictionary:
	return {"session": API_SESSION, "match": 1, "sequence": sequence,
		"required": 1, "tick": 0, "car": 1001}


## Adds actual saved node state to the accepted chain/work telemetry.
func _metrics() -> Dictionary:
	var metrics: Dictionary = super._metrics()
	metrics["saved_effects"] = (state.effects as S05SavedPresentation).receipt()
	return metrics


## Captures actual settled hydration with no historical saved effect instances active.
func _baseline(id: int) -> void:
	super._baseline(id)
	_check((state.effects as S05SavedPresentation).visible_count() == 0,
		"baseline has zero historical saved effects")


## Checks cleanup generation and node visibility before reporting inherited results.
func _result() -> void:
	_check((state.effects as S05SavedPresentation).visible_count() == 0,
		"teardown hides all saved effects")
	super._result()


## Mutates only copied adapter resources on copied saved nodes to prove guard sensitivity.
func _negative_guards() -> void:
	var source: String = load("res://tests/fixtures/s05_effect/presentation.gd").source_code
	var mutations: Array[Dictionary] = [
		{"name": "lifetime", "from": "_active[index].local_deadline <= cosmetic_tick",
			"to": "false"},
		{"name": "epoch", "from": "expected_epoch != epoch or index < 0",
			"to": "index < 0"}]
	for mutation: Dictionary in mutations:
		_check(source.contains(mutation.from), "negative mutation targets actual guard")
		# Exactly two isolated test resources; no allocation in a gameplay tick.
		var script: GDScript = GDScript.new()  # gdstyle:ignore=quality/allocation-in-loop
		script.source_code = source.replace("class_name S05SavedPresentation", "")
		script.source_code = script.source_code.replace(mutation.from, mutation.to)
		_check(script.reload() == OK, "isolated negative script compilation")
		_negative_guard(script, mutation.name)


## Executes the same public cosmetic APIs against a disposable saved fixture copy.
func _negative_guard(script: GDScript, kind: String) -> void:
	var scratch: Node = load("res://tests/fixtures/s05_effect/burst.tscn").instantiate()
	scratch.set_script(null)
	scratch.get_node("View/Match").set_script(null)
	var presentation: Node = scratch.get_node("View/Match/Presentation")
	presentation.set_script(script)
	add_child(scratch)
	var saved_slots: Array[Node3D] = []
	var saved_bodies: Array[S05Car] = []
	for slot: Node3D in presentation.get_node("Slots").get_children():
		saved_slots.append(slot)

	for body: S05Car in scratch.get_node("View/Match/Cars").get_children():
		saved_bodies.append(body)

	presentation.call("bind", saved_slots, saved_bodies)
	presentation.call("begin", API_SESSION)
	presentation.call("consume", _event(1), 1, 0)
	var old_epoch: int = presentation.get("epoch")
	if kind == "lifetime":
		for tick: int in 120:
			presentation.call("advance_cosmetic")

		_check(presentation.call("visible_count") == 1,
			"omitted lifetime guard violates literal120-tick cleanup")
	else:
		presentation.call("begin", API_SESSION)
		presentation.call("consume", _event(1), 1, 0)
		presentation.call("_release", 0, old_epoch, 1)
		_check(presentation.call("visible_count") == 0,
			"omitted epoch guard releases a new session effect")

	presentation.call("clear")
	scratch.free()
	print("S05_EFFECT " + JSON.stringify({"event": "negative", "guard": kind,
		"sensitivity_observed": true, "ok": failures.is_empty()}))
