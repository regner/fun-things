class_name S12Proof
extends Node
## Coordinates S12 combat through the unchanged S03 admission and transport owners.

const CASE_DEADLINE_MS: int = 30_000

var role: String = "host"
var profile: String = "normal"
var port: int = 25_200
var deadline_ms: int = 0
var host_summary: Dictionary = {}
var ending: bool = false

@onready var session: S03Session = $Session
@onready var match_state: S03Match = $View/Match
@onready var replication: S03Replication = $View/Match/Replication
@onready var combat: S12Combat = $Combat


## Bind unchanged session dependencies and begin the selected real-process role.
func _ready() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--role="):
			role = argument.trim_prefix("--role=")
		elif argument.begins_with("--port="):
			port = int(argument.trim_prefix("--port="))
		elif argument.begins_with("--profile="):
			profile = argument.trim_prefix("--profile=")

	session.match_state = match_state
	session.replication = replication
	replication.match_state = match_state
	replication.resolve_participant = session.participant_for_peer
	replication.handoff_confirmed.connect(session.confirm_handoff)
	replication.admission_received.connect(session.receive_admission)
	combat.configure(session, role, profile)
	combat.receipt.connect(_on_receipt)
	combat.client_finished.connect(_on_client_finished)
	combat.host_finished.connect(_on_host_finished)
	session.select_provider(S03Transport.new(get_tree()))
	deadline_ms = Time.get_ticks_msec() + CASE_DEADLINE_MS
	if role == "host":
		session.host(port)
		_emit("ready", { "port": port, "user_dir": OS.get_user_data_dir() })
	else:
		session.join(session.provider.parse_endpoint("127.0.0.1", port))


## Drive only the experiment owner after ordinary gameplay admission.
func _physics_process(delta: float) -> void:
	if ending:
		return
	if Time.get_ticks_msec() > deadline_ms:
		_result(false, { "failure": "case deadline" })
		return

	combat.physics_step(delta)


## Retain selected shot/rocket telemetry and finish the host after client acknowledgement.
func _on_receipt(record: Dictionary) -> void:
	_emit(record.event, record)
	if role == "host" and record.event == "finish_ack" and not ending:
		ending = true
		session.leave()
		_finish_host()


## Publish the complete client rows, then allow reliable acknowledgement delivery before exit.
func _on_client_finished(summary: Dictionary) -> void:
	if role != "client" or ending:
		return

	ending = true
	await get_tree().create_timer(0.25).timeout
	_result(true, { "summary": summary })


## Retain the host's bounded-state summary until the client acknowledges receipt.
func _on_host_finished(summary: Dictionary) -> void:
	host_summary = summary


## Wait for adapter cleanup before reporting the host result.
func _finish_host() -> void:
	var cleanup_deadline: int = Time.get_ticks_msec() + 2000
	while session.phase != "IDLE" and Time.get_ticks_msec() < cleanup_deadline:
		await get_tree().process_frame  # gdstyle:ignore=quality/await-in-loop

	_result(session.phase == "IDLE", {"summary": host_summary,
		"cleanup_phase": session.phase})


## Print one structured experiment record with process and lifecycle identity.
func _emit(event: String, data: Dictionary) -> void:
	data.event = event
	data.role = role
	data.pid = OS.get_process_id()
	data.phase = session.phase
	data.wall_usec = int(Time.get_unix_time_from_system() * 1_000_000.0)
	print("S12 " + JSON.stringify(data))


## Emit the terminal row and stop this owned process.
func _result(ok: bool, details: Dictionary) -> void:
	if not ending:
		ending = true
	_emit("result", { "ok": ok, "details": details })
	get_tree().quit(0 if ok else 1)
