extends SceneTree
## Independent JSON cut, malformed dependency and atomic rejection checks through actual APIs.

var failures: Array[String] = []


## Defers instantiation until the tree can own saved fixture resources.
func _initialize() -> void:
	_run.call_deferred()


## Roundtrips the real wire cut and rejects mismatched cuts without mutating installed state.
func _run() -> void:
	var packed: PackedScene = load("res://tests/fixtures/s04/boot.tscn")
	var source: Node = packed.instantiate()
	source.set_script(null)
	source.process_mode = Node.PROCESS_MODE_DISABLED
	root.add_child(source)
	var host: S04Match = source.get_node("View/Match")
	host.authoritative = true
	host.session_id = "0123456789abcdef0123456789abcdef"
	host.prepare_initial(1)
	host.prepare_initial(2)
	host.bindings[2].health = 70
	var wire: Dictionary = JSON.parse_string(JSON.stringify(host.baseline(2, 1)))
	var target: Node = packed.instantiate()
	target.set_script(null)
	target.process_mode = Node.PROCESS_MODE_DISABLED
	target.name = "Replica"
	root.add_child(target)
	var replica: S04Match = target.get_node("View/Match")
	replica.session_id = host.session_id
	_require(replica.apply_baseline(wire), "actual JSON baseline rejected")
	_require(replica.bindings[2].health == 70 and replica.seats[2].vehicle == 1002,
		"JSON baseline lost injured player or seat")
	var installed: String = JSON.stringify(replica.baseline(2, 1))
	for index: int in 5:
		var broken: Dictionary = wire.duplicate(true)
		match index:
			0:
				broken.poses[1].entity = broken.poses[0].entity
			1:
				broken.poses[1].control += 1
			2:
				broken.seats["2"].vehicle = 1001
			3:
				broken.rows[1].participant = broken.rows[0].participant
			4:
				broken.participant = 9
		_require(not replica.apply_baseline(broken), "malformed cut accepted: %d" % index)
		_require(JSON.stringify(replica.baseline(2, 1)) == installed,
			"rejected cut mutated replica: %d" % index)
	print("S04_BASELINE " + JSON.stringify({ "ok": failures.is_empty(), "failures": failures }))
	source.queue_free()
	target.queue_free()
	quit(0 if failures.is_empty() else 1)


## Reports independent expectations in both diagnostics and process status.
func _require(condition: bool, label: String) -> void:
	if not condition:
		failures.append(label)
