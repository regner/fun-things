class_name SessionStatus
extends Control
## Presents connection, loading, active, closing, and error state without deciding it.

signal primary_requested()
signal back_requested()

@onready var _eyebrow: Label = %Eyebrow
@onready var _title: Label = %Title
@onready var _detail: Label = %Detail
@onready var _primary_button: Button = %PrimaryButton
@onready var _back_button: Button = %BackButton


## Renders one immutable SessionService view into authored controls.
func present(view: Dictionary) -> void:
	var was_visible: bool = visible
	var phase: StringName = view.get("phase", SessionService.PHASE_IDLE)
	var failure: Dictionary = view.get("failure", {})
	visible = phase != SessionService.PHASE_IDLE or not failure.is_empty()
	_eyebrow.text = "SESSION / " + String(phase)
	_back_button.visible = phase == SessionService.PHASE_IDLE
	_primary_button.disabled = phase == SessionService.PHASE_CLOSING
	if not failure.is_empty():
		_present_failure(failure)
	else:
		match phase:
			SessionService.PHASE_STARTING:
				_present_progress("Making some room.", "Preparing the session.", "Cancel")
			SessionService.PHASE_CONNECTING:
				_present_progress("Finding the host.", "Opening the direct connection.", "Cancel")
			SessionService.PHASE_NEGOTIATING:
				_present_progress("Checking the city.", "Confirming compatible content.", "Cancel")
			SessionService.PHASE_LOADING:
				_present_progress("Loading the city.", "Preparing the saved world.", "Cancel")
			SessionService.PHASE_SYNCHRONIZING:
				_present_progress(
					"Receiving current state.",
					"Controls unlock after admission.",
					"Cancel",
				)
			SessionService.PHASE_ACTIVE:
				_present_progress("Ready to make trouble.", "The session is active.", "Leave")
			SessionService.PHASE_CLOSING:
				_present_progress(
					"Cleaning up.",
					"Closing the old session before returning.",
					"Closing…",
				)
			_:
				_present_progress("Session", "Choose an action from the main menu.", "Retry")

	if visible and not was_visible:
		_focus_initial_action()


## Focuses the first available action without stealing focus on later state updates.
func _focus_initial_action() -> void:
	if _primary_button.visible and not _primary_button.disabled:
		_primary_button.grab_focus()
	elif _back_button.visible and not _back_button.disabled:
		_back_button.grab_focus()


## Emits the context-sensitive action for Boot to route through SessionService.
func _on_primary_pressed() -> void:
	primary_requested.emit()


## Requests dismissal only after the session has returned to idle.
func _on_back_pressed() -> void:
	back_requested.emit()


## Applies common progress copy to the authored status card.
func _present_progress(title: String, detail: String, action: String) -> void:
	_title.text = title
	_detail.text = detail
	_primary_button.text = action
	_primary_button.visible = true


## Shows normalized failure information and enables retry only when permitted.
func _present_failure(failure: Dictionary) -> void:
	var code: String = String(failure.get("code", &"UNKNOWN"))
	_title.text = code.replace("_", " ").capitalize()
	_detail.text = "The previous operation cleaned up. You can return or retry."
	_primary_button.text = "Retry"
	_primary_button.visible = failure.get("retryable", false)
