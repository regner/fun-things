class_name FakeHudSource
extends Node
## Supplies observable read-only HUD source contracts without gameplay ownership.

signal changed(view: Dictionary)
signal alive_changed(alive: bool)

var snapshot: Dictionary = {}
var alive: bool = true
var read_count: int = 0
var write_count: int = 0


## Returns the retained owner snapshot while recording a presentation read.
func view() -> Dictionary:
	read_count += 1
	return snapshot


## Publishes an owner-side snapshot through the same immutable-view signal contract.
func publish(next_snapshot: Dictionary) -> void:
	snapshot = next_snapshot.duplicate(true)
	changed.emit(snapshot)


## Returns owner-held player life state for initial controlled-player presentation.
func is_alive() -> bool:
	read_count += 1
	return alive


## Publishes an owner-side player life transition.
func publish_alive(next_alive: bool) -> void:
	alive = next_alive
	alive_changed.emit(alive)


## Represents a gameplay mutation API that presentation must never call.
func write_gameplay_state() -> void:
	write_count += 1
