extends SceneTree
## Explicit affected-script and saved-resource/public-API checks, without editor addons.

const PARTICIPANT: int = 7
const BOOT: String = "res://tests/fixtures/s03/boot.tscn"

var _failures: Array[String] = []
var _checks: Array[String] = []


## Runs after SceneTree initialization without entering the network proof scene.
func _initialize() -> void:
	_run.call_deferred()


## Parses changed scripts, resolves saved resources and checks independent state expectations.
func _run() -> void:
	_validate_resources()

	var packed: PackedScene = load(BOOT) as PackedScene
	if packed == null:
		_check(false, "saved S03 boot load")
		_finish()
		return

	var boot: Node = packed.instantiate()
	var state: S03Match = boot.get_node("View/Match") as S03Match
	state.authoritative = true
	state.session_id = "s08-public-api"
	var entity: int = state.prepare_initial(PARTICIPANT)
	_check(entity == 1, "literal initial entity")
	_check(state.baseline(PARTICIPANT, 1).rows[0].health == 75, "literal baseline health75")
	_check(state.apply_journal(PARTICIPANT, 70, 2), "public journal accepted")
	_check(state.baseline(PARTICIPANT, 2).rows[0].health == 70, "literal journal health70")
	_check(not state.apply_journal(PARTICIPANT, 10, 2), "obsolete journal rejected")
	_check(state.baseline(PARTICIPANT, 3).rows[0].health == 70, "rejected journal preserves70")
	var frame: Dictionary = { "context": state.context(PARTICIPANT), "sequence": 1, "move": 0.5 }
	_check(state.submit_held(PARTICIPANT, frame) == "NOT_ADMITTED", "pre-admission rejected")
	state.admit(PARTICIPANT)
	_check(state.submit_held(PARTICIPANT, frame) == "OK", "admitted current intent accepted")
	state.authoritative = false
	_check(state.submit_held(PARTICIPANT, frame) == "NOT_ADMITTED", "replica authority rejected")
	state.authoritative = true
	state.prepare_resync(PARTICIPANT)
	_check(state.baseline(PARTICIPANT, 4).rows[0].health == 70, "resync preserves literal70")
	_check(state.prepare_initial(PARTICIPANT) == entity, "resync preserves entity identity")
	_check(state.submit_held(PARTICIPANT, frame) == "NOT_ADMITTED", "resync closes admission")
	state.admit(PARTICIPANT)
	_check(state.submit_held(PARTICIPANT, frame) == "STALE_CONTEXT", "old control rejected")
	state.rollback(PARTICIPANT)
	_check(state.bindings.is_empty() and state.entities.is_empty(), "rollback clears ownership")
	await process_frame
	boot.free()
	_finish()


## Explicitly reloads changed scripts and resolves all saved resource UID dependencies.
func _validate_resources() -> void:
	for path: String in ["res://tests/fixtures/s03/replication.gd",
		"res://tests/fixtures/s08/release_boot.gd"]:
		var script: GDScript = ResourceLoader.load(path, "GDScript",
			ResourceLoader.CACHE_MODE_REPLACE) as GDScript
		_check(script != null, "explicit script load " + path)
		if script != null:
			_check(script.reload(true) == OK, "explicit script reload " + path)

	var inputs: Array = JSON.parse_string(FileAccess.get_file_as_string("res://s08_inputs.json"))
	for row: Dictionary in inputs:
		var path: String = "res://" + str(row.path)
		if path.ends_with(".uid") or path.ends_with(".import"):
			continue

		var resource: Resource = load(path)
		_check(resource != null, "saved dependency " + path)
		var uid: String = str(row.uid)
		if not uid.is_empty():
			var identity: int = ResourceUID.text_to_id(uid)
			_check(ResourceUID.has_id(identity), "saved UID registered " + path)
			if ResourceUID.has_id(identity):
				_check(ResourceUID.get_id_path(identity) == path, "saved UID path " + path)
				_check(load(uid) == resource, "saved UID resource " + path)


## Records literal public contract expectations without debug-only assertions.
func _check(condition: bool, contract: String) -> void:
	_checks.append(contract)
	if not condition:
		_failures.append(contract)


## Emits one explicit result and returns a failing exit when any contract fails.
func _finish() -> void:
	print("S08_API " + JSON.stringify({"ok": _failures.is_empty(),
		"checks": _checks, "failures": _failures}))
	quit(0 if _failures.is_empty() else 1)
