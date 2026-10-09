extends SceneTree
## Headless entry point for one seeded ten-minute integrated S17 host run.

const HOST_SCENE: PackedScene = preload("res://tests/fixtures/s17/host.tscn")

var _seed: int = 0
var _output: String = ""


## Parses external evidence arguments and defers until the saved host enters the tree.
func _initialize() -> void:
	var parsed: Dictionary = _parse_arguments(OS.get_cmdline_user_args())
	if not parsed.valid:
		printerr(parsed.error)
		quit(2)
		return

	_seed = parsed.seed
	_output = parsed.output
	_run.call_deferred()


## Executes one seed and writes its full timing samples and bounded receipts.
func _run() -> void:
	var host: S17Host = HOST_SCENE.instantiate() as S17Host
	root.add_child(host)
	await process_frame
	var receipt: Dictionary = host.run_seed(_seed)
	var file: FileAccess = FileAccess.open(_output, FileAccess.WRITE)
	if file == null:
		printerr("could not write S17 output: " + _output)
		quit(3)
		return

	file.store_string(JSON.stringify(receipt) + "\n")
	file.close()
	print("S17_RESULT " + JSON.stringify({
		"seed": _seed,
		"total_p95_ms": receipt.timing_ms.total.p95,
		"total_p99_ms": receipt.timing_ms.total.p99,
		"failures": receipt.failures,
	}))
	host.free()
	quit(0 if receipt.failures.is_empty() else 1)


## Parses a required nonnegative seed and absolute external JSON destination.
func _parse_arguments(arguments: PackedStringArray) -> Dictionary:
	var seed: int = -1
	var output: String = ""
	var index: int = 0
	while index < arguments.size():
		if arguments[index] == "--seed" and index + 1 < arguments.size():
			seed = arguments[index + 1].to_int()
			index += 2
		elif arguments[index] == "--output" and index + 1 < arguments.size():
			output = arguments[index + 1]
			index += 2
		else:
			return { "valid": false, "error": "unknown or incomplete argument" }
	if seed < 0 or output.is_empty() or not output.is_absolute_path():
		return { "valid": false, "error": "--seed and absolute --output are required" }

	return { "valid": true, "seed": seed, "output": output }
